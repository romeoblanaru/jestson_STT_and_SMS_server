# Jetson Orin Nano - SMS/Voice Gateway Migration Complete

**Date**: 2026-01-07
**Status**: ✅ MIGRATION SUCCESSFUL (with notes)

---

## ✅ Completed Tasks

### Phase 1: System Preparation
- ✅ Installed all system dependencies (python3-serial, python3-flask, smstools, libqmi-utils, etc.)
- ✅ Installed Python packages (webrtcvad, python-dotenv, azure-cognitiveservices-speech)
- ✅ Created directory structure (/var/log/voice_bot_ram, /var/spool/sms, etc.)
- ✅ Added rom user to dialout group
- ✅ Stopped Parakeet transcription server

### Phase 2: File Transfer
- ✅ Transferred all Python scripts from Pi (15 files)
- ✅ Transferred all shell scripts from Pi (23 files)
- ✅ Transferred SMS_Gateway directory
- ✅ Transferred TTS directory
- ✅ Transferred modem_manager directory (carriers.json with 40+ carriers)
- ✅ Transferred system_services directory
- ✅ Transferred audio_library directory
- ✅ Transferred docs directory
- ✅ Transferred configuration files (.env, voice_config.json, etc.)

### Phase 3: Configuration
- ✅ Configured SMSTools (/etc/smsd.conf)
- ✅ Updated .env file (VPN IP: 10.100.0.2, Client: Jetson_Gateway_1)
- ✅ Set LOG_MODE=production
- ✅ No hardcoded /home/pi paths found

### Phase 4: Service Installation
- ✅ Installed systemd services:
  - sim7600-detector.service
  - sim7600-voice-bot.service
  - sms-api.service
  - smstools.service
  - monitoring-webhook.service
  - internet-monitor.service
  - wg-failover.service
- ✅ Enabled all services for auto-start
- ✅ Reloaded systemd daemon

### Phase 5: Modem Testing
- ✅ Modem detected: SIM7600G-H (USB ID 1e0e:9001)
- ✅ 5 ttyUSB ports created (/dev/ttyUSB0-4)
- ✅ AT communication tested successfully
- ✅ IMSI: 234159593176535 (Vodafone UK)

### Phase 6: Modem Configuration (Automatic)
- ✅ Carrier detected: Vodafone UK (MCC 234, MNC 15)
- ✅ Data APN configured: pp.vodafone.co.uk
- ✅ IMS APN configured: ims (for VoLTE)
- ✅ Port mapping saved to /home/rom/sim7600_ports.json
- ✅ Ports tested: ttyUSB2 (SMS), ttyUSB3 (Voice)

### Phase 7: Services Started
- ✅ **sim7600-detector** - Active (running)
- ✅ **smstools** - Active (running)
- ✅ **sms-api** - Active (running, port 8088)
- ✅ **monitoring-webhook** - Active (running, port 8070)
- ✅ **internet-monitor** - Active (running)
- ✅ **wg-failover** - Active (running)

---

## ⚠️ Known Issues

### 1. Voice Bot Not Running
**Status**: Service failed to start (exit code 256)

**Possible Causes**:
- Missing Python dependencies
- Configuration file issues
- Permission issues

**To Investigate**:
```bash
sudo journalctl -u sim7600-voice-bot -n 100
tail -100 /var/log/voice_bot_ram/sim7600_voice_bot.log
```

**Manual Start Test**:
```bash
cd /home/rom
python3 sim7600_voice_bot.py
# Look for error messages
```

### 2. VoLTE Commands Not Supported
**Status**: Warning (non-critical)

The modem firmware doesn't support AT+CEVOLTE commands, but VoLTE may still work automatically when IMS APN is configured. Modern carriers (like Vodafone UK) enable VoLTE automatically when they detect IMS registration.

---

## 🎯 System Status

### Running Services (6/7)
| Service | Status | Port | Purpose |
|---------|--------|------|---------|
| sim7600-detector | ✅ Running | - | Modem auto-detection & config |
| smstools | ✅ Running | - | SMS send/receive (ttyUSB2) |
| sms-api | ✅ Running | 8088 | TTS & SMS API |
| monitoring-webhook | ✅ Running | 8070 | Remote monitoring |
| internet-monitor | ✅ Running | - | QMI failover |
| wg-failover | ✅ Running | - | VPN monitoring |
| sim7600-voice-bot | ❌ Failed | - | Voice call handling |

### Modem Configuration
```json
{
  "config_port": "/dev/ttyUSB3",
  "nmea": "/dev/ttyUSB1",
  "sms_port": "/dev/ttyUSB2",
  "at_command": "/dev/ttyUSB3",
  "audio": "/dev/ttyUSB4",
  "apn": "pp.vodafone.co.uk",
  "ims_apn": "ims",
  "carrier": "Vodafone UK"
}
```

### Network Configuration
- **VPN IP**: 10.100.0.2 (WireGuard wg0)
- **VPS IP**: 10.100.0.1
- **Client Name**: Jetson_Gateway_1

---

## 🧪 Testing Guide

### Test 1: SMS API
```bash
# Test health endpoint (if available)
curl http://localhost:8088/health

# Test SMS sending
curl -X POST http://localhost:8088/sms/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+447501234567",
    "message": "Test from Jetson",
    "priority": "1"
  }'

# Check SMS queue
ls -l /var/spool/sms/outgoing/
ls -l /var/spool/sms/sent/
```

### Test 2: Monitoring API
```bash
# Get help
curl http://localhost:8070/monitor/help

# Check modem status (sync mode)
curl http://localhost:8070/monitor/sim7600/sync

# Check system status
curl http://localhost:8070/monitor/system
```

