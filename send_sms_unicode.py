#!/usr/bin/env python3
"""
Send SMS with proper UCS2 encoding - binary format
This is how smstools3 expects Unicode messages
Supports Romanian (ăîâșț) and Lithuanian (ąčęėįšųūž) diacritics
"""
import sys
import os
import time

def create_unicode_sms_file(recipient, message):
    """Create SMS file with binary UTF-16BE encoding for smstools3"""

    # Remove + from number
    recipient = recipient.lstrip('+')

    # Create unique filename
    timestamp = int(time.time())
    pid = os.getpid()
    filename = f"/var/spool/sms/outgoing/sms_{timestamp}_{pid}"

    # Open file in binary mode
    with open(filename, 'wb') as f:
        # Write headers in ASCII
        f.write(f"To: {recipient}\n".encode('ascii'))
        f.write(b"Alphabet: UCS2\n")
        f.write(b"\n")

        # Write message in UTF-16 BE (Big Endian) - NOT hex, actual binary!
        f.write(message.encode('utf-16-be'))

    # Set permissions
    os.chmod(filename, 0o666)

    print(f"✅ SMS queued with proper UCS2 binary encoding")
    print(f"📁 File: {filename}")
    print(f"📱 To: +{recipient}")
    print(f"📝 Message: {message}")

    return filename

def main():
    if len(sys.argv) < 3:
        print("Usage: send_sms_unicode.py <recipient> <message>")
        print("Example: send_sms_unicode.py 447504128961 'Bună ziua! Ăă Șș Țț'")
        print("Example: send_sms_unicode.py +40721234567 'Labas! ąčęėįšųūž'")
        sys.exit(1)

    recipient = sys.argv[1]
    message = ' '.join(sys.argv[2:])

    print("\n" + "="*60)
    print("🌍 Unicode SMS Sender (Romanian & Lithuanian support)")
    print("="*60)

    filename = create_unicode_sms_file(recipient, message)

    print("\n⏳ Message queued. SMSTools will send it shortly...")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
