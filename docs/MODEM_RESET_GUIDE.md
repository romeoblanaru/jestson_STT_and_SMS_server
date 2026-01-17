# SIM7600G-H Modem Reset Guide

**Last Updated:** 2026-01-15

---

## Problem: Modem Crashes and Becomes Unresponsive

### Symptoms
- Modem stops responding to AT commands
- Error in logs: `write_to_modem: error 5: Input/output error`
- ttyUSB2 (AT command port) disappears from `/dev/`
- SMSD shows: `MODEM IS NOT REGISTERED, WAITING...`
- All subsequent SMS fail to send

### Root Cause
SIM7600G-H firmware bug - certain message content or format causes the modem to crash completely. The modem enters a hung state where:
- USB device is still connected (visible in `lsusb`)
- Most ttyUSB ports exist (ttyUSB0, 1, 3, 4, 5)
- **ttyUSB2 (AT port) disappears** - this is the critical failure
- Modem cannot process any commands until hardware reset

### Common Triggers
- Messages containing certain newline/carriage return combinations
- Specific character encodings in UCS-2 messages
- Multipart messages with certain content patterns
- Unknown firmware edge cases

---

## Solution: Hardware USB Reset

### Method 1: USB Authorization Reset (RECOMMENDED)

**This is the most reliable method.** It simulates physically unplugging and replugging the USB cable.

#### Command:
```bash
echo 'Romy_1202' | sudo -S sh -c 'echo 0 > /sys/bus/usb/devices/1-2.1/authorized && sleep 3 && echo 1 > /sys/bus/usb/devices/1-2.1/authorized'
```

#### How It Works:

1. **`/sys/bus/usb/devices/1-2.1/authorized`** - This is the sysfs control file for the modem's USB device

2. **`echo 0 > .../authorized`** - Writing `0` de-authorizes the device (virtually disconnects it from USB bus)

3. **`sleep 3`** - Wait 3 seconds for complete disconnect

4. **`echo 1 > .../authorized`** - Writing `1` re-authorizes it (virtually reconnects it)

This is equivalent to **physically unplugging and replugging the USB cable**, but done in software. It completely resets the modem hardware without needing physical access.

#### Automated Script:
```bash
sudo /home/rom/modem_usb_reset.sh
```

The script:
- Stops SMSD to release serial ports
- De-authorizes USB device (disconnect)
- Waits for complete reset
- Re-authorizes USB device (reconnect)
- Waits for enumeration
- Restarts SMSD
- Verifies modem is working

---

### Method 2: USB Unbind/Bind (Fallback)

Less reliable but can work in some cases.

```bash
echo "1-2.2" > /sys/bus/usb/drivers/usb/unbind
sleep 3
echo "1-2.2" > /sys/bus/usb/drivers/usb/bind
```

**Note:** This method often fails with "No such device" errors. Use Method 1 instead.

---

## Verification After Reset

### 1. Check ttyUSB2 is back:
```bash
ls -la /dev/ttyUSB2
```

Expected: `/dev/ttyUSB2` should exist

### 2. Check SMSD is communicating:
```bash
sudo tail -50 /var/log/smstools/smsd.log
```

Expected: No more "write_to_modem: error 5" messages

### 3. Check modem registration:
```bash
sudo tail -20 /var/log/smstools/smsd.log | grep -i "registered"
```

Expected: Modem should register to network within 30 seconds

---

## Finding the USB Device Path

If the modem path changes, use this to find it:

```bash
# Find modem by vendor ID (1e0e = SimTech)
for device in /sys/bus/usb/devices/*/idVendor; do
    dir=$(dirname $device)
    if grep -q "1e0e" $device 2>/dev/null; then
        echo "Found modem at: $dir"
    fi
done
```

Output example: `/sys/bus/usb/devices/1-2.1`

The path `1-2.1` is what you use in the reset command.

---

## Prevention

Unfortunately, there is **no reliable prevention** for this SIM7600G-H firmware bug. The only solutions are:

1. **Monitor and auto-reset**: Use `modem_health_monitor.sh` to detect crashes and auto-reset
2. **Message sanitization**: Avoid certain content patterns (but hard to predict all triggers)
3. **Firmware update**: Check if newer firmware is available from vendor (often doesn't fix the issue)
4. **Hardware replacement**: Consider more stable modem models if issue is frequent

---

## Log Analysis

When investigating crashes, check these logs:

```bash
# SMSD log - shows I/O errors and failed sends
sudo tail -100 /var/log/smstools/smsd.log

# System log - shows USB device issues
sudo tail -100 /var/log/syslog | grep -i "modem\|gsm\|usb"

# Find messages that were being sent when crash occurred
ls -lt /var/spool/sms/checked/ | head -20
```

The last message in the checked folder before the crash is likely the trigger.

---

## Related Files

- **Reset script**: `/home/rom/modem_usb_reset.sh`
- **Health monitor**: `/home/rom/modem_health_monitor.sh`
- **SMSD config**: `/etc/smsd.conf`
- **SMSD logs**: `/var/log/smstools/smsd.log`
- **USB device info**: `/sys/bus/usb/devices/1-2.1/`

---

## Example: Real Crash from 2026-01-15

**Time:** 18:11:37
**Trigger:** User sent SMS from mobile with newline character
**Symptom:** Modem stopped responding, ttyUSB2 disappeared
**Error:** `write_to_modem: error 5: Input/output error`
**Solution:** USB authorization reset - modem recovered in 10 seconds
**Result:** ttyUSB2 returned, modem registered, SMS queue resumed

---

**Remember:** This is a hardware-level reset. It's safe to use and will not damage the modem, but it will briefly interrupt all modem communication.
