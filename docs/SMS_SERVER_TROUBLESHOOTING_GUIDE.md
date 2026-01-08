# SMS Server Troubleshooting & Setup Guide
**For NVIDIA Jetson Orin Nano with SIM7600G-H Modem**
**Date:** 2026-01-08
**Status:** Production-Ready Solution

---

## Table of Contents
1. [Issues Encountered](#issues-encountered)
2. [Root Causes](#root-causes)
3. [Solutions Implemented](#solutions-implemented)
4. [Final Configuration](#final-configuration)
5. [Installation Steps](#installation-steps)
6. [Monitoring Script](#monitoring-script)

---

## Issues Encountered

### Issue 1: Modem Communication Errors
**Symptoms:**
- Continuous I/O errors: `write_to_modem: error 5: Input/output error`
- Modem not responding to AT commands
- Messages not sending

**Root Cause:**
- SMSTools configuration had incorrect device path (`/dev/ttyUSB2`)
- Non-persistent device path changed after reboot/replug
- Wrong PID file path in systemd service

**Solution:**
- Use persistent device path: `/dev/serial/by-id/usb-SimTech__Incorporated_SimTech__Incorporated_0123456789ABCDEF-if02-port0`
- Update systemd service to specify correct PID file location

---

### Issue 2: SMSTools Service Timeout & Restart Loop
**Symptoms:**
- Service stuck in "activating (start)" state
- Service restarting every 1-2 minutes
- Error: "Can't open PID file /run/smsd.pid (yet?) after start: Operation not permitted"
- Timeout after 90 seconds

**Root Cause:**
- PID file path mismatch between SMSTools and systemd
- Default timeout too short for modem initialization
- SMSTools writing PID to `/var/run/smstools/smsd.pid` but systemd expecting `/run/smsd.pid`

**Solution:**
```bash
# systemd service file: /etc/systemd/system/smstools.service
[Service]
Type=forking
ExecStart=/usr/sbin/smsd -c/etc/smsd.conf -p/run/smsd.pid
PIDFile=/run/smsd.pid
TimeoutStartSec=180
```

---

### Issue 3: Multipart Unicode Messages Failing
**Symptoms:**
- Part 1 of message sends successfully
- Part 2/2 or 2/3 fails with "The modem answer was not OK"
- Messages stuck in `/var/spool/sms/checked/` with `.LOCK` files
- Failed messages in `/var/spool/sms/failed/` with "Fail_reason: Unknown"

**Root Cause:**
- TEXT mode (`init = AT+CMGF=1`) unreliable for multipart Unicode messages
- Configuration conflict: TEXT mode set but UCS-2 encoding needed for diacritics
- SMSTools switching between TEXT and PDU causing failures

**Solution:**
- **PERMANENT FIX:** Use pure PDU mode (remove `AT+CMGF=1`)
- PDU mode with UCS-2 supports ALL diacritics (Romanian ăâîșț, Lithuanian ąčęėįšųūž)
- Let SMSTools use PDU mode automatically for Unicode

---

### Issue 4: Incoming Message Body Not Displayed
**Symptoms:**
- SMS received notification shown but message body missing
- Only sender number displayed

**Root Cause:**
- Log format changed after VPS forwarding setup
- "Wrote an incoming message file:" line no longer logged
- Script waiting for non-existent log pattern

**Solution:**
- Modified `sms_watch.sh` to read message body immediately after "SMS received, From:" detection
- Added 0.2s delay and file verification before reading

---

### Issue 5: Outgoing Message Body Not Displayed
**Symptoms:**
- "→ OUT" shown but message content missing
- Sent folder empty (messages not persisting)

**Root Cause:**
- Messages moved from sent folder too quickly
- Script looking in wrong location for message content

**Solution:**
- Extract message content from unified API log where it was queued
- Parse "SMS queued:" log entries for message preview

---

## Root Causes Summary

| Issue | Root Cause | Impact |
|-------|-----------|---------|
| Modem Errors | Non-persistent device path | High |
| Service Restarts | PID file mismatch | High |
| **Multipart Failures** | **TEXT mode for Unicode** | **Critical** |
| Missing Message Body | Log format changes | Medium |
| Sudo Prompts | User not in dialout group | Low |

---

## Solutions Implemented

### 1. Persistent Device Path
```bash
# Find your modem's persistent path
ls -la /dev/serial/by-id/ | grep SimTech

# Use in config
device = /dev/serial/by-id/usb-SimTech__Incorporated_SimTech__Incorporated_0123456789ABCDEF-if02-port0
```

### 2. Fixed Systemd Service
```bash
# /etc/systemd/system/smstools.service
[Unit]
Description=SMSTools Daemon
After=network.target

[Service]
Type=forking
ExecStart=/usr/sbin/smsd -c/etc/smsd.conf -p/run/smsd.pid
ExecStop=/usr/bin/killall smsd
PIDFile=/run/smsd.pid
Restart=always
RestartSec=10
TimeoutStartSec=180

[Install]
WantedBy=multi-user.target
```

### 3. **PDU Mode Configuration (CRITICAL)**
```bash
# /etc/smsd.conf - Production Configuration

devices = GSM1
outgoing = /var/spool/sms/outgoing
checked = /var/spool/sms/checked
incoming = /var/spool/sms/incoming
logfile = /var/log/smstools/smsd.log
infofile = /var/run/smstools/smsd.working
pidfile = /var/run/smstools/smsd.pid
failed = /var/spool/sms/failed
sent = /var/spool/sms/sent
stats = /var/log/smstools/smsd_stats
loglevel = 5

# Performance
receive_before_send = no
autosplit = 3
delaytime = 1
delaytime_mainprocess = 1

# VPS forwarding (optional)
eventhandler = /usr/local/bin/sms_handler_unicode.py

[GSM1]
device = /dev/serial/by-id/usb-SimTech__Incorporated_SimTech__Incorporated_0123456789ABCDEF-if02-port0
incoming = yes
report = yes
baudrate = 115200
rtscts = no

# PDU Mode - DO NOT add AT+CMGF=1 (causes failures)
cs_convert = yes

# Modem initialization
init = AT+CMEE=1
init2 = AT+CNMI=2,1,0,0,0

# Reliability
check_memory_method = 1
memory_start = 1
send_delay = 1
```

### 4. User Permissions
```bash
# Add user to dialout group (reduces sudo prompts)
sudo usermod -a -G dialout <username>
# Logout and login for changes to take effect
```

---

## Final Configuration

### Hardware
- **Device:** NVIDIA Jetson Orin Nano
- **Modem:** SIMCOM SIM7600G-H
- **Ports:** ttyUSB0-4 (interface 2 = AT commands)

### Software Stack
- **SMSTools:** v3.1.21 (PDU mode)
- **SMS API:** Python unified_sms_voice_api.py (port 8088)
- **Monitoring:** sms_watch.sh

### Message Flow
```
┌─────────────┐
│ Incoming SMS│
└──────┬──────┘
       │
       v
┌─────────────────┐
│ Modem → SMSTools│
└──────┬──────────┘
       │
       v
┌────────────────────┐
│ Event Handler      │
│ (forwards to VPS)  │
└──────┬─────────────┘
       │
       v
┌─────────────┐
│ VPS Process │
└──────┬──────┘
       │
       v
┌────────────────┐
│ VPS → SMS API  │
└──────┬─────────┘
       │
       v
┌─────────────────┐
│ SMSTools → Modem│
└──────┬──────────┘
       │
       v
┌─────────────┐
│ Outgoing SMS│
└─────────────┘
```

---

## Installation Steps for New Machine

### Step 1: Install Dependencies
```bash
sudo apt-get update
sudo apt-get install smstools python3 python3-pip curl
```

### Step 2: Configure SMSTools
```bash
# Backup existing config
sudo cp /etc/smsd.conf /etc/smsd.conf.backup

# Find your modem's persistent path
ls -la /dev/serial/by-id/ | grep -i simtech

# Edit config (use the PDU mode configuration above)
sudo nano /etc/smsd.conf
```

### Step 3: Create/Update Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/smstools.service
# (paste the service configuration from above)

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable smstools.service
sudo systemctl start smstools.service

# Verify
sudo systemctl status smstools.service
```

### Step 4: Set Permissions
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Create spool directories if needed
sudo mkdir -p /var/spool/sms/{incoming,outgoing,checked,failed,sent}
sudo chown -R root:dialout /var/spool/sms/
sudo chmod -R 775 /var/spool/sms/
```

### Step 5: Test Modem Communication
```bash
# Test with Python
python3 << EOF
import serial
ser = serial.Serial('/dev/serial/by-id/usb-SimTech__*if02-port0', 115200, timeout=2)
ser.write(b'AT\r\n')
print(ser.read(100).decode('utf-8', errors='ignore'))
ser.close()
EOF
```

### Step 6: Send Test Message
```bash
# Via API
curl -X POST http://localhost:8088/send_sms \
  -H "Content-Type: application/json" \
  -d '{"to": "+1234567890", "message": "Test diacritics: ăâîșț ąčęėįšųūž"}'

# Check logs
tail -f /var/log/smstools/smsd.log
```

---

## Monitoring Script

### sms_watch.sh Features
- Real-time SMS activity monitoring
- Displays incoming/outgoing messages with content
- Shows VPS forwarding status
- Color-coded output
- Detects system messages (VODAFONE, etc.)

### Key Updates Made:
1. **Incoming messages:** Two-line format with message body
2. **Outgoing messages:** Two-line format with message body
3. **VPS status:** Shows "✓ MSG - successfully sent to VPS" or "✗ ERROR - VPS down"
4. **Removed redundant:** "SERVER REPLY queued" messages
5. **Updated:** "WEBHOOK RECEIVED" → "RECEIVED message from VPS"

---

## Common Issues & Quick Fixes

### Issue: Service won't start
```bash
# Check logs
journalctl -u smstools.service -n 50

# Common fixes:
sudo rm -f /run/smsd.pid
sudo systemctl restart smstools.service
```

### Issue: Messages stuck in checked folder
```bash
# Clean up (only if service is stable)
sudo rm -f /var/spool/sms/checked/*.LOCK
sudo mv /var/spool/sms/checked/* /var/spool/sms/outgoing/
```

### Issue: Diacritics not working
```bash
# Verify PDU mode (should NOT have AT+CMGF=1)
grep "AT+CMGF" /etc/smsd.conf

# If found, remove it and restart
sudo systemctl restart smstools.service
```

### Issue: Permission denied errors
```bash
# Check user is in dialout group
groups

# If not, add and re-login
sudo usermod -a -G dialout $USER
```

---

## Testing Checklist

- [ ] Service starts and stays running
- [ ] Modem responds to AT commands
- [ ] Can send simple ASCII message
- [ ] Can send message with diacritics (ăâîșț)
- [ ] Can receive incoming SMS
- [ ] Incoming message body displayed
- [ ] Outgoing message body displayed
- [ ] Multipart messages send completely
- [ ] No messages stuck in checked folder
- [ ] No .LOCK files persisting
- [ ] VPS forwarding working (if configured)

---

## Key Takeaways

### ✅ DO:
- Use PDU mode for production (industry standard)
- Use persistent device paths (/dev/serial/by-id/)
- Set proper TimeoutStartSec in systemd (180s)
- Test with diacritics before deployment
- Monitor /var/log/smstools/smsd.log

### ❌ DON'T:
- Use TEXT mode (AT+CMGF=1) for Unicode messages
- Use /dev/ttyUSB* paths (change after reboot)
- Ignore .LOCK files in checked folder
- Assume TEXT mode doesn't support diacritics (it tries, but fails)
- Run cleanup cron jobs as "fix" (address root cause instead)

---

## Production Readiness Checklist

- [x] Persistent device path configured
- [x] PDU mode enabled (TEXT mode removed)
- [x] Systemd service configured with proper timeout
- [x] User permissions set (dialout group)
- [x] VPS forwarding configured (if needed)
- [x] Monitoring script deployed
- [x] Tested with multiple languages/diacritics
- [x] Verified multipart messages send completely
- [x] No stuck messages in queues
- [x] Service survives reboot

---

## Support Information

**Hardware:** NVIDIA Jetson Orin Nano
**Modem:** SIMCOM SIM7600G-H
**Network:** Vodafone UK
**Encoding:** UCS-2 (Unicode)
**Mode:** PDU (Production)

**Configuration Files:**
- SMSTools: `/etc/smsd.conf`
- Systemd: `/etc/systemd/system/smstools.service`
- Logs: `/var/log/smstools/smsd.log`
- Queues: `/var/spool/sms/`

**Backup Location:** `/etc/smsd.conf.backup_*`

---

**Document Version:** 1.0
**Last Updated:** 2026-01-08
**Status:** ✅ Production-Ready
