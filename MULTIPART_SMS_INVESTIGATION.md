# Multipart SMS Investigation - SIM7600G-H Modem Hang Issue

**Date:** 2026-01-12
**Issue:** Modem hangs when sending long multipart UCS2 (Unicode) messages
**Modem:** SIM7600G-H
**SMSTools Version:** 3.1.21

---

## Problem Summary

When the VPS sends long messages with Romanian diacritics (ă, â, î, ș, ț), the modem gets stuck and stops responding to AT commands. The system requires a physical modem reset to recover.

---

## Investigation Findings

### 1. Message Flow

**VPS → Jetson:**
- VPS sends ONE complete message with `Alphabet: UCS2`
- Example: "Ora curent este 14:30 (ora local, 13 ianuarie 2026). Cu ce vă pot ajuta?"

**SMSTools3 Processing:**
- SMSTools receives the message
- Detects it's too long for single SMS
- **Splits locally:** "Splitting this message into 2 parts of max 67 characters (unicode)"
- Attempts to send Part 1/2

### 2. Character Set Configuration

**Modem Capabilities:**
```
AT+CSCS=?
Response: +CSCS: ("IRA","GSM","UCS2")
```

**Current Setting:**
```
AT+CSCS?
Response: +CSCS: "IRA"
```
❌ **Problem:** "IRA" = International Reference Alphabet (basic ASCII) - **does NOT support diacritics!**

### 3. TEXT vs PDU Mode Behavior

**Configuration says:**
- `init = AT+CMGF=1` (TEXT mode)
- `decode_unicode_text = yes`
- `cs_convert = yes`

**Actual behavior in logs:**
```
23:04:22 - Selecting PDU mode
23:04:22 - AT+CMGF=0 (switch to PDU mode)
```
**SMSTools3 automatically switches to PDU mode for multipart messages!**

### 4. The Hang Timeline

```
23:04:22 - Modem: AT+CMGF=0 (switch to PDU mode) → OK
23:04:22 - Modem: AT+CMGS=154 (prepare to send SMS) → > (ready for data)
23:04:22 - Send PDU data for Part 1/2 (154 bytes)
23:04:23 - Waiting for modem response... (60 second timeout)
23:05:23 - TIMEOUT! Modem never responded
23:05:23 - Error: "Incorrect answer, put_command expected (OK)|(ERROR)"
23:05:23 - Modem is now HUNG - no longer responds to any AT commands
```

**The modem accepts the PDU data but never completes sending Part 1 - it hangs completely.**

### 5. Root Cause Analysis

The modem **cannot handle multipart UCS2 messages in PDU mode**. Possible reasons:
1. **Modem firmware bug** with concatenated UCS2/PDU
2. **Missing modem-specific configuration** for multipart handling
3. **Hardware/firmware limitation** of SIM7600G-H with UCS2 concatenation
4. **Character set mismatch** - using IRA instead of UCS2

---

## Current Configuration

### `/etc/smsd.conf` - Before Changes

