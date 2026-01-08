#!/bin/bash
# SMS Queue Cleanup - Runs every minute
# Prevents stuck messages and .LOCK files

# Remove .LOCK files older than 2 minutes (stuck processing)
find /var/spool/sms/checked/ -name "*.LOCK" -mmin +2 -delete 2>/dev/null

# Move messages stuck in checked (older than 3 minutes) back to outgoing for retry
find /var/spool/sms/checked/ -name "api_*" ! -name "*.LOCK" -mmin +3 -exec mv {} /var/spool/sms/outgoing/ \; 2>/dev/null

# Clean up old failed messages (older than 1 hour)
find /var/spool/sms/failed/ -name "api_*" -mmin +60 -delete 2>/dev/null

# Log cleanup action
if [ -n "$(find /var/spool/sms/checked/ -name '*.LOCK' 2>/dev/null)" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Cleanup: Removed stuck .LOCK files" >> /var/log/sms_cleanup.log
fi
