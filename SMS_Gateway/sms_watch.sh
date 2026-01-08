#!/bin/bash
# Enhanced SMS watcher - shows all activity including rejected messages
# Now with international SMS failure detection

echo "SMS Activity Monitor v3 - International SMS Tracking"
echo "====================================================="
echo ""

# Clean up old tracking file on startup
if [[ -f /tmp/sms_sent_tracking.tmp ]]; then
    # Keep only last 100 entries
    tail -100 /tmp/sms_sent_tracking.tmp > /tmp/sms_sent_tracking.new 2>/dev/null
    mv /tmp/sms_sent_tracking.new /tmp/sms_sent_tracking.tmp 2>/dev/null
fi

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
GRAY='\033[0;90m'
DARKGRAY='\033[1;30m'
RESET='\033[0m'

# Simple deduplication - track last printed message
last_printed_message=""

# Track last queued phone number for CMS ERROR correlation
last_queued_number=""

# Function to format timestamp
format_time() {
    date '+%H:%M:%S'
}

# Function to print only if message is different from last one
print_if_new() {
    local msg="$1"
    if [[ "$msg" != "$last_printed_message" ]]; then
        echo -e "$msg"
        last_printed_message="$msg"
    fi
}

# Monitor incoming directory for new SMS
monitor_incoming() {
    inotifywait -m -e create /var/spool/sms/incoming 2>/dev/null | while read path event file; do
        if [[ "$file" =~ GSM ]]; then
            sleep 0.5  # Let file be written completely
            time=$(format_time)
            # Read the SMS file
            from=$(sudo grep "^From:" "/var/spool/sms/incoming/$file" 2>/dev/null | cut -d' ' -f2-)
            message=$(sudo sed '1,/^$/d' "/var/spool/sms/incoming/$file" 2>/dev/null | head -1)
            if [[ -n "$from" ]] && [[ -n "$message" ]]; then
                echo -e "[$time] ← IN  from $from: ${CYAN}${message}${RESET}"
            fi
        fi
    done
}

# If inotifywait not available, use polling method
if ! command -v inotifywait &> /dev/null; then
    echo "Note: Install inotify-tools for better performance (sudo apt-get install inotify-tools)"
    echo ""
fi

# Monitor multiple sources in parallel
(
    # Monitor incoming SMS files directly
    monitor_incoming 2>/dev/null || while true; do
        for file in /var/spool/sms/incoming/GSM*; do
            if [[ -f "$file" ]] && [[ ! -f "/tmp/seen_$(basename $file)" ]]; then
                touch "/tmp/seen_$(basename $file)"
                time=$(format_time)
                from=$(sudo grep "^From:" "$file" 2>/dev/null | cut -d' ' -f2-)
                message=$(sudo sed '1,/^$/d' "$file" 2>/dev/null | tr '\n' ' ' | head -c 100)
                if [[ -n "$from" ]] && [[ -n "$message" ]]; then
                    echo -e "[$time] ← IN  from $from: ${CYAN}${message}${RESET}"
                fi
            fi
        done
        sleep 2
    done
) &

