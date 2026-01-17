#!/bin/bash
# Install EC25 Port Monitor systemd timer

echo "Installing EC25 Port Monitor..."

# Copy service and timer files
cp /tmp/ec25-port-monitor.service /etc/systemd/system/
cp /tmp/ec25-port-monitor.timer /etc/systemd/system/

# Disable old udev-based detection service
systemctl disable ec25-port-setup.service 2>/dev/null || true

# Reload systemd
systemctl daemon-reload

# Enable and start the timer
systemctl enable ec25-port-monitor.timer
systemctl start ec25-port-monitor.timer

echo ""
echo "✅ EC25 Port Monitor installed and started!"
echo ""
echo "Status:"
systemctl status ec25-port-monitor.timer --no-pager -l

echo ""
echo "How it works:"
echo "- Checks every 30 seconds if /dev/ttyUSB_AT is correct"
echo "- If broken or wrong, fixes it automatically"
echo "- Restarts SMSTools if port changes"
echo "- Logs to /var/log/ec25_port_monitor.log"
echo ""
echo "Manual commands:"
echo "  Check status:  systemctl status ec25-port-monitor.timer"
echo "  Run now:       systemctl start ec25-port-monitor.service"
echo "  View log:      cat /var/log/ec25_port_monitor.log"
echo "  Disable:       systemctl stop ec25-port-monitor.timer"