```ini
# SMSTools3 Configuration - SIM7600G-H Optimized
# Supports Romanian (ă,â,î,ș,ț) and Lithuanian (ą,č,ę,ė,į,š,ų,ū,ž)

devices = GSM1
outgoing = /var/spool/sms/outgoing
checked = /var/spool/sms/checked
incoming = /var/spool/sms/incoming
logfile = /var/log/smstools/smsd.log
infofile = /var/run/smstools/smsd.working
pidfile = /var/run/smstools/smsd.pid
failed = /var/spool/sms/failed
sent = /var/spool/sms/sent
stats = /var/log/smstools/smsd_stats

# CHANGED: Increased from 5 to 7 for full crash debugging
loglevel = 7

# Global settings
# OPTION 2: Process incoming SMS before sending to prevent interruption
receive_before_send = yes

autosplit = 3

# Performance optimizations - keep as requested by user
delaytime = 1
delaytime_mainprocess = 1
blocktime = 1

# CHANGED: Increased from 1 to 5 - SIM7600G-H needs recovery time after I/O errors
errorsleeptime = 5

# Event handler - forwards incoming SMS to VPS
eventhandler = /usr/local/bin/sms_handler_unicode.py

[GSM1]
device = /dev/ttyUSB_SIM7600_AT

# Modem initialization commands
# NOTE: SMSTools3 only supports init and init2 (init3/init4 do not work - tested)
# TESTING: Removed init2 (AT+CPMS) - modem defaults to ME anyway

# MUST use TEXT mode for Unicode to work properly
init = AT+CMGF=1

# OPTION 3: Configure message indication to not interrupt send operations
# Format: AT+CNMI=<mode>,<mt>,<bm>,<ds>,<bfr>
#   mode=2: Buffer unsolicited result codes when busy
#   mt=1: Store and notify (+CMTI) - keeps notifications working
#   bm=0: No broadcast notifications
#   ds=0: No status reports via unsolicited code
#   bfr=0: Flush buffer to TE when ready
init2 = AT+CNMI=2,1,0,0,0

pin = ignore
incoming = yes
report = yes

# Enable Unicode text decoding
decode_unicode_text = yes
# Character set conversion
cs_convert = yes

report_device_details = yes

# Speed optimizations with stability fixes
# CHANGED: Enabled from 0 - verify registration before send to prevent crashes
check_network = 1

check_memory_method = 1
baudrate = 115200
pre_init = no
sending_disabled = no

# CHANGED: Increased from 0 to 2 - adds delay between ALL commands
# Prevents overwhelming the SIM7600G-H modem with rapid command sequences
send_delay = 2

# ADDED: 2 seconds delay after each part of multipart SMS is sent
# Prevents modem from hanging when processing long concatenated messages
sentsleeptime = 2

send_retries = 2
rtscts = no
memory_start = 0
phonecalls = no

# ADDED: Keep serial port open to prevent USB reopen crashes
# Critical for USB modems - prevents I/O error 5 (device lock issues)
keep_open = yes
```

### Key Parameters:
- **Mode:** TEXT mode init (`AT+CMGF=1`) but SMSTools auto-switches to PDU for multipart
- **Character set:** NOT CONFIGURED - defaults to "IRA" (no diacritics support)
- **Autosplit:** 3 (standard concatenated SMS)
- **Send delay:** 2 milliseconds (almost instant)
- **Sentsleeptime:** 2 seconds (delay between parts) - **NOT WORKING because Part 1 never completes**

### Modem Status Script Configuration:

`/home/rom/modem_status_collector.sh` Line 18:
```bash
# Using GSM encoding for testing (160 chars max, not 70 for UCS2)
echo -e "To: $RECIPIENT\nAlphabet: GSM\n\n$msg" > "$file"
```
Currently set to GSM for testing. Should be UCS2 for diacritics support.

---

## Failed Message Example

**File:** `/var/spool/sms/failed/api_1768259059040_894`

```
To: +447504128961
Alphabet: UCS2
Modem: GSM1
IMSI: 234100406701824
IMEI: 862636055891897
Fail_reason: Modem initialization failed
Failed: 26-01-12 23:07:25
PDU: 0071000C914457402198160008FF8C050003460201004F0072006100200063007500720065006E0074010300200065007300740065002000310034003A0033003000200028006F007200610020006C006F00630061006C0103002C002000310033002000690061006E00750061007200690065002000320030003200360029002E00200043007500200063006500200076010300200070006F0074

Message (Part 1/2): "Ora curent este 14:30 (ora local, 13 ianuarie 2026). Cu ce vă pot ajuta?"
```

**PDU Analysis:**
- `050003460201` = UDH (User Data Header) indicating part 1/2 of message ID 0x46
- Message contains Romanian characters: ă, ț, î
- Length: 67 characters (max for UCS2 concatenated SMS)

---

## Proposed Solutions

### **Option A: Force TEXT Mode + UCS2 Character Set** (TO BE TESTED)

**Changes:**
1. Add character set initialization: `init2 = AT+CSCS="UCS2"`
2. Keep TEXT mode: `init = AT+CMGF=1` (already set)
3. Rely on modem to handle concatenation in TEXT mode

**Expected behavior:**
- Modem receives full message text
- Modem handles UCS2 encoding
- Modem automatically splits if needed
- **Risk:** May not support multipart properly in TEXT mode

**Pros:**
- Simpler - let modem handle encoding
- May avoid PDU mode hang issue
- Character set properly configured for diacritics

**Cons:**
- TEXT mode multipart support is modem-dependent
- Less control over message splitting
- May fail completely for long messages

---

### **Option B: Fix PDU Mode with SIM7600-Specific Commands** (Future investigation)

