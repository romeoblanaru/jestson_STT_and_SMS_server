#!/bin/bash
###############################################################################
# Start SMSD (normal startup)
# Clears manual stop flag to re-enable auto-restart
###############################################################################

MANUAL_STOP_FLAG="/tmp/smsd_manual_stop"
LOG="/var/log/smsd_monitor.log"

echo "Starting SMSD..."

# Start SMSD
echo 'Romy_1202' | sudo -S /usr/sbin/smsd

sleep 3

if pgrep -x "smsd" > /dev/null; then
    echo "✓ SMSD started successfully"

    # Remove manual stop flag to re-enable auto-restart
    if [ -f "$MANUAL_STOP_FLAG" ]; then
        rm -f "$MANUAL_STOP_FLAG"
        echo "✓ Auto-restart RE-ENABLED (flag cleared)"
        echo "[$(date)] Flag cleared by smsd_start.sh" >> "$LOG"
    fi

    echo ""
    echo "SMSD is running and will auto-restart if crashed"
else
    echo "✗ Failed to start SMSD"
    exit 1
fi
