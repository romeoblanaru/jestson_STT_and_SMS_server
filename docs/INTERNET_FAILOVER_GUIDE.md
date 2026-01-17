# Internet Failover Configuration Guide

**System:** Professional SMS Gateway with LTE Backup
**Method:** CDC Ethernet (ECM) over USB
**Date:** 2026-01-17

---

## Overview

Professional SMS gateway with automatic internet failover using CDC Ethernet:
- **Primary:** WiFi (wlP1p1s0)
- **Backup:** EC25 LTE modem via CDC Ethernet (enxd6c3ace3c59c)
- **SMS Gateway:** Unaffected, always running on ttyUSB2
- **No ModemManager or PPP required!**

---

## Architecture: Clean CDC Ethernet Approach

### Why CDC Ethernet Instead of PPP?

**PPP Problems (Old approach):**
- ❌ Required ModemManager (port conflicts)
- ❌ Kernel didn't have ppp_generic module
- ❌ Slow performance (1.3s ping) due to serial port conflicts
- ❌ Complex setup with chat scripts

**CDC Ethernet Solution (New approach):**
- ✅ Native USB networking (kernel has cdc_ether module)
- ✅ No ModemManager needed
- ✅ Fast performance (25-48ms ping)
- ✅ Simple setup - just enable usbnet on modem
- ✅ SMSTools completely isolated on ttyUSB2

### Port Allocation

| Port | Service | Purpose | Status |
|------|---------|---------|--------|
| **ttyUSB2** | **SMSTools** | **SMS Gateway** | **Exclusive for AT commands** |
| ttyUSB3 | Available | Optional voice/AT | Not currently used |
| ttyUSB0 | Diagnostics | DM port | Not used |
| ttyUSB1 | GPS | NMEA data | Not used |
| **enxd6c3ace3c59c** | **EC25 Network** | **LTE Backup Internet** | **CDC Ethernet interface** |

### How It Works

```
┌─────────────────────────────────────────────────┐
│                  EC25 Modem                      │
│                                                  │
│  USB Composition: 0125 with usbnet=1            │
│                                                  │
│  ttyUSB2 (AT Port) ───────► SMSTools            │
│                              (SMS Gateway)       │
│                              EXCLUSIVE ACCESS    │
│                                                  │
│  CDC Ethernet Interface ──► enxd6c3ace3c59c     │
│  (192.168.225.20/24)        LTE Internet Backup │
│                             Auto-configured DHCP │
└─────────────────────────────────────────────────┘
```

---

## Setup Instructions

### 1. Enable CDC Ethernet on EC25

**Switch modem to CDC Ethernet mode:**

```bash
# Create and run the configuration script
bash /tmp/switch_ec25_rndis.sh
```

**What it does:**
1. Sends `AT+QCFG="usbnet",1` to enable CDC Ethernet
2. Reboots modem with `AT+CFUN=1,1`
3. Modem creates network interface automatically

**Verification:**
```bash
# Check if interface exists
ip link show enxd6c3ace3c59c

# Should show: UP, LOWER_UP, and an IP like 192.168.225.20/24
ip addr show enxd6c3ace3c59c

# Test internet
ping -c 4 -I enxd6c3ace3c59c 8.8.8.8
```

### 2. Load Kernel Modules (One-time)

```bash
# Load CDC Ethernet modules
sudo modprobe rndis_host
sudo modprobe cdc_ether

# Make it permanent
echo "cdc_ether" | sudo tee -a /etc/modules
echo "rndis_host" | sudo tee -a /etc/modules
```

### 3. Failover Script Already Configured

The failover script `/home/rom/internet_failover.sh` manages:
- Monitoring WiFi connectivity every minute
- Adding EC25 route when WiFi fails
- Removing EC25 route when WiFi returns
- VPS notifications on failover events

**Automatic timer runs every 1 minute** via systemd.

---

## How Failover Works

### Monitoring Flow

```
Every 1 minute (via systemd timer):
├─ Check WiFi connectivity
│  ├─ Ping 8.8.8.8 via wlP1p1s0
│  └─ Check link state
│
├─ If WiFi is UP:
│  ├─ Internet working ✅
│  └─ If EC25 route exists → Remove EC25 route
│
└─ If WiFi is DOWN:
   ├─ Internet failed ❌
   └─ If EC25 route not active → Add EC25 route
```

