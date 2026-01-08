# SMSTools3 + SIM7600G-H Modem Communication Issue
## Diagnostic Report - October 15, 2025

---

## 1. SYSTEM CONFIGURATION

### Hardware
- **Device**: Raspberry Pi (Linux 6.12.25+rpt-rpi-v8)
- **Modem**: SIMCOM SIM7600G-H
  - IMEI: 862636055891897
  - Firmware: LE20B04SIM7600G22
  - Carrier: Vodafone UK (MCC-MNC: 234-15)
- **Serial Interface**: USB serial ports (option driver)
  - SMS Port: /dev/ttyUSB2
  - Baudrate: 115200

### Software
- **SMSTools Version**: 3.1.21
- **Mode**: TEXT mode (AT+CMGF=1)
- **Storage**: Modem memory (AT+CPMS="ME","ME","ME")
- **Delivery Reports**: Enabled (report = yes)

---

## 2. PROBLEM SUMMARY

**TWO DISTINCT ISSUES IDENTIFIED**:

### Issue #1 (PRIMARY - CRITICAL): Communication Timeouts & Initialization Failure
- SMSTools cannot reliably communicate with SIM7600G-H
- AT commands timeout (10-second waits with no response)
- Initialization randomly fails - modem handler terminates after device details query
- Direct AT commands to modem work perfectly (<1 second response)
- **This is a SMSTools ↔ SIM7600 serial communication incompatibility**

### Issue #2 (SECONDARY - When System Works): Slow SMS Sending
- When SMSTools successfully initializes, SMS sending takes 3-4 minutes
- Actual transmission is fast (~26 seconds)
- Delay occurs during delivery report wait
- Caused by unsolicited +CMTI notifications interrupting the wait loop
- **This is a separate issue from the initialization failures**

**Current State**: Issue #1 prevents system from working at all. Issue #2 only matters if Issue #1 is resolved.

---

## 3. DETAILED SYMPTOMS

### 3.1 Initialization Hang Pattern

**Expected behavior**:
```
Device details query → Init commands → Working state
```

**Actual behavior**:
```
19:55:29 GSM1: ## End of device details
19:55:29 GSM1: Modem handler terminated (up 0 min)
```

SMSTools queries device capabilities successfully but fails to transition to operational state. No error messages - just terminates.

### 3.2 AT Command Timeout Pattern

**From detailed logs (loglevel=7)**:
```
19:58:38 -> AT+CREG=2
19:58:38 Command is sent, waiting for the answer. (10)
19:58:48 No answer, timeout occurred. 1.
19:58:48 <- [empty response]
19:58:48 Modem did not accept the pre-init string
```

**Observations**:
- Modem does not respond within 10-second timeout
- Empty response received after timeout
- Pattern repeats with multiple commands (AT, AT+CREG, etc.)

### 3.3 Desynchronization Pattern

**From logs**:
```
19:59:44 -> [empty command]
19:59:44 Command is sent, waiting for the answer. (5)
19:59:49 No answer, timeout occurred. 13.
19:59:49 <- [empty]
19:59:50 Unexpected input: OK
```

**Analysis**:
- SMSTools sends empty command (sync lost)
- Receives "OK" from previous command (buffer lag)
- Indicates timing mismatch between sent commands and received responses

### 3.4 SMS Sending Delay Pattern (SECONDARY ISSUE - Only when system works)

**When SMS sending succeeds** (recorded earlier during rare successful initialization):
```
18:16:48 SMS sent (part 1/2), sending time 5 sec.  ✅ Fast
18:17:09 SMS sent (part 2/2), sending time 21 sec. ✅ Fast
18:18:20 The modem answer was not OK: [empty]     ⏳ Waiting for delivery report
18:19:22 The modem answer was not OK: [empty]     ⏳ Still waiting
18:20:48 The modem answer was not OK: +CMTI: "ME",1  ❌ Interrupted by notification
18:20:48 Sending failed, trying time 218 sec. Retries: 2.
```

