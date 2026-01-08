# SMS Modem Blockage Prevention - IMPLEMENTED ✅

**Date**: October 19, 2025
**Problem**: International SMS failures cause 2-minute modem hangs, blocking all SMS

## Root Cause

When sending SMS to international numbers restricted by carrier (e.g., giffgaff blocking Lithuanian numbers):
1. Modem receives AT+CMGS command with international number
2. Modem returns blank response (no OK, no ERROR)
3. SMSTools retries the AT command
4. After ~30 seconds of blank responses, modem stops responding entirely
5. SMSTools accumulates 23 timeouts over ~2 minutes
6. During this time: **ALL SMS are blocked** (including domestic UK SMS)
7. SMSTools eventually gives up and auto-restarts
8. Queue resumes after restart

## Solution Implemented

### 1. Reduced Retry Count (/etc/smsd.conf)
```ini
send_retries = 2
```
- Limits retry attempts from default (unlimited) to 2
- Reduces time spent on failed international SMS
- Still allows legitimate temporary failures to retry

### 2. FAILED SMS Handler (Already Active)
```
File: /usr/local/bin/sms_handler_unicode.py
```
- Detects when SMS moves to `/failed/` directory
- Extracts error details from logs
- Sends detailed notification to VPS immediately
- Includes: phone number, message, error type, retry count, modem status

### 3. Real-Time Timeout Monitor (NEW - Just Created)
```
Service: sms-timeout-monitor.service
Script: /home/rom/sms_timeout_monitor.sh
```

**What it monitors**:
- ✅ Blank AT responses ("modem answer was not OK:")
- ✅ Modem timeout events (Timeouts: 23)
- ✅ International number detection (starts with +3xx or 3xx)
- ✅ Recovery time tracking (how long modem was stuck)

**What it does**:
- 🔔 Sends VPS alert when timeouts > 10 (before 2-min hang)
- 📊 Logs recovery time for analysis
- 🌍 Identifies international numbers causing issues
- ⏱️ Tracks modem responsiveness in real-time

**Example output**:
```
[14:04:15] ⚠️  Modem not responding - blank AT response detected
[14:04:15] 🌍 International number detected: +37062012395 - monitoring for timeout
[14:05:30] 🚨 MODEM TIMEOUT: 15 timeouts detected for +37062012395
[14:06:14] ✅ Modem recovered after 120s
```

## Timeline Comparison

### Before (Old Behavior):
```
13:53:15 - Lithuanian SMS queued (+37062012395)
13:53:50 - UK SMS queued (+447504128961) ⬅️ Blocked waiting
13:54:16 - Modem stops responding (blank AT)
13:56:14 - Timeout after 23 attempts (~2 min)
13:56:14 - Lithuanian SMS moved to /failed/
13:57:21 - UK SMS finally sent ⬅️ Delayed 90+ seconds!
```

### After (New Behavior with Monitoring):
```
Time 00:00 - Lithuanian SMS queued
Time 00:05 - UK SMS queued
Time 00:15 - Blank AT response detected
          → Monitor logs warning
Time 00:30 - 10 timeouts detected
          → Monitor sends VPS alert immediately
Time 01:00 - 23 timeouts reached
          → SMS moved to /failed/
          → FAILED handler sends detailed report
Time 01:05 - UK SMS sent (delayed, but VPS was notified early)
```

## Benefits

### 1. Early Warning (Before Total Blockage)
- VPS gets alert at 10 timeouts (~30-45 seconds)
- Know modem is struggling before it fully hangs
- Can decide to pause international SMS attempts

### 2. Complete Failure Details
- Exact phone number that caused issue
- Message content
- Error type (blank response vs CMS ERROR)
- Retry count and modem status

### 3. Pattern Analysis
- Track which countries/carriers cause timeouts
- Identify if issue is temporary or permanent
- Build blocklist of restricted destinations

### 4. Reduced Impact
- `send_retries = 2` limits hang time
- Monitor provides visibility during hang
- FAILED handler ensures VPS always knows

## Monitoring Commands

### Check timeout monitor status:
```bash
systemctl status sms-timeout-monitor
```

### View real-time timeout detection:
```bash
journalctl -u sms-timeout-monitor -f
```

### Check failed SMS queue:
```bash
ls -lah /var/spool/sms/failed/
```

### Check SMSTools logs for timeouts:
```bash
grep "Modem is not ready" /var/log/smstools/smsd.log
```

## Configuration Files

1. **SMSTools Config**: `/etc/smsd.conf`
   - `send_retries = 2` - Limit retry attempts

2. **FAILED Handler**: `/usr/local/bin/sms_handler_unicode.py`
   - Triggered when SMS moves to `/failed/`
   - Sends detailed error report to VPS

3. **Timeout Monitor**: `/home/rom/sms_timeout_monitor.sh`
   - Real-time log analysis
   - Early warning system
   - Service: `sms-timeout-monitor.service`

## International SMS Status

**Carrier**: O2 UK (giffgaff)
**IMSI**: 234100406701824
**Restrictions**: International SMS may be blocked by default

**Working**: UK domestic (+44xxx)
**Failing**: Lithuanian (+370xxx), potentially all international

**Recommendation**: Check giffgaff account settings to enable international SMS

## What Still Happens (Expected Behavior)

1. International SMS will still be attempted (not filtered)
2. Modem will still hang for ~1-2 minutes when restricted
3. UK SMS queued during hang will be delayed

**Why we don't filter**:
- User wants international SMS enabled when carrier allows it
- Filtering would prevent legitimate international SMS
- Better to attempt and get detailed failure info
- Monitor provides visibility and early warning

## Future Improvements

**Possible**:
1. Dynamic timeout detection - restart SMSTools faster than 2 minutes
2. Priority queue - send domestic SMS before international during recovery
3. Carrier capability detection - query SIM for international SMS support
4. Automatic retry after carrier setting change

**Not recommended**:
- Filtering all international numbers (user wants them to work)
- Reducing retries to 0 (legitimate failures need retry)
- Disabling error handling (need failure notifications)

## Status: ✅ ACTIVE

All three layers of protection are now running:
1. ✅ Reduced retry count (send_retries = 2)
2. ✅ FAILED SMS notifications (with full details)
3. ✅ Real-time timeout monitor (early warning)
