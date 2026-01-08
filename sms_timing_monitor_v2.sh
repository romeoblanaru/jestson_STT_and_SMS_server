#!/bin/bash
# SMS Timing Monitor V2 - Enhanced with error tracking and ME storage issues
# Monitors both delays and errors in SMS processing

YELLOW='\033[1;33m'
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "SMS Timing Monitor V2 - Real-time Delay & Error Tracking"
echo "========================================================="
echo ""
echo -e "${YELLOW}Monitoring for:${NC}"
echo "  • SMS send/receive delays (ME storage issue)"
echo "  • CMS ERROR messages (modem errors)"
echo "  • CMTI interruptions"
echo "  • Memory storage issues"
echo ""
echo -e "${BLUE}Starting monitoring...${NC}"
echo ""

# Track timing
declare -A receive_times
declare -A send_times

# Function to format timestamp
format_time() {
    date '+%H:%M:%S'
}

# Monitor main logs
tail -f /var/log/smstools/smsd.log /var/log/voice_bot_ram/*.log 2>/dev/null | while IFS= read -r line; do
    current_time=$(format_time)

    # CMS ERROR detection - CRITICAL
    if [[ "$line" =~ "CMS ERROR" ]] || [[ "$line" =~ "+CMS ERROR" ]]; then
        echo -e "${RED}[$current_time] ⚠️  MODEM ERROR DETECTED!${NC}"
        echo -e "${RED}    Error: ${line}${NC}"
        echo "    Possible causes:"
        echo "      - ME storage full or corrupt"
        echo "      - SIM card issue"
        echo "      - Network registration lost"
        echo "      - Memory access timeout"
        echo ""
    fi

    # CMTI notification (interruption)
    if [[ "$line" =~ "+CMTI:" ]]; then
        echo -e "${YELLOW}[$current_time] 🔔 CMTI Notification (potential interruption)${NC}"
        echo "    $line"
    fi

    # Incoming SMS received
    if [[ "$line" =~ "SMS received, From:" ]]; then
        sender=$(echo "$line" | grep -oE 'From: [0-9+]+' | cut -d' ' -f2)
        receive_times[$sender]=$(date +%s)
        echo -e "${GREEN}[$current_time] 📱 SMS RECEIVED${NC}"
        echo "    From: $sender"
        echo "    Stage 1: Network → Modem (ME storage)"
    fi

    # SMS processing/forwarding
    if [[ "$line" =~ "Processing incoming SMS" ]]; then
        echo "    Stage 2: Modem → SMSTools processing"
    fi

    # Webhook forwarding
    if [[ "$line" =~ "Webhook attempt" ]] || [[ "$line" =~ "Forwarding to VPS" ]]; then
        echo "    Stage 3: SMSTools → VPS webhook"
    fi

    # Webhook success
    if [[ "$line" =~ "Successfully forwarded" ]]; then
        # Extract sender if possible
        if [[ "$line" =~ "from \+?([0-9]+)" ]]; then
            sender="${BASH_REMATCH[1]}"
            if [[ -n "${receive_times[$sender]}" ]]; then
                end_time=$(date +%s)
                total_delay=$((end_time - receive_times[$sender]))
                echo -e "    ${GREEN}✓ Webhook completed${NC}"
                echo -e "    ${BLUE}📊 Total receive latency: ${total_delay} seconds${NC}"
                unset receive_times[$sender]
            fi
        fi
    fi

    # Outgoing SMS queued
    if [[ "$line" =~ "SMS To:" ]] && [[ "$line" =~ "Moved file.*outgoing.*checked" ]]; then
        recipient=$(echo "$line" | grep -oE 'To: \+?[0-9]+' | grep -oE '[0-9]+$')
        send_times[$recipient]=$(date +%s)
        echo -e "${BLUE}[$current_time] 📤 OUTGOING SMS QUEUED${NC}"
        echo "    To: $recipient"
        echo "    Stage 1: API → SMSTools queue"
    fi

    # Outgoing SMS being sent
    if [[ "$line" =~ "Sending SMS" ]] && [[ ! "$line" =~ "failed" ]]; then
        echo "    Stage 2: SMSTools → Modem (AT+CMGS)"
    fi

    # SMS sent successfully
    if [[ "$line" =~ "SMS sent" ]] && [[ "$line" =~ "sending time" ]]; then
        recipient=$(echo "$line" | grep -oE 'To: \+?[0-9]+' | grep -oE '[0-9]+$')
        modem_time=$(echo "$line" | grep -oE 'sending time [0-9]+' | grep -oE '[0-9]+')

        if [[ -n "${send_times[$recipient]}" ]]; then
            end_time=$(date +%s)
            total_delay=$((end_time - send_times[$recipient]))
            echo -e "    ${GREEN}✓ SMS sent successfully${NC}"
            echo "    Modem processing: ${modem_time}s"
            echo -e "    ${BLUE}📊 Total send latency: ${total_delay} seconds${NC}"

            # Alert if delay is excessive
            if [[ $total_delay -gt 60 ]]; then
                echo -e "    ${RED}⚠️  WARNING: Excessive delay (>60s) - likely ME storage issue${NC}"
            fi

            unset send_times[$recipient]
        else
            echo -e "    ${GREEN}✓ SMS sent (modem time: ${modem_time}s)${NC}"
        fi
        echo ""
    fi

    # SMS send failed
    if [[ "$line" =~ "Sending SMS.*failed" ]] || [[ "$line" =~ "FAILED" ]]; then
        echo -e "${RED}    ✗ SMS SEND FAILED${NC}"
        echo "    Check modem status and ME storage"
        recipient=$(echo "$line" | grep -oE 'to [0-9]+' | grep -oE '[0-9]+')
        unset send_times[$recipient]
        echo ""
    fi

    # Memory/storage issues
    if [[ "$line" =~ "CPMS" ]]; then
        if [[ "$line" =~ '"ME"' ]]; then
            # Extract ME storage usage
            if [[ "$line" =~ \"ME\",([0-9]+),([0-9]+) ]]; then
                used="${BASH_REMATCH[1]}"
                total="${BASH_REMATCH[2]}"
                if [[ $used -gt 20 ]]; then
                    echo -e "${YELLOW}[$current_time] ⚠️  ME Storage: $used/$total (getting full)${NC}"
                fi
            fi
        fi
    fi

    # API errors
    if [[ "$line" =~ "MODEM_ERROR" ]] || [[ "$line" =~ "Modem communication failed" ]]; then
        echo -e "${RED}[$current_time] 🚨 API MODEM ERROR${NC}"
        echo "    SMS API couldn't communicate with modem"
        echo "    Check: smstools service, modem connection, USB ports"
        echo ""
    fi
done