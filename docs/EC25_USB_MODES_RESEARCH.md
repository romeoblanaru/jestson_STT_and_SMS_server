# EC25 USB Modes Research & Findings

**Date:** 2026-01-17
**Investigation:** EC25 USB Composition and usbnet Modes
**Status:** ✅ RESOLVED - Mobile backup working correctly

---

## Summary

After investigation and online research, we confirmed that **EC25 with USB PID 0125 requires Mode 1 (ECM)** for CDC Ethernet, NOT Mode 2 as originally configured.

**Result:** Mobile internet backup is working correctly with current configuration.

---

## AT+QCFG="usbnet" Modes

Based on Quectel documentation and community forums:

| Mode | Name | Description | USB PID | Use Case |
|------|------|-------------|---------|----------|
| **0** | QMI/RMNET | Default mode, QMI interface | 0125 | Default, QMI tools required |
| **1** | **ECM** | **CDC Ethernet (Linux native)** | **0125** | **✅ Correct for our setup** |
| **2** | MBIM | Mobile Broadband Interface | 0125 | Windows 8+ |
| **3** | RNDIS | Remote NDIS (Windows) | 0306 | Windows XP-7 |

---

## Our Configuration

### Hardware
- **Modem:** Quectel EC25-AUX
- **USB PID:** 0125 (Standard Serial + Network)
- **Firmware:** EC25AUXGAR08A15M1G

### Current Settings (Working)
```bash
AT+QCFG="usbnet"
+QCFG: "usbnet",1
OK
```

### What's Working
- ✅ CDC Ethernet interface: `enxc25b2e9d5e17`
- ✅ Mobile IP: `192.168.225.25/24`
- ✅ Gateway: `192.168.225.1`
- ✅ Internet: 43ms ping via LTE
- ✅ Failover route: metric 999 (backup mode)
- ✅ SMS Gateway: Unaffected on ttyUSB2

---

## What Was Wrong

### Original Configurator Script (INCORRECT)
```bash
# WRONG: This was trying to set mode 2 (MBIM)
AT+QCFG="usbnet",2,1
ERROR  # EC25 with PID 0125 doesn't support mode 2 properly
```

**Problem:**
- Comment incorrectly stated "Mode 2 = RNDIS/CDC Ethernet"
- Actually Mode 2 = MBIM (not RNDIS)
- RNDIS is Mode 3
- For CDC Ethernet on PID 0125, need Mode 1 (ECM)

### Fixed Configurator Script (CORRECT)
```bash
# CORRECT: Mode 1 for ECM/CDC Ethernet
AT+QCFG="usbnet",1,1
OK
```

---

## Technical Details

### Mode 1 (ECM) Characteristics
- Uses CDC Ethernet drivers (cdc_ether kernel module)
- Creates network interface automatically (enx*)
- DHCP assigns IP from modem (192.168.225.x/24)
- No ModemManager or PPP required
- SMS/AT ports remain available (ttyUSB2, ttyUSB3)
- Native Linux support, no additional drivers needed

### Interface Detection
```bash
# Interface appears as:
ip link show
110: enxc25b2e9d5e17: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500

# IP assigned by modem's internal DHCP:
ip addr show enxc25b2e9d5e17
inet 192.168.225.25/24 brd 192.168.225.255 scope global dynamic
```

### Failover System
```bash
# Passive failover mode (automatic Linux routing)
default via 192.168.0.1 dev wlP1p1s0 metric 600       # WiFi - PRIMARY
default via 192.168.225.1 dev enxc25b2e9d5e17 metric 999  # LTE - BACKUP

# Linux automatically uses LTE when WiFi fails
# No manual intervention needed
```

---

## Research Sources

1. **Quectel Forums - EC25-E usbnet support:**
   [EC25-E: AT+QCFG="usbnet" officially supported](https://forums.quectel.com/t/ec25-e-at-qcfg-usbnet-officially-supported-as-in-ec200t/15755)

2. **Quectel Forums - ECM mode help:**
   [Help with ECM mode and usbnet, with EG25-G](https://forums.quectel.com/t/help-with-ecm-mode-and-usbnet-with-eg25-g/34641)

3. **Quectel Official Documentation:**
   [LTE/5G Linux USB Driver User Guide](https://sixfab.com/wp-content/uploads/2020/12/Quectel_LTE5G_Linux_USB_Driver_User_Guide_V2.0.pdf)

4. **Sixfab ECM Mode Guide:**
   [Cellular Internet Connection in ECM Mode](https://docs.sixfab.com/page/cellular-internet-connection-in-ecm-mode)

5. **OpenWrt Forum Discussion:**
   [Quectel EC25 4G modem QMI mode](https://forum.openwrt.org/t/quectel-ec25-4g-modem-qmi-mode/70092)

---

## Commands Used

### Query Current Mode
```bash
echo -e 'AT+QCFG="usbnet"\r' > /dev/ttyUSB2
# Response: +QCFG: "usbnet",1
```

### Set to ECM Mode (Persistent)
```bash
echo -e 'AT+QCFG="usbnet",1,1\r' > /dev/ttyUSB2
#                      ↑  ↑
#                      │  └─ Save to NV memory (persistent)
#                      └──── Mode 1 (ECM)
```

### Soft Reset (Apply Changes)
```bash
echo -e 'AT+CFUN=1,1\r' > /dev/ttyUSB2
# Modem resets and applies new USB configuration
```

### Verify CDC Ethernet Interface
```bash
# Check interface exists
ip link show | grep enx

# Check IP assignment
ip addr show enxc25b2e9d5e17

# Test internet via LTE
ping -c 4 -I enxc25b2e9d5e17 8.8.8.8
```

---

## Files Updated

### 1. `/home/rom/ec25_smart_configurator.sh`
**Changed:**
- Line 166: `AT+QCFG="usbnet",2,1` → `AT+QCFG="usbnet",1,1`
- Updated comments to reflect correct modes
- Added persistent save flag (`,1`)

**Function:** `configure_usb_composition()`

### 2. Related Scripts
- ✅ `/home/rom/internet_failover.sh` - No changes needed (works with any interface)
- ✅ `/home/rom/check_ec25_status.sh` - Updated to use manual stop/start for SMSD
- ✅ `/home/rom/smsd_manual_stop.sh` - Added logging to sms_watch
- ✅ `/home/rom/smsd_manual_start.sh` - Added logging to sms_watch

---

## Conclusion

✅ **Mode 1 (ECM) is the correct setting for EC25 USB PID 0125**
✅ **Mobile backup is working perfectly**
✅ **Configuration is now persistent (saved to NV memory)**
✅ **Configurator script corrected and documented**

No further changes needed - system is working as designed!

---

## Notes

- **Do NOT use Mode 0** - Requires QMI tools (qmi_wwan, libqmi)
- **Do NOT use Mode 2** - MBIM mode (Windows 8+, not needed for Linux)
- **Do NOT use Mode 3** - RNDIS mode (changes USB PID to 0306, Windows-specific)
- **Use Mode 1** - ECM mode (native Linux CDC Ethernet, perfect for our setup)

The original confusion was that Mode 2 was labeled as "RNDIS" in comments, but it's actually MBIM. RNDIS is Mode 3 and changes the USB PID to 0306.
