#!/bin/bash
###############################################################################
# Modem Connection Handler
# Triggered by udev when SIM7600 modem is connected/reconnected
# Detects correct AT port and sends notification
###############################################################################

LOG="/var/log/modem_port_detector.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG" 2>&1; }

log "=== Modem USB Connection Detected ==="

# Wait for all USB enumeration to complete
sleep 3

# Remove old symlinks to force recreation
rm -f /dev/ttyUSB_SIM7600_AT 2>/dev/null
rm -f /dev/ttyUSB_SIM7600_DIAG 2>/dev/null
rm -f /dev/ttyUSB_SIM7600_VOICE 2>/dev/null
rm -f /dev/ttyUSB_SIM7600_AUDIO 2>/dev/null

log "Recreating symlinks based on Interface Numbers..."

# Find and create symlinks for all interfaces
AT_PORT=""
for port in /dev/ttyUSB*; do
    [ -c "$port" ] || continue
    INTERFACE=$(udevadm info -a "$port" 2>/dev/null | grep -m1 'ATTRS{bInterfaceNumber}' | grep -o '"[^"]*"' | tr -d '"')

    case "$INTERFACE" in
        "00")
            ln -sf "$port" /dev/ttyUSB_SIM7600_DIAG
            log "Interface 00 (Diagnostics) -> $port"
            ;;
        "02")
            ln -sf "$port" /dev/ttyUSB_SIM7600_AT
            AT_PORT="$port"
            log "Interface 02 (AT/SMS) -> $port"
            ;;
        "03")
            ln -sf "$port" /dev/ttyUSB_SIM7600_VOICE
            log "Interface 03 (Voice) -> $port"
            ;;
        "04")
            ln -sf "$port" /dev/ttyUSB_SIM7600_AUDIO
            log "Interface 04 (Audio) -> $port"
            ;;
    esac
done

if [ -z "$AT_PORT" ]; then
    log "ERROR: Could not detect Interface 02"
    exit 1
fi

# Set permissions on symlinks
chmod 666 /dev/ttyUSB_SIM7600_* 2>/dev/null

log "All symlinks created successfully"

# List all USB ports
USB_PORTS=$(ls /dev/ttyUSB* 2>/dev/null | xargs)
log "All USB ports: $USB_PORTS"

# Create interface mapping
MAPPING=""
for port in /dev/ttyUSB*; do
    [ -c "$port" ] || continue
    INTERFACE=$(udevadm info -a "$port" 2>/dev/null | grep -m1 'ATTRS{bInterfaceNumber}' | grep -o '"[^"]*"' | tr -d '"')
    MAPPING="$MAPPING\n$(basename $port) -> Interface $INTERFACE"
done

# Send notification to VPS
NOTIFICATION="📡 SIM7600 Modem Connected

AT Port (Interface 02): $AT_PORT
Symlink: /dev/ttyUSB_SIM7600_AT

USB Port Mapping:$MAPPING

All Ports: $USB_PORTS

System: Jetson Orin Nano (10.100.0.2)
Time: $(date '+%Y-%m-%d %H:%M:%S')"

if [ -f /home/rom/pi_send_message.sh ]; then
    /home/rom/pi_send_message.sh "$NOTIFICATION" info >> "$LOG" 2>&1
    log "Notification sent to VPS"
else
    log "WARNING: pi_send_message.sh not found"
fi

log "=== Modem Connection Handler Complete ==="
exit 0
