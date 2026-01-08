#!/bin/bash
# Automated Disk Cleanup Script
# Saves ~3-4GB of disk space

LOG_FILE="/home/rom/cleanup_log.txt"
PASS="Romy_1202"

echo "=== Disk Cleanup Started: $(date) ===" > "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "Initial disk usage:" >> "$LOG_FILE"
df -h / >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 1. Clean Docker unused images
echo "[1/6] Cleaning Docker unused images..." >> "$LOG_FILE"
echo "$PASS" | sudo -S docker image prune -a -f >> "$LOG_FILE" 2>&1
echo "✓ Docker cleanup complete" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 2. Clean npm cache
echo "[2/6] Cleaning npm cache..." >> "$LOG_FILE"
npm cache clean --force >> "$LOG_FILE" 2>&1
echo "✓ npm cache cleaned" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 3. Trim old system logs
echo "[3/6] Trimming old system logs..." >> "$LOG_FILE"
echo "$PASS" | sudo -S journalctl --vacuum-time=7d >> "$LOG_FILE" 2>&1
echo "✓ Old logs removed" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 4. Remove old snap revisions
echo "[4/6] Removing old snap revisions..." >> "$LOG_FILE"
LANG=C snap list --all 2>/dev/null | awk '/disabled/{print $1, $3}' | while read snapname revision; do
    echo "  Removing $snapname revision $revision..." >> "$LOG_FILE"
    echo "$PASS" | sudo -S snap remove "$snapname" --revision="$revision" >> "$LOG_FILE" 2>&1
done
echo "✓ Old snap revisions removed" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 5. Auto-remove unused packages
echo "[5/6] Auto-removing unused packages..." >> "$LOG_FILE"
echo "$PASS" | sudo -S apt-get autoremove -y >> "$LOG_FILE" 2>&1
echo "✓ Unused packages removed" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 6. Clean apt cache archives (keep cache structure)
echo "[6/6] Final apt cleanup..." >> "$LOG_FILE"
echo "$PASS" | sudo -S apt-get autoclean -y >> "$LOG_FILE" 2>&1
echo "✓ Apt cleanup complete" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "=== Cleanup Summary ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "Final disk usage:" >> "$LOG_FILE"
df -h / >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

echo "=== Disk Cleanup Completed: $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
echo "Check results: cat /home/rom/cleanup_log.txt" >> "$LOG_FILE"
