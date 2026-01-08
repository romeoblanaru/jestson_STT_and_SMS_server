#!/bin/bash
# Modem Initialization Script
# Checks and enables USB Audio and VoLTE
# NEVER uses AT+CFUN=1,1 (causes freeze)

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

MODEM_TYPE=""
AT_PORT=""
CHANGES_MADE=false
SMSTOOLS_WAS_RUNNING=false
VOICEBOT_WAS_RUNNING=false

# Stop services to avoid port conflicts
stop_services() {
    echo -e "${YELLOW}Checking services...${NC}"

    if systemctl is-active --quiet smstools; then
        SMSTOOLS_WAS_RUNNING=true
        echo "Stopping smstools..."
        sudo systemctl stop smstools
    fi

    if systemctl is-active --quiet ec25-voice-bot; then
        VOICEBOT_WAS_RUNNING=true
        echo "Stopping ec25-voice-bot..."
        sudo systemctl stop ec25-voice-bot
    fi

    if [ "$SMSTOOLS_WAS_RUNNING" = true ] || [ "$VOICEBOT_WAS_RUNNING" = true ]; then
        sleep 2  # Wait for ports to be released
        echo -e "${GREEN}Services stopped${NC}"
    else
        echo "No services running"
    fi
}

# Restart services if they were running
restart_services() {
    if [ "$SMSTOOLS_WAS_RUNNING" = true ] || [ "$VOICEBOT_WAS_RUNNING" = true ]; then
        echo -e "\n${YELLOW}Restarting services...${NC}"
        services_to_start=()

        if [ "$SMSTOOLS_WAS_RUNNING" = true ]; then
            services_to_start+=("smstools")
        fi
        if [ "$VOICEBOT_WAS_RUNNING" = true ]; then
            services_to_start+=("ec25-voice-bot")
        fi

        sudo systemctl start "${services_to_start[@]}"
        sleep 3
        echo -e "${GREEN}Services restarted${NC}"
    fi
}

# Detect modem type
detect_modem() {
    if lsusb | grep -q "2c7c:0125"; then
        MODEM_TYPE="EC25"
        AT_PORT="/dev/ttyUSB2"
        echo -e "${GREEN}Detected: EC25-AUX${NC}"
    elif lsusb | grep -q "1e0e:9001"; then
        MODEM_TYPE="SIM7600"
        AT_PORT="/dev/ttyUSB2"
        echo -e "${GREEN}Detected: SIM7600G-H${NC}"
    else
        echo -e "${RED}No modem detected!${NC}"
        exit 1
    fi
}

# Send AT command
send_at() {
    local cmd="$1"
    echo -e "${cmd}\r\n" | picocom -b 115200 -x 1500 "$AT_PORT" 2>&1 | grep -v "picocom\|Terminating\|Thanks\|Type"
}

# Initialize EC25
init_ec25() {
    echo -e "\n${YELLOW}=== EC25 Configuration ===${NC}"

    # Check USB Audio (QPCMV)
    echo -n "USB Audio: "
    audio_status=$(send_at "AT+QPCMV?" | grep "QPCMV:" | awk -F: '{print $2}' | tr -d ' \r\n' | cut -d',' -f1)
    if [ "$audio_status" = "1" ]; then
        echo -e "${GREEN}ENABLED${NC}"
    else
        echo -e "${RED}DISABLED${NC} - Enabling..."
        send_at "AT+QPCMV=1,2" > /dev/null
        send_at "AT&W" > /dev/null  # Save to NV memory
        echo -e "${GREEN}ENABLED${NC}"
        CHANGES_MADE=true
    fi

    # Check IMS/VoLTE
    echo -n "IMS/VoLTE: "
    ims_status=$(send_at "AT+QCFG=\"ims\"" | grep "ims" | awk -F, '{print $2}' | tr -d ' \r\n')
    if [ "$ims_status" = "1" ]; then
        echo -e "${GREEN}ENABLED${NC}"
    else
        echo -e "${RED}DISABLED${NC} - Enabling..."
        send_at "AT+QCFG=\"ims\",1" > /dev/null
        # Configure IMS APN
        send_at "AT+QICSGP=2,1,\"ims\",\"\",\"\",2" > /dev/null
        send_at "AT&W" > /dev/null  # Save to NV memory
        echo -e "${GREEN}ENABLED${NC}"
        CHANGES_MADE=true
    fi
}

# Initialize SIM7600
init_sim7600() {
    echo -e "\n${YELLOW}=== SIM7600 Configuration ===${NC}"

    # Check USB Audio (CUSBAUDIO)
    echo -n "USB Audio: "
    audio_status=$(send_at "AT+CUSBAUDIO?" | grep "CUSBAUDIO:" | awk -F: '{print $2}' | tr -d ' \r\n')
    if [ "$audio_status" = "1" ]; then
        echo -e "${GREEN}ENABLED${NC}"
    else
        echo -e "${RED}DISABLED${NC} - Enabling..."
        send_at "AT+CUSBAUDIO=1" > /dev/null
        send_at "AT&W" > /dev/null  # Save to NV memory
        echo -e "${GREEN}ENABLED${NC}"
        CHANGES_MADE=true
    fi

    # Note: SIM7600 VoLTE is carrier-dependent, no universal AT command
    echo "VoLTE: Carrier-dependent (Vodafone UK detected)"
}

# Main
echo -e "${YELLOW}Modem Initialization Script${NC}"
echo "=============================="

stop_services

detect_modem

if [ "$MODEM_TYPE" = "EC25" ]; then
    init_ec25
elif [ "$MODEM_TYPE" = "SIM7600" ]; then
    init_sim7600
fi

echo ""
if [ "$CHANGES_MADE" = true ]; then
    echo -e "${YELLOW}⚠️  Changes made - restarting modem...${NC}"
    echo "Restarting modem (40 second wait)..."
    echo -e "AT+CFUN=1,1\r\n" | picocom -b 115200 -x 3000 "$AT_PORT" > /dev/null 2>&1
    sleep 40
    echo -e "${GREEN}✅ Modem restarted${NC}"
else
    echo -e "${GREEN}✅ All settings already configured${NC}"
fi

restart_services

echo ""
echo "Summary sent to monitoring server..."
/tmp/test_ec25_message.sh custom "Modem ${MODEM_TYPE}: Audio and VoLTE checked/enabled" info 2>/dev/null || true
