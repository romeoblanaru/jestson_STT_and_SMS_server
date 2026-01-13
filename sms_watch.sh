#!/bin/bash
# SMS Activity Monitor with Chronological Sorting

echo "SMS Activity Monitor - Chronologically Sorted"
echo "=============================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
DARKGRAY='\033[1;30m'
ORANGE='\033[38;5;208m'
LIGHTBLUEBG='\033[104m'
BOLDWHITE='\033[1;37m'
RESET='\033[0m'

# Track last printed message
last_printed_msg=""
last_queued_number=""

# Buffer file for sorting
BUFFER_FILE="/tmp/sms_watch_buffer_$$"
> "$BUFFER_FILE"
trap "rm -f $BUFFER_FILE" EXIT

# Process and buffer messages
process_buffer() {
    if [[ -s "$BUFFER_FILE" ]]; then
        # Sort by timestamp and display
        sort "$BUFFER_FILE" | cut -d'|' -f2- | while IFS= read -r msg; do
            if [[ -n "$msg" ]] && [[ "$msg" != "$last_printed_msg" ]]; then
                echo -e "$msg"
                last_printed_msg="$msg"
            fi
        done
        > "$BUFFER_FILE"
    fi
}

# Start buffer flush every 0.3 seconds in background
(while true; do sleep 0.3; touch "$BUFFER_FILE.flush"; done) &
FLUSHER_PID=$!
trap "kill $FLUSHER_PID 2>/dev/null; rm -f $BUFFER_FILE $BUFFER_FILE.flush" EXIT

