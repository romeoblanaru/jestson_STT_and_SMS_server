#!/bin/bash
# SMSTools call eventhandler - triggered on RING
# Stops SMS service and starts voice bot to handle the call

EVENT_TYPE="$1"
CALLER_NUMBER="$2"
DEVICE="$3"

LOGFILE="/var/log/voice_bot/call_handoff.log"

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOGFILE"
}

log_message "============================================"
log_message "Incoming call detected!"
log_message "Event: $EVENT_TYPE"
log_message "Caller: $CALLER_NUMBER"
log_message "Device: $DEVICE"

# CRITICAL: Stop SMSTools immediately to release serial port
log_message "Stopping SMSTools to hand over serial port..."
sudo systemctl stop smstools

if [ $? -eq 0 ]; then
    log_message "✅ SMSTools stopped successfully"
    sleep 1  # Give port time to be released

    # Start voice bot in call-handling mode (one-shot)
    log_message "Starting voice bot to handle call from $CALLER_NUMBER..."

    # Run voice bot in background to handle this specific call
    # Voice bot will restart SMSTools when call ends
    /usr/bin/python3 /home/rom/sim7600_voice_bot_session.py "$CALLER_NUMBER" >> "$LOGFILE" 2>&1 &

    log_message "Voice bot started (PID: $!)"
else
    log_message "❌ ERROR: Failed to stop SMSTools"
fi

log_message "Eventhandler completed"