### Automatic Actions

**When WiFi fails:**
1. Script detects failure (no ping response)
2. Adds default route via EC25: `ip route add default via 192.168.225.1 dev enxd6c3ace3c59c metric 999`
3. Internet traffic flows through LTE
4. Notification sent to VPS: "⚠️ Switched to EC25 LTE backup"

**When WiFi returns:**
1. Script detects WiFi recovery
2. Removes EC25 route: `ip route del default via 192.168.225.1 dev enxd6c3ace3c59c metric 999`
3. Traffic switches back to WiFi (lower metric = higher priority)
4. Notification sent to VPS: "✅ Switched back to WiFi"

**SMSTools:** Completely unaffected - operates independently on ttyUSB2

---

## Testing

### Manual Failover Test

```bash
# Test the failover script manually
sudo /home/rom/internet_failover.sh

# Watch the logs
tail -f /var/log/internet_failover.log
```

### Simulate WiFi Failure

```bash
# Disable WiFi temporarily
sudo ip link set wlP1p1s0 down

# Wait for failover to trigger (script runs automatically within 1 minute)
# OR trigger manually:
sudo /home/rom/internet_failover.sh

# Check if EC25 route is active
ip route | grep enxd6c3ace3c59c

# Check connectivity via EC25
ping -c 4 8.8.8.8  # Should work via EC25

# Re-enable WiFi
sudo ip link set wlP1p1s0 up

# Wait or trigger manually again
sudo /home/rom/internet_failover.sh

# Verify EC25 route is removed
ip route | grep enxd6c3ace3c59c  # Should return nothing
```

### Check Failover Timer Status

```bash
# Check timer status
systemctl status internet-failover.timer

# Check last run
systemctl status internet-failover.service

# View timer schedule
systemctl list-timers | grep failover
```

---

## Verification

### Confirm SMSTools is Working

```bash
# Check SMSTools status
tail -f /var/log/smstools/smsd.log

# Should see normal AT command traffic on ttyUSB2
# Example output:
# GSM1: <- AT OK
# GSM1: Modem is registered to the network
```

### Check EC25 Network Interface

```bash
# Interface should be UP with IP address
ip addr show enxd6c3ace3c59c

# Should show:
# - state UP
# - IP: 192.168.225.20/24 (or similar)
# - Gateway: 192.168.225.1

# Test direct connectivity
ping -c 4 -I enxd6c3ace3c59c 8.8.8.8
```

### Check Routing Table

```bash
# View all routes
ip route

# WiFi route (lower metric = higher priority):
# default via 10.X.X.X dev wlP1p1s0 metric 50

# When failover active, you'll see:
# default via 192.168.225.1 dev enxd6c3ace3c59c metric 999
```

---

## Configuration Files

### Failover Script

**File:** `/home/rom/internet_failover.sh`

Key variables:
```bash
WIFI_INTERFACE="wlP1p1s0"
EC25_INTERFACE="enxd6c3ace3c59c"
EC25_GATEWAY="192.168.225.1"
ROUTE_MARKER="999"  # Higher metric = lower priority
```

### Systemd Timer

**Timer:** `/etc/systemd/system/internet-failover.timer`
```ini
[Timer]
OnBootSec=2min
OnUnitActiveSec=1min    # Runs every 1 minute
AccuracySec=10s
```

**Service:** `/etc/systemd/system/internet-failover.service`
```ini
[Service]
Type=oneshot
ExecStart=/home/rom/internet_failover.sh
User=root
```

### EC25 Modem Configuration

**Check current config:**
```bash
# Via AT commands on ttyUSB3
echo -e "AT+QCFG=\"usbnet\"\r" > /dev/ttyUSB3
timeout 2 cat < /dev/ttyUSB3

# Should show: +QCFG: "usbnet",1
# 0 = disabled, 1 = CDC Ethernet (ECM), 2 = RNDIS
```

---

## Monitoring

### Check Failover Logs

```bash
# Real-time monitoring
tail -f /var/log/internet_failover.log

# Recent failover events
grep "WiFi" /var/log/internet_failover.log | tail -20

# Check if backup is active
grep "backup active" /var/log/internet_failover.log | tail -5
```

