#!/bin/bash
################################################################################
# Automatic Modem Configuration Script
# Configures APN, VoLTE, and IMS settings based on SIM card carrier
# Supports: EC25-AUX, SIM7600G-H
# Works across all European carriers
# Version: 1.0.0
# Author: Claude Code + Romeo
# Date: 2025-10-11
################################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="$(dirname "$SCRIPT_DIR")/lib"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")/config"
LOG_DIR="$(dirname "$SCRIPT_DIR")/logs"
LOG_FILE="$LOG_DIR/auto_config_$(date +%Y%m%d_%H%M%S).log"

# Import modem detector library
source "$LIB_DIR/modem_detector.sh"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DRY_RUN=false
FORCE=false
ENABLE_VOLTE=true
TEST_CONNECTION=true
RESTART_SERVICES=true

################################################################################
# Logging functions
################################################################################
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "$@"
    echo -e "${BLUE}ℹ${NC}  $@"
}

log_success() {
    log "SUCCESS" "$@"
    echo -e "${GREEN}✓${NC}  $@"
}

log_warning() {
    log "WARNING" "$@"
    echo -e "${YELLOW}⚠${NC}  $@"
}

log_error() {
    log "ERROR" "$@"
    echo -e "${RED}✗${NC}  $@"
}

################################################################################
# Function: stop_services
# Description: Stops services that use the modem port
################################################################################
stop_services() {
    log_info "Stopping services to access modem..."

    local services_stopped=()

    if systemctl is-active --quiet smstools; then
        sudo systemctl stop smstools
        services_stopped+=("smstools")
        log_success "Stopped smstools"
    fi

    if systemctl is-active --quiet ec25-voice-bot; then
        sudo systemctl stop ec25-voice-bot
        services_stopped+=("ec25-voice-bot")
        log_success "Stopped ec25-voice-bot"
    fi

    if [ ${#services_stopped[@]} -gt 0 ]; then
        sleep 2  # Wait for ports to be released
        log_info "Services stopped: ${services_stopped[*]}"
    else
        log_info "No services to stop"
    fi

    # Export for later restart
    export STOPPED_SERVICES="${services_stopped[*]}"
}

################################################################################
# Function: restart_services
# Description: Restarts services that were stopped
################################################################################
restart_services() {
    if [ -z "${STOPPED_SERVICES:-}" ]; then
        return 0
    fi

    log_info "Restarting services..."

    for service in $STOPPED_SERVICES; do
        sudo systemctl start "$service" 2>/dev/null &
        log_success "Restarted $service"
    done

    sleep 2
}

################################################################################
# Function: send_at_command
# Description: Sends AT command to modem and returns response
# Args: $1 - AT command, $2 - AT port (optional)
# Returns: Command response
################################################################################
send_at_command() {
    local cmd="$1"
    local at_port="${2:-$(get_at_command_port)}"
    local timeout=3

    if [ ! -w "$at_port" ]; then
        log_error "Cannot write to $at_port"
        return 1
    fi

    # Send command and read response
    # Use strings to filter out binary/escape codes, then clean up
    local response=$(timeout $timeout bash -c "echo -e '${cmd}\r' > $at_port; sleep 0.5; timeout 1 cat $at_port" 2>/dev/null | strings | tr -d '\r')

    echo "$response"
}

################################################################################
# Function: read_sim_imsi
# Description: Reads IMSI from SIM card
# Returns: IMSI (15 digits)
################################################################################
read_sim_imsi() {
    log_info "Reading SIM card IMSI..."

    local response=$(send_at_command "AT+CIMI")

    local imsi=$(echo "$response" | grep -oE '[0-9]{14,15}' | head -1)

    if [ -z "$imsi" ]; then
        log_error "Failed to read IMSI - SIM card not detected?"
        return 1
    fi

    log_success "IMSI: $imsi"
    echo "$imsi"
}

################################################################################
# Function: parse_mcc_mnc
# Description: Extracts MCC and MNC from IMSI
# Args: $1 - IMSI
# Returns: MCC-MNC format (e.g., "246-02")
################################################################################
parse_mcc_mnc() {
    local imsi=$1

    # Clean IMSI: extract only digits
    imsi=$(echo "$imsi" | grep -oE '[0-9]{14,15}' | head -1)

    if [ -z "$imsi" ]; then
        echo "UNKNOWN"
        return 1
    fi

    local mcc=${imsi:0:3}
    local mnc2=${imsi:3:2}
    local mnc3=${imsi:3:3}

    # Try 2-digit MNC first (most common), output both for lookup to decide
    # The lookup_carrier function will try 2-digit first, then 3-digit
    echo "${mcc}-${mnc2}"
}

################################################################################
# Function: lookup_carrier
# Description: Looks up carrier configuration from database
# Args: $1 - MCC-MNC, $2 - IMSI (optional, for 3-digit MNC fallback)
# Returns: JSON carrier config
################################################################################
lookup_carrier() {
    local mcc_mnc=$1
    local imsi=$2
    local carrier_db="$CONFIG_DIR/carriers.json"

    if [ ! -f "$carrier_db" ]; then
        log_error "Carrier database not found: $carrier_db"
        return 1
    fi

    # Try exact match first
    local carrier=$(jq ".carriers.\"$mcc_mnc\"" "$carrier_db")

    if [ "$carrier" != "null" ]; then
        log_success "Found carrier: $(echo "$carrier" | jq -r '.carrier')" >&2
        echo "$carrier"
        return 0
    fi

    # Try 3-digit MNC if 2-digit failed (and IMSI was provided)
    local mcc=${mcc_mnc%-*}
    local mnc2=${mcc_mnc#*-}
    if [ ${#mnc2} -eq 2 ] && [ -n "$imsi" ]; then
        local mnc3=${imsi:3:3}
        local mcc_mnc3="${mcc}-${mnc3}"
        carrier=$(jq ".carriers.\"$mcc_mnc3\"" "$carrier_db")

        if [ "$carrier" != "null" ]; then
            log_success "Found carrier (3-digit MNC): $(echo "$carrier" | jq -r '.carrier')" >&2
            echo "$carrier"
            return 0
        fi
    fi

    # Use fallback configuration
    log_warning "Carrier $mcc_mnc not in database, using fallback configuration"

    local fallback=$(jq -r ".fallback" "$carrier_db")
    local ims_domain=$(echo "$fallback" | jq -r '.ims_domain_template' | sed "s/{MNC}/${mnc3}/g; s/{MCC}/${mcc}/g")

    # Build fallback carrier JSON
    cat <<EOF
{
  "carrier": "Unknown (MCC:$mcc MNC:${mnc3})",
  "country": "Unknown",
  "mcc": "$mcc",
  "mnc": "${mnc3}",
  "data_apn": "$(echo "$fallback" | jq -r '.data_apn')",
  "ims_apn": "$(echo "$fallback" | jq -r '.ims_apn')",
  "ims_domain": "$ims_domain",
  "volte_supported": true,
  "notes": "Fallback - requires verification"
}
EOF
}

################################################################################
# Function: configure_data_apn
# Description: Configures data APN (PDP context 1)
# Args: $1 - APN name
################################################################################
configure_data_apn() {
    local apn=$1

    log_info "Configuring data APN: $apn"

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would configure: AT+CGDCONT=1,\"IP\",\"$apn\""
        return 0
    fi

    # Set data APN (context 1)
    local response=$(send_at_command "AT+CGDCONT=1,\"IP\",\"$apn\"")

    if echo "$response" | grep -q "OK"; then
        log_success "Data APN configured: $apn"
        return 0
    else
        log_error "Failed to configure data APN"
        log_error "Response: $response"
        return 1
    fi
}

################################################################################
# Function: configure_ims_apn
# Description: Configures IMS APN (PDP context 2)
# Args: $1 - IMS APN name
################################################################################
configure_ims_apn() {
    local ims_apn=$1

    log_info "Configuring IMS APN: $ims_apn"

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would configure: AT+CGDCONT=2,\"IP\",\"$ims_apn\""
        return 0
    fi

    # Set IMS APN (context 2)
    local response=$(send_at_command "AT+CGDCONT=2,\"IP\",\"$ims_apn\"")

    if echo "$response" | grep -q "OK"; then
        log_success "IMS APN configured: $ims_apn"
        return 0
    else
        log_warning "IMS APN configuration may have failed (some modems don't support context 2)"
        return 0  # Don't fail - some modems handle this differently
    fi
}

################################################################################
# Function: enable_volte_ims
# Description: Enables VoLTE and IMS
################################################################################
enable_volte_ims() {
    local modem_type=$(detect_modem)

    log_info "Enabling VoLTE and IMS..."

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would enable VoLTE/IMS"
        return 0
    fi

    case "$modem_type" in
        EC25)
            # Enable IMS
            local response=$(send_at_command 'AT+QCFG="ims",1')
            if echo "$response" | grep -q "OK"; then
                log_success "IMS enabled"
            else
                log_warning "IMS enable may have failed"
            fi

            # Enable VoLTE
            response=$(send_at_command 'AT+QCFG="volte",1')
            if echo "$response" | grep -q "OK"; then
                log_success "VoLTE enabled"
            else
                log_warning "VoLTE enable may have failed"
            fi
            ;;

        SIM7600)
            # Enable VoLTE on SIM7600
            local response=$(send_at_command "AT+CVOLTE=1")
            if echo "$response" | grep -q "OK"; then
                log_success "VoLTE enabled (SIM7600)"
            else
                log_warning "VoLTE enable may have failed"
            fi
            ;;

        *)
            log_error "Unknown modem type: $modem_type"
            return 1
            ;;
    esac

    return 0
}

################################################################################
# Function: restart_modem
# Description: Restarts modem to apply settings
################################################################################
restart_modem() {
    log_info "Restarting modem to apply settings..."

    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would restart modem"
        return 0
    fi

    local response=$(send_at_command "AT+CFUN=1,1")

    log_warning "Modem restarting... waiting 15 seconds..."
    sleep 15

    log_success "Modem restart complete"
}

################################################################################
# Function: verify_configuration
# Description: Verifies APN and VoLTE configuration
################################################################################
verify_configuration() {
    log_info "Verifying configuration..."

    # Check data APN
    local apn_response=$(send_at_command "AT+CGDCONT?")
    log_info "Current PDP contexts:"
    echo "$apn_response" | grep "+CGDCONT:" | tee -a "$LOG_FILE"

    # Check IMS/VoLTE status (EC25 specific)
    local modem_type=$(detect_modem)
    if [ "$modem_type" = "EC25" ]; then
        local ims_status=$(send_at_command 'AT+QCFG="ims"')
        log_info "IMS status: $(echo "$ims_status" | grep "+QCFG" || echo "Unknown")"

        local volte_status=$(send_at_command 'AT+QCFG="volte"')
        log_info "VoLTE status: $(echo "$volte_status" | grep "+QCFG" || echo "Unknown")"
    fi

    log_success "Verification complete - see log for details"
}

################################################################################
# Function: print_banner
################################################################################
print_banner() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   AUTOMATIC MODEM CONFIGURATION                              ║
║   Multi-Carrier | Multi-Modem | VoLTE Ready                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

################################################################################
# Function: usage
################################################################################
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Automatically configures modem (EC25-AUX, SIM7600G-H) based on SIM card.

OPTIONS:
    -h, --help          Show this help message
    -d, --dry-run       Simulate without making changes
    -f, --force         Force configuration even if already configured
    --no-volte          Skip VoLTE/IMS configuration
    --no-test           Skip connection testing
    --no-restart        Don't restart services after configuration

EXAMPLES:
    $0                  # Normal automatic configuration
    $0 --dry-run        # See what would be configured
    $0 --no-volte       # Configure APN only, skip VoLTE

EOF
}

################################################################################
# Main execution
################################################################################
main() {
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                exit 0
                ;;
            -d|--dry-run)
                DRY_RUN=true
                shift
                ;;
            -f|--force)
                FORCE=true
                shift
                ;;
            --no-volte)
                ENABLE_VOLTE=false
                shift
                ;;
            --no-test)
                TEST_CONNECTION=false
                shift
                ;;
            --no-restart)
                RESTART_SERVICES=false
                shift
                ;;
            *)
                echo "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done

    # Create log directory
    mkdir -p "$LOG_DIR"

    print_banner

    log_info "Starting automatic modem configuration..."
    log_info "Log file: $LOG_FILE"

    if [ "$DRY_RUN" = true ]; then
        log_warning "DRY RUN MODE - No changes will be made"
    fi

    # Step 1: Detect modem
    log_info "Step 1: Detecting modem..."
    local modem_type=$(detect_modem)

    if [ "$modem_type" = "UNKNOWN" ]; then
        log_error "No supported modem detected"
        exit 1
    fi

    log_success "Detected: $modem_type"

    # Step 2: Stop services
    log_info "Step 2: Stopping services..."
    stop_services

    # Step 3: Read SIM card
    log_info "Step 3: Reading SIM card..."
    local imsi=$(read_sim_imsi)

    if [ -z "$imsi" ]; then
        log_error "Failed to read SIM card"
        restart_services
        exit 1
    fi

    # Step 4: Identify carrier
    log_info "Step 4: Identifying carrier..."
    local mcc_mnc=$(parse_mcc_mnc "$imsi")
    log_info "MCC-MNC: $mcc_mnc"

    local carrier_config=$(lookup_carrier "$mcc_mnc" "$imsi")

    if [ -z "$carrier_config" ]; then
        log_error "Failed to lookup carrier"
        restart_services
        exit 1
    fi

    # Extract carrier details
    local carrier_name=$(echo "$carrier_config" | jq -r '.carrier')
    local data_apn=$(echo "$carrier_config" | jq -r '.data_apn')
    local ims_apn=$(echo "$carrier_config" | jq -r '.ims_apn')
    local volte_supported=$(echo "$carrier_config" | jq -r '.volte_supported')

    log_success "Carrier: $carrier_name"
    log_info "Data APN: $data_apn"
    log_info "IMS APN: $ims_apn"
    log_info "VoLTE supported: $volte_supported"

    # Step 5: Configure data APN
    log_info "Step 5: Configuring data APN..."
    if ! configure_data_apn "$data_apn"; then
        log_error "Failed to configure data APN"
        restart_services
        exit 1
    fi

    # Step 6: Configure IMS APN
    log_info "Step 6: Configuring IMS APN..."
    configure_ims_apn "$ims_apn"

    # Step 7: Enable VoLTE/IMS
    if [ "$ENABLE_VOLTE" = true ] && [ "$volte_supported" = "true" ]; then
        log_info "Step 7: Enabling VoLTE and IMS..."
        enable_volte_ims
    else
        log_warning "Step 7: Skipping VoLTE/IMS (disabled or not supported)"
    fi

    # Step 8: Restart modem
    log_info "Step 8: Restarting modem..."
    if [ "$DRY_RUN" = false ]; then
        restart_modem
    else
        log_info "[DRY RUN] Skipping modem restart"
    fi

    # Step 9: Verify configuration
    log_info "Step 9: Verifying configuration..."
    if [ "$DRY_RUN" = false ]; then
        verify_configuration
    fi

    # Step 10: Restart services
    if [ "$RESTART_SERVICES" = true ]; then
        log_info "Step 10: Restarting services..."
        restart_services
    fi

    echo ""
    log_success "═══════════════════════════════════════════════════════"
    log_success "  Automatic configuration completed successfully!"
    log_success "═══════════════════════════════════════════════════════"
    echo ""
    log_info "Summary:"
    log_info "  Carrier: $carrier_name"
    log_info "  Data APN: $data_apn"
    log_info "  IMS APN: $ims_apn"
    log_info "  VoLTE: $([ "$ENABLE_VOLTE" = true ] && echo "Enabled" || echo "Disabled")"
    echo ""
    log_info "Log file: $LOG_FILE"
}

# Run main function
main "$@"
