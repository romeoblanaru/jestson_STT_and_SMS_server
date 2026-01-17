#!/bin/bash
###############################################################################
# EC25 Internet Backup Setup
# Configure PPP internet failover without interfering with SMS gateway
###############################################################################

set -e

LOG="/var/log/ec25_internet_setup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

log "=========================================="
log "EC25 Internet Backup Configuration"
log "=========================================="

# 1. Install required packages
log "Installing PPP and ModemManager..."
sudo apt update
sudo apt install -y ppp modemmanager libqmi-utils

# 2. Create udev rule to prevent ModemManager from touching ttyUSB2 (SMSTools)
log "Creating udev rule to protect ttyUSB2 from ModemManager..."

sudo tee /etc/udev/rules.d/99-modemmanager-ec25.rules > /dev/null << 'EOF'
# EC25 Modem - Prevent ModemManager from managing ttyUSB2 (reserved for SMSTools)
# ttyUSB2 is for SMS gateway only, ttyUSB3 is for data/internet

# Identify EC25 modem
SUBSYSTEM=="tty", ATTRS{idVendor}=="2c7c", ATTRS{idProduct}=="0125", ENV{ID_MM_DEVICE_IGNORE}="1"

# But allow ModemManager to manage the modem for data on other ports
SUBSYSTEM=="usb", ATTRS{idVendor}=="2c7c", ATTRS{idProduct}=="0125", ENV{ID_MM_CANDIDATE}="1"

# Block ModemManager from ttyUSB2 specifically
SUBSYSTEM=="tty", KERNEL=="ttyUSB2", ENV{ID_MM_DEVICE_IGNORE}="1"

# Allow ModemManager on ttyUSB3 for data
SUBSYSTEM=="tty", KERNEL=="ttyUSB3", ENV{ID_MM_PORT_TYPE_AT_PRIMARY}="1"
EOF

log "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# 3. Configure ModemManager to use specific ports
log "Configuring ModemManager..."

# Stop ModemManager temporarily
sudo systemctl stop ModemManager 2>/dev/null || true

# Start ModemManager
sudo systemctl enable ModemManager
sudo systemctl start ModemManager

# Wait for ModemManager to detect modem
log "Waiting for ModemManager to detect modem..."
sleep 5

# 4. Create PPP configuration for EC25
log "Creating PPP peer configuration..."

sudo tee /etc/ppp/peers/ec25-backup > /dev/null << 'EOF'
# EC25 Internet Backup Connection
# Uses ttyUSB3 to avoid conflict with SMSTools on ttyUSB2

# Serial port (using ttyUSB3 - not ttyUSB2 which is for SMS)
/dev/ttyUSB3
115200

# Hardware flow control
crtscts

# Modem control lines
modem

# Don't use modem's IP as default route (WiFi is primary)
nodefaultroute

# Get IP from peer
noipdefault

# Use peer DNS (but as secondary)
usepeerdns

# No authentication required
noauth

# Keep trying if connection fails
persist

# Maximum failure attempts before giving up
maxfail 0

# Connect script
connect '/usr/sbin/chat -v -f /etc/ppp/chat-ec25-backup'

# Disconnect script
disconnect '/usr/sbin/chat -v -f /etc/ppp/chat-ec25-disconnect'

# Log to syslog
debug
EOF

# 5. Create chat scripts
log "Creating chat scripts..."

sudo tee /etc/ppp/chat-ec25-backup > /dev/null << 'EOF'
ABORT 'BUSY'
ABORT 'NO CARRIER'
ABORT 'ERROR'
TIMEOUT 30
'' AT
OK ATZ
OK AT+CFUN=1
OK AT+CGDCONT=1,"IP","internet"
OK ATD*99#
CONNECT ''
EOF

sudo tee /etc/ppp/chat-ec25-disconnect > /dev/null << 'EOF'
ABORT "ERROR"
ABORT "NO DIALTONE"
"" "\K"
"" "+++ATH0"
SAY "Disconnected"
EOF

