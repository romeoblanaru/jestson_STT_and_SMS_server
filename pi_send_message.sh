#!/bin/bash
# Raspberry Pi system monitoring and notification script

# Configuration
# Use internal VPN IP to ensure traffic goes through VPN tunnel
API_URL="http://10.100.0.1:5000/api/send"
# Alternative if using nginx on VPN server:
# API_URL="https://10.100.0.1/api/send"
HOSTNAME=$(hostname)
SERVICE="raspberry-pi-vpn"

# Prevent concurrent execution - use flock for locking
# Use md5 hash of message to avoid "filename too long" errors
LOCK_HASH=$(echo -n "${1:-default}" | md5sum | cut -d' ' -f1)
LOCK_FILE="/tmp/pi_send_message_${LOCK_HASH}.lock"
LOCK_FD=200

# Try to acquire lock with 2-second timeout
exec 200>"$LOCK_FILE"
if ! flock -n -x 200; then
    # Another instance is running, exit silently
    logger -t pi_send_message "Skipping - another instance already running for: ${1:-default}"
    exit 0
fi

# Get VPN IP address
VPN_IP=$(ip -4 addr show wg0 2>/dev/null | grep inet | awk '{print $2}' | cut -d/ -f1)
if [ -z "$VPN_IP" ]; then
    VPN_IP="no-vpn"
fi

# Function to send notification
send_notification() {
    local severity="$1"
    local message="$2"

    # Build JSON payload using jq for proper escaping
    local hostname_with_ip="$HOSTNAME [$VPN_IP]"

    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        # jq is not installed - send manual JSON with warning
        logger -t pi_send_message "WARNING: jq not installed - sending manually formatted JSON"

        # Escape basic characters for JSON (not perfect but works for most cases)
        local escaped_message=$(echo "$message" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr '\n' ' ')

        local fallback_warning="WARNING: jq JSON parser is not installed on $hostname_with_ip. Install with: sudo apt install -y jq | Original message: $escaped_message"

        # Create simple JSON manually (not as robust as jq but works)
        local json_payload="{\"hostname\":\"$hostname_with_ip\",\"service\":\"$SERVICE\",\"severity\":\"warning\",\"message\":\"$fallback_warning\"}"

        # Send the notification
        local response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL" \
            -H "Content-Type: application/json" \
            -d "$json_payload" \
            --connect-timeout 10 \
            --max-time 60)

        local http_code=$(echo "$response" | tail -1)
        local body=$(echo "$response" | sed '$d')

        logger -t pi_send_message "Fallback JSON sent - VPS Response: HTTP $http_code - $body"
        echo "$body"
        return
    fi

    # Use jq to build proper JSON - handles all special characters correctly
    local json_payload=$(jq -n \
        --arg hostname "$hostname_with_ip" \
        --arg service "$SERVICE" \
        --arg severity "$severity" \
        --arg message "$message" \
        '{hostname: $hostname, service: $service, severity: $severity, message: $message}')

    # Send the notification and log response
    logger -t pi_send_message "Sending curl request (payload size: ${#json_payload} bytes)"
    local response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "$json_payload" \
        --connect-timeout 10 \
        --max-time 60)
    logger -t pi_send_message "Curl completed"

    local http_code=$(echo "$response" | tail -1)
    local body=$(echo "$response" | sed '$d')

    # Log to syslog for monitoring
    logger -t pi_send_message "VPS Response: HTTP $http_code - $body"

    # Return body for caller
    echo "$body"
}

# Get CPU usage from file (strip any % sign)
get_cpu_usage() {
    if [ -f /tmp/cpu_usage_avg ]; then
        cat /tmp/cpu_usage_avg 2>/dev/null | sed 's/%$//' || echo "0"
    else
        # Fallback to calculating CPU usage if file doesn't exist
        top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}' | cut -d. -f1
    fi
}

