#!/usr/bin/env python3
"""
SMS Handler for smstools3 - Python version with proper Unicode handling
Forwards incoming SMS to VPS webhook with proper character encoding
Only processes RECEIVED messages, ignores FAILED messages
Includes retry logic with notifications on failure
Resilient to log file permission issues
"""

import sys
import json
import requests
import logging
from datetime import datetime
import re
import unicodedata
import time
import subprocess
import os

# Configuration - NOW USING RAM DISK
LOG_FILE = "/var/log/voice_bot_ram/sms_gateway.log"

# Load config from .env if available
WEBHOOK_URL = "http://10.100.0.1:8088/webhook/sms/receive"
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Try to load from .env file
try:
    env_file = '/home/rom/.env'
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('VPS_WEBHOOK_URL='):
                    WEBHOOK_URL = line.split('=', 1)[1].strip()
                elif line.startswith('SMS_MAX_RETRIES='):
                    MAX_RETRIES = int(line.split('=')[1].strip())
                elif line.startswith('SMS_RETRY_DELAY='):
                    RETRY_DELAY = int(line.split('=')[1].strip())
except:
    pass  # Use defaults if .env can't be read

# Flag to track if we've already sent a log permission warning
log_permission_warning_sent = False

def setup_logging():
    """Setup logging with fallback to stderr if file is not writable"""
    global log_permission_warning_sent

    try:
        # Try to set up file logging
        logging.basicConfig(
            filename=LOG_FILE,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            force=True
        )
        # Test if we can write
        logging.info("Logging initialized")
        return True
    except (PermissionError, IOError) as e:
        # Fallback to stderr logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            stream=sys.stderr,
            force=True
        )

        # Send warning notification if not already sent
        if not log_permission_warning_sent:
            try:
                subprocess.run(
                    ['/home/rom/pi_send_message.sh',
                     f"SMS handler: Log file permission problem - {LOG_FILE} not writable. SMS forwarding continues.",
                     'warning'],
                    capture_output=True,
                    timeout=10
                )
                log_permission_warning_sent = True
            except:
                pass

        logging.warning(f"Cannot write to {LOG_FILE}, using stderr instead")
        return False

# Try to set up logging
setup_logging()

def clean_control_chars(text):
    """Remove control characters while preserving normal text and diacritics"""
    if not text:
        return ""

    # Define allowed categories
    allowed_categories = {
        'Ll', 'Lu', 'Lt', 'Lm', 'Lo',  # Letters
        'Nd', 'Nl', 'No',               # Numbers
        'Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po',  # Punctuation
        'Sm', 'Sc', 'Sk', 'So',        # Symbols
        'Zs', 'Zl', 'Zp',              # Separators (spaces, line/paragraph separators)
        'Mn', 'Mc', 'Me',              # Marks (diacritics)
    }

    cleaned = []
    for char in text:
        # Allow newlines and tabs explicitly
        if char in '\n\r\t':
            cleaned.append(char)
        # Check Unicode category
        elif unicodedata.category(char) in allowed_categories:
            cleaned.append(char)
        # Replace other characters with space
        else:
            cleaned.append(' ')

    return ''.join(cleaned)

def parse_sms_file(filepath):
    """Parse SMS file from smstools3"""
    sms_data = {
        'from': '',
        'received': '',
        'message': ''
    }

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Split headers and body
        parts = content.split('\n\n', 1)
        if len(parts) >= 1:
            headers = parts[0]
            body = parts[1] if len(parts) > 1 else ''

            # Parse headers
            is_international = False
            from_number = ''

            for line in headers.split('\n'):
                if line.startswith('From:'):
                    from_number = line.split(':', 1)[1].strip()
                elif line.startswith('From_TOA:'):
                    # Check if it's international (91 = international)
                    if '91 international' in line:
                        is_international = True
                elif line.startswith('Received:'):
                    sms_data['received'] = line.split(':', 1)[1].strip()

            # Add + prefix for international numbers
            if from_number:
                if is_international and not from_number.startswith('+'):
                    sms_data['from'] = '+' + from_number
                    logging.info(f"Added + prefix for international number: {from_number} -> {sms_data['from']}")
                else:
                    sms_data['from'] = from_number

            # Clean message body
            sms_data['message'] = clean_control_chars(body.strip())

    except Exception as e:
        # Try to re-setup logging in case permissions changed
        setup_logging()
        logging.error(f"Error parsing SMS file: {str(e)}")

    return sms_data

