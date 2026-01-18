# EC25 Smart Configuration System

**Complete Automated Modem Management**
**Date:** 2026-01-17
**Status:** ✅ Implemented
**Architecture:** Simplified Sequential Design

---

## System Overview

**Smart, automated system** that handles:
- ✅ Modem replacement (IMEI tracking)
- ✅ SIM card changes (IMSI tracking)
- ✅ Country/operator changes (auto-detection)
- ✅ USB port changes (runtime monitoring)
- ✅ Zero manual intervention

---

## Architecture (Simplified!)

```
┌─────────────────────────────────────────────────────────┐
│  Systemd Timer (every 30 seconds)                       │
│  ├─ Triggers: ec25-port-monitor.service                 │
│  └─ Always running                                      │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Port Monitor (entry point)                             │
│  ├─ Check if EC25 present                              │
│  ├─ Validate /dev/ttyUSB_AT symlink                     │
│  └─ Create/fix symlink if needed                        │
└─────────────────────────────────────────────────────────┘
                         ↓
                  Symlink changed?
                         ↓ YES
┌─────────────────────────────────────────────────────────┐
│  Smart Configurator (runs synchronously)                │
│  ├─ Uses /dev/ttyUSB_AT from port monitor              │
│  ├─ Check IMEI → New modem? → USB composition          │
│  ├─ Check IMSI → New SIM? → APN/VoLTE config           │
│  └─ Returns to port monitor                             │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  Port Monitor (continues)                               │
│  └─ Restart SMSTools if needed                          │
└─────────────────────────────────────────────────────────┘
```

**Key Insight:** Single entry point, sequential execution, no locks needed!

---

## Components

### 1. Port Monitor (Master Control)

**File:** `/home/rom/ec25_port_monitor.sh`

**Responsibilities:**
- Detects EC25 modem presence
- Creates/validates `/dev/ttyUSB_AT` symlink
- Calls configurator when port changes
- Restarts SMSTools when needed
- Runs every 30 seconds via systemd timer

**Trigger:** Systemd timer (ec25-port-monitor.timer)

**Why it's the entry point:**
- Already handles 50-60 second modem initialization
- Natural place to detect modem changes
- Creates symlink that configurator needs

### 2. Smart Configurator (Called by Monitor)

**File:** `/home/rom/ec25_smart_configurator.sh`

**Responsibilities:**
- Uses `/dev/ttyUSB_AT` symlink (from port monitor)
- Tracks IMEI (modem identity)
- Tracks IMSI (SIM card identity)
- Configures only when IMEI or IMSI changes
- Returns control to port monitor

**Trigger:** Port monitor (when symlink changes)

**Smart Tracking:**
```json
{
  "imei": "867584045362810",
  "imsi": "246031234567890",
  "operator": "Telia Lithuania",
  "last_configured": "2026-01-17 18:00:00"
}
```

**Stored in:** `/var/lib/ec25/modem.json`

### 3. Modem-Specific Configuration

**File:** `/home/rom/configure_smsd_for_modem.sh`

**Responsibilities:**
- Detects modem vendor (SimTech, Quectel, Samsung)
- Configures SMSTools parameters for EC25
- Called by smart configurator

**Already handles EC25!** ✅

---

## Decision Logic

### Port Monitor Flow

```
Every 30 seconds:
  ↓
Is EC25 present? → NO → Exit
  ↓ YES
Is /dev/ttyUSB_AT valid? → YES → Exit (all good)
  ↓ NO (broken or wrong)
Find correct EC25 port
  ↓
Update symlink
  ↓
PORT_CHANGED = true
  ↓
Call configurator (synchronous)
  ↓
Configurator returns
  ↓
Restart SMSTools
  ↓
Done
```

### Smart Configurator Flow

