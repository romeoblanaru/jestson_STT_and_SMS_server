# EC25-AUX vs SIM7600G-H Modem Comparison

**Test Date:** October 11, 2025
**Test Setup:** Raspberry Pi 4B, UK network (giffgaff/O2 and Vodafone)

---

## Summary

| Feature | EC25-AUX | SIM7600G-H |
|---------|----------|------------|
| **Outgoing Calls** | ✅ Works | ✅ Works |
| **Incoming Calls** | ❌ Network rejects ("cannot connect") | ⚠️ Network accepts (rings) but not answered |
| **USB Audio** | ✅ hw:EC25AUX appears | ❌ Enabled but device doesn't enumerate |
| **VoLTE/IMS** | ✅ Configurable | ⚠️ Carrier-dependent |
| **Network** | O2 UK / giffgaff (234-10) | Vodafone UK (234-15) |
| **Firmware** | EC25AUXGAR08A15M1G (A0.301) | SIM7600G_V2.0.2 |

---

## Detailed Testing Results

### EC25-AUX (Quectel)

**SIM:** giffgaff (O2 UK)
**IMSI:** 234100406701824
**IMEI:** 862708045450728

#### Configuration Applied:
```bash
AT+QCFG="usbnet",0                              # QMI mode
AT+QCFG="usbcfg",0x2C7C,0x0125,1,1,1,1,1,0,1  # USB composite (QMI + Audio)
AT+QPCMV=1,2                                    # USB audio enabled
AT+QCFG="ims",1                                 # IMS/VoLTE enabled
AT+QICSGP=2,1,"ims","","",2                     # IMS APN configured
AT&W                                            # Save to NV memory
```

#### Test Results:

**Outgoing Calls:** ✅ SUCCESS
```
ATD07504128961; → OK
Call connects successfully
```

**Incoming Calls:** ❌ FAILED
- Operator message: "It's not possible to connect your call"
- Network rejects call before device rings
- Possible causes:
  - VoLTE not fully registered with IMS server
  - Carrier provisioning issue (giffgaff data SIM?)
  - Missing APN configuration on network side

**USB Audio:** ✅ SUCCESS
```
$ arecord -l
card 3: EC25AUX [EC25-AUX], device 0: USB Audio [USB Audio]
```

**Network Status:**
```
AT+COPS? → +COPS: 0,0,"O2 - UK giffgaff",7
AT+CREG? → +CREG: 0,1  (Registered, home network)
AT+CSQ   → +CSQ: 15,99 (Signal: 48%)
```

---

### SIM7600G-H (SIMCom)

**SIM:** Vodafone UK
**IMSI:** 234159593176535
**IMEI:** 862636055891897

#### Configuration Applied:
```bash
AT+CUSBAUDIO=1   # USB audio enabled
AT&W             # Save to NV memory
AT+CFUN=1,1      # Restart modem (via picocom -x 3000)
```

#### Test Results:

**Outgoing Calls:** ✅ SUCCESS
```
ATD07504128961; → OK
Call connects successfully
```

**Incoming Calls:** ⚠️ PARTIALLY WORKING
- **Network accepts call** - phone rings!
- No answer mechanism (no voice bot service)
- Console freezes when ringing (port blocked)
- Requires manual answer: `ATA`

**USB Audio:** ❌ FAILED TO ENUMERATE
```
AT+CUSBAUDIO? → +CUSBAUDIO: 1  (Enabled in firmware)
$ arecord -l → No device found
```
**Issue:** Setting enables USB audio in modem firmware, but Linux doesn't detect USB audio device. May be SIM7600G limitation or need different USB PID mode.

**Network Status:**
```
AT+COPS? → +COPS: 0,0,"vodafone UK",7
AT+CREG? → +CREG: 0,1  (Registered, home network)
AT+CSQ   → +CSQ: 17,99 (Signal: 54%)
```

---

## Key Findings

### 1. Incoming Call Behavior Difference

**EC25:** Network-level rejection
- Call never reaches the modem
- Operator intercepts before ringing
- Suggests IMS/VoLTE registration issue

**SIM7600G:** Device-level issue
- Call reaches the modem (rings!)
- Network routing works correctly
- Just needs answer mechanism

**Conclusion:** SIM7600G has better incoming call support. Network accepts the call.

### 2. USB Audio Support

**EC25:** Full USB audio support
- Device enumerates as USB Audio Class
- hw:EC25AUX appears in arecord -l
- Ready for voice bot integration

