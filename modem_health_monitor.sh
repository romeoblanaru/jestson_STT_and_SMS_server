#!/bin/bash
###############################################################################
# Professional Modem Health Monitor
# Detects modem I/O errors, port contention, and auto-recovers
###############################################################################

LOG="/var/log/modem_health_monitor.log"
ALERT_LOG="/var/log/modem_alerts.log"
SMSD_LOG="/var/log/smstools/smsd.log"
MODEM_PORT="/dev/ttyUSB2"
ERROR_THRESHOLD=5
CHECK_INTERVAL=30

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

alert() {
    local severity="$1"
    shift
    local message="$*"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$severity] $message" | tee -a "$ALERT_LOG"

    # Send notification to VPS
    if [ -f /home/rom/pi_send_message.sh ]; then
        /home/rom/pi_send_message.sh "🚨 Modem Alert [$severity]

$message

System: Jetson (10.100.0.2)
Time: $(date '+%Y-%m-%d %H:%M:%S')" "error" >> "$LOG" 2>&1
    fi
}

check_io_errors() {
    # Count recent I/O errors in SMSD log (last 2 minutes)
    local error_count=$(tail -100 "$SMSD_LOG" 2>/dev/null | \
        grep -c "write_to_modem: error 5: Input/output error")

    if [ "$error_count" -ge "$ERROR_THRESHOLD" ]; then
        alert "CRITICAL" "Modem I/O errors detected: $error_count errors in recent logs. Modem may be hung."
        return 1
    fi
    return 0
}

check_port_contention() {
    # Check if multiple processes are accessing the modem
    local processes=$(lsof "$MODEM_PORT" 2>/dev/null | tail -n +2 | wc -l)

    if [ "$processes" -gt 1 ]; then
        local process_list=$(lsof "$MODEM_PORT" 2>/dev/null | tail -n +2 | awk '{print $1":"$2}')
        alert "WARNING" "Port contention detected: $processes processes accessing $MODEM_PORT
Processes: $process_list"
        return 1
    fi
    return 0
}

check_smsd_status() {
    if ! systemctl is-active --quiet smstools; then
        alert "CRITICAL" "SMSD is not running!"
        return 1
    fi

    # Check if SMSD is in error loop
    local recent_errors=$(tail -50 "$SMSD_LOG" 2>/dev/null | \
        grep -c "write_to_modem: error")

    if [ "$recent_errors" -gt 10 ]; then
        alert "ERROR" "SMSD in error loop: $recent_errors write errors in last 50 log lines"
        return 1
    fi

    return 0
}

check_unprocessed_sms() {
    local incoming_count=$(ls /var/spool/sms/incoming/ 2>/dev/null | wc -l)

    if [ "$incoming_count" -gt 10 ]; then
        alert "WARNING" "High number of unprocessed SMS: $incoming_count messages in incoming folder. Eventhandler may not be running."
        return 1
    fi
    return 0
}

check_modem_responsiveness() {
    # Quick AT test (without stopping SMSD - just check if port responds)
    timeout 2 bash -c "echo -e 'AT\r' > $MODEM_PORT 2>/dev/null" 2>/dev/null
    local result=$?

    if [ $result -ne 0 ]; then
        alert "ERROR" "Modem port $MODEM_PORT is not responsive (AT command failed)"
        return 1
    fi
    return 0
}

recover_modem() {
    log "=== Starting modem recovery procedure ==="

    # Stop SMSD
    log "Stopping SMSD..."
    sudo /usr/bin/systemctl stop smstools 2>&1 | tee -a "$LOG"
    sleep 3

    # Check if port is still locked
    local locks=$(fuser "$MODEM_PORT" 2>&1 | grep -v "Cannot stat")
    if [ -n "$locks" ]; then
        log "WARNING: Port still locked by: $locks"
    fi

    # Try AT command reset
    log "Attempting AT command reset..."
    timeout 5 bash -c "
        echo -e 'ATZ\r' > $MODEM_PORT
        sleep 1
        echo -e 'AT+CFUN=1,1\r' > $MODEM_PORT
    " 2>&1 | tee -a "$LOG"

    sleep 5

    # Restart SMSD
    log "Restarting SMSD..."
    sudo /usr/bin/systemctl start smstools 2>&1 | tee -a "$LOG"
    sleep 3

    # Verify recovery
    if systemctl is-active --quiet smstools; then
        log "SMSD restarted successfully"
        alert "INFO" "Modem recovery completed successfully"
        return 0
    else
        alert "CRITICAL" "Modem recovery FAILED - SMSD did not start"
        return 1
    fi
}

# Main monitoring loop
log "=== Modem Health Monitor Started ==="
log "Monitoring interval: ${CHECK_INTERVAL}s"
log "Error threshold: $ERROR_THRESHOLD I/O errors"

CONSECUTIVE_FAILURES=0
MAX_FAILURES=3

while true; do
    HEALTH_OK=true

    # Run all health checks
    check_smsd_status || HEALTH_OK=false
    check_io_errors || HEALTH_OK=false
    check_port_contention || HEALTH_OK=false
    check_unprocessed_sms || HEALTH_OK=false

    if [ "$HEALTH_OK" = false ]; then
        CONSECUTIVE_FAILURES=$((CONSECUTIVE_FAILURES + 1))
        log "Health check failed (attempt $CONSECUTIVE_FAILURES/$MAX_FAILURES)"

        if [ "$CONSECUTIVE_FAILURES" -ge "$MAX_FAILURES" ]; then
            alert "CRITICAL" "Multiple consecutive health check failures. Initiating automatic recovery."
            recover_modem
            CONSECUTIVE_FAILURES=0
        fi
    else
        if [ "$CONSECUTIVE_FAILURES" -gt 0 ]; then
            log "Health check passed after previous failures. Resetting counter."
        fi
        CONSECUTIVE_FAILURES=0
    fi

    sleep "$CHECK_INTERVAL"
done
