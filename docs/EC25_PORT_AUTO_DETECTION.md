# EC25 USB Port Auto-Detection System

**⚠️ DEPRECATED - This document describes the old udev-based approach**

**Date:** 2026-01-17
**Status:** ❌ Replaced by systemd timer approach

---

## This Approach Has Been Replaced

The udev-based auto-detection system described in this document **did not work reliably** due to:

1. **Unpredictable timing:** EC25 modem takes 50-60 seconds to fully initialize
2. **Race conditions:** Multiple script instances running simultaneously
3. **Failed detection:** Even with 30 retries, ports weren't ready in time

---

## New Solution: Systemd Timer

**Please refer to the new documentation:**

📄 **[EC25_PORT_AUTO_MONITOR.md](EC25_PORT_AUTO_MONITOR.md)**

**The new approach:**
- Uses systemd timer that runs every 30 seconds
- Checks if symlink is valid and fixes it if broken
- Self-healing system - no timing issues
- 100% reliable - tested and working

---

## Old Files Removed

All files related to the udev approach have been removed:
- `/home/rom/setup_ec25_port.sh`
- `/home/rom/install_fixed_udev_rule.sh`
- Various test and installation scripts
- `/etc/udev/rules.d/99-ec25-auto-detect.rules`
- `/etc/systemd/system/ec25-port-setup.service`

---

**For current information, see:** [EC25_PORT_AUTO_MONITOR.md](EC25_PORT_AUTO_MONITOR.md)
