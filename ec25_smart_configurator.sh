#!/bin/bash
###############################################################################
# EC25 Smart Auto-Configurator
# Called by port monitor when port changes (runs synchronously)
# - New modem (IMEI change) → USB composition + full config
# - New SIM (IMSI change) → Operator detection + APN/VoLTE config
# - No changes → Skip (exit fast)
#
# IMPORTANT: Uses /dev/ttyUSB_AT symlink (created by port monitor)
###############################################################################

# Configuration
STATE_DIR="/var/lib/ec25"
STATE_FILE="$STATE_DIR/modem.json"
LOG_FILE="/var/log/ec25_configurator.log"
SMSD_CONF="/etc/smsd.conf"
AT_PORT="/dev/ttyUSB_AT"  # Use symlink from port monitor

# Flags
NEEDS_MODEM_RESET=false  # Set to true if modem needs soft reset

# Timeouts
MODEM_TIMEOUT=30  # seconds to wait for modem to respond

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log_silent() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

error_exit() {
    log "ERROR: $*"
    exit 1
}

# Ensure state directory exists
mkdir -p "$STATE_DIR"

log "=========================================="
log "EC25 Smart Configurator Started"
log "=========================================="

# Function to send AT command with retries
send_at_command() {
    local port="$1"
    local command="$2"
    local timeout="${3:-2}"
    local retries="${4:-3}"

    for i in $(seq 1 $retries); do
        response=$(timeout $timeout sh -c "echo -e '${command}\r' > $port && cat < $port" 2>/dev/null | tr -d '\r' | grep -v "^$" | head -5)

        if echo "$response" | grep -q "OK"; then
            echo "$response"
            return 0
        fi

        sleep 1
    done

    return 1
}

# Function to get IMEI from modem
get_modem_imei() {
    local port="$1"
    log_silent "Querying modem IMEI..."

    response=$(send_at_command "$port" "AT+GSN" 3 5)

    if [ $? -eq 0 ]; then
        imei=$(echo "$response" | grep -oP '\d{15}' | head -1)
        if [ -n "$imei" ]; then
            echo "$imei"
            return 0
        fi
    fi

    return 1
}

# Function to get IMSI from SIM
get_sim_imsi() {
    local port="$1"
    log_silent "Querying SIM IMSI..."

    response=$(send_at_command "$port" "AT+CIMI" 3 5)

    if [ $? -eq 0 ]; then
        imsi=$(echo "$response" | grep -oP '\d{15}' | head -1)
        if [ -n "$imsi" ]; then
            echo "$imsi"
            return 0
        fi
    fi

    return 1
}

# Function to detect operator from IMSI
detect_operator_from_imsi() {
    local imsi="$1"
    local mcc_mnc="${imsi:0:5}"

    # MCC+MNC to operator mapping (expandable)
    case "$mcc_mnc" in
        24603) echo "Telia Lithuania" ;;
        24601) echo "Omnitel Lithuania" ;;
        24602) echo "Bite Lithuania" ;;
        24001) echo "Telia Sweden" ;;
        24008) echo "Telenor Sweden" ;;
        24007) echo "Tele2 Sweden" ;;
        22601) echo "Vodafone Romania" ;;
        22603) echo "Telekom Romania" ;;
        22610) echo "Orange Romania" ;;
        *)     echo "Unknown (MCC+MNC: $mcc_mnc)" ;;
    esac
}

# Function to get APN for operator
get_apn_for_operator() {
    local imsi="$1"
    local mcc_mnc="${imsi:0:5}"

    # Operator APN mapping
    case "$mcc_mnc" in
        24603) echo "internet.telia.lt" ;;
        24601) echo "omnitel" ;;
        24602) echo "mobile.bite.lt" ;;
        24001) echo "online.telia.se" ;;
        24008) echo "internet.telenor.se" ;;
        24007) echo "internet.tele2.se" ;;
        22601) echo "internet.vodafone.ro" ;;
        22603) echo "internet.telekom.ro" ;;
        22610) echo "internet" ;;  # Orange Romania
        *)     echo "internet" ;;  # Generic fallback
    esac
}

