#!/bin/bash
###############################################################################
# Internet Failover Script - Enhanced with Passive/Active Modes
# Monitors primary internet (WiFi/LAN) and manages EC25 backup
###############################################################################

# Load configuration
source /home/rom/lte_config.sh

LOG="/var/log/internet_failover.log"
CHECK_HOST="8.8.8.8"
WIFI_INTERFACE="wlP1p1s0"
LAN_INTERFACE="enP8p1s0"

# Auto-detect EC25 CDC Ethernet interface (enx* pattern on 192.168.225.x network)
# This handles dynamic interface name changes when modem reconnects
detect_ec25_interface() {
    # Look for enx* interfaces with 192.168.225.x IP
    local interface=$(ip -4 addr show | grep -B2 "inet 192.168.225" | grep -oP "enx[0-9a-f]+" | head -1)

    # Fallback: look for any UP enx* interface
    if [ -z "$interface" ]; then
        interface=$(ip link show | grep -oP "enx[0-9a-f]+(?=:.*state UP)" | head -1)
    fi

    echo "$interface"
}

EC25_INTERFACE=$(detect_ec25_interface)
EC25_GATEWAY="192.168.225.1"  # EC25 modem always uses this gateway
LOCKFILE="/var/run/internet_failover.lock"
ROUTE_MARKER="999"  # High metric for EC25 route (low priority - last resort)
NOTIFICATION_SENT_FILE="/var/run/internet_failover_4g_notified"

# Prevent multiple instances
if [ -f "$LOCKFILE" ]; then
    exit 0
fi
touch "$LOCKFILE"
trap "rm -f $LOCKFILE" EXIT

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

# Send notification to VPS
send_notification() {
    local message="$1"
    local level="$2"
    /home/rom/pi_send_message.sh "$message" "$level" 2>&1 >> "$LOG"
}

# Check if primary internet (WiFi or LAN) is working
check_primary_internet() {
    # Try WiFi first
    if ip link show "$WIFI_INTERFACE" 2>/dev/null | grep -q "state UP"; then
        if ping -c 2 -W 3 -I "$WIFI_INTERFACE" "$CHECK_HOST" > /dev/null 2>&1; then
            return 0
        fi
    fi

    # Try LAN if WiFi failed
    if ip link show "$LAN_INTERFACE" 2>/dev/null | grep -q "state UP"; then
        if ping -c 2 -W 3 -I "$LAN_INTERFACE" "$CHECK_HOST" > /dev/null 2>&1; then
            return 0
        fi
    fi

    return 1
}

# Check if EC25 interface is up
check_ec25_interface() {
    if [ -z "$EC25_INTERFACE" ]; then
        return 1
    fi
    # CDC Ethernet interfaces may show state UNKNOWN instead of UP
    if ip link show "$EC25_INTERFACE" 2>/dev/null | grep -qE "state (UP|UNKNOWN)"; then
        return 0
    fi
    return 1
}

# Check if EC25 route exists
check_ec25_route() {
    if ip route show | grep -q "default via $EC25_GATEWAY.*metric $ROUTE_MARKER"; then
        return 0
    fi
    return 1
}

# Check if traffic is currently using EC25
check_ec25_in_use() {
    # Get the actual route being used for internet
    local active_route=$(ip route get $CHECK_HOST 2>/dev/null | head -1)
    if echo "$active_route" | grep -q "$EC25_INTERFACE"; then
        return 0
    fi
    return 1
}

###############################################################################
# MODE 1: LTE_4G_ENABLED=OFF
# Completely disable 4G backup
###############################################################################
if [ "$LTE_4G_ENABLED" = "OFF" ]; then
    log "LTE 4G disabled - removing all EC25 routes"

    # Remove any existing EC25 routes
    sudo ip route del default via "$EC25_GATEWAY" dev "$EC25_INTERFACE" 2>/dev/null
    sudo ip route del default via "$EC25_GATEWAY" dev "$EC25_INTERFACE" metric "$ROUTE_MARKER" 2>/dev/null

    # Clean up notification flag
    rm -f "$NOTIFICATION_SENT_FILE"

    exit 0
fi

# Verify EC25 interface is available
if ! check_ec25_interface; then
    log "WARNING: EC25 CDC Ethernet interface not detected - backup unavailable"
    exit 0
fi

