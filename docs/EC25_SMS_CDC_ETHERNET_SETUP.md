# EC25 SMS Gateway + CDC Ethernet Configuration

**Complete Setup Guide**
**Date:** 2026-01-17
**Status:** ✅ Production Ready

---

## Overview

This guide documents the complete configuration for running both SMS Gateway and CDC Ethernet internet backup simultaneously on the EC25 modem.

**What Works:**
- ✅ SMS Gateway (incoming + outgoing)
- ✅ CDC Ethernet internet backup (25-48ms ping)
- ✅ Automatic internet failover
- ✅ No port conflicts
- ✅ No ModemManager needed

---

## Key Configuration Changes

### 1. CDC Ethernet Enabled

**Modem Configuration:**
```bash
AT+QCFG="usbnet",1
```

**What This Does:**
- Enables CDC Ethernet network interface
- Creates `enxd6c3ace3c59c` interface for LTE internet
- **Changes USB port mapping** (important!)

### 2. USB Port Mapping Changes

**Before CDC Ethernet (usbnet=0):**
```
ttyUSB0 - Diagnostic port
ttyUSB1 - GPS/NMEA port
ttyUSB2 - AT commands (SMS) ← Used by SMSTools
ttyUSB3 - AT commands (Voice)
ttyUSB4 - Audio
```

**After CDC Ethernet (usbnet=1):**
```
ttyUSB0 - Diagnostic port
ttyUSB1 - GPS/NMEA port
ttyUSB2 - REMOVED! ← This is the critical change
ttyUSB3 - AT commands (SMS/Voice)
ttyUSB4 - Audio
enxd6c3ace3c59c - CDC Ethernet (LTE internet)
```

**Impact:** ttyUSB2 disappears, SMSTools must use ttyUSB3 instead.

---

## SMSTools Configuration for EC25 + CDC Ethernet

### Required Changes in /etc/smsd.conf

#### Change 1: Storage Memory Location

**Problem:** EC25 stores incoming SMS in MT (Mobile Terminal) memory, not SR (Status Report) memory.

**Solution:** Add init command to set CPMS:

```ini
[GSM1]
device = /dev/ttyUSB_SIM7600_AT

# CRITICAL: Set SMS storage to MT (Mobile Terminal memory)
# EC25 modem stores incoming SMS in MT, not SR (Status Report)
init = AT+CPMS="MT","MT","MT"

# ... rest of configuration
```

**Without this:** Incoming SMS will be stored in modem but never processed by SMSTools.

#### Change 2: Device Symlink

**Update symlink to point to ttyUSB3:**

```bash
sudo rm /dev/ttyUSB_SIM7600_AT
sudo ln -s /dev/ttyUSB3 /dev/ttyUSB_SIM7600_AT
```

**Why:** The old symlink pointed to ttyUSB2 which no longer exists with CDC Ethernet enabled.

---

## Complete Working Configuration

### File: /etc/smsd.conf

```ini
# SMSTools3 Configuration - EC25 with CDC Ethernet

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

loglevel = 7

# Process incoming before sending
receive_before_send = no

# Disable autosplit for single SMS only
autosplit = 0

# Performance settings
delaytime = 1
delaytime_mainprocess = 1
blocktime = 1
errorsleeptime = 5

# Event handler for incoming SMS
eventhandler = /usr/local/bin/sms_handler_unicode.py

[GSM1]
device = /dev/ttyUSB_SIM7600_AT

# CRITICAL FOR EC25 + CDC ETHERNET:
# Set SMS storage to MT (Mobile Terminal memory)
# EC25 stores incoming SMS in MT, not SR
init = AT+CPMS="MT","MT","MT"

pin = ignore
incoming = yes
report = yes

# Unicode support
decode_unicode_text = yes
cs_convert = yes

report_device_details = yes

# Network and memory checking
check_network = 1
check_memory_method = 1

baudrate = 115200
pre_init = no
sending_disabled = no

# Timing and retry settings
send_delay = 2
sentsleeptime = 1
send_retries = 2

rtscts = no
memory_start = 0
phonecalls = no

# Keep serial port open (critical for USB modems)
keep_open = yes
```

---