# Get EC25 status with timeout protection - combined classic + enhanced status + modem details
get_ec25_status() {
    local ec25_info=""
    local at_responds="NO"
    local modem_details=""
    local smstools_was_running=false

    # Check if SMSTools is running and stop it temporarily
    if systemctl is-active --quiet smstools; then
        smstools_was_running=true
        sudo systemctl stop smstools 2>/dev/null
        sleep 1  # Wait for port to be released
    fi

    # Helper function to send AT command
    send_at() {
        echo -e "$1\r" | timeout 1 picocom -b 115200 -qrx 500 /dev/ttyUSB_EC25_DATA 2>/dev/null | grep -v "^$" | grep -v "picocom" | grep -v "Terminal"
    }

    # Check if modem exists and responds to AT commands
    if ls /dev/ttyUSB* 2>/dev/null | grep -q ttyUSB; then
        if [ -w /dev/ttyUSB_EC25_DATA ]; then
            # Test AT command response
            local at_test=$(send_at "AT" | grep -c "OK")
            if [ "$at_test" -gt 0 ]; then
                at_responds="YES"

                # Get modem details
                local model=$(send_at "ATI" | grep -E "EC25" | head -1 | xargs)
                local revision=$(send_at "ATI" | grep "Revision:" | cut -d: -f2 | xargs)
                local imei=$(send_at "AT+GSN" | grep -v "AT" | grep -v "OK" | grep -E "[0-9]{15}" | xargs)
                local sim_iccid=$(send_at "AT+QCCID" | grep "+QCCID:" | cut -d: -f2 | xargs)
                local imsi=$(send_at "AT+CIMI" | grep -v "AT" | grep -v "OK" | grep -E "[0-9]{15}" | xargs)

                # Get signal strength
                local signal=$(send_at "AT+CSQ" | grep "+CSQ:" | grep -oE "[0-9]+" | head -1)
                if [ -n "$signal" ] && [ "$signal" -ne 99 ]; then
                    signal=$((signal * 100 / 31))
                    signal="${signal}%"
                else
                    signal="0%"
                fi

                # Get network operator - try cached value first for speed
                local network="No Network"
                local cache_file="/tmp/ec25_operator.cache"

                if [ -f "$cache_file" ] && [ $(($(date +%s) - $(stat -c %Y "$cache_file" 2>/dev/null || echo 0))) -lt 300 ]; then
                    network=$(cat "$cache_file" 2>/dev/null)
                fi

                if [ -z "$network" ] || [ "$network" = "No Network" ]; then
                    network=$(timeout 2 bash -c 'echo -e "AT+COPS=3,0\r" > /dev/ttyUSB_EC25_DATA; sleep 0.3; echo -e "AT+COPS?\r" > /dev/ttyUSB_EC25_DATA; sleep 0.5; timeout 1 cat /dev/ttyUSB_EC25_DATA' 2>/dev/null | grep "+COPS:" | grep -oP '"\K[^"]+' | head -1)
                    if [ -n "$network" ]; then
                        echo "$network" > "$cache_file"
                    else
                        network="No Network"
                    fi
                fi

                # Build modem details line
                modem_details="**Model:** ${model} | **FW:** ${revision} | **IMEI:** ${imei}"$'\n'
                modem_details+="**SIM ICCID:** ${sim_iccid} | **IMSI:** ${imsi}"

                # Build main status line
                ec25_info="**EC25:** Connected | AT: ${at_responds} | ${network} | Signal: ${signal}"
            else
                ec25_info="**EC25:** Detected | AT: NO | Cannot communicate"
            fi
        else
            ec25_info="**EC25:** Detected | AT: NO | No write permission"
        fi
    else
        ec25_info="**EC25:** Not Detected | AT: NO"
    fi

    # Get enhanced config from SMS API (audio, VoLTE, network mode)
    local api_response=$(curl -s --connect-timeout 2 --max-time 3 http://localhost:8088/pi_send_message 2>/dev/null)

    if [ $? -eq 0 ] && [ -n "$api_response" ]; then
        # Parse JSON response using jq if available
        if command -v jq &> /dev/null; then
            local audio_status=$(echo "$api_response" | jq -r '.status_summary.audio // "Unknown"')
            local network_mode=$(echo "$api_response" | jq -r '.status_summary.network // "Unknown"')
            local volte_status=$(echo "$api_response" | jq -r '.status_summary.volte // "Unknown"')
            local signal_csq=$(echo "$api_response" | jq -r '.status_summary.signal // "Unknown"')

            # Add enhanced config line (FIXED: removed extra '=' sign)
            ec25_info+=$'\n'"**Config:** ${network_mode} | VoLTE: ${volte_status} | Audio: ${audio_status} | Signal CSQ: ${signal_csq}"
        fi
    fi

    # Add modem details if available
    if [ -n "$modem_details" ]; then
        ec25_info+=$'\n'"${modem_details}"
    fi

    # Restart SMSTools if it was running before
    if [ "$smstools_was_running" = true ]; then
        sudo systemctl start smstools 2>/dev/null &
    fi

    echo "$ec25_info"
}

# Get unique system errors from last hour with timestamps
get_system_errors() {
    local errors=""
    
    # Try journalctl first
    if command -v journalctl &> /dev/null; then
        # Get unique errors - extract just the error message part and show first occurrence
        errors=$(sudo journalctl --since "1 hour ago" --priority=err --no-pager -o short 2>/dev/null | \
                grep -v "^-- " | \
                awk '{
                    # Extract error message starting from service name
                    msg = substr($0, index($0,$6))
                    # Remove common prefixes to get unique error
                    gsub(/^[^:]+: /, "", msg)
                    # If not seen before, print with timestamp
                    if (!seen[msg]++) {
                        print $1, $2, $3 " - " msg
                    }
                }' | \
                head -5)
    fi
    
    # If no errors or journalctl not available, check dmesg
    if [ -z "$errors" ]; then
        errors=$(dmesg -T 2>/dev/null | \
                grep -i "error\|fail" | \
                tail -20 | \
                awk -F'] ' '{
                    msg = $2
                    gsub(/^[^:]+: /, "", msg)
                    if (!seen[msg]++) {
                        print $1 "] " msg
                    }
                }' | \
                tail -5)
    fi
    
    if [ -z "$errors" ]; then
        echo "No recent errors"
    else
        echo "$errors"
    fi
}

# Get listening ports with process names
get_listening_ports() {
    sudo netstat -tlnp 2>/dev/null | \
        grep LISTEN | \
        awk '{
            split($7,a,"/")
            port = substr($4,index($4,":")+1)
            process = a[2]
            
            # Add custom labels for known ports
            if (port == "8070") label = " (Monitor Messg)"
            else if (port == "8088") label = " (SMS Gateway)"
            else if (port == "10000") label = " (Webmin Panel)"
            else label = ""
            
            print "Port " port label " - " process
        }' | \
        head -10
}

