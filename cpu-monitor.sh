#!/bin/bash

# CPU monitor daemon that writes 10-second average to a file
CPU_FILE="/tmp/cpu_usage_avg"
SAMPLE_COUNT=10
SAMPLE_INTERVAL=1

# Function to get CPU stats
get_cpu_stats() {
    grep '^cpu ' /proc/stat | awk '{for(i=2;i<=NF;i++)sum+=$i; print sum, $5}'
}

# Initialize with first reading
read total1 idle1 <<< $(get_cpu_stats)

# Main calculation loop
while true; do
    sleep $SAMPLE_COUNT
    
    # Get new reading after interval
    read total2 idle2 <<< $(get_cpu_stats)
    
    # Calculate differences
    total_diff=$((total2 - total1))
    idle_diff=$((idle2 - idle1))
    
    if [ $total_diff -gt 0 ]; then
        usage=$((100 * (total_diff - idle_diff) / total_diff))
        echo "${usage}%" > "$CPU_FILE"
    else
        echo "0%" > "$CPU_FILE"
    fi
    
    # Update baseline for next calculation
    total1=$total2
    idle1=$idle2
done