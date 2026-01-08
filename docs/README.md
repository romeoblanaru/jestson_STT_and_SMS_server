# SIM7600 Voice Bot & SMS Gateway System

Professional Raspberry Pi-based voice bot and SMS gateway system with automatic modem detection and management.

## Overview

This system provides:
- **Automated SIM7600 modem detection** with USB hot-plug support
- **Voice bot** with progressive transcription (Whisper) and TTS
- **SMS Gateway** with Unicode support via SMSTools
- **Multi-carrier support** across 40+ European carriers (Lithuania, UK, Germany, etc.)
- **WireGuard VPN** integration for secure remote management
- **Robust disconnect handling** with 20-second grace period for modem resets

## Architecture

```
SIM7600 Modem (USB)
  ├─ /dev/ttyUSB0 - Diagnostic
  ├─ /dev/ttyUSB1 - GPS/NMEA
  ├─ /dev/ttyUSB2 - AT Commands (SMSTools)
  ├─ /dev/ttyUSB3 - AT Commands (Voice Bot)
  └─ /dev/ttyUSB4 - PCM Audio (8kHz, 16-bit)

Services:
  ├─ sim7600-detector.service  → Auto-detects modem, starts services
  ├─ sim7600-voice-bot.service → Voice bot with VAD & Whisper
  ├─ smstools.service          → SMS gateway
  └─ voice-config-init.service → Fetches VPS config on boot
```

## Key Features

### 1. Smart Modem Detection
- **USB hot-plug support** - automatically detects when modem is plugged/unplugged
- **20-second grace period** - prevents service restart during modem firmware resets
- **EMI-safe initialization** - gradual power ramp to avoid USB hub interference
- **Port validation** - verifies all 5 ports before starting services

### 2. Voice Bot (`sim7600_voice_bot.py`)
- **Dynamic call control** - fetches fresh config from VPS on every ring
- **VAD-based conversation** - WebRTC VAD with 800ms silence detection
- **Progressive transcription** - Whisper integration ready
- **Serial PCM audio** - 8kHz raw audio via /dev/ttyUSB4
- **Multi-TTS support** - Azure, OpenAI, Google, Liepa (Lithuanian)

### 3. SMS Gateway
- **Unicode SMS support** - handles UTF-8, emojis, special characters
- **HTTP API** - REST endpoint on port 8088
- **SMSTools integration** - reliable message queue management
- **Auto-restart handling** - stops/starts SMSTools as needed

### 4. Disconnect Protection
When modem disconnects (USB unplug, firmware reset, etc.):
1. **t=0s**: Disconnect detected, 20s grace period starts
2. **t=1-19s**: Services keep running, waiting for reconnect
3. **t<20s + reconnect**: Grace period canceled, services continue
4. **t≥20s**: Services stopped cleanly (true disconnect)

## Quick Start

### Prerequisites
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv git smstools
```

### Installation
```bash
# Clone repository
cd /home/rom
git clone <repo-url> .

# Install Python dependencies
pip3 install -r requirements.txt

# Install system services
sudo ./install_services.sh

# Configure environment
cp .env.example .env
nano .env  # Add API keys
```

### Configuration Files
- **`.env`** - API keys, VPS endpoints (NEVER commit this!)
- **`CLAUDE.md`** - System documentation for AI assistant
- **`/etc/smsd.conf`** - SMSTools configuration
- **Service files** in `/home/rom/system_services/`

## System Services

```bash
# Check modem detector
systemctl status sim7600-detector

# Check voice bot
systemctl status sim7600-voice-bot

# Check SMS gateway
systemctl status smstools

