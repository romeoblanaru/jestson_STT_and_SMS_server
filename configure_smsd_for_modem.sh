#!/bin/bash
###############################################################################
# Auto-configure SMSD for detected modem
# Detects: SIM600/SIM7600 series, Quectel EC25, Samsung phones (USB modem mode)
# Handles: check_memory_method, timing, and device path switching
###############################################################################

LOG="/var/log/smsd_modem_config.log"
SMSD_CONF="/etc/smsd.conf"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
}

# Find Samsung ttyACM device
find_samsung_acm_port() {
    for acm in /dev/ttyACM*; do
        if [ -c "$acm" ]; then
            local vendor=$(udevadm info --name="$acm" 2>/dev/null | grep "ID_VENDOR_ID=" | cut -d= -f2)
            if [ "$vendor" = "04e8" ]; then
                echo "$acm"
                return 0
            fi
        fi
    done
    echo "/dev/ttyACM0"
    return 1
}

detect_modem_vendor() {
    # Detect modem by USB vendor ID
    # Priority order: Samsung (1st) → EC25 (2nd) → SIM7600 (last resort)

    local found_samsung=false
    local found_quectel=false
    local found_simtech=false

    for device in /sys/bus/usb/devices/*/idVendor; do
        dir=$(dirname "$device")
        vendor_id=$(cat "$device" 2>/dev/null)

        case "$vendor_id" in
            04e8)
                # Samsung - verify ttyACM device exists
                samsung_port=$(find_samsung_acm_port)
                if [ -c "$samsung_port" ]; then
                    found_samsung=true
                    samsung_product=$(cat "$dir/idProduct" 2>/dev/null)
                    samsung_serial=$(cat "$dir/serial" 2>/dev/null)
                fi
                ;;
            2c7c)
                # Quectel (EC25, EC20, etc.)
                found_quectel=true
                quectel_product=$(cat "$dir/idProduct" 2>/dev/null)
                ;;
            1e0e)
                # SimTech (SIM600/SIM7600 series)
                found_simtech=true
                simtech_product=$(cat "$dir/idProduct" 2>/dev/null)
                ;;
        esac
    done

    # Return based on priority: Samsung → EC25 → SIM7600
    if [ "$found_samsung" = true ]; then
        log "Detected Samsung phone modem (vendor: 04e8, product: $samsung_product, serial: $samsung_serial, port: $samsung_port) [PRIORITY 1]"
        echo "SAMSUNG"
        return 0
    elif [ "$found_quectel" = true ]; then
        log "Detected Quectel modem (vendor: 2c7c, product: $quectel_product) [PRIORITY 2]"
        echo "QUECTEL"
        return 0
    elif [ "$found_simtech" = true ]; then
        log "Detected SimTech modem (vendor: 1e0e, product: $simtech_product) [PRIORITY 3 - last resort]"
        echo "SIMTECH"
        return 0
    fi

    log "WARNING: Could not detect modem vendor"
    echo "UNKNOWN"
    return 1
}

configure_modem_settings() {
    local modem_vendor="$1"
    local check_method=""
    local sent_sleep=""
    local delay_time=""
    local device_path=""
    local init_cmd=""
    local init2_cmd=""

    case "$modem_vendor" in
        SIMTECH)
            # SIM600/SIM7600 series - use method 5 with longer delays (firmware bugs)
            check_method="5"
            sent_sleep="2"
            delay_time="2"
            # Use symlink if available, otherwise ttyUSB_AT
            if [ -L /dev/ttyUSB_AT ]; then
                device_path="/dev/ttyUSB_AT"
            else
                device_path="/dev/ttyUSB2"
            fi
            init_cmd='AT+CPMS="MT","MT","MT"'
            log "Configuring for SimTech modem:"
            log "  device = $device_path"
            log "  check_memory_method = 5"
            log "  sentsleeptime = 2 (longer delay for firmware stability)"
            log "  delaytime = 2 (longer delay for firmware stability)"
            ;;
        QUECTEL)
            # Quectel EC25/EC20 - use standard method 1 with normal delays
            check_method="1"
            sent_sleep="1"
            delay_time="1"
            if [ -L /dev/ttyUSB_AT ]; then
                device_path="/dev/ttyUSB_AT"
            else
                device_path="/dev/ttyUSB2"
            fi
            init_cmd='AT+CPMS="ME","ME","ME"'
            log "Configuring for Quectel modem:"
            log "  device = $device_path"
            log "  check_memory_method = 1"
            log "  sentsleeptime = 1"
            log "  delaytime = 1"
            ;;
        SAMSUNG)
            # Samsung phone - uses ttyACM, text mode, MT storage (SIM + phone memory)
            check_method="1"
            sent_sleep="2"
            delay_time="2"
            device_path=$(find_samsung_acm_port)
            init_cmd='AT+CPMS="MT","MT","MT"'
            log "Configuring for Samsung phone modem:"
            log "  device = $device_path (CDC ACM)"
            log "  init = $init_cmd (MT = SIM + phone memory)"
            log "  check_memory_method = 1"
            log "  sentsleeptime = 2"
            log "  delaytime = 2"
            ;;
        UNKNOWN)
            # Unknown modem - use safe defaults
            check_method="1"
            sent_sleep="1"
            delay_time="1"
            device_path="/dev/ttyUSB1"
            log "Unknown modem - using safe defaults:"
            log "  device = $device_path"
            log "  check_memory_method = 1"
            log "  sentsleeptime = 1"
            log "  delaytime = 1"
            ;;
    esac

    # Update smsd.conf - settings
    if sudo sed -i "s/^check_memory_method = .*/check_memory_method = $check_method/" "$SMSD_CONF" && \
       sudo sed -i "s/^sentsleeptime = .*/sentsleeptime = $sent_sleep/" "$SMSD_CONF" && \
       sudo sed -i "s/^delaytime = .*/delaytime = $delay_time/" "$SMSD_CONF"; then
        log "SUCCESS: Updated timing settings in $SMSD_CONF"
    else
        log "ERROR: Failed to update timing settings in $SMSD_CONF"
        return 1
    fi

    # Update device path
    if sudo sed -i "s|^device = /dev/tty[A-Za-z0-9_]*|device = $device_path|" "$SMSD_CONF"; then
        log "SUCCESS: Updated device path to $device_path"
    else
        log "ERROR: Failed to update device path"
        return 1
    fi

    # Update init commands if specified
    if [ -n "$init_cmd" ]; then
        sudo sed -i "s|^init = .*|init = $init_cmd|" "$SMSD_CONF"
        log "Updated init command: $init_cmd"
    fi
    if [ -n "$init2_cmd" ]; then
        # Check if init2 exists, add if not
        if grep -q "^init2 = " "$SMSD_CONF"; then
            sudo sed -i "s|^init2 = .*|init2 = $init2_cmd|" "$SMSD_CONF"
        else
            sudo sed -i "/^init = /a init2 = $init2_cmd" "$SMSD_CONF"
        fi
        log "Updated init2 command: $init2_cmd"
    fi

    return 0
}

