#!/bin/bash
################################################################################
# Modem Detector Library
# Detects and identifies LTE modems (EC25-AUX, SIM7600G-H, Samsung S7)
# Version: 1.1.0
# Author: Claude Code + Romeo
# Date: 2025-10-11 (Updated: 2025-01-25)
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

# Samsung phones in USB modem mode (dm+acm+adb)
# Detection: vendor_id 04e8 + ttyACM device present
# product_id varies by phone model - stored for logging only
declare -A MODEM_SAMSUNG=(
    [name]="Samsung Phone (USB Modem)"
    [vendor_id]="04e8"
    [product_id]="any"
    [manufacturer]="Samsung"
    [type]="LTE"
    [has_usb_audio]=false
    [audio_device]="none"
    [has_3g_fallback]=true
    [volte_capable]=true
    [typical_ports]="ttyACM0"
    [at_port_interface]="00"
    [notes]="Phone as USB modem (dm+acm+adb mode), CDC ACM interface"
)

################################################################################
# Function: detect_modem
# Description: Detects connected LTE modem
# Returns: Modem type (EC25, SIM7600, SAMSUNG, UNKNOWN) via echo
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

    # Check for Samsung phone in modem mode (vendor 04e8 + ttyACM device)
    if echo "$usb_devices" | grep -q "04e8:"; then
        # Verify ttyACM device exists for this Samsung
        for acm in /dev/ttyACM*; do
            if [ -c "$acm" ]; then
                local vendor=$(udevadm info --name="$acm" 2>/dev/null | grep "ID_VENDOR_ID=" | cut -d= -f2)
                if [ "$vendor" = "04e8" ]; then
                    echo "SAMSUNG"
                    return 0
                fi
            fi
        done
    fi

    # No supported modem found
    echo "UNKNOWN"
    return 1
}

################################################################################
# Function: detect_all_modems
# Description: Detects ALL connected modems (for multi-modem support)
# Returns: Space-separated list of modem types
################################################################################
detect_all_modems() {
    local usb_devices=$(lsusb)
    local modems=""

    # Check for EC25-AUX
    if echo "$usb_devices" | grep -q "2c7c:0125"; then
        modems="EC25"
    fi

    # Check for SIM7600G-H
    if echo "$usb_devices" | grep -q "1e0e:9011"; then
        modems="$modems SIM7600"
    fi

    # Check for Samsung phone in modem mode
    if echo "$usb_devices" | grep -q "04e8:"; then
        for acm in /dev/ttyACM*; do
            if [ -c "$acm" ]; then
                local vendor=$(udevadm info --name="$acm" 2>/dev/null | grep "ID_VENDOR_ID=" | cut -d= -f2)
                if [ "$vendor" = "04e8" ]; then
                    modems="$modems SAMSUNG"
                    break
                fi
            fi
        done
    fi

    # Trim leading space
    echo "$modems" | xargs
}

################################################################################
# Function: get_modem_info
# Description: Returns detailed modem information
# Args: $1 - modem_type (EC25, SIM7600, SAMSUNG)
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
        SAMSUNG)
            # Get actual product ID from connected device for logging
            local actual_product_id="unknown"
            local actual_serial="unknown"
            local actual_model="unknown"
            for acm in /dev/ttyACM*; do
                if [ -c "$acm" ]; then
                    local info=$(udevadm info --name="$acm" 2>/dev/null)
                    local vendor=$(echo "$info" | grep "ID_VENDOR_ID=" | cut -d= -f2)
                    if [ "$vendor" = "04e8" ]; then
                        actual_product_id=$(echo "$info" | grep "ID_MODEL_ID=" | cut -d= -f2)
                        actual_serial=$(echo "$info" | grep "ID_SERIAL_SHORT=" | cut -d= -f2)
                        actual_model=$(echo "$info" | grep "ID_MODEL=" | cut -d= -f2)
                        break
                    fi
                fi
            done
            cat <<EOF
{
  "name": "${MODEM_SAMSUNG[name]}",
  "vendor_id": "${MODEM_SAMSUNG[vendor_id]}",
  "product_id": "$actual_product_id",
  "serial": "$actual_serial",
  "model": "$actual_model",
  "manufacturer": "${MODEM_SAMSUNG[manufacturer]}",
  "type": "${MODEM_SAMSUNG[type]}",
  "has_usb_audio": ${MODEM_SAMSUNG[has_usb_audio]},
  "audio_device": "${MODEM_SAMSUNG[audio_device]}",
  "has_3g_fallback": ${MODEM_SAMSUNG[has_3g_fallback]},
  "volte_capable": ${MODEM_SAMSUNG[volte_capable]},
  "typical_ports": "${MODEM_SAMSUNG[typical_ports]}",
  "at_port_interface": "${MODEM_SAMSUNG[at_port_interface]}",
  "notes": "${MODEM_SAMSUNG[notes]}"
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
# Args: $1 - modem_type (optional, auto-detect if not provided)
# Returns: Device path (e.g., /dev/ttyUSB1, /dev/ttyACM0) or symlink
################################################################################
get_at_command_port() {
    local modem_type="${1:-$(detect_modem)}"

    case "$modem_type" in
        EC25)
            # First try the stable symlink
            if [ -L /dev/ttyUSB_AT ]; then
                echo "/dev/ttyUSB_AT"
                return 0
            fi
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
            # First try the stable symlink
            if [ -L /dev/ttyUSB_AT ]; then
                echo "/dev/ttyUSB_AT"
                return 0
            fi
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
        SAMSUNG)
            # For Samsung phones, find ttyACM device with Samsung vendor ID
            for acm in /dev/ttyACM*; do
                if [ -c "$acm" ]; then
                    local vendor=$(udevadm info --name="$acm" 2>/dev/null | grep "ID_VENDOR_ID=" | cut -d= -f2)
                    if [ "$vendor" = "04e8" ]; then
                        echo "$acm"
                        return 0
                    fi
                fi
            done
            # Fallback to ttyACM0
            echo "/dev/ttyACM0"
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
        echo -e "${YELLOW}Supported modems: Quectel EC25-AUX, SIMCom SIM7600G-H, Samsung Phone (USB Modem)${NC}"
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
    ls -la /dev/ttyACM* 2>/dev/null | grep -E "^c|^l" | awk '{print "  " $0}'
    echo ""
}

################################################################################
# Main execution (if script is run directly)
################################################################################
if [ "${BASH_SOURCE[0]}" -ef "$0" ]; then
    print_modem_status
fi
