# Configuration Backup

This directory contains backups of system configurations for the Jetson Orin Nano SMS/STT server.

## Contents

- `crontab/` - User crontab jobs
- `gammu/` - Gammu and SMSD configuration files
- `systemd/` - Systemd service files

## Restoration Instructions

### Crontab
```bash
crontab config/crontab/rom.crontab
```

### Gammu Configuration
```bash
sudo cp config/gammu/gammurc /etc/gammurc
sudo cp config/gammu/gammu-smsdrc /etc/gammu-smsdrc
```

### Systemd Services
```bash
sudo cp config/systemd/*.service /etc/systemd/system/
sudo cp config/systemd/*.timer /etc/systemd/system/
sudo systemctl daemon-reload

# Enable services as needed:
sudo systemctl enable ec25-port-monitor.timer
sudo systemctl enable incoming-sms-processor.service
sudo systemctl enable modem-health-monitor.service
sudo systemctl enable sms-api.service
sudo systemctl enable parakeet-asr.service
```

## Last Updated
2025-01-18
