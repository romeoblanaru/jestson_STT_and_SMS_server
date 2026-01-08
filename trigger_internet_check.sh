#!/bin/bash
################################################################################
# Trigger Priority Internet Check
# Called by voice bot or SMS system when call/SMS arrives
# Signals internet monitor to check immediately and start PPP if needed
################################################################################

SIGNAL_FILE="/tmp/internet_check_priority"
REASON="${1:-Call/SMS arrived}"

# Create signal file with reason
echo "$REASON" > "$SIGNAL_FILE"

# Log the trigger
logger -t internet-check "Priority check triggered: $REASON"

# Exit successfully
exit 0
