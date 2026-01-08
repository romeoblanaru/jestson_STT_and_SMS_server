# NVIDIA Jetson Orin Nano - STT and SMS Server

This repository contains the complete setup for an NVIDIA Jetson Orin Nano station running Speech-to-Text (STT) services and SMS gateway functionality.

## Hardware

- **Device**: NVIDIA Jetson Orin Nano
- **Operating System**: Linux 5.15.148-tegra (JetPack)
- **Modem**: SIMCOM SIM7600G-H 4G LTE module
- **Purpose**: AI services (STT) and SMS gateway

## Features

### 1. Speech-to-Text (STT) Services
- Multiple STT engines support
- Optimized for Jetson hardware acceleration
- Real-time speech recognition
- Support for multiple languages

### 2. SMS Gateway
- Bidirectional SMS communication
- Unicode/diacritics support (Romanian, Lithuanian, etc.)
- VPS integration via webhooks
- Real-time monitoring dashboard
- Automatic message forwarding
- PDU mode for reliable multipart messages

## Directory Structure

```
/home/rom/
├── sms_watch.sh              # SMS activity monitor
├── docs/                      # Documentation
│   └── SMS_SERVER_TROUBLESHOOTING_GUIDE.md
├── whisper.cpp/              # Whisper.cpp STT engine
├── riva_quickstart_v2.19.0/  # NVIDIA Riva STT
├── parakeet-tdt-0.6b-v3/     # Parakeet TDT model
├── CLAUDE.md                 # System context
├── LARGE_FILES.md            # Large files documentation
└── .gitignore

/etc/
├── smsd.conf                 # SMS Tools configuration
└── systemd/system/
    └── smstools.service      # SMS Tools systemd service

/usr/local/bin/
└── sms_handler_unicode.py    # SMS event handler

/var/spool/sms/               # SMS queues
├── incoming/
├── outgoing/
├── checked/
├── failed/
└── sent/

/var/log/
├── smstools/                 # SMS Tools logs
├── voice_bot_ram/            # Application logs
│   ├── unified_api.log
│   └── sms_gateway.log
```

## SMS Server Setup

### Prerequisites

```bash
sudo apt-get update
sudo apt-get install smstools python3 python3-pip
```

### Configuration

1. **Configure modem** (persistent device path):
   ```bash
   # Find modem by-id path
   ls -l /dev/serial/by-id/

   # Update /etc/smsd.conf with correct device path
   device = /dev/serial/by-id/usb-SimTech__Incorporated_*
   ```

2. **PDU Mode** (critical for Unicode support):
   - SMS Tools uses PDU mode by default
   - Supports multipart messages
   - Full diacritics support (ăâîșț, ąčęėįšųūž)

3. **Event Handler**:
   ```bash
   sudo cp sms_handler_unicode.py /usr/local/bin/
   sudo chmod +x /usr/local/bin/sms_handler_unicode.py
   ```

4. **Start service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable smstools
   sudo systemctl start smstools
   ```

### SMS Monitoring

Real-time SMS activity monitoring with chronological ordering:

```bash
cd /home/rom
./sms_watch.sh
```

**Features**:
- Incoming messages with light blue background highlight
- Outgoing messages in orange
- VPS integration status (success/failure)
- Message bodies displayed
- Chronological sorting (300ms buffer)
- Color-coded message types

**Display Legend**:
- `→ IN` (light blue background) - Incoming SMS
- `← OUT` (orange) - Outgoing SMS
- `↑ MSG` (green) - Successfully sent to VPS
- `↓ RECEIVED` (green) - Message from VPS
- `← SYSTEM` (cyan) - System messages (VODAFONE)
- `✗ ERROR` (red) - Modem or VPS errors

## STT Services

### Faster-Whisper

Small model optimized for real-time transcription.

### Whisper.cpp

Quantized models for efficient inference on Jetson hardware.

### NVIDIA Riva

Enterprise-grade streaming ASR with Parakeet models.

## Troubleshooting

See detailed troubleshooting guide:
- [SMS Server Troubleshooting Guide](docs/SMS_SERVER_TROUBLESHOOTING_GUIDE.md)

### Quick Diagnostics

```bash
# Check SMS service status
sudo systemctl status smstools

# Check modem communication
sudo smsd -c/etc/smsd.conf -v

# View live logs
tail -f /var/log/smstools/smsd.log

# Check message queues
ls -la /var/spool/sms/outgoing/
ls -la /var/spool/sms/incoming/

# Test SMS sending
echo "Test message" | sudo smssend +1234567890
```

### Common Issues

1. **Modem not responding**: Check device path in `/etc/smsd.conf`
2. **Messages stuck**: Check for `.LOCK` files in `/var/spool/sms/checked/`
3. **Unicode issues**: Ensure PDU mode is enabled (no `AT+CMGF=1` in config)
4. **Service restarts**: Check PID file path in systemd service

## VPS Integration

The SMS gateway integrates with a VPS webhook for bidirectional messaging:

1. Incoming SMS → Event handler → VPS webhook
2. VPS responds → Unified API → SMS gateway → Outgoing SMS

**Configuration**: Set VPS webhook URL in `sms_handler_unicode.py`

## Large Files

Model files over 300MB are excluded from this repository. See [LARGE_FILES.md](LARGE_FILES.md) for:
- Model descriptions
- Download instructions
- Disk space requirements

## Installation on New Machine

1. Clone this repository
2. Install prerequisites (see above)
3. Copy configuration files to system locations
4. Download required models (see LARGE_FILES.md)
5. Configure modem device path
6. Start services

## Maintenance

### Log Rotation

Logs are stored in `/var/log/` and should be rotated regularly.

### Queue Monitoring

Monitor SMS queues for stuck messages:
```bash
watch -n 5 'ls -la /var/spool/sms/outgoing/ /var/spool/sms/checked/'
```

### Backup

Important files to backup:
- `/etc/smsd.conf`
- `/usr/local/bin/sms_handler_unicode.py`
- `/etc/systemd/system/smstools.service`
- Application logs

## Credits

- SMSTools: http://smstools3.kekekasvi.com/
- NVIDIA Riva: https://docs.nvidia.com/deeplearning/riva/
- Faster-Whisper: https://github.com/guillaumekln/faster-whisper
- Whisper.cpp: https://github.com/ggerganov/whisper.cpp

## License

Configuration and scripts in this repository are provided as-is for deployment on NVIDIA Jetson Orin Nano devices.