# 6. Create failover monitoring script
log "Creating internet failover script..."

tee /home/rom/internet_failover.sh > /dev/null << 'EOF'
#!/bin/bash
###############################################################################
# Internet Failover Script
# Monitors WiFi and switches to EC25 backup if WiFi fails
###############################################################################

LOG="/var/log/internet_failover.log"
CHECK_HOST="8.8.8.8"
WIFI_INTERFACE="wlP1p1s0"
PPP_PEER="ec25-backup"
LOCKFILE="/var/run/internet_failover.lock"

# Prevent multiple instances
if [ -f "$LOCKFILE" ]; then
    exit 0
fi
touch "$LOCKFILE"
trap "rm -f $LOCKFILE" EXIT

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

# Check if WiFi is working
check_wifi() {
    if ip link show "$WIFI_INTERFACE" 2>/dev/null | grep -q "state UP"; then
        if ping -c 2 -W 3 -I "$WIFI_INTERFACE" "$CHECK_HOST" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Check if PPP is active
check_ppp() {
    if ip link show ppp0 2>/dev/null | grep -q "state UNKNOWN"; then
        return 0
    fi
    return 1
}

# Start PPP backup
start_ppp() {
    log "WiFi failed - Starting EC25 backup connection..."
    sudo /usr/bin/pon "$PPP_PEER"
    sleep 10

    if check_ppp; then
        log "EC25 backup connection established"
        # Send notification to VPS
        /home/rom/pi_send_message.sh "⚠️ Internet Failover: Switched to EC25 backup (WiFi down)" "warning"
        return 0
    else
        log "Failed to establish EC25 backup connection"
        return 1
    fi
}

# Stop PPP backup
stop_ppp() {
    log "WiFi restored - Stopping EC25 backup connection..."
    sudo /usr/bin/poff "$PPP_PEER"
    sleep 3
    log "EC25 backup connection stopped"
    # Send notification to VPS
    /home/rom/pi_send_message.sh "✅ Internet Restored: Switched back to WiFi (EC25 backup stopped)" "info"
}

# Main logic
if check_wifi; then
    # WiFi is working
    if check_ppp; then
        # PPP is active but WiFi works - stop PPP
        stop_ppp
    fi
else
    # WiFi is down
    if ! check_ppp; then
        # PPP is not active - start it
        start_ppp
    else
        log "WiFi down, EC25 backup already active"
    fi
fi
EOF

chmod +x /home/rom/internet_failover.sh

# 7. Create systemd service for automatic failover
log "Creating failover monitoring service..."

sudo tee /etc/systemd/system/internet-failover.service > /dev/null << 'EOF'
[Unit]
Description=Internet Failover Monitor (WiFi to EC25)
After=network.target ModemManager.service

[Service]
Type=oneshot
ExecStart=/home/rom/internet_failover.sh
User=root

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/internet-failover.timer > /dev/null << 'EOF'
[Unit]
Description=Internet Failover Monitor Timer
Requires=internet-failover.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=1min
AccuracySec=10s

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable internet-failover.timer
sudo systemctl start internet-failover.timer

log "=========================================="
log "Configuration Complete!"
log "=========================================="
log ""
log "Summary:"
log "  • ttyUSB2: Protected for SMSTools (no interference)"
log "  • ttyUSB3: Available for ModemManager/PPP data"
log "  • Failover: Monitors WiFi every minute"
log "  • Automatic: Switches to EC25 when WiFi fails"
log ""
log "SMSTools will NOT be affected - it keeps using ttyUSB2"
log ""
log "Next steps:"
log "  1. Verify: systemctl status internet-failover.timer"
log "  2. Test failover: sudo /home/rom/internet_failover.sh"
log "  3. Check logs: tail -f /var/log/internet_failover.log"

echo ""
echo "Setup complete! Check $LOG for details."
EOF