```
Start (called by port monitor)
  ↓
Verify /dev/ttyUSB_AT exists
  ↓
Read IMEI from modem
  ↓
Load saved IMEI from /var/lib/ec25/modem.json
  ↓
┌─────────────────────────────────────────────────────┐
│ IMEI Different? (New modem!)                        │
│   ↓ YES                                             │
│   Send AT+QCFG="usbnet",2 (RNDIS mode)             │
│   Set flag: NEEDS_MODEM_RESET=true                 │
│   Continue (don't wait for reset yet) ↓            │
│                                                     │
│ IMEI Same? → Skip USB config                        │
└─────────────────────────────────────────────────────┘
  ↓
Read IMSI from SIM
  ↓
Load saved IMSI
  ↓
┌─────────────────────────────────────────────────────┐
│ IMSI Different? (New SIM!)                          │
│   ↓ YES                                             │
│   Auto-detect operator from IMSI                    │
│   Get APN for operator                              │
│   Configure network settings                        │
│   Configure VoLTE if supported                      │
│   Run configure_smsd_for_modem.sh                   │
│                                                     │
│ IMSI Same? → Skip network config                    │
└─────────────────────────────────────────────────────┘
  ↓
Save state (IMEI + IMSI)
  ↓
Log completion message
  ↓
NEEDS_MODEM_RESET flag set?
  ↓ YES
  Send AT+CFUN=1,1 (soft reset)
  ↓
  Exit (modem will reset)
  ↓
  Port monitor will detect reset and restart SMSTools
  ↓ NO
  Exit normally
  ↓
Return to port monitor
```

---

## EC25 USB Composition Modes

**AT Command:** `AT+QCFG="usbnet",<mode>`

| Mode | Product ID | Description | Ports Available |
|------|------------|-------------|-----------------|
| 0 | 0125 | Standard Serial | ttyUSB0-4, no network |
| 1 | - | Reserved | - |
| **2** | **0306** | **RNDIS/CDC Ethernet** ✅ | **ttyUSB0,1,3,4 + network** |

**Our Configuration:** Mode 2 (RNDIS)
- Enables CDC Ethernet for LTE internet backup
- Provides SMS functionality via ttyUSB3
- **Note:** ttyUSB2 is removed in this mode!

**Soft Reset Required:** After changing `usbnet` mode, modem must be reset with `AT+CFUN=1,1` to apply changes.

---

## Operator Auto-Detection

**Based on IMSI (MCC+MNC)**

| IMSI Prefix | Operator | Country | APN |
|-------------|----------|---------|-----|
| 24603 | Telia | Lithuania | internet.telia.lt |
| 24601 | Omnitel | Lithuania | omnitel |
| 24602 | Bite | Lithuania | mobile.bite.lt |
| 24001 | Telia | Sweden | online.telia.se |
| 24008 | Telenor | Sweden | internet.telenor.se |
| 24007 | Tele2 | Sweden | internet.tele2.se |
| 22601 | Vodafone | Romania | internet.vodafone.ro |
| 22603 | Telekom | Romania | internet.telekom.ro |
| 22610 | Orange | Romania | internet |

**Expandable:** Add more operators to `get_apn_for_operator()` function

---

## Scenarios

### Scenario 1: Modem Replacement

```
Old modem breaks → unplug
  ↓
Plug in new modem (different IMEI)
  ↓
Wait 30-60 seconds for initialization
  ↓
Port monitor detects new modem
  ↓
Creates /dev/ttyUSB_AT
  ↓
Calls configurator
  ↓
Configurator reads IMEI → Different!
  ↓
Configures USB composition
  ↓
Configures network (reads IMSI)
  ↓
Saves new IMEI + IMSI
  ↓
SMSTools restarts
  ↓
✅ System working with new modem
```

**Time:** ~2 minutes (modem init + config)
**Manual intervention:** None!

### Scenario 2: Moving to New Country

