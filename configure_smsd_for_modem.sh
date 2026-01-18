#!/bin/bash
###############################################################################
# Auto-configure SMSD check_memory_method based on detected modem
# Detects: SIM600/SIM7600 series vs other modems (Samsung, etc.)
###############################################################################

LOG="/var/log/smsd_modem_config.log"
SMSD_CONF="/etc/smsd.conf"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2
}

detect_modem_vendor() {
    # Detect modem by USB vendor ID
    for device in /sys/bus/usb/devices/*/idVendor; do
        dir=$(dirname "$device")
        vendor_id=$(cat "$device" 2>/dev/null)

        case "$vendor_id" in
            1e0e)
                # SimTech (SIM600/SIM7600 series)
                product_id=$(cat "$dir/idProduct" 2>/dev/null)
                log "Detected SimTech modem (vendor: $vendor_id, product: $product_id)"
                echo "SIMTECH"
                return 0
                ;;
            2c7c)
                # Quectel (EC25, EC20, etc.)
                product_id=$(cat "$dir/idProduct" 2>/dev/null)
                log "Detected Quectel modem (vendor: $vendor_id, product: $product_id)"
                echo "QUECTEL"
                return 0
                ;;
            04e8)
                # Samsung
                log "Detected Samsung modem (vendor: $vendor_id)"
                echo "SAMSUNG"
                return 0
                ;;
            *)
                # Check other ports
                ;;
        esac
    done

    log "WARNING: Could not detect modem vendor"
    echo "UNKNOWN"
    return 1
}

configure_modem_settings() {
    local modem_vendor="$1"
    local check_method=""
    local sent_sleep=""
    local delay_time=""

    case "$modem_vendor" in
        SIMTECH)
            # SIM600/SIM7600 series - use method 5 with longer delays (firmware bugs)
            check_method="5"
            sent_sleep="2"
            delay_time="2"
            log "Configuring for SimTech modem:"
            log "  check_memory_method = 5"
            log "  sentsleeptime = 2 (longer delay for firmware stability)"
            log "  delaytime = 2 (longer delay for firmware stability)"
            ;;
        QUECTEL)
            # Quectel EC25/EC20 - use standard method 1 with normal delays
            check_method="1"
            sent_sleep="1"
            delay_time="1"
            log "Configuring for Quectel modem:"
            log "  check_memory_method = 1"
            log "  sentsleeptime = 1"
            log "  delaytime = 1"
            ;;
        SAMSUNG)
            # Samsung - use standard method 1 with normal delays
            check_method="1"
            sent_sleep="1"
            delay_time="1"
            log "Configuring for Samsung modem:"
            log "  check_memory_method = 1"
            log "  sentsleeptime = 1"
            log "  delaytime = 1"
            ;;
        UNKNOWN)
            # Unknown modem - use safe defaults
            check_method="1"
            sent_sleep="1"
            delay_time="1"
            log "Unknown modem - using safe defaults:"
            log "  check_memory_method = 1"
            log "  sentsleeptime = 1"
            log "  delaytime = 1"
            ;;
    esac

    # Update smsd.conf
    if sudo sed -i "s/^check_memory_method = .*/check_memory_method = $check_method/" "$SMSD_CONF" && \
       sudo sed -i "s/^sentsleeptime = .*/sentsleeptime = $sent_sleep/" "$SMSD_CONF" && \
       sudo sed -i "s/^delaytime = .*/delaytime = $delay_time/" "$SMSD_CONF"; then
        log "SUCCESS: Updated $SMSD_CONF with modem-specific settings"
        return 0
    else
        log "ERROR: Failed to update $SMSD_CONF"
        return 1
    fi
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
