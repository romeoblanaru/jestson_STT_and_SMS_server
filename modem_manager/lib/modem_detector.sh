#!/bin/bash
################################################################################
# Modem Detector Library
# Detects and identifies LTE modems (EC25-AUX, SIM7600G-H)
# Version: 1.0.0
# Author: Claude Code + Romeo
# Date: 2025-10-11
################################################################################

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Modem database - USB VID/PID and characteristics
declare -A MODEM_EC25=(
    [name]="Quectel EC25-AUX"
    [vendor_id]="2c7c"
    [product_id]="0125"
    [manufacturer]="Quectel"
    [type]="LTE"
    [has_usb_audio]=true
    [audio_device]="hw:EC25AUX"
    [has_3g_fallback]=true
    [volte_capable]=true
    [typical_ports]="ttyUSB0,ttyUSB1"
    [at_port_interface]="01"
    [notes]="USB Audio Class, 2G/3G/4G support"
)

declare -A MODEM_SIM7600=(
    [name]="SIMCom SIM7600G-H"
    [vendor_id]="1e0e"
    [product_id]="9011"
    [manufacturer]="SIMCom"
    [type]="LTE"
    [has_usb_audio]=false
    [audio_device]="none"
    [has_3g_fallback]=false
    [volte_capable]=true
    [typical_ports]="ttyUSB0,ttyUSB1,ttyUSB2"
    [at_port_interface]="02"
    [notes]="4G only, no 3G/2G, requires external audio"
)

################################################################################
# Function: detect_modem
# Description: Detects connected LTE modem
# Returns: Modem type (EC25, SIM7600, UNKNOWN) via echo
################################################################################
detect_modem() {
    local usb_devices=$(lsusb)

    # Check for EC25-AUX
    if echo "$usb_devices" | grep -q "2c7c:0125"; then
        echo "EC25"
        return 0
    fi

    # Check for SIM7600G-H
    if echo "$usb_devices" | grep -q "1e0e:9011"; then
        echo "SIM7600"
        return 0
    fi

    # No supported modem found
    echo "UNKNOWN"
    return 1
}

################################################################################
# Function: get_modem_info
# Description: Returns detailed modem information
# Args: $1 - modem_type (EC25, SIM7600)
# Returns: JSON-formatted modem info
################################################################################
get_modem_info() {
    local modem_type=$1

    case "$modem_type" in
        EC25)
            cat <<EOF
{
  "name": "${MODEM_EC25[name]}",
  "vendor_id": "${MODEM_EC25[vendor_id]}",
  "product_id": "${MODEM_EC25[product_id]}",
  "manufacturer": "${MODEM_EC25[manufacturer]}",
  "type": "${MODEM_EC25[type]}",
  "has_usb_audio": ${MODEM_EC25[has_usb_audio]},
  "audio_device": "${MODEM_EC25[audio_device]}",
  "has_3g_fallback": ${MODEM_EC25[has_3g_fallback]},
  "volte_capable": ${MODEM_EC25[volte_capable]},
  "typical_ports": "${MODEM_EC25[typical_ports]}",
  "at_port_interface": "${MODEM_EC25[at_port_interface]}",
  "notes": "${MODEM_EC25[notes]}"
}
EOF
            ;;
        SIM7600)
            cat <<EOF
{
  "name": "${MODEM_SIM7600[name]}",
  "vendor_id": "${MODEM_SIM7600[vendor_id]}",
  "product_id": "${MODEM_SIM7600[product_id]}",
  "manufacturer": "${MODEM_SIM7600[manufacturer]}",
  "type": "${MODEM_SIM7600[type]}",
  "has_usb_audio": ${MODEM_SIM7600[has_usb_audio]},
  "audio_device": "${MODEM_SIM7600[audio_device]}",
  "has_3g_fallback": ${MODEM_SIM7600[has_3g_fallback]},
  "volte_capable": ${MODEM_SIM7600[volte_capable]},
  "typical_ports": "${MODEM_SIM7600[typical_ports]}",
  "at_port_interface": "${MODEM_SIM7600[at_port_interface]}",
  "notes": "${MODEM_SIM7600[notes]}"
}
EOF
            ;;
        *)
            echo '{"error": "Unknown modem type"}'
            return 1
            ;;
    esac
}

################################################################################
# Function: get_at_command_port
# Description: Identifies the correct AT command port for the modem
# Returns: Device path (e.g., /dev/ttyUSB1) or symlink
################################################################################
get_at_command_port() {
    # First try the stable symlink
    if [ -L /dev/ttyUSB_EC25_DATA ]; then
        echo "/dev/ttyUSB_EC25_DATA"
        return 0
    fi

    # Detect modem type and find correct port
    local modem_type=$(detect_modem)

    case "$modem_type" in
        EC25)
            # For EC25, interface 01 is the AT port
            for port in /dev/ttyUSB*; do
                [ -c "$port" ] || continue
                local interface=$(udevadm info -a "$port" 2>/dev/null | grep -m1 'bInterfaceNumber' | grep -o '"[^"]*"' | tr -d '"')
                if [ "$interface" = "01" ]; then
                    echo "$port"
                    return 0
                fi
            done
            # Fallback to ttyUSB1
            echo "/dev/ttyUSB1"
            ;;
        SIM7600)
            # For SIM7600, interface 02 is typically AT port
            for port in /dev/ttyUSB*; do
                [ -c "$port" ] || continue
                local interface=$(udevadm info -a "$port" 2>/dev/null | grep -m1 'bInterfaceNumber' | grep -o '"[^"]*"' | tr -d '"')
                if [ "$interface" = "02" ]; then
                    echo "$port"
                    return 0
                fi
            done
            # Fallback to ttyUSB2
            echo "/dev/ttyUSB2"
            ;;
        *)
            echo "/dev/ttyUSB1"
            return 1
            ;;
    esac
}

