#!/bin/bash
###############################################################################
# Professional Incoming SMS Processor
# Continuously monitors incoming SMS folder and processes them
# This is the PROFESSIONAL fix for the eventhandler not working
###############################################################################

INCOMING_DIR="/var/spool/sms/incoming"
CHECKED_DIR="/var/spool/sms/checked"
HANDLER="/usr/local/bin/sms_handler_unicode.py"
LOG="/var/log/incoming_sms_processor.log"
LOCK_FILE="/var/run/incoming_sms_processor.lock"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

# Create log if it doesn't exist
touch "$LOG" 2>/dev/null || LOG="/tmp/incoming_sms_processor.log"

process_sms_file() {
    local sms_file="$1"
    local filename=$(basename "$sms_file")

    # Skip if already processing
    if [ -f "${sms_file}.lock" ]; then
        return
    fi

    # Create lock
    touch "${sms_file}.lock" 2>/dev/null

    log "Processing: $filename"

    # Call handler
    if python3 "$HANDLER" "$sms_file" 2>&1 | tee -a "$LOG"; then
        log "Handler executed successfully for $filename"
    else
        log "WARNING: Handler failed for $filename (exit code: $?)"
    fi

    # Move to checked
    if mv "$sms_file" "$CHECKED_DIR/" 2>> "$LOG"; then
        log "Moved $filename to checked folder"
        rm -f "${sms_file}.lock" 2>/dev/null
    else
        log "ERROR: Failed to move $filename to checked"
        rm -f "${sms_file}.lock" 2>/dev/null
    fi
}

log "=== Incoming SMS Processor Started ==="

while true; do
    # Process all SMS files in incoming folder
    processed=0

    for sms_file in "$INCOMING_DIR"/GSM1.*; do
        # Skip if no files match
        [ -e "$sms_file" ] || continue

        # Skip lock files
        [[ "$sms_file" == *.lock ]] && continue

        process_sms_file "$sms_file"
        processed=$((processed + 1))
    done

    if [ $processed -gt 0 ]; then
        log "Processed $processed SMS files"
    fi

    # Check every 2 seconds
    sleep 2
done