**Analysis**:
- Actual SMS transmission: **~26 seconds** (acceptable)
- Delivery report wait: **~192 seconds** (excessive timeout)
- Root cause: Unsolicited +CMTI notifications interrupt delivery report handling
- Total time: **218 seconds** (~3.6 minutes)

**NOTE**: This is a SEPARATE issue from the initialization timeouts. This only happens when SMSTools successfully initializes and operates, which is currently rare.

---

## 4. WHAT WORKS vs WHAT DOESN'T

### 4.1 Direct AT Commands (WORKING ✅)

**Test performed** (SMSTools stopped):
```bash
$ sudo bash -c 'echo -e "AT+CMGF=1\r" > /dev/ttyUSB2; sleep 1; cat /dev/ttyUSB2'
OK

$ sudo bash -c 'echo -e "AT+CPMS=\"ME\",\"ME\",\"ME\"\r" > /dev/ttyUSB2; sleep 1; cat /dev/ttyUSB2'
+CPMS: 0,23,0,23,0,23
OK

$ sudo bash -c 'echo -e "AT+CSQ\r" > /dev/ttyUSB2; sleep 1; cat /dev/ttyUSB2'
+CSQ: 14,99
OK
```

**Conclusion**: Modem responds correctly and quickly to direct AT commands.

### 4.2 SMSTools Communication (FAILING ❌)

Same commands through SMSTools:
- Random 5-10 second timeouts
- Empty responses
- Desynchronized command/response pairs
- "Modem did not accept init string" errors

---

## 5. CONFIGURATION TESTED

### 5.1 Current Working Config (Partial Success)

```ini
[GSM1]
device = /dev/ttyUSB2
baudrate = 115200
init = AT+CMGF=1
init2 = AT+CPMS="ME","ME","ME"
report = yes
loglevel = 7

# Timing parameters
delaytime = 1
delaytime_mainprocess = 1
blocktime = 1
errorsleeptime = 1
```

**Result**: SMS receiving works sometimes, SMS sending works but very slow (3-4 min)

### 5.2 SIM Storage Attempt (FAILED)

```ini
init2 = AT+CPMS="SM","SM","SM"  # SIM card storage instead of modem memory
```

**Result**:
- Modem accepts command when tested directly: `+CPMS: 0,50,0,50,0,50 OK`
- SMSTools hangs during initialization - won't become operational
- Reverted to "ME","ME","ME" (modem memory)

### 5.3 CNMI Notification Control Attempt (CAUSED FREEZE)

**Goal**: Disable +CMTI unsolicited notifications that interrupt delivery reports

**Attempts**:
1. Added to init string: `AT+CNMI=2,0,0,0,0`
   - Result: SMSTools doesn't support multiline init
2. Tried init3 parameter
   - Result: "Unknown setting" - not supported
3. Manual configuration before SMSTools start
   - Result: Modem froze, required physical replug

---

## 6. MODEM-SPECIFIC OBSERVATIONS

### 6.1 Network Registration Timing

**Pattern observed**:
```
T+0s:  Modem plugged in
T+4s:  USB ports enumerate (ttyUSB0-4)
T+10s: +CSQ: 99,99 (no signal)
       +CREG: 2,2 (searching)
T+30s: +CSQ: 3,99 (weak signal detected)
       +CREG: 2,2 (still searching)
T+60s: +CSQ: 14,99 (good signal 45%)
       +CREG: 0,1 (registered home network)
```

**Implication**: SMSTools may attempt initialization before modem fully registers to network.

### 6.2 Unsolicited Result Codes (URCs)

**Observed URCs during operation**:
```
+CMTI: "ME",1          # New SMS arrived in modem memory location 1
+CREG: 2               # Network registration status changed
+CPIN: READY           # SIM card ready
SMS DONE               # SMS subsystem initialized
```

**Issue**: These URCs arrive asynchronously and appear to confuse SMSTools' command/response parser, causing "Unexpected input" errors.

### 6.3 Response Buffer Behavior

