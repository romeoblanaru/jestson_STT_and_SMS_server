# Modem Manager - Professional Multi-Modem System

**Version:** 1.0.0
**Date:** 2025-10-11
**Author:** Claude Code + Romeo

---

## 📋 Overview

Professional modem management system designed for **voice bot deployment across Europe**. Supports multiple modems, automatic carrier detection, and VoLTE/IMS configuration.

### Key Features

✅ **Multi-Modem Support**
- Quectel EC25-AUX (3G/2G fallback, USB Audio)
- SIMCom SIM7600G-H (4G only, more reliable)
- Easy switching between modems

✅ **Multi-Country Support**
- 40+ European carriers pre-configured
- Lithuania (Telia, Tele2, Bite)
- UK (O2/giffgaff, Vodafone, EE, Three)
- Germany, Poland, Latvia, Estonia, France, Spain, Italy, Netherlands

✅ **Automatic Configuration**
- Reads SIM card IMSI
- Detects carrier automatically
- Configures correct APN
- Enables VoLTE/IMS for future-proofing

✅ **Future-Proof**
- VoLTE ready (for 2G/3G shutdown)
- IMS configuration included
- Works after 2G/3G networks are decommissioned

---

## 📁 Directory Structure

```
/home/rom/modem_manager/
├── lib/                    # Libraries
│   └── modem_detector.sh   # Modem detection library
├── config/                 # Configuration files
│   └── carriers.json       # European carrier database
├── scripts/                # Executable scripts
│   └── auto_configure_modem.sh  # Main auto-config script
├── logs/                   # Log files
│   └── auto_config_*.log   # Configuration logs
└── docs/                   # Documentation
    └── README.md           # This file
```

---

## 🚀 Quick Start

### 1. Detect Modem

```bash
/home/rom/modem_manager/lib/modem_detector.sh
```

**Output:**
```
╔══════════════════════════════════════════════════════════════╗
║           Modem Detection & Status Report                   ║
╚══════════════════════════════════════════════════════════════╝

✓ Modem detected: EC25

  Model:         Quectel EC25-AUX
  USB ID:        2c7c:0125
  VoLTE:         ✓ Supported
  3G Fallback:   ✓ Available
  USB Audio:     ✓ hw:EC25AUX

  AT Port:       /dev/ttyUSB_EC25_DATA
  AT Commands:   ✓ Responding
  Firmware:      EC25AUXGAR08A15M1G
  IMEI:          862708045450728
```

### 2. Auto-Configure (Dry Run First)

```bash
sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh --dry-run
```

This will:
- Detect modem type
- Read SIM card IMSI
- Identify carrier
- Show what would be configured (without making changes)

### 3. Auto-Configure (Live)

```bash
sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh
```

This will:
- Stop services (smstools, ec25-voice-bot)
- Configure data APN
- Configure IMS APN
- Enable VoLTE/IMS
- Restart modem
- Verify configuration
- Restart services

**Note:** Modem will restart (15 second wait), services will be automatically restarted.

---

## 📖 Usage Guide

### Auto-Configuration Options

```bash
sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh [OPTIONS]

OPTIONS:
    -h, --help          Show help message
    -d, --dry-run       Simulate without making changes
    -f, --force         Force configuration even if already configured
    --no-volte          Skip VoLTE/IMS configuration
    --no-test           Skip connection testing
    --no-restart        Don't restart services after configuration
```

### Examples

**Test what would be configured:**
```bash
sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh --dry-run
```

**Configure APN only (skip VoLTE):**
```bash
sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh --no-volte
```

**Full automatic configuration:**
```bash
sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh
```

---

## 🗺️ Supported Carriers

### Lithuania (MCC 246)
- **Telia** (MNC 02): `internet.lt.telia.lt`
- **Tele2** (MNC 01): `m2m.tele2.lt`
- **Bite** (MNC 03): `data.bite.lt`

### United Kingdom (MCC 234)
- **O2 / giffgaff** (MNC 10): `internet`
- **Vodafone** (MNC 15): `pp.vodafone.co.uk`
- **EE** (MNC 30): `everywhere`
- **Three** (MNC 20): `three.co.uk`

### Germany (MCC 262)
- **Deutsche Telekom** (MNC 01): `internet.t-mobile`
- **Vodafone** (MNC 02): `web.vodafone.de`
- **O2** (MNC 03): `internet`

### Poland (MCC 260)
- **T-Mobile** (MNC 02): `internet`
- **Plus** (MNC 01): `internet`
- **Orange** (MNC 03): `internet`
- **Play** (MNC 06): `internet`

### Latvia (MCC 247)
- **LMT** (MNC 01): `internet.lmt.lv`
- **Tele2** (MNC 02): `internet.tele2.lv`
- **Bite** (MNC 03): `internet.bite.lv`

### Estonia (MCC 248)
- **EMT/Telia** (MNC 01): `internet.emt.ee`
- **Elisa** (MNC 02): `internet.elisa.ee`
- **Tele2** (MNC 03): `internet.tele2.ee`

**+ France, Spain, Italy, Netherlands** (see `config/carriers.json` for full list)

---

