#!/bin/bash

# SIM7600 Status Check Script
# Called by monitoring webhook to send comprehensive status to VPS
# Updated: Oct 18, 2025 - Uses ttyUSB3 and includes IMEI, Firmware, etc.

# Port mapping file (created by detector)
PORT_MAPPING="/home/rom/sim7600_ports.json"

# Check if SIM7600 is present
if lsusb | grep -q "1e0e:9011\|1e0e:9001"; then
    MODEM_PRESENT="✅ Present"

    # Get USB composition
    USB_COMP=$(lsusb -v -d 1e0e: 2>/dev/null | grep -i "iproduct" | head -1)
    if echo "$USB_COMP" | grep -q "9001"; then
        USB_MODE="9001 (Voice Mode)"
    elif echo "$USB_COMP" | grep -q "9011"; then
        USB_MODE="9011 (Fast Data)"
    elif echo "$USB_COMP" | grep -q "1025"; then
        USB_MODE="1025 (QMI Mode)"
    else
        USB_MODE="Unknown"
    fi
else
    MODEM_PRESENT="❌ Not Found"
    /home/rom/pi_send_message.sh "🔴 SIM7600 Status: Modem not detected via USB" "error"
    exit 1
fi

# Try to load cached details from port mapping first
MANUFACTURER="Unknown"
MODEL="Unknown"
FIRMWARE="Unknown"
IMEI="Unknown"
IMSI="Unknown"
CARRIER="Unknown"
APN="Unknown"
IMS_APN="Unknown"

if [ -f "$PORT_MAPPING" ]; then
    # Extract details from JSON (if available)
    CARRIER=$(jq -r '.carrier // "Unknown"' "$PORT_MAPPING" 2>/dev/null)
    APN=$(jq -r '.apn // "Unknown"' "$PORT_MAPPING" 2>/dev/null)
    IMS_APN=$(jq -r '.ims_apn // "Unknown"' "$PORT_MAPPING" 2>/dev/null)
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

# Stop SMSTools temporarily to query modem (SMS can wait, voice calls cannot!)
SMSTOOLS_WAS_RUNNING=false

if systemctl is-active --quiet smstools; then
    SMSTOOLS_WAS_RUNNING=true
    sudo systemctl stop smstools 2>/dev/null
    sleep 2
fi

