#!/bin/bash
# SMS Timing Monitor - Real-time tracking of SMS delays and errors

echo "SMS Timing Monitor - Tracking send/receive delays"
echo "================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Monitor logs
tail -f /var/log/smstools/smsd.log | while read line; do
    timestamp=$(date '+%H:%M:%S')

    # Track CMS ERRORS (MODEM ERRORS)
    if [[ "$line" =~ "CMS ERROR" ]]; then
        echo -e "${RED}[$timestamp] ❌ MODEM ERROR:${NC}"
        echo "    $line"
        # Extract phone number if present
        if [[ "$line" =~ "to ([0-9+]+)" ]]; then
            number="${BASH_REMATCH[1]}"
            echo -e "    ${YELLOW}Number: $number${NC}"
            # Check if number lacks country code
            if [[ "$number" =~ ^0[0-9]{9,10}$ ]]; then
                echo -e "    ${RED}⚠️  Missing country code! Should be +44${number:1}${NC}"
            fi
        fi
        echo ""
    fi

    # Track successful SMS sends
    if [[ "$line" =~ "SMS sent" ]] && [[ "$line" =~ "Message_id" ]]; then
        number=$(echo "$line" | grep -oE 'To: [0-9+]+' | cut -d' ' -f2)
        time=$(echo "$line" | grep -oE 'sending time [0-9]+' | grep -oE '[0-9]+')
        echo -e "${GREEN}[$timestamp] ✅ SMS SENT${NC}"
        echo "    To: $number"
        echo "    Modem time: ${time}s"
        echo ""
    fi

    # Track incoming SMS
    if [[ "$line" =~ "SMS received" ]]; then
        from=$(echo "$line" | grep -oE 'From: [0-9+]+' | cut -d' ' -f2)
        echo -e "${GREEN}[$timestamp] 📱 SMS RECEIVED${NC}"
        echo "    From: $from"
        echo ""
    fi

    # Track SMS queue
    if [[ "$line" =~ "Moved file.*outgoing.*checked" ]]; then
        to=$(echo "$line" | grep -oE 'To: [0-9+]+' | cut -d' ' -f2)
        echo "[$timestamp] 📤 Queued for sending to: $to"
    fi

    # Track retries
    if [[ "$line" =~ "Waiting.*before retrying" ]]; then
        echo -e "${YELLOW}    Retrying...${NC}"
    fi

    # Track failures
    if [[ "$line" =~ "failed.*Retries:" ]]; then
        echo -e "${RED}    Failed after retries - moved to failed queue${NC}"
        echo ""
    fi
done