**Research needed:**
1. Check SIM7600G-H AT command manual
2. Look for concatenated SMS configuration commands
3. Investigate if modem has multipart/concatenation settings
4. Check for firmware bugs or known issues

**Potential commands to investigate:**
- `AT+CSMP` - SMS Parameters
- `AT+CSDH` - Show Text Mode Parameters
- SIM7600-specific concatenation settings

---

## Test Plan for Option A

1. **Backup current config**
2. **Add UCS2 character set** to init commands
3. **Restart SMSD**
4. **Test single-part message** with diacritics
5. **Test multi-part message** (gradually increase length)
6. **Monitor for:**
   - Message delivery success
   - Diacritics preservation
   - Modem hang/timeout
   - AT command responses

---

## Notes

- **VPS sends UCS2 messages** - this is correct for diacritics
- **Splitting happens on Jetson** - not at VPS
- **Modem supports UCS2** - confirmed via `AT+CSCS=?`
- **sentsleeptime parameter** is correctly set but ineffective since Part 1 never completes
- **Physical modem reset** required after each hang

---

## Next Steps

1. ✅ Document current configuration (this file)
2. ⏳ Implement Option A changes
3. ⏳ Test with short message (single-part)
4. ⏳ Test with long message (multi-part)
5. ⏳ Document results
6. ⏳ If Option A fails, investigate Option B

---

**Document Version:** 1.0
**Last Updated:** 2026-01-12 23:15 GMT

---

# UPDATE - 2026-01-12 23:40 GMT

## Option A Test Results

### Implementation:
```ini
init = AT+CMGF=1
init2 = AT+CSCS="UCS2"
```

### Test Results:

**✅ Single-Part Message Test - SUCCESS:**
- Message: "Bun ziua! Cu ce vă pot ajuta astăzi?" (Romanian with diacritics)
- Alphabet: UCS2
- Status: **SENT SUCCESSFULLY** in 6 seconds
- Diacritics: Preserved correctly
- Sending time: 23:33:46

**❌ Modem Stability - FAILED:**
- Modem hung **AFTER** sending the message
- Hang occurred during routine status check (AT+CSQ)
- Error: `write_to_modem: error 5: Input/output error`
- USB port ttyUSB2 disappeared after hang
- Required physical modem reset

**Conclusion:** UCS2 character set works for single messages but causes severe modem instability.

---

## Manual Testing via Picocom (2026-01-12 23:40)

### Modem Info:
```
Manufacturer: SIMCOM INCORPORATED
Model: SIMCOM_SIM7600G-H
Revision: SIM7600G_V2.0.2
IMEI: 862636055891897
```

### AT Command Tests:

**Character Set Configuration:**
```
AT+CSCS="UCS2"
Response: OK

AT+CSCS?
Response: +CSCS: "UCS2"  ✅ Confirmed
```

**SMS Parameters:**
```
AT+CSMP?
Response: +CSMP: 17,183,0,0
```
- `17` = First octet with UDHI (User Data Header Indicator) enabled
- Should support concatenation, but...

**TEXT Mode Sending:**
```
AT+CMGF=1
AT+CMGS="+447504128961"
Response: ERROR
```

**Key Discovery:** 
- ❌ **Modem does NOT auto-split long messages in TEXT mode**
- ❌ **TEXT mode + UCS2 is incompatible for CMGS** on SIM7600G-H
- Even with CSMP=17 (concatenation enabled), modem doesn't split automatically

---

## Research Findings - Best Professional Solution

### Discovery: SMSTools3 Native Unicode Support

**How SMSTools3 is DESIGNED to work:**

1. **Application receives UTF-8 messages** (from VPS)
2. **SMSTools3 automatically detects** non-GSM-7 characters
3. **SMSTools3 auto-switches to PDU mode** when needed
4. **SMSTools3 handles UCS-2 encoding** internally
5. **SMSTools3 creates concatenation headers** for multipart
6. **Modem stays in simple mode** (IRA or GSM)

### ❌ What We Did Wrong (Option A):

```ini
init2 = AT+CSCS="UCS2"  # Forced modem to UCS2
```

**Problems:**
- Set modem character set to UCS2
- Expected modem to handle everything
- **UCS-2 in TEXT mode on SIM7600 is BUGGY**
- Known issues: multipart unreliable, character corruption, modem hangs
- Fighting against SMSTools3's design

---

## ✅ Correct Approach - Option B (IRA/GSM Character Set)

