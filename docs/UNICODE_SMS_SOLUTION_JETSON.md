# Unicode SMS Solution - Jetson Orin Nano
**Date:** 2026-01-11
**Status:** ✅ Working
**Tested with:** Romanian (ăîâșț) and Lithuanian (ąčęėįšųūž) diacritics

---

## Problem Solved
SMS with diacritics were displaying incorrectly or getting stripped.

---

## Working Solution

### 1. SMSTools Configuration (`/etc/smsd.conf`)

```ini
# SMSTools3 Configuration - Universal with proper Unicode support
# Supports Romanian (ă,â,î,ș,ț) and Lithuanian (ą,č,ę,ė,į,š,ų,ū,ž)

devices = GSM1
outgoing = /var/spool/sms/outgoing
checked = /var/spool/sms/checked
failed = /var/spool/sms/failed
sent = /var/spool/sms/sent
incoming = /var/spool/sms/incoming
logfile = /var/log/smstools/smsd.log
pidfile = /var/run/smstools/smsd.pid
loglevel = 5

# Global settings
receive_before_send = no
autosplit = 3

[GSM1]
device = /dev/ttyUSB_SIM7600_AT
incoming = yes
baudrate = 115200
memory_start = 0
pin =

# CRITICAL: Unicode support settings (from Pi)
decode_unicode_text = yes
cs_convert = yes

# Initialize modem in text mode
init = AT+CMGF=1

# Set message indication mode
init2 = AT+CNMI=2,1,0,0,0

# Modem behavior
receive_before_send = no
check_memory_method = 1
```

**Key settings:**
- `decode_unicode_text = yes` - Decodes Unicode in incoming/outgoing SMS
- `cs_convert = yes` - Enables character set conversion
- `init = AT+CMGF=1` - MUST use text mode (not PDU)

---

### 2. Unicode SMS Sender Script

**Location:** `/home/rom/send_sms_unicode.py`

This script creates SMS files with proper binary UTF-16-BE encoding that SMSTools expects.

**Usage:**
```bash
# Romanian diacritics
python3 /home/rom/send_sms_unicode.py 447504128961 "Bună ziua! Ăă Îî Șș Țț"

# Lithuanian diacritics
python3 /home/rom/send_sms_unicode.py +37061234567 "Labas! ąčęėįšųūž"

# Mixed
python3 /home/rom/send_sms_unicode.py 40721234567 "Test: ăîâșț + ąčęėįšųūž"
```

---

### 3. How It Works

SMSTools requires Unicode SMS files in this specific format:

```
To: 447504128961        ← ASCII header
Alphabet: UCS2          ← Tells SMSTools to use Unicode
                        ← Empty line
[BINARY UTF-16-BE]      ← Raw binary data (NOT text, NOT hex!)
```

The script:
1. Writes headers in ASCII
2. Adds `Alphabet: UCS2` header
3. Writes message as **binary UTF-16-BE** (not text!)
4. Sets proper file permissions
5. SMSTools picks it up and sends

---

### 4. Integration with SMS Gateway API

If you have an SMS Gateway API (like on the Pi), integrate the binary file creation method:

```python
def send_sms_with_unicode(recipient, message):
    """Send SMS with proper Unicode support"""
    import os
    import time

    # Remove + from number
    recipient = recipient.lstrip('+')

    # Create unique filename
    timestamp = int(time.time())
    pid = os.getpid()
    filename = f"/var/spool/sms/outgoing/api_{timestamp}_{pid}"

    # Check if message needs Unicode
    needs_unicode = any(ord(c) > 127 for c in message)

    if needs_unicode:
        # Binary UTF-16-BE for Unicode
        with open(filename, 'wb') as f:
            f.write(f"To: {recipient}\n".encode('ascii'))
            f.write(b"Alphabet: UCS2\n\n")
            f.write(message.encode('utf-16-be'))
    else:
        # Plain text for ASCII
        with open(filename, 'w') as f:
            f.write(f"To: {recipient}\n\n{message}")

    os.chmod(filename, 0o666)
    return filename
```

---

## What NOT to Do

❌ **Don't use PDU mode** (`AT+CMGF=0`) - causes issues
❌ **Don't write text files** for Unicode - must be binary
❌ **Don't use hex encoding** - use raw binary UTF-16-BE
❌ **Don't forget** `Alphabet: UCS2` header for Unicode messages

---

## Testing

**Test Romanian:**
```bash
python3 /home/rom/send_sms_unicode.py YOUR_NUMBER "Bună ziua! Cum îți place țara? Ăă Șș Țț"
```

**Test Lithuanian:**
```bash
python3 /home/rom/send_sms_unicode.py YOUR_NUMBER "Labas! Kaip laikaisi? ąčęėįšųūž"
```

**Test both:**
```bash
python3 /home/rom/send_sms_unicode.py YOUR_NUMBER "RO: ăîâșț | LT: ąčęėįšųūž ✅"
```

---

## Troubleshooting

### If diacritics don't appear:
1. ✅ Check SMSTools config has `decode_unicode_text = yes`
2. ✅ Check SMSTools config has `cs_convert = yes`
3. ✅ Verify using `/home/rom/send_sms_unicode.py` script (not plain text files)
4. ✅ Restart SMSTools: `sudo systemctl restart smstools`
5. ✅ Check receiving phone supports Unicode SMS

### If SMS fails to send:
1. Check logs: `tail -50 /var/log/smstools/smsd.log`
2. Verify modem: `AT+CNMP?` (should be 38 for LTE)
3. Check network: `AT+COPS?`
4. Test with plain ASCII first to isolate issue

---

## Key Discovery

SMSTools3 with `Alphabet: UCS2` expects the message body to be **raw UTF-16-BE binary data**, not text or hex-encoded strings. This is why:
- ✅ Using `/home/rom/send_sms_unicode.py` works
- ❌ Creating text files with diacritics fails

---

## Working Configuration Summary

**Modem:** SIM7600G-H
**Carrier:** Any (Giffgaff, Lycamobile, Lithuanian carriers)
**Mode:** LTE-only (AT+CNMP=38)
**SMSTools:** Text mode with Unicode support
**Languages:** Romanian, Lithuanian, and any UTF-16 supported language

---

## Files

- `/etc/smsd.conf` - SMSTools configuration with Unicode support
- `/home/rom/send_sms_unicode.py` - Unicode SMS sender script
- `/home/rom/docs/UNICODE_SMS_SOLUTION_JETSON.md` - This documentation

---

**Created:** 2026-01-11
**System:** Jetson Orin Nano - SIM7600G-H Modem
**Based on:** Working Pi configuration at 10.100.0.11
