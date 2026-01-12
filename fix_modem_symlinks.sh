#!/bin/bash
###############################################################################
# Fix SIM7600 Modem Symlinks
# Removes old symlinks and recreates them based on current Interface assignments
###############################################################################

LOG="/var/log/modem_symlink_fix.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "=== Fixing SIM7600 Modem Symlinks ==="

# Remove old symlinks if they exist
log "Removing old symlinks..."
rm -f /dev/ttyUSB_SIM7600_AT 2>/dev/null
rm -f /dev/ttyUSB_SIM7600_DIAG 2>/dev/null
rm -f /dev/ttyUSB_SIM7600_VOICE 2>/dev/null
rm -f /dev/ttyUSB_SIM7600_AUDIO 2>/dev/null

# Detect and create new symlinks based on Interface Numbers
log "Detecting interface assignments..."

for port in /dev/ttyUSB*; do
    [ -c "$port" ] || continue

    INTERFACE=$(udevadm info -a "$port" 2>/dev/null | grep -m1 'ATTRS{bInterfaceNumber}' | grep -o '"[^"]*"' | tr -d '"')

    case "$INTERFACE" in
        "00")
            ln -sf "$port" /dev/ttyUSB_SIM7600_DIAG
            log "Interface 00 (Diagnostics) -> $port -> /dev/ttyUSB_SIM7600_DIAG"
            ;;
        "02")
            ln -sf "$port" /dev/ttyUSB_SIM7600_AT
            log "Interface 02 (AT/SMS) -> $port -> /dev/ttyUSB_SIM7600_AT"
            AT_PORT="$port"
            ;;
        "03")
            ln -sf "$port" /dev/ttyUSB_SIM7600_VOICE
            log "Interface 03 (Voice) -> $port -> /dev/ttyUSB_SIM7600_VOICE"
            ;;
        "04")
            ln -sf "$port" /dev/ttyUSB_SIM7600_AUDIO
            log "Interface 04 (Audio) -> $port -> /dev/ttyUSB_SIM7600_AUDIO"
            ;;
    esac
done

# Set permissions
chmod 666 /dev/ttyUSB_SIM7600_* 2>/dev/null

log "Current symlinks:"
ls -la /dev/ttyUSB_SIM7600_* 2>/dev/null | tee -a "$LOG"

# Reload udev rules for future auto-updates
log "Reloading udev rules..."
udevadm control --reload-rules 2>&1 | tee -a "$LOG"
udevadm trigger 2>&1 | tee -a "$LOG"

# Send notification
if [ -n "$AT_PORT" ]; then
    NOTIFICATION="✅ SIM7600 Symlinks Fixed

AT Port: /dev/ttyUSB_SIM7600_AT -> $AT_PORT

All symlinks updated to current USB configuration.

System: Jetson Orin Nano (10.100.0.2)
Time: $(date '+%Y-%m-%d %H:%M:%S')"

    /home/rom/pi_send_message.sh "$NOTIFICATION" info 2>&1 | tee -a "$LOG"
fi

log "=== Symlink Fix Complete ==="