**Hypothesis**: SIM7600 may buffer responses differently than EC25 (previous modem):
- Responses arrive with variable delays
- Multiple responses may arrive in single read
- Line termination handling may differ

---

## 7. ROOT CAUSE HYPOTHESIS

### Issue #1 (Primary): Communication Timeout Mystery

**Evidence**:
1. ✅ Modem hardware works perfectly (direct AT commands respond <1 second)
2. ✅ USB serial driver works (no I/O errors in normal operation)
3. ❌ SMSTools sends AT command → waits 10 seconds → receives nothing
4. ✅ Same SMSTools config works with EC25 modem (previously deployed)

**The Mystery**:
- When we send `AT+CREG=2` directly to /dev/ttyUSB2, modem responds instantly
- When SMSTools sends the same command to the same port, modem doesn't respond
- **What is different?** Timing? Buffering? Line endings? DTR/RTS signals?

**Conclusion**: There is something in SMSTools' serial communication method that the SIM7600 doesn't respond to, but we don't know what yet.

### Issue #2 (Secondary): Delivery Report Delays

**Evidence from earlier successful session**:
- SMS sends successfully in 26 seconds
- SMSTools waits for delivery report
- During wait, incoming SMS triggers +CMTI notification
- SMSTools interprets +CMTI as "modem answer was not OK"
- Results in 3-4 minute timeout before retry

**Root Cause**:
- Unsolicited +CMTI notifications interrupt delivery report handling
- SMSTools expects specific response, gets +CMTI instead
- Falls into retry/timeout loop

### Critical Difference

**Issue #1**: Modem doesn't respond to SMSTools at all (no communication)
**Issue #2**: Modem responds, but wrong message type interrupts flow (communication works but +CMTI interferes)

These are SEPARATE problems requiring DIFFERENT solutions.

---

## 8. ATTEMPTED SOLUTIONS (ALL FAILED)

### 8.1 Increase Timeouts
- Tried longer timeout values in SMSTools config
- Result: Initialization still hangs, just takes longer to fail

### 8.2 Reduce Logging Overhead
- Disabled report_device_details
- Result: No improvement, still hangs after querying device

### 8.3 Change Storage Location
- Switched from modem memory (ME) to SIM storage (SM)
- Result: Modem accepts command but SMSTools won't initialize

### 8.4 Disable Unsolicited Notifications
- Attempted AT+CNMI=2,0,0,0,0 to suppress +CMTI
- Result: Modem froze, required physical replug

### 8.5 Clean Test Environment
- Cleared all SMS queues
- Cleared all logs
- Increased loglevel to 7 (maximum debug)
- Result: Problem persists - initialization still fails

---

## 9. CURRENT STATUS

### Issue #1 Status (Communication Timeouts)
**Current State**: ❌ **BLOCKING** - System non-functional
- SMSTools cannot initialize reliably
- Random 10-second AT command timeouts
- Modem handler terminates without error messages
- No workaround identified

### Issue #2 Status (Sending Delays)
**Current State**: ⚠️ **OBSERVED** - Only matters if Issue #1 resolved
- SMS sends successfully when system works
- Delivery report wait takes 3-4 minutes due to +CMTI interference
- Potential workaround: `report = no` (untested, loses delivery confirmation)

### Overall Production Readiness
❌ **NOT SUITABLE** - Issue #1 must be resolved before production deployment

---

## 10. DIAGNOSTIC DATA

### 10.1 Successful Direct Modem Test
```bash
# All commands return immediately (<1 second)
AT              → OK
AT+CMGF=1       → OK
AT+CPMS=?       → +CPMS: ("ME","MT","SM","SR"),("ME","MT","SM"),("ME","SM") OK
AT+CPMS="ME","ME","ME" → +CPMS: 0,23,0,23,0,23 OK
AT+CSQ          → +CSQ: 14,99 OK
AT+CREG?        → +CREG: 2,1 OK (registered)
AT+CNMI?        → +CNMI: 2,1,0,0,0 OK
```

