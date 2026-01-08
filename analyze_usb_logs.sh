#!/bin/bash
# Analyze USB audio monitoring logs to identify patterns

LOG_FILE="/var/log/ec25_usb_audio_monitor.log"

echo "============================================================"
echo "EC25 USB Audio Log Analysis"
echo "============================================================"
echo ""

if [ ! -f "$LOG_FILE" ]; then
    echo "No log file found at $LOG_FILE"
    echo "Start monitoring first: sudo systemctl start ec25-usb-monitor.service"
    exit 1
fi

echo "=== ERROR SUMMARY ==="
echo "Total USB errors:"
grep "ERROR" "$LOG_FILE" | wc -l

echo ""
echo "USB -19 errors (device not found):"
grep "ERROR.*-19" "$LOG_FILE" | wc -l

echo ""
echo "Device disconnects:"
grep "DISCONNECTED" "$LOG_FILE" | wc -l

echo ""
echo "ALSA device disappeared:"
grep "ALSA device DISAPPEARED" "$LOG_FILE" | wc -l

echo ""
echo "=== PROCESS ACCESS PATTERNS ==="
echo "Processes that accessed ttyUSB1 (audio port):"
grep "Process accessing ttyUSB1" "$LOG_FILE" | awk -F'AUDIO): ' '{print $2}' | sort | uniq -c | sort -rn

echo ""
echo "=== TIMING ANALYSIS ==="
echo "Time between errors:"
grep "ERROR" "$LOG_FILE" | awk '{print $1, $2}' | while read -r date time; do
    timestamp=$(date -d "$date $time" +%s 2>/dev/null)
    if [ -n "$prev_timestamp" ]; then
        diff=$((timestamp - prev_timestamp))
        if [ "$diff" -gt 0 ]; then
            echo "$diff seconds"
        fi
    fi
    prev_timestamp=$timestamp
done | sort -n | uniq -c

echo ""
echo "=== LAST 10 ERRORS ==="
grep "ERROR" "$LOG_FILE" | tail -10

echo ""
echo "=== LAST 10 WARNINGS ==="
grep "WARNING" "$LOG_FILE" | tail -10

echo ""
echo "=== RECOMMENDATIONS ==="

error_count=$(grep "ERROR.*-19" "$LOG_FILE" | wc -l)
if [ "$error_count" -gt 5 ]; then
    echo "⚠️  High number of USB -19 errors detected ($error_count)"
    echo "   This indicates the EC25 audio interface is unstable"
    echo "   Firmware update strongly recommended"
fi

disconnect_count=$(grep "DISCONNECTED" "$LOG_FILE" | wc -l)
if [ "$disconnect_count" -gt 3 ]; then
    echo "⚠️  Multiple disconnect events detected ($disconnect_count)"
    echo "   Check USB cable quality and power supply"
fi

alsa_missing=$(grep "ALSA device DISAPPEARED" "$LOG_FILE" | wc -l)
if [ "$alsa_missing" -gt 0 ]; then
    echo "⚠️  ALSA audio device disappeared $alsa_missing time(s)"
    echo "   This is a driver/firmware issue"
fi

echo ""
echo "============================================================"
echo "Full log available at: $LOG_FILE"
echo "============================================================"
