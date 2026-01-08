# Testing Guide - Modem Manager System

**Before Production Deployment**

---

## ✅ Pre-Test Checklist

### 1. Fix Symlinks (If Needed)

**Check if symlinks exist:**
```bash
ls -la /dev/ttyUSB_EC25_*
```

**If missing, recreate:**
```bash
sudo ln -sf ttyUSB0 /dev/ttyUSB_EC25_CTRL
sudo ln -sf ttyUSB1 /dev/ttyUSB_EC25_DATA
```

**Make permanent with udev:**
```bash
sudo cp /home/rom/to_test/99-quectel-ec25-stable.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 2. Verify Modem Access

**Stop services:**
```bash
sudo systemctl stop smstools ec25-voice-bot
```

**Test AT commands:**
```bash
printf "AT\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA
```

**Should return:** `AT`, newline, `OK`

**Restart services:**
```bash
sudo systemctl start smstools ec25-voice-bot
```

---

## 🧪 Test Sequence

### Test 1: Modem Detection

```bash
/home/rom/modem_manager/lib/modem_detector.sh
```

**Expected:**
- ✓ Modem detected: EC25
- ✓ AT Commands: Responding
- Shows firmware, IMEI

**If failed:** Check USB connection, ports, permissions

---

### Test 2: Dry Run Configuration

```bash
sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh --dry-run
```

**Expected:**
- Detects EC25
- Reads IMSI correctly (15 digits, not color codes!)
- Identifies carrier (O2/giffgaff or your carrier)
- Shows APNs that would be configured
- No errors

**If IMSI read fails:**
- Symlink might be wrong
- SIM card not inserted
- Port permissions issue

---

### Test 3: Live Configuration (Current Carrier - giffgaff)

**⚠️ This will restart the modem!**

```bash
sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh
```

**Expected:**
- Stops services
- Reads IMSI: 234100...
- Carrier: O2 UK / giffgaff
- Data APN: internet
- IMS APN: ims
- VoLTE enabled
- Modem restarts (15 sec)
- Services restart

**Verify:**
```bash
# Check APN
printf "AT+CGDCONT?\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA
# Should show: +CGDCONT: 1,"IP","internet"...

# Check VoLTE
printf "AT+QCFG=\"volte\"\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA
# Should show: +QCFG: "volte",1
```

---

### Test 4: Data Connection

**Test internet connectivity:**
```bash
# Check network registration
printf "AT+CREG?\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA
# Should show: +CREG: 0,1 (registered home network)

# Check signal
printf "AT+CSQ\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA
# Should show: +CSQ: XX,99 (XX = signal strength)
```

**Test monitoring endpoint:**
```bash
curl -s http://localhost:8088/pi_send_message
```

**Should show:**
- network_mode: 4G/LTE
- signal_quality: XX/31

---

### Test 5: Voice Call

**Make a test call to verify:**
1. Voice bot answers
2. Audio works (USB Audio)
3. Call quality is good
4. Network doesn't drop to 3G (stays 4G with VoLTE)

**Check network mode during call:**
```bash
# During active call:
printf "AT+QNWINFO\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA
# Should still show LTE (not WCDMA/UMTS)
```

---

### Test 6: SMS

**Send test SMS:**
```bash
curl -X POST http://localhost:8088/send \
  -H "Content-Type: application/json" \
  -d '{"to": "+447XXXXXXXXX", "message": "Test from auto-configured modem"}'
```

**Should receive:** SMS on target number

---

### Test 7: SIM Card Swap (Lithuania Test)

**When you insert Lithuanian SIM:**

1. **Physical swap:**
   ```bash
   # Stop services
   sudo systemctl stop smstools ec25-voice-bot
   # Remove giffgaff SIM, insert Telia/Tele2/Bite SIM
   # Wait 10 seconds
   ```

2. **Auto-configure:**
   ```bash
   sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh
   ```

3. **Verify:**
   - IMSI starts with 246 (Lithuania)
   - Carrier detected correctly (Telia/Tele2/Bite)
   - APN configured correctly
   - VoLTE enabled

4. **Test voice call in Lithuania**

---

## 🔍 Verification Commands

### Check Current Configuration

```bash
# Stop services first
sudo systemctl stop smstools

