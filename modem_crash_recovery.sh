#!/bin/bash
###############################################################################
# Modem Crash Recovery - Auto-detect and reset crashed modems
# Works with: SIM7600G-H, Samsung S7, and future modems
# Detects modem type automatically and applies appropriate recovery
###############################################################################

LOG="/var/log/modem_crash_recovery.log"
SYSTEM_EVENTS_LOG="/var/log/smstools/smsd.log"
SMSD_LOG="/var/log/smstools/smsd.log"
LOCKFILE="/var/run/modem_crash_recovery.lock"

# Exit if already running
if [ -f "$LOCKFILE" ]; then
    exit 0
fi
touch "$LOCKFILE"
trap "rm -f $LOCKFILE" EXIT

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

system_event() {
    # Log to system events for sms_watch.sh to display
    local severity="$1"
    local message="$2"
    echo "$(date '+%Y-%m-%d %H:%M:%S'),6, SYSTEM: [$severity] $message" >> "$SYSTEM_EVENTS_LOG"
}

detect_modem_type() {
    # Auto-detect connected modem by USB vendor ID
    local vendor_id=""
    local usb_path=""

    # Check for SIM7600G-H (SimTech, vendor ID: 1e0e)
    for device in /sys/bus/usb/devices/*/idVendor; do
        dir=$(dirname "$device")
        if grep -q "1e0e" "$device" 2>/dev/null; then
            vendor_id="1e0e"
            usb_path=$(basename "$dir")
            echo "SIM7600G-H|$usb_path"
            return 0
        fi
    done

    # Check for EC25 (Quectel, vendor ID: 2c7c)
    for device in /sys/bus/usb/devices/*/idVendor; do
        dir=$(dirname "$device")
        if grep -q "2c7c" "$device" 2>/dev/null; then
            vendor_id="2c7c"
            usb_path=$(basename "$dir")
            echo "EC25|$usb_path"
            return 0
        fi
    done

    # Check for Samsung S7 (Samsung, vendor ID: 04e8)
    for device in /sys/bus/usb/devices/*/idVendor; do
        dir=$(dirname "$device")
        if grep -q "04e8" "$device" 2>/dev/null; then
            vendor_id="04e8"
            usb_path=$(basename "$dir")
            echo "SAMSUNG_S7|$usb_path"
            return 0
        fi
    done

    echo "UNKNOWN|"
    return 1
}

check_modem_crashed() {
    local modem_type="$1"

    # Check 1: I/O errors in recent logs (last 50 lines)
    local io_errors=$(tail -50 "$SMSD_LOG" 2>/dev/null | grep -c "write_to_modem: error 5: Input/output error")

    # Check 2: AT port missing (port depends on modem type)
    local at_port=""
    local at_port_missing=0

    case "$modem_type" in
        SIM7600G-H)
            at_port="/dev/ttyUSB2"
            ;;
        EC25)
            at_port="/dev/ttyUSB3"
            ;;
        SAMSUNG_S7)
            at_port="/dev/ttyUSB2"
            ;;
        *)
            # Default to ttyUSB2 for unknown modems
            at_port="/dev/ttyUSB2"
            ;;
    esac

    if [ ! -c "$at_port" ]; then
        at_port_missing=1
    fi

    # Check 3: Modem handler terminated
    local handler_terminated=$(tail -20 "$SMSD_LOG" 2>/dev/null | grep -c "Modem handler .* terminated")

    # Crash detected if:
    # - 3+ I/O errors AND (AT port missing OR handler terminated)
    if [ "$io_errors" -ge 3 ] && ([ "$at_port_missing" -eq 1 ] || [ "$handler_terminated" -gt 0 ]); then
        log "CRASH DETECTED: I/O errors=$io_errors, AT port ($at_port) missing=$at_port_missing, handler terminated=$handler_terminated"
        return 0
    fi

    return 1
}

reset_modem_usb() {
    local modem_type="$1"
    local usb_path="$2"

    log "=== Starting USB Hardware Reset for $modem_type ==="
    log "USB path: $usb_path"

    # Stop SMSD first
    log "Stopping SMSD..."
    sudo systemctl stop smstools 2>&1 | tee -a "$LOG"
    sleep 2

    # USB Authorization Reset (works for all modems)
    if [ -f "/sys/bus/usb/devices/$usb_path/authorized" ]; then
        log "De-authorizing USB device..."
        if sudo sh -c "echo 0 > /sys/bus/usb/devices/$usb_path/authorized" 2>&1 | tee -a "$LOG"; then
            log "USB device de-authorized"

            sleep 3

            log "Re-authorizing USB device..."
            if sudo sh -c "echo 1 > /sys/bus/usb/devices/$usb_path/authorized" 2>&1 | tee -a "$LOG"; then
                log "USB device re-authorized"

                sleep 5

                # Check if AT port is back (port depends on modem type)
                local at_port=""
                case "$modem_type" in
                    SIM7600G-H)
                        at_port="/dev/ttyUSB2"
                        ;;
                    EC25)
                        at_port="/dev/ttyUSB3"
                        ;;
                    SAMSUNG_S7)
                        at_port="/dev/ttyUSB2"
                        ;;
                    *)
                        at_port="/dev/ttyUSB2"
                        ;;
                esac

                if [ -c "$at_port" ]; then
                    log "SUCCESS: $at_port is back after reset"
                else
                    log "WARNING: $at_port still missing after reset"
                fi
            else
                log "ERROR: Failed to re-authorize USB device"
                return 1
            fi
        else
            log "ERROR: Failed to de-authorize USB device"
            return 1
        fi
    else
        log "ERROR: USB authorization file not found at /sys/bus/usb/devices/$usb_path/authorized"
        return 1
    fi

    # Restart SMSD
    log "Restarting SMSD..."
    sudo systemctl start smstools 2>&1 | tee -a "$LOG"
    sleep 3

    # Verify SMSD is running
    if systemctl is-active --quiet smstools; then
        log "SUCCESS: SMSD restarted successfully"
        return 0
    else
        log "ERROR: SMSD failed to restart"
        return 1
    fi
}

# Main recovery logic
# First detect modem type (needed for crash check)
modem_info=$(detect_modem_type)
modem_type=$(echo "$modem_info" | cut -d'|' -f1)
usb_path=$(echo "$modem_info" | cut -d'|' -f2)

if [ "$modem_type" = "UNKNOWN" ]; then
    # Can't detect modem type, use default check
    modem_type="UNKNOWN"
fi

if ! check_modem_crashed "$modem_type"; then
    # Modem is healthy, exit silently
    exit 0
fi

# Modem crashed - log and recover
log "=========================================="
log "MODEM CRASH DETECTED - Starting Recovery"
log "=========================================="

if [ "$modem_type" = "UNKNOWN" ]; then
    log "ERROR: Could not detect modem type"
    system_event "ERROR" "Modem crashed but type detection failed"
    exit 1
fi

log "Detected modem: $modem_type at USB path: $usb_path"

# Log to system events for sms_watch.sh
system_event "CRITICAL" "Modem crashed ($modem_type) - Hardware reset triggered"

# Perform USB reset
if reset_modem_usb "$modem_type" "$usb_path"; then
    log "=========================================="
    log "RECOVERY SUCCESSFUL"
    log "=========================================="
    system_event "INFO" "Modem hardware reset complete - Service restored ($modem_type)"

    # Send notification to VPS using pi_send_message.sh
    if [ -f /home/rom/pi_send_message.sh ]; then
        /home/rom/pi_send_message.sh "🔄 MODEM AUTO-RECOVERY

Modem Type: $modem_type
Status: Crash detected and recovered
Action: Hardware USB reset performed
USB Path: $usb_path

The modem crashed (I/O error) and was automatically reset via USB authorization. Service has been restored.

System: Jetson Orin Nano (10.100.0.2)
Time: $(date '+%Y-%m-%d %H:%M:%S')" "warning" >> "$LOG" 2>&1
        log "Notification sent to VPS via pi_send_message.sh"
    else
        log "WARNING: pi_send_message.sh not found - notification not sent"
    fi
else
    log "=========================================="
    log "RECOVERY FAILED"
    log "=========================================="
    system_event "CRITICAL" "Modem reset FAILED - Manual intervention required"

    # Send critical notification to VPS
    if [ -f /home/rom/pi_send_message.sh ]; then
        /home/rom/pi_send_message.sh "🚨 MODEM RECOVERY FAILED

Modem Type: $modem_type
Status: Crash detected but recovery FAILED
Action: Hardware USB reset attempted but FAILED
USB Path: $usb_path

⚠️ MANUAL INTERVENTION REQUIRED

The modem crashed and automatic recovery was attempted but failed. The modem may need to be manually reset or the system rebooted.

System: Jetson Orin Nano (10.100.0.2)
Time: $(date '+%Y-%m-%d %H:%M:%S')" "critical" >> "$LOG" 2>&1
        log "Critical notification sent to VPS via pi_send_message.sh"
    else
        log "ERROR: pi_send_message.sh not found - critical notification not sent"
    fi

    exit 1
fi

exit 0
