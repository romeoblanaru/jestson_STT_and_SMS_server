# Pi Services Complete Documentation
**Complete Guide to Replicate SMS/Voice/Modem System on Another Station**

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Hardware Requirements](#hardware-requirements)
3. [Service Architecture](#service-architecture)
4. [Core Services](#core-services)
5. [Support Scripts](#support-scripts)
6. [Configuration Files](#configuration-files)
7. [Network & VPN](#network--vpn)
8. [File Structure](#file-structure)
9. [Replication Guide](#replication-guide)
10. [Dependencies](#dependencies)

---

## System Overview

This Raspberry Pi operates as a **GSM Voice/SMS Gateway** with:
- **SIM7600G-H modem** for voice calls and SMS
- **VoLTE (4G) voice calls** with real-time transcription
- **SMS sending/receiving** via SMSTools
- **Unified API** for TTS and SMS operations (port 8088)
- **WireGuard VPN** connection to VPS (10.100.0.x network)
- **Auto-detection** of modem on USB plug-in
- **Remote monitoring** webhook (port 8070)
- **Internet failover** to modem QMI when WiFi/WAN fails

**Primary VPN IPs:**
- This Pi: `10.100.0.11`
- VPS: `10.100.0.1`
- Client machines: `10.100.0.2`, `10.100.0.3`, etc.

---

## Hardware Requirements

### Modem
- **Model**: SIM7600G-H (USB dongle)
- **Vendor ID**: 1e0e (Qualcomm)
- **USB Composition**: 9001 (voice-stable mode)
- **Ports Created**:
  - `/dev/ttyUSB0` - Diagnostics (DO NOT USE - causes broken pipe)
  - `/dev/ttyUSB1` - GPS/NMEA
  - `/dev/ttyUSB2` - AT Commands (SMSTools - locked for SMS)
  - `/dev/ttyUSB3` - AT Commands (Main port - voice + config)
  - `/dev/ttyUSB4` - PCM Audio (8kHz, 16-bit raw audio during calls)
  - `/dev/cdc-wdm0` - QMI interface (for internet)
  - `wwan0` - Network interface (QMI data)

### Raspberry Pi
- **Model**: Raspberry Pi 3B+ or 4 recommended
- **RAM**: 4GB (minimum 2GB)
- **Storage**: 32GB microSD (29GB+ usable)
- **OS**: Raspberry Pi OS (Debian-based, kernel 6.12+)

### Network
- **Primary**: WiFi (RomeoSamsung priority 30, TP-Link_Romeo priority 20)
- **Backup**: Modem QMI internet via wwan0
- **VPN**: WireGuard to VPS (10.100.0.0/24 network)

---

## Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Raspberry Pi Station                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────┐      ┌──────────────┐                    │
│  │  SIM7600 USB  │─────▶│  USB Kernel  │                    │
│  │   Modem       │      │   (udev)     │                    │
│  └───────────────┘      └──────┬───────┘                    │
│                                 │                             │
│                                 ▼                             │
│                   ┌─────────────────────────┐                │
│                   │ sim7600-detector.service│                │
│                   │ /home/rom/sim7600_detector.py           │
│                   └──────────┬──────────────┘                │
│                              │                                │
│         ┌────────────────────┼────────────────────┐          │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────┐   ┌───────────────┐   ┌──────────────┐   │
│  │  smstools    │   │ sim7600-voice │   │   sms-api    │   │
│  │  (ttyUSB2)   │   │  -bot.service │   │ (port 8088)  │   │
│  │              │   │  (ttyUSB3/4)  │   │              │   │
│  └──────┬───────┘   └───────┬───────┘   └──────┬───────┘   │
│         │                   │                   │           │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         WireGuard VPN (wg0) - 10.100.0.11            │  │
│  └───────────────────────────┬──────────────────────────┘  │
│                               │                             │
│  ┌────────────────────────────┼──────────────────────────┐ │
│  │ Monitoring (8070)  Internet Monitor  WG Failover     │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
                ┌───────────────────────────────┐
                │  VPS (10.100.0.1)             │
                ├───────────────────────────────┤
                │ • Notifications (port 5000)   │
                │ • Phone events (port 8088)    │
                │ • Transcription (port 9000)   │
                │ • Voice config (webhook)      │
                └───────────────────────────────┘
```

---

## Core Services

### 1. SIM7600 Detector Service
**File**: `/home/rom/sim7600_detector.py`
**Service**: `/etc/systemd/system/sim7600-detector.service`
**Status**: `systemctl status sim7600-detector`

**What it does:**
- Monitors USB bus for SIM7600 modem plug-in via udev rules
- Verifies USB composition mode (9001 = voice-stable)
- Changes USB composition if needed (9011 → 9001)
- Performs gradual modem initialization (EMI-safe power ramp)
- Configures Data APN + IMS APN (carrier-specific from database)
- Enables VoLTE (AT+CEVOLTE=1,1)
- Activates PDP contexts (Data + IMS for VoLTE)
- Tests serial ports (ttyUSB2, ttyUSB3)
- Saves port mapping to `/home/rom/sim7600_ports.json`
- Starts SMSTools and Voice Bot services
- Sends status report to VPS

**Modem Initialization Sequence:**
```bash
Step 0: AT+CUSBPIDSWITCH=9001,1,1 (if needed) → wait 8s
Step 1: AT+CFUN=0 (radio OFF) → wait 3s
Step 2: AT+CFUN=1 (radio ON) → wait 3s
Step 3a: AT+CGDCONT=1,"IP","<data_apn>" → wait 2s
Step 3b: AT+CGDCONT=2,"IPV4V6","<ims_apn>" → wait 2s
Step 4: Wait 10s for network
Step 5a: AT+CGACT=1,1 (activate Data) → wait 2s
Step 5b: AT+CGACT=1,2 (activate IMS) → wait 3s
Step 6: Wait 3s
Step 7: AT+CEVOLTE=1,1 (enable VoLTE) → wait 5s
```

**Dependencies:**
- Python 3
- `pyserial` library
- `/home/rom/modem_manager/config/carriers.json`

**Auto-start**: ✅ Enabled (triggered by udev on USB insertion)

**Configuration:**
- `/home/rom/sim7600_ports.json` (generated, contains port mapping + APN)

---

### 2. SIM7600 Voice Bot Service
**File**: `/home/rom/sim7600_voice_bot.py`
**Service**: `/etc/systemd/system/sim7600-voice-bot.service`
**Status**: `systemctl status sim7600-voice-bot`
**Logs**: `journalctl -u sim7600-voice-bot -f` and `/var/log/sim7600_voice_bot.log`

**What it does:**
- Listens for incoming calls on ttyUSB3 (AT+CLIP, AT+CRC)
- Fetches fresh voice config from VPS on EVERY RING
- Decides whether to answer based on `answer_after_rings` value:
  - `-1` = Don't answer (reject call)
  - `1-10` = Answer after N rings
- Answers call with `ATA` command
- Enables PCM audio on ttyUSB4 (AT+CPCMREG=1)
- Plays welcome message via TTS
- **VAD-based conversation flow**:
  - Listens for caller speech via ttyUSB4 (8kHz, 16-bit PCM)
  - WebRTC VAD detects 800ms silence before bot responds
  - Sends audio chunks to VPS for Whisper transcription + LLM response
  - Dual-threshold VAD system (progressive transcription)
- Generates TTS responses via local API (port 8088)
- Plays audio back through ttyUSB4
- Handles call hangup and cleanup
- Saves call recordings to `/home/rom/audio_wav/`
- Sends call events to VPS webhook (ring, answer, hangup)

**Voice Bot Initialization (on service start):**
```bash
AT          # Test connection
ATE0        # Disable echo
AT+CSCLK=0  # Disable auto-sleep (prevents I/O errors)
AT+CLVL=5   # Set volume
AT+CLIP=1   # Enable caller ID
AT+CRC=1    # Enable RING notifications
ATS0=0      # Disable modem auto-answer (manual control via webhook)
AT+CEVOLTE=1,1  # Enable VoLTE
```

**Dependencies:**
- Python 3
- `pyserial`, `webrtcvad`, `numpy`, `requests`
- TTS API (port 8088)
- VPS transcription endpoint (10.100.0.1:9000)
- VPS voice config endpoint (my-bookings.co.uk webhook)

**Auto-start**: ✅ Enabled (started by detector after modem init)

**Audio Files**: `/home/rom/audio_wav/` (raw PCM, OGG Opus, transcriptions)

**Related Docs:**
- `/home/rom/CALL_HANDLING_FLOW.md`
- `/home/rom/docs/VAD_CONVERSATION_FLOW.md`
- `/home/rom/docs/DUAL_THRESHOLD_VAD.md`
- `/home/rom/docs/VPS_API_PAYLOAD_SPEC.md`

---

### 3. SMSTools Service
**Binary**: `/usr/sbin/smsd`
**Service**: `/etc/systemd/system/smstools.service`
**Config**: `/etc/smsd.conf`
**Status**: `systemctl status smstools`
**Logs**: `/var/log/smstools/smsd.log`

**What it does:**
- Receives SMS messages via ttyUSB2
- Saves incoming SMS to `/var/spool/sms/incoming/`
- Sends outgoing SMS from `/var/spool/sms/outgoing/`
- Triggers event handler on SMS arrival (optional)
- Keeps ttyUSB2 port locked exclusively

**Configuration**: `/etc/smsd.conf`
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

# Optional: Trigger internet check on SMS arrival
# eventhandler = /home/rom/trigger_internet_check.sh "Incoming SMS"
```

**CRITICAL**: SMSTools locks ttyUSB2 exclusively!
- Voice bot uses ttyUSB3 (no conflict)
- Detector stops SMSTools temporarily for configuration

**Auto-start**: ✅ Enabled (started by detector after modem init)

**Related Docs**: `/home/rom/SMSTOOLS_HANDLING.md`

---

### 4. Unified SMS/Voice API Service
**File**: `/home/rom/SMS_Gateway/unified_sms_voice_api.py`
**Service**: `/etc/systemd/system/sms-api.service`
**Port**: 8088 (listens on 0.0.0.0)
**Status**: `systemctl status sms-api`

**What it does:**
- Provides unified HTTP API for TTS generation and SMS sending
- Handles multiple TTS engines (Azure, OpenAI, Google, Liepa)
- Manages TTS queue with priorities
- Generates audio files in multiple formats (PCM, WAV, OGG)
- Sends SMS via SMSTools (writes to `/var/spool/sms/outgoing/`)
- Forwards messages to VPS notification endpoint

**API Endpoints:**

**TTS Generation:**
```bash
POST http://localhost:8088/phone_call
{
  "callId": "1234567890",
  "sessionId": "session_123",
  "text": "Hello world",
  "action": "speak",
  "priority": "high",
  "language": "en-GB",
  "audio_format": "pcm"
}
```

**SMS Sending:**
```bash
POST http://localhost:8088/sms/send
{
  "to": "+447501234567",
  "message": "Test message",
  "priority": "1"
}
```

**Message to VPS:**
```bash
POST http://localhost:8088/pi_send_message
{
  "message": "Status update",
  "severity": "info"
}
```

**TTS Module Files**: `/home/rom/TTS/`
- `tts_azure.py` - Azure Cognitive Services TTS
- `tts_openai.py` - OpenAI TTS
- `tts_google.py` - Google Cloud TTS
- `tts_liepa.py` - Liepa TTS (Lithuanian)
- `tts_base.py` - Base abstract class

**Dependencies:**
- Python 3
- Flask, requests
- TTS engine libraries (azure-cognitiveservices-speech, openai, google-cloud-texttospeech)

**Auto-start**: ✅ Enabled (starts on boot)

**CRITICAL**: Never run manually! Use systemctl only to avoid port conflicts.

---

### 5. Monitoring Webhook Service
**File**: `/home/rom/monitoring_webhook.py`
**Service**: `/etc/systemd/system/monitoring-webhook.service`
**Port**: 8070 (listens on 0.0.0.0)
**Status**: `systemctl status monitoring-webhook`

**What it does:**
- Provides HTTP API for remote monitoring/health checks
- Allows VPS to trigger system reports via HTTP
- Two modes: async (background) and sync (returns output)
- Executes monitoring scripts and returns results

**API Endpoints:**

**Async Mode** (returns immediately):
```bash
GET/POST http://10.100.0.11:8070/monitor/vpn
GET/POST http://10.100.0.11:8070/monitor/system
GET/POST http://10.100.0.11:8070/monitor/system-full
GET/POST http://10.100.0.11:8070/monitor/network
GET/POST http://10.100.0.11:8070/monitor/sim7600
GET/POST http://10.100.0.11:8070/monitor/tts
GET/POST http://10.100.0.11:8070/monitor/logs
```

**Sync Mode** (waits for output):
```bash
GET/POST http://10.100.0.11:8070/monitor/sim7600/sync
GET/POST http://10.100.0.11:8070/monitor/tts/sync
GET/POST http://10.100.0.11:8070/monitor/logs/sync
```

**Custom Message:**
```bash
POST http://10.100.0.11:8070/monitor/custom
{
  "message": "Custom alert",
  "severity": "warning"
}
```

**Help:**
```bash
GET http://10.100.0.11:8070/monitor/help
```

**Dependencies:**
- Python 3
- Flask
- Monitoring scripts (see Support Scripts section)

**Auto-start**: ✅ Enabled (starts on boot)

---

### 6. Internet Monitor Service
**File**: `/home/rom/internet_monitor.py`
**Service**: `/etc/systemd/system/internet-monitor.service`
**Status**: `systemctl status internet-monitor`
**Logs**: `journalctl -u internet-monitor -f` or `/var/log/voice_bot_ram/internet_monitor.log`

**What it does:**
- Auto-detects primary network interface (wlan0, eth0, etc.)
- Pings 8.8.8.8 through primary interface every 30 seconds
- After 3 consecutive failures (90s), starts QMI backup internet
- Continues monitoring primary interface (not wwan0!)
- When primary recovers, stops QMI automatically
- **Priority mode**: When call/SMS arrives, checks internet instantly
- If internet down during call/SMS, starts QMI immediately (skips 90s wait)

**Configuration:**
- Check interval: 30s (normal mode)
- Failure threshold: 3 failures = 90s (normal mode)
- Priority mode: Instant check + instant QMI (call/SMS)
- Primary interface: Auto-detected (NOT wwan0)
- APN: Auto-loaded from `/home/rom/sim7600_ports.json`
- QMI device: `/dev/cdc-wdm0`
- Signal file: `/tmp/internet_check_priority`

**Manual Trigger:**
```bash
/home/rom/trigger_internet_check.sh "Custom reason"
```

**Manual QMI Start:**
```bash
sudo qmicli -d /dev/cdc-wdm0 --wds-start-network "apn='internet',ip-type=4" --client-no-release-cid
```

**Dependencies:**
- Python 3
- `qmi-utils` package (qmicli command)
- `/home/rom/sim7600_ports.json` (APN configuration)

**Auto-start**: ✅ Enabled (starts on boot)

**Related Script**: `/home/rom/trigger_internet_check.sh`

---

### 7. WireGuard Failover Service
**File**: `/home/rom/wg_failover.py`
**Service**: `/etc/systemd/system/wg-failover.service`
**Status**: `systemctl status wg-failover`

**What it does:**
- Monitors WireGuard VPN connection (10.100.0.1)
- Pings VPS every 30 seconds
- Restarts WireGuard if connection fails
- Ensures VPN stays connected for VPS communication

**Configuration:**
- Check interval: 30s
- VPS endpoint: 10.100.0.1
- WireGuard interface: wg0

**Dependencies:**
- Python 3
- WireGuard installed (`wg` command)

**Auto-start**: ✅ Enabled (starts on boot)

**VPN Config**: `/etc/wireguard/wg0.conf`

---

## Support Scripts

### 1. pi_send_message.sh
**Location**: `/home/rom/pi_send_message.sh`

**What it does:**
- Sends status messages/alerts to VPS
- Called by all services for notifications
- Supports different actions: vpn, system, network, etc.

**Usage:**
```bash
/home/rom/pi_send_message.sh "Message text" "severity"
/home/rom/pi_send_message.sh vpn
/home/rom/pi_send_message.sh system
/home/rom/pi_send_message.sh system-full
```

**VPS Endpoint**: `http://10.100.0.1:5000/api/send`

---

### 2. trigger_internet_check.sh
**Location**: `/home/rom/trigger_internet_check.sh`

**What it does:**
- Signals internet monitor to check connection immediately
- Used by voice bot when call arrives (priority mode)
- Creates signal file: `/tmp/internet_check_priority`

**Usage:**
```bash
/home/rom/trigger_internet_check.sh "Incoming call"
```

---

### 3. check_sim7600_status.sh
**Location**: `/home/rom/check_sim7600_status.sh`

**What it does:**
- Comprehensive SIM7600 modem status report
- Queries signal, network, carrier, IMEI, IMSI, APN, VoLTE
- Called by monitoring webhook

**Usage:**
```bash
/home/rom/check_sim7600_status.sh
```

**Checks:**
- Modem model and firmware
- SIM card status
- Signal strength (CSQ)
- Network registration (CREG)
- Carrier name (COPS)
- IMEI and IMSI
- APN configuration (CGDCONT)
- PDP context status (CGACT)
- VoLTE status (CEVOLTE)

---

### 4. monitor_tts_health.sh
**Location**: `/home/rom/monitor_tts_health.sh`

**What it does:**
- Monitors TTS queue and voice call status
- Checks for stuck TTS jobs
- Reports active calls

**Usage:**
```bash
/home/rom/monitor_tts_health.sh
```

---

### 5. log_monitor.sh
**Location**: `/home/rom/log_monitor.sh`

**What it does:**
- Scans systemd logs for errors and restarts
- Reports recent service failures
- Identifies problematic services

**Usage:**
```bash
/home/rom/log_monitor.sh check
```

---

### 6. list_all_services.sh
**Location**: `/home/rom/list_all_services.sh`

**What it does:**
- Lists all systemd services and their status
- Reports which services are enabled/disabled

**Usage:**
```bash
/home/rom/list_all_services.sh
```

---

### 7. SMS Watch Script
**Location**: `/home/rom/sms_watch.sh`

**What it does:**
- Watches `/var/spool/sms/incoming/` for new SMS
- Processes incoming SMS files
- Can trigger custom actions on SMS arrival

**Usage:**
```bash
/home/rom/sms_watch.sh
```

---

## Configuration Files

### 1. sim7600_ports.json
**Location**: `/home/rom/sim7600_ports.json`
**Generated by**: `sim7600_detector.py`

**Contents:**
```json
{
  "at_port": "/dev/ttyUSB3",
  "sms_port": "/dev/ttyUSB2",
  "audio_port": "/dev/ttyUSB4",
  "gps_port": "/dev/ttyUSB1",
  "diag_port": "/dev/ttyUSB0",
  "qmi_device": "/dev/cdc-wdm0",
  "wwan_interface": "wwan0",
  "carrier": "O2 - UK",
  "mcc_mnc": "234-10",
  "data_apn": "internet",
  "ims_apn": "ims",
  "imsi": "234102345678901",
  "imei": "867698051234567",
  "usb_composition": "9001"
}
```

**Used by:**
- Voice bot (to find audio_port)
- Internet monitor (for APN)
- All services (for port mapping)

---

### 2. runtime_voice_config.json
**Location**: `/home/rom/runtime_voice_config.json`
**Generated by**: Voice bot (fetched from VPS webhook)

**Contents:**
```json
{
  "language": "en-GB",
  "tts_model": "azure",
  "answer_after_rings": 2,
  "welcome_message": "Hello, how can I help you?",
  "voice_settings": {
    "voice_name": "en-GB-SoniaNeural",
    "rate": "0%",
    "pitch": "0%"
  },
  "azure_key": "...",
  "azure_region": "uksouth"
}
```

**Updated**: On EVERY incoming call (fetched from VPS)

**Webhook**: `http://my-bookings.co.uk/webhooks/get_voice_config.php?ip={VPN_IP}&include_key=1`

---

### 3. carriers.json
**Location**: `/home/rom/modem_manager/config/carriers.json`
**Database**: 40+ European carriers with MCC-MNC codes

**Sample Entry:**
```json
{
  "carriers": {
    "234-10": {
      "name": "O2 - UK",
      "country": "United Kingdom",
      "data_apn": "internet",
      "ims_apn": "ims",
      "volte_supported": true,
      "mcc": "234",
      "mnc": "10"
    }
  }
}
```

**Used by**: Detector for automatic APN configuration

---

### 4. WireGuard Config
**Location**: `/etc/wireguard/wg0.conf`

```ini
[Interface]
Address = 10.100.0.11/32
PrivateKey = YLYkh/bvknUcyy8hiTdi2/f2RxtPN08ENBT+vB998lE=
DNS = 8.8.8.8

[Peer]
PublicKey = 2tdfztUSLQsD0s/wNKi4NeDWClou3LFnXoASKl2YGns=
Endpoint = 144.91.96.97:443
AllowedIPs = 10.100.0.0/24
PersistentKeepalive = 25
```

**Commands:**
```bash
sudo wg-quick up wg0
sudo wg-quick down wg0
sudo wg show
```

---

### 5. SMSTools Config
**Location**: `/etc/smsd.conf`

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

---

## Network & VPN

### VPS Endpoints (10.100.0.1)

**System Notifications:**
- URL: `http://10.100.0.1:5000/api/send`
- Used by: `pi_send_message.sh`
- Purpose: Status messages, alerts, events

**Phone Call Events:**
- URL: `http://10.100.0.1:8088/webhook/phone_call/receive`
- Used by: `sim7600_voice_bot.py`
- Purpose: Call events (ring, answer, hangup)

**VPS Transcription:**
- URL: `http://10.100.0.1:9000/api/transcribe`
- Used by: `sim7600_voice_bot.py`
- Payload: OGG Opus audio chunks (base64) + end_sentence signals
- Response: Transcription + LLM response + timing data
- Docs: `/home/rom/docs/DUAL_THRESHOLD_VAD.md`, `/home/rom/docs/VPS_API_PAYLOAD_SPEC.md`

**Voice Config Fetch:**
- URL: `http://my-bookings.co.uk/webhooks/get_voice_config.php?ip={VPN_IP}&include_key=1`
- Used by: `sim7600_voice_bot.py` (on every RING)
- Purpose: Fresh call configuration (language, TTS model, answer_after_rings, welcome_message)
- Returns: JSON with voice settings, Azure TTS keys, call behavior

### Local Endpoints (Raspberry Pi)

**TTS Generation:**
- URL: `http://localhost:8088/phone_call`
- Service: `unified_sms_voice_api.py`

**Local Message Sending:**
- URL: `http://localhost:8088/pi_send_message`
- Service: `unified_sms_voice_api.py`

**Monitoring Webhook:**
- URL: `http://10.100.0.11:8070/monitor/{action}`
- Service: `monitoring_webhook.py`

### Port Summary

**TCP Ports:**
- 22 - SSH server
- 8070 - Monitoring webhook
- 8088 - Unified SMS/Voice API
- 10000 - Webmin admin interface

**UDP Ports:**
- 38133 - WireGuard VPN
- 5353 - Avahi mDNS

---

## File Structure

```
/home/rom/
├── sim7600_detector.py              # Modem auto-detection service
├── sim7600_voice_bot.py             # Voice call handler (main service)
├── pi_send_message.sh               # Send status to VPS
├── trigger_internet_check.sh        # Trigger priority internet check
├── check_sim7600_status.sh          # Modem status report
├── monitor_tts_health.sh            # TTS queue monitor
├── log_monitor.sh                   # Log error scanner
├── list_all_services.sh             # Service status lister
├── sms_watch.sh                     # SMS incoming file watcher
├── internet_monitor.py              # Internet failover service
├── wg_failover.py                   # WireGuard monitor
├── monitoring_webhook.py            # Remote monitoring API
├── sim7600_ports.json               # Port mapping (generated)
├── runtime_voice_config.json        # Voice config cache
│
├── SMS_Gateway/
│   ├── unified_sms_voice_api.py     # Main API server (port 8088)
│   └── (legacy SMS scripts)
│
├── TTS/
│   ├── tts_base.py                  # Base TTS class
│   ├── tts_azure.py                 # Azure TTS
│   ├── tts_openai.py                # OpenAI TTS
│   ├── tts_google.py                # Google TTS
│   └── tts_liepa.py                 # Liepa TTS (Lithuanian)
│
├── modem_manager/
│   ├── config/
│   │   └── carriers.json            # 40+ carrier database
│   ├── scripts/
│   │   └── auto_configure_modem.sh  # Standalone config script
│   └── docs/
│       └── (carrier documentation)
│
├── audio_wav/                       # Call recordings
│   ├── call_*_incoming_raw_*.wav    # Raw PCM recordings
│   ├── call_*_vad_chunk_*.ogg       # VAD chunks (Opus)
│   ├── call_*_vad_chunk_*.wav.txt   # Transcriptions
│   └── call_*_outgoing_tts_*.wav    # TTS audio
│
├── audio_library/                   # Pre-recorded audio files
│   └── silence_fillers_expressions.txt
│
├── timing_analysis/                 # Call timing logs
│   ├── latest.json                  # Latest call timings
│   └── call_*.json                  # Individual call timings
│
├── to_test/                         # Test scripts
│   └── (test scripts)
│
├── system_services/                 # Service files (reference)
│   ├── sim7600-voice-bot.service
│   ├── sim7600-detector.service
│   ├── sms-api.service
│   ├── monitoring-webhook.service
│   ├── internet-monitor.service
│   ├── wg-failover.service
│   ├── sync-audio-library.service
│   ├── sync-audio-library.timer
│   └── sync-audio-library.sh
│
├── docs/                            # Documentation
│   ├── CLAUDE.md                    # System overview (main docs)
│   ├── CALL_HANDLING_FLOW.md        # Call flow documentation
│   ├── VAD_CONVERSATION_FLOW.md     # VAD implementation guide
│   ├── DUAL_THRESHOLD_VAD.md        # Dual VAD system docs
│   ├── VPS_API_PAYLOAD_SPEC.md      # VPS API specification
│   ├── SMSTOOLS_HANDLING.md         # SMSTools management
│   ├── SIM7600_MODEM_CONFIGURATION.md  # Modem config guide
│   ├── SERVICE_MANAGEMENT.md        # Service management guide
│   ├── AUDIO_OUTPUT_LOCATIONS.md    # Audio file organization
│   └── PI_SERVICES_EXPLAINED.md     # This file
│
└── CLAUDE.md                        # Main system documentation

/etc/
├── systemd/system/
│   ├── sim7600-detector.service     # Modem detector (installed)
│   ├── sim7600-voice-bot.service    # Voice bot (installed)
│   ├── sms-api.service              # API server (installed)
│   ├── smstools.service             # SMSTools (installed)
│   ├── monitoring-webhook.service   # Monitoring (installed)
│   ├── internet-monitor.service     # Internet failover (installed)
│   └── wg-failover.service          # VPN monitor (installed)
│
├── wireguard/
│   └── wg0.conf                     # WireGuard VPN config
│
├── ssh/
│   └── sshd_config                  # SSH server config
│
├── smsd.conf                        # SMSTools config
│
└── udev/rules.d/
    └── 99-sim7600.rules             # USB auto-detection rule

/var/
├── log/
│   ├── smstools/
│   │   └── smsd.log                 # SMSTools log
│   └── sim7600_voice_bot.log        # Voice bot log
│
├── spool/sms/
│   ├── incoming/                    # Received SMS
│   ├── outgoing/                    # SMS to send
│   ├── sent/                        # Sent SMS
│   └── failed/                      # Failed SMS
│
└── lib/systemd/
    └── (systemd state files)
```

---

## Replication Guide

### Step 1: Prepare Target Raspberry Pi

1. **Flash Raspberry Pi OS** (64-bit recommended)
   ```bash
   # Use Raspberry Pi Imager
   # Enable SSH during imaging
   ```

2. **Initial Setup**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   sudo apt install -y git python3 python3-pip python3-venv
   ```

3. **Create rom user** (if not using existing user)
   ```bash
   sudo adduser rom
   sudo usermod -aG sudo rom
   su - rom
   ```

---

### Step 2: Install System Dependencies

```bash
# Core utilities
sudo apt install -y python3-serial python3-flask python3-requests \
  python3-numpy python3-webrtcvad smstools wireguard qmi-utils \
  picocom minicom usbutils

# Optional: Webmin
# Follow webmin.com installation guide
```

---

### Step 3: Copy Files from Source Pi

**Method 1: rsync over network (recommended)**
```bash
# From target Pi, pull files from source Pi
rsync -avz --progress rom@10.100.0.11:/home/rom/ /home/rom/ \
  --exclude='audio_wav/*' \
  --exclude='timing_analysis/*' \
  --exclude='.cache' \
  --exclude='__pycache__'
```

**Method 2: USB transfer**
```bash
# Insert USB drive, mount it
sudo mount /dev/sda1 /mnt
sudo rsync -avz /home/rom/ /mnt/pi_backup/
sudo umount /mnt

# On target Pi
sudo mount /dev/sda1 /mnt
sudo rsync -avz /mnt/pi_backup/ /home/rom/
sudo umount /mnt
```

**Method 3: SD card clone**
```bash
# Follow SD card cloning procedure in CLAUDE.md
# Creates bootable copy on new card
```

---

### Step 4: Install Python Dependencies

```bash
cd /home/rom

# TTS engines
pip3 install azure-cognitiveservices-speech openai google-cloud-texttospeech

# Core libraries
pip3 install pyserial flask requests numpy webrtcvad

# Optional: Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt  # if requirements.txt exists
```

---

### Step 5: Copy System Configuration Files

```bash
# SMSTools config
sudo cp /etc/smsd.conf /etc/smsd.conf.backup  # backup existing
sudo nano /etc/smsd.conf
# Paste contents from source Pi

# Create SMS spool directories
sudo mkdir -p /var/spool/sms/{incoming,outgoing,sent,failed}
sudo chown -R rom:rom /var/spool/sms

# SSH config (if needed)
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
# Review and adjust if needed

# Log directories
sudo mkdir -p /var/log/smstools
sudo chown rom:rom /var/log/smstools
```

---

### Step 6: Install Systemd Services

```bash
# Copy service files
sudo cp /home/rom/system_services/*.service /etc/systemd/system/
sudo cp /home/rom/system_services/*.timer /etc/systemd/system/ 2>/dev/null || true

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable sim7600-detector
sudo systemctl enable sim7600-voice-bot
sudo systemctl enable sms-api
sudo systemctl enable smstools
sudo systemctl enable monitoring-webhook
sudo systemctl enable internet-monitor
sudo systemctl enable wg-failover

# DO NOT START YET - wait for VPN setup
```

---

### Step 7: Setup WireGuard VPN

1. **Generate new WireGuard keys**
   ```bash
   wg genkey | tee privatekey | wg pubkey > publickey
   cat privatekey  # Use this as PrivateKey
   cat publickey   # Send this to VPS admin
   ```

2. **Create WireGuard config**
   ```bash
   sudo nano /etc/wireguard/wg0.conf
   ```

   ```ini
   [Interface]
   Address = 10.100.0.XX/32  # Request new IP from VPS admin
   PrivateKey = <NEW_PRIVATE_KEY>
   DNS = 8.8.8.8

   [Peer]
   PublicKey = <VPS_PUBLIC_KEY>
   Endpoint = 144.91.96.97:443
   AllowedIPs = 10.100.0.0/24
   PersistentKeepalive = 25
   ```

3. **Add peer to VPS WireGuard config**
   ```bash
   # On VPS (10.100.0.1), add to /etc/wireguard/wg0.conf:
   [Peer]
   PublicKey = <NEW_PI_PUBLIC_KEY>
   AllowedIPs = 10.100.0.XX/32
   ```

4. **Start VPN**
   ```bash
   sudo wg-quick up wg0
   sudo systemctl enable wg-quick@wg0

   # Test connectivity
   ping 10.100.0.1  # Should reach VPS
   ```

---

### Step 8: Configure WiFi (if needed)

```bash
# List available networks
nmcli device wifi list

# Connect to WiFi
sudo nmcli device wifi connect "SSID" password "PASSWORD"

# Set priority
sudo nmcli connection modify "SSID" connection.autoconnect-priority 30

# Check status
nmcli connection show
```

---

### Step 9: Setup udev Rules for Modem

```bash
# Create udev rule for SIM7600 auto-detection
sudo nano /etc/udev/rules.d/99-sim7600.rules
```

Add:
```
# SIM7600 USB Modem Auto-Detection
ACTION=="add", SUBSYSTEM=="usb", ATTRS{idVendor}=="1e0e", ATTRS{idProduct}=="9001", RUN+="/bin/systemctl restart sim7600-detector.service"
```

Reload udev:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

---

### Step 10: Start Services

```bash
# Start API first (needed by voice bot)
sudo systemctl start sms-api
sudo systemctl status sms-api

# Start monitoring
sudo systemctl start monitoring-webhook
sudo systemctl status monitoring-webhook

# Start internet monitor
sudo systemctl start internet-monitor
sudo systemctl status internet-monitor

# Start VPN monitor
sudo systemctl start wg-failover
sudo systemctl status wg-failover

# Plug in SIM7600 modem - should auto-detect and start voice bot + smstools
# Watch logs:
journalctl -u sim7600-detector -f
```

---

### Step 11: Test System

**Test VPN:**
```bash
ping 10.100.0.1
curl http://10.100.0.1:5000/api/test
```

**Test Monitoring:**
```bash
curl http://localhost:8070/monitor/help
curl http://localhost:8070/monitor/system
```

**Test TTS API:**
```bash
curl -X POST http://localhost:8088/phone_call \
  -H "Content-Type: application/json" \
  -d '{
    "callId": "test123",
    "sessionId": "session1",
    "text": "Hello world",
    "action": "speak",
    "language": "en-GB"
  }'
```

**Test SMS (when modem connected):**
```bash
# Check modem ports
cat /home/rom/sim7600_ports.json

# Check SMSTools
sudo systemctl status smstools
tail -f /var/log/smstools/smsd.log

# Send test SMS
echo "Test message" | sudo tee /var/spool/sms/outgoing/test.txt
```

**Test Voice (call the SIM card number):**
```bash
# Watch voice bot logs
journalctl -u sim7600-voice-bot -f
tail -f /var/log/sim7600_voice_bot.log
```

---

### Step 12: Update VPS Configuration

On VPS, add new Pi to monitoring/webhook systems:

1. **Add to voice config webhook** (my-bookings.co.uk)
   - Map new VPN IP (10.100.0.XX) to voice settings

2. **Add to notification system** (port 5000)
   - Allow messages from new Pi IP

3. **Add to transcription whitelist** (port 9000)
   - Allow transcription requests from new Pi IP

---

## Dependencies

### System Packages
```bash
sudo apt install -y \
  python3 python3-pip python3-venv \
  python3-serial python3-flask python3-requests \
  python3-numpy python3-webrtcvad \
  smstools wireguard qmi-utils \
  picocom minicom usbutils \
  git curl wget net-tools
```

### Python Libraries
```bash
pip3 install \
  pyserial \
  flask \
  requests \
  numpy \
  webrtcvad \
  azure-cognitiveservices-speech \
  openai \
  google-cloud-texttospeech
```

### Optional Tools
```bash
# Webmin (web admin interface)
# Follow: https://webmin.com/download/

# tcpdump (network debugging)
sudo apt install tcpdump

# lsof (port debugging)
sudo apt install lsof

# htop (process monitor)
sudo apt install htop

# socat (network testing)
sudo apt install socat
```

---

## Service Startup Order

**Critical order** for proper operation:

1. **Boot** → `sim7600-detector.service` (waits for USB)
2. **USB plug** → Detector triggers:
   - Stops SMSTools (if running)
   - Stops Voice Bot (if running)
   - Configures modem
   - Starts `smstools.service` (FIRST)
   - Starts `sim7600-voice-bot.service` (SECOND)
3. **Independent services** (can start anytime):
   - `sms-api.service` (port 8088)
   - `monitoring-webhook.service` (port 8070)
   - `internet-monitor.service`
   - `wg-failover.service`

**Why this order?**
- SMSTools locks ttyUSB2 for SMS
- Voice Bot uses ttyUSB3/4 for calls
- Both need modem initialized first
- API needed for TTS generation

---

## Troubleshooting

### Modem not detected
```bash
# Check USB devices
lsusb | grep 1e0e

# Check serial ports
ls -l /dev/ttyUSB*

# Check detector logs
journalctl -u sim7600-detector -n 50

# Manually trigger detector
sudo systemctl restart sim7600-detector
```

### Voice bot not answering calls
```bash
# Check voice bot status
systemctl status sim7600-voice-bot
journalctl -u sim7600-voice-bot -f

# Check RING notifications enabled
sudo systemctl stop smstools
timeout 3 bash -c 'echo -e "AT+CRC?\r" > /dev/ttyUSB3; sleep 0.5; cat /dev/ttyUSB3'
sudo systemctl start smstools

# Expected: +CRC: 1 (enabled)
# If 0: Restart voice bot
sudo systemctl restart sim7600-voice-bot
```

### SMS not working
```bash
# Check SMSTools
systemctl status smstools
tail -f /var/log/smstools/smsd.log

# Check port
cat /home/rom/sim7600_ports.json | grep sms_port

# Test AT commands (STOP smstools first!)
sudo systemctl stop smstools
timeout 3 bash -c 'echo -e "AT\r" > /dev/ttyUSB2; sleep 0.5; cat /dev/ttyUSB2'
sudo systemctl start smstools
```

### VPN not working
```bash
# Check WireGuard status
sudo wg show

# Check handshake (should be recent)
# If > 2 minutes, connection broken

# Restart WireGuard
sudo wg-quick down wg0
sudo wg-quick up wg0

# Ping VPS
ping 10.100.0.1
```

### Internet failover not working
```bash
# Check internet monitor
systemctl status internet-monitor
journalctl -u internet-monitor -f

# Check QMI device
ls -l /dev/cdc-wdm0

# Manual QMI test
sudo qmicli -d /dev/cdc-wdm0 --wds-start-network "apn='internet',ip-type=4" --client-no-release-cid

# Check wwan0 interface
ip addr show wwan0
```

### Port 8088 already in use
```bash
# NEVER run unified_sms_voice_api.py manually!
# It creates crash loop if run outside systemd

# Kill all instances
sudo pkill -f unified_sms_voice_api.py

# Restart service properly
sudo systemctl restart sms-api
```

---

## VPS Requirements

For complete system operation, VPS must provide:

1. **WireGuard VPN Server** (144.91.96.97:443)
   - Accepts peer connections
   - Routes traffic between peers (IP forwarding enabled)
   - AllowedIPs: 10.100.0.0/24

2. **Notification API** (10.100.0.1:5000/api/send)
   - Receives status messages from Pi
   - Stores/displays alerts

3. **Phone Events Webhook** (10.100.0.1:8088/webhook/phone_call/receive)
   - Receives call events (ring, answer, hangup)
   - Logs call history

4. **Transcription API** (10.100.0.1:9000/api/transcribe)
   - Receives audio chunks (OGG Opus, base64)
   - Returns transcription + LLM response
   - Dual-threshold VAD system
   - See: `/home/rom/docs/VPS_API_PAYLOAD_SPEC.md`

5. **Voice Config Webhook** (my-bookings.co.uk/webhooks/get_voice_config.php)
   - Returns JSON config per VPN IP
   - Includes: language, tts_model, answer_after_rings, welcome_message, voice_settings, Azure keys

**VPS Firewall Rules:**
```bash
# Allow WireGuard
sudo iptables -A INPUT -p udp --dport 443 -j ACCEPT

# Allow VPN traffic forwarding
sudo iptables -A FORWARD -i wg0 -o wg0 -j ACCEPT
sudo sysctl -w net.ipv4.ip_forward=1
```

---

## Security Notes

1. **SSH Keys**: Use public key authentication (already configured)
2. **VPN Only**: Expose APIs only on VPN interface (10.100.0.x)
3. **Firewall**: No iptables/nftables configured - relies on VPN isolation
4. **Root Access**: Webmin allows root login (port 10000) - secure with strong password
5. **Service Isolation**: Each service runs as `rom` user (not root, except SMSTools)

---

## Backup Strategy

**Before replication, backup:**
```bash
# Configuration files
/etc/smsd.conf
/etc/wireguard/wg0.conf
/etc/systemd/system/*.service

# User data
/home/rom/sim7600_ports.json
/home/rom/runtime_voice_config.json
/home/rom/modem_manager/config/carriers.json

# Scripts
/home/rom/*.py
/home/rom/*.sh
/home/rom/SMS_Gateway/
/home/rom/TTS/

# Audio library
/home/rom/audio_library/
```

**Full SD card clone:**
```bash
# See CLAUDE.md section "SD Card Backup & Cloning"
# Fast clone method creates bootable card in ~15 minutes
```

---

## Quick Reference

**Service Commands:**
```bash
# Status
systemctl status sim7600-detector
systemctl status sim7600-voice-bot
systemctl status smstools
systemctl status sms-api

# Restart
sudo systemctl restart sim7600-voice-bot
sudo systemctl restart smstools
sudo systemctl restart sms-api

# Logs
journalctl -u sim7600-voice-bot -f
tail -f /var/log/sim7600_voice_bot.log
tail -f /var/log/smstools/smsd.log

# Enable/Disable
sudo systemctl enable sim7600-voice-bot
sudo systemctl disable sim7600-voice-bot
```

**Modem Commands:**
```bash
# Status
cat /home/rom/sim7600_ports.json
/home/rom/check_sim7600_status.sh

# AT commands (STOP smstools first!)
sudo systemctl stop smstools
picocom -b 115200 /dev/ttyUSB3
# AT commands here
# Ctrl+A, Ctrl+X to exit
sudo systemctl start smstools
```

**Network Commands:**
```bash
# VPN
sudo wg show
ping 10.100.0.1

# WiFi
nmcli device status
nmcli connection show

# Internet failover
systemctl status internet-monitor
/home/rom/trigger_internet_check.sh "Manual test"
```

**Monitoring Commands:**
```bash
# Remote (from VPS)
curl http://10.100.0.11:8070/monitor/system
curl http://10.100.0.11:8070/monitor/sim7600/sync

# Local
/home/rom/check_sim7600_status.sh
/home/rom/monitor_tts_health.sh
/home/rom/log_monitor.sh check
```

---

## Additional Documentation

**Main Documentation:**
- `/home/rom/CLAUDE.md` - Complete system overview

**Call Handling:**
- `/home/rom/CALL_HANDLING_FLOW.md` - Call flow documentation
- `/home/rom/docs/VAD_CONVERSATION_FLOW.md` - VAD implementation
- `/home/rom/docs/DUAL_THRESHOLD_VAD.md` - Dual VAD system

**VPS Integration:**
- `/home/rom/docs/VPS_API_PAYLOAD_SPEC.md` - API specification

**Modem Configuration:**
- `/home/rom/docs/SIM7600_MODEM_CONFIGURATION.md` - Modem setup
- `/home/rom/modem_manager/docs/` - Carrier documentation

**Service Management:**
- `/home/rom/docs/SERVICE_MANAGEMENT.md` - Service guide
- `/home/rom/SMSTOOLS_HANDLING.md` - SMSTools management

**Audio Files:**
- `/home/rom/docs/AUDIO_OUTPUT_LOCATIONS.md` - Audio organization

---

## Support & Troubleshooting

**Logs to check when issues occur:**
```bash
# Service status
systemctl status sim7600-detector sim7600-voice-bot smstools sms-api

# Detailed logs
journalctl -u sim7600-detector -n 100
journalctl -u sim7600-voice-bot -n 100
tail -100 /var/log/sim7600_voice_bot.log
tail -100 /var/log/smstools/smsd.log

# System logs
dmesg | grep -i usb
dmesg | grep -i tty

# Network
sudo wg show
ip addr show
ip route show
ping 10.100.0.1
```

**Common Issues:**
1. **Modem not detected** → Check USB cable, run `lsusb`, restart detector
2. **No incoming calls** → Check AT+CRC=1, restart voice bot
3. **No SMS** → Check SMSTools logs, verify ttyUSB2 port
4. **VPN down** → Check WireGuard handshake, ping VPS
5. **API errors** → Check port 8088 not in use, restart sms-api

---

**Document Version**: 1.0
**Last Updated**: 2026-01-07
**System Version**: v3.0 (Instant Answer + Dual VAD)
**Author**: Auto-generated from system analysis

---

**END OF DOCUMENTATION**
