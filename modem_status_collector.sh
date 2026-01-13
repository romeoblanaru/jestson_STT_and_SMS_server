#!/bin/bash
###############################################################################
# Modem Status Collector - Using proven working method from check_sim7600_status.sh
# Gets REAL-TIME modem data via AT commands
###############################################################################

RECIPIENT="$1"
AT_PORT="/dev/ttyUSB_SIM7600_AT"  # Stable symlink to Interface 02 (auto-detected)
API_URL="http://localhost:8088/send_sms"
LOG="/var/log/modem_status_collector.log"

log() { echo "[$(date '+%H:%M:%S')] $*" >> "$LOG" 2>&1; }

send_sms() {
    local msg="$1"
    # Use unified API - handles encoding, splitting, and delays automatically
    local response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"to\":\"$RECIPIENT\",\"message\":\"$msg\"}" 2>&1)

    if echo "$response" | grep -q '"success": true'; then
        local parts=$(echo "$response" | grep -o '"parts": [0-9]*' | grep -o '[0-9]*')
        log "SMS sent via API (parts: ${parts:-1})"
    else
        log "ERROR: API failed - $response"
    fi
}

# Trap to ensure SMSD always restarts
trap 'sudo /usr/bin/systemctl start smstools >> "$LOG" 2>&1; log "EXIT"' EXIT

log "=== START: $RECIPIENT ==="

# Stop SMSD to access modem
log "Stopping SMSD..."
if ! sudo /usr/bin/systemctl stop smstools >> "$LOG" 2>&1; then
    log "ERROR: Failed to stop SMSD"
    exit 1
fi
sleep 2

# SHORTENED MESSAGE FORMAT - fits in single SMS (under 160 chars GSM)
MSG="MODEM STATUS\n"

# Signal Quality (AT+CSQ)
log "Signal..."
CSQ_RESP=$(timeout 5 bash -c "echo -e 'AT+CSQ\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=200 2>/dev/null")
SIGNAL=$(echo "$CSQ_RESP" | grep "+CSQ:" | sed -n 's/.*+CSQ: \([0-9]*\),.*/\1/p')
if [ -n "$SIGNAL" ]; then
    MSG+="Signal: $SIGNAL/31\n"
    log "Signal: $SIGNAL"
else
    MSG+="Signal: N/A\n"
fi
sleep 0.3

# Network Operator (AT+COPS?)
log "Operator..."
COPS_RESP=$(timeout 5 bash -c "echo -e 'AT+COPS?\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=300 2>/dev/null")
OPERATOR=$(echo "$COPS_RESP" | grep "+COPS:" | sed -n 's/.*+COPS: [0-9]*,[0-9]*,"\([^"]*\)".*/\1/p')

# Network Type - Get connection type (4G/3G/2G) using AT+CPSI?
log "Network type..."
CPSI_RESP=$(timeout 5 bash -c "echo -e 'AT+CPSI?\r' > $AT_PORT; sleep 0.5; dd if=$AT_PORT bs=1 count=500 2>/dev/null")
NET_TYPE="Unknown"
if echo "$CPSI_RESP" | grep -q "+CPSI: LTE"; then
    NET_TYPE="4G"
elif echo "$CPSI_RESP" | grep -q "+CPSI: WCDMA"; then
    NET_TYPE="3G"
elif echo "$CPSI_RESP" | grep -q "+CPSI: GSM"; then
    NET_TYPE="2G"
elif echo "$CPSI_RESP" | grep -q "NO SERVICE"; then
    NET_TYPE="NoSvc"
fi

# Combine operator and network type on one line
if [ -n "$OPERATOR" ]; then
    # Shorten operator name (remove spaces, shorten common words)
    OPERATOR_SHORT=$(echo "$OPERATOR" | sed 's/ - UK / /g; s/giffgaff/gg/g')
    MSG+="Network: $OPERATOR_SHORT ($NET_TYPE)\n"
    log "Operator: $OPERATOR ($NET_TYPE)"
else
    MSG+="Network: ($NET_TYPE)\n"
fi
sleep 0.3

# Check VPS SMS Server
log "VPS SMS check..."
VPS_STATUS="Err"
if timeout 3 curl -s -o /dev/null -w "%{http_code}" http://10.100.0.1:8088/health 2>/dev/null | grep -q "200"; then
    VPS_STATUS="OK"
fi
log "VPS SMS: $VPS_STATUS"
sleep 0.3

# Check TTS Server
log "TTS check..."
TTS_STATUS="Err"
if timeout 3 curl -s http://10.100.0.2:9001/health 2>/dev/null | grep -q "ok\|healthy\|status"; then
    TTS_STATUS="OK"
fi
log "TTS: $TTS_STATUS"

# Combine services on one line
MSG+="VPS: $VPS_STATUS | TTS: $TTS_STATUS\n"
MSG+="Time: $(date '+%d %b %H:%M')"

log "Restarting SMSD..."
if ! sudo /usr/bin/systemctl start smstools >> "$LOG" 2>&1; then
    log "ERROR: Failed to restart SMSD"
fi

# Wait 3 seconds for SMSD to stabilize before queuing message
sleep 3
log "SMSD stabilized, queuing message..."

log "Sending SMS..."
send_sms "$(echo -e "$MSG")"

log "=== DONE ==="
trap - EXIT
exit 0
