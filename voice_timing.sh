#!/bin/bash
# Voice Call Timing Analysis Display
# Reads profiler JSON data and displays formatted timing analysis

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to format numbers with dot separator for thousands
format_number() {
    local num=$1
    if [ "$num" -ge 1000 ]; then
        printf "%'d" "$num" | sed 's/,/./g'
    else
        echo "$num"
    fi
}

# JSON file (default to latest)
JSON_FILE="${1:-/home/rom/timing_analysis/latest.json}"

if [ ! -f "$JSON_FILE" ]; then
    echo "Error: JSON file not found: $JSON_FILE"
    echo "Usage: $0 [path_to_json_file]"
    exit 1
fi

# Parse JSON using jq (single pass for speed)
CALL_ID=$(jq -r '.call_id' "$JSON_FILE")
START_TIME=$(jq -r '.start_time' "$JSON_FILE")
DURATION_MS=$(jq -r '(.duration * 1000) | floor' "$JSON_FILE")
VAD_CHUNKS=$(jq -r '.summary.vad_chunks' "$JSON_FILE")

# Format duration with dot separator
DURATION_FORMATTED=$(format_number "$DURATION_MS")

# Clear screen and display header
clear
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}                        VOICE CALL TIMING ANALYSIS${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Call ID:       ${WHITE}$CALL_ID${NC}"
echo -e "Start Time:    ${WHITE}$START_TIME${NC}"
echo -e "Duration:      ${WHITE}${DURATION_FORMATTED}ms${NC}"
echo ""

# Summary section
echo -e "${YELLOW}═══ SUMMARY ═══${NC}"
echo -e "${GREEN}VAD Chunks:${NC}    $VAD_CHUNKS speech segments detected"
echo ""

# Event timeline
echo -e "${YELLOW}═══ EVENT TIMELINE (Time reset after ring_wait_complete) ═══${NC}"
printf "${WHITE}%-35s | %-12s | %-12s | %-20s${NC}\n" "EVENT" "TIME" "DURATION" "DETAILS"
echo "─────────────────────────────────────────────────────────────────────────────"

# Initialize offset variable
time_offset=0

# Process all events
jq -r '.events[] |
    (.time * 1000 | floor) as $time_ms |
    (if .details.duration then (.details.duration * 1000 | floor) else null end) as $dur_ms |
    (.details | del(.duration) | to_entries | map("\(.key)=\(.value)") | join(", ")) as $other |
    "\(.name)|\($time_ms)|\($dur_ms)|\(if $other == "" then "-" else $other end)"
' "$JSON_FILE" | while IFS='|' read -r name time_ms dur_ms details; do

    # Apply current offset to this event
    adjusted_time=$((time_ms - time_offset))

    # Format numbers
    time_str=$(format_number "$adjusted_time")

    if [ "$dur_ms" = "null" ] || [ -z "$dur_ms" ]; then
        dur_str="-"
    else
        dur_str=$(format_number "$dur_ms")
        dur_str="${dur_str}ms"
    fi

    # Print event row
    printf "${GREEN}%-35s${NC} | %12s | %12s | %-20s\n" "$name" "${time_str}ms" "$dur_str" "$details"

    # AFTER displaying ring_wait_complete, set the offset for all following events
    if [ "$name" = "ring_wait_complete" ]; then
        time_offset=$time_ms
    fi
done

echo ""
echo -e "${GREEN}Analysis complete!${NC}"
echo ""
