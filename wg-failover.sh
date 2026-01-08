#!/bin/bash

WG_INTERFACE="wg0"
PING_HOST="10.100.0.1"
PING_COUNT=3
PING_TIMEOUT=5
CHECK_INTERVAL=30
MAX_FAILURES=3
MESSAGE_SCRIPT="/home/rom/SMS_Gateway/pi_send_message.sh"

failure_count=0
disconnection_start=""
was_disconnected=false

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

send_notification() {
    local message="$1"
    local severity="${2:-info}"
    
    if [ -x "$MESSAGE_SCRIPT" ]; then
        "$MESSAGE_SCRIPT" "$message" "$severity"
    fi
}

check_wg_interface() {
    if ! ip link show "$WG_INTERFACE" &>/dev/null; then
        return 1
    fi
    
    if ! ip link show "$WG_INTERFACE" | grep -q "UP"; then
        return 1
    fi
    
    return 0
}

check_wg_handshake() {
    local last_handshake=$(sudo wg show "$WG_INTERFACE" latest-handshakes | awk '{print $2}')
    
    if [ -z "$last_handshake" ]; then
        return 1
    fi
    
    local current_time=$(date +%s)
    local time_diff=$((current_time - last_handshake))
    
    if [ "$time_diff" -gt 180 ]; then
        return 1
    fi
    
    return 0
}

check_connectivity() {
    ping -c "$PING_COUNT" -W "$PING_TIMEOUT" -I "$WG_INTERFACE" "$PING_HOST" &>/dev/null
    return $?
}

restart_wireguard() {
    log_message "Restarting WireGuard interface $WG_INTERFACE"
    
    sudo wg-quick down "$WG_INTERFACE" 2>/dev/null
    sleep 2
    sudo wg-quick up "$WG_INTERFACE"
    
    sleep 5
    
    if check_wg_interface && check_connectivity; then
        log_message "WireGuard restarted successfully"
        return 0
    else
        log_message "Failed to restart WireGuard"
        return 1
    fi
}

log_message "WireGuard failover monitor started for interface $WG_INTERFACE"

while true; do
    if ! check_wg_interface; then
        log_message "WARNING: WireGuard interface $WG_INTERFACE is down"
        failure_count=$((failure_count + 1))
    elif ! check_wg_handshake; then
        log_message "WARNING: WireGuard handshake is stale (>3 minutes)"
        failure_count=$((failure_count + 1))
    elif ! check_connectivity; then
        log_message "WARNING: Cannot ping $PING_HOST through WireGuard"
        failure_count=$((failure_count + 1))
    else
        if [ "$failure_count" -gt 0 ] || [ "$was_disconnected" = true ]; then
            log_message "Connection restored"
            
            if [ "$was_disconnected" = true ] && [ -n "$disconnection_start" ]; then
                local current_time=$(date +%s)
                local downtime=$((current_time - disconnection_start))
                local downtime_minutes=$((downtime / 60))
                local downtime_seconds=$((downtime % 60))
                
                local downtime_msg="WireGuard connection restored after ${downtime_minutes}m ${downtime_seconds}s of downtime"
                log_message "$downtime_msg"
                send_notification "$downtime_msg" "warning"
                
                disconnection_start=""
                was_disconnected=false
            fi
        fi
        failure_count=0
    fi
    
    if [ "$failure_count" -ge "$MAX_FAILURES" ]; then
        log_message "ERROR: $failure_count consecutive failures detected"
        
        if [ "$was_disconnected" = false ]; then
            disconnection_start=$(date +%s)
            was_disconnected=true
            send_notification "WireGuard connection lost - attempting restart" "error"
        fi
        
        if restart_wireguard; then
            failure_count=0
            
            if [ "$was_disconnected" = true ] && [ -n "$disconnection_start" ]; then
                local current_time=$(date +%s)
                local downtime=$((current_time - disconnection_start))
                local downtime_minutes=$((downtime / 60))
                local downtime_seconds=$((downtime % 60))
                
                local recovery_msg="WireGuard restarted successfully after ${downtime_minutes}m ${downtime_seconds}s downtime"
                log_message "$recovery_msg"
                send_notification "$recovery_msg" "info"
                
                disconnection_start=""
                was_disconnected=false
            fi
        else
            log_message "ERROR: Restart failed, will retry in next cycle"
            if [ "$failure_count" -eq "$MAX_FAILURES" ]; then
                send_notification "WireGuard restart failed - manual intervention may be needed" "critical"
            fi
        fi
    fi
    
    sleep "$CHECK_INTERVAL"
done