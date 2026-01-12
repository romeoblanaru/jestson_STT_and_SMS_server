#!/bin/bash
###############################################################################
# Modem USB Reset - Software reset via USB unbind/bind
# Simulates unplugging and replugging the modem
###############################################################################

LOG="/var/log/modem_usb_reset.log"
USB_DEVICE="1-2.2"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

log "=== Starting Modem USB Reset ==="

# Stop SMSD to release the serial ports
log "Stopping SMSD..."
if sudo /usr/bin/systemctl stop smstools 2>&1 | tee -a "$LOG"; then
    log "SMSD stopped successfully"
else
    log "WARNING: SMSD stop command failed, continuing anyway..."
fi
sleep 2

# Check current USB devices
log "Current ttyUSB devices: $(ls /dev/ttyUSB* 2>/dev/null | xargs)"

# Unbind the USB device (disconnect)
log "Unbinding USB device $USB_DEVICE..."
if sudo bash -c "echo '$USB_DEVICE' > /sys/bus/usb/drivers/usb/unbind" 2>&1 | tee -a "$LOG"; then
    log "USB device unbound successfully"
else
    log "ERROR: Failed to unbind USB device"
    # Try to restart SMSD anyway
    sudo /usr/bin/systemctl start smstools 2>&1 | tee -a "$LOG"
    exit 1
fi

# Wait for device to fully disconnect
sleep 3

# Bind the USB device back (reconnect)
log "Rebinding USB device $USB_DEVICE..."
if sudo bash -c "echo '$USB_DEVICE' > /sys/bus/usb/drivers/usb/bind" 2>&1 | tee -a "$LOG"; then
    log "USB device rebound successfully"
else
    log "ERROR: Failed to rebind USB device"
    exit 1
fi

# Wait for device enumeration
log "Waiting for device enumeration..."
sleep 5

# Check new USB devices
log "New ttyUSB devices: $(ls /dev/ttyUSB* 2>/dev/null | xargs)"

# Restart SMSD
log "Starting SMSD..."
if sudo /usr/bin/systemctl start smstools 2>&1 | tee -a "$LOG"; then
    log "SMSD started successfully"
else
    log "ERROR: Failed to start SMSD"
    exit 1
fi

# Wait for SMSD to initialize
sleep 3

# Check SMSD status
if systemctl is-active --quiet smstools; then
    log "SUCCESS: Modem reset complete, SMSD is running"
    log "=== Modem USB Reset Complete ==="
    exit 0
else
    log "WARNING: SMSD is not running after reset"
    log "=== Modem USB Reset Complete (with warnings) ==="
    exit 1
fi
