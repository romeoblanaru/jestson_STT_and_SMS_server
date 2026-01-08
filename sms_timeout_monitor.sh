#!/bin/bash
# SMS Timeout Monitor - Prevents modem blockage from international SMS failures
# Monitors for "The modem answer was not OK" pattern and intervenes

LOG_FILE="/var/log/smstools/smsd.log"
CHECK_INTERVAL=15  # Check every 15 seconds
INTERVENTION_THRESHOLD=30  # Intervene after 30 seconds of no response

last_error_time=0
error_phone_number=""

monitor_loop() {
    tail -f "$LOG_FILE" | while IFS= read -r line; do
        # Detect "modem answer was not OK" (blank response)
        if [[ "$line" =~ "The modem answer was not OK: " ]] && [[ "$line" =~ "GSM1" ]]; then
            # Extract timestamp
            timestamp=$(echo "$line" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}')
            current_time=$(date +%s)
            
            # Check if this is a blank response (no error message)
            if [[ ! "$line" =~ "ERROR:" ]]; then
                echo "[$(date '+%H:%M:%S')] ⚠️  Modem not responding - blank AT response detected"
                last_error_time=$current_time
                
                # Extract phone number from recent context
                phone=$(tail -20 "$LOG_FILE" | grep "SMS To:" | tail -1 | grep -oE 'To: [0-9+]+' | sed 's/To: //')
                error_phone_number="$phone"
                
                # Check if international number
                if [[ "$phone" =~ ^\+3[0-9]{10,}$ ]] || [[ "$phone" =~ ^3[0-9]{10,}$ ]]; then
                    echo "[$(date '+%H:%M:%S')] 🌍 International number detected: $phone - monitoring for timeout"
                fi
            fi
        fi
        
        # Detect "Modem is not ready" with timeout count
        if [[ "$line" =~ "Modem is not ready to answer commands" ]] && [[ "$line" =~ "Timeouts:" ]]; then
            timeout_count=$(echo "$line" | grep -oE 'Timeouts: [0-9]+' | grep -oE '[0-9]+')
            phone=$(tail -50 "$LOG_FILE" | grep "SMS To:" | tail -1 | grep -oE 'To: [0-9+]+' | sed 's/To: //')
            
            echo "[$(date '+%H:%M:%S')] 🚨 MODEM TIMEOUT: $timeout_count timeouts detected for $phone"
            
            # If timeouts > 10, SMSTools will handle it, but notify VPS immediately
            if [[ $timeout_count -gt 10 ]]; then
                /home/rom/pi_send_message.sh "⚠️ Modem Timeout Alert: $timeout_count timeouts on $phone. SMSTools will auto-restart soon." "warning" &
            fi
        fi
        
        # Detect successful recovery
        if [[ "$line" =~ "SMS sent" ]]; then
            if [[ $last_error_time -gt 0 ]]; then
                recovery_time=$(($(date +%s) - last_error_time))
                echo "[$(date '+%H:%M:%S')] ✅ Modem recovered after ${recovery_time}s"
                last_error_time=0
                error_phone_number=""
            fi
        fi
    done
}

echo "SMS Timeout Monitor started - monitoring modem responsiveness"
echo "Will detect blank AT responses and international SMS timeouts"
echo "=============================================================="
monitor_loop
