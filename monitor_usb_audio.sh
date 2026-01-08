#!/bin/bash
# Real-time USB Audio Monitoring for EC25
# Monitors USB errors, process access, and kernel messages

LOG_FILE="/var/log/ec25_usb_audio_monitor.log"
ALERT_SCRIPT="/home/rom/pi_send_message.sh"

# Colors for terminal output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_msg() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" | tee -a "$LOG_FILE"
}

log_error() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${RED}[$timestamp] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${YELLOW}[$timestamp] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${BLUE}[$timestamp] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

send_alert() {
    local severity="$1"
    local message="$2"
    bash "$ALERT_SCRIPT" "EC25 USB Monitor: $message" "$severity" 2>/dev/null &
}

# Check what processes are accessing USB audio
check_audio_access() {
    local audio_users=$(sudo lsof /dev/ttyUSB1 2>/dev/null | awk 'NR>1 {print $1":"$2}' | tr '\n' ' ')
    if [ -n "$audio_users" ]; then
        echo "$audio_users"
    else
        echo "none"
    fi
}

# Check ALSA audio device status
check_alsa_status() {
    if aplay -l 2>/dev/null | grep -q "EC25"; then
        echo "present"
    else
        echo "missing"
    fi
}

# Monitor kernel messages in real-time
monitor_kernel() {
    log_info "Starting kernel message monitor..."

    dmesg -w 2>/dev/null | while read -r line; do
        # Check for USB errors
        if echo "$line" | grep -qE "usb.*-19|cannot submit urb|device not accepting|reset.*USB"; then
            log_error "USB ERROR: $line"
            send_alert "error" "USB device error detected"
        fi

        # Check for audio-specific errors
        if echo "$line" | grep -qE "ttyUSB1|EC25.*audio|snd_usb"; then
            log_warning "USB AUDIO EVENT: $line"
        fi

        # Check for device disconnect
        if echo "$line" | grep -qE "USB disconnect.*2c7c"; then
            log_error "EC25 DISCONNECTED!"
            send_alert "critical" "EC25 modem disconnected from USB"
        fi
    done
}

# Monitor process access to ttyUSB1 (audio port)
monitor_port_access() {
    log_info "Starting port access monitor..."

    local prev_users=""
    while true; do
        local current_users=$(check_audio_access)

        if [ "$current_users" != "$prev_users" ]; then
            if [ "$current_users" != "none" ]; then
                log_warning "Process accessing ttyUSB1 (AUDIO): $current_users"

                # Get detailed process info
                sudo lsof /dev/ttyUSB1 2>/dev/null | while read -r line; do
                    if [ -n "$line" ] && ! echo "$line" | grep -q "COMMAND"; then
                        log_info "  $line"
                    fi
                done
            else
                log_info "ttyUSB1 (AUDIO) released"
            fi
            prev_users="$current_users"
        fi

        sleep 1
    done
}

# Monitor ALSA device status
monitor_alsa() {
    log_info "Starting ALSA device monitor..."

    local prev_status=""
    while true; do
        local current_status=$(check_alsa_status)

        if [ "$current_status" != "$prev_status" ]; then
            if [ "$current_status" = "present" ]; then
                log_info "EC25-AUX ALSA device appeared"
            else
                log_error "EC25-AUX ALSA device DISAPPEARED!"
                send_alert "error" "EC25 ALSA audio device disappeared"
            fi
            prev_status="$current_status"
        fi

        sleep 2
    done
}

# Monitor USB device enumeration
monitor_usb_enum() {
    log_info "Starting USB enumeration monitor..."

    while true; do
        if ! lsusb | grep -q "2c7c:0125"; then
            log_error "EC25 not visible on USB bus!"
            send_alert "critical" "EC25 disappeared from USB bus"

            # Wait for it to come back
            while ! lsusb | grep -q "2c7c:0125"; do
                sleep 1
            done
            log_info "EC25 reappeared on USB bus"
        fi

        sleep 5
    done
}

# Main monitoring loop with system stats
monitor_stats() {
    log_info "Starting system stats monitor..."

    while true; do
        # Check if device exists
        if [ -c /dev/ttyUSB2 ]; then
            # Removed AT+CSQ signal check - causes modem freeze when USB audio enabled
            # local signal=$(echo -e "AT+CSQ\r" | timeout 1 picocom -b 115200 -qrx 300 /dev/ttyUSB2 2>/dev/null | grep "+CSQ:" | grep -oE "[0-9]+" | head -1)
            local signal="N/A"

            # Get audio access
            local audio_users=$(check_audio_access)

            # Get ALSA status
            local alsa_status=$(check_alsa_status)

            # USB device count
            local usb_count=$(ls -1 /dev/ttyUSB* 2>/dev/null | wc -l)

            log_info "Status: USB_Ports=$usb_count | Signal=$signal | ALSA=$alsa_status | Audio_Access=$audio_users"
        else
            log_error "ttyUSB2 (DATA) port missing!"
        fi

        sleep 10
    done
}

# Cleanup function
cleanup() {
    log_info "Monitor stopped by user"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start all monitors in background
log_info "============================================================"
log_info "EC25 USB Audio Monitor Started"
log_info "Log file: $LOG_FILE"
log_info "Monitoring: Kernel messages, Port access, ALSA, USB enum, Stats"
log_info "Press Ctrl+C to stop"
log_info "============================================================"

# Start background monitors
monitor_kernel &
monitor_port_access &
monitor_alsa &
monitor_usb_enum &
monitor_stats &

# Wait for all background jobs
wait
