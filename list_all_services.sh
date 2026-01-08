#!/bin/bash

# List All Services Status Script
# Shows status of all important services on the Raspberry Pi

echo "🔧 Checking all services status..."

# Define all services to check with descriptions
declare -A SERVICES=(
    ["smstools"]="SMS Gateway Service"
    ["sim7600-voice-bot"]="SIM7600 Voice Bot"
    ["sim7600-detector"]="SIM7600 Modem Detector"
    ["ec25-voice-bot"]="EC25 Voice Bot"
    ["unified-api"]="Unified SMS/Voice API (8088)"
    ["monitoring-webhook"]="Monitoring Webhook (8070)"
    ["wireguard"]="WireGuard VPN"
    ["wg-quick@wg0"]="WireGuard Interface"
    ["ssh"]="SSH Server"
    ["networking"]="Network Service"
    ["systemd-resolved"]="DNS Resolver"
    ["systemd-timesyncd"]="Time Sync Service"
    ["cron"]="Cron Scheduler"
    ["rsyslog"]="System Logging"
)

# Additional Python process-based services to check
PYTHON_SERVICES=(
    "unified_sms_voice_api.py:8088:SMS Gateway API"
    "monitoring_webhook.py:8070:Monitoring Webhook"
    "sim7600_voice_bot.py:N/A:SIM7600 Voice Bot"
    "ec25_voice_bot_v3.py:N/A:EC25 Voice Bot"
)

STATUS_REPORT="**📋 SERVICES STATUS REPORT**"$'\n'
STATUS_REPORT+="$(date '+%Y-%m-%d %H:%M:%S')"$'\n'
STATUS_REPORT+="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"$'\n'
STATUS_REPORT+=""$'\n'

# Check systemd services
STATUS_REPORT+="<blue>**🔹 SYSTEMD SERVICES:**</blue>"$'\n'
for SERVICE in "${!SERVICES[@]}"; do
    DESCRIPTION="${SERVICES[$SERVICE]}"

    if systemctl is-active --quiet "$SERVICE" 2>/dev/null; then
        # Get uptime if running
        UPTIME=$(systemctl show "$SERVICE" --property=ActiveEnterTimestamp --value 2>/dev/null)
        if [ ! -z "$UPTIME" ] && [ "$UPTIME" != "n/a" ]; then
            UPTIME_SECONDS=$(($(date +%s) - $(date -d "$UPTIME" +%s)))
            if [ $UPTIME_SECONDS -gt 86400 ]; then
                UPTIME_STR="$(($UPTIME_SECONDS / 86400))d"
            elif [ $UPTIME_SECONDS -gt 3600 ]; then
                UPTIME_STR="$(($UPTIME_SECONDS / 3600))h"
            else
                UPTIME_STR="$(($UPTIME_SECONDS / 60))m"
            fi
            STATUS_LINE="✅ ${SERVICE}: RUNNING (${UPTIME_STR}) - ${DESCRIPTION}"
        else
            STATUS_LINE="✅ ${SERVICE}: RUNNING - ${DESCRIPTION}"
        fi
    else
        # Check if service exists
        if systemctl list-unit-files | grep -q "^${SERVICE}"; then
            STATUS_LINE="❌ ${SERVICE}: STOPPED - ${DESCRIPTION}"
        else
            STATUS_LINE="⚪ ${SERVICE}: NOT INSTALLED - ${DESCRIPTION}"
        fi
    fi
    STATUS_REPORT+="${STATUS_LINE}"$'\n'
done

# Check Python process-based services
STATUS_REPORT+=""$'\n'
STATUS_REPORT+="<blue>**🔹 PYTHON SERVICES:**</blue>"$'\n'
for SERVICE_INFO in "${PYTHON_SERVICES[@]}"; do
    IFS=':' read -r SCRIPT PORT DESC <<< "$SERVICE_INFO"

    if pgrep -f "$SCRIPT" > /dev/null 2>&1; then
        PID=$(pgrep -f "$SCRIPT" | head -1)
        if [ "$PORT" != "N/A" ]; then
            if netstat -tuln 2>/dev/null | grep -q ":$PORT "; then
                STATUS_LINE="✅ ${DESC} (PID: ${PID}, Port: ${PORT}): RUNNING"
            else
                STATUS_LINE="⚠️ ${DESC} (PID: ${PID}): RUNNING but port ${PORT} not listening"
            fi
        else
            STATUS_LINE="✅ ${DESC} (PID: ${PID}): RUNNING"
        fi
    else
        STATUS_LINE="❌ ${DESC}: NOT RUNNING"
    fi
    STATUS_REPORT+="${STATUS_LINE}"$'\n'
