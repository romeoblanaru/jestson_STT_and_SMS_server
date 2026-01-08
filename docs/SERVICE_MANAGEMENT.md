# Service Management Guide

## ⚠️ IMPORTANT: Always Use Systemd Services!

**NEVER manually run these scripts** - they are managed by systemd and will auto-start on boot.

## Active Services

| Service Name | Script | Port | Auto-Start |
|--------------|--------|------|------------|
| `sms-api.service` | `/home/rom/SMS_Gateway/unified_sms_voice_api.py` | 8088 | ✅ Enabled |
| `sim7600-voice-bot.service` | `/home/rom/sim7600_voice_bot.py` | - | ❌ Disabled |
| `sim7600-detector.service` | `/home/rom/sim7600_detector.py` | - | ✅ Enabled |
| `smstools` | SMSTools daemon | - | ✅ Enabled |

## Proper Service Management

### ✅ CORRECT Way to Restart Services:

```bash
# Restart unified SMS/Voice API
sudo systemctl restart sms-api

# Restart voice bot
sudo systemctl restart sim7600-voice-bot

# Restart SIM7600 detector
sudo systemctl restart sim7600-detector

# Check service status
sudo systemctl status sms-api
sudo systemctl status sim7600-voice-bot
```

### ❌ WRONG - Will Cause Crash Loop!

```bash
# ❌ DON'T DO THIS - creates port conflict!
cd /home/rom/SMS_Gateway
python3 unified_sms_voice_api.py  # WRONG - conflicts with systemd service

# ❌ DON'T DO THIS - creates duplicate processes!
nohup python3 unified_sms_voice_api.py &  # WRONG - systemd already manages it
```

## Why Manual Start Causes Problems

**What happened (Oct 19, 2025):**
1. Manual process started on port 8088
2. Systemd service `sms-api.service` tried to auto-start
3. Port conflict → service crashed → systemd auto-restarted it every 10 seconds
4. **Result**: Crash loop spam in logs

**Fix:** Always use `sudo systemctl restart sms-api` instead

## After System Reboot

All enabled services auto-start automatically:
- ✅ `sms-api.service` → Unified SMS/Voice API
- ✅ `sim7600-detector.service` → Modem auto-detection
- ✅ `smstools` → SMS sending/receiving

**Voice bot** must be started manually (or enabled for auto-start):
```bash
sudo systemctl start sim7600-voice-bot
# Or enable for auto-start:
sudo systemctl enable sim7600-voice-bot
```

## Enable/Disable Auto-Start

```bash
# Enable service to start on boot
sudo systemctl enable sms-api

# Disable service from starting on boot
sudo systemctl disable sms-api

# Check if enabled
systemctl is-enabled sms-api
```

## View Logs

```bash
# Real-time logs
journalctl -u sms-api -f
journalctl -u sim7600-voice-bot -f

# Last 50 lines
journalctl -u sms-api -n 50

# Check for errors
journalctl -u sms-api | grep -i error
```

## Troubleshooting Port Conflicts

If you see crash loops:

```bash
# 1. Check what's using port 8088
sudo netstat -tlnp | grep 8088

# 2. Find the process
ps aux | grep unified_sms_voice_api

# 3. Kill manual processes (keep systemd one)
sudo kill <PID>

# 4. Restart service properly
sudo systemctl restart sms-api
```

## Summary

**Golden Rule:**
- ✅ Use `sudo systemctl restart <service-name>`
- ❌ Never run scripts manually when systemd service exists

This prevents:
- Port conflicts
- Crash loops
- Log spam
- Duplicate processes