# Get critical services status
get_services_status() {
    local services_info=""

    # Check unified-modem service (handles both SMS and Voice)
    if systemctl is-active --quiet unified-modem 2>/dev/null; then
        services_info="Voice/SMS: ✓ Running"
    elif systemctl is-active --quiet ec25-voice-bot 2>/dev/null; then
        services_info="Voice: ✓ Running"
    else
        services_info="Voice: ✗ Stopped"
    fi

    # Check SMS API
    if systemctl is-active --quiet sms-api 2>/dev/null; then
        services_info="${services_info} | SMS API: ✓ Running"
    else
        services_info="${services_info} | SMS API: ✗ Stopped"
    fi

    # Check STT Server (Parakeet)
    local stt_status="✗ Stopped"
    local stt_name="Unknown"

    # Check if Parakeet container is running
    if docker ps --format "{{.Image}}" 2>/dev/null | grep -q "parakeet-server"; then
        # Try to get server name from health endpoint
        local health_response=$(curl -s --connect-timeout 2 --max-time 3 http://localhost:9001/health 2>/dev/null)
        if [ $? -eq 0 ] && [ -n "$health_response" ]; then
            stt_name=$(echo "$health_response" | jq -r '.model // "Parakeet"' 2>/dev/null || echo "Parakeet")
            stt_status="✓ Running"
        else
            stt_name="Parakeet"
            stt_status="⚠ No Response"
        fi
    fi

    services_info="${services_info} | STT Server: $stt_status ($stt_name)"

    echo "$services_info"
}

# Get simple modem status (model and USB port)
get_modem_status() {
    local modem_model="Not Detected"
    local usb_ports="N/A"

    # Check for SIM7600
    if lsusb | grep -q "1e0e:9011\|1e0e:9001"; then
        modem_model="SIM7600G-H"
    # Check for EC25
    elif lsusb | grep -q "2c7c:0125"; then
        modem_model="EC25-AUX"
    fi

    # Get USB port count
    if ls /dev/ttyUSB* 2>/dev/null | grep -q ttyUSB; then
        local port_count=$(ls -1 /dev/ttyUSB* 2>/dev/null | wc -l)
        local port_list=$(ls /dev/ttyUSB* 2>/dev/null | xargs -n1 basename | tr '\n' ',' | sed 's/,$//')
        usb_ports="$port_count ports ($port_list)"
    fi

    echo "**Modem Detected:** Model: $modem_model | USB PORT: $usb_ports"
}

# Get running processes (top 10 by CPU) with more details, excluding temporary processes
get_running_processes() {
    ps aux --sort=-%cpu | \
        awk 'NR>1 {
            # Get full command with arguments
            cmd = $11
            for (i=12; i<=NF; i++) cmd = cmd " " $i
            
            # Skip temporary processes like this script
            if (cmd ~ /pi_send_message\.sh/ || cmd ~ /^ps aux/ || cmd ~ /^awk/) next
            
            # Count valid processes
            if (++count > 10) exit
            
            # Truncate if too long
            if (length(cmd) > 60) cmd = substr(cmd, 1, 57) "..."
            printf "(%s%% CPU, %s) %s\n", $3, $1, cmd
        }'
}