done

# Check modem status
STATUS_REPORT+=""$'\n'
STATUS_REPORT+="<blue>**🔹 MODEM STATUS:**</blue>"$'\n'
if lsusb | grep -q "1e0e:9011\|1e0e:9001"; then
    STATUS_REPORT+="✅ SIM7600G-H: CONNECTED"$'\n'
elif lsusb | grep -q "2c7c:0125"; then
    STATUS_REPORT+="✅ EC25-AUX: CONNECTED"$'\n'
else
    STATUS_REPORT+="❌ No GSM modem detected"$'\n'
fi

# Check network interfaces
STATUS_REPORT+=""$'\n'
STATUS_REPORT+="<blue>**🔹 NETWORK INTERFACES:**</blue>"$'\n'
if ip link show wg0 2>/dev/null | grep -q "UP"; then
    WG_IP=$(ip -4 addr show wg0 | grep inet | awk '{print $2}' | cut -d/ -f1)
    STATUS_REPORT+="✅ WireGuard VPN: UP (${WG_IP})"$'\n'
else
    STATUS_REPORT+="❌ WireGuard VPN: DOWN"$'\n'
fi

if ip link show wlan0 2>/dev/null | grep -q "UP"; then
    WLAN_IP=$(ip -4 addr show wlan0 | grep inet | awk '{print $2}' | cut -d/ -f1)
    STATUS_REPORT+="✅ WiFi: UP (${WLAN_IP})"$'\n'
else
    STATUS_REPORT+="⚠️ WiFi: DOWN or not configured"$'\n'
fi

if ip link show eth0 2>/dev/null | grep -q "UP"; then
    ETH_IP=$(ip -4 addr show eth0 | grep inet | awk '{print $2}' | cut -d/ -f1)
    STATUS_REPORT+="✅ Ethernet: UP (${ETH_IP})"$'\n'
else
    STATUS_REPORT+="⚪ Ethernet: Not connected"$'\n'
fi

# Check port listeners
STATUS_REPORT+=""$'\n'
STATUS_REPORT+="<blue>**🔹 LISTENING PORTS:**</blue>"$'\n'
PORTS_INFO=$(netstat -tuln 2>/dev/null | grep LISTEN | grep -E ":(22|80|443|8070|8088|10000) " | awk '{print $4}' | sed 's/.*://' | sort -u)
for PORT in $PORTS_INFO; do
    case $PORT in
        22) STATUS_REPORT+="✅ Port ${PORT}: SSH"$'\n' ;;
        8070) STATUS_REPORT+="✅ Port ${PORT}: Monitoring Webhook"$'\n' ;;
        8088) STATUS_REPORT+="✅ Port ${PORT}: SMS Gateway API"$'\n' ;;
        10000) STATUS_REPORT+="✅ Port ${PORT}: Webmin"$'\n' ;;
        *) STATUS_REPORT+="✅ Port ${PORT}: Active"$'\n' ;;
    esac
done

# Summary
RUNNING_COUNT=$(echo "$STATUS_REPORT" | grep -c "✅")
STOPPED_COUNT=$(echo "$STATUS_REPORT" | grep -c "❌")
WARNING_COUNT=$(echo "$STATUS_REPORT" | grep -c "⚠️")

STATUS_REPORT+=""$'\n'
STATUS_REPORT+="━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"$'\n'
STATUS_REPORT+="**📊 SUMMARY:** ✅ ${RUNNING_COUNT} Running | ❌ ${STOPPED_COUNT} Stopped | ⚠️ ${WARNING_COUNT} Warning"

# Send to VPS
echo "$STATUS_REPORT"
/home/rom/pi_send_message.sh "$STATUS_REPORT" "info"