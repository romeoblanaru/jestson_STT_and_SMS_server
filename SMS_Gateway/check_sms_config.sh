#!/bin/bash
# SMS Configuration Monitor - Checks if PDU mode is still active

CONFIG_FILE="/etc/smsd.conf"
BACKUP_FILE="/etc/smsd.conf.working_pdu"
LOG_FILE="/var/log/sms_config_monitor.log"

# Check if PDU mode is still enabled
if ! grep -q "AT+CMGF=0" "$CONFIG_FILE"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: PDU mode disabled in smsd.conf!" | tee -a "$LOG_FILE"
    logger -t SMS_CONFIG "CRITICAL: PDU mode disabled - Unicode SMS will fail!"
    
    # Check if different from backup
    if ! diff -q "$CONFIG_FILE" "$BACKUP_FILE" >/dev/null 2>&1; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Configuration differs from working backup" | tee -a "$LOG_FILE"
        echo "To restore: sudo cp $BACKUP_FILE $CONFIG_FILE" | tee -a "$LOG_FILE"
    fi
    exit 1
fi

# Optional: Check other critical settings
if ! grep -q "decode_unicode_text = yes" "$CONFIG_FILE"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: Unicode decoding disabled!" | tee -a "$LOG_FILE"
    exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Configuration check OK - PDU mode active" >> "$LOG_FILE"