# Comprehensive system check - formatted message
comprehensive_system_check() {
    # Debug timing
    logger -t pi_send_message "Starting comprehensive_system_check"

    # Gather all data
    local cpu_usage=$(get_cpu_usage)
    local cpu_temp=$(vcgencmd measure_temp 2>/dev/null | cut -d'=' -f2 | cut -d"'" -f1 || echo "N/A")
    local mem_info=$(free | grep Mem | awk '{print int($3/$2 * 100) "%"}')
    local disk_usage=$(df -h / | awk 'NR==2 {printf "%s", $5}')
    
    # Network info - fix VPN detection for different interface names
    local system_hostname=$(hostname)
    local avahi_hostname=$(systemctl status avahi-daemon 2>/dev/null | grep -oP 'running \[\K[^.]+(?=\.local\])' | head -1)
    if [ -z "$avahi_hostname" ]; then
        avahi_hostname="$system_hostname"
    fi
    local ip_info=$(ip -4 addr show | grep inet | grep -v "127.0.0.1" | grep -v "tun\|wg" | head -1 | awk '{print $2}' || echo "No IP")
    local vpn_ip=$(ip -4 addr show | grep -E "tun|wg" | grep inet | awk '{print $2}' | head -1 || echo "")
    if [ -z "$vpn_ip" ]; then
        vpn_ip="No VPN"
    fi
    local default_gw=$(ip route | grep default | awk '{print $3}' | head -1 || echo "No GW")

    # Modem status (simple detection)
    local modem_status=$(get_modem_status)

    # Services status
    local services_status=$(get_services_status)
    
    # Listening ports
    local ports=$(get_listening_ports)
    
    # Running processes
    local processes=$(get_running_processes)
    
    # Recent errors
    local errors=$(get_system_errors)
    
    # Build comprehensive message with colored section titles - no leading spaces
    local message=""
    # Build message piece by piece without heredoc indentation
    message+="**System Report** - CPU: ${cpu_usage}% @ ${cpu_temp}°C | Mem: ${mem_info} | Disk: ${disk_usage}"$'\n'
    message+="**Local Network:** Host: ${system_hostname} (${avahi_hostname}.local) | IP: ${ip_info} | GW: ${default_gw} | VPN: <blue>**${vpn_ip}**</blue>"$'\n'
    message+="${modem_status}"$'\n'
    message+="**Services:** ${services_status}"$'\n'
    message+="**=== Listening Ports ===**"$'\n'
    message+="${ports}"$'\n'
    message+="<blue>**=== Top Processes ===**</blue>"$'\n'
    message+="${processes}"$'\n'
    message+="<red>**=== Recent Errors ===**</red>"$'\n'
    message+="${errors}"
    
    # Determine severity based on thresholds
    local severity="info"
    local cpu_usage_int=${cpu_usage%.*}
    local cpu_temp_int=${cpu_temp%.*}
    local disk_usage_int=${disk_usage%\%}
    
    if [ "$cpu_usage_int" -gt 80 ] 2>/dev/null || \
       [ "$cpu_temp_int" -gt 70 ] 2>/dev/null || \
       [ "$disk_usage_int" -gt 90 ] 2>/dev/null; then
        severity="warning"
    fi
    
    # Send comprehensive message
    send_notification "$severity" "$message"
}

