#!/bin/bash
###############################################################################
# Manually stop SMSD for debugging (prevents auto-restart)
###############################################################################

MANUAL_STOP_FLAG="/tmp/smsd_manual_stop"

echo "Stopping SMSD manually for debugging..."

# Create flag to prevent auto-restart
touch "$MANUAL_STOP_FLAG"
echo "[$(date)] SMSD manually stopped for debugging" > "$MANUAL_STOP_FLAG"

# Stop SMSD
sudo pkill -9 smsd

sleep 2

if ! pgrep -x "smsd" > /dev/null; then
    echo "✓ SMSD stopped successfully"
    echo "✓ Auto-restart DISABLED (debugging mode)"
    echo ""
    echo "To restart: run ./smsd_manual_start.sh"

    # Log to sms_watch (appears in yellow like other SMSD messages)
    echo "$(date '+%Y-%m-%d %H:%M:%S') SYSTEM: [WARNING] 🛑 SMSD manually stopped for debugging (auto-restart disabled)" >> /var/log/smstools/smsd.log
else
    echo "✗ Failed to stop SMSD"
    rm -f "$MANUAL_STOP_FLAG"
    exit 1
fi
