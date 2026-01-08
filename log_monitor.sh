#!/bin/bash
# Log monitoring script - watches for errors and service restarts
# Sends notifications via pi_send_message.sh

# Configuration
MONITOR_SCRIPT="/home/rom/pi_send_message.sh"
STATE_FILE="/tmp/log_monitor.state"
CHECK_INTERVAL=60  # seconds

# Patterns to watch for
ERROR_PATTERNS=(
    "ERROR"
    "CRITICAL" 
    "FATAL"
    "Failed"
    "failed to"
    "cannot"
    "unable to"
    "panic"
    "crash"
)

SERVICE_PATTERNS=(
    "Started"
    "Stopped"
    "Restarted"
    "Reloading"
    "Failed to start"
)

# Initialize state file if doesn't exist
if [ ! -f "$STATE_FILE" ]; then
    date +%s > "$STATE_FILE"
fi

# Function to check for errors in logs
check_errors() {
    local last_check=$(cat "$STATE_FILE" 2>/dev/null || echo "0")
    local current_time=$(date +%s)
    
    # Check journal for errors since last check
    local errors=$(sudo journalctl --since "@$last_check" --priority=err --no-pager 2>/dev/null | \
                   grep -E "$(IFS='|'; echo "${ERROR_PATTERNS[*]}")" | \
                   head -5)
    
    if [ -n "$errors" ]; then
        # Count number of errors
        local error_count=$(echo "$errors" | wc -l)
        local message="Log Monitor: $error_count error(s) detected in system logs"
        
        # Add first error as example
        local first_error=$(echo "$errors" | head -1 | sed 's/^.*: //' | cut -c1-100)
        if [ -n "$first_error" ]; then
            message="$message - Example: $first_error"
        fi
        
        $MONITOR_SCRIPT "$message" "warning"
    fi
    
    # Update state file
    echo "$current_time" > "$STATE_FILE"
}

# Function to check for service state changes
check_service_changes() {
    local services=$(sudo journalctl -u "*.service" --since "1 minute ago" --no-pager 2>/dev/null | \
                    grep -E "$(IFS='|'; echo "${SERVICE_PATTERNS[*]}")")
    
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            # Extract service name and action
            local service=$(echo "$line" | grep -oP '(?<=systemd\[)[^]]*\]:\s*\K[^:]*' || \
                          echo "$line" | grep -oP '(?<=Unit )[^.]*' || \
                          echo "unknown")
            
            # Check for restart/failure
            if echo "$line" | grep -qE "Restarted|Failed|Stopped"; then
                local action="restarted/failed"
                local severity="warning"
                
                if echo "$line" | grep -q "Failed"; then
                    action="failed"
                    severity="error"
                fi
                
                $MONITOR_SCRIPT "Service Alert: $service $action" "$severity"
            fi
        fi
    done <<< "$services"
}

# Function for continuous monitoring
monitor_logs() {
    echo "Log Monitor started - checking every $CHECK_INTERVAL seconds"
    
    while true; do
        check_errors
        check_service_changes
        sleep $CHECK_INTERVAL
    done
}

# Function for one-time check with status report
check_once() {
    local last_check=$(cat "$STATE_FILE" 2>/dev/null || echo "0")
    local current_time=$(date +%s)
    local time_range=$((current_time - last_check))
    local hours=$((time_range / 3600))
    local minutes=$(((time_range % 3600) / 60))

    # Check journal for errors since last check
    local errors=$(sudo journalctl --since "@$last_check" --priority=err --no-pager 2>/dev/null | \
                   grep -E "$(IFS='|'; echo "${ERROR_PATTERNS[*]}")" | \
                   head -5)

    # Check for service changes
    local services=$(sudo journalctl -u "*.service" --since "@$last_check" --no-pager 2>/dev/null | \
                    grep -E "$(IFS='|'; echo "${SERVICE_PATTERNS[*]}")" | \
                    grep -E "Restarted|Failed|Stopped" | wc -l)

    # Build status message
    local message="**Log Monitor Status**"$'\n'

    # Time range checked
    if [ "$hours" -gt 0 ]; then
        message+="Checked: Last ${hours}h ${minutes}m"$'\n'
    else
        message+="Checked: Last ${minutes}m"$'\n'
    fi

    # Log sources
    message+="**Sources:**"$'\n'
    message+="- systemd journal (all units)"$'\n'
    message+="- Priority: error and above"$'\n'
    message+="- Service state changes"$'\n'

    # Error patterns monitored
    message+="**Patterns:** ${ERROR_PATTERNS[*]}"$'\n'

    # Results
    if [ -n "$errors" ]; then
        local error_count=$(echo "$errors" | wc -l)
        message+="**Result:** ⚠️  $error_count error(s) detected"$'\n'
        local first_error=$(echo "$errors" | head -1 | sed 's/^.*: //' | cut -c1-150)
        message+="Example: $first_error"
        $MONITOR_SCRIPT "$message" "warning"
    elif [ "$services" -gt 0 ]; then
        message+="**Result:** ⚠️  $services service change(s) detected"
        $MONITOR_SCRIPT "$message" "warning"
    else
        message+="**Result:** ✅ No errors or service issues detected"
        $MONITOR_SCRIPT "$message" "info"
    fi

    # Update state file
    echo "$current_time" > "$STATE_FILE"
}

# Main script logic
case "${1:-}" in
    "monitor")
        monitor_logs
        ;;
    "check")
        check_once
        ;;
    "errors")
        check_errors
        ;;
    "services")
        check_service_changes
        ;;
    *)
        echo "Usage: $0 {monitor|check|errors|services}"
        echo ""
        echo "Commands:"
        echo "  monitor  - Continuous monitoring (runs in loop)"
        echo "  check    - One-time check for errors and service changes"
        echo "  errors   - Check only for errors in logs"
        echo "  services - Check only for service state changes"
        exit 1
        ;;
esac