## 🔧 Manual Configuration

If you prefer manual configuration:

### Check Current APN:
```bash
printf "AT+CGDCONT?\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA
```

### Set Data APN:
```bash
printf "AT+CGDCONT=1,\"IP\",\"internet\"\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA
```

### Enable VoLTE (EC25):
```bash
# Enable IMS
printf "AT+QCFG=\"ims\",1\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA

# Enable VoLTE
printf "AT+QCFG=\"volte\",1\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA

# Restart modem
printf "AT+CFUN=1,1\r\n" > /dev/ttyUSB_EC25_DATA
```

### Verify VoLTE Status:
```bash
printf "AT+QCFG=\"volte\"\r\n" > /dev/ttyUSB_EC25_DATA
sleep 1
timeout 2 cat /dev/ttyUSB_EC25_DATA
```

---

## 🔄 Switching Between Modems

### Current Modem: EC25-AUX

**Characteristics:**
- USB Audio built-in (hw:EC25AUX)
- 3G/2G fallback available
- Stable symlink: `/dev/ttyUSB_EC25_DATA`

### Future Modem: SIM7600G-H

**Characteristics:**
- No USB audio (requires external sound card)
- 4G only (no 3G/2G fallback)
- More reliable
- VoLTE required for voice calls

**To switch:**
1. Physically replace modem
2. Run: `sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh`
3. Script will auto-detect new modem and configure it

---

## 📊 Logs

All configuration operations are logged:

```bash
# View latest log
ls -lt /home/rom/modem_manager/logs/ | head -5

# Read specific log
cat /home/rom/modem_manager/logs/auto_config_20251011_143919.log
```

**Log includes:**
- Modem detection
- SIM card IMSI
- Carrier identification
- All AT commands sent
- Responses received
- Success/failure status

---

## ⚠️ Troubleshooting

### Issue: "Permission denied" on /dev/ttyUSB_EC25_DATA

**Solution:** Run with sudo:
```bash
sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh
```

### Issue: "No such file or directory" for symlink

**Solution:** Recreate stable symlinks:
```bash
sudo ln -sf ttyUSB0 /dev/ttyUSB_EC25_CTRL
sudo ln -sf ttyUSB1 /dev/ttyUSB_EC25_DATA
```

Or install udev rules (see `/home/rom/to_test/99-quectel-ec25-stable.rules`)

### Issue: AT commands not responding

**Cause:** SMSTools or voice bot using the port

**Solution:** Script automatically stops services, but you can manually:
```bash
sudo systemctl stop smstools ec25-voice-bot
# Run your commands
sudo systemctl start smstools ec25-voice-bot
```

### Issue: Wrong APN configured

**Solution:** Check carrier database and verify:
```bash
# View carrier database
cat /home/rom/modem_manager/config/carriers.json | jq '.carriers."246-02"'

# Re-run configuration
sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh -f
```

### Issue: VoLTE not working

**Check:**
1. Carrier supports VoLTE
2. VoLTE enabled on modem: `AT+QCFG="volte"`
3. IMS registered: `AT+CIREG?`
4. Correct IMS APN configured

---

## 🎯 Testing Checklist

Before deploying to production, test:

- [ ] Modem detection works
- [ ] SIM card IMSI reads correctly
- [ ] Carrier identified correctly
- [ ] Data APN configured
- [ ] IMS APN configured
- [ ] VoLTE enabled
- [ ] Voice calls work
- [ ] Data connection works
- [ ] SMS works
- [ ] Services restart correctly

---

## 🌍 Adding New Carriers

To add a new carrier to the database:

1. Edit `/home/rom/modem_manager/config/carriers.json`
2. Add new entry under `"carriers"`:

```json
"260-04": {
  "carrier": "New Carrier Name",
  "country": "Poland",
  "country_code": "PL",
  "mcc": "260",
  "mnc": "04",
  "data_apn": "internet.carrier.pl",
  "ims_apn": "ims",
  "ims_domain": "ims.mnc004.mcc260.3gppnetwork.org",
  "volte_supported": true,
  "vowifi_supported": false,
  "ipv6_supported": true,
  "apn_type": "default,supl,ims",
  "auth_type": "NONE",
  "notes": "Description"
}
```

3. Test with: `sudo /home/rom/modem_manager/scripts/auto_configure_modem.sh --dry-run`

---

## 🔮 Future Features (When SIM7600G-H Arrives)

- [ ] Automatic modem switching script
- [ ] Modem failover (EC25 ↔ SIM7600)
- [ ] Dual-modem configuration
- [ ] External audio routing for SIM7600
- [ ] Performance comparison tests

---

## 📞 Support

For issues or questions:
1. Check logs: `/home/rom/modem_manager/logs/`
2. Review `/home/rom/CLAUDE.md` for AT command reference
3. Test with dry-run first: `--dry-run`

---

## 📝 Version History

**v1.0.0 (2025-10-11)**
- Initial release
- 40+ European carriers
- EC25-AUX and SIM7600G-H support
- Auto-detection and configuration
- VoLTE/IMS support
- Comprehensive logging

---

**Built with ❤️ for reliable voice communication across Europe**