def send_notification(message, severity="warning"):
    """Send notification using pi_send_message.sh"""
    try:
        result = subprocess.run(
            ['/home/rom/pi_send_message.sh', message, severity],
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        # Try to re-setup logging in case permissions changed
        setup_logging()
        logging.error(f"Failed to send notification: {str(e)}")
        return False

def send_to_webhook_with_retries(sms_data, gateway_ip=None):
    """Send SMS data to VPS webhook with retry logic"""
    # Get actual VPN IP dynamically
    if gateway_ip is None:
        # Method 1: Try to get from WireGuard interface
        try:
            import subprocess
            result = subprocess.run(['ip', 'addr', 'show', 'wg0'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'inet ' in line:
                        gateway_ip = line.split()[1].split('/')[0]
                        logging.info(f"Got VPN IP from wg0: {gateway_ip}")
                        break
        except:
            pass

        # Method 2: Fallback to .env file if available
        if not gateway_ip:
            try:
                env_file = '/home/rom/.env'
                if os.path.exists(env_file):
                    with open(env_file, 'r') as f:
                        for line in f:
                            if line.startswith('WG_VPN_IP='):
                                gateway_ip = line.split('=')[1].strip()
                                logging.info(f"Got VPN IP from .env: {gateway_ip}")
                                break
            except:
                pass

        # No fallback - fail if can't determine IP
        if not gateway_ip:
            logging.error("Cannot determine gateway IP - check WireGuard connection or .env file")
            return False

    payload = {
        'from': sms_data['from'],
        'message': sms_data['message'],
        'received': sms_data['received'],
        'gateway_ip': gateway_ip
    }

    last_error = "Unknown error"
    last_status_code = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Try to re-setup logging in case permissions changed
            setup_logging()

            # Log the attempt
            logging.info(f"Webhook attempt {attempt}/{MAX_RETRIES}: Sending to {WEBHOOK_URL}")

            # Send request
            response = requests.post(
                WEBHOOK_URL,
                json=payload,
                timeout=10,
                headers={'Content-Type': 'application/json'}
            )

            logging.info(f"Webhook response: {response.status_code} - {response.text}")

            # Check if successful
            if response.status_code == 200:
                logging.info("Successfully forwarded to VPS")
                return True
            else:
                last_status_code = response.status_code
                try:
                    error_data = response.json()
                    last_error = f"HTTP {response.status_code}: {error_data.get('error', response.text[:100])}"
                except:
                    last_error = f"HTTP {response.status_code}: {response.text[:100]}"
                logging.warning(f"Webhook returned non-200 status: {response.status_code}")

        except requests.exceptions.ConnectionError as e:
            last_error = "Connection refused - VPS webhook service down"
            logging.error(f"Attempt {attempt}/{MAX_RETRIES} failed: Connection refused to VPS webhook")
        except requests.exceptions.Timeout as e:
            last_error = "Request timeout - VPS not responding"
            logging.error(f"Attempt {attempt}/{MAX_RETRIES} failed: Request timeout")
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if "Connection refused" in error_msg:
                last_error = "Connection refused - VPS webhook port 8088 not accessible"
            else:
                last_error = error_msg[:100]  # Limit error message length
            logging.error(f"Attempt {attempt}/{MAX_RETRIES} failed: {error_msg}")

        # If not the last attempt, wait before retrying
        if attempt < MAX_RETRIES:
            logging.info(f"Waiting {RETRY_DELAY} seconds before retry...")
            time.sleep(RETRY_DELAY)

    # All retries failed
    logging.error(f"Failed to forward to VPS after {MAX_RETRIES} attempts")

    # Send detailed notification about the failure
    notification_msg = (
        f"SMS->VPS Webhook Failed ({MAX_RETRIES} attempts)\n"
        f"URL: {WEBHOOK_URL}\n"
        f"Payload: {{'from':'{sms_data['from']}', 'message':'{sms_data['message'][:50]}...', 'gateway_ip':'{gateway_ip}'}}\n"
        f"VPS Response: {last_error}\n"
        f"Debug: Check VPS logs for details"
    )
    if send_notification(notification_msg, "warning"):
        logging.info("Failure notification sent")
    else:
        logging.error("Failed to send failure notification")

    return False

def parse_failed_sms(filepath):
    """Parse failed SMS file to extract details"""
    sms_data = {
        'to': '',
        'message': '',
        'alphabet': 'GSM7',
        'modem': '',
        'error_type': 'Unknown',
        'retries': 0
    }

    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Split headers and body
        parts = content.split('\n\n', 1)
        if len(parts) >= 1:
            headers = parts[0]
            body = parts[1] if len(parts) > 1 else ''

            # Parse headers
            for line in headers.split('\n'):
                if line.startswith('To:'):
                    sms_data['to'] = line.split(':', 1)[1].strip()
                elif line.startswith('Alphabet:'):
                    sms_data['alphabet'] = line.split(':', 1)[1].strip()
                elif line.startswith('Modem:'):
                    sms_data['modem'] = line.split(':', 1)[1].strip()

            # Get message body
            sms_data['message'] = clean_control_chars(body.strip())

        # Extract error details from recent logs
        try:
            log_tail = subprocess.run(
                ['tail', '-100', '/var/log/smstools/smsd.log'],
                capture_output=True, text=True, timeout=2
            )
            if log_tail.returncode == 0:
                log_lines = log_tail.stdout.split('\n')
                phone_number = sms_data['to']

                # Look for CMS ERROR or other errors related to this number
                for line in reversed(log_lines):
                    if phone_number in line or 'CMS ERROR' in line or 'Timeout' in line:
                        if 'CMS ERROR' in line:
                            # Extract CMS error
                            cms_match = re.search(r'CMS ERROR: ([^$\n]+)', line)
                            if cms_match:
                                sms_data['error_type'] = f"CMS ERROR: {cms_match.group(1).strip()}"
                        elif 'Modem is not ready' in line:
                            sms_data['error_type'] = 'Modem timeout - not responding to AT commands'
                            timeout_match = re.search(r'Timeouts: (\d+)', line)
                            if timeout_match:
                                sms_data['error_type'] += f' ({timeout_match.group(1)} timeouts)'
                        elif 'Retries:' in line and phone_number in line:
                            retry_match = re.search(r'Retries: (\d+)', line)
                            if retry_match:
                                sms_data['retries'] = int(retry_match.group(1))
        except:
            pass

    except Exception as e:
        setup_logging()
        logging.error(f"Error parsing failed SMS file: {str(e)}")

    return sms_data

def handle_failed_sms(sms_file):
    """Handle FAILED SMS events - send detailed error report to VPS"""
    if not sms_file:
        logging.error("No SMS file provided for FAILED event")
        return

    setup_logging()
    logging.error(f"Processing FAILED SMS: {sms_file}")

    # Parse the failed SMS
    sms_data = parse_failed_sms(sms_file)

    # Get modem status from recent logs (avoid AT commands that conflict with SMSTools)
    modem_status = "Unknown"
    signal_quality = "Unknown"
    try:
        # Check recent SMSTools logs for signal quality
        log_tail = subprocess.run(
            ['tail', '-200', '/var/log/smstools/smsd.log'],
            capture_output=True, text=True, timeout=2
        )
        if log_tail.returncode == 0:
            # Look for recent CSQ or signal info
            for line in reversed(log_tail.stdout.split('\n')):
                if '+CSQ:' in line or 'Signal quality' in line:
                    csq_match = re.search(r'\+CSQ: (\d+),', line)
                    if csq_match:
                        signal_quality = f"{csq_match.group(1)}/31"
                        break
            # Check if modem is responding
            if 'Modem is not ready' in log_tail.stdout:
                modem_status = "Not responding (check logs)"
            else:
                modem_status = "Active in SMSTools"
    except:
        pass

    # Build detailed error notification
    error_report = f"""⚠️ SMS MODEM ERROR - Failed to Send

📱 Recipient: {sms_data['to']}
📝 Message: {sms_data['message'][:200]}{'...' if len(sms_data['message']) > 200 else ''}

❌ Error Details:
   Type: {sms_data['error_type']}
   Retries: {sms_data['retries']}
   Encoding: {sms_data['alphabet']}
   Modem: {sms_data['modem'] or 'GSM1'}

📊 Modem Status:
   Status: {modem_status}
   Signal: {signal_quality}

🔍 Analysis:
   File: {sms_file}
   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚡ Action Required:
   - Check if phone number format is correct
   - Verify modem is responding to AT commands
   - Review /var/log/smstools/smsd.log for details
   - Message has been moved to /failed/ directory"""

    # Log the error
    logging.error(f"SMS FAILED to {sms_data['to']} - {sms_data['error_type']}")
    logging.error(f"Message: {sms_data['message'][:100]}")

    # Send notification to VPS
    try:
        result = subprocess.run(
            ['/home/rom/pi_send_message.sh', error_report, 'error'],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            logging.info("FAILED SMS notification sent to VPS")
        else:
            logging.error(f"Failed to send notification: {result.stderr}")
    except Exception as e:
        logging.error(f"Error sending FAILED notification: {str(e)}")

def main():
    """Main handler function"""
    # Get event type from first argument (RECEIVED, SENT, FAILED, CALL, etc.)
    event_type = sys.argv[1] if len(sys.argv) > 1 else None

    # Handle incoming phone calls
    if event_type == "CALL":
        call_file = sys.argv[2] if len(sys.argv) > 2 else None
        if call_file:
            # Extract caller number from CALL file
            try:
                with open(call_file, 'r') as f:
                    content = f.read()
                    # CALL file format: From: <number>
                    caller_match = re.search(r'From:\s*(\+?\d+)', content)
                    caller_number = caller_match.group(1) if caller_match else "Unknown"

                logging.info(f"Incoming call detected from {caller_number}")

                # Delete CALL file immediately to prevent reprocessing on restart
                try:
                    os.remove(call_file)
                    logging.info(f"Deleted CALL file: {call_file}")
                except Exception as del_err:
                    logging.warning(f"Could not delete CALL file {call_file}: {del_err}")

                # Trigger call handler script
                subprocess.Popen(['/usr/local/bin/handle_incoming_call.sh', 'CALL', caller_number, 'GSM1'])

            except Exception as e:
                logging.error(f"Error handling incoming call: {e}")
        return

    # Handle FAILED messages (modem errors)
    if event_type == "FAILED":
        handle_failed_sms(sys.argv[2] if len(sys.argv) > 2 else None)
        return

    # Only process RECEIVED messages (incoming SMS)
    if event_type != "RECEIVED":
        # Silently exit for non-incoming messages
        return

    # Get SMS file path from arguments
    sms_file = None
    if len(sys.argv) > 2:
        sms_file = sys.argv[2]

    if not sms_file:
        logging.error("No SMS file provided in arguments")
        return

    # Skip if file is in failed directory
    if "/failed/" in sms_file:
        return

    # Try to re-setup logging at start of processing
    setup_logging()

    logging.info(f"Processing incoming SMS file: {sms_file}")

    # Parse SMS
    sms_data = parse_sms_file(sms_file)

    # Only forward if we have a valid sender
    if not sms_data['from']:
        logging.info(f"Skipping SMS with no sender: {sms_file}")
        return

    # Log received SMS
    logging.info(f"SMS received from {sms_data['from']}: {sms_data['message']}")

    # Forward to webhook with retries - this will continue even if logging fails
    send_to_webhook_with_retries(sms_data)

if __name__ == "__main__":
    main()