# Use ttyUSB2 (SMS port - safe to use while voice calls are active)
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
    MFG_RESP=$(timeout 5 bash -c "echo -e 'AT+CGMI\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    MANUFACTURER=$(echo "$MFG_RESP" | grep -v "AT+CGMI" | grep -v "OK" | grep -v "^$" | tr -d '\r\n' | head -1)
    sleep 0.3

    # Model
    MODEL_RESP=$(timeout 5 bash -c "echo -e 'AT+CGMM\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    MODEL=$(echo "$MODEL_RESP" | grep -v "AT+CGMM" | grep -v "OK" | grep -v "^$" | tr -d '\r\n' | head -1)
    sleep 0.3

    # Firmware
    FW_RESP=$(timeout 5 bash -c "echo -e 'AT+CGMR\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    FIRMWARE=$(echo "$FW_RESP" | grep -v "AT+CGMR" | grep -v "OK" | grep -v "^$" | tr -d '\r\n' | head -1)
    sleep 0.3

    # IMEI
    IMEI_RESP=$(timeout 5 bash -c "echo -e 'AT+CGSN\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    IMEI=$(echo "$IMEI_RESP" | grep -v "AT+CGSN" | grep -v "OK" | grep -v "^$" | tr -d '\r\n' | head -1)
    sleep 0.3

    # IMSI
    IMSI_RESP=$(timeout 5 bash -c "echo -e 'AT+CIMI\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    IMSI=$(echo "$IMSI_RESP" | grep -v "AT+CIMI" | grep -v "OK" | grep -v "^$" | tr -d '\r\n' | head -1)
    sleep 0.3

    # Signal strength
    SIGNAL_RESP=$(timeout 5 bash -c "echo -e 'AT+CSQ\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    SIGNAL=$(echo "$SIGNAL_RESP" | grep "+CSQ:" | sed -n 's/.*+CSQ: \([0-9]*\),.*/\1\/31/p')
    [ -z "$SIGNAL" ] && SIGNAL="Unknown"
    sleep 0.3

    # SIM status
    SIM_RESP=$(timeout 5 bash -c "echo -e 'AT+CPIN?\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    if echo "$SIM_RESP" | grep -q "READY"; then
        SIM_STATUS="✅ Ready"
    elif echo "$SIM_RESP" | grep -q "NOT INSERTED"; then
        SIM_STATUS="❌ Not Inserted"
    else
        SIM_STATUS="⚠️ Unknown"
    fi
    sleep 0.3

    # Network registration
    CREG_RESP=$(timeout 5 bash -c "echo -e 'AT+CREG?\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    if echo "$CREG_RESP" | grep -q "+CREG: 0,1\|+CREG: 0,5"; then
        NETWORK_REG="✅ Registered"
    else
        NETWORK_REG="❌ Not Registered"
    fi
    sleep 0.3

    # Query APN configurations (AT+CGDCONT?)
    CGDCONT_RESP=$(timeout 5 bash -c "echo -e 'AT+CGDCONT?\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=600 2>/dev/null")

    # Parse Data APN (context 1)
    DATA_APN_TYPE=$(echo "$CGDCONT_RESP" | grep "+CGDCONT: 1," | sed -n 's/.*+CGDCONT: 1,"\([^"]*\)".*/\1/p')
    DATA_APN_NAME=$(echo "$CGDCONT_RESP" | grep "+CGDCONT: 1," | sed -n 's/.*+CGDCONT: 1,"[^"]*","\([^"]*\)".*/\1/p')

    # Parse IMS APN (context 2)
    IMS_APN_TYPE=$(echo "$CGDCONT_RESP" | grep "+CGDCONT: 2," | sed -n 's/.*+CGDCONT: 2,"\([^"]*\)".*/\1/p')
    IMS_APN_NAME=$(echo "$CGDCONT_RESP" | grep "+CGDCONT: 2," | sed -n 's/.*+CGDCONT: 2,"[^"]*","\([^"]*\)".*/\1/p')

    # Validate IMS APN type
    if [ "$IMS_APN_TYPE" = "IPV4V6" ]; then
        IMS_TYPE_STATUS="✅ IPV4V6 (correct)"
    elif [ "$IMS_APN_TYPE" = "IP" ]; then
        IMS_TYPE_STATUS="⚠️ IP (should be IPV4V6!)"
    else
        IMS_TYPE_STATUS="❓ $IMS_APN_TYPE"
    fi
    sleep 0.3

    # PDP context status (both contexts)
    CGACT_RESP=$(timeout 5 bash -c "echo -e 'AT+CGACT?\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=300 2>/dev/null")

    # Context 1 (Data)
    if echo "$CGACT_RESP" | grep -q "+CGACT: 1,1"; then
        CTX1_STATUS="✅ Active"
    else
        CTX1_STATUS="❌ Inactive"
    fi

    # Context 2 (IMS)
    if echo "$CGACT_RESP" | grep -q "+CGACT: 2,1"; then
        CTX2_STATUS="✅ Active"
    else
        CTX2_STATUS="❌ Inactive"
    fi

    # Combined status
    if [ "$CTX1_STATUS" = "✅ Active" ] && [ "$CTX2_STATUS" = "✅ Active" ]; then
        PDP_CONTEXT="✅ Both contexts active"
    elif [ "$CTX1_STATUS" = "✅ Active" ] && [ "$CTX2_STATUS" != "✅ Active" ]; then
        PDP_CONTEXT="⚠️ Only Data active (IMS inactive)"
    elif [ "$CTX1_STATUS" != "✅ Active" ] && [ "$CTX2_STATUS" = "✅ Active" ]; then
        PDP_CONTEXT="⚠️ Only IMS active (Data inactive)"
    else
        PDP_CONTEXT="❌ Both contexts inactive"
    fi
    sleep 0.3

    # VoLTE status
    VOLTE_RESP=$(timeout 5 bash -c "echo -e 'AT+CEVOLTE?\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    if echo "$VOLTE_RESP" | grep -q "+CEVOLTE: 1,1"; then
        VOLTE="✅ Enabled"
    elif echo "$VOLTE_RESP" | grep -q "ERROR"; then
        VOLTE="⚠️ Not supported (auto-enabled by network)"
    else
        VOLTE="❌ Disabled"
    fi
    sleep 0.3

    # Network mode preference (AT+CNMP?)
    CNMP_RESP=$(timeout 5 bash -c "echo -e 'AT+CNMP?\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    if echo "$CNMP_RESP" | grep -q "+CNMP: 38"; then
        NET_PREF="✅ LTE-only (mode 38)"
    elif echo "$CNMP_RESP" | grep -q "+CNMP: 2"; then
        NET_PREF="⚠️ Auto (allows 3G fallback)"
    else
        NET_PREF="❓ Unknown"
    fi
    sleep 0.3

    # System information - actual network mode (AT+CPSI?)
    CPSI_RESP=$(timeout 5 bash -c "echo -e 'AT+CPSI?\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=500 2>/dev/null")
    if echo "$CPSI_RESP" | grep -q "LTE"; then
        ACTUAL_MODE="✅ LTE (VoLTE ready)"
    elif echo "$CPSI_RESP" | grep -q "WCDMA"; then
        ACTUAL_MODE="⚠️ WCDMA (3G - no VoLTE)"
    elif echo "$CPSI_RESP" | grep -q "GSM"; then
        ACTUAL_MODE="⚠️ GSM (2G - no VoLTE)"
    else
        ACTUAL_MODE="❓ Unknown"
    fi
    sleep 0.3

    # Network system mode (AT+CNSMOD?)
    CNSMOD_RESP=$(timeout 5 bash -c "echo -e 'AT+CNSMOD?\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    if echo "$CNSMOD_RESP" | grep -q "+CNSMOD: 0,8\|+CNSMOD: 1,8"; then
        NETWORK_TECH="LTE"
    elif echo "$CNSMOD_RESP" | grep -q "+CNSMOD: 0,7\|+CNSMOD: 1,7"; then
        NETWORK_TECH="HSPA (3G+)"
    elif echo "$CNSMOD_RESP" | grep -q "+CNSMOD: 0,4\|+CNSMOD: 1,4"; then
        NETWORK_TECH="WCDMA (3G)"
    elif echo "$CNSMOD_RESP" | grep -q "+CNSMOD: 0,2\|+CNSMOD: 1,2"; then
        NETWORK_TECH="GPRS (2.5G)"
    elif echo "$CNSMOD_RESP" | grep -q "+CNSMOD: 0,1\|+CNSMOD: 1,1"; then
        NETWORK_TECH="GSM (2G)"
    else
        NETWORK_TECH="Unknown"
    fi
    sleep 0.3

    # EPS registration status (AT+CEREG?)
    CEREG_RESP=$(timeout 5 bash -c "echo -e 'AT+CEREG?\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
    if echo "$CEREG_RESP" | grep -q "+CEREG: 0,1"; then
        EPS_STATUS="✅ Registered (home network)"
    elif echo "$CEREG_RESP" | grep -q "+CEREG: 0,5"; then
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
    sudo systemctl start smstools
fi

# Build comprehensive status message
STATUS_MSG="**🟦 SIM7600 Comprehensive Status Report**"$'\n'
STATUS_MSG+="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**📱 Modem Hardware:**"$'\n'
STATUS_MSG+="• Modem: ${MODEM_PRESENT}"$'\n'
STATUS_MSG+="• Manufacturer: ${MANUFACTURER}"$'\n'
STATUS_MSG+="• Model: ${MODEL}"$'\n'
STATUS_MSG+="• Firmware: ${FIRMWARE}"$'\n'
STATUS_MSG+="• IMEI: ${IMEI}"$'\n'
STATUS_MSG+="• USB Composition: ${USB_MODE}"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**📶 Network Status:**"$'\n'
STATUS_MSG+="• SIM Card: ${SIM_STATUS}"$'\n'
STATUS_MSG+="• IMSI: ${IMSI}"$'\n'
STATUS_MSG+="• Carrier: ${CARRIER}"$'\n'
STATUS_MSG+="• Network Registration: ${NETWORK_REG}"$'\n'
STATUS_MSG+="• Signal Strength: ${SIGNAL}"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**📡 Network Mode:**"$'\n'
STATUS_MSG+="• Mode Preference: ${NET_PREF:-Unknown}"$'\n'
STATUS_MSG+="• Actual Network: ${ACTUAL_MODE:-Unknown}"$'\n'
STATUS_MSG+="• Technology: ${NETWORK_TECH:-Unknown}"$'\n'
STATUS_MSG+="• EPS (LTE) Registration: ${EPS_STATUS:-Unknown}"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**🌐 Data & VoLTE:**"$'\n'
STATUS_MSG+="• PDP Context: ${PDP_CONTEXT}"$'\n'
STATUS_MSG+="  - Context 1 (Data): ${CTX1_STATUS:-Unknown}"$'\n'
STATUS_MSG+="  - Context 2 (IMS): ${CTX2_STATUS:-Unknown}"$'\n'
STATUS_MSG+="• Data APN: ${DATA_APN_NAME:-$APN} (${DATA_APN_TYPE:-Unknown})"$'\n'
STATUS_MSG+="• IMS APN: ${IMS_APN_NAME:-$IMS_APN} (${IMS_TYPE_STATUS:-Unknown})"$'\n'
STATUS_MSG+="• VoLTE: ${VOLTE}"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**🔌 Connectivity:**"$'\n'
STATUS_MSG+="• AT Port: ${AT_PORT_STATUS} (${AT_PORT})"$'\n'
STATUS_MSG+="• Internet: ${INTERNET} (Ping: ${PING_TIME})"$'\n'
STATUS_MSG+="• wwan0: ${WWAN0_STATUS} (${WWAN0_IP})"$'\n'
STATUS_MSG+=""$'\n'
STATUS_MSG+="**⚙️ Services:**"$'\n'
STATUS_MSG+="• SMSTools: ${SMSTOOLS_STATUS}"$'\n'
STATUS_MSG+="• Voice Bot: ${VOICEBOT_STATUS}"

# Send to VPS
/home/rom/pi_send_message.sh "$STATUS_MSG" "info"

echo "$STATUS_MSG"
