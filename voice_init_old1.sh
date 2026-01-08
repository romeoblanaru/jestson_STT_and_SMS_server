#!/bin/bash
#
# Voice Configuration Initialization Script
# Runs after WireGuard connection is established
# Fetches configuration from VPS and applies settings
#

LOG_FILE="/var/log/voice_init.log"
CONFIG_MANAGER="/home/rom/voice_config_manager.py"
MAX_RETRIES=5
RETRY_DELAY=10

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check WireGuard connection
check_wireguard() {
    if sudo wg show wg0 2>/dev/null | grep -q "latest handshake"; then
        return 0
    else
        return 1
    fi
}

# Function to get VPN IP
get_vpn_ip() {
    ip addr show wg0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d'/' -f1
}

# Main initialization
main() {
    log_message "========================================="
    log_message "Starting Voice Configuration Init"
    log_message "========================================="

    # Wait for WireGuard to be ready
    log_message "Waiting for WireGuard connection..."
    WAIT_COUNT=0
    while [ $WAIT_COUNT -lt 30 ]; do
        if check_wireguard; then
            VPN_IP=$(get_vpn_ip)
            log_message "✅ WireGuard connected: $VPN_IP"
            break
        fi
        sleep 2
        WAIT_COUNT=$((WAIT_COUNT + 1))
    done

    if [ $WAIT_COUNT -eq 30 ]; then
        log_message "❌ WireGuard connection timeout!"
        exit 1
    fi

    # Small delay to ensure network is stable
    sleep 3

    # Run voice configuration manager
    log_message "Fetching voice configuration..."
    RETRY_COUNT=0
    SUCCESS=false

    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if python3 "$CONFIG_MANAGER" 2>&1 | tee -a "$LOG_FILE"; then
            SUCCESS=true
            log_message "✅ Voice configuration applied successfully!"
            break
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            log_message "⚠️ Configuration failed (attempt $RETRY_COUNT/$MAX_RETRIES)"

            if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
                log_message "Waiting ${RETRY_DELAY}s before retry..."
                sleep $RETRY_DELAY
            fi
        fi
    done

    if [ "$SUCCESS" = false ]; then
        log_message "❌ Failed to apply voice configuration after $MAX_RETRIES attempts"

        # Check if cached config exists
        if [ -f "/home/rom/voice_config.json" ]; then
            log_message "📋 Using cached configuration"
            # Restart voice bot with cached config
            sudo systemctl restart ec25-voice-bot
        else
            log_message "❌ No cached configuration available"
            exit 1
        fi
    fi

    # Verify services are running
    sleep 5
    log_message "Checking services status..."

    # Check voice bot service
    if systemctl is-active --quiet ec25-voice-bot; then
        log_message "✅ ec25-voice-bot service is running"
    else
        log_message "⚠️ ec25-voice-bot service is not running"
        sudo systemctl start ec25-voice-bot
    fi

    # Send notification to monitoring
    if [ "$SUCCESS" = true ]; then
        /home/rom/pi_send_message.sh "Voice system initialized: VPN=$VPN_IP" "info" 2>/dev/null || true
    else
        /home/rom/pi_send_message.sh "Voice init: Using cached config" "warning" 2>/dev/null || true
    fi

    log_message "Voice initialization complete!"
    log_message "========================================="
}

# Run main function
main "$@"