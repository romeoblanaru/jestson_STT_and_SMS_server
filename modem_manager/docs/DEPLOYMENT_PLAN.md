# Modem Deployment Plan

**Date:** October 11, 2025
**Status:** Production Deployment

---

## Current Decision

**Primary Modem:** SIM7600G-H (Vodafone UK)
**Backup Modem:** EC25-AUX (giffgaff/O2 UK) - Spare, not active

---

## Why SIM7600 as Primary?

### ✅ Advantages:
1. **Incoming calls WORK** - Network accepts calls, phone rings
2. **Call answering works** - Voice bot answers after 2 rings
3. **Vodafone network stable** - Good signal (54%)
4. **Audio solution exists** - Serial port PCM on /dev/ttyUSB4
5. **Ready for production** - Just needs audio recording implementation

### ⚠️ Limitations:
1. **No USB Audio Class** - Uses serial port instead (solved)
2. **Requires custom audio code** - Can't use standard arecord (solvable)

---

## Why EC25 as Spare?

### ✅ Advantages:
1. **USB Audio Class works** - hw:EC25AUX device available
2. **Standard ALSA support** - Easy to use arecord/aplay
3. **Full configuration documented** - VoLTE/IMS enabled
4. **European carrier database** - 40+ carriers pre-configured

### ❌ Critical Issue:
1. **Incoming calls FAIL** - Network rejects before ringing
   - Operator message: "Cannot connect your call"
   - Possible causes:
     - giffgaff SIM might be data-only
     - IMS registration not working
     - Carrier provisioning issue
     - VoLTE not fully activated

### Status: NOT WORKING FOR PRODUCTION
- Keep configured and documented
- Don't try to fix now
- May investigate later or swap SIM cards

---

## Production Setup

### Primary Configuration: SIM7600G-H

**Hardware:**
- Model: SIMCom SIM7600G-H
- Firmware: SIM7600G_V2.0.2
- IMEI: 862636055891897
- USB PID: 9011 (with audio support)

**SIM Card:**
- Carrier: Vodafone UK
- IMSI: 234159593176535
- Network: LTE (4G)

**Ports:**
- /dev/ttyUSB2 - AT Commands (symlink: /dev/ttyUSB_EC25_DATA for compatibility)
- /dev/ttyUSB4 - PCM Audio (8kHz, 16-bit, Mono)

**Services:**
- smstools: Uses /dev/ttyUSB2
- voice-bot: Modified to support serial port audio

**Audio Method:**
- Command: AT+CPCMREG=1
- Device: /dev/ttyUSB4 (serial port)
- Format: Raw PCM (8000Hz, 16-bit signed, mono)
- Recording: Python serial read + VAD
- Conversion: Sox for WAV export

---

## Backup Configuration: EC25-AUX

**Hardware:**
- Model: Quectel EC25-AUX
- Firmware: EC25AUXGAR08A15M1G (A0.301)
- IMEI: 862708045450728
- USB PID: 0125

**SIM Card:**
- Carrier: giffgaff (O2 UK)
- IMSI: 234100406701824
- Network: LTE (4G)

**Ports:**
- /dev/ttyUSB2 - AT Commands (when EC25 plugged in)
- hw:EC25AUX - USB Audio Class device

**Configuration Saved:**
- USB Audio: Enabled (AT+QPCMV=1,2 + AT&W)
- VoLTE/IMS: Enabled (AT+QCFG="ims",1 + AT&W)
- IMS APN: "ims" configured

**Status:**
- ✅ Fully configured
- ✅ Documented in `/home/rom/modem_manager/docs/EC25-AUX_FINAL_CONFIG.md`
- ❌ Incoming calls fail (network level issue)
- 🔄 Kept as spare for future troubleshooting

---

## How to Switch Modems (Future)

### Switch to SIM7600 (Current):
1. Unplug EC25
2. Plug in SIM7600
3. Services use /dev/ttyUSB2 automatically (symlink still works)
4. Voice bot uses serial port audio (/dev/ttyUSB4)

### Switch to EC25 (If needed):
1. Unplug SIM7600
2. Plug in EC25
3. Services use /dev/ttyUSB2 automatically
4. Voice bot uses USB Audio Class (hw:EC25AUX)
5. **Note:** Incoming calls won't work until carrier issue resolved

