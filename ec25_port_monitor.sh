#!/bin/bash
###############################################################################
# EC25 Port Monitor - Periodic Check and Auto-Fix
# Runs periodically via systemd timer to ensure symlink is always correct
###############################################################################

SYMLINK="/dev/ttyUSB_AT"
LOG="/var/log/ec25_port_monitor.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"
}

# Function to find EC25 AT command port
find_ec25_port() {
    # Check if EC25 modem is present
    if ! lsusb -d 2c7c: > /dev/null 2>&1; then
        return 1
    fi

    # Priority 1: Check ttyUSB2 (preferred for SMS)
    if [ -c "/dev/ttyUSB2" ]; then
        if udevadm info --name=/dev/ttyUSB2 2>/dev/null | grep -q "ID_VENDOR_ID=2c7c"; then
            echo "/dev/ttyUSB2"
            return 0
        fi
    fi

    # Priority 2: Check ttyUSB3 (fallback)
    if [ -c "/dev/ttyUSB3" ]; then
        if udevadm info --name=/dev/ttyUSB3 2>/dev/null | grep -q "ID_VENDOR_ID=2c7c"; then
            echo "/dev/ttyUSB3"
            return 0
        fi
    fi

    # Priority 3: Find any ttyUSB* device from EC25
    for port in /dev/ttyUSB*; do
        if [ -c "$port" ] && udevadm info --name="$port" 2>/dev/null | grep -q "ID_VENDOR_ID=2c7c"; then
            echo "$port"
            return 0
        fi
    done

    return 1
}

# Check if symlink exists and is valid
check_symlink() {
    if [ ! -L "$SYMLINK" ]; then
        # Symlink doesn't exist
        return 1
    fi

    local target=$(readlink -f "$SYMLINK")

    # Check if target device exists
    if [ ! -c "$target" ]; then
        # Target device doesn't exist
        return 1
    fi

    # Check if target is still an EC25 device
    if ! udevadm info --name="$target" 2>/dev/null | grep -q "ID_VENDOR_ID=2c7c"; then
        # Target is not EC25
        return 1
    fi

    # Symlink is valid
    return 0
}

# Main monitoring logic
if ! lsusb -d 2c7c: > /dev/null 2>&1; then
    # EC25 modem not present - nothing to do
    exit 0
fi

# Check if symlink is valid
if check_symlink; then
    # Symlink is valid - nothing to do
    exit 0
fi

# Symlink is invalid or missing - need to fix it
log "Symlink invalid or missing - attempting repair..."

# Find the correct port
EC25_PORT=$(find_ec25_port)

if [ $? -ne 0 ] || [ -z "$EC25_PORT" ]; then
    log "ERROR: Cannot find EC25 AT command port"
    exit 1
fi

log "Detected EC25 AT port: $EC25_PORT"

# Get current symlink target (if exists)
if [ -L "$SYMLINK" ]; then
    CURRENT=$(readlink -f "$SYMLINK")
    if [ "$CURRENT" != "$EC25_PORT" ]; then
        log "Port changed from $CURRENT to $EC25_PORT - updating symlink"
        rm -f "$SYMLINK"
        ln -s "$EC25_PORT" "$SYMLINK"
        PORT_CHANGED=true
    fi
else
    log "Creating symlink: $SYMLINK -> $EC25_PORT"
    rm -f "$SYMLINK"
    ln -s "$EC25_PORT" "$SYMLINK"
    PORT_CHANGED=true
fi

# If port changed, run smart configurator to check IMEI/IMSI
if [ "$PORT_CHANGED" = "true" ]; then
    log "Port changed - running smart configurator..."

    # Run configurator synchronously (it will check IMEI/IMSI and configure if needed)
    if [ -x /home/rom/ec25_smart_configurator.sh ]; then
        /home/rom/ec25_smart_configurator.sh
        CONFIGURATOR_STATUS=$?

        if [ $CONFIGURATOR_STATUS -eq 0 ]; then
            log "Configurator completed successfully"
        else
            log "WARNING: Configurator exited with status $CONFIGURATOR_STATUS"
        fi
    else
        log "WARNING: Configurator not found or not executable"
    fi
fi

# Restart SMSTools if port changed and it's running
if [ "$PORT_CHANGED" = "true" ] && pgrep smsd > /dev/null; then
    log "Port changed - restarting SMSTools..."

    # Use manual stop/start scripts to properly handle the manual stop flag
    /home/rom/smsd_manual_stop.sh > /dev/null 2>&1
    sleep 2
    /home/rom/smsd_manual_start.sh > /dev/null 2>&1

    log "SMSTools restarted on new port"
fi

log "Port monitoring complete: $SYMLINK -> $EC25_PORT"
exit 0