# Function to configure USB composition for EC25
configure_usb_composition() {
    local port="$1"
    log "Configuring USB composition for EC25..."

    # EC25 USB composition modes (AT+QCFG="usbnet"):
    # Mode 0 = QMI/RMNET (default)
    # Mode 1 = ECM (CDC Ethernet) - CORRECT for USB PID 0125
    # Mode 2 = MBIM (Mobile Broadband Interface)
    # Mode 3 = RNDIS (Windows network mode, changes PID to 0306)
    #
    # For EC25 with USB PID 0125, use Mode 1 (ECM) for CDC Ethernet
    # This enables SMS + CDC Ethernet for LTE backup

    log "Querying current USB composition..."

    # Query current composition
    current=$(send_at_command "$port" "AT+QCFG=\"usbnet\"" 2)
    log "Current USB config: $current"

    # Set to mode 1 (ECM/CDC Ethernet) if not already
    if ! echo "$current" | grep -q "\"usbnet\",1"; then
        log "Switching to ECM mode (usbnet=1) with persistent save..."

        if send_at_command "$port" "AT+QCFG=\"usbnet\",1,1" 3; then
            log "✅ USB composition changed to mode 1 (ECM/CDC Ethernet) - SAVED TO NV MEMORY"
            log "Modem reset will be triggered at end of configuration"
            NEEDS_MODEM_RESET=true
            return 0
        else
            log "ERROR: Failed to change USB composition"
            return 1
        fi
    else
        log "✅ USB composition already correct (mode 1 - ECM/CDC Ethernet)"
        return 0
    fi
}

# Function to configure VoLTE and network settings
configure_network_settings() {
    local port="$1"
    local apn="$2"
    local operator="$3"

    log "Configuring network for operator: $operator"
    log "APN: $apn"

    # Configure APN
    log "Setting APN..."
    send_at_command "$port" "AT+CGDCONT=1,\"IP\",\"$apn\"" 3

    # Enable VoLTE if supported by operator
    case "$operator" in
        *"Telia"*|*"Vodafone"*|*"Orange"*)
            log "Enabling VoLTE for $operator..."
            send_at_command "$port" "AT+QCFG=\"ims\",1" 3
            send_at_command "$port" "AT+QCFG=\"volte/enable\",1" 3
            ;;
        *)
            log "VoLTE configuration skipped for $operator"
            ;;
    esac

    # Set network mode to auto (2G/3G/4G)
    log "Setting network mode to auto..."
    send_at_command "$port" "AT+QCFG=\"nwscanmode\",0,1" 3

    log "Network configuration complete"
}