restart_smsd_if_needed() {
    if pgrep -x smsd > /dev/null; then
        log "SMSD is running - restart required for changes to take effect"
        log "Restarting SMSD..."

        # Use manual stop/start scripts to properly handle the manual stop flag
        if /home/rom/smsd_manual_stop.sh > /dev/null 2>&1; then
            sleep 2

            if /home/rom/smsd_manual_start.sh > /dev/null 2>&1; then
                log "SUCCESS: SMSD restarted"
                sleep 3

                if pgrep -x smsd > /dev/null; then
                    log "SMSD is running with new configuration"
                    return 0
                else
                    log "ERROR: SMSD failed to start after restart"
                    return 1
                fi
            else
                log "ERROR: Failed to start SMSD"
                return 1
            fi
        else
            log "ERROR: Failed to stop SMSD"
            return 1
        fi
    else
        log "SMSD is not running - configuration updated, will apply on next start"
        return 0
    fi
}

# Main configuration logic
log "=========================================="
log "Auto-configuring SMSD for detected modem"
log "=========================================="

# Detect modem
modem_vendor=$(detect_modem_vendor)

if [ "$modem_vendor" = "UNKNOWN" ]; then
    log "WARNING: Modem detection failed - using safe defaults"
fi

# Configure modem-specific settings
if configure_modem_settings "$modem_vendor"; then
    log "Configuration updated successfully"

    # Show current settings
    log "Current SMSD settings:"
    grep -E "check_memory_method|sentsleeptime|delaytime|receive_before_send" "$SMSD_CONF" | grep -v "^#" | tee -a "$LOG"

    # Restart SMSD if running
    restart_smsd_if_needed
else
    log "ERROR: Configuration update failed"
    exit 1
fi

log "=========================================="
log "Configuration complete"
log "=========================================="

exit 0