```
System in Lithuania (Telia SIM)
  ↓
Move to Romania, swap SIM (Vodafone)
  ↓
Port monitor detects (30 sec)
  ↓
Calls configurator
  ↓
Configurator reads IMSI → Different!
  ↓
Detects: Vodafone Romania (from IMSI)
  ↓
Configures APN: internet.vodafone.ro
  ↓
Enables VoLTE
  ↓
Saves new IMSI
  ↓
SMSTools restarts
  ↓
✅ Working in Romania
```

**Time:** ~30-60 seconds
**Manual intervention:** None!

### Scenario 3: Runtime Port Change

```
Modem reconnects, ttyUSB2 → ttyUSB3
  ↓
Port monitor detects (within 30 sec)
  ↓
Updates symlink: /dev/ttyUSB_AT → ttyUSB3
  ↓
Calls configurator
  ↓
Configurator reads IMEI → Same!
  ↓
Reads IMSI → Same!
  ↓
Logs: "No changes detected - skipped"
  ↓
Returns quickly
  ↓
SMSTools restarts on new port
  ↓
✅ Working again
```

**Time:** ~5-10 seconds
**Manual intervention:** None!

---

## Advantages of This Design

### ✅ Simplicity
- **One entry point** (port monitor timer)
- **Sequential execution** (no race conditions)
- **No locking needed** (runs in order)
- **Easy to debug** (single flow)

### ✅ Reliability
- **Port monitor already handles timing** (50-60 sec modem init)
- **Symlink guaranteed valid** when configurator runs
- **Error handling** throughout
- **Graceful degradation** (retries on next cycle)

### ✅ Intelligence
- **IMEI tracking** → Only reconfigure USB when modem changes
- **IMSI tracking** → Only reconfigure network when SIM changes
- **Fast exit** when nothing changed
- **Auto-operator detection** for any country

### ✅ No Interference
- **Configurator doesn't create symlinks** (port monitor's job)
- **Runs synchronously** (port monitor waits)
- **No separate udev rules** (one systemd timer)
- **Clean separation of concerns**

---

## Logs and Debugging

### Port Monitor Log
```bash
cat /var/log/ec25_port_monitor.log
```

**Example:**
```
[2026-01-17 18:00:15] Symlink invalid or missing - attempting repair...
[2026-01-17 18:00:15] Detected EC25 AT port: /dev/ttyUSB2
[2026-01-17 18:00:15] Port changed from /dev/ttyUSB3 to /dev/ttyUSB2 - updating symlink
[2026-01-17 18:00:15] Port changed - running smart configurator...
[2026-01-17 18:00:45] Configurator completed successfully
[2026-01-17 18:00:45] Port changed - restarting SMSTools...
[2026-01-17 18:00:47] SMSTools restarted on new port
[2026-01-17 18:00:47] Port monitoring complete: /dev/ttyUSB_AT -> /dev/ttyUSB2
```

### Configurator Log
```bash
cat /var/log/ec25_configurator.log
```

**Example (new modem):**
```
[2026-01-17 18:00:15] Smart Configurator Started
[2026-01-17 18:00:15] Using AT port: /dev/ttyUSB_AT -> /dev/ttyUSB2
[2026-01-17 18:00:17] Modem IMEI: 867584045362999
[2026-01-17 18:00:17] NEW MODEM DETECTED!
[2026-01-17 18:00:17] Previous IMEI: 867584045362810
[2026-01-17 18:00:17] Current IMEI:  867584045362999
[2026-01-17 18:00:17] Configuring USB composition for EC25...
[2026-01-17 18:00:32] USB composition changed - modem will reset
[2026-01-17 18:00:32] SIM IMSI: 246031234567890
[2026-01-17 18:00:32] Detected operator: Telia Lithuania
[2026-01-17 18:00:32] Configuring network for operator: Telia Lithuania
[2026-01-17 18:00:35] Network configuration complete
[2026-01-17 18:00:40] Configurator completed successfully
```