### 10.2 Failed SMSTools Initialization Log
```
19:58:28 GSM1: Modem handler 0 has started. PID: 273215
19:58:28 GSM1: Checking if modem is ready
19:58:28 -> AT
19:58:28 Command is sent, waiting for the answer. (5)
19:58:28 <- OK  ✅
19:58:28 GSM1: Pre-initializing modem
19:58:28 -> AT+CREG=2
19:58:28 Command is sent, waiting for the answer. (10)
19:58:38 No answer, timeout occurred. 1.  ❌ 10-SECOND TIMEOUT
19:58:38 <- [empty]
19:58:38 Modem did not accept the pre-init string
19:58:38 -> AT+CMGF=1
19:58:38 Command is sent, waiting for the answer. (10)
[continues with multiple timeouts...]
```

### 10.3 SMS Sending Delay Log
```
18:16:43 -> AT+CMGS=...
18:16:43 <- >
18:16:43 -> [PDU data]
18:16:48 <- +CMGS: 217 OK  ✅ Sent successfully in 5 seconds
18:16:48 SMS sent (part 1/2), Message_id: 217, sending time 5 sec.

[SMSTools now waits for delivery report...]

18:18:20 The modem answer was not OK: [empty]  ⏳ Timeout
18:19:22 The modem answer was not OK: [empty]  ⏳ Timeout
18:20:48 The modem answer was not OK: +CMTI: "ME",1  ❌ Interrupted by notification
18:20:48 Sending failed, trying time 218 sec. Retries: 2.

Total time: 218 seconds (3 minutes 38 seconds)
```

---

## 11. QUESTIONS FOR SPECIALIST

### Priority #1: Initialization Timeout Issue (CRITICAL)

1. **Why doesn't SIM7600 respond to SMSTools' AT commands?**
   - Direct AT commands via bash work instantly (<1 sec)
   - SMSTools' AT commands timeout (10 sec, no response)
   - What is different in SMSTools' serial communication method?

2. **Serial port configuration differences?**
   - Flow control needed? (currently rtscts = no)
   - DTR/RTS signaling requirements?
   - Different baudrate/parity/stop bits needed?
   - Line ending characters (\r vs \r\n)?

3. **Is there a known SIM7600 + SMSTools3 incompatibility?**
   - Are there documented issues with this modem model?
   - Is there a SIM7600-specific configuration template?
   - Should we use different check_memory_method?

4. **Modem initialization sequence?**
   - Does SIM7600 need specific AT commands before accepting CREG?
   - Should initialization wait for network registration first?
   - Are there modem-specific init commands required?

### Priority #2: SMS Sending Delay Issue (SECONDARY - only if #1 resolved)

5. **How to handle +CMTI interrupting delivery report wait?**
   - Can unsolicited +CMTI be suppressed safely?
   - Should `report = no` be used (loses delivery confirmation)?
   - Is there a way to filter URCs during specific operations?

### General Questions

6. **Alternative solutions**
   - Should we use PDU mode instead of TEXT mode?
   - Should we consider a different SMS daemon (Gammu, ModemManager)?
   - Is custom Python script with pyserial more suitable for SIM7600?

---

## 12. ATTACHED LOG FILES

- **Full SMSTools log**: /var/log/smstools/smsd.log
- **Current configuration**: /etc/smsd.conf
- **Working backup config**: /etc/smsd.conf.backup_before_sim7600_fix
- **Port mapping**: /home/rom/sim7600_ports.json
- **Modem detector log**: `journalctl -u sim7600-detector -n 100`

---

## 13. CONTACT & ENVIRONMENT

**System**: Raspberry Pi GSM Gateway (Production)
**Location**: United Kingdom (Vodafone network)
**Critical**: Yes - SMS functionality required for business operations
**Assistance Needed**: Configuration guidance or alternative solution for SIM7600 + SMSTools

---

**Report Generated**: October 15, 2025
**Diagnostic Session Duration**: ~4 hours
**Status**: Issue unresolved - seeking specialist guidance