# Quick health check
check_system_health() {
    local cpu_usage=$(get_cpu_usage)
    local cpu_temp=$(vcgencmd measure_temp | cut -d'=' -f2 | cut -d"'" -f1)
    local mem_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    local message="CPU: ${cpu_usage}% @ ${cpu_temp}°C | Mem: ${mem_usage}% | Disk: ${disk_usage}%"
    send_notification "info" "$message"
}

# VPN check
check_vpn_status() {
    local vpn_gw="10.100.0.1"
    local vpn_interface=$(ip -4 addr show | grep -E "tun|wg" | grep inet | awk '{print $NF}' | head -1)

    if [ -z "$vpn_interface" ]; then
        send_notification "error" "VPN interface not found - VPN is down"
        return
    fi

    if ! ping -c 1 -W 5 "$vpn_gw" > /dev/null 2>&1; then
        send_notification "error" "VPN connection lost - unable to reach gateway $vpn_gw"
    else
        local handshake_info=$(sudo wg show 2>/dev/null | grep "latest handshake" | head -1)
        send_notification "info" "VPN connected - gateway $vpn_gw reachable | $handshake_info"
    fi
}

# EC25 specific check
check_ec25() {
    local ec25_status=$(get_ec25_status)

    # Get USB port information
    local usb_info=""
    local service_info=""

    if ls /dev/ttyUSB[0-9]* 2>/dev/null | grep -q ttyUSB; then
        # Count physical USB ports (not symlinks)
        local port_count=$(ls -1 /dev/ttyUSB[0-9]* 2>/dev/null | wc -l)

        # Check for symbolic links to show port functions
        local port_details=""
        if [ -L /dev/ttyUSB_EC25_DATA ]; then
            local data_port=$(readlink /dev/ttyUSB_EC25_DATA)
            local ctrl_port=$(readlink /dev/ttyUSB_EC25_CTRL 2>/dev/null || echo "N/A")

            # Check for USB audio device (hw:EC25AUX)
            local audio_port="N/A"
            if arecord -l 2>/dev/null | grep -q "EC25AUX"; then
                audio_port="hw:EC25AUX"
            fi

            port_details="DATA:$data_port, AUDIO:$audio_port, CTRL:$ctrl_port"
        else
            # Just show the ports if no symlinks
            port_details=$(ls /dev/ttyUSB[0-9]* 2>/dev/null | xargs -n1 basename | tr '\n' ',' | sed 's/,$//')
        fi

        usb_info="$port_count ports ($port_details)"

        # Find which services are using the modem
        local services=$(sudo lsof /dev/ttyUSB[0-9]* 2>/dev/null | awk 'NR>1 {print $1}' | sort -u | tr '\n' ', ' | sed 's/,$//')

        if [ -z "$services" ]; then
            service_info="Idle"
        else
            service_info="Active: $services"
        fi
    fi

    # Build complete message with USB info inserted after first line, before model details
    local message=""

    # Split ec25_status into lines
    local first_line=$(echo "$ec25_status" | head -1)
    local remaining_lines=$(echo "$ec25_status" | tail -n +2)

    # Build message: Line 1, then USB info, then remaining lines (Config, Model, SIM)
    message="$first_line"

    if [ -n "$usb_info" ]; then
        message+=$'\n'"**USB:** $usb_info | **Status:** $service_info"
    fi

    if [ -n "$remaining_lines" ]; then
        message+=$'\n'"$remaining_lines"
    fi

    # Check signal strength for severity
    if echo "$ec25_status" | grep -q "Signal:"; then
        local signal=$(echo "$ec25_status" | grep -o "Signal: [0-9]*%" | grep -o "[0-9]*")
        if [ -n "$signal" ] && [ "$signal" -lt 20 ] 2>/dev/null; then
            send_notification "warning" "$message"
        else
            send_notification "info" "$message"
        fi
    else
        send_notification "info" "$message"
    fi
}

