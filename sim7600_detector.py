#!/usr/bin/env python3
"""
SIM7600 Auto-Detection and Management Daemon
Professional production-ready modem detection and service management
Automatically starts voice bot when SIM7600 is detected
"""

import os
import sys
import time
import serial
import subprocess
import json
import requests
import logging
from pathlib import Path
from datetime import datetime
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/home/rom/.env')

# Configure logging based on mode
LOG_MODE = os.getenv('LOG_MODE', 'production')
LOG_LEVEL = logging.DEBUG if LOG_MODE == 'development' else logging.INFO

# Setup logging with rotation
from logging.handlers import RotatingFileHandler

log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    if LOG_MODE == 'development' else
    '%(asctime)s - %(levelname)s - %(message)s'
)

# File handler with rotation (using RAM disk)
file_handler = RotatingFileHandler(
    '/var/log/voice_bot_ram/sim7600_detector.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(LOG_LEVEL)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(LOG_LEVEL)

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class SIM7600Detector:
    """Professional SIM7600 detection and management"""

    def __init__(self):
        self.modem_detected = False
        self.voice_bot_running = False
        self.last_detection = None
        self.detection_count = 0
        self.previous_device_count = 0  # Track USB device count changes

        # Disconnect grace period (prevents service restart on brief disconnects)
        self.disconnect_grace_active = False
        self.disconnect_start_time = None
        self.DISCONNECT_GRACE_PERIOD = 20  # seconds

        # Port mapping for SIM7600
        self.port_mapping = {
            'diagnostic': None,  # ttyUSB0
            'nmea': None,        # ttyUSB1
            'at_command': None,  # ttyUSB2
            'ppp': None,         # ttyUSB3
            'audio': None        # ttyUSB4 (critical for voice)
        }

        # Modem details
        self.modem_details = {
            'manufacturer': 'Unknown',
            'model': 'Unknown',
            'firmware': 'Unknown',
            'imei': 'Unknown',
            'imsi': 'Unknown',
            'carrier': 'Unknown',
            'signal': 'Unknown',
            'apn': 'Unknown',
            'volte': 'Unknown',
            'usb_composition': 'Unknown'
        }

        # Port test results (actual AT command tests)
        self.port_tests = {}

        # Internet configuration
        self.modem_internet = {
            'interface': None,
            'ip': None,
            'ping_test': 'Not tested'
        }

        # VPS endpoints
        # Note: modem status goes through pi_send_message.sh to port 5000
        # Phone call data goes to port 8088 webhook
        self.use_pi_send_message = True  # Primary notification method

        logger.info("="*60)
        logger.info("SIM7600 Detector Started")
        logger.info(f"Mode: {LOG_MODE.upper()}")
        logger.info(f"Log Level: {logging.getLevelName(LOG_LEVEL)}")
        logger.info("="*60)

    def detect_usb_devices(self):
        """Detect all USB serial devices"""
        devices = []
        for i in range(10):  # Check up to ttyUSB9
            device = f"/dev/ttyUSB{i}"
            if os.path.exists(device):
                devices.append(device)

        # Only log when device count changes (development) or stay silent (production)
        if LOG_MODE == 'development':
            if len(devices) != self.previous_device_count:
                logger.info(f"USB devices changed: {self.previous_device_count} → {len(devices)} ports")
                self.previous_device_count = len(devices)

        return devices

    def verify_sim7600_ports(self, devices):
        """Verify this is a SIM7600 and map ports"""
        if len(devices) < 4:
            logger.debug(f"Only {len(devices)} ports found, need at least 4 for SIM7600")
            return False

        # SIM7600 port layout (USB composition 9001 - stable mode for voice):
        # ttyUSB0 - Diagnostics (causes broken pipe, DO NOT USE!)
        # ttyUSB1 - GPS/NMEA
        # ttyUSB2 - AT Commands (SMSTools - locked during SMS operations)
        # ttyUSB3 - AT Commands (MAIN PORT - reliable for configuration + voice)
        # ttyUSB4 - PCM Audio (8kHz raw audio during calls)
        # wwan0 - Internet (QMI interface, NOT serial port)
        self.port_mapping = {
            'config_port': devices[3] if len(devices) > 3 else None,  # ttyUSB3 - Main AT port
            'nmea': devices[1] if len(devices) > 1 else None,         # ttyUSB1 - GPS
            'sms_port': devices[2] if len(devices) > 2 else None,     # ttyUSB2 - SMSTools
            'at_command': devices[3] if len(devices) > 3 else None,   # ttyUSB3 - Voice bot (same as config)
            'audio': devices[4] if len(devices) > 4 else None,        # ttyUSB4 - PCM audio
        }

        # Verify critical ports
        config_port = self.port_mapping['config_port']
        if not config_port:
            logger.error("No AT command port (ttyUSB3) found")
            return False

        voice_port = self.port_mapping['at_command']
        if not voice_port:
            logger.error("No voice AT port (ttyUSB3) found")
            return False

        # CRITICAL: Stop smstools before configuration (just for safety)
        # We use ttyUSB3 for configuration (no conflict), but stop SMSTools anyway
        smstools_was_running = self.stop_smstools_temporarily()

        # STEP 0: Verify/Set USB composition to 9001 (stable mode for voice)
        # This must happen FIRST before any other configuration
        # 9001 = Stable mode (optimized for voice, slower data but more reliable)
        # 9011 = Fast data mode (causes instability on ttyUSB3/ttyUSB4 for voice)
        logger.info("🔧 Checking USB composition mode...")

        # Check USB composition via lsusb (safer than AT commands on ttyUSB2)
        try:
            result = subprocess.run(
                ['lsusb'],
                capture_output=True,
                text=True,
                timeout=2
            )

            current_mode = None
            if "1e0e:9001" in result.stdout:
                current_mode = "9001"
            elif "1e0e:9011" in result.stdout:
                current_mode = "9011"
            elif "1e0e:9024" in result.stdout:
                current_mode = "9024"

            # Store USB composition in modem details
            if current_mode:
                self.modem_details['usb_composition'] = current_mode
            else:
                self.modem_details['usb_composition'] = 'Unknown'

            if current_mode == "9001":
                logger.info("✅ USB composition already in 9001 mode (stable voice)")
            elif current_mode == "9011":
                logger.error(f"❌ USB composition in {current_mode} mode - REQUIRES MANUAL CHANGE!")
                logger.error("   Please run this command on ttyUSB2:")
                logger.error("   sudo timeout 5 bash -c 'echo -e \"AT+CUSBPIDSWITCH=9001,1,1\\r\" > /dev/ttyUSB2; sleep 2; cat /dev/ttyUSB2'")
                logger.error("   Then unplug/replug modem and restart detector")
                return False
            elif current_mode == "9024":
                logger.info(f"ℹ️ USB composition in {current_mode} mode")
            else:
                logger.warning(f"⚠️ Could not determine USB composition mode (device not found in lsusb)")
                logger.warning("   Proceeding with current configuration...")

        except Exception as e:
            logger.error(f"Error checking USB composition: {e}")
            logger.warning("Proceeding with current configuration...")

        # Wait for modem to be ready for AT commands
        # Modem needs time to stabilize after USB enumeration
        logger.info("⏳ Waiting 3 seconds for modem to be ready for AT commands...")
        time.sleep(3)

        # Continue with modem verification
        try:

            with serial.Serial(config_port, 115200, timeout=2, write_timeout=2) as ser:
                # Test AT commands to confirm it's SIM7600
                ser.write(b"AT\r\n")
                time.sleep(1)
                response = ser.read(100).decode('utf-8', errors='ignore')

                if "OK" not in response:
                    logger.debug(f"No OK response from {config_port}")
                    return False

                # Check manufacturer
                ser.write(b"AT+CGMI\r\n")
                time.sleep(1)
                response = ser.read(100).decode('utf-8', errors='ignore')

                if "SIMCOM" in response or "SIM7600" in response:
                    logger.info("✅ SIM7600 confirmed via AT commands")

                    # Query comprehensive modem details
                    self.query_modem_details(ser)

                    return True
                else:
                    logger.debug(f"Not a SIM7600: {response}")
                    return False

        except Exception as e:
            logger.error(f"Error verifying SIM7600: {e}")
            return False
        finally:
            # NOTE: We do NOT restart smstools here anymore
            # It will be restarted once at the end of production configuration
            # This prevents unnecessary stop/start cycles in the middle of setup
            pass

    def stop_smstools_temporarily(self):
        """Stop smstools to free serial port for AT commands"""
        try:
            # Check if smstools is running
            status = subprocess.run(
                ['systemctl', 'is-active', 'smstools'],
                capture_output=True,
                text=True
            )

            if status.stdout.strip() == 'active':
                logger.info("Stopping smstools temporarily for AT commands...")
                os.system('sudo systemctl stop smstools')
                time.sleep(2)  # Wait for port to be released
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking smstools status: {e}")
            return False

    def restart_smstools(self):
        """Restart smstools after AT command verification"""
        try:
            logger.info("Restarting smstools...")
            os.system('sudo systemctl start smstools')
            time.sleep(1)

            # Verify it started
            status = subprocess.run(
                ['systemctl', 'is-active', 'smstools'],
                capture_output=True,
                text=True
            )

            if status.stdout.strip() == 'active':
                logger.info("✅ smstools restarted successfully")
            else:
                logger.error("⚠️ smstools failed to restart!")

        except Exception as e:
            logger.error(f"Error restarting smstools: {e}")

    def query_modem_details(self, ser):
        """Query comprehensive modem details via AT commands"""
        try:
            # Set shorter timeout to prevent freezes
            ser.timeout = 1
            ser.write_timeout = 1
            # ATI - Gets manufacturer, model, firmware, IMEI in one command
            ser.reset_input_buffer()
            ser.write(b"ATI\r\n")
            time.sleep(1)  # TEST #3: Increased to 1s
            response = ser.read(ser.in_waiting or 500).decode('utf-8', errors='ignore')

            # Parse ATI response (format: "Label: Value")
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith("Manufacturer:"):
                    self.modem_details['manufacturer'] = line.split(":", 1)[1].strip()
                elif line.startswith("Model:"):
                    self.modem_details['model'] = line.split(":", 1)[1].strip()
                elif line.startswith("Revision:"):
                    self.modem_details['firmware'] = line.split(":", 1)[1].strip()
                elif line.startswith("IMEI:"):
                    self.modem_details['imei'] = line.split(":", 1)[1].strip()

            # AT+CPIN? - Check SIM card status (CRITICAL: Must check before reading IMSI!)
            ser.reset_input_buffer()
            ser.write(b"AT+CPIN?\r\n")
            time.sleep(1)
            response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')

            sim_ready = False
            if "+CPIN: READY" in response:
                logger.info("✅ SIM card ready")
                sim_ready = True
            elif "+CPIN: NOT INSERTED" in response:
                logger.error("❌ SIM card not inserted!")
                self.modem_details['imsi'] = "No SIM card"
            elif "+CPIN: SIM PIN" in response:
                logger.error("❌ SIM card locked (PIN required)")
                self.modem_details['imsi'] = "SIM locked (PIN)"
            else:
                logger.warning(f"⚠️ Unknown SIM status: {response}")

            # AT+CIMI - Get IMSI (SIM card number) - only if SIM is ready
            if sim_ready:
                ser.reset_input_buffer()
                ser.write(b"AT+CIMI\r\n")
                time.sleep(1)  # TEST #3: Increased to 1s
                response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')
                for line in response.split('\n'):
                    line = line.strip()
                    if line.isdigit() and len(line) >= 14:
                        self.modem_details['imsi'] = line
                        logger.info(f"📱 IMSI: {line}")
                        break

                if self.modem_details.get('imsi') == 'Unknown':
                    logger.warning("⚠️ IMSI query failed despite SIM being ready")

            # AT+CSQ - Get signal strength
            ser.reset_input_buffer()
            ser.write(b"AT+CSQ\r\n")
            time.sleep(1)  # TEST #3: Increased to 1s
            response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')
            if "+CSQ:" in response:
                try:
                    # Format: +CSQ: 18,4 (0-31 scale)
                    signal = int(response.split('+CSQ:')[1].split(',')[0].strip())
                    if signal == 99:
                        self.modem_details['signal'] = "Unknown"
                    else:
                        # Convert to percentage (31 = 100%)
                        signal_percent = int((signal / 31.0) * 100)
                        self.modem_details['signal'] = f"{signal_percent}% ({signal}/31)"
                except:
                    pass

            # AT+COPS? - Get carrier/operator
            ser.reset_input_buffer()
            ser.write(b"AT+COPS?\r\n")
            time.sleep(1)  # TEST #3: Increased to 1s
            response = ser.read(ser.in_waiting or 300).decode('utf-8', errors='ignore')
            if "+COPS:" in response:
                try:
                    # Format: +COPS: 0,0,"vodafone UK",7
                    parts = response.split('+COPS:')[1].split(',')
                    if len(parts) >= 3:
                        carrier = parts[2].strip().strip('"')
                        if carrier:
                            self.modem_details['carrier'] = carrier
                except:
                    pass

            # AT+CGDCONT? - Get APN configuration
            ser.reset_input_buffer()
            ser.write(b"AT+CGDCONT?\r\n")
            time.sleep(1)  # TEST #3: Increased to 1s
            response = ser.read(ser.in_waiting or 500).decode('utf-8', errors='ignore')
            if "+CGDCONT:" in response:
                try:
                    # Format: +CGDCONT: 1,"IPV4V6","wap.vodafone.co.uk",...
                    for line in response.split('\n'):
                        if '+CGDCONT: 1,' in line:
                            parts = line.split(',')
                            if len(parts) >= 3:
                                apn = parts[2].strip().strip('"')
                                if apn:
                                    self.modem_details['apn'] = apn
                            break
                except:
                    pass

            # AT+CEVOLTE? - Get VoLTE status (may not be supported)
            ser.reset_input_buffer()
            ser.write(b"AT+CEVOLTE?\r\n")
            time.sleep(1)  # TEST #3: Increased to 1s
            response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')
            volte_enabled = False
            if "+CEVOLTE:" in response:
                try:
                    status = response.split('+CEVOLTE:')[1].split(',')[0].strip()
                    volte_enabled = (status == "1")
                    self.modem_details['volte'] = "✅" if volte_enabled else "❌"
                except:
                    self.modem_details['volte'] = "❌"
            else:
                self.modem_details['volte'] = "❌"

            # Note: VoLTE enablement moved to AFTER internet configuration
            # VoLTE requires IMS APN + PDP context to be configured first
            # Will be enabled in configure_modem_internet() after APNs are set

            logger.info("📊 Modem Details Queried:")
            logger.info(f"  Manufacturer: {self.modem_details['manufacturer']}")
            logger.info(f"  Model: {self.modem_details['model']}")
            logger.info(f"  Firmware: {self.modem_details['firmware']}")
            logger.info(f"  IMEI: {self.modem_details['imei']}")
            logger.info(f"  IMSI: {self.modem_details['imsi']}")
            logger.info(f"  Carrier: {self.modem_details['carrier']}")
            logger.info(f"  Signal: {self.modem_details['signal']}")
            logger.info(f"  APN: {self.modem_details['apn']}")
            logger.info(f"  VoLTE: {self.modem_details['volte']}")

        except Exception as e:
            logger.error(f"Error querying modem details: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def check_critical_ports(self):
        """Check if critical ports are available"""
        critical_ok = True

        # AT command port is critical
        if not self.port_mapping['at_command']:
            logger.error("❌ AT command port missing")
            critical_ok = False
        else:
            logger.info(f"✅ AT command port: {self.port_mapping['at_command']}")

        # Audio port is critical for voice
        if not self.port_mapping['audio']:
            logger.warning("⚠️ Audio port (ttyUSB4) not found - voice may not work")
            # Don't fail completely, some SIM7600 variants handle audio differently
        else:
            logger.info(f"✅ Audio port: {self.port_mapping['audio']}")

        # Log all mapped ports
        logger.info("Port Mapping:")
        for name, port in self.port_mapping.items():
            status = "✅" if port else "❌"
            logger.info(f"  {status} {name:12} : {port if port else 'Not found'}")

        return critical_ok

    def save_port_mapping(self):
        """Save port mapping to file for voice bot to use"""
        mapping_file = '/home/rom/sim7600_ports.json'
        try:
            with open(mapping_file, 'w') as f:
                json.dump(self.port_mapping, f, indent=2)
            logger.info(f"Port mapping saved to {mapping_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save port mapping: {e}")
            return False

    def configure_ttyusb3_for_at(self):
        """
        Verify and configure ttyUSB3 for AT commands
        Factory default may have it in PPP-only mode
        """
        try:
            voice_port = self.port_mapping.get('at_command')
            if not voice_port:
                logger.error("No voice AT port (ttyUSB3) available")
                return False

            logger.info(f"Testing AT commands on {voice_port}...")

            # Test if AT commands work
            try:
                with serial.Serial(voice_port, 115200, timeout=2, write_timeout=1) as ser:
                    ser.write(b"AT\r\n")
                    time.sleep(0.3)
                    response = ser.read(ser.in_waiting or 100).decode('utf-8', errors='ignore')

                    if "OK" in response:
                        logger.info(f"✅ {voice_port} already supports AT commands")
                        return True
                    else:
                        logger.warning(f"⚠️ {voice_port} did not respond to AT - attempting USB reconfiguration")

            except Exception as e:
                logger.warning(f"Could not test {voice_port}: {e}")

            # If AT failed, try to reconfigure USB mode
            # Use ttyUSB2 to send configuration command
            sms_port = self.port_mapping.get('sms_port')
            if not sms_port:
                logger.error("Cannot reconfigure - no SMS port available")
                return False

            logger.info("Reconfiguring USB mode to enable AT on all ports...")

            # Stop SMSTools to access ttyUSB2
            smstools_was_running = self.stop_smstools_temporarily()

            try:
                with serial.Serial(sms_port, 115200, timeout=2, write_timeout=1) as ser:
                    # AT+CUSBPIDSWITCH=9011,1,1 - Enable AT on all ports
                    ser.write(b"AT+CUSBPIDSWITCH=9011,1,1\r\n")
                    time.sleep(0.5)
                    response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')

                    if "OK" in response:
                        logger.info("✅ USB mode reconfigured - modem will reset")
                        # Modem will reset - give it time
                        time.sleep(5)
                        return True
                    else:
                        logger.error(f"USB reconfiguration failed: {response}")
                        return False

            finally:
                if smstools_was_running:
                    time.sleep(2)  # Wait for modem reset
                    self.restart_smstools()

        except Exception as e:
            logger.error(f"Error configuring ttyUSB3: {e}")
            return False

    def load_carrier_config(self, imsi):
        """
        Load carrier configuration from modem_manager database
        Returns data_apn, ims_apn based on IMSI
        """
        try:
            if not imsi or len(imsi) < 6:
                logger.warning("Invalid IMSI - using fallback config")
                return {'data_apn': 'internet', 'ims_apn': 'ims', 'carrier': 'Unknown'}

            # Extract MCC-MNC from IMSI
            mcc = imsi[:3]
            mnc = imsi[3:5]  # Try 2-digit MNC first
            mcc_mnc = f"{mcc}-{mnc}"

            logger.info(f"Looking up carrier: MCC-MNC {mcc_mnc} (IMSI: {imsi})")

            # Load carrier database
            carrier_db_path = '/home/rom/modem_manager/config/carriers.json'
            if not os.path.exists(carrier_db_path):
                logger.warning(f"Carrier database not found: {carrier_db_path}")
                return {'data_apn': 'internet', 'ims_apn': 'ims', 'carrier': 'Unknown'}

            with open(carrier_db_path, 'r') as f:
                carrier_db = json.load(f)

            # Try 2-digit MNC
            carrier_config = carrier_db.get('carriers', {}).get(mcc_mnc)

            # Try 3-digit MNC if 2-digit failed
            if not carrier_config:
                mnc3 = imsi[3:6]
                mcc_mnc3 = f"{mcc}-{mnc3}"
                carrier_config = carrier_db.get('carriers', {}).get(mcc_mnc3)
                if carrier_config:
                    logger.info(f"Found carrier with 3-digit MNC: {mcc_mnc3}")

            if carrier_config:
                logger.info(f"✅ Carrier found: {carrier_config.get('carrier', 'Unknown')}")
                return {
                    'data_apn': carrier_config.get('data_apn', 'internet'),
                    'ims_apn': carrier_config.get('ims_apn', 'ims'),
                    'carrier': carrier_config.get('carrier', 'Unknown'),
                    'volte_supported': carrier_config.get('volte_supported', True)
                }
            else:
                logger.warning(f"Carrier {mcc_mnc} not in database - using fallback")
                return {'data_apn': 'internet', 'ims_apn': 'ims', 'carrier': f'Unknown (MCC-MNC: {mcc_mnc})'}

        except Exception as e:
            logger.error(f"Error loading carrier config: {e}")
            return {'data_apn': 'internet', 'ims_apn': 'ims', 'carrier': 'Unknown'}

    def configure_modem_internet(self):
        """
        Configure modem for internet via PPP (ttyUSB5)
        CRITICAL: Also configures IMS APN for VoLTE support
        USB composition 9001 uses PPP, not RNDIS/ECM
        """
        try:
            logger.info("Configuring modem internet (PPP on ttyUSB5) + IMS for VoLTE...")

            # Get IMSI and load carrier-specific config
            imsi = self.modem_details.get('imsi', '')
            carrier_config = self.load_carrier_config(imsi)

            data_apn = carrier_config.get('data_apn', 'internet')
            ims_apn = carrier_config.get('ims_apn', 'ims')
            carrier_name = carrier_config.get('carrier', 'Unknown')

            logger.info(f"Carrier: {carrier_name}")
            logger.info(f"Data APN: {data_apn}")
            logger.info(f"IMS APN: {ims_apn}")

            # Save APN to port mapping for internet monitor to use
            self.port_mapping['apn'] = data_apn
            self.port_mapping['ims_apn'] = ims_apn
            self.port_mapping['carrier'] = carrier_name

            # Save updated port mapping with APN info
            logger.info("Saving APN info to port mapping...")
            self.save_port_mapping()

            # Use ttyUSB0 for configuration (dedicated config port, no conflicts)
            config_port = self.port_mapping.get('config_port')
            if not config_port:
                logger.error("No config port (ttyUSB0) available for internet configuration")
                return False

            try:
                with serial.Serial(config_port, 115200, timeout=3, write_timeout=1) as ser:
                    # ========================================
                    # SKIP POWER RAMP (causes ttyUSB3 to disappear!)
                    # ========================================
                    # NOTE: Gradual power ramp (AT+CFUN=0/1) was designed for initial boot
                    # But when modem is already on and communicating, CFUN=0 causes USB reset
                    # and ttyUSB3 disappears, breaking voice bot startup.
                    # Since modem is already working, we skip power cycling.

                    logger.info("⚡ Skipping radio power cycle (modem already on and communicating)")

                    # STEPS 1-2 SKIPPED: Radio already on, no need for CFUN=0/1

                    # Step 3: Configure Data APN (PDP context 1)
                    logger.info(f"📡 Step 3a: Configuring Data APN: {data_apn}...")
                    ser.reset_input_buffer()
                    ser.write(b"AT+CGDCONT=1,\"IP\",\"" + data_apn.encode() + b"\"\r\n")
                    time.sleep(2)  # Increased from 1s to 2s
                    response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')

                    if "OK" not in response:
                        logger.error(f"Failed to set data APN: {response}")
                        return False

                    logger.info(f"✅ Data APN configured: {data_apn}")

                    # Step 3b: Configure IMS APN (PDP context 2 - CRITICAL for VoLTE!)
                    # NOTE: IMS APN MUST use IPV4V6, not IP! Using IP causes activation failure.
                    logger.info(f"📡 Step 3b: Configuring IMS APN: {ims_apn} (IPV4V6)...")
                    ser.reset_input_buffer()
                    ser.write(b"AT+CGDCONT=2,\"IPV4V6\",\"" + ims_apn.encode() + b"\"\r\n")
                    time.sleep(2)
                    response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')

                    if "OK" in response:
                        logger.info(f"✅ IMS APN configured: {ims_apn} with IPV4V6 (required for VoLTE)")
                    else:
                        logger.warning(f"⚠️ IMS APN configuration failed: {response}")
                        # Don't fail - continue anyway

                    # Step 4: Wait for network to settle (EMI mitigation)
                    logger.info("⏳ Step 4: Waiting 10 seconds for network to settle...")
                    time.sleep(10)  # Increased from 7s to 10s

                    # Step 5: Activate PDP contexts (HIGH POWER - EMI risk)
                    # Activate context 1 (Data APN - internet)
                    logger.info("⚡ Step 5a: Activating Data PDP context (AT+CGACT=1,1)...")
                    logger.warning("   ⚠️ HIGH POWER TRANSMISSION - watch for EMI!")
                    ser.reset_input_buffer()
                    ser.write(b"AT+CGACT=1,1\r\n")
                    time.sleep(3)  # Increased from 1s to 3s
                    response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')

                    if "OK" in response:
                        logger.info("✅ Data PDP context activated (context 1)")
                    else:
                        logger.warning(f"⚠️ Data context activation response: {response}")

                    # Wait for context 1 to settle
                    time.sleep(2)

                    # Step 5b: Activate context 2 (IMS APN - required for VoLTE)
                    logger.info("⚡ Step 5b: Activating IMS PDP context (AT+CGACT=1,2)...")
                    ser.reset_input_buffer()
                    ser.write(b"AT+CGACT=1,2\r\n")
                    time.sleep(3)
                    response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')

                    if "OK" in response:
                        logger.info("✅ IMS PDP context activated (context 2) - VoLTE ready!")
                    else:
                        logger.warning(f"⚠️ IMS context activation failed: {response}")
                        logger.warning("   VoLTE may not work without IMS context active")

                    # Wait for both contexts to settle
                    time.sleep(3)

                    # Step 6: Check and Enable VoLTE (CRITICAL - must be AFTER PDP context activation!)
                    # 2G/3G networks being deprecated across Europe (UK: 2025)
                    logger.info("⚡ Step 6: Checking VoLTE status...")

                    # First query current VoLTE status
                    ser.reset_input_buffer()
                    ser.write(b"AT+CEVOLTE?\r\n")
                    time.sleep(1)
                    query_response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')
                    logger.info(f"   VoLTE query response: {query_response.strip()}")

                    # Try to enable VoLTE
                    ser.reset_input_buffer()
                    ser.write(b"AT+CEVOLTE=1,1\r\n")
                    time.sleep(2)
                    enable_response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')

                    if "OK" in enable_response:
                        logger.info("✅ VoLTE enabled successfully via AT+CEVOLTE=1,1")
                        self.modem_details['volte'] = "✅ Enabled"
                    elif "ERROR" in enable_response:
                        # ERROR might mean already enabled or not supported
                        if "+CEVOLTE: 1,1" in query_response:
                            logger.info("✅ VoLTE already enabled (query shows 1,1)")
                            self.modem_details['volte'] = "✅ Already enabled"
                        elif "ERROR" in query_response:
                            logger.warning("⚠️ VoLTE commands not supported by modem/firmware")
                            logger.warning("   Network may enable VoLTE automatically when IMS APN is configured")
                            self.modem_details['volte'] = "⚠️ Not supported (auto-enabled by network?)"
                        else:
                            logger.warning(f"⚠️ VoLTE enable failed: {enable_response.strip()}")
                            logger.warning("   This may be normal - some carriers enable VoLTE automatically")
                            self.modem_details['volte'] = "⚠️ Not confirmed"
                    else:
                        logger.warning(f"⚠️ Unexpected VoLTE response: {enable_response.strip()}")
                        self.modem_details['volte'] = "⚠️ Unknown"

                    # Step 7: Force LTE-only mode to prevent 3G fallback during calls
                    # CRITICAL: Without this, modem falls back to 3G (CSFB) during voice calls
                    #
                    # AT+CNMP Mode Reference (Network Mode Preference):
                    #   2  = Automatic (allows fallback to 2G/3G - causes slow PCM init & no VoLTE)
                    #   13 = GSM Only (2G)
                    #   14 = WCDMA Only (3G)
                    #   38 = LTE Only ← REQUIRED for VoLTE, prevents 3G fallback
                    #   39 = GSM+WCDMA+LTE
                    #   51 = GSM+LTE
                    #   54 = WCDMA+LTE
                    #   59 = TDS-CDMA Only
                    #   60 = GSM+TDS-CDMA
                    #   63 = GSM+WCDMA+TDS-CDMA
                    #
                    # Mode 38 (LTE Only) ensures:
                    # - VoLTE calls work (no 3G fallback)
                    # - Fast PCM audio initialization (~200ms instead of 2s)
                    # - Prevents CSFB (Circuit Switched Fallback) to 3G
                    logger.info("⚡ Step 7: Setting network mode to LTE-only (AT+CNMP=38)...")
                    ser.reset_input_buffer()
                    ser.write(b"AT+CNMP=38\r\n")
                    time.sleep(2)
                    cnmp_response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')

                    if "OK" in cnmp_response:
                        logger.info("✅ Network mode set to LTE-only (mode 38)")
                        logger.info("   Benefits: VoLTE forced, 3G fallback disabled, fast PCM init")
                        self.modem_details['network_mode'] = "LTE-only (mode 38)"
                    else:
                        logger.warning(f"⚠️ Failed to set LTE-only mode: {cnmp_response.strip()}")
                        logger.warning("   Modem may fall back to 3G during calls (slow PCM, no VoLTE)")
                        self.modem_details['network_mode'] = "Unknown (AT+CNMP=38 failed)"

                # Wait for modem to stabilize after network mode change
                logger.info("⏳ Waiting 5 seconds for modem to stabilize after LTE-only mode change...")
                time.sleep(5)

                # Step 8: Verify network mode and registration status
                logger.info("⚡ Step 8: Verifying network status...")

                # Check system information (network mode, band, signal)
                ser.reset_input_buffer()
                ser.write(b"AT+CPSI?\r\n")
                time.sleep(1)
                cpsi_response = ser.read(ser.in_waiting or 500).decode('utf-8', errors='ignore')
                logger.info(f"   📡 System Info (AT+CPSI?): {cpsi_response.strip()}")

                # Parse system mode from CPSI response
                if "LTE" in cpsi_response:
                    actual_mode = "✅ LTE (VoLTE ready)"
                elif "WCDMA" in cpsi_response:
                    actual_mode = "⚠️ WCDMA (3G - VoLTE NOT available)"
                elif "GSM" in cpsi_response:
                    actual_mode = "⚠️ GSM (2G - VoLTE NOT available)"
                else:
                    actual_mode = "❓ Unknown"

                # Check network system mode (detailed mode info)
                ser.reset_input_buffer()
                ser.write(b"AT+CNSMOD?\r\n")
                time.sleep(1)
                cnsmod_response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')
                logger.info(f"   📡 Network Mode (AT+CNSMOD?): {cnsmod_response.strip()}")

                # Parse CNSMOD: 8=LTE, 7=HSPA, 4=WCDMA, 2=GPRS, 1=GSM
                if "+CNSMOD: 0,8" in cnsmod_response or "+CNSMOD: 1,8" in cnsmod_response:
                    network_tech = "LTE"
                elif "+CNSMOD: 0,7" in cnsmod_response or "+CNSMOD: 1,7" in cnsmod_response:
                    network_tech = "HSPA (3G+)"
                elif "+CNSMOD: 0,4" in cnsmod_response or "+CNSMOD: 1,4" in cnsmod_response:
                    network_tech = "WCDMA (3G)"
                elif "+CNSMOD: 0,2" in cnsmod_response or "+CNSMOD: 1,2" in cnsmod_response:
                    network_tech = "GPRS (2.5G)"
                elif "+CNSMOD: 0,1" in cnsmod_response or "+CNSMOD: 1,1" in cnsmod_response:
                    network_tech = "GSM (2G)"
                else:
                    network_tech = "Unknown"

                # Check EPS (LTE) registration status
                ser.reset_input_buffer()
                ser.write(b"AT+CEREG?\r\n")
                time.sleep(1)
                cereg_response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')
                logger.info(f"   📡 EPS Registration (AT+CEREG?): {cereg_response.strip()}")

                # Parse CEREG: 1=registered home, 5=registered roaming
                if "+CEREG: 0,1" in cereg_response or "+CEREG: 0,5" in cereg_response:
                    eps_status = "✅ Registered (VoLTE available)"
                else:
                    eps_status = "❌ Not registered (VoLTE unavailable)"

                # Step 8b: Verify APN configurations (CGDCONT)
                logger.info("⚡ Verifying APN configurations (AT+CGDCONT?)...")
                ser.reset_input_buffer()
                ser.write(b"AT+CGDCONT?\r\n")
                time.sleep(1)
                cgdcont_response = ser.read(ser.in_waiting or 600).decode('utf-8', errors='ignore')

                # Parse APN configurations
                data_apn_type = "Unknown"
                ims_apn_type = "Unknown"
                data_apn_configured = False
                ims_apn_configured = False

                for line in cgdcont_response.split('\n'):
                    if '+CGDCONT: 1,' in line:
                        if 'IP","' in line:
                            data_apn_type = "IP"
                        elif 'IPV4V6","' in line:
                            data_apn_type = "IPV4V6"
                        data_apn_configured = True
                        logger.info(f"   ✅ Context 1 (Data): {data_apn} ({data_apn_type})")
                    elif '+CGDCONT: 2,' in line:
                        if 'IPV4V6","' in line:
                            ims_apn_type = "✅ IPV4V6 (correct)"
                        elif 'IP","' in line:
                            ims_apn_type = "⚠️ IP (should be IPV4V6!)"
                        ims_apn_configured = True
                        logger.info(f"   ✅ Context 2 (IMS): {ims_apn} ({ims_apn_type})")

                # Step 8c: Verify PDP context activation (CGACT)
                logger.info("⚡ Verifying PDP context activation (AT+CGACT?)...")
                ser.reset_input_buffer()
                ser.write(b"AT+CGACT?\r\n")
                time.sleep(1)
                cgact_response = ser.read(ser.in_waiting or 300).decode('utf-8', errors='ignore')

                # Parse context activation status
                ctx1_active = "+CGACT: 1,1" in cgact_response
                ctx2_active = "+CGACT: 2,1" in cgact_response

                if ctx1_active:
                    logger.info(f"   ✅ Context 1 (Data): ACTIVE")
                else:
                    logger.warning(f"   ⚠️ Context 1 (Data): INACTIVE")

                if ctx2_active:
                    logger.info(f"   ✅ Context 2 (IMS): ACTIVE - VoLTE ready!")
                else:
                    logger.warning(f"   ⚠️ Context 2 (IMS): INACTIVE - VoLTE may not work!")

                # Store IMS/PDP status
                self.modem_details['ctx1_active'] = ctx1_active
                self.modem_details['ctx2_active'] = ctx2_active
                self.modem_details['data_apn_type'] = data_apn_type
                self.modem_details['ims_apn_type'] = ims_apn_type

                # Internet configuration complete!
                # USB composition 9001 uses wwan0 (QMI) for data, not PPP
                # Internet monitor will use wwan0 with qmicli when primary internet fails
                logger.info(f"✅ Modem configured for internet via wwan0 (QMI)")
                logger.info(f"   Data APN: {data_apn}, IMS APN: {ims_apn}")
                logger.info(f"   PDP context activated - ready for VoLTE")
                logger.info(f"   VoLTE: {self.modem_details['volte']}")
                logger.info(f"   Network Mode: {actual_mode} ({network_tech})")
                logger.info(f"   EPS Status: {eps_status}")
                logger.info(f"   Backup internet: internet-monitor will use wwan0 when WiFi fails")

                # Store network status in modem details
                self.modem_details['actual_network_mode'] = actual_mode
                self.modem_details['network_tech'] = network_tech
                self.modem_details['eps_status'] = eps_status

                self.modem_internet['interface'] = 'wwan0 (QMI)'
                self.modem_internet['ip'] = 'Ready (internet-monitor will activate)'

                return True

            except serial.SerialException as e:
                logger.error(f"Serial communication error: {e}")
                return False

        except Exception as e:
            logger.error(f"Error configuring modem internet: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def test_modem_connectivity(self, interface):
        """
        Test internet connectivity through modem interface only
        Force ping through specific interface, not WiFi/Ethernet
        """
        try:
            logger.info(f"Testing connectivity through {interface}...")

            # Ping my-bookings.co.uk through modem interface only (3 second timeout)
            result = subprocess.run(
                ['ping', '-c', '1', '-I', interface, '-W', '3', 'my-bookings.co.uk'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                # Extract average ping time
                for line in result.stdout.split('\n'):
                    if 'avg' in line or 'rtt' in line:
                        parts = line.split('/')
                        if len(parts) >= 5:
                            avg_ping = parts[4]
                            self.modem_internet['ping_test'] = f"✅ OK ({avg_ping}ms avg)"
                            logger.info(f"✅ Modem connectivity test passed: {avg_ping}ms avg")
                            return True

                self.modem_internet['ping_test'] = "✅ OK"
                logger.info("✅ Modem connectivity test passed")
                return True
            else:
                self.modem_internet['ping_test'] = "❌ Failed - no response"
                logger.error("❌ Modem connectivity test failed - no response")
                return False

        except subprocess.TimeoutExpired:
            self.modem_internet['ping_test'] = "❌ Failed - timeout (3s)"
            logger.error("❌ Modem connectivity test timed out (3s)")
            return False
        except Exception as e:
            self.modem_internet['ping_test'] = f"❌ Error: {str(e)[:30]}"
            logger.error(f"Error testing modem connectivity: {e}")
            return False

    def test_all_ports_for_at(self):
        """
        Test EVERY ttyUSB port for AT command support
        Real tests, not assumptions
        """
        try:
            logger.info("Testing all USB ports for AT command support...")

            # Get all ttyUSB devices
            devices = []
            for i in range(10):
                device = f"/dev/ttyUSB{i}"
                if os.path.exists(device):
                    devices.append(device)

            # Test each port
            for device in devices:
                port_num = device.split('ttyUSB')[1]

                # Determine port purpose (known assignments)
                purpose = {
                    '0': 'Diagnostic',
                    '1': 'GPS/NMEA',
                    '2': 'AT Commands (SMS)',
                    '3': 'AT Commands (Voice)',
                    '4': 'PCM Audio'
                }.get(port_num, 'Unknown')

                # Test AT commands (skip SMSTools port if running)
                at_support = "Unknown"

                # For ttyUSB2, need to stop SMSTools first
                if port_num == '2':
                    smstools_running = subprocess.run(
                        ['systemctl', 'is-active', 'smstools'],
                        capture_output=True,
                        text=True
                    ).stdout.strip() == 'active'

                    if smstools_running:
                        at_support = "Locked (SMSTools)"
                    else:
                        at_support = self._test_at_on_port(device)
                else:
                    at_support = self._test_at_on_port(device)

                self.port_tests[device] = {
                    'purpose': purpose,
                    'at_support': at_support
                }

                logger.info(f"{device}: {purpose} - AT: {at_support}")

        except Exception as e:
            logger.error(f"Error testing ports: {e}")

    def test_critical_ports_for_at(self):
        """
        Test only critical ports (ttyUSB2 and ttyUSB3) for AT command support
        CRITICAL: Stops SMSTools and Voice Bot before testing to avoid port conflicts
        """
        try:
            logger.info("Testing critical ports (ttyUSB2, ttyUSB3) for AT command support...")

            # STEP 1: Stop SMSTools (to release ttyUSB2)
            logger.info("Stopping SMSTools before testing ttyUSB2...")
            self.stop_smstools_temporarily()

            # STEP 2: Stop Voice Bot (to release ttyUSB3)
            logger.info("Stopping Voice Bot before testing ttyUSB3...")
            self.stop_voice_bot_service()

            # Wait for services to fully release ports
            time.sleep(2)

            critical_ports = {
                '/dev/ttyUSB2': 'AT Commands (SMS)',
                '/dev/ttyUSB3': 'AT Commands (Voice)'
            }

            # STEP 3: Test both ports with services stopped
            for device, purpose in critical_ports.items():
                if not os.path.exists(device):
                    logger.warning(f"{device}: Not found")
                    continue

                at_support = self._test_at_on_port(device)

                self.port_tests[device] = {
                    'purpose': purpose,
                    'at_support': at_support
                }

                logger.info(f"{device}: {purpose} - AT: {at_support}")

            # NOTE: SMSTools and Voice Bot will be started later in the flow
            # This ensures ports are tested cleanly without service conflicts
            logger.info("✅ Port testing complete - services will be started after configuration")

        except Exception as e:
            logger.error(f"Error testing critical ports: {e}")

    def _test_at_on_port(self, port):
        """Test a single port for AT command support"""
        try:
            with serial.Serial(port, 115200, timeout=3, write_timeout=1) as ser:
                ser.reset_input_buffer()
                ser.write(b"AT\r\n")
                time.sleep(3)  # 3 seconds - modem needs time to settle after PDP activation
                response = ser.read(ser.in_waiting or 100).decode('utf-8', errors='ignore')

                if "OK" in response:
                    return "✅ Yes (tested)"
                else:
                    # Log the response to help debug
                    logger.debug(f"Port {port} response: {response.strip()}")
                    return "❌ No response"

        except serial.SerialException as e:
            return f"❌ Cannot open ({str(e)[:30]})"
        except Exception as e:
            return f"❌ Error: {str(e)[:20]}"

    def stop_voice_bot_service(self):
        """Stop the SIM7600 voice bot service"""
        try:
            logger.info("Stopping SIM7600 voice bot service...")
            result = os.system('sudo systemctl stop sim7600-voice-bot 2>/dev/null')
            time.sleep(1)  # Wait for service to stop
            return True
        except Exception as e:
            logger.error(f"Error stopping voice bot service: {e}")
            return False

    def start_voice_bot_service(self):
        """Start the SIM7600 voice bot service"""
        try:
            # Start SIM7600 voice bot
            logger.info("Starting SIM7600 voice bot service...")
            result = os.system('sudo systemctl start sim7600-voice-bot')

            if result == 0:
                # Verify it's running
                time.sleep(2)
                status = subprocess.run(
                    ['systemctl', 'is-active', 'sim7600-voice-bot'],
                    capture_output=True,
                    text=True
                )

                if status.stdout.strip() == 'active':
                    logger.info("✅ SIM7600 voice bot service started successfully")
                    self.voice_bot_running = True
                    return True
                else:
                    logger.error(f"Service failed to stay active: {status.stdout}")
                    return False
            else:
                logger.error(f"Failed to start service: exit code {result}")
                return False

        except Exception as e:
            logger.error(f"Error starting voice bot service: {e}")
            return False

    def notify_vps(self, status, details):
        """Send notification to VPS about modem status"""
        try:
            # Determine severity based on status
            severity_map = {
                'connected': 'success',
                'disconnected': 'warning',
                'error': 'error',
                'warning': 'warning'
            }
            severity = severity_map.get(status, 'info')

            # Build comprehensive message with modem details
            if status == 'connected':
                # Build port enumeration
                port_list = ""
                for port in sorted(self.port_tests.keys()):
                    port_info = self.port_tests[port]
                    port_list += f"\n  {port}: {port_info['purpose']}"
                    port_list += f"\n    AT: {port_info['at_support']}"

                # Rich status report with all modem information
                message = f"""🟦 SIM7600 Status Report:
━━━━━━━━━━━━━━━━━━━━━━━━━━
Modem: ✅ Present
Voice Port: ✅ {self.port_mapping.get('at_command', 'N/A')}
SMS Port: ✅ {self.port_mapping.get('sms_port', 'N/A')}
USB Composition: {self.modem_details['usb_composition']}
━━━━━━━━━━━━━━━━━━━━━━━━━━
📱 Modem Info:
  • Manufacturer: {self.modem_details['manufacturer']}
  • Model: {self.modem_details['model']}
  • Firmware: {self.modem_details['firmware']}
  • IMEI: {self.modem_details['imei']}
━━━━━━━━━━━━━━━━━━━━━━━━━━
📶 Network:
  • SIM: {self.modem_details['imsi']}
  • Carrier: {self.modem_details['carrier']}
  • Signal: {self.modem_details['signal']}
  • Network Mode: {self.modem_details.get('network_mode', 'Unknown')}
  • Actual Network: {self.modem_details.get('actual_network_mode', 'Unknown')}
  • Technology: {self.modem_details.get('network_tech', 'Unknown')}
  • EPS Status: {self.modem_details.get('eps_status', 'Unknown')}
━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 Data & VoLTE:
  • Data APN: {self.modem_details['apn']} ({self.modem_details.get('data_apn_type', 'Unknown')})
  • IMS APN: {self.modem_details['ims_apn']} ({self.modem_details.get('ims_apn_type', 'Unknown')})
  • PDP Context 1 (Data): {"✅ Active" if self.modem_details.get('ctx1_active') else "❌ Inactive"}
  • PDP Context 2 (IMS): {"✅ Active" if self.modem_details.get('ctx2_active') else "❌ Inactive"}
  • VoLTE: {self.modem_details['volte']}
━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 Internet:
  • Interface: {self.modem_internet['interface'] or 'Not configured'}
  • IP: {self.modem_internet['ip'] or 'No IP'}
  • Status: ❌ NOT WORKING in USB 9001 (wwan0 visible but QMI fails)
  • Note: Switch to USB composition 1025 for working internet
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌 USB Ports (Tested):{port_list}"""
            else:
                # Simple message for non-connected states
                message = f"SIM7600 {status.upper()}: {details.get('message', 'Status update')}"

            # PRIMARY METHOD: Use pi_send_message.sh (goes to port 5000)
            logger.info(f"Notifying VPS: {status}")

            result = subprocess.run(
                ['/home/rom/pi_send_message.sh', 'custom', message, severity],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.info(f"✅ VPS notified via pi_send_message: {status}")
                if LOG_MODE == 'development':
                    logger.debug(f"Response: {result.stdout}")
            else:
                logger.error(f"pi_send_message failed: {result.stderr}")

            # Log detailed info locally for debugging
            if LOG_MODE == 'development':
                logger.debug(f"Detection count: {self.detection_count}")
                logger.debug(f"Port mapping: {json.dumps(self.port_mapping, indent=2)}")
                logger.debug(f"Modem details: {json.dumps(self.modem_details, indent=2)}")

        except Exception as e:
            logger.error(f"Failed to notify VPS: {e}")

    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting monitor loop...")

        # CRITICAL: Clean up any running services from previous sessions
        logger.info("🧹 Cleaning up services from previous sessions...")
        logger.info("Stopping SMSTools if running...")
        os.system('sudo systemctl stop smstools 2>/dev/null')
        logger.info("Stopping Voice Bot if running...")
        os.system('sudo systemctl stop sim7600-voice-bot 2>/dev/null')
        time.sleep(2)  # Wait for services to fully stop
        logger.info("✅ Service cleanup complete")

        check_interval = 10  # Check every 10 seconds (both dev and production)

        while True:
            try:
                devices = self.detect_usb_devices()

                if devices and not self.modem_detected:
                    # New devices detected
                    logger.info(f"USB devices detected: {len(devices)}")

                    # Wait 4 seconds for modem to initialize serial ports after USB enumeration
                    # This prevents first-attempt failures when modem ports aren't ready yet
                    logger.info("⏳ Waiting 4 seconds for modem initialization...")
                    time.sleep(4)
                    logger.info("✅ Initialization wait complete, testing modem...")

                    if self.verify_sim7600_ports(devices):
                        self.modem_detected = True
                        self.detection_count += 1
                        self.last_detection = datetime.now()

                        logger.info("="*60)
                        logger.info("🎉 SIM7600 DETECTED AND VERIFIED")
                        logger.info("="*60)

                        # Check critical ports
                        if self.check_critical_ports():
                            # Save port mapping
                            self.save_port_mapping()

                            # PRODUCTION CONFIGURATION
                            logger.info("Configuring modem for production use...")

                            # 1. Enable AT commands on ttyUSB3 (voice port)
                            # DISABLED - ttyUSB3 typically works out-of-box on SIM7600
                            # Only enable if you get "No AT response" errors on ttyUSB3
                            # if not self.configure_ttyusb3_for_at():
                            #     logger.error("Failed to configure ttyUSB3 for AT commands")
                            logger.info("ℹ️ USB reconfiguration skipped (ttyUSB3 works by default)")

                            # 2. CRITICAL: Enable and configure modem internet (REQUIRED FOR VoLTE!)
                            # VoLTE needs active PDP context for 4G voice calls
                            # 2G/3G being deprecated across Europe - VoLTE is mandatory
                            logger.info("🔴 CRITICAL: Configuring internet for VoLTE support...")
                            if not self.configure_modem_internet():
                                logger.error("❌ Internet configuration failed - VoLTE may not work!")
                                logger.error("   Voice calls will fail when 2G/3G networks shut down!")

                            # Wait for modem to settle (increased from 2s to 5s for stability)
                            # PDP context activation (AT+CGACT) temporarily makes ports unresponsive
                            logger.info("⏳ Waiting 5 seconds for modem to settle...")
                            time.sleep(5)

                            # 3. Test critical ports for AT command support (ttyUSB2, ttyUSB3)
                            self.test_critical_ports_for_at()

                            # 4. Notify VPS BEFORE starting services
                            # This ensures VPS gets status immediately after configuration
                            self.notify_vps('connected', {
                                'message': 'SIM7600 connected and configured',
                                'voice_ready': True
                            })

                            # 5. Restart SMSTools before starting voice bot
                            # This ensures SMS service is ready and ttyUSB2 is properly configured
                            self.restart_smstools()

                            # 6. Start voice bot service
                            if self.start_voice_bot_service():
                                logger.info("✅ Voice bot started successfully")

                                # Start monitoring service logs
                                threading.Thread(
                                    target=self.monitor_service_logs,
                                    daemon=True
                                ).start()
                            else:
                                logger.error("❌ Voice bot failed to start")
                                # Note: VPS already notified of configuration success above
                        else:
                            # Critical ports check failed - do NOT restart SMSTools
                            # SMSTools should only run after successful configuration
                            logger.warning("Critical ports check failed - waiting for next detection cycle")
                            self.notify_vps('warning', {
                                'message': 'SIM7600 detected but critical ports missing',
                                'voice_ready': False
                            })
                    else:
                        # Modem verification failed - do NOT restart SMSTools
                        # SMSTools should only run after successful configuration
                        logger.warning("Modem verification failed - waiting for next detection cycle")

                elif not devices and self.modem_detected:
                    # Modem disconnected - use grace period to avoid service restart on brief disconnects
                    if not self.disconnect_grace_active:
                        # First detection of disconnect - start grace period
                        self.disconnect_start_time = time.time()
                        self.disconnect_grace_active = True
                        logger.warning(f"⚠️ SIM7600 disconnected - starting {self.DISCONNECT_GRACE_PERIOD}s grace period (modem reset protection)...")
                    else:
                        # Check if grace period has expired
                        elapsed = time.time() - self.disconnect_start_time
                        if elapsed >= self.DISCONNECT_GRACE_PERIOD:
                            # Grace period expired - modem truly disconnected
                            logger.error(f"❌ SIM7600 still disconnected after {self.DISCONNECT_GRACE_PERIOD}s - stopping services")
                            self.modem_detected = False
                            self.voice_bot_running = False
                            self.disconnect_grace_active = False

                            # Stop voice bot service
                            subprocess.run(['sudo', 'systemctl', 'stop', 'sim7600-voice-bot'],
                                         capture_output=True)

                            # Stop smstools service (no longer needed without modem)
                            logger.info("Stopping smstools service...")
                            subprocess.run(['sudo', 'systemctl', 'stop', 'smstools'],
                                         capture_output=True)

                            self.notify_vps('disconnected', {
                                'message': 'SIM7600 disconnected',
                                'voice_ready': False
                            })
                        else:
                            # Still within grace period - keep waiting
                            logger.info(f"⏳ Modem disconnected - grace period active ({elapsed:.0f}s / {self.DISCONNECT_GRACE_PERIOD}s)")

                # Reset grace period if modem is connected
                if devices and self.modem_detected and self.disconnect_grace_active:
                    logger.info("✅ Modem reconnected during grace period - canceling disconnect")
                    self.disconnect_grace_active = False
                    self.disconnect_start_time = None

                # Check service health if running
                if self.voice_bot_running:
                    status = subprocess.run(
                        ['systemctl', 'is-active', 'sim7600-voice-bot'],
                        capture_output=True,
                        text=True
                    )

                    if status.stdout.strip() != 'active':
                        logger.error("Voice bot service died, restarting...")
                        self.start_voice_bot_service()

                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Shutting down detector...")
                break
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(check_interval)

    def monitor_service_logs(self):
        """Monitor voice bot service logs in background"""
        logger.info("Starting service log monitor...")

        try:
            # Follow journalctl for the service
            process = subprocess.Popen(
                ['sudo', 'journalctl', '-f', '-u', 'sim7600-voice-bot', '--no-pager'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            for line in iter(process.stdout.readline, ''):
                if line:
                    # Parse and forward important messages (match actual log level, not just word in message)
                    if ' - ERROR - ' in line or ' - CRITICAL - ' in line:
                        logger.error(f"Voice Bot: {line.strip()}")
                    elif ' - WARNING - ' in line:
                        logger.warning(f"Voice Bot: {line.strip()}")
                    elif LOG_MODE == 'development':
                        # Use simple print with icon instead of logger.debug for cleaner output
                        print(f"📱 Voice-Bot: {line.strip()}")

        except Exception as e:
            logger.error(f"Log monitor error: {e}")

def main():
    """Main entry point"""
    try:
        # Create log directory if needed
        Path('/var/log').mkdir(exist_ok=True)

        detector = SIM7600Detector()
        detector.monitor_loop()

    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()