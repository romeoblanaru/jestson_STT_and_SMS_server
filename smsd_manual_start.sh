#!/bin/bash
###############################################################################
# Manually start SMSD and re-enable auto-restart
###############################################################################

MANUAL_STOP_FLAG="/tmp/smsd_manual_stop"

echo "Starting SMSD and re-enabling auto-restart..."

# Start SMSD
sudo /usr/sbin/smsd

sleep 3

if pgrep -x "smsd" > /dev/null; then
    echo "✓ SMSD started successfully"

    # Remove manual stop flag to re-enable auto-restart
    if [ -f "$MANUAL_STOP_FLAG" ]; then
        rm -f "$MANUAL_STOP_FLAG"
        echo "✓ Auto-restart RE-ENABLED"
        echo "[$(date)] Flag cleared by smsd_manual_start.sh" >> /var/log/smsd_monitor.log
    fi

    echo ""
    echo "SMSD is running and will auto-restart if crashed"

    # Log to sms_watch (appears in yellow like other SMSD messages)
    echo "$(date '+%Y-%m-%d %H:%M:%S') SYSTEM: [INFO] ▶️ SMSD manually started (auto-restart re-enabled)" >> /var/log/smstools/smsd.log
else
    echo "✗ Failed to start SMSD"
    exit 1
fi
