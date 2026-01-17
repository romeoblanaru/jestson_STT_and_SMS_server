#!/bin/bash
###############################################################################
# Update SMSD configuration for EC25 modem
###############################################################################

echo "Stopping SMSD..."
sudo systemctl stop smstools

echo "Updating SMSD configuration for EC25..."
sudo sed -i 's/^check_memory_method = .*/check_memory_method = 1/' /etc/smsd.conf
sudo sed -i 's/^sentsleeptime = .*/sentsleeptime = 1/' /etc/smsd.conf
sudo sed -i 's/^delaytime = .*/delaytime = 1/' /etc/smsd.conf

echo "Configuration updated:"
grep -E "check_memory_method|sentsleeptime|delaytime" /etc/smsd.conf | grep -v "^#"

echo ""
echo "Starting SMSD..."
sudo systemctl start smstools

sleep 3

echo ""
echo "SMSD status:"
systemctl status smstools --no-pager -l | head -15

echo ""
echo "Checking recent log:"
tail -10 /var/log/smstools/smsd.log