**SIM7600G:** Firmware support only
- AT+CUSBAUDIO=1 enables in firmware
- USB device doesn't enumerate in Linux
- May need alternative voice handling

### 3. VoLTE/IMS Configuration

**EC25:** Explicit configuration
- AT+QCFG="ims",1 enables IMS
- AT+QICSGP=2 configures IMS APN
- Settings save with AT&W

**SIM7600G:** Limited configuration
- No AT+CVOLTE command
- Carrier-dependent VoLTE
- Vodafone UK may auto-provision

---

## Issues Identified

### 1. Asterisk udev Rule Conflict (RESOLVED)

**File:** `/etc/udev/rules.d/99-ignore-all-modems.rules`

Old rule was setting all USB modems to `asterisk` ownership, causing permission conflicts.

**Solution:** Disabled the rule
```bash
sudo mv /etc/udev/rules.d/99-ignore-all-modems.rules \
         /etc/udev/rules.d/99-ignore-all-modems.rules.disabled
```

### 2. Port Freezing Issues

**Cause:** Multiple tools accessing serial port simultaneously
- SMSTools holds port exclusively
- AT commands cause freeze when services running
- Incoming calls freeze console when not handled

**Solution:** Always stop services before AT commands
```bash
sudo systemctl stop smstools ec25-voice-bot
# ... send AT commands ...
sudo systemctl start smstools ec25-voice-bot
```

### 3. AT+CFUN=1,1 Freeze Issue (RESOLVED)

**Problem:** Modem restart command caused system freeze
```bash
AT+CFUN=1,1  # Hangs indefinitely
```

**Solution:** Use picocom with exit timeout
```bash
echo -e "AT+CFUN=1,1\r\n" | picocom -b 115200 -x 3000 /dev/ttyUSB2
sleep 40  # Wait for modem restart
```

---

## Recommendations

### For EC25-AUX:
1. ✅ USB audio works - use for voice bot
2. ❌ Incoming calls broken - investigate IMS registration
3. Check if giffgaff SIM supports voice (might be data-only)
4. Consider switching to different carrier SIM for testing

### For SIM7600G-H:
1. ✅ Incoming calls ring - **best option for testing**
2. ❌ USB audio doesn't enumerate - use external audio or serial AT commands
3. Create voice bot service to answer incoming calls
4. Vodafone network routing works correctly

### Next Steps:
1. **Test SIM7600G with voice bot** - adapt ec25-voice-bot to use SIM7600G
2. **Compare with external audio** - use Asterisk or simple ATA answer
3. **Swap SIMs between modems** - test if issue is SIM or modem specific
4. **Check carrier provisioning** - contact giffgaff/Vodafone about VoLTE activation

---

## Configuration Scripts

### Initialization Script
**Location:** `/home/rom/modem_manager/scripts/initialize_modem.sh`

**Features:**
- Auto-detects EC25 or SIM7600G
- Checks and enables USB audio
- Checks and enables VoLTE/IMS
- Stops/restarts services safely
- Uses safe restart command (no freeze)
- Sends notification when done

**Usage:**
```bash
sudo /home/rom/modem_manager/scripts/initialize_modem.sh
```

### udev Rules

**EC25:** `/etc/udev/rules.d/99-quectel-ec25-stable.rules`
```bash
SUBSYSTEM=="tty", ATTRS{idVendor}=="2c7c", ATTRS{idProduct}=="0125", ATTRS{bInterfaceNumber}=="02", SYMLINK+="ttyUSB_EC25_DATA"
```

**SIM7600G:** `/etc/udev/rules.d/99-simcom-sim7600-stable.rules`
```bash
SUBSYSTEM=="tty", ATTRS{idVendor}=="1e0e", ATTRS{idProduct}=="9001", ATTRS{bInterfaceNumber}=="02", SYMLINK+="ttyUSB_SIM7600_DATA"
```

---

## Conclusion

**Winner: SIM7600G-H** ✅

Despite USB audio enumeration issues, SIM7600G has **working incoming call network routing** - the phone actually rings! This is the critical difference.

EC25 has better USB audio support but incoming calls are rejected at network level, suggesting a deeper IMS/VoLTE or carrier provisioning issue.

**Recommended Path Forward:**
1. Use SIM7600G for incoming call testing
2. Answer calls via AT commands (ATA) or adapt voice bot
3. Investigate EC25 IMS registration separately
4. Consider swapping SIMs to isolate hardware vs network issues
