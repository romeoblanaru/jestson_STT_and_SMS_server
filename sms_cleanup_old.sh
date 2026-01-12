#!/bin/bash
###############################################################################
# SMS Old Messages Cleanup Script
# Deletes failed SMS messages older than 31 days
# Runs daily at midnight via cron
###############################################################################

FAILED_DIR="/var/spool/sms/failed"
LOG_FILE="/var/log/voice_bot_ram/sms_cleanup.log"
DAYS_OLD=31

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

log "=== Starting SMS cleanup (delete messages older than $DAYS_OLD days) ==="

# Find and delete messages older than 31 days
DELETED_COUNT=0
while IFS= read -r -d '' file; do
    filename=$(basename "$file")
    log "Deleting: $filename"
    rm -f "$file" && ((DELETED_COUNT++))
done < <(find "$FAILED_DIR" -type f -mtime +$DAYS_OLD -print0 2>/dev/null)

log "=== Cleanup completed: $DELETED_COUNT messages deleted ==="

# Log remaining count
REMAINING=$(find "$FAILED_DIR" -type f 2>/dev/null | wc -l)
log "Remaining failed messages: $REMAINING"

exit 0
