#!/bin/bash
if ! systemctl is-active --quiet gammu-smsd; then
    echo "[$(date)] Gammu-SMSD down, restarting..." >> /var/log/gammu_monitor.log
    echo 'Romy_1202' | sudo -S systemctl start gammu-smsd >> /var/log/gammu_monitor.log 2>&1
fi
