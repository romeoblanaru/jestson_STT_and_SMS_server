# LTE 4G Failover Modes - Complete Guide

**Configuration System for EC25 Internet Backup**
**Date:** 2026-01-17
**Status:** ✅ Production Ready

---

## Overview

The internet failover system now supports **three operational modes** controlled by two simple configuration variables. This allows you to adapt the system to different scenarios: normal operation, power issues, modem instability, or active monitoring needs.

---

## Configuration File

**Location:** `/home/rom/lte_config.sh`

```bash
# Master switch - Controls if 4G is available at all
LTE_4G_ENABLED=ON   # ON or OFF

# Failover mode - Controls how failover works
LTE_4G_FAILOVER=OFF # OFF (passive) or ON (active)
```

**To change configuration:**
```bash
nano /home/rom/lte_config.sh
# Edit the values
# No restart needed - changes take effect on next script run (within 1 minute)
```

---

## Three Operational Modes

### MODE 1: 4G Completely Disabled
**Configuration:** `LTE_4G_ENABLED=OFF` (any FAILOVER value)

**Use Case:**
- Power saving mode
- Modem hardware issues
- Data plan exhausted
- Troubleshooting network problems

**Behavior:**
- ❌ All EC25 routes removed
- ❌ 4G backup unavailable
- ✅ WiFi/LAN only
- 📊 Lower power consumption

**Log Output:**
```
LTE 4G disabled - removing all EC25 routes
```

---

### MODE 2: Passive Failover (DEFAULT - RECOMMENDED)
**Configuration:** `LTE_4G_ENABLED=ON` + `LTE_4G_FAILOVER=OFF`

**Use Case:**
- Normal production operation
- "Set it and forget it" mode
- Minimal intervention needed
- Linux kernel handles routing automatically

**Behavior:**
- ✅ **EC25 route always present** (metric 999 - last resort)
- ✅ **Automatic failover** - Linux chooses best route by metric
- ✅ **Notification when 4G used** - Alerts when WiFi/LAN fail
- ✅ **Hourly recovery check** - Detects when WiFi/LAN return
- ⚡ **Instant failover** - No detection delay (kernel handles it)

**How It Works:**
1. EC25 route established on boot with metric 999 (lowest priority)
2. WiFi (metric 600) or LAN (metric 100-300) used preferentially
3. If WiFi/LAN fail, kernel **automatically** switches to EC25 (metric 999)
4. Script detects 4G is in use → Sends notification to VPS
5. Every hour (via cron), script checks if WiFi/LAN came back
6. When primary returns, kernel **automatically** switches back

**Routing Table:**
```
default via 10.92.250.119 dev wlP1p1s0 metric 600      ← WiFi (used first)
default via 192.168.1.1 dev enP8p1s0 metric 100        ← LAN (if connected)
default via 192.168.225.1 dev enx3af9327b5d6b metric 999  ← EC25 (last resort)
```

**Notifications:**
- ⚠️ "Internet via EC25 LTE Backup - WiFi/LAN down (Passive failover)"
- ✅ "Primary Internet Restored - EC25 LTE now standby (Passive mode)"

**Advantages:**
- Zero-latency failover (kernel-level)
- Always ready (route always exists)
- Simple and reliable
- No active route management overhead

---

### MODE 3: Active Failover
**Configuration:** `LTE_4G_ENABLED=ON` + `LTE_4G_FAILOVER=ON`

**Use Case:**
- Troubleshooting and testing
- When you need detailed logs of failover events
- Development/debugging

**Behavior:**
- 🔄 **Script actively manages routes**
- 🔄 **Adds EC25 route when WiFi/LAN fail**
- 🔄 **Removes EC25 route when WiFi/LAN return**
- 📊 **Detailed logging** of all failover actions
- ⏱️ **1-minute detection delay** (timer-based)

**How It Works:**
1. Script runs every 1 minute (systemd timer)
2. Checks if WiFi/LAN are working
3. If both failed → Adds EC25 route (metric 999)
4. Sends notification to VPS
5. If WiFi/LAN return → Removes EC25 route
6. Sends notification to VPS

**Routing Table (varies):**
```
# When WiFi/LAN working:
default via 10.92.250.119 dev wlP1p1s0 metric 600      ← WiFi only

# When WiFi/LAN failed:
default via 192.168.225.1 dev enx3af9327b5d6b metric 999  ← EC25 added
```

