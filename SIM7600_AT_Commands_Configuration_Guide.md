# SIM7600 Modem Configuration - AT Commands Documentation

## Configuration Sequence (as used by sim7600_detector.py)

### STEP 0: USB Composition Verification
**Purpose:** Ensure modem is in stable voice mode (9001)

```
lsusb check for: 1e0e:9001
```
- **9001** = Stable voice mode (required for VoLTE)
- **9011** = Fast data mode (causes ttyUSB3/4 instability)  
- **9024** = Alternative mode

---

### VERIFICATION PHASE

**AT** - Test modem communication
```
Command: AT
Response: OK
Purpose: Basic connectivity test
```

**AT+CGMI** - Get Manufacturer
```
Command: AT+CGMI
Response: SIMCOM INCORPORATED
Purpose: Verify it's a SIMCOM modem
```

**ATI** - Get comprehensive modem info
```
Command: ATI
Response: Manufacturer: SIMCOM INCORPORATED
         Model: SIMCOM_SIM7600G-H
         Revision: SIM7600M22_V2.0
         IMEI: 862636055891897
Purpose: Get model, firmware, IMEI in one command
```

**AT+CPIN?** - Check SIM card status
```
Command: AT+CPIN?
Response: +CPIN: READY
Purpose: Verify SIM card is inserted and unlocked
Why: Must check BEFORE reading IMSI (fails if SIM not ready)
```

**AT+CIMI** - Get IMSI (SIM identity)
```
Command: AT+CIMI
Response: 234XXXXXXXXXXX (15 digits)
Purpose: Identify carrier from IMSI prefix
Why: Used to auto-detect carrier and load correct APNs
```

---

### STEP 3: Configure APNs (Data + IMS)

**AT+CGDCONT=1,"IP","everywhere"** - Configure Data APN
```
Command: AT+CGDCONT=1,"IP","everywhere"
Response: OK
Purpose: Set PDP context 1 for data/internet
Context: 1 = Data context (internet access)
APN: "everywhere" (carrier-specific, varies by IMSI)
Type: IP or IPV4V6
```

**AT+CGDCONT=2,"IPV4V6","ims"** - Configure IMS APN  
```
Command: AT+CGDCONT=2,"IPV4V6","ims"
Response: OK
Purpose: Set PDP context 2 for IMS/VoLTE
Context: 2 = IMS context (voice over LTE)
APN: "ims" (standard for most carriers)
Type: IPV4V6 (REQUIRED - IP alone causes failure!)
Why IMS: Needed for VoLTE calls. Without this, calls use 3G fallback.
Why IPV4V6: IMS requires dual-stack. Using "IP" will cause activation failure.
```

**⚠️ CRITICAL:** IMS APN MUST use IPV4V6, not IP!

---

### STEP 4: Wait for Network to Settle
```
sleep 10 seconds
Purpose: Let network register and stabilize after APN config
```

---

### STEP 5: Activate PDP Contexts

**AT+CGACT=1,1** - Activate Data context
```
Command: AT+CGACT=1,1
Response: OK
Purpose: Activate PDP context 1 (data/internet)
Context: 1 = Data
Action: 1 = Activate
⚠️ HIGH POWER: Can cause EMI during transmission
```

**AT+CGACT=1,2** - Activate IMS context
```
Command: AT+CGACT=1,2
Response: OK
Purpose: Activate PDP context 2 (IMS for VoLTE)
Context: 2 = IMS
Action: 1 = Activate
Why: VoLTE REQUIRES active IMS context
```

---

### STEP 6: Enable VoLTE

**AT+CEVOLTE?** - Query VoLTE status
```
Command: AT+CEVOLTE?
Response: +CEVOLTE: 1,1  (if supported)
         ERROR (if not supported)
Purpose: Check if VoLTE is already enabled
```

**AT+CEVOLTE=1,1** - Enable VoLTE
```
Command: AT+CEVOLTE=1,1
Response: OK or ERROR
Purpose: Enable VoLTE for voice calls over LTE
Parameter 1: 1 = Enable VoLTE
Parameter 2: 1 = Enable
Why: Without VoLTE, calls fall back to 3G (CSFB)
Note: Some carriers enable this automatically via network
```

---

### STEP 7: Force LTE-Only Mode (CRITICAL for VoLTE)

**AT+CNMP=38** - Set network mode to LTE-only
```
Command: AT+CNMP=38
Response: OK
Purpose: FORCE LTE-only mode, prevent 3G fallback
```

**Network Mode Reference (AT+CNMP):**
- **2** = Automatic (allows 2G/3G fallback) ← DEFAULT (bad for VoLTE!)
- **13** = GSM Only (2G)
- **14** = WCDMA Only (3G)
- **38** = **LTE Only** ← REQUIRED for VoLTE
- **39** = GSM+WCDMA+LTE
- **51** = GSM+LTE
- **54** = WCDMA+LTE

**Why Mode 38 is CRITICAL:**
1. **Forces VoLTE:** No 3G fallback during calls
2. **Fast PCM Init:** Audio starts in ~200ms (vs 2s on 3G)
3. **No CSFB:** Prevents Circuit Switched Fallback to 3G
4. **Future-proof:** 2G/3G networks shutting down (UK: 2025)

**⚠️ Problem:** Without AT+CNMP=38, modem falls back to 3G during calls, causing:
- Slow audio initialization (2+ seconds)
- No VoLTE (uses old circuit-switched calls)
- Incompatible with network shutdowns

---

### STEP 8: Verify Configuration

**AT+CPSI?** - Get system information
```
Command: AT+CPSI?
Response: +CPSI: LTE,Online,234-20,0x8FC8,42013412,125,EUTRAN-BAND3,1851,...
Purpose: Verify modem is on LTE network
Check: "LTE" in response = good, "WCDMA"/"GSM" = bad
```

