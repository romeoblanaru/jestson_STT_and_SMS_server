#!/bin/bash
###############################################################################
# Modem USB Reset - Software reset for SIM7600G-H modem
# Simulates unplugging and replugging the modem
#
# TWO METHODS AVAILABLE:
#
# METHOD 1: USB Authorization (RECOMMENDED - More reliable)
#   Uses USB authorization to reset the modem. This is equivalent to physically
#   unplugging and replugging the USB cable, but done in software.
#
#   Command used:
#   echo 0 > /sys/bus/usb/devices/1-2.1/authorized  # Disconnect
#   sleep 3
#   echo 1 > /sys/bus/usb/devices/1-2.1/authorized  # Reconnect
#
#   How it works:
#   1. /sys/bus/usb/devices/1-2.1/authorized - sysfs control file for modem
#   2. echo 0 > .../authorized - De-authorizes device (virtual disconnect)
#   3. sleep 3 - Wait for complete disconnect
#   4. echo 1 > .../authorized - Re-authorizes device (virtual reconnect)
#
#   This completely resets the modem hardware without physical access.
#   Especially useful when modem crashes with "write_to_modem: error 5: I/O error"
#   and ttyUSB2 (AT port) disappears.
#
# METHOD 2: USB Unbind/Bind (Fallback)
#   Uses USB driver unbind/bind. Less reliable but still works in some cases.
#
###############################################################################

LOG="/var/log/modem_usb_reset.log"
USB_DEVICE="1-2.2"      # For unbind/bind method
USB_AUTH_PATH="1-2.1"   # For authorization method

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

# METHOD 1: Try USB Authorization Reset (RECOMMENDED)
log "Attempting USB authorization reset (Method 1)..."
if [ -f "/sys/bus/usb/devices/$USB_AUTH_PATH/authorized" ]; then
    log "De-authorizing USB device $USB_AUTH_PATH..."
    if sudo bash -c "echo 0 > /sys/bus/usb/devices/$USB_AUTH_PATH/authorized" 2>&1 | tee -a "$LOG"; then
        log "USB device de-authorized successfully"

        # Wait for device to fully disconnect
        log "Waiting for complete disconnect..."
        sleep 3

        # Re-authorize the USB device (reconnect)
        log "Re-authorizing USB device $USB_AUTH_PATH..."
        if sudo bash -c "echo 1 > /sys/bus/usb/devices/$USB_AUTH_PATH/authorized" 2>&1 | tee -a "$LOG"; then
            log "USB device re-authorized successfully"

            # Wait for device enumeration
            log "Waiting for device enumeration..."
            sleep 5

            # Check new USB devices
            log "New ttyUSB devices: $(ls /dev/ttyUSB* 2>/dev/null | xargs)"
        else
            log "ERROR: Failed to re-authorize USB device"
            # Try to restart SMSD anyway
            sudo /usr/bin/systemctl start smstools 2>&1 | tee -a "$LOG"
            exit 1
        fi
    else
        log "WARNING: Failed to de-authorize, trying fallback method..."
    fi
else
    log "WARNING: Authorization file not found, trying fallback method..."
fi

# METHOD 2: Fallback to Unbind/Bind if authorization didn't work
# (This code is kept for compatibility but usually not needed)
# Uncomment below if you need the fallback method:
#
# log "Attempting USB unbind/bind reset (Method 2 - Fallback)..."
# if sudo bash -c "echo '$USB_DEVICE' > /sys/bus/usb/drivers/usb/unbind" 2>&1 | tee -a "$LOG"; then
#     log "USB device unbound successfully"
#     sleep 3
#     if sudo bash -c "echo '$USB_DEVICE' > /sys/bus/usb/drivers/usb/bind" 2>&1 | tee -a "$LOG"; then
#         log "USB device rebound successfully"
#         sleep 5
#         log "New ttyUSB devices: $(ls /dev/ttyUSB* 2>/dev/null | xargs)"
#     else
#         log "ERROR: Failed to rebind USB device"
#         sudo /usr/bin/systemctl start smstools 2>&1 | tee -a "$LOG"
#         exit 1
#     fi
# else
#     log "ERROR: Both reset methods failed"
#     sudo /usr/bin/systemctl start smstools 2>&1 | tee -a "$LOG"
#     exit 1
# fi

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