**Notifications:**
- ⚠️ "Internet Failover: Switched to EC25 LTE backup (Primary internet down - Active mode)"
- ✅ "Internet Restored: Switched back to primary connection (EC25 backup inactive - Active mode)"

**Disadvantages:**
- 1-minute detection delay
- More log entries
- Route changes visible in logs

---

## Comparison Table

| Feature | MODE 1<br>(Disabled) | MODE 2<br>(Passive - Default) | MODE 3<br>(Active) |
|---------|---------------------|-------------------------------|-------------------|
| **Config** | ENABLED=OFF | ENABLED=ON<br>FAILOVER=OFF | ENABLED=ON<br>FAILOVER=ON |
| **4G Route** | ❌ None | ✅ Always present (999) | 🔄 Added/removed |
| **Failover Speed** | N/A | ⚡ Instant (kernel) | ⏱️ ~1 minute |
| **Notifications** | None | When 4G used/restored | When failover/restore |
| **Route Changes** | None | None (static) | Every failover |
| **Logs** | Minimal | Moderate | Detailed |
| **Use Case** | Power save | Production | Debug/Test |
| **Recommended** | Emergency only | ✅ **YES** | Development |

---

## Current Configuration Status

**Check current mode:**
```bash
cat /home/rom/lte_config.sh
```

**Check if script is working:**
```bash
tail -10 /var/log/internet_failover.log
```

**Check current routes:**
```bash
ip route show default
```

**Check which route is being used:**
```bash
ip route get 8.8.8.8
```

**Current Settings (as deployed):**
```
LTE_4G_ENABLED=ON
LTE_4G_FAILOVER=OFF
→ MODE 2: Passive Failover (RECOMMENDED)
```

---

## Testing Each Mode

### Test MODE 1 (Disabled)

```bash
# Edit config
nano /home/rom/lte_config.sh
# Set: LTE_4G_ENABLED=OFF

# Run script
sudo /home/rom/internet_failover.sh

# Verify
ip route show default
# Should show: No EC25 route

# Check log
tail /var/log/internet_failover.log
# Should show: "LTE 4G disabled - removing all EC25 routes"
```

### Test MODE 2 (Passive - Current)

```bash
# Edit config
nano /home/rom/lte_config.sh
# Set: LTE_4G_ENABLED=ON
# Set: LTE_4G_FAILOVER=OFF

# Run script
sudo /home/rom/internet_failover.sh

# Verify
ip route show default
# Should show: EC25 route with metric 999

# Check which is used
ip route get 8.8.8.8
# Should show: WiFi or LAN (not EC25)

# Simulate WiFi failure
sudo ip link set wlP1p1s0 down

# Check which is used now
ip route get 8.8.8.8
# Should show: EC25 (automatic failover!)

# Restore WiFi
sudo ip link set wlP1p1s0 up

# Check logs
tail /var/log/internet_failover.log
```

### Test MODE 3 (Active)

```bash
# Edit config
nano /home/rom/lte_config.sh
# Set: LTE_4G_ENABLED=ON
# Set: LTE_4G_FAILOVER=ON

# Run script
sudo /home/rom/internet_failover.sh

# Verify - should remove EC25 route (WiFi working)
ip route show default

# Simulate WiFi failure
sudo ip link set wlP1p1s0 down

# Run script again (simulates 1-minute timer)
sudo /home/rom/internet_failover.sh

# Verify - EC25 route should be added
ip route show default

# Restore WiFi
sudo ip link set wlP1p1s0 up

# Run script again
sudo /home/rom/internet_failover.sh

# Verify - EC25 route should be removed
ip route show default
```

---

## Systemd Timer Configuration

The failover script runs automatically every 1 minute via systemd timer.

**Check timer status:**
```bash
systemctl status internet-failover.timer
```

**Timer configuration:**
```
OnBootSec=2min          # Start 2 minutes after boot
OnUnitActiveSec=1min    # Run every 1 minute
```

**Behavior by mode:**
- **MODE 1 (Disabled):** Script runs, removes routes, exits
- **MODE 2 (Passive):** Script runs, ensures route exists, checks if 4G in use
- **MODE 3 (Active):** Script runs, actively manages routes

---

## Notifications to VPS

All modes send notifications via `/home/rom/pi_send_message.sh` to `http://10.100.0.1:8088/webhook/...`

**MODE 1:** No notifications

**MODE 2 Notifications:**
- ⚠️ When 4G starts being used (WiFi/LAN failed)
- ✅ When primary internet restored (while 4G was in use)
- 📊 Notification sent ONCE (not repeated every minute)