## Verification Steps

### 1. Check Modem CDC Ethernet Configuration

```bash
# Query modem configuration
echo -e "AT+QCFG=\"usbnet\"\r" > /dev/ttyUSB3 && timeout 2 cat < /dev/ttyUSB3

# Should show: +QCFG: "usbnet",1
```

### 2. Check USB Ports

```bash
ls -la /dev/ttyUSB*

# Should show:
# ttyUSB0, ttyUSB1, ttyUSB3, ttyUSB4
# (ttyUSB2 is missing - this is correct!)
```

### 3. Check Symlink

```bash
ls -la /dev/ttyUSB_SIM7600_AT

# Should show: /dev/ttyUSB_SIM7600_AT -> /dev/ttyUSB3
```

### 4. Check CDC Ethernet Interface

```bash
ip addr show enxd6c3ace3c59c

# Should show: UP, with IP 192.168.225.x
```

### 5. Test Incoming SMS

```bash
# Watch SMSTools logs
tail -f /var/log/smstools/smsd.log

# Send SMS to gateway from external phone
# Should see: "SMS received, From: +xxxxxxxxxxxx"
```

### 6. Check SMS Storage Configuration

```bash
# Check SMSTools logs for CPMS
grep "CPMS" /var/log/smstools/smsd.log | tail -5

# Should show: +CPMS: "MT",X,255,"MT",X,255
# (MT memory, not SR)
```

---

## Troubleshooting

### Issue: Incoming SMS Not Received

**Symptoms:**
- Outgoing SMS works fine
- Incoming SMS not processed
- SMSTools logs show "No SMS received"

**Diagnosis:**
```bash
# Check which memory SMSTools is checking
grep "Used memory" /var/log/smstools/smsd.log | tail -3

# If it shows "Used memory is 0 of 5" but you sent SMS,
# the storage is configured wrong
```

**Fix:**
1. Check `/etc/smsd.conf` has `init = AT+CPMS="MT","MT","MT"`
2. Restart SMSTools: `sudo pkill smsd && sudo /usr/sbin/smsd -uroot -groot`
3. Verify in logs: should see messages being received

### Issue: SMSTools Can't Open Device

**Symptoms:**
```
write_to_modem: error 5: Input/output error
MODEM IS NOT REGISTERED
```

**Diagnosis:**
```bash
# Check if ttyUSB3 exists
ls -la /dev/ttyUSB3

# Check symlink
ls -la /dev/ttyUSB_SIM7600_AT
```

**Fix:**
```bash
# Update symlink to ttyUSB3
sudo rm /dev/ttyUSB_SIM7600_AT
sudo ln -s /dev/ttyUSB3 /dev/ttyUSB_SIM7600_AT

# Restart SMSTools
sudo pkill smsd
sudo /usr/sbin/smsd -p/var/run/smstools/smsd.pid -uroot -groot
```

### Issue: CDC Ethernet Not Working

**Symptoms:**
- No `enxd6c3ace3c59c` interface
- Internet backup not available

**Diagnosis:**
```bash
# Check modem USB configuration
echo -e "AT+QCFG=\"usbnet\"\r" > /dev/ttyUSB3 && timeout 2 cat < /dev/ttyUSB3

# Check kernel modules
lsmod | grep cdc_ether
```

**Fix:**
```bash
# Enable CDC Ethernet on modem
bash /tmp/switch_ec25_rndis.sh

# Load kernel modules
sudo modprobe cdc_ether
sudo modprobe rndis_host

# Check interface appeared
ip link show enxd6c3ace3c59c
```

---

## Migration from SIM7600 to EC25

If you're migrating from SIM7600 to EC25, here are the key differences:

### Port Mapping Differences

**SIM7600 (no CDC Ethernet):**
- Uses ttyUSB2 for AT commands
- All 5 serial ports available
- No network interface

**EC25 with CDC Ethernet:**
- Uses ttyUSB3 for AT commands (ttyUSB2 removed)
- 4 serial ports + 1 network interface
- LTE internet via CDC Ethernet

### Configuration Changes Needed

