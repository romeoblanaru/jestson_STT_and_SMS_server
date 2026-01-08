#!/usr/bin/env python3
"""
Internet Connection Monitor with PPP Failover
Monitors primary internet (WiFi/WAN) and automatically fails over to modem PPP
when primary connection fails for 1 minute.
"""

import subprocess
import time
import logging
import os
import json
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Configure logging
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = RotatingFileHandler(
    '/var/log/voice_bot_ram/internet_monitor.log',
    maxBytes=5*1024*1024,  # 5MB
    backupCount=3
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class InternetMonitor:
    """Monitor primary internet and failover to PPP when needed"""

    def __init__(self):
        self.check_interval = 30  # Check every 30 seconds
        self.failure_threshold = 3  # 3 failures = 90 seconds
        self.consecutive_failures = 0
        self.ppp_active = False
        self.ppp_pid = None
        self.primary_interface = None  # Will be detected dynamically

        # Priority check signal file
        self.priority_signal_file = '/tmp/internet_check_priority'

        # Get APN for wwan0/QMI backup internet
        self.backup_apn = self.get_apn_from_carrier_config()

        # Detect primary interface (WiFi/WAN, not wwan0!)
        self.detect_primary_interface()

        logger.info("="*60)
        logger.info("Internet Monitor Started")
        logger.info(f"Check interval: {self.check_interval}s")
        logger.info(f"Failure threshold: {self.failure_threshold} failures ({self.failure_threshold * self.check_interval}s)")
        logger.info(f"Priority signal: {self.priority_signal_file}")
        logger.info(f"Backup interface: wwan0 (QMI)")
        logger.info(f"Backup APN: {self.backup_apn}")
        logger.info(f"Primary interface: {self.primary_interface or 'Auto-detect'}")
        logger.info("="*60)

    def get_apn_from_carrier_config(self):
        """Get APN from modem_manager carrier database or modem query"""
        try:
            # Try to read IMSI from port mapping file metadata
            mapping_file = '/home/rom/sim7600_ports.json'
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r') as f:
                    mapping = json.load(f)
                    # Check if detector saved modem details with APN
                    if 'apn' in mapping:
                        logger.info(f"APN loaded from mapping: {mapping['apn']}")
                        return mapping['apn']

            # Default fallback APN (works with most UK networks)
            default_apn = "internet"
            logger.warning(f"APN not found in mapping, using default: {default_apn}")
            return default_apn

        except Exception as e:
            logger.error(f"Error loading APN: {e}")
            return "internet"

    def detect_primary_interface(self):
        """
        Detect primary internet interface (WiFi or WAN, NOT PPP!)
        Returns the interface that should be monitored (e.g., wlan0, eth0)
        """
        try:
            # Get all interfaces with IP addresses
            result = subprocess.run(
                ['ip', 'route', 'show', 'default'],
                capture_output=True,
                text=True,
                timeout=5
            )

            # Parse default routes
            # Example: "default via 192.168.1.1 dev wlan0 proto dhcp metric 600"
            for line in result.stdout.split('\n'):
                if 'default via' in line:
                    parts = line.split()
                    if 'dev' in parts:
                        dev_idx = parts.index('dev') + 1
                        if dev_idx < len(parts):
                            interface = parts[dev_idx]

                            # Exclude PPP and loopback
                            if not interface.startswith('ppp') and interface != 'lo':
                                logger.info(f"Detected primary interface: {interface}")
                                self.primary_interface = interface
                                return interface

            # If no default route, look for WiFi interfaces
            result = subprocess.run(
                ['ip', 'link', 'show'],
                capture_output=True,
                text=True,
                timeout=5
            )

            for line in result.stdout.split('\n'):
                # Look for WiFi (wlan*, wlp*) or Ethernet (eth*, enp*)
                if 'wlan' in line or 'wlp' in line:
                    interface = line.split(':')[1].strip().split('@')[0]
                    logger.info(f"Found WiFi interface: {interface}")
                    self.primary_interface = interface
                    return interface
                elif 'eth' in line or 'enp' in line:
                    interface = line.split(':')[1].strip().split('@')[0]
                    logger.info(f"Found Ethernet interface: {interface}")
                    self.primary_interface = interface
                    return interface

            logger.warning("No primary interface detected - will use generic ping")
            return None

        except Exception as e:
            logger.error(f"Error detecting primary interface: {e}")
            return None

    def check_primary_internet(self):
        """
        Check primary internet connectivity (WiFi/WAN) ONLY
        CRITICAL: Pings through specific primary interface, NOT through PPP!
        This prevents false positives when PPP is active.
        """
        try:
            # Re-detect primary interface each time (in case WiFi reconnects)
            current_primary = self.detect_primary_interface()

            if not current_primary:
                logger.warning("No primary interface found - cannot check primary internet")
                return False

            # CRITICAL: Ping 8.8.8.8 through SPECIFIC interface (-I flag)
            # This ensures we test WiFi/WAN, not PPP!
            # If WiFi is down but PPP is up, this will fail (correct behavior)
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '5', '-I', current_primary, '8.8.8.8'],
                capture_output=True,
                timeout=6
            )

            if result.returncode == 0:
                logger.debug(f"Primary internet OK via {current_primary}")
                return True
            else:
                logger.debug(f"Primary internet DOWN on {current_primary}")
                return False

        except subprocess.TimeoutExpired:
            logger.warning(f"Ping timeout (>5s) on {current_primary}")
            return False
        except Exception as e:
            logger.error(f"Error checking internet on {current_primary}: {e}")
            return False

    def is_ppp_running(self):
        """Check if pppd is already running"""
        try:
            result = subprocess.run(
                ['pgrep', '-f', 'pppd.*ttyUSB5'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False

    def start_ppp(self):
        """Start wwan0 connection via QMI (renamed for compatibility, actually uses QMI not PPP)"""
        try:
            logger.info(f"🔵 Starting wwan0 (QMI) backup internet with APN: {self.backup_apn}...")

            # Step 1: Bring up wwan0 interface
            logger.info("Bringing up wwan0 interface...")
            subprocess.run(['sudo', 'ip', 'link', 'set', 'wwan0', 'up'], check=False)
            time.sleep(2)

            # Step 2: Start QMI network connection
            logger.info(f"Starting QMI network with APN '{self.backup_apn}'...")
            result = subprocess.run(
                [
                    'sudo', 'qmicli', '-d', '/dev/cdc-wdm0',
                    '--wds-start-network',
                    f"apn='{self.backup_apn}',ip-type=4",
                    '--client-no-release-cid'
                ],
                capture_output=True,
                text=True,
                timeout=15
            )

            # Check for success or if already connected
            if result.returncode == 0 or 'CallFailed' in result.stderr:
                if 'CallFailed' in result.stderr:
                    logger.warning("QMI reports call failed, trying to get IP anyway...")

                # Step 3: Get IP address via DHCP
                logger.info("Requesting IP address via DHCP on wwan0...")
                dhcp_result = subprocess.run(
                    ['sudo', 'dhclient', '-v', 'wwan0'],
                    capture_output=True,
                    text=True,
                    timeout=20
                )

                time.sleep(3)

                # Step 4: Check if wwan0 has IP
                check_result = subprocess.run(
                    ['ip', 'addr', 'show', 'wwan0'],
                    capture_output=True,
                    text=True
                )

                if check_result.returncode == 0:
                    # Extract IP address
                    for line in check_result.stdout.split('\n'):
                        if 'inet ' in line and 'inet6' not in line:
                            ip = line.strip().split()[1].split('/')[0]
                            logger.info(f"✅ wwan0 (QMI) connection established - IP: {ip}")
                            self.ppp_active = True  # Keep variable name for compatibility

                            # Send notification to VPS
                            self.notify_vps('backup_internet_started', {
                                'interface': 'wwan0',
                                'method': 'QMI',
                                'ip': ip,
                                'apn': self.backup_apn,
                                'reason': 'Primary internet failure'
                            })

                            return True

                logger.warning("⚠️ wwan0 started but no IP address yet")
                self.ppp_active = True  # Mark as active anyway
                return True
            else:
                logger.error(f"QMI start failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Timeout starting wwan0 connection")
            return False
        except Exception as e:
            logger.error(f"Failed to start wwan0: {e}")
            return False

    def stop_ppp(self):
        """Stop wwan0 connection (renamed for compatibility, actually stops QMI not PPP)"""
        try:
            logger.info("🔴 Stopping wwan0 (QMI) backup internet...")

            # Step 1: Release DHCP lease
            subprocess.run(
                ['sudo', 'dhclient', '-r', 'wwan0'],
                capture_output=True,
                timeout=10
            )

            time.sleep(1)

            # Step 2: Stop QMI network (release CID if we had saved it, for now just bring down interface)
            # Note: We used --client-no-release-cid so CID stays active, but interface down is enough
            subprocess.run(
                ['sudo', 'ip', 'link', 'set', 'wwan0', 'down'],
                capture_output=True
            )

            time.sleep(2)

            # Verify wwan0 has no IP
            result = subprocess.run(
                ['ip', 'addr', 'show', 'wwan0'],
                capture_output=True,
                text=True
            )

            has_ip = False
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and 'inet6' not in line:
                        has_ip = True
                        break

            if not has_ip:
                logger.info("✅ wwan0 backup internet stopped")
                self.ppp_active = False

                # Send notification to VPS
                self.notify_vps('backup_internet_stopped', {
                    'interface': 'wwan0',
                    'reason': 'Primary internet restored'
                })

                return True
            else:
                logger.warning("⚠️ wwan0 still has IP address")
                # Bring it down anyway
                self.ppp_active = False
                return True

        except Exception as e:
            logger.error(f"Error stopping wwan0: {e}")
            return False

    def check_priority_signal(self):
        """
        Check if priority signal file exists (call/SMS triggered immediate check)
        Returns True if priority check requested
        """
        if os.path.exists(self.priority_signal_file):
            # Read reason from file if available
            try:
                with open(self.priority_signal_file, 'r') as f:
                    reason = f.read().strip()
            except:
                reason = "Unknown"

            logger.info(f"🚨 PRIORITY CHECK requested: {reason}")

            # Remove signal file
            try:
                os.remove(self.priority_signal_file)
            except:
                pass

            return True

        return False

    def handle_priority_check(self, reason="Priority check"):
        """
        Handle priority internet check (call/SMS arrived)
        Check immediately and start PPP if needed (skip threshold)
        """
        logger.info(f"🚨 PRIORITY: {reason} - checking internet immediately...")

        # Check primary internet
        internet_ok = self.check_primary_internet()

        if internet_ok:
            logger.info(f"✅ PRIORITY: Primary internet OK - no action needed")
            return True

        else:
            # Primary internet is DOWN
            logger.error(f"❌ PRIORITY: Primary internet DOWN during {reason}!")

            # If PPP already active, nothing to do
            if self.ppp_active or self.is_ppp_running():
                logger.info("PPP already active - using backup internet")
                return False

            # Start PPP IMMEDIATELY (skip threshold for priority events)
            logger.error(f"🚨 CRITICAL: Starting PPP immediately for {reason}")
            success = self.start_ppp()

            if success:
                logger.info(f"✅ PPP started successfully for {reason}")
                # Reset failure counter (we're on backup now)
                self.consecutive_failures = 0
            else:
                logger.error(f"❌ FAILED to start PPP for {reason}!")

            return success

    def notify_vps(self, event, data):
        """Send notification to VPS about PPP status"""
        try:
            message = f"Internet Monitor: {event} - {data}"
            severity = 'info' if event == 'ppp_stopped' else 'warning'

            subprocess.run(
                ['/home/rom/pi_send_message.sh', message, severity],
                capture_output=True,
                timeout=10
            )

        except Exception as e:
            logger.error(f"Failed to notify VPS: {e}")

    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Starting internet monitoring loop...")

        while True:
            try:
                # PRIORITY CHECK: Check for call/SMS signal (immediate check)
                if self.check_priority_signal():
                    # Read reason from file content
                    reason = "Call/SMS arrived"
                    self.handle_priority_check(reason)
                    # Continue with normal monitoring after priority check

                # Regular check: Check primary internet
                internet_ok = self.check_primary_internet()

                if internet_ok:
                    # Primary internet is working
                    if self.consecutive_failures > 0:
                        logger.info(f"✅ Primary internet restored (was down for {self.consecutive_failures * self.check_interval}s)")

                    self.consecutive_failures = 0

                    # If PPP is active, stop it (primary is back)
                    if self.ppp_active:
                        logger.info("Primary internet restored - stopping PPP backup")
                        self.stop_ppp()

                else:
                    # Primary internet is down
                    self.consecutive_failures += 1
                    elapsed = self.consecutive_failures * self.check_interval

                    logger.warning(f"⚠️ Primary internet down ({elapsed}s / {self.failure_threshold * self.check_interval}s threshold)")

                    # Check if we've exceeded threshold
                    if self.consecutive_failures >= self.failure_threshold:
                        if not self.ppp_active and not self.is_ppp_running():
                            logger.error(f"❌ Primary internet failed for {elapsed}s - activating PPP backup")
                            self.start_ppp()
                        elif not self.ppp_active and self.is_ppp_running():
                            # PPP is running but we didn't start it
                            logger.info("PPP already running (started externally)")
                            self.ppp_active = True

                # Sleep before next check
                time.sleep(self.check_interval)

            except KeyboardInterrupt:
                logger.info("Shutting down internet monitor...")
                if self.ppp_active:
                    logger.info("Cleaning up PPP connection...")
                    self.stop_ppp()
                break

            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(self.check_interval)

def main():
    """Main entry point"""
    try:
        # Create log directory if needed
        Path('/var/log/voice_bot_ram').mkdir(parents=True, exist_ok=True)

        monitor = InternetMonitor()
        monitor.monitor_loop()

    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
