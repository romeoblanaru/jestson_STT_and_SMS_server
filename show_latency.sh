#!/bin/bash
#
# Display Riva STT Wrapper Latency Logs
# Usage: ./show_latency.sh [number_of_lines]
#

# Check for help flag
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: ./show_latency.sh [number_of_lines]"
    echo ""
    echo "Display Riva STT wrapper latency statistics and recent transcriptions."
    echo ""
    echo "Options:"
    echo "  [number]         Number of recent transcriptions to show (default: 20)"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./show_latency.sh          - Show last 20 transcriptions"
    echo "  ./show_latency.sh 50       - Show last 50 transcriptions"
    echo "  ./show_latency.sh 0        - Show all transcriptions"
    exit 0
fi

# Number of lines to show (default: 20)
LINES=${1:-20}

echo "========================================================================="
echo "Riva STT Wrapper - Latency Statistics"
echo "========================================================================="
echo ""

# Check if service is running
if systemctl is-active --quiet riva-wrapper.service; then
    echo "✓ Service Status: RUNNING"
else
    echo "✗ Service Status: STOPPED"
fi

echo ""
echo "Recent Transcriptions (last $LINES):"
echo "-------------------------------------------------------------------------"

# Get logs and filter for LATENCY entries
echo "Romy_1202" | sudo -S journalctl -u riva-wrapper.service --no-pager | grep "\[LATENCY\]" | tail -n "$LINES"

# Count total transcriptions
TOTAL=$(echo "Romy_1202" | sudo -S journalctl -u riva-wrapper.service --no-pager | grep -c "\[LATENCY\]")

echo "-------------------------------------------------------------------------"
echo "Total Transcriptions Since Service Start: $TOTAL"
echo ""

# Show average latency if there are transcriptions
if [ "$TOTAL" -gt 0 ]; then
    echo "Calculating Statistics..."
    echo "Romy_1202" | sudo -S journalctl -u riva-wrapper.service --no-pager | \
        grep "\[LATENCY\]" | \
        awk -F'|' '{
            # Extract timing values
            for(i=1; i<=NF; i++) {
                if($i ~ /Conversion:/) {
                    split($i, a, " ");
                    conv += substr(a[2], 1, length(a[2])-1);
                    conv_count++;
                }
                if($i ~ /Transcription:/) {
                    split($i, a, " ");
                    trans += substr(a[2], 1, length(a[2])-1);
                    trans_count++;
                }
                if($i ~ /Total:/) {
                    split($i, a, " ");
                    total += substr(a[2], 1, length(a[2])-1);
                    total_count++;
                }
            }
        }
        END {
            if(conv_count > 0) {
                printf("  Average Conversion Time:     %.3f seconds\n", conv/conv_count);
                printf("  Average Transcription Time:  %.3f seconds\n", trans/trans_count);
                printf("  Average Total Latency:       %.3f seconds\n", total/total_count);
            }
        }'
    echo ""
fi

echo "========================================================================="
