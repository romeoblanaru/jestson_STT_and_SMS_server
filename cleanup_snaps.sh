#!/bin/bash
# Snap Cleanup Script - Removes old snap revisions

echo "=== Starting Snap Cleanup ==="
echo ""
echo "Current disk usage:"
df -h / | grep nvme
echo ""

# Start snapd
echo "[1/4] Starting snapd service..."
echo "Romy_1202" | sudo -S systemctl start snapd
sleep 15  # Wait for snapd to fully start
echo "✓ snapd started"
echo ""

# Check snap status
echo "[2/4] Checking snap status..."
snap version
echo ""

# List and remove old revisions
echo "[3/4] Removing old snap revisions..."
echo "This may take 5-10 minutes (each revision takes 30-60 seconds)..."
echo ""

snap list --all | awk '/disabled/{print $1, $3}' | while read snapname revision; do
    echo "  Removing $snapname revision $revision..."
    echo "Romy_1202" | sudo -S snap remove "$snapname" --revision="$revision" 2>&1 | grep -v "password"
done

echo ""
echo "✓ Old snap revisions removed"
echo ""

# Stop snapd to save memory
echo "[4/4] Stopping snapd to save memory..."
echo "Romy_1202" | sudo -S systemctl stop snapd
echo "✓ snapd stopped"
echo ""

echo "=== Snap Cleanup Complete ==="
echo ""
echo "Final disk usage:"
df -h / | grep nvme
echo ""
echo "Check saved space!"