**MODE 3 Notifications:**
- ⚠️ When EC25 route is added (failover activated)
- ✅ When EC25 route is removed (failback to primary)
- 📊 Notification sent on every transition

---

## Hourly Cron Job (for MODE 2)

The systemd timer already runs every 1 minute, which handles:
- Passive mode: Check if 4G is in use, notify, check for primary recovery
- Active mode: Manage routes actively

**No additional cron job needed!** The 1-minute timer is sufficient for:
- Detecting when 4G is in use
- Detecting when primary internet returns
- Managing routes in all modes

---

## Troubleshooting

### Issue: 4G Never Used (MODE 2)

**Check:**
```bash
# Is EC25 route present?
ip route show default | grep 192.168.225.1

# Should show: default via 192.168.225.1 dev enx... metric 999

# Is EC25 interface UP?
ip link show | grep enx

# Should show: state UP or state UNKNOWN
```

**Fix:**
```bash
# Run script manually
sudo /home/rom/internet_failover.sh

# Check logs
tail /var/log/internet_failover.log
```

### Issue: No Notification When 4G Used

**Check:**
```bash
# Is 4G actually being used?
ip route get 8.8.8.8

# Should show: via 192.168.225.1 dev enx...

# Check notification flag
ls -la /var/run/internet_failover_4g_notified

# Should exist if notification was sent
```

**Fix:**
```bash
# Remove flag to force new notification
sudo rm /var/run/internet_failover_4g_notified

# Run script
sudo /home/rom/internet_failover.sh
```

### Issue: Routes Not Cleaned Up (MODE 3)

**Symptom:** Both WiFi and EC25 routes present in active mode

**This is normal for up to 1 minute** (timer interval)

**Force immediate cleanup:**
```bash
sudo /home/rom/internet_failover.sh
```

---

## Best Practices

### Recommended Configuration

✅ **Use MODE 2 (Passive) for production:**
- Set it and forget it
- Instant failover
- Automatic recovery
- Minimal logging

### When to Use Other Modes

**Use MODE 1 (Disabled) when:**
- Modem has hardware issues
- Need to save power
- Data plan exhausted
- Troubleshooting network without 4G

**Use MODE 3 (Active) when:**
- Debugging failover issues
- Testing failover behavior
- Need detailed logs of transitions
- Development/validation

### Configuration Changes

**Changes take effect:**
- Within 1 minute (next timer run)
- Or immediately if you run script manually

**No service restart needed!**

---

## Quick Reference Commands

```bash
# View current configuration
cat /home/rom/lte_config.sh

# Change to MODE 1 (Disabled)
sudo nano /home/rom/lte_config.sh
# Set: LTE_4G_ENABLED=OFF

# Change to MODE 2 (Passive - Recommended)
sudo nano /home/rom/lte_config.sh
# Set: LTE_4G_ENABLED=ON
# Set: LTE_4G_FAILOVER=OFF

# Change to MODE 3 (Active)
sudo nano /home/rom/lte_config.sh
# Set: LTE_4G_ENABLED=ON
# Set: LTE_4G_FAILOVER=ON

# Test configuration immediately
sudo /home/rom/internet_failover.sh

# Check current routes
ip route show default

# Check which route is used
ip route get 8.8.8.8

# Check logs
tail -f /var/log/internet_failover.log

# Check timer status
systemctl status internet-failover.timer
```

---

## Summary

✅ **Three flexible modes** - Adapt to any scenario
✅ **Simple configuration** - Two variables control everything
✅ **Passive mode (default)** - Zero-latency automatic failover
✅ **Active mode** - Detailed logging and control
✅ **Disabled mode** - Complete 4G shutdown when needed
✅ **VPS notifications** - Always informed of internet status
✅ **No manual intervention** - Fully automatic operation

**Current Status:**
```
Mode: Passive Failover (MODE 2)
4G Route: Always present (metric 999)
Failover: Automatic (kernel-level)
Status: ✅ Production Ready
```

**Your SMS gateway now has intelligent, adaptive internet backup that works exactly how you need it!**

---

**Related Documentation:**
- `/home/rom/docs/INTERNET_FAILOVER_GUIDE.md` - Technical details
- `/home/rom/docs/EC25_SMS_CDC_ETHERNET_SETUP.md` - SMS + CDC Ethernet setup

**Last Updated:** 2026-01-17
**Configuration:** Passive Failover Mode (Default)
**Status:** ✅ Tested and Working
