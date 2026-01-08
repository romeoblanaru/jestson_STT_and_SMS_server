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
            'volte': 'Unknown'
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

        # Typical SIM7600 port layout (per documentation)
        # ttyUSB0 - Diagnostic
        # ttyUSB1 - GPS/NMEA
        # ttyUSB2 - AT Commands (SMSTools ONLY - locked for SMS)
        # ttyUSB3 - Voice AT Commands (NO PPP - dedicated to voice bot)
        # ttyUSB4 - PCM Audio
        # Internet uses RNDIS/ECM (usb0), NOT PPP on ttyUSB3
        self.port_mapping = {
            'diagnostic': devices[0] if len(devices) > 0 else None,
            'nmea': devices[1] if len(devices) > 1 else None,
            'sms_port': devices[2] if len(devices) > 2 else None,  # SMSTools only (ttyUSB2)
            'at_command': devices[3] if len(devices) > 3 else None,  # Voice bot AT (ttyUSB3)
            'audio': devices[4] if len(devices) > 4 else None  # PCM audio (ttyUSB4)
        }

        # Verify AT command port
        at_port = self.port_mapping['at_command']
        if not at_port:
            logger.error("No AT command port found")
            return False

        # For detection, use ttyUSB2 temporarily (need to stop SMSTools)
        # Voice bot will use ttyUSB3 (no conflict)
        sms_port = devices[2] if len(devices) > 2 else None
        if not sms_port:
            logger.error("No SMS/AT port found for detection")
            return False

        # CRITICAL: Stop smstools before AT commands on ttyUSB2
        smstools_was_running = self.stop_smstools_temporarily()

        try:
            # Test AT commands to confirm it's SIM7600 (using ttyUSB2 temporarily)
            # Use short timeout to prevent freezes
            with serial.Serial(sms_port, 115200, timeout=1, write_timeout=1) as ser:
                ser.write(b"AT\r\n")
                time.sleep(1)  # TEST #3: Increased to 1s
                response = ser.read(100).decode('utf-8', errors='ignore')

                if "OK" not in response:
                    logger.debug(f"No OK response from {at_port}")
                    return False

                # Check manufacturer
                ser.write(b"AT+CGMI\r\n")
                time.sleep(1)  # TEST #3: Increased to 1s
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

            # AT+CIMI - Get IMSI (SIM card number)
            ser.reset_input_buffer()
            ser.write(b"AT+CIMI\r\n")
            time.sleep(1)  # TEST #3: Increased to 1s
            response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')
            for line in response.split('\n'):
                line = line.strip()
                if line.isdigit() and len(line) >= 14:
                    self.modem_details['imsi'] = line
                    break

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
            if "+CEVOLTE:" in response:
                try:
                    status = response.split('+CEVOLTE:')[1].split(',')[0].strip()
                    self.modem_details['volte'] = "✅" if status == "1" else "❌"
                except:
                    self.modem_details['volte'] = "❌"
            else:
                self.modem_details['volte'] = "❌"

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

    def configure_modem_internet(self):
        """
        Configure modem for internet via RNDIS/ECM (usb0/wwan0)
        This allows internet without blocking ttyUSB3 for voice
        """
        try:
            logger.info("Configuring modem internet (RNDIS/ECM)...")

            # Get APN from modem details
            apn = self.modem_details.get('apn', 'internet')
            if apn == 'Unknown':
                apn = 'internet'  # Fallback

            logger.info(f"Using APN: {apn}")

            # Use ttyUSB3 for configuration (now that it supports AT)
            voice_port = self.port_mapping.get('at_command')
            if not voice_port:
                logger.error("No voice port available for internet configuration")
                return False

            try:
                with serial.Serial(voice_port, 115200, timeout=3, write_timeout=1) as ser:
                    # ========================================
                    # GRADUAL POWER RAMP-UP TO REDUCE EMI
                    # ========================================

                    # Step 1: Turn radio OFF completely
                    logger.info("📻 Step 1: Turning radio OFF (AT+CFUN=0)...")
                    ser.reset_input_buffer()
                    ser.write(b"AT+CFUN=0\r\n")
                    time.sleep(3)  # Wait 3s for radio to power down
                    response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')
                    logger.info(f"   Radio OFF response: {response.strip()}")

                    # Step 2: Turn radio ON at minimal power
                    logger.info("📻 Step 2: Turning radio ON minimal (AT+CFUN=1)...")
                    ser.reset_input_buffer()
                    ser.write(b"AT+CFUN=1\r\n")
                    time.sleep(3)  # Wait 3s for radio to stabilize
                    response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')
                    logger.info(f"   Radio ON response: {response.strip()}")

                    # Step 3: Configure APN
                    logger.info(f"📡 Step 3: Configuring APN: {apn}...")
                    ser.reset_input_buffer()
                    ser.write(b"AT+CGDCONT=1,\"IP\",\"" + apn.encode() + b"\"\r\n")
                    time.sleep(1)
                    response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')

                    if "OK" not in response:
                        logger.error(f"Failed to set APN: {response}")
                        return False

                    logger.info("✅ APN configured")

                    # Step 4: Wait for network to settle (EMI mitigation)
                    logger.info("⏳ Step 4: Waiting 7 seconds for network to settle...")
                    time.sleep(7)

                    # Step 5: Activate PDP context (HIGH POWER - EMI risk)
                    logger.info("⚡ Step 5: Activating PDP context (AT+CGACT=1,1)...")
                    logger.warning("   ⚠️ HIGH POWER TRANSMISSION - watch for EMI!")
                    ser.reset_input_buffer()
                    ser.write(b"AT+CGACT=1,1\r\n")
                    time.sleep(1)
                    response = ser.read(ser.in_waiting or 200).decode('utf-8', errors='ignore')

                    logger.info("PDP context activated")

                # Wait for network interface to appear
                time.sleep(3)

                # Check for usb0 or wwan0
                result = subprocess.run(
                    ['ip', 'link', 'show'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if 'usb0' in result.stdout or 'wwan0' in result.stdout:
                    interface = 'usb0' if 'usb0' in result.stdout else 'wwan0'
                    logger.info(f"✅ Network interface {interface} detected")

                    # Bring up interface and get DHCP with LOW PRIORITY (high metric)
                    # This ensures WAN/WiFi stay as primary internet
                    subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], timeout=5)

                    # Kill any existing dhclient for this interface
                    subprocess.run(['sudo', 'pkill', '-f', f'dhclient.*{interface}'],
                                 capture_output=True, timeout=5)

                    # Get DHCP
                    dhcp_result = subprocess.run(['sudo', 'dhclient', '-v', interface],
                                                capture_output=True, text=True, timeout=10)

                    # Get IP address
                    time.sleep(1)
                    ip_result = subprocess.run(['ip', 'addr', 'show', interface],
                                             capture_output=True, text=True, timeout=5)

                    modem_ip = None
                    for line in ip_result.stdout.split('\n'):
                        if 'inet ' in line and 'inet6' not in line:
                            modem_ip = line.strip().split()[1].split('/')[0]
                            break

                    self.modem_internet['interface'] = interface
                    self.modem_internet['ip'] = modem_ip or 'No IP assigned'

                    logger.info(f"✅ Modem internet configured on {interface} - IP: {modem_ip}")

                    # FIX ROUTING: Set modem as BACKUP (lowest priority)
                    # Priority: 1. WAN (metric ~100), 2. WiFi (metric ~600), 3. Modem (metric 1000)
                    logger.info("Setting modem route as backup (lowest priority)...")

                    # Remove any default route added by dhclient for this interface
                    subprocess.run(['sudo', 'ip', 'route', 'del', 'default', 'dev', interface],
                                 capture_output=True, timeout=5)

                    # Get gateway from interface routes
                    route_info = subprocess.run(['ip', 'route', 'show', 'dev', interface],
                                              capture_output=True, text=True, timeout=5)

                    # Find gateway and add default route with LOW PRIORITY (metric 1000)
                    gateway = None
                    for line in route_info.stdout.split('\n'):
                        if 'via' in line:
                            parts = line.split()
                            if 'via' in parts:
                                gateway_idx = parts.index('via') + 1
                                if gateway_idx < len(parts):
                                    gateway = parts[gateway_idx]
                                    break

                    if gateway:
                        subprocess.run([
                            'sudo', 'ip', 'route', 'add', 'default',
                            'via', gateway, 'dev', interface, 'metric', '1000'
                        ], capture_output=True, timeout=5)
                        logger.info(f"✅ Modem route added with metric 1000 (backup only)")
                    else:
                        logger.warning("Could not determine gateway for modem interface")

                    # Test connectivity through modem (force route through modem interface)
                    self.test_modem_connectivity(interface)

                    return True
                else:
                    logger.warning("⚠️ No usb0/wwan0 interface found - internet may not be available")
                    return False

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
        Faster than testing all ports, focuses on what matters for SMS and voice
        """
        try:
            logger.info("Testing critical ports (ttyUSB2, ttyUSB3) for AT command support...")

            critical_ports = {
                '/dev/ttyUSB2': 'AT Commands (SMS)',
                '/dev/ttyUSB3': 'AT Commands (Voice)'
            }

            for device, purpose in critical_ports.items():
                if not os.path.exists(device):
                    logger.warning(f"{device}: Not found")
                    continue

                port_num = device.split('ttyUSB')[1]
                at_support = "Unknown"

                # For ttyUSB2, check if SMSTools is running
                if port_num == '2':
                    smstools_running = subprocess.run(
                        ['systemctl', 'is-active', 'smstools'],
                        capture_output=True,
                        text=True
                    ).stdout.strip() == 'active'

                    if smstools_running:
                        at_support = "✅ Locked (SMSTools) - Expected"
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
            logger.error(f"Error testing critical ports: {e}")

    def _test_at_on_port(self, port):
        """Test a single port for AT command support"""
        try:
            with serial.Serial(port, 115200, timeout=1, write_timeout=1) as ser:
                ser.reset_input_buffer()
                ser.write(b"AT\r\n")
                time.sleep(0.3)
                response = ser.read(ser.in_waiting or 100).decode('utf-8', errors='ignore')

                if "OK" in response:
                    return "✅ Yes (tested)"
                else:
                    return "❌ No response"

        except serial.SerialException:
            return "❌ Cannot open"
        except Exception as e:
            return f"❌ Error: {str(e)[:20]}"

    def start_voice_bot_service(self):
        """Start the SIM7600 voice bot service"""
        try:
            # Stop any existing EC25 voice bot
            logger.info("Stopping EC25 voice bot if running...")
            os.system('sudo systemctl stop ec25-voice-bot 2>/dev/null')

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
  • APN: {self.modem_details['apn']}
  • VoLTE: {self.modem_details['volte']}
━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 Internet:
  • Interface: {self.modem_internet['interface'] or 'Not configured'}
  • IP: {self.modem_internet['ip'] or 'No IP'}
  • Ping Test (my-bookings.co.uk): {self.modem_internet['ping_test']}
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌 USB Ports (Tested):{port_list}"""
            else:
                # Simple message for non-connected states
                message = f"SIM7600 {status.upper()}: {details.get('message', 'Status update')}"

            # PRIMARY METHOD: Use pi_send_message.sh (goes to port 5000)
            logger.info(f"Notifying VPS: {status}")

            result = subprocess.run(
                ['/home/rom/pi_send_message.sh', message, severity],
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
                            if not self.configure_ttyusb3_for_at():
                                logger.error("Failed to configure ttyUSB3 for AT commands")

                            # 2. Enable and configure modem internet (RNDIS/ECM)
                            # RE-ENABLED FOR TEST #3 (2025-10-14) with 1s delays between AT commands
                            if not self.configure_modem_internet():
                                logger.warning("Failed to configure modem internet")

                            # Wait 2 seconds for modem to settle after internet configuration
                            # PDP context activation (AT+CGACT) temporarily makes ports unresponsive
                            logger.info("⏳ Waiting 2 seconds for modem to settle after internet config...")
                            time.sleep(2)

                            # 3. Test critical ports for AT command support (ttyUSB2, ttyUSB3)
                            self.test_critical_ports_for_at()

                            # 4. Restart SMSTools before starting voice bot
                            # This ensures SMS service is ready and ttyUSB2 is properly configured
                            self.restart_smstools()

                            # Start voice bot service
                            if self.start_voice_bot_service():
                                # Notify VPS of success
                                self.notify_vps('connected', {
                                    'message': 'SIM7600 connected and voice bot started',
                                    'voice_ready': True
                                })

                                # Start monitoring service logs
                                threading.Thread(
                                    target=self.monitor_service_logs,
                                    daemon=True
                                ).start()
                            else:
                                self.notify_vps('error', {
                                    'message': 'SIM7600 detected but voice bot failed to start',
                                    'voice_ready': False
                                })
                        else:
                            # Critical ports check failed - restart SMSTools and notify
                            logger.warning("Critical ports check failed - restarting SMSTools")
                            self.restart_smstools()
                            self.notify_vps('warning', {
                                'message': 'SIM7600 detected but critical ports missing',
                                'voice_ready': False
                            })
                    else:
                        # Modem detection failed - restart SMSTools for next attempt
                        logger.warning("Modem verification failed - restarting SMSTools")
                        self.restart_smstools()

                elif not devices and self.modem_detected:
                    # Modem disconnected
                    logger.warning("SIM7600 disconnected!")
                    self.modem_detected = False
                    self.voice_bot_running = False

                    # Stop voice bot service
                    subprocess.run(['sudo', 'systemctl', 'stop', 'sim7600-voice-bot'],
                                 capture_output=True)

                    self.notify_vps('disconnected', {
                        'message': 'SIM7600 disconnected',
                        'voice_ready': False
                    })

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
                    # Parse and forward important messages
                    if 'ERROR' in line or 'CRITICAL' in line:
                        logger.error(f"Voice Bot: {line.strip()}")
                    elif 'WARNING' in line:
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