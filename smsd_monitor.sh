#!/bin/bash
###############################################################################
# SMSD Monitor - Check if SMSD is running and restart if down
# Runs every 30 seconds via cron
###############################################################################

LOG="/var/log/smsd_monitor.log"
SMSD_LOG="/var/log/smstools/smsd.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG" 2>&1; }

# Check if SMSD daemon is actually running (not just service status)
if ! pgrep -x "smsd" > /dev/null; then
    log "WARNING: SMSD found down, attempting restart..."

    # Get last error from SMSD log
    LAST_ERROR="No specific error found"
    if [ -f "$SMSD_LOG" ]; then
        LAST_ERROR=$(tail -50 "$SMSD_LOG" | grep -i "error\|fail\|cannot\|timeout" | tail -1)
        if [ -z "$LAST_ERROR" ]; then
            LAST_ERROR=$(tail -5 "$SMSD_LOG" | tr '\n' ' ')
        fi
    fi

    # Restart SMSD
    sudo /usr/bin/systemctl start smstools 2>&1 | tee -a "$LOG"

    # Wait a moment for service to start
    sleep 2

    # Check if restart was successful
    if systemctl is-active --quiet smstools; then
        log "SUCCESS: SMSD restarted successfully"
        STATUS="SMSD restarted successfully"
    else
        log "ERROR: SMSD restart FAILED"
        STATUS="SMSD restart FAILED - manual intervention required"
    fi

    # Send notification to VPS webhook
    VPS_WEBHOOK="http://10.100.0.1:8088/webhook/sms/status"

    curl -s -X POST "$VPS_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{
            \"gateway_ip\": \"10.100.0.2\",
            \"service\": \"smstools\",
            \"status\": \"$(if systemctl is-active --quiet smstools; then echo 'restarted'; else echo 'restart_failed'; fi)\",
            \"error\": \"SMSD found down. Last error: ${LAST_ERROR:-No errors in recent logs}\",
            \"timestamp\": \"$(date -Iseconds)\"
        }" >> "$LOG" 2>&1

    # Also send via pi_send_message.sh if it exists (for backwards compatibility)
    NOTIFICATION="⚠️ WARNING: SMSD on Jetson (STT/ SMS server) found down and restart attempted

Status: $STATUS
Time: $(date '+%Y-%m-%d %H:%M:%S')

Last Error Found:
${LAST_ERROR:-No errors in recent logs}

System: Jetson Orin Nano (10.100.0.2)
"

    if [ -f /home/rom/pi_send_message.sh ]; then
        /home/rom/pi_send_message.sh "$NOTIFICATION" warning 2>&1 | tee -a "$LOG"
    fi
else
    # SMSD is running fine - log only once per hour to avoid log spam
    MINUTE=$(date '+%M')
    if [ "$MINUTE" = "00" ]; then
        log "INFO: SMSD health check - running OK"
    fi
fi

exit 0