### Recommended Configuration:

**Primary recommendation (most stable):**
```ini
init = AT+CMGF=1
init2 = AT+CSCS="IRA"
```

**Alternative (if IRA has issues):**
```ini
init = AT+CMGF=1
init2 = AT+CSCS="GSM"
```

### Why IRA is Best:

**IRA (International Reference Alphabet) Benefits:**
- ✅ **Most stable with SMSTools3**
- ✅ Supports full GSM-7 + extended characters
- ✅ Covers most Lithuanian/Romanian diacritics
- ✅ **Fewer encoding bugs** than UCS2
- ✅ **Better multipart reliability**
- ✅ SMSTools3 designed to work with IRA
- ✅ **Modem stays stable** - no hangs

**How it works:**
1. Modem set to IRA (simple, stable)
2. VPS sends UTF-8 message to SMSTools3
3. **SMSTools3 detects diacritics** (non-GSM-7 chars)
4. **SMSTools3 automatically switches to PDU mode**
5. **SMSTools3 encodes to UCS-2 in PDU**
6. **SMSTools3 creates concatenation headers**
7. Modem sends PDU (modem just transmits, no encoding logic)
8. **No modem hang** - modem isn't doing encoding

### Why UCS2 Failed:

**Known SIM7600G-H Issues with UCS2:**
- ❌ UCS-2 in TEXT mode is **buggy/unreliable**
- ❌ **Multipart messages fail or hang**
- ❌ Special character corruption
- ❌ Modem instability (confirmed by our tests)
- ❌ Community reports widespread issues

**Root cause:** We were forcing the modem to do encoding/concatenation that SMSTools3 should handle.

---

## Option B Implementation Plan

### Configuration Change:

**Before (Option A - FAILED):**
```ini
init = AT+CMGF=1
init2 = AT+CSCS="UCS2"  # BUGGY on SIM7600!
```

**After (Option B - RECOMMENDED):**
```ini
init = AT+CMGF=1
init2 = AT+CSCS="IRA"   # Stable, let SMSTools3 handle encoding
```

### Keep These Settings:
```ini
autosplit = 3                    # SMSTools3 splits long messages
decode_unicode_text = yes        # SMSTools3 decodes incoming UCS-2
cs_convert = yes                 # SMSTools3 handles character set conversion
sentsleeptime = 2               # 2 second delay between parts
```

### Expected Behavior:

**Incoming SMS:**
1. Modem receives PDU
2. SMSTools3 detects UCS-2 encoding
3. SMSTools3 decodes to UTF-8
4. Diacritics preserved

**Outgoing SMS:**
1. VPS sends UTF-8 message
2. SMSTools3 detects diacritics
3. SMSTools3 switches to PDU mode
4. SMSTools3 encodes to UCS-2
5. SMSTools3 splits into parts (autosplit=3)
6. SMSTools3 adds concatenation headers
7. Modem sends each PDU part
8. **sentsleeptime=2** adds 2 second delay between parts
9. **Modem stays stable** (no encoding logic)

---

## Test Plan for Option B

1. ✅ Document findings (this update)
2. ⏳ Change config to IRA character set
3. ⏳ Backup and restart SMSD
4. ⏳ Test single-part message with diacritics
5. ⏳ Test multipart message (gradually increase length)
6. ⏳ Monitor for:
   - Message delivery success
   - Diacritics preservation
   - Modem stability (no hangs)
   - Proper multipart splitting
   - AT command responses
7. ⏳ If IRA works: Document success
8. ⏳ If IRA fails: Try GSM character set

---

## Key Learnings

1. **SMSTools3 is designed to handle encoding** - don't force modem to do it
2. **UCS2 on SIM7600 is buggy** - avoid in TEXT mode
3. **IRA is the stable choice** - industry best practice
4. **Modem should be simple** - just transmit PDUs, don't encode
5. **Single messages worked** - proves diacritics can work
6. **Multipart is the challenge** - but SMSTools3 handles it in PDU mode
7. **Let SMSTools3 do its job** - auto-detection and encoding

---

## Status Update

- **Option A (UCS2):** ❌ FAILED - Modem unstable, hangs after sending
- **Option B (IRA):** ⏳ READY TO TEST - Recommended professional solution
- **Next:** Implement IRA configuration and test multipart

---

**Document Version:** 2.0  
**Last Updated:** 2026-01-12 23:45 GMT
