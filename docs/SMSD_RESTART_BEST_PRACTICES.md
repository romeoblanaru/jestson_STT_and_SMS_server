# SMSD Restart Best Practices

**Date:** 2026-01-17
**Issue:** SMS Gateway went down despite "perfect" system status
**Root Cause:** Manual stop flag not cleared when SMSD restarted via systemctl

---

## 🔴 What Happened (Post-Mortem)

### Timeline
```
19:44 - Manual stop flag created (/tmp/smsd_manual_stop)
19:52 - Configurator restarted SMSD via systemctl (flag NOT cleared)
19:52 - SMSD running briefly
~19:53 - SMSD crashed (unknown reason)
20:42-21:38 - Monitor checks every 2min, sees flag, refuses to restart
Result: SMS down for 2+ hours
```

### Root Cause
The configurator used `systemctl start smstools` instead of `smsd_manual_start.sh`, leaving the manual stop flag in place. When SMSD crashed, the monitor refused to auto-restart because it saw the flag.

---

## 🎯 The Manual Stop Flag System

### Purpose
Prevents auto-restart when debugging SMSD issues:
- Flag file: `/tmp/smsd_manual_stop`
- Created by: `smsd_manual_stop.sh`
- Cleared by: `smsd_manual_start.sh`
- Checked by: `smsd_monitor.sh` (runs every 2 minutes)

### How It Works
```bash
# Manual stop (for debugging)
./smsd_manual_stop.sh
  → Creates flag: /tmp/smsd_manual_stop
  → Kills SMSD: pkill -9 smsd
  → Logs to sms_watch with 🛑 emoji

# Monitor detects SMSD down
smsd_monitor.sh (cron every 2min)
  → Checks: Is SMSD running?
  → If down: Check for flag
  → If flag exists: Don't restart (exit)
  → If no flag: Auto-restart + notify VPS

# Manual start (re-enable auto-restart)
./smsd_manual_start.sh
  → Starts SMSD
  → Deletes flag: rm -f /tmp/smsd_manual_stop
  → Logs to sms_watch with ▶️ emoji
```

---

## ❌ Scripts That Restart SMSD Incorrectly

### Problem Scripts (Bypass Manual Start Script)

#### 1. **ec25_smart_configurator.sh**
**Location:** Line 342
**Issue:** Calls `configure_smsd_for_modem.sh` which restarts SMSD

```bash
# Current (WRONG):
/home/rom/configure_smsd_for_modem.sh
  └─> sudo systemctl restart smstools  # Doesn't clear flag!
```

#### 2. **configure_smsd_for_modem.sh**
**Location:** Needs verification
**Issue:** Uses systemctl directly

```bash
# Current (WRONG):
sudo systemctl restart smstools  # Doesn't clear flag!
```

#### 3. **ec25_port_monitor.sh**
**Location:** Lines 134-138
**Issue:** Restarts SMSD manually without clearing flag

```bash
# Current (WRONG):
pkill -9 smsd
sleep 2
/usr/sbin/smsd -p/var/run/smstools/smsd.pid ...
# Flag not cleared!
```

#### 4. **check_ec25_status.sh**
**Location:** Lines 88, 292
**Issue:** NOW FIXED! Uses manual stop/start scripts correctly

```bash
# Current (CORRECT - Fixed Jan 17):
/home/rom/smsd_manual_stop.sh
...
/home/rom/smsd_manual_start.sh
```

---

## ✅ How to Restart SMSD Correctly

### Rule #1: Always Use Manual Scripts

```bash
# CORRECT - Clears flag and restarts
/home/rom/smsd_manual_start.sh

# WRONG - Leaves flag, breaks auto-restart
sudo systemctl start smstools
sudo /usr/sbin/smsd
pkill smsd && /usr/sbin/smsd
```

### Rule #2: If You Must Use systemctl

```bash
# If you absolutely must use systemctl:
rm -f /tmp/smsd_manual_stop  # Clear flag first!
sudo systemctl restart smstools
```

### Rule #3: Never Leave Flags Behind

```bash
# Always pair manual stop with manual start
./smsd_manual_stop.sh
# ... do debugging ...
./smsd_manual_start.sh  # Clears flag!
```

---

## 🛠️ Mitigation Strategies