# Tail unified API logs, SMS gateway logs, and SMSTools logs
tail -f /var/log/voice_bot_ram/unified_api.log /var/log/voice_bot_ram/sms_gateway.log /var/log/smstools/smsd.log 2>/dev/null | while IFS= read -r line; do
    # Extract timestamp from log line (format: 2026-01-08 14:27:29,xxx)
    if [[ "$line" =~ ([0-9]{4}-[0-9]{2}-[0-9]{2}[[:space:]][0-9]{2}:[0-9]{2}:[0-9]{2}) ]]; then
        full_timestamp="${BASH_REMATCH[1]}"
        time=$(echo "$full_timestamp" | cut -d' ' -f2)
    else
        full_timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        time=$(date '+%H:%M:%S')
    fi
    msg=""
    
    # INCOMING SMS (from eventhandler log) - DISABLED to avoid duplicates
    # if [[ "$line" =~ "SMS received from" ]]; then
    #     from=$(echo "$line" | sed -n 's/.*SMS received from \([^:]*\):.*/\1/p')
    #     msg_content=$(echo "$line" | sed -n 's/.*SMS received from [^:]*: \(.*\)/\1/p' | cut -c1-50)
    #     msg="[$time] ${BLUE}← IN${RESET} from ${YELLOW}$from${RESET} ${DARKGRAY}\"${msg_content}...\"${RESET}"

    # INCOMING SMS (from SMSTools directly)
    if [[ "$line" =~ "SMS received, From:" ]]; then
        from=$(echo "$line" | sed -n 's/.*From: \(.*\)/\1/p' | xargs)

        # Distinguish system messages from regular messages
        if [[ "$from" == "VODAFONE" ]] || [[ "$from" =~ ^[A-Z]+$ ]]; then
            msg="[$time] ${CYAN}← SYSTEM${RESET} from ${YELLOW}$from${RESET}"
        else
            msg="[$time] ${LIGHTBLUEBG} → IN ${RESET} from ${YELLOW}$from${RESET}"
        fi

        # Read message body from the most recent incoming file
        sleep 0.2  # Brief delay to ensure file is written
        latest_sms=$(ls -t /var/spool/sms/incoming/GSM1.* 2>/dev/null | head -1)
        if [[ -f "$latest_sms" ]]; then
            # Check if this file is from the sender we just detected
            if sudo grep -q "From: ${from}" "$latest_sms" 2>/dev/null; then
                msg_body=$(sudo awk '/^$/{p=1;next} p' "$latest_sms" 2>/dev/null | head -20 | tr '\n' ' ')
                if [[ -n "$msg_body" ]]; then
                    # Print the message on the same event
                    echo -e "$msg"
                    msg="[$time] ${MAGENTA}  ↳ Message:${RESET} ${DARKGRAY}\"${msg_body}\"${RESET}"
                fi
            fi
        fi

    # SMS sent - Log entry shows the sent message
    elif [[ "$line" =~ "SMS sent" ]] && [[ "$line" =~ "Message_id:" ]]; then
        number=$(echo "$line" | grep -oE 'To: [0-9+]+' | sed 's/To: //')
        message_id=$(echo "$line" | grep -oE 'Message_id: [0-9]+' | sed 's/Message_id: //')

        # Print the first line
        msg="[$time] ${ORANGE}← OUT${RESET} to ${YELLOW}$number${RESET} via Vodafone"

        # Find the actual sent file and read its content
        sleep 0.1  # Brief delay to ensure file is moved to sent/
        sent_file=$(ls -t /var/spool/sms/sent/*${message_id}* 2>/dev/null | head -1)

        if [[ -z "$sent_file" ]]; then
            # Fallback: try to find by number and timestamp
            sent_file=$(ls -t /var/spool/sms/sent/ 2>/dev/null | grep -E "api_.*_${number##+}" | head -1)
        fi

        # Use API log for message content (cleaner, handles UCS2 properly)
        # Match by timestamp proximity and number
        msg_content=""

        # Detect if this is a multipart message
        part_label=""
        if [[ -f "$sent_file" ]] && [[ "$sent_file" =~ _part([0-9]+) ]]; then
            part_num="${BASH_REMATCH[1]}"
            part_label="Part ${part_num}: "

            # Find the specific part in API log
            msg_content=$(grep "SMS queued:.*${number}.*Part ${part_num}/" /var/log/voice_bot_ram/unified_api.log 2>/dev/null | tail -1 | sed -n 's/.*Part [0-9]*\/[0-9]* - \(.*\) (Unicode:.*/\1/p')
        fi

        # If not found or not multipart, get the most recent message for this number
        if [[ -z "$msg_content" ]]; then
            msg_content=$(grep "SMS queued:.*${number}" /var/log/voice_bot_ram/unified_api.log 2>/dev/null | tail -1 | sed -n 's/.*- \(.*\) (Unicode:.*/\1/p')
        fi

        # Limit to 60 chars for display
        if [[ -n "$msg_content" ]]; then
            msg_content="${part_label}${msg_content:0:60}"
        fi

        if [[ -n "$msg_content" ]]; then
            # Print the OUT line first
            echo -e "$msg"
            # Then print the message content on a second line
            msg="[$time] ${MAGENTA}  ↳ Message:${RESET} ${DARKGRAY}\"${msg_content}...\"${RESET}"
        fi
        
    # VPS forwarding status - SUCCESS
    elif [[ "$line" =~ "Successfully forwarded to VPS" ]]; then
        msg="[$time] ${GREEN}↑ MSG${RESET} - successfully sent to VPS"

    # VPS forwarding status - ERRORS
    elif [[ "$line" =~ "Failed to forward to VPS" ]] || [[ "$line" =~ "Connection refused" ]] || [[ "$line" =~ "Request timeout" ]] || [[ "$line" =~ "VPS webhook service down" ]]; then
        error_msg=$(echo "$line" | sed -n 's/.*: \(.*\)/\1/p' | head -c 50)
        if [[ -z "$error_msg" ]]; then
            error_msg="VPS not responding"
        fi
        msg="[$time] ${RED}✗ ERROR${RESET} - VPS down - ${RED}${error_msg}${RESET}"

    # MODEM ERROR
    elif [[ "$line" =~ "The modem answer was not OK" ]] && [[ "$line" =~ "CMS ERROR" ]]; then
        error=$(echo "$line" | grep -oE 'CMS ERROR: [^$]+' || echo "Unknown error")
        msg="[$time] ${RED}✗ MODEM ERROR${RESET} to  - ${RED}$error${RESET}"

    # FAILED SMS - Moved to failed directory
    elif [[ "$line" =~ "Moved file".*/var/spool/sms/checked/.*"to /var/spool/sms/failed/" ]]; then
        recipient=$(echo "$line" | grep -oE 'To: [0-9+]+' | sed 's/To: //')
        filename=$(echo "$line" | grep -oE 'failed/[^ ]+' | sed 's|failed/||')
        if [[ -z "$recipient" ]]; then
            recipient="unknown"
        fi
        msg="[$time] ${RED}✗✗ SEND FAILED${RESET} to ${YELLOW}$recipient${RESET} - moved to ${RED}failed/${RESET} (${filename})"

    # Webhook received
    elif [[ "$line" =~ "POST /send" ]] && [[ "$line" =~ "10.100.0.1" ]]; then
        msg="[$time] ${GREEN}↓ RECEIVED${RESET} message from VPS"
        
    # SMS queued via API - COMMENTED OUT (can be re-enabled if needed)
    # elif [[ "$line" =~ "SMS queued:" ]]; then
    #     recipient=$(echo "$line" | grep -oE '\+?[0-9]{10,}' | head -1)
    #     # Extract message content after "SMS queued: +number - "
    #     msg_preview=$(echo "$line" | sed -n 's/.*SMS queued: [+0-9]* - \(.*\) (Unicode:.*/\1/p' | cut -c1-60)
    #     if [[ -z "$msg_preview" ]]; then
    #         # Fallback for non-unicode messages
    #         msg_preview=$(echo "$line" | sed -n 's/.*SMS queued: [+0-9]* - \(.*\)/\1/p' | cut -c1-60)
    #     fi
    #     msg="[$time] ${GREEN}✓ QUEUED${RESET} for ${CYAN}$recipient${RESET} ${DARKGRAY}\"${msg_preview}...\"${RESET}"
    fi
    
    # Buffer message with full timestamp for sorting
    if [[ -n "$msg" ]]; then
        echo "${full_timestamp}|${msg}" >> "$BUFFER_FILE"
    fi

    # Check if it's time to flush buffer
    if [[ -f "$BUFFER_FILE.flush" ]]; then
        rm -f "$BUFFER_FILE.flush"
        process_buffer
    fi
done
