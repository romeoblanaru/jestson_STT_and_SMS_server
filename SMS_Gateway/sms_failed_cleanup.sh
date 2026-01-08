#!/bin/bash
# SMS Failed Messages Cleanup Script
# Removes failed SMS older than 3 minutes to prevent endless retries

FAILED_DIR="/var/spool/sms/failed"
MAX_AGE_MINUTES=3
LOG_FILE="/var/log/sms_failed_cleanup.log"

# Create log entry
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting failed SMS cleanup" >> "$LOG_FILE"

# Find and remove failed SMS files older than 3 minutes
if [ -d "$FAILED_DIR" ]; then
    # Count files before cleanup
    BEFORE_COUNT=$(find "$FAILED_DIR" -type f -name "*" 2>/dev/null | wc -l)
    
    # Remove old files
    find "$FAILED_DIR" -type f -mmin +${MAX_AGE_MINUTES} -exec rm -f {} \; 2>/dev/null
    
    # Count files after cleanup
    AFTER_COUNT=$(find "$FAILED_DIR" -type f -name "*" 2>/dev/null | wc -l)
    
    # Calculate removed files
    REMOVED=$((BEFORE_COUNT - AFTER_COUNT))
    
    if [ $REMOVED -gt 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Removed $REMOVED failed SMS files older than $MAX_AGE_MINUTES minutes" >> "$LOG_FILE"
    fi
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Failed directory not found: $FAILED_DIR" >> "$LOG_FILE"
fi