################################################################################
# Function: get_modem_firmware
# Description: Queries modem firmware version
# Args: $1 - AT command port (optional, auto-detect if not provided)
# Returns: Firmware version string
################################################################################
get_modem_firmware() {
    local at_port="${1:-$(get_at_command_port)}"

    # Send ATI command to get firmware
    local response=$(timeout 2 bash -c "echo -e 'ATI\r' > $at_port; sleep 0.5; timeout 1 cat $at_port" 2>/dev/null)

    # Extract revision line
    echo "$response" | grep "Revision:" | cut -d: -f2 | xargs
}

################################################################################
# Function: get_modem_imei
# Description: Queries modem IMEI
# Args: $1 - AT command port (optional)
# Returns: IMEI (15 digits)
################################################################################
get_modem_imei() {
    local at_port="${1:-$(get_at_command_port)}"

    local response=$(timeout 2 bash -c "echo -e 'AT+GSN\r' > $at_port; sleep 0.5; timeout 1 cat $at_port" 2>/dev/null)

    echo "$response" | grep -oE '[0-9]{15}' | head -1
}

################################################################################
# Function: test_at_communication
# Description: Tests if modem responds to AT commands
# Args: $1 - AT command port (optional)
# Returns: 0 if OK, 1 if failed
################################################################################
test_at_communication() {
    local at_port="${1:-$(get_at_command_port)}"

    if [ ! -w "$at_port" ]; then
        return 1
    fi

    local response=$(timeout 2 bash -c "echo -e 'AT\r' > $at_port; sleep 0.5; timeout 1 cat $at_port" 2>/dev/null)

    if echo "$response" | grep -q "OK"; then
        return 0
    else
        return 1
    fi
}

################################################################################
# Function: print_modem_status
# Description: Prints comprehensive modem status (pretty output)
################################################################################
print_modem_status() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           Modem Detection & Status Report                   ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    local modem_type=$(detect_modem)

    if [ "$modem_type" = "UNKNOWN" ]; then
        echo -e "${RED}✗ No supported modem detected${NC}"
        echo -e "${YELLOW}Supported modems: Quectel EC25-AUX, SIMCom SIM7600G-H${NC}"
        return 1
    fi

    echo -e "${GREEN}✓ Modem detected: $modem_type${NC}"
    echo ""

    # Get detailed info
    local modem_info=$(get_modem_info "$modem_type")
    local name=$(echo "$modem_info" | jq -r '.name')
    local usb_id=$(echo "$modem_info" | jq -r '"\(.vendor_id):\(.product_id)"')
    local volte=$(echo "$modem_info" | jq -r '.volte_capable')
    local fallback=$(echo "$modem_info" | jq -r '.has_3g_fallback')
    local audio=$(echo "$modem_info" | jq -r '.has_usb_audio')
    local audio_dev=$(echo "$modem_info" | jq -r '.audio_device')

    echo -e "  ${BLUE}Model:${NC}         $name"
    echo -e "  ${BLUE}USB ID:${NC}        $usb_id"
    echo -e "  ${BLUE}VoLTE:${NC}         $([ "$volte" = "true" ] && echo -e "${GREEN}✓ Supported${NC}" || echo -e "${RED}✗ Not supported${NC}")"
    echo -e "  ${BLUE}3G Fallback:${NC}   $([ "$fallback" = "true" ] && echo -e "${GREEN}✓ Available${NC}" || echo -e "${YELLOW}✗ 4G only${NC}")"
    echo -e "  ${BLUE}USB Audio:${NC}     $([ "$audio" = "true" ] && echo -e "${GREEN}✓ $audio_dev${NC}" || echo -e "${YELLOW}✗ External required${NC}")"
    echo ""

    # AT command port
    local at_port=$(get_at_command_port)
    echo -e "  ${BLUE}AT Port:${NC}       $at_port"

    # Test AT communication
    if test_at_communication "$at_port"; then
        echo -e "  ${BLUE}AT Commands:${NC}   ${GREEN}✓ Responding${NC}"

        # Get firmware and IMEI
        local firmware=$(get_modem_firmware "$at_port")
        local imei=$(get_modem_imei "$at_port")

        if [ -n "$firmware" ]; then
            echo -e "  ${BLUE}Firmware:${NC}      $firmware"
        fi

        if [ -n "$imei" ]; then
            echo -e "  ${BLUE}IMEI:${NC}          $imei"
        fi
    else
        echo -e "  ${BLUE}AT Commands:${NC}   ${RED}✗ Not responding${NC}"
    fi

    echo ""
    echo -e "${BLUE}USB Ports:${NC}"
    ls -la /dev/ttyUSB* 2>/dev/null | grep -E "^c|^l" | awk '{print "  " $0}'
    echo ""
}

################################################################################
# Main execution (if script is run directly)
################################################################################
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    print_modem_status
fi