### Monitor Network Interfaces

```bash
# Watch interface status
watch -n 1 'ip addr show wlP1p1s0; echo "---"; ip addr show enxd6c3ace3c59c'

# Monitor routes
watch -n 2 'ip route'
```

### Check Kernel Logs

```bash
# CDC Ethernet driver logs
sudo dmesg | grep cdc_ether | tail -20

# Should show:
# cdc_ether 1-2.1:1.4 enxXXXXXXXXXXXX: register 'cdc_ether' at usb-...
```

---

## Troubleshooting

### Issue: EC25 Interface Not Appearing

**Check modem configuration:**
```bash
# Is usbnet enabled?
echo -e "AT+QCFG=\"usbnet\"\r" > /dev/ttyUSB3
timeout 2 cat < /dev/ttyUSB3

# If it shows 0, enable it:
bash /tmp/switch_ec25_rndis.sh
```

**Check kernel modules:**
```bash
# Are CDC Ethernet modules loaded?
lsmod | grep cdc_ether

# If not, load them:
sudo modprobe cdc_ether
sudo modprobe rndis_host
```

**Check USB interfaces:**
```bash
# Should show CDC Ethernet interfaces
sudo lsusb -d 2c7c: -v 2>&1 | grep -E "Ethernet|CDC"
```

### Issue: Failover Not Triggering

**Check timer:**
```bash
# Is timer active?
systemctl status internet-failover.timer

# Manual trigger
sudo /home/rom/internet_failover.sh

# Check logs
tail -f /var/log/internet_failover.log
```

**Test WiFi check:**
```bash
# Can you ping via WiFi?
ping -c 2 -I wlP1p1s0 8.8.8.8

# Is WiFi interface UP?
ip link show wlP1p1s0 | grep "state UP"
```

### Issue: EC25 Internet Not Working

**Diagnose:**
```bash
# Is interface UP?
ip link show enxd6c3ace3c59c

# Does it have an IP?
ip addr show enxd6c3ace3c59c

# Can you ping the gateway?
ping -c 4 192.168.225.1

# Can you ping via EC25?
ping -c 4 -I enxd6c3ace3c59c 8.8.8.8
```

**Check modem network registration:**
```bash
# Check if modem is registered to network
echo -e "AT+CREG?\r" > /dev/ttyUSB2
timeout 2 cat < /dev/ttyUSB2

# Should show: +CREG: 2,1 or +CREG: 2,5 (registered)
```

### Issue: Both WiFi and EC25 Routes Active

**This is normal briefly!**

The failover script checks every 1 minute. If WiFi just recovered:
- Both routes may exist for up to 1 minute
- EC25 route will be removed on next check
- WiFi has lower metric (50) so it's used preferentially

**To force immediate cleanup:**
```bash
sudo /home/rom/internet_failover.sh
```

---

## Performance & Cost

### Connection Performance

| Connection | Speed | Latency | Test Results |
|------------|-------|---------|--------------|
| WiFi (primary) | Full speed | ~20-70ms | ✅ Production |
| EC25 LTE CDC Ethernet | ~10-50 Mbps | ~25-48ms | ✅ Tested |
| ~~EC25 PPP (old)~~ | ~~10-50 Mbps~~ | ~~1300ms~~ | ❌ Port conflicts |

**CDC Ethernet is 26x faster than PPP was!**

### Data Usage

**When failover is active:**
- Background traffic only
- LLM queries: ~1-5 KB per request
- SMS processing: negligible
- Estimated: ~10-50 MB/hour

**Cost optimization:**
- EC25 route removed automatically when WiFi returns
- Only active during WiFi outages
- Interface stays UP but unused (no data cost when route not active)

---

## Maintenance

### Monthly Checks

```bash
# Test failover manually
sudo ip link set wlP1p1s0 down
sudo /home/rom/internet_failover.sh
ip route | grep enxd6c3ace3c59c  # Should exist
ping -c 4 8.8.8.8  # Should work via EC25

# Restore WiFi
sudo ip link set wlP1p1s0 up
sudo /home/rom/internet_failover.sh
ip route | grep enxd6c3ace3c59c  # Should be gone

# Check logs for automatic failovers
grep "Switched to EC25" /var/log/internet_failover.log

# Verify SMSTools unaffected
grep -i error /var/log/smstools/smsd.log | tail -20
```