### Strategy 1: Auto-Clear Stale Flags (RECOMMENDED)

Add to `smsd_monitor.sh` around line 26:

```bash
# Check if this is a manual stop (for debugging)
if [ -f "$MANUAL_STOP_FLAG" ]; then
    # Check if flag is stale (older than 30 minutes)
    FLAG_AGE=$(($(date +%s) - $(stat -c %Y "$MANUAL_STOP_FLAG")))
    if [ $FLAG_AGE -gt 1800 ]; then
        log "WARNING: Manual stop flag is stale (${FLAG_AGE}s old) - auto-clearing"
        system_event "WARNING" "Stale manual stop flag cleared - resuming auto-restart"
        rm -f "$MANUAL_STOP_FLAG"
        # Continue to restart section
    else
        log "INFO: SMSD manually stopped (debugging mode) - NOT auto-restarting"
        # Send notification...
        exit 0
    fi
fi
```

**Benefits:**
- Prevents 2+ hour outages from forgotten flags
- Still respects recent manual stops (< 30 min)
- Self-healing system

### Strategy 2: Centralize SMSD Restart Logic

Create `/home/rom/restart_smsd.sh`:

```bash
#!/bin/bash
# Centralized SMSD restart - use this from ALL scripts
# Automatically handles flag cleanup

MANUAL_STOP_FLAG="/tmp/smsd_manual_stop"

# Always clear manual stop flag
if [ -f "$MANUAL_STOP_FLAG" ]; then
    echo "Clearing manual stop flag"
    rm -f "$MANUAL_STOP_FLAG"
fi

# Restart SMSD
sudo /usr/bin/systemctl restart smstools

# Wait for startup
sleep 3

# Verify
if pgrep -x smsd > /dev/null; then
    echo "SMSD restarted successfully"
    exit 0
else
    echo "ERROR: SMSD failed to restart"
    exit 1
fi
```

**Update all scripts to use:**
```bash
/home/rom/restart_smsd.sh  # Consistent restart everywhere
```

### Strategy 3: Flag with Auto-Expiry

Update `smsd_manual_stop.sh`:

```bash
# Create flag with timestamp and expiry
EXPIRE_TIME=$(($(date +%s) + 3600))  # 1 hour
echo "expire:$EXPIRE_TIME" > "$MANUAL_STOP_FLAG"
echo "[$(date)] SMSD manually stopped - expires in 1 hour" >> "$MANUAL_STOP_FLAG"
```

Update `smsd_monitor.sh`:

```bash
if [ -f "$MANUAL_STOP_FLAG" ]; then
    # Check expiry
    EXPIRE_TIME=$(head -1 "$MANUAL_STOP_FLAG" | grep -oP 'expire:\K\d+')
    if [ -n "$EXPIRE_TIME" ] && [ $(date +%s) -gt $EXPIRE_TIME ]; then
        log "Manual stop flag expired - clearing"
        rm -f "$MANUAL_STOP_FLAG"
    else
        log "SMSD manually stopped - NOT auto-restarting"
        exit 0
    fi
fi
```

### Strategy 4: Alert on Long Outages

Add to `smsd_monitor.sh`:

```bash
OUTAGE_THRESHOLD=600  # 10 minutes

if ! pgrep -x "smsd" > /dev/null; then
    if [ -f "$MANUAL_STOP_FLAG" ]; then
        # Check how long it's been down
        FLAG_AGE=$(($(date +%s) - $(stat -c %Y "$MANUAL_STOP_FLAG")))

        if [ $FLAG_AGE -gt $OUTAGE_THRESHOLD ]; then
            # Send urgent alert
            /home/rom/pi_send_message.sh \
                "🚨 URGENT: SMSD down for ${FLAG_AGE}s with manual stop flag. Possible forgotten debugging session!" \
                "error"
        fi
    fi
fi
```

---

## 📋 Required Script Updates

### Priority 1 (Critical)
1. ✅ **check_ec25_status.sh** - FIXED (uses manual scripts)
2. ⚠️ **ec25_port_monitor.sh** - Update lines 134-138 to use `smsd_manual_start.sh`
3. ⚠️ **configure_smsd_for_modem.sh** - Update to use `smsd_manual_start.sh`
4. ⚠️ **smsd_monitor.sh** - Add stale flag detection (Strategy 1)