1. **Update symlink:**
   ```bash
   sudo rm /dev/ttyUSB_SIM7600_AT
   sudo ln -s /dev/ttyUSB3 /dev/ttyUSB_SIM7600_AT
   ```

2. **Add CPMS init in smsd.conf:**
   ```ini
   init = AT+CPMS="MT","MT","MT"
   ```

3. **Enable CDC Ethernet:**
   ```bash
   # Via AT command on modem
   AT+QCFG="usbnet",1
   AT+CFUN=1,1  # Reboot modem
   ```

4. **Load kernel modules:**
   ```bash
   sudo modprobe cdc_ether
   sudo modprobe rndis_host

   # Make permanent
   echo "cdc_ether" | sudo tee -a /etc/modules
   echo "rndis_host" | sudo tee -a /etc/modules
   ```

---

## Performance Metrics

### SMS Gateway

| Operation | Performance |
|-----------|-------------|
| Incoming SMS detection | ~1-3 seconds |
| Outgoing SMS send | ~2-4 seconds |
| Unicode/diacritics | ✅ Supported (Romanian, Lithuanian) |
| Multipart SMS | ✅ Working |

### CDC Ethernet Internet

| Metric | Performance |
|--------|-------------|
| Ping latency | 25-48ms |
| Speed | 10-50 Mbps (network dependent) |
| Failover detection | 1 minute (via systemd timer) |
| Failback time | 1 minute (automatic) |

---

## Production Checklist

Before deploying, verify all components:

- [ ] **CDC Ethernet enabled:** `AT+QCFG="usbnet",1`
- [ ] **Kernel modules loaded:** `lsmod | grep cdc_ether`
- [ ] **Network interface exists:** `ip link show enxd6c3ace3c59c`
- [ ] **Symlink correct:** `/dev/ttyUSB_SIM7600_AT -> /dev/ttyUSB3`
- [ ] **CPMS configured:** `grep "init = AT+CPMS" /etc/smsd.conf`
- [ ] **SMSTools running:** `ps aux | grep smsd`
- [ ] **Incoming SMS tested:** Send test SMS from external phone
- [ ] **Outgoing SMS tested:** Send via API
- [ ] **Internet failover tested:** Disconnect WiFi, verify EC25 backup
- [ ] **Failback tested:** Reconnect WiFi, verify switch back

---

## Quick Reference Commands

```bash
# Check SMS gateway status
tail -f /var/log/smstools/smsd.log

# Check incoming SMS processing
tail -f /var/log/voice_bot_ram/sms_gateway.log

# Restart SMSTools
sudo pkill smsd
sudo /usr/sbin/smsd -p/var/run/smstools/smsd.pid -uroot -groot

# Check CDC Ethernet status
ip addr show enxd6c3ace3c59c

# Test internet via EC25
ping -c 4 -I enxd6c3ace3c59c 8.8.8.8

# Check modem USB configuration
echo -e "AT+QCFG=\"usbnet\"\r" > /dev/ttyUSB3 && timeout 2 cat < /dev/ttyUSB3

# View current routes
ip route show default

# Test failover
sudo /home/rom/internet_failover.sh
```

---

## Summary

✅ **SMS Gateway Working**
- Incoming SMS: ✅ Processed from MT memory
- Outgoing SMS: ✅ Sending normally
- Port: ttyUSB3 (not ttyUSB2)

✅ **CDC Ethernet Working**
- Interface: enxd6c3ace3c59c
- Internet backup: ✅ Active
- Failover: ✅ Automatic

✅ **No Conflicts**
- SMSTools uses ttyUSB3
- CDC Ethernet uses separate USB interface
- ModemManager not needed
- Clean, simple setup

**Your SMS gateway now has professional-grade redundancy with both SMS and internet backup working seamlessly!**

---

## Related Documentation

- `/home/rom/docs/INTERNET_FAILOVER_GUIDE.md` - Complete failover system documentation
- `/home/rom/docs/EC25_MONITORING_GUIDE.md` - EC25 status monitoring
- `/home/rom/docs/EC25_USB_COMPOSITION.md` - USB composition modes

---

**Last Updated:** 2026-01-17
**Configuration Status:** ✅ Production Ready
**Tested and Verified:** SMS + CDC Ethernet working simultaneously