**Example (same modem/SIM):**
```
[2026-01-17 18:05:15] Smart Configurator Started
[2026-01-17 18:05:15] Using AT port: /dev/ttyUSB_AT -> /dev/ttyUSB3
[2026-01-17 18:05:17] Modem IMEI: 867584045362810
[2026-01-17 18:05:17] Same modem detected (IMEI matches)
[2026-01-17 18:05:19] SIM IMSI: 246031234567890
[2026-01-17 18:05:19] Same SIM card detected (IMSI matches)
[2026-01-17 18:05:19] No changes detected - configuration skipped
```

### State File
```bash
cat /var/lib/ec25/modem.json
```

**Example:**
```json
{
  "imei": "867584045362810",
  "imsi": "246031234567890",
  "operator": "Telia Lithuania",
  "last_configured": "2026-01-17 18:00:45"
}
```

---

## Testing

### Test 1: System Reboot
```bash
sudo reboot
```

**Expected:**
- Timer starts 15 seconds after boot
- Port monitor detects modem (within 60 seconds)
- Creates symlink
- Configurator checks IMEI/IMSI (same → skips)
- SMSTools starts
- SMS working

### Test 2: Modem Unplug/Replug
```bash
# Unplug modem
# Wait 5 seconds
# Plug it back in
# Wait 90 seconds

cat /var/log/ec25_port_monitor.log
```

**Expected:**
- Port monitor detects within 60 seconds
- Configurator runs, checks IMEI/IMSI (same → skips)
- SMSTools restarts
- SMS working

### Test 3: Simulate New Modem
```bash
# Delete state file
sudo rm /var/lib/ec25/modem.json

# Wait for next port monitor cycle (up to 30 sec)
cat /var/log/ec25_configurator.log
```

**Expected:**
- Configurator treats as new modem
- Configures USB composition
- Configures network
- Creates new state file

---

## Manual Operations

### Force Configuration
```bash
# Run configurator manually (uses current symlink)
sudo /home/rom/ec25_smart_configurator.sh
```

### Check System Status
```bash
# Timer status
systemctl status ec25-port-monitor.timer

# Current symlink
ls -la /dev/ttyUSB_AT

# Saved state
cat /var/lib/ec25/modem.json

# Recent logs
tail -20 /var/log/ec25_port_monitor.log
tail -20 /var/log/ec25_configurator.log
```

### Reset to Factory
```bash
# Clear saved state (will reconfigure on next cycle)
sudo rm -f /var/lib/ec25/modem.json
```

---

## File Locations

**Scripts:**
- `/home/rom/ec25_port_monitor.sh` - Port monitor (entry point)
- `/home/rom/ec25_smart_configurator.sh` - Smart configurator
- `/home/rom/configure_smsd_for_modem.sh` - Modem-specific config

**Systemd:**
- `/etc/systemd/system/ec25-port-monitor.service` - Port monitor service
- `/etc/systemd/system/ec25-port-monitor.timer` - Timer (every 30 sec)

**State:**
- `/var/lib/ec25/modem.json` - IMEI/IMSI tracking

**Logs:**
- `/var/log/ec25_port_monitor.log` - Port monitoring
- `/var/log/ec25_configurator.log` - Configuration actions

**Symlink:**
- `/dev/ttyUSB_AT` - Stable port reference

---

## Summary

✅ **Fully Automated System**
- Modem replacement → Auto-configured
- SIM card change → Auto-configured
- Country move → Auto-configured
- Port changes → Auto-fixed
- No manual intervention ever needed

✅ **Simple Architecture**
- One entry point (port monitor timer)
- Sequential execution (no race conditions)
- Clear separation of concerns
- Easy to debug and maintain

✅ **Production Ready**
- Error handling throughout
- Graceful degradation
- Comprehensive logging
- State tracking

**The system is complete and ready for production use!**

---

**Last Updated:** 2026-01-17
**Architecture:** Simplified Sequential
**Status:** ✅ Production Ready