# View logs
journalctl -u sim7600-detector -f
journalctl -u sim7600-voice-bot -f
tail -f /var/log/smstools/smsd.log
```

## File Structure

```
/home/rom/
├── sim7600_detector.py         # Main modem detector daemon
├── sim7600_voice_bot.py        # Voice bot with VAD
├── voice_config_manager.py     # VPS config fetcher
├── voice_init.sh               # Boot initialization script
├── vad_config.py               # VAD configuration
├── pi_send_message.sh          # VPS notification helper
├── CLAUDE.md                   # AI assistant documentation
├── README.md                   # This file
├── .env                        # Environment variables (SECRET!)
├── TTS/                        # TTS modules (Azure, OpenAI, etc.)
├── SMS_Gateway/                # SMS API server
├── docs/                       # Documentation
├── system_services/            # Systemd service files
├── modem_manager/              # Multi-carrier configs (40+ carriers)
└── to_test/                    # Test scripts
```

## Network Architecture

- **WireGuard VPN**: Secure connection to VPS (10.100.0.10/24)
- **WiFi Priority**: RomeoSamsung (30) > TP-Link_Romeo (20)
- **VPS Endpoints**:
  - System notifications: `http://10.100.0.1:5000/api/send`
  - Phone call data: `http://10.100.0.1:8088/webhook/phone_call/receive`
  - Voice config: `http://my-bookings.co.uk/webhooks/get_voice_config.php`

## Call Handling Flow

1. **RING detected** → Fetch voice config from VPS
2. **Check `answer_after_rings`**:
   - If `-1`: Don't answer (reject call)
   - If `1-10`: Answer after N rings
3. **After answering**: Play welcome message via TTS
4. **During call**: Use VAD to detect when caller stops speaking
5. **Transcribe** caller audio with Whisper (when integrated)

See `/home/rom/CALL_HANDLING_FLOW.md` for complete flow.

## Troubleshooting

### Modem not detected
```bash
# Check USB devices
lsusb | grep -i simcom

# Check ttyUSB ports
ls -la /dev/ttyUSB*

# Check detector logs
journalctl -u sim7600-detector -f
```

### Voice bot not answering calls
```bash
# Verify RING notifications enabled
sudo systemctl stop smstools
timeout 3 bash -c 'echo -e "AT+CRC?\r" > /dev/ttyUSB3; sleep 0.5; cat /dev/ttyUSB3'
sudo systemctl start smstools
# Expected: +CRC: 1

# Restart voice bot
sudo systemctl restart sim7600-voice-bot
```

### SMS not working
```bash
# Check SMSTools status
systemctl status smstools

# Check logs
tail -f /var/log/smstools/smsd.log

# Test AT commands (stop SMSTools first!)
sudo systemctl stop smstools
picocom -b 115200 /dev/ttyUSB2
AT
AT+CPIN?
AT+CREG?
```

## Development

### Adding New TTS Provider
1. Create new module in `TTS/tts_newprovider.py`
2. Inherit from `TTS/tts_base.py`
3. Implement `synthesize()` method
4. Update voice bot to import new provider

### Testing Voice Bot
```bash
# Debug mode (verbose logging)
LOG_MODE=development python3 sim7600_voice_bot.py

# Test audio recording
python3 to_test/test_audio_recording.py

# Monitor detector
python3 sim7600_detector.py
```

## Multi-Country Deployment (Future)

The `/home/rom/modem_manager/` directory contains:
- **40+ carrier configurations** (MCC-MNC codes, APNs, VoLTE)
- **Auto-detection** based on SIM IMSI
- **Ready for deployment** across Europe (UK, Lithuania, Germany, Poland, etc.)

Currently using hardcoded APN for UK testing. Will integrate when scaling.

## Security Notes

- **Never commit `.env`** - contains API keys and credentials
- **WireGuard keys** are generated per-device
- **VPS authentication** uses IP whitelisting via VPN
- **SMS API** accessible only via VPN (10.100.0.x)

## License

Proprietary - Internal use only

## Credits

- **Author**: Romeo's Voice Bot Team
- **Hardware**: Raspberry Pi 4 + SIM7600G-H modem
- **Key Libraries**: WebRTC VAD, Whisper, SMSTools, PySerial