###############################################################################
# MODE 2: LTE_4G_ENABLED=ON, LTE_4G_FAILOVER=OFF (PASSIVE MODE - DEFAULT)
# 4G route always present (metric 999), Linux routing chooses automatically
# Notify when 4G is in use, hourly check for WiFi/LAN recovery
###############################################################################
if [ "$LTE_4G_ENABLED" = "ON" ] && [ "$LTE_4G_FAILOVER" = "OFF" ]; then
    # Ensure EC25 route exists with metric 999 (last resort priority)
    if ! check_ec25_route; then
        # Remove any low-metric DHCP route
        sudo ip route del default via "$EC25_GATEWAY" dev "$EC25_INTERFACE" 2>/dev/null

        # Add high-metric backup route
        sudo ip route add default via "$EC25_GATEWAY" dev "$EC25_INTERFACE" metric "$ROUTE_MARKER" 2>/dev/null
        log "Passive mode: EC25 backup route established (metric $ROUTE_MARKER)"
    fi

    # Check if we're currently using 4G
    if check_ec25_in_use; then
        # 4G is being used - send notification if not already sent
        if [ ! -f "$NOTIFICATION_SENT_FILE" ]; then
            log "⚠️ Traffic using EC25 LTE backup (WiFi/LAN unavailable)"
            send_notification "⚠️ Internet via EC25 LTE Backup - WiFi/LAN down (Passive failover)" "warning"
            touch "$NOTIFICATION_SENT_FILE"
        fi

        # Check if primary internet came back
        if check_primary_internet; then
            log "✅ Primary internet restored - traffic will switch automatically"
            send_notification "✅ Primary Internet Restored - EC25 LTE now standby (Passive mode)" "info"
            rm -f "$NOTIFICATION_SENT_FILE"
        fi
    else
        # Primary internet is being used - clean up notification flag
        if [ -f "$NOTIFICATION_SENT_FILE" ]; then
            log "✅ Traffic using primary internet (WiFi/LAN)"
            rm -f "$NOTIFICATION_SENT_FILE"
        fi
    fi

    exit 0
fi

###############################################################################
# MODE 3: LTE_4G_ENABLED=ON, LTE_4G_FAILOVER=ON (ACTIVE MODE)
# Script actively manages routes - adds EC25 when WiFi/LAN fail, removes when they return
###############################################################################
if [ "$LTE_4G_ENABLED" = "ON" ] && [ "$LTE_4G_FAILOVER" = "ON" ]; then
    log "Active failover mode enabled"

    # Add EC25 route (active mode)
    add_ec25_route() {
        log "Primary internet failed - Activating EC25 backup connection (Active mode)..."

        if ! check_ec25_interface; then
            log "ERROR: EC25 interface $EC25_INTERFACE is not available"
            return 1
        fi

        # Remove any low-metric DHCP route that EC25 might have created
        sudo ip route del default via "$EC25_GATEWAY" dev "$EC25_INTERFACE" 2>/dev/null

        # Add default route with HIGH metric (low priority - only used as backup)
        sudo ip route add default via "$EC25_GATEWAY" dev "$EC25_INTERFACE" metric "$ROUTE_MARKER" 2>/dev/null

        # Verify it works
        if ping -c 2 -W 3 -I "$EC25_INTERFACE" "$CHECK_HOST" > /dev/null 2>&1; then
            log "EC25 backup connection active (ping: OK)"
            send_notification "⚠️ Internet Failover: Switched to EC25 LTE backup (Primary internet down - Active mode)" "warning"
            return 0
        else
            log "EC25 interface up but internet not reachable"
            sudo ip route del default via "$EC25_GATEWAY" dev "$EC25_INTERFACE" metric "$ROUTE_MARKER" 2>/dev/null
            return 1
        fi
    }

    # Remove EC25 route (active mode)
    remove_ec25_route() {
        log "Primary internet restored - Deactivating EC25 backup connection (Active mode)..."
        # Remove high-metric backup route
        sudo ip route del default via "$EC25_GATEWAY" dev "$EC25_INTERFACE" metric "$ROUTE_MARKER" 2>/dev/null
        # Also remove any low-metric DHCP route that might have been created
        sudo ip route del default via "$EC25_GATEWAY" dev "$EC25_INTERFACE" 2>/dev/null
        log "EC25 backup route removed, using primary internet"
        send_notification "✅ Internet Restored: Switched back to primary connection (EC25 backup inactive - Active mode)" "info"
    }

    # Active failover logic
    if check_primary_internet; then
        # Primary internet (WiFi or LAN) is working
        if check_ec25_route; then
            # EC25 route is active but primary works - remove EC25 route
            remove_ec25_route
        else
            # Primary working, EC25 not active - also clean up any DHCP routes
            sudo ip route del default via "$EC25_GATEWAY" dev "$EC25_INTERFACE" 2>/dev/null
        fi
    else
        # Primary internet is down
        if ! check_ec25_route; then
            # EC25 route not active - add it
            add_ec25_route
        fi
    fi

    exit 0
fi

# Should never reach here
log "ERROR: Invalid configuration state"
exit 1
