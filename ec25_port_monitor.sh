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

# Send notification to VPS
send_notification() {
    local message="$1"
    local level="$2"
    if [ -x /home/rom/pi_send_message.sh ]; then
        /home/rom/pi_send_message.sh "$message" "$level" 2>&1 >> "$LOG"
    fi
}

# Check if both ttyUSB2 and ttyUSB3 exist (normal) or only one (incomplete enumeration)
check_usb_enumeration() {
    local usb2_exists=false
    local usb3_exists=false

    if [ -c "/dev/ttyUSB2" ] && udevadm info --name=/dev/ttyUSB2 2>/dev/null | grep -q "ID_VENDOR_ID=2c7c"; then
        usb2_exists=true
    fi

    if [ -c "/dev/ttyUSB3" ] && udevadm info --name=/dev/ttyUSB3 2>/dev/null | grep -q "ID_VENDOR_ID=2c7c"; then
        usb3_exists=true
    fi

    if [ "$usb2_exists" = true ] && [ "$usb3_exists" = true ]; then
        echo "BOTH"
        return 0
    elif [ "$usb2_exists" = true ]; then
        echo "USB2_ONLY"
        return 0
    elif [ "$usb3_exists" = true ]; then
        echo "USB3_ONLY"
        return 0
    else
        echo "NONE"
        return 1
    fi
}

# Test AT communication on a port
test_at_communication() {
    local port="$1"
    local temp_response="/tmp/ec25_at_test_$$"

    # Try simple AT command
    (echo -e 'AT\r' > "$port") 2>/dev/null
    sleep 1
    timeout 2 cat "$port" > "$temp_response" 2>/dev/null &
    local cat_pid=$!
    sleep 2
    kill $cat_pid 2>/dev/null

    if grep -q "OK" "$temp_response" 2>/dev/null; then
        rm -f "$temp_response"
        return 0
    else
        rm -f "$temp_response"
        return 1
    fi
}

# Perform USB hard reset using authorization method
usb_hard_reset() {
    log "⚠️ Performing USB hard reset (authorization method)..."

    # Find USB device path for EC25
    local usb_device_path=""
    for port in /dev/ttyUSB*; do
        if [ -c "$port" ] && udevadm info --name="$port" 2>/dev/null | grep -q "ID_VENDOR_ID=2c7c"; then
            usb_device_path=$(udevadm info --name="$port" 2>/dev/null | grep "DEVPATH=" | grep -oP 'usb\d+/\d+-\d+' | head -1)
            break
        fi
    done

    if [ -z "$usb_device_path" ]; then
        log "ERROR: Cannot find USB device path for EC25"
        return 1
    fi

    local usb_sys_path="/sys/bus/usb/devices/$usb_device_path"

    if [ ! -f "$usb_sys_path/authorized" ]; then
        log "ERROR: USB authorization file not found: $usb_sys_path/authorized"
        return 1
    fi

    log "USB device path: $usb_device_path"

    # Deauthorize (disconnect)
    echo 0 | sudo tee "$usb_sys_path/authorized" > /dev/null 2>&1
    log "USB device deauthorized (disconnected)"
    sleep 3

    # Re-authorize (reconnect)
    echo 1 | sudo tee "$usb_sys_path/authorized" > /dev/null 2>&1
    log "USB device re-authorized (reconnected)"
    sleep 5

    log "USB hard reset completed - waiting for re-enumeration..."
    return 0
}

# Main monitoring logic
if ! lsusb -d 2c7c: > /dev/null 2>&1; then
    # EC25 modem not present - nothing to do
    exit 0
fi

# Check if symlink is valid
if check_symlink; then
    # Symlink is valid but check for optimization opportunities
    CURRENT_TARGET=$(readlink -f "$SYMLINK")
    ENUM_STATUS=$(check_usb_enumeration)

    # CASE 1: Using fallback ttyUSB3 but preferred ttyUSB2 is now available - switch to it
    if [ "$CURRENT_TARGET" = "/dev/ttyUSB3" ] && [ "$ENUM_STATUS" = "BOTH" ]; then
        log "✅ Preferred port ttyUSB2 is now available - switching from fallback ttyUSB3"
        # Don't exit - let the script continue to repair logic to update symlink
    # CASE 2: Using fallback ttyUSB3 and ttyUSB2 is missing - incomplete enumeration
    elif [ "$CURRENT_TARGET" = "/dev/ttyUSB3" ] && [ "$ENUM_STATUS" != "BOTH" ]; then
        log "⚠️ Symlink valid but incomplete USB enumeration detected"
        log "Using fallback port ttyUSB3 but ttyUSB2 is missing ($ENUM_STATUS)"
        log "This may cause SMSD crashes - attempting USB hard reset..."

        send_notification "⚠️ EC25 Incomplete Enumeration: Using fallback port - attempting USB reset" "warning"

        if usb_hard_reset; then
            sleep 8
            ENUM_STATUS_AFTER=$(check_usb_enumeration)
            log "USB enumeration after reset: $ENUM_STATUS_AFTER"

            if [ "$ENUM_STATUS_AFTER" = "BOTH" ]; then
                log "✅ USB reset successful - both ports now present"
                send_notification "✅ EC25 USB Reset Successful: All ports restored - will update symlink on next run" "info"
                # Don't exit - let script continue to update symlink to preferred port
            else
                log "⚠️ USB reset completed but enumeration still incomplete: $ENUM_STATUS_AFTER"
                send_notification "⚠️ EC25 USB Reset Partial: Enumeration still incomplete - may need physical replug" "warning"
                exit 0
            fi
        else
            exit 0
        fi
    else
        # Symlink is valid and optimal - nothing to do
        exit 0
    fi
