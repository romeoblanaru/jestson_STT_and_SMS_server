#!/bin/bash
# Audio library sync from VPS shared directory
# Syncs all files normally, but mirrors silence_fills/ directories exactly

SOURCE="VPS_shared_files/audio_library/"
DEST="/home/rom/audio_library/"
LOG="/var/log/voice_bot_ram/audio_sync.log"

# Create destination if doesn't exist
mkdir -p "$DEST"

# Create log directory if doesn't exist
mkdir -p "$(dirname "$LOG")"

# Timestamp
echo "========================================" | tee -a "$LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting audio library sync" | tee -a "$LOG"

# Pass 1: Sync everything WITHOUT delete (creates dirs, updates files, keeps extras)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pass 1: Syncing all files (no delete)..." | tee -a "$LOG"
rsync -av --exclude='silence_fills/' "$SOURCE" "$DEST" 2>&1 | tee -a "$LOG" | grep -E '^(sending|deleting|total size|speedup)' || true

# Pass 2: Sync ONLY silence_fills/ directories WITH delete (exact mirror)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pass 2: Syncing silence_fills/ directories (with delete)..." | tee -a "$LOG"
rsync -av --delete --include='*/' --include='*/silence_fills/***' --exclude='*' "$SOURCE" "$DEST" 2>&1 | tee -a "$LOG" | grep -E '^(sending|deleting|total size|speedup)' || true

# Summary
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sync completed successfully" | tee -a "$LOG"
echo "" | tee -a "$LOG"
