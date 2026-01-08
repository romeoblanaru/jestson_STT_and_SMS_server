#!/bin/bash
#
# Install and update all system services
# This script organizes and installs all custom services
#

echo "=========================================="
echo "Installing System Services"
echo "=========================================="

SERVICES_DIR="/home/rom/system_services"
SYSTEMD_DIR="/etc/systemd/system"

# List of services to install
SERVICES=(
    "ec25-voice-bot.service"
    "voice-config-init.service"
    "phone-call-api.service"
    "monitoring-webhook.service"
    "ec25-audio-setup.service"
    "unified-modem.service"
    "wg-failover.service"
)

echo "Installing services from $SERVICES_DIR to $SYSTEMD_DIR"
echo ""

# Copy each service file
for SERVICE in "${SERVICES[@]}"; do
    if [ -f "$SERVICES_DIR/$SERVICE" ]; then
        echo "Installing $SERVICE..."
        echo "Romy_1202" | sudo -S cp "$SERVICES_DIR/$SERVICE" "$SYSTEMD_DIR/$SERVICE"
        echo "Romy_1202" | sudo -S chmod 644 "$SYSTEMD_DIR/$SERVICE"
        echo "✓ Installed $SERVICE"
    else
        echo "⚠ Warning: $SERVICE not found in $SERVICES_DIR"
    fi
done

echo ""
echo "Reloading systemd daemon..."
echo "Romy_1202" | sudo -S systemctl daemon-reload

echo ""
echo "Enabling services..."

# Enable critical services
echo "Romy_1202" | sudo -S systemctl enable voice-config-init.service
echo "✓ Enabled voice-config-init"

echo "Romy_1202" | sudo -S systemctl enable phone-call-api.service
echo "✓ Enabled phone-call-api"

echo "Romy_1202" | sudo -S systemctl enable ec25-voice-bot.service
echo "✓ Enabled ec25-voice-bot"

echo ""
echo "Starting services..."

# Start voice configuration first
echo "Romy_1202" | sudo -S systemctl start voice-config-init.service
echo "✓ Started voice-config-init"

# Wait for config to load
sleep 5

# Start phone call API
echo "Romy_1202" | sudo -S systemctl start phone-call-api.service
echo "✓ Started phone-call-api"

# Restart voice bot with new config
echo "Romy_1202" | sudo -S systemctl restart ec25-voice-bot.service
echo "✓ Restarted ec25-voice-bot"

echo ""
echo "=========================================="
echo "Service Installation Complete!"
echo "=========================================="
echo ""
echo "Check status with:"
echo "  systemctl status voice-config-init"
echo "  systemctl status phone-call-api"
echo "  systemctl status ec25-voice-bot"
echo ""
echo "View logs with:"
echo "  journalctl -u voice-config-init -f"
echo "  journalctl -u phone-call-api -f"
echo "  journalctl -u ec25-voice-bot -f"