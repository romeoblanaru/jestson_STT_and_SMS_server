#!/bin/bash

# EC25 Status Check Script
# Called by monitoring webhook to send comprehensive status to VPS
# Created: 2026-01-16 - Quectel EC25 specific AT commands

# Port mapping file
PORT_MAPPING="/home/rom/ec25_ports.json"

# Check if EC25 is present
if lsusb | grep -q "2c7c:0125\|2c7c:0121"; then
    MODEM_PRESENT="✅ Present"

    # Get product ID to determine model
    PRODUCT_ID=$(lsusb -d 2c7c: | grep -oP '2c7c:\K[0-9a-f]+')
    case "$PRODUCT_ID" in
        0125)
            MODEL_VARIANT="EC25 (Standard)"
            USB_COMPOSITION="0125 (Standard Serial + Network)"
            ;;
        0121)
            MODEL_VARIANT="EC25-AF (Americas)"
            USB_COMPOSITION="0121 (Standard Serial + Network)"
            ;;
        0306)
            MODEL_VARIANT="EC25 (RNDIS)"
            USB_COMPOSITION="0306 (RNDIS Mode)"
            ;;
        0512)
            MODEL_VARIANT="EC25 (MBIM)"
            USB_COMPOSITION="0512 (MBIM Mode)"
            ;;
        0620)
            MODEL_VARIANT="EC25 (ECM)"
            USB_COMPOSITION="0620 (ECM Mode)"
            ;;
        *)
            MODEL_VARIANT="EC25 (Unknown variant)"
            USB_COMPOSITION="$PRODUCT_ID (Unknown composition)"
            ;;
    esac

    # Get detailed USB interface configuration
    USB_INTERFACES=$(lsusb -d 2c7c: -v 2>/dev/null | grep -E "bNumInterfaces|bInterfaceClass" | head -6 | tr '\n' ' ')
    NUM_INTERFACES=$(lsusb -d 2c7c: -v 2>/dev/null | grep "bNumInterfaces" | head -1 | awk '{print $2}')
    [ -z "$NUM_INTERFACES" ] && NUM_INTERFACES="Unknown"

else
    MODEM_PRESENT="❌ Not Found"
    /home/rom/pi_send_message.sh "🔴 EC25 Status: Modem not detected via USB" "error"
    exit 1
fi

# Initialize variables
MANUFACTURER="Unknown"
MODEL="Unknown"
FIRMWARE="Unknown"
IMEI="Unknown"
IMSI="Unknown"
ICCID="Unknown"
CARRIER="Unknown"
APN="Unknown"

# Try to load cached details from port mapping if available
if [ -f "$PORT_MAPPING" ]; then
    CARRIER=$(jq -r '.carrier // "Unknown"' "$PORT_MAPPING" 2>/dev/null)
    APN=$(jq -r '.apn // "Unknown"' "$PORT_MAPPING" 2>/dev/null)
fi

# Check services status
SMSTOOLS_STATUS="❌ Stopped"
VOICEBOT_STATUS="❌ Stopped"

if systemctl is-active --quiet smstools; then
    SMSTOOLS_STATUS="✅ Running"
fi

if systemctl is-active --quiet sim7600-voice-bot; then
    VOICEBOT_STATUS="✅ Running"
fi

# Stop SMSTools temporarily to query modem
SMSTOOLS_WAS_RUNNING=false

if systemctl is-active --quiet smstools; then
    SMSTOOLS_WAS_RUNNING=true
    sudo /usr/bin/systemctl stop smstools 2>/dev/null
    sleep 5
    # Verify SMSD actually stopped
    for i in {1..5}; do
        systemctl is-active --quiet smstools || break
        sleep 1
    done
fi

# Use ttyUSB2 (AT port for EC25)
AT_PORT="/dev/ttyUSB2"

# Check AT port responsiveness
AT_PORT_STATUS="❌"
if [ -c "$AT_PORT" ]; then
    AT_RESP=$(timeout 3 bash -c "echo -e 'AT\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=100 2>/dev/null" | grep "OK")
    if [ ! -z "$AT_RESP" ]; then
        AT_PORT_STATUS="✅"
    fi