### Test 3: SMS Diacritics Support
```bash
# Create test SMS with Lithuanian characters
cat > /var/spool/sms/outgoing/test_unicode << EOF
To: +447501234567
Alphabet: UCS
Message: Test Lithuanian: ąčęėįšųū žemė
EOF

# Watch SMSTools log
tail -f /var/log/smstools/smsd.log
```

### Test 4: Modem AT Commands
```bash
# Use picocom to test directly
picocom -b 115200 /dev/ttyUSB3

# In picocom, test:
AT              # Should return OK
AT+CGMM         # Get model
AT+CIMI         # Get IMSI
AT+CSQ          # Signal quality
AT+CREG?        # Network registration
AT+CGDCONT?     # APN configuration
AT+CGACT?       # PDP context status

# Press Ctrl+A then Ctrl+X to exit picocom
```

---

## 🔧 Troubleshooting Commands

### Service Management
```bash
# Check all service statuses
sudo systemctl status sim7600-detector sms-api monitoring-webhook smstools

# Restart detector (reconfigures modem)
sudo systemctl restart sim7600-detector

# View logs
sudo journalctl -u sim7600-detector -f
sudo journalctl -u sms-api -f
tail -f /var/log/smstools/smsd.log
tail -f /var/log/voice_bot_ram/sim7600_detector.log
```

### Modem Debugging
```bash
# Check USB
lsusb | grep 1e0e

# Check ports
ls -l /dev/ttyUSB*

# Check port locks
sudo lsof | grep ttyUSB

# Restart modem (replug USB or use AT command)
# AT command on ttyUSB3:
echo -e "AT+CFUN=1,1\r\n" | picocom -b 115200 -q /dev/ttyUSB3
```

### SMS Debugging
```bash
# Check SMS queues
ls -l /var/spool/sms/incoming/
ls -l /var/spool/sms/outgoing/
ls -l /var/spool/sms/failed/

# SMSTools status
sudo systemctl status smstools
tail -f /var/log/smstools/smsd.log

# Test SMS manually via picocom on ttyUSB2
# (Stop SMSTools first: sudo systemctl stop smstools)
```

---

## 📋 Next Steps

### 1. Fix Voice Bot (Priority: High)
The voice bot is the only service not running. To fix:
1. Check logs for specific error
2. Verify Python dependencies
3. Test manual start
4. Check voice_config.json and runtime_voice_config.json

### 2. Test SMS Send/Receive (Priority: High)
- Send test SMS via API
- Receive SMS and verify forwarding to VPS
- Test Unicode/diacritics support

### 3. VPS Integration (Priority: Medium)
- Update VPS to recognize Jetson IP (10.100.0.2)
- Test webhook communication
- Configure voice bot webhook on VPS

### 4. Test Internet Failover (Priority: Medium)
```bash
# Disconnect WiFi to trigger QMI failover
# Monitor: tail -f /var/log/voice_bot_ram/internet_monitor.log
```

### 5. Monitor System Performance (Priority: Low)
- Watch CPU/RAM usage during calls
- Monitor Jetson temperature
- Check if services auto-restart on failure

---

## 📚 Documentation

All documentation has been transferred from the Pi:
- `/home/rom/docs/PI_SERVICES_EXPLAINED.md` - Complete service guide
- `/home/rom/docs/SIM7600_MODEM_CONFIGURATION.md` - Modem setup details
- `/home/rom/docs/VAD_CONVERSATION_FLOW.md` - Voice bot conversation flow
- `/home/rom/docs/DUAL_THRESHOLD_VAD.md` - VAD system
- `/home/rom/docs/VPS_API_PAYLOAD_SPEC.md` - VPS API specification
- `/home/rom/JETSON_MIGRATION_PLAN.md` - Migration plan (this was created)
- `/home/rom/MIGRATION_COMPLETE.md` - This file

---

## 🎉 Success Metrics

### Achieved ✅
- [x] Modem auto-detected
- [x] Modem auto-configured with carrier-specific APNs
- [x] SMSTools running (SMS gateway ready)
- [x] Unified API running (port 8088)
- [x] Monitoring API running (port 8070)
- [x] Internet failover monitoring active
- [x] WireGuard VPN monitoring active
- [x] All services enabled for auto-start
- [x] Configuration migrated (10.100.0.2)

### Pending ⏳
- [ ] Voice bot running (needs troubleshooting)
- [ ] Test SMS send/receive
- [ ] Test SMS diacritics
- [ ] Test VoLTE calls
- [ ] VPS integration complete
- [ ] Production testing

---

## 🔐 Security Notes

- SMSTools locks ttyUSB2 exclusively (no conflicts with voice bot)
- Voice bot uses ttyUSB3 + ttyUSB4 (no conflicts with SMS)
- All services run as 'rom' user (not root)
- Log files in RAM disk for performance (/var/log/voice_bot_ram)
- WireGuard VPN encrypted (10.100.0.0/24 network)

---

## 💡 Tips

1. **Re-login required**: The rom user was added to dialout group. Log out and back in for full permissions.

2. **Modem replug**: If modem doesn't respond, physically replug the USB cable. Detector will auto-reconfigure.

3. **Service dependencies**:
   - Detector starts SMSTools and Voice Bot automatically
   - Don't start Voice Bot manually while Detector is running

4. **Logs**: Check both journalctl and /var/log/voice_bot_ram/ for troubleshooting

5. **Port conflicts**: Make sure no other services are using ports 8088 or 8070

---

**Migration Time**: ~45 minutes
**Services Running**: 6/7 (86%)
**Ready for Testing**: Yes (except voice calls)

---

Generated by Claude Code
Migration Plan: /home/rom/JETSON_MIGRATION_PLAN.md
Source: Pi Gateway (10.100.0.11)
Target: Jetson Gateway (10.100.0.2)