fi

# Symlink is invalid or missing - need to fix it
log "Symlink invalid or missing - attempting repair..."

# Check USB enumeration status
ENUM_STATUS=$(check_usb_enumeration)
log "USB enumeration status: $ENUM_STATUS"

# Find the correct port
EC25_PORT=$(find_ec25_port)

if [ $? -ne 0 ] || [ -z "$EC25_PORT" ]; then
    log "ERROR: Cannot find EC25 AT command port"
    exit 1
fi

log "Detected EC25 AT port: $EC25_PORT"

# Get current symlink target (if exists)
CURRENT=""
if [ -L "$SYMLINK" ]; then
    CURRENT=$(readlink -f "$SYMLINK")
fi

# Determine if this is a port change
if [ -n "$CURRENT" ] && [ "$CURRENT" != "$EC25_PORT" ]; then
    PORT_CHANGED=true
    log "Port changed from $CURRENT to $EC25_PORT"
elif [ -z "$CURRENT" ]; then
    PORT_CHANGED=true
    log "Creating new symlink"
else
    PORT_CHANGED=false
fi

# Handle based on scenario
if [ "$PORT_CHANGED" = "true" ]; then
    if [ "$ENUM_STATUS" = "BOTH" ]; then
        # SCENARIO A: Normal port shift (both ports exist)
        log "✅ SCENARIO A: Normal port shift detected (both ttyUSB2 and ttyUSB3 present)"
        rm -f "$SYMLINK"
        ln -s "$EC25_PORT" "$SYMLINK"
        send_notification "📡 EC25 Port Shift: $CURRENT → $EC25_PORT (Normal operation)" "info"
    else
        # SCENARIO B: Incomplete USB enumeration (only one port exists)
        log "⚠️ SCENARIO B: Incomplete USB enumeration detected!"
        log "Only $ENUM_STATUS available - this may indicate USB power issue"

        # Test AT communication on the available port
        log "Testing AT communication on $EC25_PORT..."
        if test_at_communication "$EC25_PORT"; then
            log "✅ AT communication successful on $EC25_PORT"
            rm -f "$SYMLINK"
            ln -s "$EC25_PORT" "$SYMLINK"
            send_notification "⚠️ EC25 Incomplete Enumeration: Using $EC25_PORT (AT test passed)" "warning"
        else
            log "❌ AT communication failed on $EC25_PORT - performing USB hard reset"
            send_notification "🔄 EC25 USB Hard Reset: Incomplete enumeration - AT communication failed" "warning"

            # Perform USB hard reset
            if usb_hard_reset; then
                # Wait for re-enumeration
                sleep 8

                # Re-check enumeration
                ENUM_STATUS_AFTER=$(check_usb_enumeration)
                log "USB enumeration after reset: $ENUM_STATUS_AFTER"

                # Find port again
                EC25_PORT=$(find_ec25_port)
                if [ $? -eq 0 ] && [ -n "$EC25_PORT" ]; then
                    log "✅ Port found after reset: $EC25_PORT"
                    rm -f "$SYMLINK"
                    ln -s "$EC25_PORT" "$SYMLINK"

                    if [ "$ENUM_STATUS_AFTER" = "BOTH" ]; then
                        send_notification "✅ EC25 USB Reset Successful: All ports restored ($ENUM_STATUS_AFTER)" "info"
                    else
                        send_notification "⚠️ EC25 USB Reset Partial: Port found but enumeration still incomplete ($ENUM_STATUS_AFTER)" "warning"
                    fi
                else
                    log "❌ ERROR: Cannot find EC25 port after USB reset"
                    send_notification "🔴 EC25 USB Reset Failed: Manual intervention required - modem may need physical replug" "error"
                    exit 1
                fi
            else
                log "❌ USB hard reset failed"
                send_notification "🔴 EC25 USB Reset Failed: Hard reset error - manual intervention required" "error"
                exit 1
            fi
        fi
    fi
else
    # No port change, just update symlink if needed
    if [ ! -L "$SYMLINK" ]; then
        rm -f "$SYMLINK"
        ln -s "$EC25_PORT" "$SYMLINK"
    fi
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
