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
echo 'Romy_1202' | sudo -S pkill -9 smsd

sleep 2

if ! pgrep -x "smsd" > /dev/null; then
    echo "✓ SMSD stopped successfully"
    echo "✓ Auto-restart DISABLED (debugging mode)"
    echo ""
    echo "To restart: run ./smsd_manual_start.sh"
else
    echo "✗ Failed to stop SMSD"
    rm -f "$MANUAL_STOP_FLAG"
    exit 1
fi