### Priority 2 (Recommended)
5. Create `/home/rom/restart_smsd.sh` (Strategy 2)
6. Update all scripts to use centralized restart function
7. Add long outage alerts (Strategy 4)

---

## 🔍 How to Detect This Issue

### Symptoms
- SMS not working
- Everything else looks "perfect"
- No errors in visible logs
- SMSD service shows "active (exited)"

### Diagnosis Commands

```bash
# Check if SMSD is actually running
pgrep -x smsd
# If empty: SMSD is DOWN

# Check for manual stop flag
ls -la /tmp/smsd_manual_stop
cat /tmp/smsd_manual_stop
# If exists: Auto-restart is disabled

# Check monitor log
tail -50 /var/log/smsd_monitor.log
# Should show: "manually stopped - NOT auto-restarting"

# Check how long flag has been there
stat /tmp/smsd_manual_stop
# Compare Modify time with current time
```

### Quick Fix (Emergency)

```bash
# Option 1: Use manual start script
/home/rom/smsd_manual_start.sh

# Option 2: Manual flag removal + systemctl
rm -f /tmp/smsd_manual_stop
sudo systemctl restart smstools
```

---

## 📊 Monitoring Improvements

### Add to Monitoring Dashboard

```bash
# Check for stale manual stop flags
if [ -f /tmp/smsd_manual_stop ]; then
    FLAG_AGE=$(($(date +%s) - $(stat -c %Y /tmp/smsd_manual_stop)))
    echo "⚠️ Manual stop flag active (${FLAG_AGE}s old)"
fi

# Check SMSD actual status vs service status
SMSD_RUNNING=$(pgrep -x smsd > /dev/null && echo "YES" || echo "NO")
SERVICE_STATUS=$(systemctl is-active smstools)
echo "SMSD Process: $SMSD_RUNNING | Service: $SERVICE_STATUS"
```

### Alert Conditions

| Condition | Alert Level | Action |
|-----------|-------------|--------|
| Flag exists < 10 min | INFO | Log only |
| Flag exists 10-30 min | WARNING | Send notification |
| Flag exists > 30 min | CRITICAL | Auto-clear + alert |
| SMSD down + no flag | CRITICAL | Auto-restart + alert |
| Restart fails | CRITICAL | VPS notification + manual intervention |

---

## 🎓 Lessons Learned

### What Went Wrong
1. Inconsistent SMSD restart methods across scripts
2. No timeout on manual stop flag
3. No visibility when flag prevents restart
4. Multiple ways to restart SMSD (systemctl, manual scripts, direct smsd command)

### Best Practices Going Forward
1. **Standardize:** One way to restart SMSD (`restart_smsd.sh` or manual scripts)
2. **Timeouts:** All flags should have automatic expiry
3. **Visibility:** Alert when flag prevents restart for > 10 minutes
4. **Testing:** Test that flag cleanup works in all scenarios
5. **Documentation:** This document! Reference before modifying SMSD restart logic

---

## 🔗 Related Files

- `/home/rom/smsd_manual_stop.sh` - Manual stop (creates flag)
- `/home/rom/smsd_manual_start.sh` - Manual start (clears flag)
- `/home/rom/smsd_monitor.sh` - Auto-restart monitor (checks flag)
- `/home/rom/ec25_port_monitor.sh` - Port monitor (restarts SMSD)
- `/home/rom/ec25_smart_configurator.sh` - Modem configurator (restarts SMSD)
- `/home/rom/configure_smsd_for_modem.sh` - SMSD config updater (restarts SMSD)
- `/home/rom/check_ec25_status.sh` - EC25 status checker (restarts SMSD)

---

## 📝 Summary

**The Problem:**
Multiple scripts restart SMSD using different methods. When `systemctl` is used instead of `smsd_manual_start.sh`, the manual stop flag doesn't get cleared, preventing future auto-restarts.

**The Solution:**
Implement Strategy 1 (auto-clear stale flags) immediately, then gradually migrate all scripts to use a centralized restart function.

**Prevention:**
Add monitoring alerts for stale flags and enforce the rule: **Always use manual scripts or centralized restart function**.

---

**Last Updated:** 2026-01-17
**Next Review:** After implementing Strategy 1
