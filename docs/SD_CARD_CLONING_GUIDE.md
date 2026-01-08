# SD Card Cloning Guide for Raspberry Pi GSM Gateway

## Overview
This guide explains how to clone your Raspberry Pi SD card to create multiple GSM gateway units with unique VPN configurations.

## Prerequisites
- USB SD card reader
- Target SD card (minimum 8GB, preferably same size or larger than source)
- rpi-clone installed (already installed on this system)

## Step 1: Physical Cloning Process

### Insert Target SD Card
1. Insert your target SD card into a USB card reader
2. Connect to the Raspberry Pi
3. Verify detection:
```bash
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,MODEL
```
The new card will appear as `/dev/sda` or `/dev/sdb`

### Clone the SD Card
```bash
# Basic clone (keeps same hostname)
sudo rpi-clone sda

# Clone with new hostname (optional)
sudo rpi-clone -s pi2 sda
```

**Note:** Since we're using VPN IP for identification, keeping the same hostname is fine.

### Cloning Details
- Source: 128GB card with 6.3GB used
- Process time: ~15-20 minutes
- Only copies used space, not empty space
- Makes the target card bootable

## Step 2: Configure Unique VPN Identity (CRITICAL)

**IMPORTANT:** Each cloned Pi MUST have:
- Unique WireGuard VPN IP address
- Unique WireGuard public/private key pair
- Unique CLIENT_ID

### On the Cloned Pi (After First Boot)

1. **Boot the cloned Pi WITHOUT network initially** (to avoid conflicts)
2. **Run the deployment script:**
```bash
cd /home/rom
sudo ./deploy_client_auto.sh
```

3. **Enter the required information when prompted:**
```
Client phone number: +447700900145
Client name: Beta Corp
VPS SSH connection: root@167.99.123.45
# Enter VPS password when prompted
```

4. **The script will automatically:**
   - Validate uniqueness via webhooks (checks if IP/phone already in use)
   - Generate NEW unique WireGuard keys (required!)
   - Register client in central database
   - Configure WireGuard with phone-based IP (last 2 digits)
   - Set CLIENT_ID and environment variables
   - Update VPS configuration via SSH
   - Test VPN connectivity
   - Create client documentation file

5. **Script output will show:**
```
✅ DEPLOYMENT COMPLETE!
Client Configuration:
  Phone Number: +447700900145
  Name: Beta Corp
  IP: 10.100.0.45
  ID: CLIENT_phone_447700900145
```

### On the VPS Server

Add the new peer configuration provided by the script to your VPS WireGuard config:

```bash
# On VPS
sudo nano /etc/wireguard/wg0.conf

# Add the [Peer] section from above
# Then restart WireGuard
sudo wg-quick down wg0 && sudo wg-quick up wg0
```

## Step 3: Monitoring Integration

The monitoring scripts have been updated to include VPN IP in all notifications.

### Notification Format
- Original Pi: `pi [10.100.0.10]` 
- First clone: `pi [10.100.0.20]`
- Second clone: `pi [10.100.0.30]`

This allows easy identification of which unit is sending alerts, even with identical hostnames.

### Modified Scripts
- `/home/rom/SMS_Gateway/pi_send_message.sh` - Includes VPN IP in hostname field
- `/home/rom/wg-failover.sh` - Uses pi_send_message.sh for notifications

## Step 4: Phone Number Association

Phone numbers are associated with VPN IPs on the VPS server side, not on the Pi.

### VPS Configuration Example
The VPS maintains a mapping like:
```python
CLIENTS = {
    '10.100.0.10': {'name': 'Client A', 'phone': '+1234567890'},
    '10.100.0.20': {'name': 'Client B', 'phone': '+9876543210'},
    '10.100.0.30': {'name': 'Client C', 'phone': '+5555555555'},
}
```

## Complete Deployment Process

### For Each New Clone:

1. **Clone SD card:**
```bash
sudo rpi-clone sda
```

2. **Boot cloned Pi offline**

3. **Configure unique identity:**
```bash
sudo ./deploy_client_auto.sh
# Enter phone number, client name, and VPS details
```

4. **Add peer to VPS** (using output from script)

5. **Connect to network** and verify:
```bash
# Check VPN connection
sudo wg show
ping 10.100.0.1

# Test monitoring
/home/rom/SMS_Gateway/pi_send_message.sh "Test from new clone" info
```

## Important Notes About Scripts

### ⚠️ Script Location Update:
- **CORRECT SCRIPT:** `/home/rom/deploy_client_auto.sh` (use this one!)
- **OLD SCRIPT:** `/home/rom/to_delete/add_new_client_simple.sh` (deprecated - DO NOT USE)

The old `add_new_client_simple.sh` was moved to `to_delete` folder because it lacks:
- Database validation to prevent duplicate IPs/phones
- Automatic VPS configuration
- Phone number-based identification
- Webhook integration for centralized tracking

## Important Reminders

### ✅ DO:
- Use `deploy_client_auto.sh` (NOT the one in to_delete folder)
- Enter phone numbers with country code (e.g., +447700900145)
- Let script validate uniqueness before deployment
- Test VPN connectivity before deployment
- Keep track of which phone number uses which IP

### ❌ DON'T:
- Use the same WireGuard keys on multiple Pis
- Use the same VPN IP on multiple Pis
- Boot clones on same network before changing IP
- Forget to add new peer configuration to VPS

## Troubleshooting

### VPN Won't Connect
- Verify new keys were generated
- Check VPS has new peer configuration
- Ensure IP address is unique

### Monitoring Shows Wrong IP
- Restart pi_send_message service
- Check `ip addr show wg0` for correct IP

### Network Conflicts
- Ensure each Pi has unique VPN IP
- Check no duplicate WireGuard public keys

## Quick Reference

| Clone # | Phone Number    | VPN IP       | CLIENT_ID                    | Notes           |
|---------|-----------------|--------------|------------------------------|-----------------|
| Original| +447700900123   | 10.100.0.23  | CLIENT_phone_447700900123    | Current Pi      |
| Clone 1 | +447700900145   | 10.100.0.45  | CLIENT_phone_447700900145    | First clone     |
| Clone 2 | +33612345678    | 10.100.0.78  | CLIENT_phone_33612345678     | Second clone    |
| Clone 3 | +12025551234    | 10.100.0.34  | CLIENT_phone_12025551234     | Third clone     |

## Files Modified During Cloning

- `/etc/wireguard/wg0.conf` - VPN configuration
- `/etc/wireguard/private.key` - Unique private key  
- `/etc/wireguard/public.key` - Unique public key
- `/etc/environment` - CLIENT_ID and CLIENT_IP variables
- `/home/rom/client_info.txt` - Client documentation (created by deploy_client_auto.sh)
- Monitoring scripts already updated to include VPN IP

---

Last updated: January 2025 - Updated to use deploy_client_auto.sh
Location: /home/rom/SD_CARD_CLONING_GUIDE.md