# Jetson Orin Nano - SMS/Voice Gateway Migration Plan

**Target**: Replicate Pi's SMS/Voice/Modem system on Jetson Orin Nano
**Source**: Raspberry Pi at 10.100.0.11
**Date**: 2026-01-07
**Current Jetson IP**: 10.100.0.2 (via WireGuard)

---

## Current Status

### ✅ Already Working on Jetson
- NVIDIA Jetson Orin Nano with Ubuntu/Jetpack
- WireGuard VPN connected (10.100.0.2)
- ModemManager disabled and uninstalled (good!)
- CUPS services not installed (good!)
- SIM7600G-H modem **DETECTED** on USB:
  - Vendor ID: 1e0e:9001 (Qualcomm/SimTech)
  - 5 ttyUSB ports created: `/dev/ttyUSB0` - `/dev/ttyUSB4`
  - Modem is ready to be configured!

### 🎯 Goals
1. **Auto-detect modem** on USB plug-in (same as Pi)
2. **Auto-configure** modem with carrier-specific APN + VoLTE
3. **SMS Gateway** - send/receive SMS with diacritics support
4. **Voice Bot** - answer calls, transcribe speech, respond via TTS
5. **Unified API** - Port 8088 for TTS and SMS operations
6. **Monitoring API** - Port 8070 for remote health checks
7. **Internet failover** - Use modem QMI when WiFi/WAN fails
8. **VPS integration** - Forward SMS, call events, transcriptions to server

---

## Migration Strategy

### Phase 1: System Preparation (30 min)
### Phase 2: File Transfer from Pi (45 min)
### Phase 3: Dependencies Installation (30 min)
### Phase 4: Service Installation (20 min)
### Phase 5: Configuration & Testing (45 min)
### Phase 6: VPS Integration (15 min)

**Total Estimated Time**: ~3 hours

---

## Phase 1: System Preparation

### 1.1 Install Base Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Core utilities
sudo apt install -y \
  python3 python3-pip python3-venv python3-serial \
  python3-flask python3-requests python3-numpy \
  smstools qmi-utils usbutils picocom minicom \
  rsync git curl wget

# Audio libraries (for TTS and voice)
sudo apt install -y \
  ffmpeg sox libsox-fmt-all opus-tools \
  alsa-utils pulseaudio-utils

# Development tools
sudo apt install -y \
  build-essential python3-dev pkg-config
```

### 1.2 Install Python Packages

```bash
# Core Python libraries
sudo pip3 install --upgrade pip

sudo pip3 install \
  pyserial flask requests numpy \
  webrtcvad python-dotenv \
  azure-cognitiveservices-speech \
  openai google-cloud-texttospeech
```

### 1.3 Create Directory Structure

```bash
# Main directories
mkdir -p /home/rom/{modem_manager/config,SMS_Gateway,TTS,docs,audio_wav,audio_library}
mkdir -p /home/rom/{system_services,timing_analysis,transcriptions}

# Log directories (RAM disk for frequent writes)
sudo mkdir -p /var/log/voice_bot_ram
sudo chown rom:rom /var/log/voice_bot_ram

# SMS spool directories
sudo mkdir -p /var/spool/sms/{incoming,outgoing,sent,failed}
sudo chown -R rom:rom /var/spool/sms

# SMSTools log directory
sudo mkdir -p /var/log/smstools
sudo chown rom:rom /var/log/smstools
```

### 1.4 Add User to Required Groups

```bash
# Allow rom user to access serial devices and dialout
sudo usermod -aG dialout rom
sudo usermod -aG tty rom