# Service monitoring
check_service() {
    local service_name="$1"
    if [ -z "$service_name" ]; then
        send_notification "error" "No service name provided"
        return
    fi
    
    if systemctl is-active --quiet "$service_name"; then
        send_notification "info" "Service $service_name is running"
    else
        send_notification "error" "Service $service_name is not running"
    fi
}

# Network connectivity test
check_network() {
    local voice_status="❌ Unreachable"
    local bookings_status="❌ Unreachable"
    local severity="critical"

    # Check voice.rom2.co.uk
    if curl -s --head --connect-timeout 5 https://voice.rom2.co.uk > /dev/null; then
        voice_status="✓ Reachable"
    fi

    # Check my-bookings.co.uk
    if curl -s --head --connect-timeout 5 https://my-bookings.co.uk > /dev/null; then
        bookings_status="✓ Reachable"
    fi

    # Determine severity
    if [[ "$voice_status" == *"Reachable"* ]] && [[ "$bookings_status" == *"Reachable"* ]]; then
        severity="info"
    elif [[ "$voice_status" == *"Reachable"* ]] || [[ "$bookings_status" == *"Reachable"* ]]; then
        severity="warning"
    fi

    local message="**Network Status:**"$'\n'"voice.rom2.co.uk: ${voice_status}"$'\n'"my-bookings.co.uk: ${bookings_status}"

    send_notification "$severity" "$message"
}

# Export function for EC25 status
export -f get_ec25_status

# Main script logic
case "${1:-}" in
    "vpn")
        check_vpn_status
        ;;
    "system")
        check_system_health
        ;;
    "system-full")
        comprehensive_system_check
        ;;
    "service")
        check_service "${2:-}"
        ;;
    "network")
        check_network
        ;;
    "ec25")
        check_ec25
        ;;
    "test")
        send_notification "info" "Test message from $HOSTNAME"
        ;;
    "custom")
        # Custom message: pi_send_message.sh custom "message" [severity]
        custom_message="${2:-No message provided}"
        custom_severity="${3:-info}"
        
        # Validate severity level
        case "$custom_severity" in
            info|warning|error|critical)
                send_notification "$custom_severity" "$custom_message"
                ;;
            *)
                # Invalid severity, default to info
                send_notification "info" "$custom_message"
                ;;
        esac
        ;;
    *)
        # If no recognized command, treat first parameter as custom message
        if [ -n "$1" ]; then
            # Custom message shorthand: pi_send_message.sh "message" [severity]
            custom_message="$1"
            custom_severity="${2:-info}"
            
            # Validate severity level
            case "$custom_severity" in
                info|warning|error|critical)
                    send_notification "$custom_severity" "$custom_message"
                    ;;
                *)
                    # Invalid severity, default to info
                    send_notification "info" "$custom_message"
                    ;;
            esac
        else
            echo "Usage: $0 {vpn|system|system-full|service <name>|network|ec25|test|custom <message> [severity]}"
            echo "       $0 \"message\" [severity]"
            echo ""
            echo "Commands:"
            echo "  vpn         - Check VPN connectivity"
            echo "  system      - Quick system health check"
            echo "  system-full - Comprehensive system report"
            echo "  service     - Check if service is running"
            echo "  network     - Check network connectivity"
            echo "  ec25        - Check EC25 modem status"
            echo "  test        - Send test message"
            echo "  custom      - Send custom message"
            echo ""
            echo "Custom message examples:"
            echo "  $0 custom \"Backup completed successfully\""
            echo "  $0 custom \"Disk space low\" warning"
            echo "  $0 \"Temperature sensor offline\" error"
            echo ""
            echo "Severity levels: info, warning, error, critical (default: info)"
            exit 1
        fi
        ;;
esac