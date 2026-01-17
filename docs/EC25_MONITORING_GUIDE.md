# EC25 Modem Monitoring Guide

**Last Updated:** 2026-01-16
**System:** Jetson Orin Nano - Multi-Modem SMS/Voice Gateway

---

## Table of Contents

1. [Overview](#overview)
2. [Monitoring Endpoints](#monitoring-endpoints)
3. [EC25 vs SIM7600 Differences](#ec25-vs-sim7600-differences)
4. [USB Composition Modes](#usb-composition-modes)
5. [AT Commands Reference](#at-commands-reference)
6. [Status Report Format](#status-report-format)
7. [Scripts and Configuration](#scripts-and-configuration)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The system supports comprehensive monitoring for both EC25 (Quectel) and SIM7600 (SimTech) modems with automatic detection and modem-specific status reporting.

### Key Features

- ✅ Auto-detection of modem type (EC25, SIM7600, Samsung)
- ✅ Modem-specific AT command support
- ✅ USB composition detection
- ✅ Async-only endpoints (no timeouts)
- ✅ Reports sent to VPS via messaging system
- ✅ Comprehensive hardware, network, and service status

---

## Monitoring Endpoints

### Base URL
```
http://10.100.0.2:8070
```

### Available Endpoints

| Endpoint | Modem | Description |
|----------|-------|-------------|
| `/monitor/ec25` | EC25 | Comprehensive EC25 status (async) |
| `/monitor/sim7600` | SIM7600 | Comprehensive SIM7600 status (async) |
| `/monitor/help` | All | List all available endpoints |

### Usage Examples

**Trigger EC25 Status Report:**
```bash
curl http://10.100.0.2:8070/monitor/ec25
```

**Response (immediate):**
```json
{
  "status": "success",
  "action": "ec25",
  "message": "Monitoring task started in background"
}
```

**Report arrives at VPS in 30-60 seconds via messaging system**

---

## EC25 vs SIM7600 Differences

### Hardware Detection

| Modem | USB Vendor ID | Product IDs | Detection Method |
|-------|---------------|-------------|------------------|
| **EC25** | 2c7c | 0125, 0121, 0306, 0512, 0620 | `lsusb \| grep "2c7c:"` |
| **SIM7600** | 1e0e | 9001, 9011, 1025 | `lsusb \| grep "1e0e:"` |

### AT Port Mapping

| Modem | AT Port | Interface | Usage |
|-------|---------|-----------|-------|
| **EC25** | /dev/ttyUSB2 | Interface 02 | SMS & AT commands |
| **SIM7600** | /dev/ttyUSB2 | Interface 02 | SMS & AT commands |

**Note:** Both modems use ttyUSB2 for AT commands (Interface 02)

### AT Command Differences

| Function | SIM7600 Command | EC25 Command |
|----------|----------------|--------------|
| Model Info | AT+CGMM | AT+CGMM (same) |
| IMEI | AT+CGSN | AT+CGSN (same) |
| Signal Quality | AT+CSQ | AT+CSQ (same) |
| **Extended Signal** | AT+CSQ | **AT+QCSQ** |
| **Network Info** | **AT+CPSI?** | **AT+QNWINFO** |
| **VoLTE Status** | **AT+CEVOLTE?** | **AT+QCFG="ims"** |
| **Network Mode** | **AT+CNMP?** | **AT+QCFG="nwscanmode"** |
| **Operator Name** | AT+COPS? | **AT+QSPN** |
| **SIM ICCID** | AT+CCID | **AT+QCCID** |

**Bold** = Vendor-specific commands

---

## USB Composition Modes

### EC25 USB Compositions

| Product ID | Mode | Description | Use Case |
|------------|------|-------------|----------|
| **0125** | **Standard** | **Serial + Network** | **SMS/Voice + Data (default)** |
| 0121 | EC25-AF | Americas variant | Regional variant |
| 0306 | RNDIS | Windows network | Windows compatibility |
| 0512 | MBIM | Mobile Broadband | Modern Windows/Linux |
| 0620 | ECM | Ethernet Control | Linux/Mac network |

### Current System Configuration

```
USB Composition: 0125 (Standard Serial + Network)
USB Interfaces: 8
```

**Interface Mapping for Product ID 0125:**
- Interface 00 → ttyUSB0 (DM/Diagnostics)
- Interface 01 → ttyUSB1 (NMEA/GPS)
- Interface 02 → ttyUSB2 (AT commands - SMS/Voice)
- Interface 03 → ttyUSB3 (Audio/Voice)
- Network interface → wwan0 (data connection)

### SIM7600 USB Compositions

| Product ID | Mode | Description |
|------------|------|-------------|
| 9001 | Voice Mode | Optimized for voice calls |
| 9011 | Fast Data | Optimized for data transfer |
| 1025 | QMI Mode | Qualcomm MSM Interface |

---

## AT Commands Reference

### EC25-Specific Commands

#### Extended Signal Quality
```bash
AT+QCSQ
# Response: +QCSQ: "LTE",-82,-116,100,-17
# Format: Technology, RSSI, RSRP, SINR, RSRQ
```

#### Network Information
```bash
AT+QNWINFO
# Response: +QNWINFO: "FDD LTE","23410","LTE BAND 3",1226
# Format: Technology, Operator, Band, Channel
```

#### VoLTE/IMS Configuration
```bash
AT+QCFG="ims"
# Response: +QCFG: "ims",1
# 0 = Disabled, 1 = Enabled
```

#### Network Scan Mode
```bash
AT+QCFG="nwscanmode"
# Response: +QCFG: "nwscanmode",0
# 0 = Auto, 1 = GSM only, 2 = WCDMA only, 3 = LTE only
```

#### Operator Name
```bash
AT+QSPN
# Response: +QSPN: "O2 - UK","O2","","0","23410"
# Format: Full name, Short name, SPN, Display format, MCC+MNC
```

#### SIM ICCID
```bash
AT+QCCID
# Response: +QCCID: 8944110069265987985F
```

### Standard AT Commands (Both Modems)

#### Basic Commands
```bash
AT              # Test modem responsiveness
ATI             # Modem identification
AT+CGMI         # Manufacturer
AT+CGMM         # Model
AT+CGMR         # Firmware version
AT+CGSN         # IMEI
AT+CIMI         # IMSI
```

#### Network Commands
```bash
AT+CSQ          # Signal quality (0-31, 99=unknown)
AT+CPIN?        # SIM PIN status
AT+CREG?        # Network registration (CS)
AT+CEREG?       # Network registration (EPS/LTE)
AT+COPS?        # Operator selection
```

#### Data/APN Commands
```bash
AT+CGDCONT?     # PDP context definition (APN config)
AT+CGACT?       # PDP context activation status
```

---

## Status Report Format

### EC25 Comprehensive Status Report

```
🟧 EC25 Comprehensive Status Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📱 Modem Hardware:
• Modem: ✅ Present
• Manufacturer: Quectel
• Model: EC25
• Variant: EC25 (Standard)
• Firmware: EC25AUXGAR08A15M1G
• IMEI: 862708045450728
• USB Composition: 0125 (Standard Serial + Network)
• USB Interfaces: 8

📶 Network Status:
• SIM Card: ✅ Ready
• ICCID: 8944110069265987985F
• IMSI: 234100406701824
• Operator: O2 - UK
• Network Registration: ✅ Registered
• Signal Strength: 16/31
• Signal Extended: LTE -82dBm

📡 Network Mode:
• Network Info: FDD LTE - 23410 - LTE BAND 3
• Mode Preference: Auto (LTE/WCDMA/GSM)
• VoLTE Capability: ✅ LTE (VoLTE capable)
• EPS (LTE) Registration: ✅ Registered (home network)

🌐 Data & VoLTE:
• PDP Context: ✅ Active
• Data APN: internet (IP)
• IMS/VoLTE: ✅ Enabled

🔌 Connectivity:
• AT Port: ✅ (/dev/ttyUSB2)
• Internet: ✅ (Ping: 11.0ms)
• wwan0: ❌ Down (No IP)

⚙️ Services:
• SMSTools: ✅ Running
• Voice Bot: ❌ Stopped

🎙️ STT Service:
• Server Status: ✅ Running
• Model: Parakeet-TDT-0.6B-v3
• Health: healthy

🔗 VPS SMS Server:
• Connectivity: ✅ OK
• Response: responding
```

---

## Scripts and Configuration

### Main Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| `check_ec25_status.sh` | EC25 status check | `/home/rom/check_ec25_status.sh` |
| `check_sim7600_status.sh` | SIM7600 status check | `/home/rom/check_sim7600_status.sh` |
| `monitoring_webhook.py` | HTTP webhook server | `/home/rom/monitoring_webhook.py` |
| `modem_crash_recovery.sh` | Auto-recovery on crash | `/home/rom/modem_crash_recovery.sh` |
| `configure_smsd_for_modem.sh` | Auto-configure SMSD | `/home/rom/configure_smsd_for_modem.sh` |

### Service Configuration

**Monitoring Webhook Service:**
```bash
systemctl status monitoring-webhook
# Listens on: 0.0.0.0:8070
# Service file: /etc/systemd/system/monitoring-webhook.service
```

**SMSD Configuration:**
```bash
# EC25 settings
check_memory_method = 1  # Standard CPMS
sentsleeptime = 1
delaytime = 1

# SIM7600 settings
check_memory_method = 5  # SIM600 compatible
sentsleeptime = 2
delaytime = 2
```

### Script Workflow

1. **VPS triggers endpoint:** `curl http://10.100.0.2:8070/monitor/ec25`
2. **Webhook returns immediately:** JSON response (no timeout)
3. **Script runs in background:**
   - Stops SMSD temporarily
   - Queries modem via AT commands
   - Collects comprehensive status
   - Restarts SMSD
4. **Report sent to VPS:** via `pi_send_message.sh`
5. **VPS receives notification:** ~30-60 seconds after trigger

---

## Troubleshooting

### Common Issues

#### 1. Modem Not Detected

**Symptoms:**
```
🔴 EC25 Status: Modem not detected via USB
```

**Check:**
```bash
lsusb | grep 2c7c  # EC25
lsusb | grep 1e0e  # SIM7600
```

**Fix:**
- Check USB connection
- Try different USB port
- Check if modem is powered

#### 2. AT Port Not Responding

**Symptoms:**
```
• AT Port: ❌ (/dev/ttyUSB2)
```

**Check:**
```bash
ls -la /dev/ttyUSB*
systemctl status smstools
```

**Fix:**
```bash
# Restart SMSD
sudo systemctl restart smstools

# Or run status check (auto-stops/starts SMSD)
bash /home/rom/check_ec25_status.sh
```

#### 3. Mixed/Corrupted AT Responses

**Symptoms:**
- Manufacturer shows AT command echoes
- Variables contain AT responses

**Cause:** SMSD is using the serial port simultaneously

**Fix:** Script automatically handles this by stopping SMSD first. If issue persists:
```bash
# Manually stop SMSD before testing
sudo systemctl stop smstools
bash /home/rom/check_ec25_status.sh
sudo systemctl start smstools
```

#### 4. Webhook Not Responding

**Check:**
```bash
systemctl status monitoring-webhook
netstat -tlnp | grep 8070
```

**Fix:**
```bash
sudo systemctl restart monitoring-webhook
```

#### 5. Network Not Registered

**Symptoms:**
```
• Network Registration: ❌ Not Registered
```

**Check:**
```bash
# Check SIM card status
echo -e "AT+CPIN?\r" > /dev/ttyUSB2

# Check signal
echo -e "AT+CSQ\r" > /dev/ttyUSB2
```

**Fix:**
- Verify SIM card is inserted
- Check SIM is activated
- Check network coverage
- Wait for network search to complete

---

## Integration with VPS

### VPS Monitoring Setup

**Cron job example:**
```bash
# Check EC25 status every hour
0 * * * * curl -s http://10.100.0.2:8070/monitor/ec25

# Check both modems daily
0 8 * * * curl -s http://10.100.0.2:8070/monitor/ec25
0 9 * * * curl -s http://10.100.0.2:8070/monitor/sim7600
```

### Notification Flow

```
VPS → HTTP Request → Jetson:8070
                          ↓
                    Webhook receives
                          ↓
                    Background script
                          ↓
                    AT command queries
                          ↓
                    Format report
                          ↓
                    pi_send_message.sh
                          ↓
VPS ← HTTP POST ← http://10.100.0.1:5000/api/send
```

---

## Quick Reference

### Test EC25 Status
```bash
# Direct script execution
bash /home/rom/check_ec25_status.sh

# Via webhook (local)
curl http://localhost:8070/monitor/ec25

# Via webhook (from VPS)
curl http://10.100.0.2:8070/monitor/ec25
```

### Check Modem Type
```bash
# Auto-detect current modem
bash /home/rom/modem_crash_recovery.sh
# (Check logs: /var/log/modem_crash_recovery.log)

# Or manually
lsusb | grep -E "2c7c|1e0e|04e8"
```

### View Webhook Help
```bash
curl http://10.100.0.2:8070/monitor/help | jq .
```

### Available Endpoints Summary
```
/monitor/ec25       - EC25 comprehensive status
/monitor/sim7600    - SIM7600 comprehensive status
/monitor/vpn        - VPN connectivity
/monitor/system     - System health
/monitor/network    - Network connectivity
/monitor/tts        - TTS/Voice status
/monitor/help       - This help
```

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-16 | 1.0 | Initial EC25 monitoring implementation |
| 2026-01-16 | 1.1 | Added USB composition detection |
| 2026-01-16 | 1.2 | Removed sync endpoints (async only) |

---

## Related Documentation

- [Modem Reset Guide](MODEM_RESET_GUIDE.md)
- [SMS Gateway Configuration](../README.md)
- [VoLTE Setup Guide](VOLTE_SETUP_GUIDE.md)

---

**For questions or issues, check system logs:**
```bash
tail -f /var/log/modem_crash_recovery.log
tail -f /var/log/smstools/smsd.log
journalctl -u monitoring-webhook -f
```