**AT+CNSMOD?** - Get network system mode
```
Command: AT+CNSMOD?
Response: +CNSMOD: 0,8  (8 = LTE)
Purpose: Detailed network technology check
Modes: 8=LTE, 7=HSPA, 4=WCDMA, 2=GPRS, 1=GSM
```

**AT+CEREG?** - Check EPS (LTE) registration
```
Command: AT+CEREG?
Response: +CEREG: 0,1  (1=registered home, 5=roaming)
Purpose: Verify registered on LTE network
```

**AT+CGDCONT?** - Verify APN configurations
```
Command: AT+CGDCONT?
Response: +CGDCONT: 1,"IP","everywhere","",0,0
          +CGDCONT: 2,"IPV4V6","ims","",0,0
Purpose: Confirm both APNs are configured correctly
```

**AT+CGACT?** - Verify PDP context activation
```
Command: AT+CGACT?
Response: +CGACT: 1,1  (context 1 active)
          +CGACT: 2,1  (context 2 active)
Purpose: Confirm both contexts are activated
Check: Both should show ",1" (active)
```

---

### STEP 9: Save Configuration to NVRAM (CRITICAL!)

**AT&W** - Write settings to non-volatile memory
```
Command: AT&W
Response: OK
Purpose: SAVE all configurations permanently
Why: Without this, ALL settings lost on modem reset!
Saves:
  - APNs (Data + IMS)
  - VoLTE settings
  - Network mode (AT+CNMP=38)
  - PDP contexts
```

**⚠️ CRITICAL:** Without AT&W, modem reverts to defaults on:
- Power cycle
- USB re-enumeration
- Modem reset (AT+CFUN=1,1)
- System reboot

---

## Why SMS Might Fail - Configuration Issues

### 1. IMS APN Misconfiguration
**Problem:** IMS APN set to "IP" instead of "IPV4V6"
```
BAD:  AT+CGDCONT=2,"IP","ims"       ← Fails to activate
GOOD: AT+CGDCONT=2,"IPV4V6","ims"   ← Works
```
**Impact:** IMS context won't activate → VoLTE fails → calls use 3G

### 2. Wrong Network Mode
**Problem:** AT+CNMP=2 (Automatic) allows 3G fallback
```
BAD:  AT+CNMP=2   ← Falls back to 3G during calls
GOOD: AT+CNMP=38  ← Stays on LTE, VoLTE works
```
**Impact:** SMS may work on 3G but causes:
- Slow call audio initialization
- No VoLTE
- Data interruption during calls

### 3. Inactive PDP Contexts
**Problem:** Context 2 (IMS) not activated
```
Check: AT+CGACT?
Should show:
  +CGACT: 1,1  ← Data context active
  +CGACT: 2,1  ← IMS context active (required!)
```
**Impact:** VoLTE unavailable → falls back to 3G

### 4. Settings Not Saved (No AT&W)
**Problem:** Configuration lost on modem reset
```
Missing: AT&W command after configuration
Result: Modem resets to AT+CNMP=2, default APNs
```
**Impact:** Works until next reboot, then breaks

### 5. Port Conflicts
**Problem:** SMSTools running during configuration
```
Solution: Stop SMSTools before configuring
Command: systemctl stop smstools
```
**Impact:** AT commands timeout or fail

---

## Configuration Summary

**Minimal working configuration for VoLTE + SMS:**
```bash
# 1. Configure APNs
AT+CGDCONT=1,"IP","everywhere"        # Data APN
AT+CGDCONT=2,"IPV4V6","ims"           # IMS APN (IPV4V6 required!)

# 2. Activate contexts
AT+CGACT=1,1                          # Activate data
AT+CGACT=1,2                          # Activate IMS

# 3. Enable VoLTE (optional, may auto-enable)
AT+CEVOLTE=1,1

# 4. CRITICAL: Force LTE-only mode
AT+CNMP=38                            # LTE-only, no 3G fallback

# 5. CRITICAL: Save everything
AT&W                                  # Save to NVRAM
```

**Total: 6 commands** (5 config + 1 save)

---

## Port Usage Strategy

**Correct approach (bulletproof):**
- **Configuration:** Use `/dev/ttyUSB_SIM7600_AT` (ttyUSB2) via symlink
  - Stop SMSTools first
  - Run all AT commands
  - Restart SMSTools after

- **Voice Bot:** Use `/dev/ttyUSB_SIM7600_VOICE` (ttyUSB3) via symlink
  - Never touch during configuration
  - Dedicated for voice calls only

- **SMSTools:** Use `/dev/ttyUSB_SIM7600_AT` (ttyUSB2) via symlink
  - Shares port with configuration (time-multiplexed)

**Why symlinks:**
- Survive USB re-enumeration
- Port numbers won't change
- No hardcoded device paths

---

## Troubleshooting

**Check current network mode:**
```bash
AT+CNMP?
Response: +CNMP: 38  ← Good (LTE-only)
Response: +CNMP: 2   ← Bad (Automatic, allows 3G)
```

**Check if settings are saved:**
```bash
# Restart modem
AT+CFUN=1,1

# Wait 30s, then check
AT+CNMP?
# Should still show 38 if AT&W was run
```

**Verify VoLTE ready:**
```bash
AT+CGDCONT?   # Both contexts configured?
AT+CGACT?     # Both contexts active (,1)?
AT+CNMP?      # Mode 38 (LTE-only)?
AT+CPSI?      # Currently on LTE?
```

---

**Document created:** $(date)  
**System:** Jetson Orin Nano - SIM7600G-H Modem  
**Configuration Script:** /home/rom/sim7600_detector.py