# Monitor logs for all events (including API service)
(sudo tail -f /var/log/smstools/smsd.log /var/log/sms_gateway.log 2>/dev/null & sudo journalctl -u sms-api -f 2>/dev/null) | \
while IFS= read -r line; do
    time=$(format_time)
    
    # SMS Rejection (Invalid numbers)
    if [[ "$line" =~ "SMS REJECTED" ]]; then
        reason=$(echo "$line" | grep -oE 'Reason: [^-]+' | sed 's/Reason: //')
        number=$(echo "$line" | grep -oE 'To: [^ ]+' | sed 's/To: //')
        message=$(echo "$line" | grep -oE 'Message: .+' | sed 's/Message: //')

        msg_key="REJECTED:$number:$reason"
        if should_print "$msg_key"; then
            echo -e "[$time] ✗ ${RED}REJECTED${RESET} to ${YELLOW}$number${RESET} - ${RED}$reason${RESET}"
            if [[ -n "$message" ]]; then
                echo -e "           Message: ${WHITE}$message${RESET}"
            fi
        fi

    # SMS Accepted
    elif [[ "$line" =~ "SMS ACCEPTED" ]]; then
        number=$(echo "$line" | grep -oE 'To: [^ ]+' | sed 's/To: //')
        message=$(echo "$line" | grep -oE 'Message: .+' | sed 's/Message: //')

        msg_key="ACCEPTED:$number"
        if should_print "$msg_key"; then
            echo -e "[$time] ✓ ${GREEN}ACCEPTED${RESET} to $number"
            if [[ -n "$message" ]]; then
                echo -e "           Message: ${WHITE}$message${RESET}"
            fi
        fi
    
    # Server response queued for outgoing (ALWAYS track the number, even if deduplicated)
    elif [[ "$line" =~ "SMS To:" ]] && [[ "$line" =~ "Moved file" ]]; then
        to=$(echo "$line" | grep -oE 'To: [0-9+]+' | sed 's/To: //')
        file=$(echo "$line" | grep -oE 'api_[0-9]+_[0-9]+')

        # ALWAYS store this number for CMS ERROR correlation (even if message is deduplicated)
        last_queued_number="$to"

        msg_key="QUEUED:$to:$file"
        if should_print "$msg_key"; then
            echo -e "[$time] ${BLUE}↓ SERVER REPLY${RESET} queued for ${YELLOW}$to${RESET} (file: $file)"
        fi
    
    # CMS ERROR 500 - Failed to send (often due to number format issues)
    elif [[ "$line" =~ "The modem answer was not OK" ]] && [[ "$line" =~ "CMS ERROR" ]]; then
        error=$(echo "$line" | grep -oE 'CMS ERROR: [^$]+' || echo "Unknown error")

        # Create dedup key from error type
        msg_key="MODEM_ERROR:$error"

        if should_print "$msg_key"; then
            echo -e "[$time] ${RED}✗ MODEM ERROR${RESET} to  - ${RED}$error${RESET}"

            # Add phone number context if we have it from previous "SMS To:" line
            if [[ -n "$last_queued_number" ]]; then
                if [[ "$last_queued_number" =~ ^0[0-9]{10}$ ]]; then
                    # UK local format without country code - THIS IS THE ISSUE!
                    echo -e "           ${YELLOW}Error due to possible phone nr issue: ${last_queued_number} should be +44${last_queued_number:1}${RESET}"
                else
                    echo -e "           Error due to possible phone nr issue: ${last_queued_number}"
                fi
            fi
        fi
    
    # Outgoing SMS sent successfully
    elif [[ "$line" =~ "SMS sent" ]] && [[ "$line" =~ "Message_id:" ]]; then
        number=$(echo "$line" | grep -oE 'To: [0-9+]+' | sed 's/To: //')
        msg_id=$(echo "$line" | grep -oE 'Message_id: [0-9]+' | grep -oE '[0-9]+')
        send_time=$(echo "$line" | grep -oE 'sending time [0-9]+' | grep -oE '[0-9]+')

        # Dedup key
        msg_key="SMS_SENT:$number:$msg_id"

        if should_print "$msg_key"; then
            # Create unique ID using timestamp and Message_id
            unique_id="$(date +%Y%m%d%H%M%S)_${msg_id}"

            # Store mapping in temp file for tracking
            echo "${unique_id}:${number}:$(date +%s)" >> /tmp/sms_sent_tracking.tmp

            # Try to get message content from the most recent file sent to this number
            # Look only at files modified in last 10 seconds
            current_time=$(date +%s)
            msg_content=""

            # Find the most recent file for this number
            for sent_file in $(sudo ls -t /var/spool/sms/sent/ 2>/dev/null | head -5); do
                file_path="/var/spool/sms/sent/$sent_file"
                if [[ -f "$file_path" ]]; then
                    file_time=$(stat -c %Y "$file_path" 2>/dev/null)
                    time_diff=$((current_time - file_time))

                    # Only check very recent files (10 seconds)
                    if [[ $time_diff -lt 10 ]]; then
                        # Check if this file is for our phone number
                        if sudo grep -q "To:.*${number}" "$file_path" 2>/dev/null; then
                            # Use strings to handle binary UTF-16-BE files (no null byte warnings)
                            msg_content=$(sudo strings "$file_path" 2>/dev/null | tail -1 | cut -c1-50)
                            break
                        fi
                    fi
                fi
            done

            if [[ -n "$msg_content" ]]; then
                print_if_new "[$time] ${GREEN}→ OUT${RESET} to ${CYAN}$number${RESET} (UID: ${unique_id}) ${DARKGRAY}\"${msg_content}...\"${RESET}"
            else
                print_if_new "[$time] ${GREEN}→ OUT${RESET} to ${CYAN}$number${RESET} (UID: ${unique_id})"
            fi
        fi
    
    # SMS Failed after retries
    elif [[ "$line" =~ "Sending SMS.*failed.*Retries:" ]]; then
        to=$(echo "$line" | grep -oE 'to [^ ]+' | sed 's/to //')
        retries=$(echo "$line" | grep -oE 'Retries: [0-9]+' | sed 's/Retries: //')
        time_taken=$(echo "$line" | grep -oE 'trying time [0-9]+' | grep -oE '[0-9]+')

        msg_key="FAILED:$to:$retries"
        if should_print "$msg_key"; then
            echo -e "[$time] ${RED}✗ DELIVERY FAILED${RESET} to ${YELLOW}$to${RESET} after $retries retries (${time_taken}s)"
        fi
    
    # Generic SMS Failed
    elif [[ "$line" =~ "Cannot send message" ]] || [[ "$line" =~ "FAILED" ]] && [[ "$line" =~ "To:" ]]; then
        number=$(echo "$line" | grep -oE 'To: [0-9]+' | grep -oE '[0-9]+')
        error=$(echo "$line" | grep -oE 'ERROR: .+' | sed 's/ERROR: //')

        msg_key="GENERIC_FAILED:$number:$error"
        if should_print "$msg_key"; then
            echo -e "[$time] ✗ ${RED}FAILED${RESET} to $number - $error"
        fi

    # Webhook forwards - Success
    elif [[ "$line" =~ "Successfully forwarded to VPS" ]]; then
        msg_key="WEBHOOK_SUCCESS"
        if should_print "$msg_key"; then
            echo -e "[$time] ${GREEN}↗ SUCCESS${RESET} - Webhook forwarded to VPS"
        fi

    # Webhook forwards - Failed
    elif [[ "$line" =~ "Failed to forward to VPS" ]]; then
        msg_key="WEBHOOK_FAILED"
        if should_print "$msg_key"; then
            echo -e "[$time] ${RED}✗ FAILED${RESET} - Webhook forward to VPS failed"
        fi

    # Webhook connection errors
    elif [[ "$line" =~ "Failed to send to webhook" ]]; then
        error_detail=$(echo "$line" | grep -oE 'Failed to send to webhook: .+' | sed 's/Failed to send to webhook: //')

        msg_key="WEBHOOK_ERROR:$error_detail"
        if should_print "$msg_key"; then
            echo -e "[$time] ✗ ${RED}WEBHOOK ERROR:${RESET} ${YELLOW}${error_detail}${RESET}"
        fi

    # Webhook HTTP errors (non-200 responses)
    elif [[ "$line" =~ "Webhook response: [45][0-9][0-9]" ]]; then
        status=$(echo "$line" | grep -oE '[45][0-9][0-9]')
        error_msg=$(echo "$line" | grep -oE '"error":"[^"]+' | sed 's/"error":"//' | sed 's/"$//')

        msg_key="WEBHOOK_HTTP:$status"
        if should_print "$msg_key"; then
            echo -e "[$time] ✗ ${RED}WEBHOOK HTTP $status ERROR${RESET}"
            if [[ -n "$error_msg" ]]; then
                echo -e "           ${YELLOW}Error: $error_msg${RESET}"
            fi
        fi

    # Webhook retry attempts
    elif [[ "$line" =~ "Webhook attempt" ]]; then
        attempt=$(echo "$line" | grep -oE '[0-9]/[0-9]')

        msg_key="WEBHOOK_RETRY:$attempt"
        if should_print "$msg_key"; then
            echo -e "[$time] 🔄 ${YELLOW}WEBHOOK attempt $attempt${RESET}"
        fi

    # Webhook retry failed
    elif [[ "$line" =~ "Attempt.*failed:" ]]; then
        attempt=$(echo "$line" | grep -oE '[0-9]/[0-9]')
        reason=$(echo "$line" | grep -oE 'failed: .+' | sed 's/failed: //')

        msg_key="RETRY_FAILED:$attempt"
        if should_print "$msg_key"; then
            echo -e "[$time] ✗ ${RED}Attempt $attempt FAILED:${RESET} ${YELLOW}$reason${RESET}"
        fi

    # Waiting for retry
    elif [[ "$line" =~ "Waiting.*seconds before retry" ]]; then
        seconds=$(echo "$line" | grep -oE '[0-9]+ seconds' | grep -oE '[0-9]+')

        msg_key="WAITING_RETRY:$seconds"
        if should_print "$msg_key"; then
            echo -e "[$time] ⏳ ${CYAN}Waiting $seconds seconds before retry...${RESET}"
        fi

    # All retries exhausted
    elif [[ "$line" =~ "Failed to forward to VPS after" ]]; then
        attempts=$(echo "$line" | grep -oE '[0-9]+ attempts' | grep -oE '[0-9]+')

        msg_key="ALL_RETRIES_FAILED:$attempts"
        if should_print "$msg_key"; then
            echo -e "[$time] ❌ ${RED}WEBHOOK FAILED after $attempts attempts!${RESET}"
        fi

    # Failure notification sent
    elif [[ "$line" =~ "Failure notification sent" ]]; then
        msg_key="NOTIFICATION_SENT"
        if should_print "$msg_key"; then
            echo -e "[$time] 📨 ${MAGENTA}Warning notification sent${RESET}"
        fi

    # Webhook response with queued reply
    elif [[ "$line" =~ "Webhook response:.*responseQueued.*true" ]]; then
        msg_key="SERVER_REPLY_QUEUED"
        if should_print "$msg_key"; then
            echo -e "[$time] ${MAGENTA}↙ SERVER HAS REPLY${RESET} - Response queued for delivery"
        fi

    # Webhook sending attempt
    elif [[ "$line" =~ "Sending to webhook:" ]]; then
        from=$(echo "$line" | grep -oE '"from":"[^"]+' | sed 's/"from":"//' | sed 's/"$//')
        msg_preview=$(echo "$line" | grep -oE '"message":"[^"]{0,50}' | sed 's/"message":"//' | sed 's/"$//')

        msg_key="WEBHOOK_SENDING:$from"
        if should_print "$msg_key"; then
            echo -e "[$time] ↗ ${BLUE}WEBHOOK sending${RESET} from ${CYAN}$from${RESET}: ${WHITE}${msg_preview}...${RESET}"
        fi

    # API requests - webhook received by gateway
    elif [[ "$line" =~ "POST /send" ]] && [[ "$line" =~ "10.100.0.1" ]]; then
        print_if_new "[$time] ${BLUE}↓ WEBHOOK RECEIVED${RESET} - Pi gateway got request from VPS"

    # API successfully queued message
    elif [[ "$line" =~ "SMS queued:" ]]; then
        recipient=$(echo "$line" | grep -oE '\+?[0-9]{10,}' | head -1)
        msg_preview=$(echo "$line" | grep -oE ' - .+' | sed 's/ - //' | cut -c1-40)

        msg_key="API_QUEUED:$recipient"
        if should_print "$msg_key"; then
            echo -e "[$time] ${GREEN}✓ QUEUED${RESET} for ${CYAN}$recipient${RESET} ${DARKGRAY}\"${msg_preview}...\"${RESET}"
        fi

    # API Server status
    elif [[ "$line" =~ "SMS API Server" ]] && ([[ "$line" =~ "started" ]] || [[ "$line" =~ "stopped" ]]); then
        if [[ "$line" =~ "started" ]]; then
            msg_key="API_STARTED"
            if should_print "$msg_key"; then
                echo -e "[$time] 🚀 ${GREEN}SMS API Server started${RESET}"
            fi
        else
            msg_key="API_STOPPED"
            if should_print "$msg_key"; then
                echo -e "[$time] 🛑 ${YELLOW}SMS API Server stopped${RESET}"
            fi
        fi
    fi
done

# Keep script running
wait