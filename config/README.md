# Configuration Files

This directory contains important system configuration files for the SMS server.

## Files

### etc/smsd.conf
- **Description**: SMS Tools daemon configuration
- **Install location**: `/etc/smsd.conf`
- **Permissions**: 644 (root:root)
- **Important**: Update `device` path to match your modem's by-id path

### systemd/smstools.service
- **Description**: Systemd service unit for SMS Tools
- **Install location**: `/etc/systemd/system/smstools.service`
- **Permissions**: 644 (root:root)
- **After changes**: Run `sudo systemctl daemon-reload`

### sms_handler_unicode.py
- **Description**: Event handler for incoming SMS (forwards to VPS)
- **Install location**: `/usr/local/bin/sms_handler_unicode.py`
- **Permissions**: 755 (root:root)
- **Important**: Update VPS webhook URL in the script

## Installation

```bash
# Copy configuration files
sudo cp config/etc/smsd.conf /etc/
sudo cp config/systemd/smstools.service /etc/systemd/system/
sudo cp config/sms_handler_unicode.py /usr/local/bin/

# Set permissions
sudo chmod 644 /etc/smsd.conf
sudo chmod 644 /etc/systemd/system/smstools.service
sudo chmod 755 /usr/local/bin/sms_handler_unicode.py

# Update modem device path in smsd.conf
sudo nano /etc/smsd.conf
# Find your modem: ls -l /dev/serial/by-id/

# Reload and start service
sudo systemctl daemon-reload
sudo systemctl enable smstools
sudo systemctl start smstools
```

## Configuration Notes

### smsd.conf Key Settings

- **device**: Must use `/dev/serial/by-id/` path for persistence
- **PDU mode**: Do NOT add `AT+CMGF=1` (breaks multipart Unicode)
- **eventhandler**: Points to sms_handler_unicode.py
- **autosplit**: Set to 3 for automatic message splitting
- **loglevel**: 5 for detailed logging

### sms_handler_unicode.py

Update these variables:
- **VPS_WEBHOOK_URL**: Your VPS endpoint
- **TIMEOUT**: Webhook timeout (default 10 seconds)
- **MAX_RETRIES**: Number of retry attempts (default 3)

## Troubleshooting

If SMS service fails to start:

1. Check device path:
   ```bash
   ls -l /dev/serial/by-id/
   ```

2. Verify modem responds:
   ```bash
   sudo smsd -c/etc/smsd.conf -v
   ```

3. Check logs:
   ```bash
   tail -f /var/log/smstools/smsd.log
   ```

4. Verify PID file path matches in service and config