### Run Initialization on Either Modem:
```bash
sudo /home/rom/modem_manager/scripts/initialize_modem.sh
```
- Auto-detects EC25 or SIM7600
- Checks/enables audio
- Checks/enables VoLTE
- Restarts modem
- Sends notification

---

## Next Steps (SIM7600 Production)

### Immediate (Required):
1. ✅ Document audio solution
2. **Modify voice bot** - Add SIM7600 serial audio support
3. **Test audio recording** - Verify PCM capture works
4. **Test VAD integration** - Silence detection on serial audio
5. **Production testing** - Full call flow with recording

### Future (Optional):
1. **Swap SIM cards** - Try giffgaff in SIM7600, Vodafone in EC25
   - Determine if issue is SIM/carrier or modem hardware
2. **Contact giffgaff** - Check if SIM is data-only or voice-enabled
3. **Investigate EC25 IMS** - Check IMS registration status
4. **Try different EC25 APN** - Some carriers need specific IMS domains

---

## Modem Comparison Summary

| Feature | EC25-AUX | SIM7600G-H |
|---------|----------|------------|
| **Incoming Calls** | ❌ Network rejects | ✅ Rings and answers |
| **Outgoing Calls** | ✅ Works | ✅ Works |
| **USB Audio** | ✅ hw:EC25AUX (ALSA) | ❌ No device (Serial PCM) |
| **Audio Recording** | ✅ Easy (arecord) | ⚠️ Custom (serial read) |
| **VoLTE/IMS** | ✅ Configurable | ⚠️ Carrier-dependent |
| **Production Ready** | ❌ No (call issues) | ✅ Yes (needs audio impl) |
| **Deployment Status** | 🔄 Backup/Spare | ✅ Primary |

---

## Files and Documentation

### Configuration Files:
- `/home/rom/modem_manager/scripts/initialize_modem.sh` - Auto-init both modems
- `/etc/udev/rules.d/99-quectel-ec25-stable.rules` - EC25 port rules
- `/etc/udev/rules.d/99-simcom-sim7600-stable.rules` - SIM7600 port rules (TODO)

### Documentation:
- `/home/rom/modem_manager/docs/EC25-AUX_FINAL_CONFIG.md` - EC25 full config
- `/home/rom/modem_manager/docs/SIM7600_AUDIO_SOLUTION.md` - SIM7600 audio guide ⭐
- `/home/rom/modem_manager/docs/MODEM_COMPARISON.md` - Test results
- `/home/rom/modem_manager/docs/DEPLOYMENT_PLAN.md` - This file

### Scripts:
- `/home/rom/ec25_voice_bot_v3.py` - Voice bot (needs SIM7600 audio support)
- `/etc/smsd.conf` - SMS daemon config
- `/home/rom/pi_send_message.sh` - Monitoring script

---

## Decision Log

**October 11, 2025:**
- ✅ Tested both modems
- ✅ EC25 incoming calls fail (network rejects)
- ✅ SIM7600 incoming calls work (rings, answers)
- ✅ Researched SIM7600 audio (serial port PCM)
- **Decision:** Use SIM7600 as primary, keep EC25 as spare
- **Rationale:** Working incoming calls > USB Audio convenience

---

## Support Notes

### If Incoming Calls Fail on SIM7600:
1. Check network registration: `AT+CREG?` should show `0,1`
2. Check operator: `AT+COPS?`
3. Check signal: `AT+CSQ` (>10 is good)
4. Verify phone number with carrier
5. Check voice services enabled on SIM

### If Audio Recording Fails on SIM7600:
1. Verify ttyUSB4 exists: `ls -l /dev/ttyUSB4`
2. Enable PCM after answer: `AT+CPCMREG=1`
3. Check interface: `cat /sys/class/tty/ttyUSB4/device/../bInterfaceNumber` (should be 06)
4. Test raw read: `timeout 5 cat /dev/ttyUSB4 > test.raw`
5. Convert and listen: `sox -r 8000 -e signed-integer -b 16 -c 1 test.raw test.wav && aplay test.wav`

### If Need to Revert to EC25:
1. Unplug SIM7600, plug EC25
2. Services will auto-use /dev/ttyUSB2
3. Modify voice bot to use hw:EC25AUX
4. **Remember:** Incoming calls still won't work (unsolved)

---

**Deployment Status:** Ready for SIM7600 audio implementation
**Blocker:** Need to code serial port audio in voice bot
**Timeline:** Complete audio implementation, then production ready