fi

# Get modem details if AT port is working
if [ "$AT_PORT_STATUS" = "✅" ]; then
    # Manufacturer
    MFG_RESP=$(timeout 5 bash -c "echo -e 'AT+CGMI\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    MANUFACTURER=$(echo "$MFG_RESP" | grep -v "AT+CGMI" | grep -v "OK" | grep -v "^$" | tr -d '\r\n' | head -1)
    sleep 0.3

    # Model
    MODEL_RESP=$(timeout 5 bash -c "echo -e 'AT+CGMM\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    MODEL=$(echo "$MODEL_RESP" | grep -v "AT+CGMM" | grep -v "OK" | grep -v "^$" | tr -d '\r\n' | head -1)
    sleep 0.3

    # Firmware
    FW_RESP=$(timeout 5 bash -c "echo -e 'AT+CGMR\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    FIRMWARE=$(echo "$FW_RESP" | grep -v "AT+CGMR" | grep -v "OK" | grep -v "^$" | tr -d '\r\n' | head -1)
    sleep 0.3

    # IMEI
    IMEI_RESP=$(timeout 5 bash -c "echo -e 'AT+CGSN\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    IMEI=$(echo "$IMEI_RESP" | grep -v "AT+CGSN" | grep -v "OK" | grep -v "^$" | tr -d '\r\n' | head -1)
    sleep 0.3

    # IMSI
    IMSI_RESP=$(timeout 5 bash -c "echo -e 'AT+CIMI\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    IMSI=$(echo "$IMSI_RESP" | grep -v "AT+CIMI" | grep -v "OK" | grep -v "^$" | tr -d '\r\n' | head -1)
    sleep 0.3

    # ICCID (Quectel-specific)
    ICCID_RESP=$(timeout 5 bash -c "echo -e 'AT+QCCID\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    ICCID=$(echo "$ICCID_RESP" | grep "+QCCID:" | sed -n 's/.*+QCCID: \([0-9A-F]*\).*/\1/p')
    [ -z "$ICCID" ] && ICCID="Unknown"
    sleep 0.3

    # Signal strength (basic)
    SIGNAL_RESP=$(timeout 5 bash -c "echo -e 'AT+CSQ\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    SIGNAL_RAW=$(echo "$SIGNAL_RESP" | grep "+CSQ:" | sed -n 's/.*+CSQ: \([0-9]*\),.*/\1/p')
    if [ ! -z "$SIGNAL_RAW" ]; then
        SIGNAL="$SIGNAL_RAW/31"
    else
        SIGNAL="Unknown"
    fi
    sleep 0.3

    # Extended signal quality (Quectel-specific)
    QCSQ_RESP=$(timeout 5 bash -c "echo -e 'AT+QCSQ\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=300 2>/dev/null")
    SIGNAL_EXT=$(echo "$QCSQ_RESP" | grep "+QCSQ:" | sed -n 's/.*+QCSQ: "\([^"]*\)",\([-0-9]*\).*/\1 \2dBm/p')
    [ -z "$SIGNAL_EXT" ] && SIGNAL_EXT="Unknown"
    sleep 0.3

    # SIM status
    SIM_RESP=$(timeout 5 bash -c "echo -e 'AT+CPIN?\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    if echo "$SIM_RESP" | grep -q "READY"; then
        SIM_STATUS="✅ Ready"
    elif echo "$SIM_RESP" | grep -q "NOT INSERTED"; then
        SIM_STATUS="❌ Not Inserted"
    else
        SIM_STATUS="⚠️ Unknown"
    fi
    sleep 0.3

    # Network registration
    CREG_RESP=$(timeout 5 bash -c "echo -e 'AT+CREG?\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    if echo "$CREG_RESP" | grep -qE "\+CREG: [0-2],1|\+CREG: [0-2],5"; then
        NETWORK_REG="✅ Registered"
    elif echo "$CREG_RESP" | grep -qE "\+CREG: [0-2],2"; then
        NETWORK_REG="⚠️ Searching"
    else
        NETWORK_REG="❌ Not Registered"
    fi
    sleep 0.3

    # Network information (Quectel-specific)
    QNWINFO_RESP=$(timeout 5 bash -c "echo -e 'AT+QNWINFO\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=300 2>/dev/null")
    if echo "$QNWINFO_RESP" | grep -q "+QNWINFO:"; then
        NETWORK_TYPE=$(echo "$QNWINFO_RESP" | grep "+QNWINFO:" | sed -n 's/.*+QNWINFO: "\([^"]*\)".*/\1/p')
        NETWORK_OPERATOR=$(echo "$QNWINFO_RESP" | grep "+QNWINFO:" | sed -n 's/.*+QNWINFO: "[^"]*","\([^"]*\)".*/\1/p')
        NETWORK_BAND=$(echo "$QNWINFO_RESP" | grep "+QNWINFO:" | sed -n 's/.*+QNWINFO: "[^"]*","[^"]*","\([^"]*\)".*/\1/p')

        NETWORK_INFO="${NETWORK_TYPE} - ${NETWORK_OPERATOR} - ${NETWORK_BAND}"

        # Determine if VoLTE capable
        if [[ "$NETWORK_TYPE" == *"LTE"* ]] || [[ "$NETWORK_TYPE" == *"FDD"* ]]; then
            VOLTE_CAPABLE="✅ LTE (VoLTE capable)"
        else
            VOLTE_CAPABLE="⚠️ ${NETWORK_TYPE} (No VoLTE)"
        fi
    else
        NETWORK_INFO="Unknown"
        VOLTE_CAPABLE="❓ Unknown"
    fi
    sleep 0.3

    # Operator name (Quectel-specific)
    QSPN_RESP=$(timeout 5 bash -c "echo -e 'AT+QSPN\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=300 2>/dev/null")
    OPERATOR_NAME=$(echo "$QSPN_RESP" | grep "+QSPN:" | sed -n 's/.*+QSPN: "\([^"]*\)".*/\1/p')
    [ -z "$OPERATOR_NAME" ] && OPERATOR_NAME="Unknown"
    sleep 0.3

    # Query APN configurations (AT+CGDCONT?)
    CGDCONT_RESP=$(timeout 5 bash -c "echo -e 'AT+CGDCONT?\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=600 2>/dev/null")

    # Parse Data APN (context 1)
    DATA_APN_TYPE=$(echo "$CGDCONT_RESP" | grep "+CGDCONT: 1," | sed -n 's/.*+CGDCONT: 1,"\([^"]*\)".*/\1/p')
    DATA_APN_NAME=$(echo "$CGDCONT_RESP" | grep "+CGDCONT: 1," | sed -n 's/.*+CGDCONT: 1,"[^"]*","\([^"]*\)".*/\1/p')

    [ -z "$DATA_APN_NAME" ] && DATA_APN_NAME=$APN
    [ -z "$DATA_APN_TYPE" ] && DATA_APN_TYPE="Unknown"
    sleep 0.3

    # PDP context status
    CGACT_RESP=$(timeout 5 bash -c "echo -e 'AT+CGACT?\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=300 2>/dev/null")

    # Context 1 (Data)
    if echo "$CGACT_RESP" | grep -q "+CGACT: 1,1"; then
        CTX1_STATUS="✅ Active"
    else
        CTX1_STATUS="❌ Inactive"
    fi

    PDP_CONTEXT="$CTX1_STATUS"
    sleep 0.3

    # IMS/VoLTE configuration check (Quectel-specific)
    QCFG_IMS_RESP=$(timeout 5 bash -c "echo -e 'AT+QCFG=\"ims\"\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    if echo "$QCFG_IMS_RESP" | grep -q "+QCFG: \"ims\",1"; then
        IMS_STATUS="✅ Enabled"
    elif echo "$QCFG_IMS_RESP" | grep -q "+QCFG: \"ims\",0"; then
        IMS_STATUS="❌ Disabled"
    else
        IMS_STATUS="⚠️ Unknown (may be auto-enabled by network)"
    fi
    sleep 0.3

    # Network scan mode (Quectel-specific)
    QCFG_NWSCAN_RESP=$(timeout 5 bash -c "echo -e 'AT+QCFG=\"nwscanmode\"\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    SCAN_MODE=$(echo "$QCFG_NWSCAN_RESP" | grep "+QCFG:" | sed -n 's/.*+QCFG: "nwscanmode",\([0-9]*\).*/\1/p')
    case "$SCAN_MODE" in
        0)
            NET_PREF="Auto (LTE/WCDMA/GSM)"
            ;;
        1)
            NET_PREF="GSM only"
            ;;
        2)
            NET_PREF="WCDMA only"
            ;;
        3)
            NET_PREF="✅ LTE only"
            ;;
        *)
            NET_PREF="Unknown"
            ;;
    esac
    sleep 0.3

    # EPS registration status (for LTE)
    CEREG_RESP=$(timeout 5 bash -c "echo -e 'AT+CEREG?\r' > $AT_PORT; sleep 1; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    if echo "$CEREG_RESP" | grep -qE "\+CEREG: [0-2],1"; then
        EPS_STATUS="✅ Registered (home network)"
    elif echo "$CEREG_RESP" | grep -qE "\+CEREG: [0-2],5"; then
        EPS_STATUS="✅ Registered (roaming)"
    else
        EPS_STATUS="❌ Not registered"
    fi
fi

# Check internet connectivity
INTERNET="❌"
PING_TIME="N/A"
if ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1; then
    INTERNET="✅"
    PING_RESP=$(ping -c 1 -W 2 8.8.8.8 2>/dev/null | grep "time=")
    if [ ! -z "$PING_RESP" ]; then
        PING_TIME=$(echo "$PING_RESP" | sed -n 's/.*time=\([0-9.]*\) ms.*/\1ms/p')
    fi
fi

# Check wwan0 interface
WWAN0_STATUS="❌ Down"
WWAN0_IP="No IP"
if ip link show wwan0 2>/dev/null | grep -q "state UP"; then
    WWAN0_STATUS="✅ Up"
    WWAN0_IP=$(ip addr show wwan0 2>/dev/null | grep "inet " | awk '{print $2}' | head -1)
    [ -z "$WWAN0_IP" ] && WWAN0_IP="No IP"
fi

# Restart SMSTools if it was running
if [ "$SMSTOOLS_WAS_RUNNING" = true ]; then
    sudo /usr/bin/systemctl start smstools
fi

# Build comprehensive status message
STATUS_MSG="**🟧 EC25 Comprehensive Status Report**"$'\n'
STATUS_MSG+="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**📱 Modem Hardware:**"$'\n'
STATUS_MSG+="• Modem: ${MODEM_PRESENT}"$'\n'
STATUS_MSG+="• Manufacturer: ${MANUFACTURER}"$'\n'
STATUS_MSG+="• Model: ${MODEL}"$'\n'
STATUS_MSG+="• Variant: ${MODEL_VARIANT}"$'\n'
STATUS_MSG+="• Firmware: ${FIRMWARE}"$'\n'
STATUS_MSG+="• IMEI: ${IMEI}"$'\n'
STATUS_MSG+="• USB Composition: ${USB_COMPOSITION}"$'\n'
STATUS_MSG+="• USB Interfaces: ${NUM_INTERFACES}"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**📶 Network Status:**"$'\n'
STATUS_MSG+="• SIM Card: ${SIM_STATUS}"$'\n'
STATUS_MSG+="• ICCID: ${ICCID}"$'\n'
STATUS_MSG+="• IMSI: ${IMSI}"$'\n'
STATUS_MSG+="• Operator: ${OPERATOR_NAME}"$'\n'
STATUS_MSG+="• Network Registration: ${NETWORK_REG}"$'\n'
STATUS_MSG+="• Signal Strength: ${SIGNAL}"$'\n'
STATUS_MSG+="• Signal Extended: ${SIGNAL_EXT}"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**📡 Network Mode:**"$'\n'
STATUS_MSG+="• Network Info: ${NETWORK_INFO:-Unknown}"$'\n'
STATUS_MSG+="• Mode Preference: ${NET_PREF:-Unknown}"$'\n'
STATUS_MSG+="• VoLTE Capability: ${VOLTE_CAPABLE:-Unknown}"$'\n'
STATUS_MSG+="• EPS (LTE) Registration: ${EPS_STATUS:-Unknown}"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**🌐 Data & VoLTE:**"$'\n'
STATUS_MSG+="• PDP Context: ${PDP_CONTEXT}"$'\n'
STATUS_MSG+="• Data APN: ${DATA_APN_NAME:-$APN} (${DATA_APN_TYPE})"$'\n'
STATUS_MSG+="• IMS/VoLTE: ${IMS_STATUS}"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**🔌 Connectivity:**"$'\n'
STATUS_MSG+="• AT Port: ${AT_PORT_STATUS} (${AT_PORT})"$'\n'
STATUS_MSG+="• Internet: ${INTERNET} (Ping: ${PING_TIME})"$'\n'
STATUS_MSG+="• wwan0: ${WWAN0_STATUS} (${WWAN0_IP})"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**⚙️ Services:**"$'\n'
STATUS_MSG+="• SMSTools: ${SMSTOOLS_STATUS}"$'\n'
STATUS_MSG+="• Voice Bot: ${VOICEBOT_STATUS}"$'\n'
STATUS_MSG+=""$'\n'

# Check STT Server (Parakeet) status
STT_STATUS="❌ Stopped"
STT_MODEL="Unknown"
STT_HEALTH="N/A"

if docker ps --format "{{.Image}}" 2>/dev/null | grep -q "parakeet-server"; then
    STT_HEALTH_RESP=$(curl -s --connect-timeout 2 --max-time 3 http://localhost:9001/health 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$STT_HEALTH_RESP" ]; then
        STT_STATUS="✅ Running"
        STT_MODEL=$(echo "$STT_HEALTH_RESP" | jq -r '.model // "Unknown"' 2>/dev/null || echo "Parakeet")
        STT_HEALTH=$(echo "$STT_HEALTH_RESP" | jq -r '.status // "Unknown"' 2>/dev/null || echo "unknown")
    else
        STT_STATUS="⚠️ Container running but no response"
    fi
fi

# Check VPS SMS Server connectivity
VPS_SMS_STATUS="❌ Unreachable"
VPS_SMS_RESPONSE="N/A"
VPS_ENDPOINT="http://10.100.0.1:5000/api/health"

# Try health endpoint first, fallback to checking if port is open
VPS_CHECK=$(curl -s --connect-timeout 3 --max-time 5 "$VPS_ENDPOINT" 2>/dev/null)
if [ $? -eq 0 ] && [ -n "$VPS_CHECK" ]; then
    VPS_SMS_STATUS="✅ OK"
    VPS_SMS_RESPONSE=$(echo "$VPS_CHECK" | jq -r '.status // "healthy"' 2>/dev/null || echo "responding")
else
    # Fallback: check if main API endpoint is reachable
    VPS_MAIN=$(curl -s --connect-timeout 3 --max-time 5 -w "%{http_code}" "http://10.100.0.1:5000/api/send" 2>/dev/null | tail -1)
    if [ "$VPS_MAIN" = "405" ] || [ "$VPS_MAIN" = "400" ] || [ "$VPS_MAIN" = "200" ]; then
        VPS_SMS_STATUS="✅ Reachable"
        VPS_SMS_RESPONSE="HTTP $VPS_MAIN"
    else
        VPS_SMS_STATUS="❌ No response"
        VPS_SMS_RESPONSE="Timeout or connection failed"
    fi
fi

STATUS_MSG+="**🎙️ STT Service:**"$'\n'
STATUS_MSG+="• Server Status: ${STT_STATUS}"$'\n'
STATUS_MSG+="• Model: ${STT_MODEL}"$'\n'
STATUS_MSG+="• Health: ${STT_HEALTH}"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**🔗 VPS SMS Server:**"$'\n'
STATUS_MSG+="• Connectivity: ${VPS_SMS_STATUS}"$'\n'
STATUS_MSG+="• Response: ${VPS_SMS_RESPONSE}"

# Send to VPS
/home/rom/pi_send_message.sh "$STATUS_MSG" "info"

echo "$STATUS_MSG"
