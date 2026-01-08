#!/usr/bin/env python3
"""
Enhanced SIM7600 Detector with Full Configuration
Configures modem on USB insertion for SMS, Voice, and Data
"""

import os
import sys
import time
import json
import serial
import subprocess
import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/voice_bot/sim7600_detector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('sim7600_detector')

class SIM7600Detector:
    """Enhanced modem detector with full configuration"""

    def __init__(self):
        self.modem_detected = False
        self.modem_info = {}
        self.carrier_db = self.load_carrier_database()
        self.vpn_ip = self.get_vpn_ip()

    def get_vpn_ip(self) -> str:
        """Get VPN IP address"""
        try:
            result = subprocess.run(
                ['ip', '-4', 'addr', 'show', 'wg0'],
                capture_output=True, text=True, timeout=2
            )
            for line in result.stdout.split('\n'):
                if 'inet ' in line:
                    return line.split()[1].split('/')[0]
        except:
            pass
        return '10.100.0.11'

    def load_carrier_database(self) -> Dict:
        """Load carrier configuration database"""
        try:
            with open('/home/rom/modem_manager/config/carriers.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load carrier database: {e}")
            return {}

    def detect_modem(self) -> bool:
        """Detect SIM7600 modem via USB"""
        try:
            result = subprocess.run(
                ['lsusb'], capture_output=True, text=True, timeout=5
            )

            # Check for SIM7600 USB IDs
            if '1e0e:9011' in result.stdout or '1e0e:9001' in result.stdout:
                logger.info("✅ SIM7600G-H modem detected!")
                self.modem_detected = True

                # Map USB ports
                self.map_usb_ports()
                return True

            logger.warning("No SIM7600 modem detected")
            return False

        except Exception as e:
            logger.error(f"Modem detection error: {e}")
            return False

    def map_usb_ports(self):
        """Map USB serial ports to functions"""
        port_mapping = {
            '/dev/ttyUSB0': 'diagnostic',
            '/dev/ttyUSB1': 'gps',
            '/dev/ttyUSB2': 'at_primary',
            '/dev/ttyUSB3': 'at_secondary',
            '/dev/ttyUSB4': 'audio_pcm'
        }

        self.ports = {}
        for port, function in port_mapping.items():
            if os.path.exists(port):
                self.ports[function] = port
                logger.info(f"  {function}: {port}")

        # Save port mapping
        with open('/home/rom/sim7600_ports.json', 'w') as f:
            json.dump(self.ports, f, indent=2)

    def send_at_command(self, ser: serial.Serial, command: str, timeout: float = 2.0) -> str:
        """Send AT command and get response"""
        try:
            ser.write(f"{command}\r\n".encode())
            ser.flush()

            response = ""
            start_time = time.time()

            while time.time() - start_time < timeout:
                if ser.in_waiting:
                    chunk = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
                    response += chunk
                    if 'OK' in response or 'ERROR' in response:
                        break
                time.sleep(0.05)

            return response

        except Exception as e:
            logger.error(f"AT command error: {e}")
            return ""

    def configure_modem(self) -> bool:
        """Configure modem with all necessary settings"""
        try:
            logger.info("=" * 60)
            logger.info("Starting SIM7600 Professional Configuration")
            logger.info("=" * 60)

            # Stop services temporarily
            logger.info("Stopping services for configuration...")
            subprocess.run(['sudo', 'systemctl', 'stop', 'smstools'], timeout=5)
            subprocess.run(['sudo', 'systemctl', 'stop', 'sim7600-voice-bot'], timeout=5)
            time.sleep(2)

            # Open AT port
            at_port = self.ports.get('at_primary', '/dev/ttyUSB2')
            ser = serial.Serial(at_port, 115200, timeout=1)

            # 1. Basic initialization
            logger.info("\n1. Basic Initialization")
            logger.info("-" * 40)

            response = self.send_at_command(ser, "AT")
            if "OK" not in response:
                logger.error("Modem not responding!")
                return False

            self.send_at_command(ser, "ATE0")  # Disable echo

            # Get modem info
            response = self.send_at_command(ser, "ATI")
            logger.info(f"Modem: {response.split('Revision:')[0].strip()}")

            # Get firmware version
            response = self.send_at_command(ser, "AT+CGMR")
            if "CGMR:" in response:
                firmware = response.split("CGMR:")[1].split("\n")[0].strip()
                self.modem_info['firmware'] = firmware
                logger.info(f"Firmware: {firmware}")

            # Get IMEI
            response = self.send_at_command(ser, "AT+CGSN")
            if response and len(response) > 10:
                imei = ''.join(filter(str.isdigit, response))[:15]
                self.modem_info['imei'] = imei
                logger.info(f"IMEI: {imei}")

            # 2. SIM Card Configuration
            logger.info("\n2. SIM Card Check")
            logger.info("-" * 40)

            response = self.send_at_command(ser, "AT+CPIN?")
            if "READY" in response:
                logger.info("✅ SIM card ready")
                self.modem_info['sim_status'] = 'ready'
            else:
                logger.error(f"❌ SIM card issue: {response}")
                self.modem_info['sim_status'] = 'error'

            # Get IMSI
            response = self.send_at_command(ser, "AT+CIMI")
            if response and len(response) > 10:
                imsi = ''.join(filter(str.isdigit, response))[:15]
                self.modem_info['imsi'] = imsi
                logger.info(f"IMSI: {imsi}")

                # Identify carrier
                mcc_mnc = f"{imsi[:3]}-{imsi[3:5]}"
                carrier_info = self.carrier_db.get('carriers', {}).get(mcc_mnc, {})
                if carrier_info:
                    self.modem_info['carrier'] = carrier_info.get('name', 'Unknown')
                    self.modem_info['country'] = carrier_info.get('country', 'Unknown')
                    logger.info(f"Carrier: {self.modem_info['carrier']} ({self.modem_info['country']})")

            # 3. Network Configuration
            logger.info("\n3. Network Configuration")
            logger.info("-" * 40)

            # Set network mode (automatic)
            self.send_at_command(ser, "AT+CNMP=2")  # Automatic mode
            logger.info("Network mode: Automatic")

            # Check registration
            response = self.send_at_command(ser, "AT+CREG?")
            if ",1" in response or ",5" in response:
                logger.info("✅ Network registered")
                self.modem_info['network_status'] = 'registered'
            else:
                logger.warning("⚠️ Not registered on network")
                self.modem_info['network_status'] = 'not_registered'

            # Signal strength
            response = self.send_at_command(ser, "AT+CSQ")
            if "+CSQ:" in response:
                rssi = response.split("+CSQ:")[1].split(",")[0].strip()
                self.modem_info['signal_strength'] = rssi
                signal_db = -113 + (int(rssi) * 2) if rssi.isdigit() else 0
                logger.info(f"Signal: {rssi}/31 ({signal_db} dBm)")

            # 4. APN Configuration
            logger.info("\n4. APN Configuration")
            logger.info("-" * 40)

            if 'carrier' in self.modem_info and carrier_info:
                apn = carrier_info.get('data_apn', '')
                if apn:
                    # Configure data APN
                    cmd = f'AT+CGDCONT=1,"IP","{apn}"'
                    self.send_at_command(ser, cmd)
                    logger.info(f"Data APN: {apn}")

                    # Configure IMS APN for VoLTE
                    ims_apn = carrier_info.get('ims_apn', 'ims')
                    cmd = f'AT+CGDCONT=2,"IPV4V6","{ims_apn}"'
                    self.send_at_command(ser, cmd)
                    logger.info(f"IMS APN: {ims_apn}")

            # 5. VoLTE Configuration
            logger.info("\n5. VoLTE/IMS Configuration")
            logger.info("-" * 40)

            # Enable VoLTE
            self.send_at_command(ser, 'AT+CVOLTE=1')
            logger.info("VoLTE: Enabled")

            # Enable IMS
            self.send_at_command(ser, 'AT+CIMS=1')
            logger.info("IMS: Enabled")

            # Check VoLTE status
            response = self.send_at_command(ser, 'AT+CVOLTE?')
            if "+CVOLTE: 1" in response:
                logger.info("✅ VoLTE active")
                self.modem_info['volte'] = 'enabled'
            else:
                logger.warning("⚠️ VoLTE not active")
                self.modem_info['volte'] = 'disabled'

            # 6. Voice Call Configuration
            logger.info("\n6. Voice Call Configuration")
            logger.info("-" * 40)

            # Enable caller ID
            self.send_at_command(ser, "AT+CLIP=1")
            logger.info("Caller ID: Enabled")

            # Configure audio
            self.send_at_command(ser, "AT+CSDVC=2")  # Speaker
            logger.info("Audio device: Speaker")

            # Load voice config and set auto-answer
            try:
                with open('/home/rom/voice_config.json', 'r') as f:
                    voice_config = json.load(f)
                    answer_rings = voice_config.get('answer_after_rings', 2)

                    if answer_rings > 0:
                        self.send_at_command(ser, f"ATS0={answer_rings}")
                        logger.info(f"Auto-answer: {answer_rings} rings")
                    else:
                        self.send_at_command(ser, "ATS0=0")
                        logger.info("Auto-answer: Disabled")
            except:
                self.send_at_command(ser, "ATS0=2")
                logger.info("Auto-answer: 2 rings (default)")

            # 7. SMS Configuration
            logger.info("\n7. SMS Configuration")
            logger.info("-" * 40)

            # Set SMS format to text mode
            self.send_at_command(ser, "AT+CMGF=1")
            logger.info("SMS mode: Text")

            # Enable SMS notifications
            self.send_at_command(ser, "AT+CNMI=2,1,0,0,0")
            logger.info("SMS notifications: Enabled")

            # Set SMS center if available
            response = self.send_at_command(ser, "AT+CSCA?")
            if "+CSCA:" in response:
                smsc = response.split('"')[1] if '"' in response else "Unknown"
                self.modem_info['sms_center'] = smsc
                logger.info(f"SMS Center: {smsc}")

            # 8. Internet Configuration (RNDIS/ECM Mode)
            logger.info("\n8. Internet Configuration (RNDIS/ECM)")
            logger.info("-" * 40)

            # Configure for RNDIS/ECM mode (network interface) instead of PPP
            # This avoids conflicts with voice/SMS on serial ports

            # Enable network interface mode
            self.send_at_command(ser, "AT+CUSBPIDSWITCH=9011,1,1")  # Ensure PID 9011 with RNDIS
            logger.info("USB mode: RNDIS/ECM enabled")

            # Set up data connection
            self.send_at_command(ser, "AT+CGACT=1,1")  # Activate PDP context
            time.sleep(1)

            # Start network interface
            response = self.send_at_command(ser, "AT+NETOPEN")
            if "OK" in response or "already" in response.lower():
                logger.info("✅ Network interface opened")
                self.modem_info['data_status'] = 'active'

                # Get IP address
                response = self.send_at_command(ser, "AT+IPADDR")
                if response:
                    logger.info(f"Modem IP: {response}")
            else:
                # Try alternative command for SIM7600
                self.send_at_command(ser, "AT+CIICR")  # Bring up wireless connection
                time.sleep(2)

                response = self.send_at_command(ser, "AT+CIFSR")  # Get local IP
                if response and "." in response:
                    logger.info(f"✅ Data connection active: {response}")
                    self.modem_info['data_status'] = 'active'
                else:
                    logger.warning("⚠️ Data connection not active")
                    self.modem_info['data_status'] = 'inactive'

            # Close serial port
            ser.close()

            # 9. Configure Network Interface
            logger.info("\n9. Network Interface Configuration")
            logger.info("-" * 40)

            # Check for RNDIS/ECM network interface
            try:
                result = subprocess.run(
                    ['ls', '/sys/class/net/'],
                    capture_output=True, text=True, timeout=2
                )

                # Look for usb0, wwan0, or similar interfaces
                interfaces = result.stdout.strip().split()
                modem_interface = None

                for iface in interfaces:
                    if iface.startswith(('usb', 'wwan', 'rmnet')):
                        modem_interface = iface
                        logger.info(f"Found modem network interface: {iface}")
                        break

                if modem_interface:
                    # Bring up the interface
                    subprocess.run(['sudo', 'ip', 'link', 'set', modem_interface, 'up'], timeout=2)
                    time.sleep(1)

                    # Request DHCP
                    subprocess.run(['sudo', 'dhclient', '-v', modem_interface], timeout=5)
                    logger.info(f"✅ Network interface {modem_interface} configured")

                    # Check IP address
                    result = subprocess.run(
                        ['ip', 'addr', 'show', modem_interface],
                        capture_output=True, text=True, timeout=2
                    )
                    if 'inet ' in result.stdout:
                        ip_line = [l for l in result.stdout.split('\n') if 'inet ' in l][0]
                        ip_addr = ip_line.split()[1]
                        logger.info(f"Interface IP: {ip_addr}")
                        self.modem_info['interface_ip'] = ip_addr
                else:
                    logger.warning("No modem network interface found - using PPP fallback")

            except Exception as e:
                logger.error(f"Network interface configuration error: {e}")

            # 10. Test Internet Connectivity
            logger.info("\n10. Internet Connectivity Test")
            logger.info("-" * 40)

            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '2', '8.8.8.8'],
                    capture_output=True, timeout=3
                )
                if result.returncode == 0:
                    logger.info("✅ Internet connectivity OK")
                    self.modem_info['internet'] = 'connected'
                else:
                    logger.warning("⚠️ No internet connectivity")
                    self.modem_info['internet'] = 'disconnected'
            except:
                self.modem_info['internet'] = 'unknown'

            # Save modem info
            with open('/var/log/voice_bot/sim7600_info.json', 'w') as f:
                json.dump(self.modem_info, f, indent=2)

            # Restart services
            logger.info("\n11. Restarting Services")
            logger.info("-" * 40)

            subprocess.run(['sudo', 'systemctl', 'start', 'smstools'], timeout=5)
            logger.info("✅ SMSTools started")

            subprocess.run(['sudo', 'systemctl', 'start', 'sim7600-voice-bot'], timeout=5)
            logger.info("✅ Voice bot started")

            # Notify VPS
            self.notify_vps_configuration()

            logger.info("\n" + "=" * 60)
            logger.info("✅ SIM7600 Configuration Complete!")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Configuration error: {e}")
            # Ensure services are restarted
            subprocess.run(['sudo', 'systemctl', 'start', 'smstools'], timeout=5)
            subprocess.run(['sudo', 'systemctl', 'start', 'sim7600-voice-bot'], timeout=5)
            return False

    def notify_vps_configuration(self):
        """Notify VPS about modem configuration"""
        try:
            # Send via pi_send_message.sh
            message = (
                f"SIM7600 Configured:\\n"
                f"Carrier: {self.modem_info.get('carrier', 'Unknown')}\\n"
                f"Signal: {self.modem_info.get('signal_strength', '?')}/31\\n"
                f"VoLTE: {self.modem_info.get('volte', 'unknown')}\\n"
                f"Internet: {self.modem_info.get('internet', 'unknown')}"
            )

            subprocess.run(
                ['/home/rom/pi_send_message.sh', message],
                timeout=5
            )

            logger.info("VPS notified of configuration")

        except Exception as e:
            logger.error(f"VPS notification error: {e}")

    def run(self):
        """Main run method"""
        logger.info("SIM7600 Enhanced Detector Starting...")

        # Detect modem
        if not self.detect_modem():
            logger.error("No SIM7600 modem found!")
            return False

        # Configure modem
        if not self.configure_modem():
            logger.error("Configuration failed!")
            return False

        return True

def main():
    """Main entry point"""
    detector = SIM7600Detector()
    success = detector.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()