# Function to save state
save_state() {
    local imei="$1"
    local imsi="$2"
    local operator="$3"

    cat > "$STATE_FILE" <<EOF
{
  "imei": "$imei",
  "imsi": "$imsi",
  "operator": "$operator",
  "last_configured": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF
    log "State saved to $STATE_FILE"
}

# Function to load previous state
load_state() {
    if [ ! -f "$STATE_FILE" ]; then
        echo "{}"
        return 1
    fi
    cat "$STATE_FILE"
    return 0
}

# Function to extract JSON value (simple jq-free parser)
get_json_value() {
    local json="$1"
    local key="$2"
    echo "$json" | grep -oP "\"$key\":\s*\"\K[^\"]*"
}

#############################################################################
# MAIN LOGIC
#############################################################################

log "=========================================="
log "Smart Configurator Started"
log "=========================================="

# Verify symlink exists (should be created by port monitor)
if [ ! -L "$AT_PORT" ]; then
    log "ERROR: $AT_PORT symlink not found (should be created by port monitor)"
    exit 1
fi

# Verify target exists
if [ ! -c "$AT_PORT" ]; then
    log "ERROR: $AT_PORT points to non-existent device"
    exit 1
fi

log "Using AT port: $AT_PORT -> $(readlink -f $AT_PORT)"

# Wait a bit for modem to be ready for AT commands
sleep 2

# Get current IMEI (with error handling)
CURRENT_IMEI=$(get_modem_imei "$AT_PORT")

if [ -z "$CURRENT_IMEI" ]; then
    log "WARNING: Failed to read IMEI from modem (may not be ready yet)"
    log "Port monitor will retry on next cycle"
    exit 0  # Exit gracefully, not an error
fi

log "Modem IMEI: $CURRENT_IMEI"

# Load previous state
PREV_STATE=$(load_state)
PREV_IMEI=$(get_json_value "$PREV_STATE" "imei")

# Check if this is a new modem
MODEM_CHANGED=false

if [ -z "$PREV_IMEI" ]; then
    log "First time configuration (no previous IMEI found)"
    MODEM_CHANGED=true
elif [ "$PREV_IMEI" != "$CURRENT_IMEI" ]; then
    log "NEW MODEM DETECTED!"
    log "Previous IMEI: $PREV_IMEI"
    log "Current IMEI:  $CURRENT_IMEI"
    MODEM_CHANGED=true
else
    log "Same modem detected (IMEI matches)"
fi

# Configure USB composition if modem changed
if [ "$MODEM_CHANGED" = "true" ]; then
    configure_usb_composition "$AT_PORT"
    # Note: Modem reset will be triggered at the end, not here
fi

# Get current IMSI
CURRENT_IMSI=$(get_sim_imsi "$AT_PORT")

if [ -z "$CURRENT_IMSI" ]; then
    log "WARNING: Failed to read IMSI - SIM card may not be ready"
    log "Saving IMEI only, will configure network on next run"
    save_state "$CURRENT_IMEI" "" "Unknown"
    exit 0
fi

log "SIM IMSI: $CURRENT_IMSI"

# Detect operator
OPERATOR=$(detect_operator_from_imsi "$CURRENT_IMSI")
log "Detected operator: $OPERATOR"

# Check if SIM changed
PREV_IMSI=$(get_json_value "$PREV_STATE" "imsi")
SIM_CHANGED=false

if [ -z "$PREV_IMSI" ]; then
    log "First time SIM configuration"
    SIM_CHANGED=true
elif [ "$PREV_IMSI" != "$CURRENT_IMSI" ]; then
    log "NEW SIM CARD DETECTED!"
    log "Previous IMSI: $PREV_IMSI"
    log "Current IMSI:  $CURRENT_IMSI"
    SIM_CHANGED=true
else
    log "Same SIM card detected (IMSI matches)"
fi

# Configure network if SIM changed or modem changed
if [ "$SIM_CHANGED" = "true" ] || [ "$MODEM_CHANGED" = "true" ]; then
    APN=$(get_apn_for_operator "$CURRENT_IMSI")
    configure_network_settings "$AT_PORT" "$APN" "$OPERATOR"

    # Run modem-specific SMSD configuration
    log "Configuring SMSTools for EC25..."
    /home/rom/configure_smsd_for_modem.sh
fi

# Save new state
save_state "$CURRENT_IMEI" "$CURRENT_IMSI" "$OPERATOR"

log "=========================================="
if [ "$MODEM_CHANGED" = "true" ] || [ "$SIM_CHANGED" = "true" ]; then
    log "Configuration completed successfully"
else
    log "No changes detected - configuration skipped"
fi
log "=========================================="

# Trigger modem soft reset if needed (at the very end!)
if [ "$NEEDS_MODEM_RESET" = "true" ]; then
    log "Triggering modem soft reset (AT+CFUN=1,1)..."
    log "Modem will reinitialize with new USB composition"

    if send_at_command "$AT_PORT" "AT+CFUN=1,1" 3; then
        log "✅ Soft reset command sent successfully"
        log "Modem will reset now - port monitor will handle restart"
    else
        log "WARNING: Failed to send soft reset command"
    fi

    # Exit - modem will reset and port monitor will detect it
    log "Configurator exiting - modem resetting..."
    exit 0
fi

# Normal exit (no reset needed)
log "Configurator completed - no modem reset needed"
exit 0