# Re-login or run: newgrp dialout
```

---

## Phase 2: File Transfer from Pi

### 2.1 Transfer Core Scripts

```bash
# Transfer all Python scripts and shell scripts
rsync -avz --progress rom@10.100.0.11:/home/rom/*.py /home/rom/
rsync -avz --progress rom@10.100.0.11:/home/rom/*.sh /home/rom/

# Make scripts executable
chmod +x /home/rom/*.sh
chmod +x /home/rom/*.py
```

**Key Files to Transfer**:
- `sim7600_detector.py` - Modem auto-detection daemon
- `sim7600_voice_bot.py` - Voice call handler
- `monitoring_webhook.py` - Port 8070 monitoring API
- `internet_monitor.py` - Internet failover service
- `wg_failover.py` - WireGuard monitor
- `pi_send_message.sh` - VPS notification script
- `check_sim7600_status.sh` - Modem status reporter
- `trigger_internet_check.sh` - Priority internet check
- `monitor_tts_health.sh` - TTS queue monitor
- `log_monitor.sh` - Log error scanner
- `list_all_services.sh` - Service status lister
- `sms_watch.sh` - SMS file watcher

### 2.2 Transfer Service Directories

```bash
# Transfer SMS Gateway (Unified API)
rsync -avz --progress rom@10.100.0.11:/home/rom/SMS_Gateway/ /home/rom/SMS_Gateway/

# Transfer TTS modules
rsync -avz --progress rom@10.100.0.11:/home/rom/TTS/ /home/rom/TTS/

# Transfer modem manager (carriers database)
rsync -avz --progress rom@10.100.0.11:/home/rom/modem_manager/ /home/rom/modem_manager/

# Transfer systemd service files
rsync -avz --progress rom@10.100.0.11:/home/rom/system_services/ /home/rom/system_services/

# Transfer audio library (pre-recorded messages)
rsync -avz --progress rom@10.100.0.11:/home/rom/audio_library/ /home/rom/audio_library/

# Transfer documentation
rsync -avz --progress rom@10.100.0.11:/home/rom/docs/ /home/rom/docs/
```

### 2.3 Transfer Configuration Files

```bash
# Transfer environment variables
rsync -avz --progress rom@10.100.0.11:/home/rom/.env /home/rom/.env

# Transfer voice configurations
rsync -avz --progress rom@10.100.0.11:/home/rom/voice_config.json /home/rom/ 2>/dev/null || true
rsync -avz --progress rom@10.100.0.11:/home/rom/vad_config.py /home/rom/
rsync -avz --progress rom@10.100.0.11:/home/rom/*_config*.py /home/rom/

# Transfer requirements file if exists
rsync -avz --progress rom@10.100.0.11:/home/rom/requirements.txt /home/rom/ 2>/dev/null || true
```

### 2.4 Verify Transfers

```bash
# Check that key files exist
ls -lh /home/rom/sim7600_detector.py
ls -lh /home/rom/sim7600_voice_bot.py
ls -lh /home/rom/SMS_Gateway/unified_sms_voice_api.py
ls -lh /home/rom/monitoring_webhook.py
ls -lh /home/rom/modem_manager/config/carriers.json

echo "✓ File transfer complete!"
```

---

## Phase 3: Configuration

### 3.1 Configure SMSTools

Create `/etc/smsd.conf`:

```bash
sudo nano /etc/smsd.conf
```

```ini
devices = GSM1
loglevel = 7
logfile = /var/log/smstools/smsd.log
stats = /var/log/smstools/smsd_stats

[GSM1]
device = /dev/ttyUSB2
incoming = /var/spool/sms/incoming
outgoing = /var/spool/sms/outgoing
failed = /var/spool/sms/failed
sent = /var/spool/sms/sent
baudrate = 115200
check_memory_method = 1
memory_start = 1
```

### 3.2 Configure Environment Variables

Edit `/home/rom/.env`:

```bash
# Add/verify these settings:
LOG_MODE=production
VPS_IP=10.100.0.1
VPS_NOTIFICATION_PORT=5000
VPS_PHONE_PORT=8088
VPS_TRANSCRIPTION_PORT=9000
GATEWAY_COUNTRY=UK
```

### 3.3 Review Python Scripts

**IMPORTANT**: Check these files and update any Pi-specific paths:

```bash
# Check for hardcoded paths
grep -r "raspberry\|/home/pi" /home/rom/*.py

# Update if needed
nano /home/rom/sim7600_detector.py
nano /home/rom/sim7600_voice_bot.py
nano /home/rom/monitoring_webhook.py
```

Paths should use `/home/rom` not `/home/pi`.

---

## Phase 4: Service Installation

### 4.1 Install Systemd Services

```bash
# Copy service files to systemd directory
sudo cp /home/rom/system_services/sim7600-detector.service /etc/systemd/system/
sudo cp /home/rom/system_services/sim7600-voice-bot.service /etc/systemd/system/
sudo cp /home/rom/system_services/sms-api.service /etc/systemd/system/
sudo cp /home/rom/system_services/monitoring-webhook.service /etc/systemd/system/
sudo cp /home/rom/system_services/internet-monitor.service /etc/systemd/system/
sudo cp /home/rom/system_services/wg-failover.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload
```

### 4.2 Review Service Files

**CRITICAL**: Verify User and paths in service files:

```bash
# Check that services use 'rom' user (not 'pi')
grep "User=" /etc/systemd/system/sim7600*.service
grep "User=" /etc/systemd/system/sms-api.service

# Update if needed
sudo nano /etc/systemd/system/sim7600-detector.service
# Ensure: User=rom, WorkingDirectory=/home/rom
```

### 4.3 Create SMS-API Service

If not present, create `/etc/systemd/system/sms-api.service`:

```ini
[Unit]
Description=SMS API Service
After=network.target

[Service]
Type=simple
User=rom
WorkingDirectory=/home/rom/SMS_Gateway
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=/usr/bin/python3 /home/rom/SMS_Gateway/unified_sms_voice_api.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 4.4 Create SMSTools Service

Create `/etc/systemd/system/smstools.service`:

```ini
[Unit]
Description=SMSTools Daemon
After=network.target

[Service]
Type=forking
ExecStart=/usr/sbin/smsd -c/etc/smsd.conf
ExecStop=/usr/bin/killall smsd
PIDFile=/var/run/smsd.pid
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4.5 Enable Services (Don't Start Yet!)

```bash
# Enable services to start on boot
sudo systemctl enable sim7600-detector
sudo systemctl enable sim7600-voice-bot
sudo systemctl enable sms-api
sudo systemctl enable smstools
sudo systemctl enable monitoring-webhook
sudo systemctl enable internet-monitor
sudo systemctl enable wg-failover

# DO NOT start yet - need to test first!
```

---

## Phase 5: Testing

### 5.1 Test Modem Detection Manually

```bash
# Check modem is visible
lsusb | grep -i "1e0e"
ls -l /dev/ttyUSB*

# Test modem communication on ttyUSB3
picocom -b 115200 /dev/ttyUSB3

# In picocom, type:
AT
AT+CGMM  # Get model
AT+CIMI  # Get IMSI
AT+CGSN  # Get IMEI
# Press Ctrl+A then Ctrl+X to exit
```

Expected output:
- Model: SIM7600G-H or similar
- IMSI: 15-digit number
- IMEI: 15-digit number

### 5.2 Test Detector Script

```bash
# Run detector manually (will configure modem)
cd /home/rom
python3 sim7600_detector.py

# Watch logs in another terminal:
tail -f /var/log/voice_bot_ram/sim7600_detector.log
```

**Expected**:
- Modem detected
- USB composition checked (should be 9001)
- Carrier identified from IMSI
- APN configured (data + IMS)
- VoLTE enabled
- Port mapping saved to `/home/rom/sim7600_ports.json`

### 5.3 Verify Port Mapping

```bash
cat /home/rom/sim7600_ports.json
```

Should contain:
```json
{
  "config_port": "/dev/ttyUSB3",
  "nmea": "/dev/ttyUSB1",
  "sms_port": "/dev/ttyUSB2",
  "at_command": "/dev/ttyUSB3",
  "audio": "/dev/ttyUSB4",
  "apn": "internet",
  "ims_apn": "ims",
  "carrier": "O2 UK / giffgaff"
}
```

### 5.4 Test SMS Sending

```bash
# Create test SMS file
cat > /var/spool/sms/outgoing/test_sms << EOF
To: +447501234567
Alphabet: UCS
Message: Test message with diacritics: ąčęėįšųū
EOF

# Start SMSTools manually
sudo systemctl start smstools

# Watch logs
tail -f /var/log/smstools/smsd.log

# Check if sent
ls -l /var/spool/sms/sent/
```

### 5.5 Test Unified API (Port 8088)

```bash
# Start API service
sudo systemctl start sms-api

# Test from another terminal
curl http://localhost:8088/health

# Test TTS generation (if keys configured)
curl -X POST http://localhost:8088/phone_call \
  -H "Content-Type: application/json" \
  -d '{
    "callId": "test_123",
    "sessionId": "session_123",
    "text": "Hello, this is a test",
    "action": "speak",
    "priority": "high",
    "language": "en-GB",
    "audio_format": "pcm"
  }'
```

### 5.6 Test Monitoring API (Port 8070)

```bash
# Start monitoring service
sudo systemctl start monitoring-webhook

# Test from another terminal or VPS
curl http://10.100.0.2:8070/monitor/help
curl http://10.100.0.2:8070/monitor/sim7600/sync
curl http://10.100.0.2:8070/monitor/system
```

### 5.7 Test Voice Bot

**WARNING**: Only test if you want to receive/answer calls!

```bash
# Start voice bot
sudo systemctl start sim7600-voice-bot

# Watch logs
tail -f /var/log/voice_bot_ram/sim7600_voice_bot.log

# Make a test call to the SIM card
# Voice bot should:
# 1. Detect RING
# 2. Fetch config from VPS
# 3. Answer after N rings (based on config)
# 4. Play welcome message
# 5. Listen for speech
# 6. Transcribe via VPS
# 7. Respond with TTS
```

---

## Phase 6: Start All Services

Once testing passes:

```bash
# Start all services
sudo systemctl start sim7600-detector
sudo systemctl start smstools
sudo systemctl start sms-api
sudo systemctl start monitoring-webhook
sudo systemctl start internet-monitor
sudo systemctl start wg-failover

# Voice bot starts automatically via detector
# Check status
sudo systemctl status sim7600-detector
sudo systemctl status sim7600-voice-bot
sudo systemctl status sms-api
sudo systemctl status smstools
sudo systemctl status monitoring-webhook

# View logs
journalctl -u sim7600-detector -f
journalctl -u sim7600-voice-bot -f
```

---

## Phase 7: VPS Integration

### 7.1 Update VPS Configuration

The Jetson will use IP `10.100.0.2` (current) or `10.100.0.3` if changed.

**VPS endpoints to update**:
1. Notification receiver (port 5000) - add Jetson IP
2. Phone webhook (port 8088) - add Jetson IP
3. Voice config webhook - add Jetson IP

### 7.2 Test VPS Communication

```bash
# Test notification sending
/home/rom/pi_send_message.sh "Jetson migration complete - testing notifications" "info"

# Check VPS received it (check VPS logs)

# Test from VPS - trigger monitoring
curl http://10.100.0.2:8070/monitor/system
```

---

## Troubleshooting

### Modem Not Detected

```bash
# Check USB
lsusb | grep -i "1e0e\|qualcomm\|simtech"

# Check ttyUSB devices
ls -l /dev/ttyUSB*

# Check dmesg for USB errors
sudo dmesg | grep -i "usb\|tty" | tail -50

# Restart detector
sudo systemctl restart sim7600-detector
journalctl -u sim7600-detector -f
```

### SMSTools Port Lock Issues

```bash
# Check if port is locked
sudo lsof | grep ttyUSB

# Stop SMSTools
sudo systemctl stop smstools

# Wait 5 seconds
sleep 5

# Start detector first
sudo systemctl restart sim7600-detector

# SMSTools will auto-start via detector
```

### VoLTE Not Working

```bash
# Check modem VoLTE status
picocom -b 115200 /dev/ttyUSB3
AT+CEVOLTE?  # Should return: +CEVOLTE: 1,1

# Check PDP contexts
AT+CGACT?    # Should show contexts 1 and 2 active

# Check network registration
AT+CREG?     # Should show registered (1 or 5)

# Restart modem configuration
sudo systemctl restart sim7600-detector
```

### Port Conflicts

```bash
# Check what's using port 8088
sudo lsof -i :8088

# Check what's using port 8070
sudo lsof -i :8070

# Kill if needed
sudo kill <PID>

# Or restart service
sudo systemctl restart sms-api
sudo systemctl restart monitoring-webhook
```

### SMS Not Sending

```bash
# Check SMSTools status
sudo systemctl status smstools

# Check logs
tail -f /var/log/smstools/smsd.log

# Check queues
ls -l /var/spool/sms/outgoing/
ls -l /var/spool/sms/failed/

# Test modem can send SMS manually
picocom -b 115200 /dev/ttyUSB2
AT+CMGF=1
AT+CMGS="+447501234567"
> Test message
> <Ctrl+Z>
```

### Diacritics Not Working in SMS

SMSTools should use **UCS-2 encoding** for Unicode:

```bash
# SMS file format:
cat > /var/spool/sms/outgoing/test << EOF
To: +447501234567
Alphabet: UCS
Message: Lithuanian text: ąčęėįšųū žemė
EOF
```

If still broken:
- Check `/etc/smsd.conf` has no `alphabet =` override
- Use `Alphabet: UCS` in SMS files
- Check modem supports UCS-2: `AT+CSCS?` (should show "UCS2")

---

## Service Dependencies

### Service Start Order

1. **sim7600-detector** (starts first, manages everything)
   ↓
2. Configures modem
   ↓
3. Starts **smstools** (locks ttyUSB2)
   ↓
4. Starts **sim7600-voice-bot** (uses ttyUSB3 + ttyUSB4)

**Independent services** (start on boot):
- **sms-api** (port 8088) - can start anytime
- **monitoring-webhook** (port 8070) - can start anytime
- **internet-monitor** - monitors internet, starts QMI if needed
- **wg-failover** - monitors WireGuard VPN

### Port Usage

| Port | Service | Purpose |
|------|---------|---------|
| ttyUSB0 | Diagnostics | **DO NOT USE** (causes broken pipe) |
| ttyUSB1 | GPS/NMEA | Optional GPS data |
| ttyUSB2 | SMSTools | SMS send/receive (locked) |
| ttyUSB3 | Voice Bot + Config | AT commands + call handling |
| ttyUSB4 | Voice Bot Audio | 8kHz PCM audio during calls |
| 8088 | Unified API | TTS generation + SMS API |
| 8070 | Monitoring | Remote health checks |

---

## File Checklist

### Core Scripts (must transfer)
- ✅ `sim7600_detector.py`
- ✅ `sim7600_voice_bot.py`
- ✅ `monitoring_webhook.py`
- ✅ `internet_monitor.py`
- ✅ `pi_send_message.sh`
- ✅ `check_sim7600_status.sh`
- ✅ `trigger_internet_check.sh`

### Directories (must transfer)
- ✅ `SMS_Gateway/` (especially `unified_sms_voice_api.py`)
- ✅ `TTS/` (tts_azure.py, tts_openai.py, tts_google.py, tts_base.py)
- ✅ `modem_manager/config/carriers.json`
- ✅ `system_services/` (all .service files)
- ✅ `audio_library/` (pre-recorded messages)
- ✅ `docs/` (reference documentation)

### Configuration Files
- ✅ `.env`
- ✅ `voice_config.json`
- ✅ `vad_config.py`
- ✅ `voice_config_manager.py`

### System Files (create/configure)
- ✅ `/etc/smsd.conf`
- ✅ `/etc/systemd/system/*.service`

---

## Success Criteria

After migration, the Jetson should:

1. **Auto-detect modem** when plugged in
2. **Configure modem** automatically with correct APN + VoLTE
3. **Send SMS** with Unicode/diacritics support
4. **Receive SMS** and forward to VPS
5. **Answer calls** based on VPS webhook configuration
6. **Transcribe speech** via VPS Whisper API
7. **Respond with TTS** using configured voice
8. **Expose port 8088** for TTS/SMS API
9. **Expose port 8070** for monitoring
10. **Internet failover** to modem QMI when WiFi fails
11. **VPN monitoring** keeps WireGuard connected

---

## Next Steps After Migration

1. **Test thoroughly** with real calls and SMS
2. **Monitor logs** for errors
3. **Update VPS** to recognize Jetson IP (10.100.0.2)
4. **Configure voice settings** via VPS webhook
5. **Test diacritics** in SMS (Lithuanian, Polish, etc.)
6. **Test VoLTE calls** for audio quality
7. **Test internet failover** (disconnect WiFi, verify QMI starts)
8. **Document any Jetson-specific changes**

---

## Emergency Rollback

If something goes wrong:

```bash
# Stop all services
sudo systemctl stop sim7600-detector sim7600-voice-bot sms-api smstools monitoring-webhook

# Release modem ports
sudo killall smsd
sudo killall python3

# Restart modem (physical replug)
# Or use AT command: AT+CFUN=1,1 (radio restart)
```

---

## Support Resources

**Pi Documentation** (transferred to Jetson):
- `/home/rom/docs/PI_SERVICES_EXPLAINED.md` - This guide
- `/home/rom/docs/SIM7600_MODEM_CONFIGURATION.md` - Modem setup
- `/home/rom/docs/VAD_CONVERSATION_FLOW.md` - Voice bot conversation
- `/home/rom/docs/DUAL_THRESHOLD_VAD.md` - VAD system
- `/home/rom/docs/VPS_API_PAYLOAD_SPEC.md` - VPS API reference

**Log Files**:
- `/var/log/voice_bot_ram/sim7600_detector.log`
- `/var/log/voice_bot_ram/sim7600_voice_bot.log`
- `/var/log/voice_bot_ram/unified_api.log`
- `/var/log/smstools/smsd.log`
- `journalctl -u <service-name>`

---

**Generated**: 2026-01-07
**Author**: Claude (Claude Code)
**Version**: 1.0
