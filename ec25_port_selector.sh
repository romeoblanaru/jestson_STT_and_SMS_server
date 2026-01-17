#!/bin/bash
###############################################################################
# EC25 Modem Port Selector
# Automatically detects and selects the correct AT command port for SMSTools
# Handles dynamic USB composition changes (ttyUSB2 ↔ ttyUSB3)
###############################################################################

SYMLINK="/dev/ttyUSB_AT"
LOG="/var/log/ec25_port_selector.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

# Wait for devices to settle
sleep 2

# Check which AT ports exist (priority: ttyUSB2 > ttyUSB3)
if [ -e "/dev/ttyUSB_EC25_AT" ]; then
    # Interface 02 exists (ttyUSB2) - preferred
    TARGET=$(readlink -f /dev/ttyUSB_EC25_AT)
    log "EC25 AT port detected: $TARGET (interface 02 - ttyUSB2)"
elif [ -e "/dev/ttyUSB_EC25_AT_FALLBACK" ]; then
    # Interface 03 exists (ttyUSB3) - fallback
    TARGET=$(readlink -f /dev/ttyUSB_EC25_AT_FALLBACK)
    log "EC25 AT port detected: $TARGET (interface 03 - ttyUSB3 fallback)"
else
    log "ERROR: No EC25 AT command port detected!"
    exit 1
fi

# Create/update the main symlink
if [ -L "$SYMLINK" ]; then
    CURRENT=$(readlink -f "$SYMLINK")
    if [ "$CURRENT" != "$TARGET" ]; then
        log "Updating symlink: $SYMLINK -> $TARGET (was: $CURRENT)"
        rm -f "$SYMLINK"
        ln -s "$TARGET" "$SYMLINK"

        # Restart SMSTools if it's running
        if pgrep smsd > /dev/null; then
            log "Restarting SMSTools to use new port..."
            pkill -9 smsd
            sleep 2
            /usr/sbin/smsd -p/var/run/smstools/smsd.pid -i/var/run/smstools/smsd.working -uroot -groot
            log "SMSTools restarted"
        fi
    else
        log "Symlink already correct: $SYMLINK -> $TARGET"
    fi
else
    log "Creating symlink: $SYMLINK -> $TARGET"
    ln -s "$TARGET" "$SYMLINK"
fi

exit 0
