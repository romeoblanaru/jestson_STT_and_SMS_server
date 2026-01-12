#!/bin/bash
# SMS Failed Messages Auto-Retry Script
# Moves failed messages back to outgoing for retry
# Runs every 3 minutes via cron
# LIMITS: Only 1 message per run AND only if outgoing folder is empty

FAILED_DIR="/var/spool/sms/failed"
OUTGOING_DIR="/var/spool/sms/outgoing"
LOG_FILE="/var/log/voice_bot_ram/sms_retry.log"  # Use existing log folder with permissions
MAX_RETRIES=3  # Maximum number of retry attempts per message
BATCH_SIZE=1   # Only retry 1 message per run for debugging

# Ensure log file exists
touch "$LOG_FILE"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log "=== Starting failed message retry check ==="

# CRITICAL: Check if outgoing folder is empty first
# FIXED: Check ALL files, not just api_* (includes modem_status_*, test_*, etc)
OUTGOING_COUNT=$(find "$OUTGOING_DIR" -type f ! -name "*.LOCK" 2>/dev/null | wc -l)
if [ "$OUTGOING_COUNT" -gt 0 ]; then
    log "SKIP: Outgoing folder not empty ($OUTGOING_COUNT messages pending), skipping retry"
    exit 0
fi

# Count messages in failed folder
# FIXED: Count ALL failed messages, not just api_*
FAILED_COUNT=$(find "$FAILED_DIR" -type f ! -name "*.LOCK" 2>/dev/null | wc -l)
log "Found $FAILED_COUNT failed messages, outgoing folder is empty"

if [ "$FAILED_COUNT" -eq 0 ]; then
    log "No failed messages to retry"
    exit 0
fi

# Counter for batch size limit
processed=0

# Process each failed message (limited to BATCH_SIZE)
# FIXED: Process ALL files (*), not just api_* (includes modem_status_*, test_*, etc)
for failed_msg in "$FAILED_DIR"/*; do
    [ -f "$failed_msg" ] || continue

    # Skip LOCK files - they are temporary and should not be retried
    [[ "$failed_msg" == *.LOCK* ]] && continue

    # Stop if we've processed the batch limit
    if [ "$processed" -ge "$BATCH_SIZE" ]; then
        log "BATCH LIMIT: Processed $BATCH_SIZE messages, stopping (will retry remaining $((FAILED_COUNT - processed)) in next run)"
        break
    fi

    filename=$(basename "$failed_msg")

    # Check if this message has a retry counter
    if [[ "$filename" =~ _retry([0-9]+)$ ]]; then
        # Extract retry count
        retry_count="${BASH_REMATCH[1]}"

        if [ "$retry_count" -ge "$MAX_RETRIES" ]; then
            log "SKIP: $filename (max retries $MAX_RETRIES reached)"
            continue
        fi

        # Increment retry counter
        new_retry_count=$((retry_count + 1))
        new_filename="${filename%_retry*}_retry${new_retry_count}"
    else
        # First retry - add retry counter
        new_filename="${filename}_retry1"
        retry_count=0
        new_retry_count=1
    fi

    # Move message back to outgoing with new filename
    if mv "$failed_msg" "$OUTGOING_DIR/$new_filename" 2>/dev/null; then
        log "RETRY: $filename -> $new_filename (attempt $new_retry_count/$MAX_RETRIES)"
        ((processed++))
    else
        log "ERROR: Failed to move $filename to outgoing"
    fi
done

log "=== Retry check completed: $processed messages moved ==="
