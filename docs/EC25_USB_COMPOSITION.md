# EC25 USB Composition Detection

**Date:** 2026-01-16
**Feature:** USB Composition and Interface Detection for EC25 Modem

---

## ✅ USB Composition Added to EC25 Status Report

### What Was Added

New fields in "📱 Modem Hardware" section:
```
• USB Composition: 0125 (Standard Serial + Network)
• USB Interfaces: 8
```

---

## USB Composition Modes Detected

The script now identifies different EC25 USB modes:

| Product ID | Mode | Description |
|------------|------|-------------|
| **0125** | **Standard** | **Serial ports + Network (current mode)** |
| 0121 | EC25-AF | Americas variant |
| 0306 | RNDIS | Windows network mode |
| 0512 | MBIM | Mobile Broadband mode |
| 0620 | ECM | Ethernet Control Model |

---

## Current Configuration

Your EC25 is running in:

**USB Composition:** 0125 (Standard Serial + Network)

**USB Interfaces:** 8 interfaces
- Interface 00 → ttyUSB0 (DM/Diagnostics)
- Interface 01 → ttyUSB1 (NMEA/GPS)
- Interface 02 → ttyUSB2 (AT commands - SMS/Voice)
- Interface 03 → ttyUSB3 (Audio/Voice)
- Network interface → wwan0 (Data connection)

---

## Example Output

```
**📱 Modem Hardware:**
• Modem: ✅ Present
• Manufacturer: Quectel
• Model: EC25
• Variant: EC25 (Standard)
• Firmware: EC25AUXGAR08A15M1G
• IMEI: 862708045450728
• USB Composition: 0125 (Standard Serial + Network)  ← NEW
• USB Interfaces: 8  ← NEW
```

---

## Endpoint

The USB composition information is now included in all EC25 status reports sent to your VPS:

```bash
curl http://10.100.0.2:8070/monitor/ec25
```

**Returns:**
```json
{
  "status": "success",
  "action": "ec25",
  "message": "Monitoring task started in background"
}
```

**Report sent to VPS includes USB composition details.**

---

## Implementation Details

### Script Location
`/home/rom/check_ec25_status.sh`

### Detection Code
```bash
# Get product ID to determine model
PRODUCT_ID=$(lsusb -d 2c7c: | grep -oP '2c7c:\K[0-9a-f]+')

case "$PRODUCT_ID" in
    0125)
        MODEL_VARIANT="EC25 (Standard)"
        USB_COMPOSITION="0125 (Standard Serial + Network)"
        ;;
    0121)
        MODEL_VARIANT="EC25-AF (Americas)"
        USB_COMPOSITION="0121 (Standard Serial + Network)"
        ;;
    0306)
        MODEL_VARIANT="EC25 (RNDIS)"
        USB_COMPOSITION="0306 (RNDIS Mode)"
        ;;
    0512)
        MODEL_VARIANT="EC25 (MBIM)"
        USB_COMPOSITION="0512 (MBIM Mode)"
        ;;
    0620)
        MODEL_VARIANT="EC25 (ECM)"
        USB_COMPOSITION="0620 (ECM Mode)"
        ;;
    *)
        MODEL_VARIANT="EC25 (Unknown variant)"
        USB_COMPOSITION="$PRODUCT_ID (Unknown composition)"
        ;;
esac

# Get number of USB interfaces
NUM_INTERFACES=$(lsusb -d 2c7c: -v 2>/dev/null | grep "bNumInterfaces" | head -1 | awk '{print $2}')
```

---

## Testing

### Test the Status Script
```bash
# Direct execution
bash /home/rom/check_ec25_status.sh

# Via webhook
curl http://localhost:8070/monitor/ec25
```

### Expected Output
The modem hardware section should show:
- USB Composition with product ID and description
- Number of USB interfaces (8 for standard mode)

---

## Notes

- The USB composition is detected from the USB product ID
- Different compositions provide different functionality
- Standard mode (0125) provides the most complete feature set for SMS/Voice
- Interface count varies by composition mode

---

## Related Files

- **Status Script:** `/home/rom/check_ec25_status.sh`
- **Webhook Server:** `/home/rom/monitoring_webhook.py`
- **Full Guide:** `/home/rom/docs/EC25_MONITORING_GUIDE.md`