# Check all PDP contexts
printf "AT+CGDCONT?\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA

# Check IMS status
printf "AT+QCFG=\"ims\"\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA

# Check VoLTE status
printf "AT+QCFG=\"volte\"\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA

# Check IMS registration
printf "AT+CIREG?\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA

# Restart services
sudo systemctl start smstools
```

---

## 🐛 Common Issues & Fixes

### Issue: Symlink doesn't exist

```bash
# Recreate manually
sudo ln -sf ttyUSB1 /dev/ttyUSB_EC25_DATA

# Or install udev rule permanently
sudo cp /home/rom/to_test/99-quectel-ec25-stable.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
```

### Issue: IMSI shows color codes

**Cause:** Terminal output capturing escape codes

**Fix:** Already handled in script, but verify:
```bash
# Manual test
printf "AT+CIMI\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA | grep -oE '[0-9]{15}'
```

### Issue: VoLTE not working after config

**Debug:**
1. Check if carrier supports VoLTE
2. Verify IMS registered: `AT+CIREG?` should show `1,1`
3. Check IMS APN: `AT+CGDCONT?` should show context 2
4. Restart modem: `AT+CFUN=1,1`

### Issue: Voice calls drop to 3G

**Possible causes:**
- VoLTE not enabled: Check `AT+QCFG="volte"`
- IMS not registered: Check `AT+CIREG?`
- Carrier IMS server issue: Check with carrier
- SIM card doesn't support VoLTE: Contact carrier

---

## 📋 Production Deployment Checklist

Before deploying in Lithuania:

- [ ] Test with UK SIM (giffgaff) - PASS
- [ ] Test modem detection
- [ ] Test auto-configuration (dry-run)
- [ ] Test auto-configuration (live)
- [ ] Verify APN configured correctly
- [ ] Verify VoLTE enabled
- [ ] Test voice calls
- [ ] Test SMS
- [ ] Test data connection
- [ ] Test with Lithuanian SIM (Telia/Tele2/Bite)
- [ ] Verify carrier auto-detected
- [ ] Test voice calls in Lithuania
- [ ] Monitor for 24 hours - stable?
- [ ] Document any issues

---

## 🚀 When SIM7600G-H Arrives

### Testing Plan

1. **Physical installation:**
   - Remove EC25
   - Install SIM7600G-H
   - Connect external audio (if needed)

2. **Auto-detection:**
   ```bash
   /home/rom/modem_manager/lib/modem_detector.sh
   ```
   - Should detect: SIM7600
   - Show: No USB Audio, 4G only

3. **Auto-configure:**
   ```bash
   sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh
   ```
   - Should work automatically
   - Different AT commands used (AT+CVOLTE)

4. **Voice testing:**
   - Update voice bot for external audio
   - Test calls
   - **VoLTE MUST work** (no 3G fallback!)

---

## 📊 Success Criteria

### Configuration Success
- ✓ Modem detected correctly
- ✓ IMSI read successfully
- ✓ Carrier identified
- ✓ APN configured (verified with AT+CGDCONT?)
- ✓ VoLTE enabled (verified with AT+QCFG="volte")
- ✓ IMS enabled (verified with AT+QCFG="ims")
- ✓ No errors in log file

### Operational Success
- ✓ Voice calls work
- ✓ Audio quality good
- ✓ SMS works
- ✓ Data connection works
- ✓ Network stays on 4G during calls (VoLTE)
- ✓ Services restart automatically
- ✓ System stable for 24+ hours

---

**Ready for Production!** 🎉