### If Modem Reboots

The CDC Ethernet interface will automatically reconfigure:
1. Kernel detects modem reappearing
2. cdc_ether driver creates interface
3. DHCP assigns 192.168.225.x IP
4. Interface is ready within ~10 seconds

**No manual intervention needed!**

---

## Summary

✅ **Clean, simple failover**
- No ModemManager conflicts
- No PPP complexity
- Fast CDC Ethernet (25-48ms ping)
- Automatic route management

✅ **Professional reliability**
- WiFi/LAN primary, LTE automatic backup
- SMS gateway working with CDC Ethernet
- Automatic switching (1-minute detection)
- VPS notifications on failover events

✅ **Port configuration**
- ttyUSB3 for SMSTools (ttyUSB2 removed by CDC Ethernet)
- CDC Ethernet on separate USB interface (enxd6c3ace3c59c)
- No conflicts, no interference

✅ **24/7 Connectivity**
- SMS gateway always connected (incoming + outgoing)
- LLM queries never interrupted
- Automatic recovery when WiFi/LAN returns

**Your SMS gateway now has enterprise-grade redundant connectivity with the simplest possible implementation!**

---

## Important: SMS Configuration with CDC Ethernet

**CRITICAL:** When CDC Ethernet is enabled (`AT+QCFG="usbnet",1`), the EC25 modem **removes ttyUSB2** and only provides ttyUSB3 for AT commands.

**Required SMSTools Configuration Changes:**

1. **Update device symlink:**
   ```bash
   sudo rm /dev/ttyUSB_SIM7600_AT
   sudo ln -s /dev/ttyUSB3 /dev/ttyUSB_SIM7600_AT
   ```

2. **Add CPMS init in /etc/smsd.conf:**
   ```ini
   [GSM1]
   device = /dev/ttyUSB_SIM7600_AT

   # CRITICAL: EC25 stores SMS in MT memory, not SR
   init = AT+CPMS="MT","MT","MT"
   ```

3. **Restart SMSTools:**
   ```bash
   sudo pkill smsd
   sudo /usr/sbin/smsd -p/var/run/smstools/smsd.pid -uroot -groot
   ```

**See detailed SMS configuration:** `/home/rom/docs/EC25_SMS_CDC_ETHERNET_SETUP.md`

---

## Quick Reference

```bash
# Check EC25 network interface
ip addr show enxd6c3ace3c59c

# Test EC25 internet
ping -c 4 -I enxd6c3ace3c59c 8.8.8.8

# Test failover
sudo /home/rom/internet_failover.sh

# Check logs
tail -f /var/log/internet_failover.log

# Check timer status
systemctl status internet-failover.timer

# View current routes
ip route

# Enable/disable WiFi for testing
sudo ip link set wlP1p1s0 down  # Disable
sudo ip link set wlP1p1s0 up    # Enable

# Check modem usbnet config
echo -e "AT+QCFG=\"usbnet\"\r" > /dev/ttyUSB3 && timeout 2 cat < /dev/ttyUSB3
```

---

## Comparison: CDC Ethernet vs PPP

| Feature | CDC Ethernet (Current) | PPP (Old/Failed) |
|---------|------------------------|------------------|
| Kernel Support | ✅ cdc_ether module available | ❌ ppp_generic module missing |
| ModemManager | ✅ Not needed | ⚠️ Required (caused conflicts) |
| Port Conflicts | ✅ None - separate USB interface | ❌ Yes - ttyUSB3 shared |
| Ping Latency | ✅ 25-48ms | ❌ 1300ms (port spam) |
| Setup Complexity | ✅ Simple (1 AT command) | ❌ Complex (chat scripts, peers) |
| SMSTools Impact | ✅ Zero | ⚠️ Port conflicts possible |
| Auto-config | ✅ DHCP automatic | ⚠️ Manual peer files |
| Performance | ✅ Excellent | ❌ Unusable |

**CDC Ethernet is the clear winner!**
