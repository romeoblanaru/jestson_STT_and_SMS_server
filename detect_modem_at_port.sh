#!/bin/bash
###############################################################################
# Modem AT Port Detector
# Automatically detects the correct AT command port (Interface 02)
# Creates stable symlink: /dev/ttyUSB_SIM7600_AT
###############################################################################

LOG="/var/log/modem_port_detector.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "=== Modem AT Port Detection Started ==="

# Find the port with Interface 02 (SMS/AT config port)
AT_PORT=""
for port in /dev/ttyUSB*; do
    if [ ! -c "$port" ]; then
        continue
    fi

    # Get interface number
    INTERFACE=$(udevadm info -a "$port" 2>/dev/null | grep -m1 'ATTRS{bInterfaceNumber}' | grep -o '"[^"]*"' | tr -d '"')

    if [ "$INTERFACE" = "02" ]; then
        AT_PORT="$port"
        log "Found Interface 02 (AT/SMS port): $port"
        break
    fi
done

if [ -z "$AT_PORT" ]; then
    log "ERROR: Could not find Interface 02 port"
    exit 1
fi

# Create stable symlink
SYMLINK="/dev/ttyUSB_SIM7600_AT"
log "Creating symlink: $SYMLINK -> $AT_PORT"

# Remove old symlink if exists
if [ -L "$SYMLINK" ]; then
    sudo rm -f "$SYMLINK"
fi

# Create new symlink
if sudo ln -sf "$AT_PORT" "$SYMLINK"; then
    log "Symlink created successfully"
else
    log "ERROR: Failed to create symlink"
    exit 1
fi

# Verify symlink
if [ -L "$SYMLINK" ]; then
    REAL_PATH=$(readlink -f "$SYMLINK")
    log "Verification: $SYMLINK -> $REAL_PATH"

    # Test AT communication
    if timeout 2 bash -c "echo -e 'AT\r' > $SYMLINK; sleep 0.5; timeout 1 cat $SYMLINK" 2>/dev/null | grep -q "OK"; then
        log "SUCCESS: AT commands working on $AT_PORT (Interface 02)"
    else
        log "WARNING: AT command test failed on $AT_PORT"
    fi
else
    log "ERROR: Symlink verification failed"
    exit 1
fi

# Update modem_status_collector.sh if needed
COLLECTOR_SCRIPT="/home/rom/modem_status_collector.sh"
if [ -f "$COLLECTOR_SCRIPT" ]; then
    CURRENT_PORT=$(grep '^AT_PORT=' "$COLLECTOR_SCRIPT" | cut -d'"' -f2)
    if [ "$CURRENT_PORT" != "$SYMLINK" ]; then
        log "Updating collector script: $CURRENT_PORT -> $SYMLINK"
        # This will be done separately with proper edit
    else
        log "Collector script already using correct port"
    fi
fi

log "=== Detection Complete ==="
exit 0
