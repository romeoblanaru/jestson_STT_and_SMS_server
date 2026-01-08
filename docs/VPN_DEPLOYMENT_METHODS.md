# VPN Client Deployment Methods Documentation

**Last Updated:** January 2025  
**Current Script:** `/home/rom/deploy_client_auto_vpn.sh`  
**Webhook Domain:** `my-bookings.co.uk` (note the 's')

## Overview

The deployment script now supports TWO methods for configuring new clients:

1. **VPN Tunnel Method** (PRIMARY - for cloned systems)
2. **SSH Key Method** (FALLBACK - when VPN not available)

## Method 1: VPN Tunnel Configuration (Recommended)

### How It Works

When you clone a Pi, it inherits the original's VPN connection. We use this existing tunnel to configure the new client identity:

```
Cloned Pi (10.100.0.10) → VPN Tunnel → VPS (10.100.0.1) → Webhook → Configure New Peer
```

### Prerequisites

1. **VPS Webhook Setup**
   - Endpoint: `http://10.100.0.1:8090/api/wireguard/add_peer`
   - Accepts JSON POST requests from VPN clients only
   - Modifies WireGuard configuration on VPS

2. **Original Pi Disconnected**
   - MUST disconnect original Pi before running script
   - Prevents IP conflicts during configuration

### Process Flow

1. **Detection Phase**
   ```bash
   # Script automatically detects:
   - Active WireGuard interface (wg0)
   - Current VPN IP (inherited from clone)
   - Connectivity to VPS (10.100.0.1)
   - Webhook availability
   ```

2. **Configuration Phase**
   ```bash
   # Script generates new keys locally
   sudo wg genkey → private key
   private key → public key
   ```

3. **VPS Update via Webhook**
   ```json
   POST http://10.100.0.1:8090/api/wireguard/add_peer
   {
       "new_ip": "10.100.0.45",          // New client IP
       "public_key": "xyz789...",        // New public key
       "phone": "+447700900145",         // Phone identifier
       "name": "Beta Corp",              // Client name
       "auth_token": "394c2b67..."      // Security token (SHA256 hash)
   }
   ```

4. **Identity Switch**
   ```bash
   # Stop old connection
   sudo systemctl stop wg-quick@wg0
   
   # Apply new configuration
   Address = 10.100.0.45/32          # New IP
   PrivateKey = [new_private_key]    # New key
   
   # Start with new identity
   sudo systemctl start wg-quick@wg0
   ```

### Advantages

- **No SSH keys needed** - Uses existing VPN tunnel
- **More secure** - Webhook only accessible from VPN network
- **Faster** - Single webhook call vs multiple SSH commands
- **Automatic validation** - VPS knows request comes from valid client

### VPS Webhook Implementation

Your webhook at `http://10.100.0.1:8090/api/wireguard/add_peer` expects:

```python
# Expected payload format
{
    "new_ip": "10.100.0.45",           # New client IP address
    "public_key": "nM9Fj...",          # WireGuard public key
    "phone": "+447700900145",          # Phone number identifier
    "name": "Beta Corp",                # Client name
    "auth_token": "394c2b67cf7b..."    # SHA256 auth token
}

# The webhook should:
# 1. Validate auth token matches expected value
# 2. Validate request comes from VPN subnet (10.100.0.0/24)
# 3. Add peer to /etc/wireguard/wg0.conf
# 4. Run: wg set wg0 peer [public_key] allowed-ips [new_ip]/32
# 5. Return: {"status": "success"} or {"status": "error", "message": "..."}
```

## Method 2: SSH Key Configuration (Fallback)

### When Used

- VPN tunnel method fails
- Webhook not accessible
- Fresh installation (no inherited VPN)
- User chooses SSH method

### How It Works

1. **Temporary SSH Key Input**
   ```
   - User pastes SSH private key
   - Stored in RAM (/dev/shm/) not disk
   - Used for VPS configuration
   - Automatically deleted after use
   ```

2. **Security Features**
   ```bash
   # Trap ensures cleanup even on failure
   trap cleanup EXIT INT TERM
   
   # Secure deletion with shred
   shred -vfz -n 3 /dev/shm/temp_ssh_key_$$
   ```

3. **Process Flow**
   - Prompt for SSH key
   - Test SSH connection
   - Configure VPS via SSH
   - Delete key immediately

### Advantages

- **No permanent keys** on Pi
- **Works without VPN** connection
- **Secure cleanup** guaranteed
- **Manual control** over authentication

## Script Decision Flow

```
START
  ↓
Check VPN Connection
  ↓
Connected? ──NO──→ Use SSH Method
  ↓YES
Check Webhook
  ↓
Accessible? ──NO──→ Use SSH Method
  ↓YES
Use VPN Method
  ↓
Success? ──NO──→ Fallback to SSH Method
  ↓YES
DONE
```

## Usage Instructions

### For Cloned Systems (VPN Method)

1. **Clone the SD card**
   ```bash
   sudo rpi-clone sda
   ```

2. **Boot cloned Pi**
   - Disconnect original Pi first!
   - Cloned Pi starts with inherited VPN

3. **Run deployment script**
   ```bash
   sudo ./deploy_client_auto_vpn.sh
   ```

4. **Script auto-detects VPN**
   ```
   DETECTED: Active VPN Connection
   Current VPN IP: 10.100.0.10
   Use VPN tunnel method? (y/n): y
   ```

5. **Enter client details**
   ```
   Phone number: +447700900145
   IP suffix: 45
   Client name: Beta Corp
   ```

6. **Automatic configuration**
   - Generates new keys
   - Calls VPS webhook
   - Switches identity
   - Tests connection

### For Fresh Systems (SSH Method)

1. **Run deployment script**
   ```bash
   sudo ./deploy_client_auto_vpn.sh
   ```

2. **No VPN detected**
   ```
   ⚠️ No WireGuard interface found
   Will use SSH configuration method
   ```

3. **Enter VPS details**
   ```
   VPS SSH connection: root@144.91.96.97
   ```

4. **Paste SSH key when prompted**
   ```
   Paste your SSH private key below
   [Paste key, press Enter, Ctrl-D]
   ```

5. **Automatic configuration**
   - Uses SSH to configure VPS
   - Deletes SSH key after use

## Configuration Files

### Generated Files

- `/etc/wireguard/wg0.conf` - WireGuard configuration
- `/etc/wireguard/private.key` - Client private key
- `/etc/wireguard/public.key` - Client public key
- `/etc/environment` - Environment variables
- `/home/rom/client_info.txt` - Deployment summary

### Persistent Settings

- `/home/rom/.deploy_config` - Saved webhook domain

## Troubleshooting

### VPN Method Issues

**Webhook not accessible:**
- Check VPS webhook is running on port 8090
- Verify firewall allows VPN subnet access
- Test: `curl http://10.100.0.1:8090/api/wireguard/add_peer`

**Configuration fails:**
- Ensure original Pi is disconnected
- Check auth token matches VPS expectation
- Verify VPS has write permissions to WireGuard config

### SSH Method Issues

**SSH connection fails:**
- Verify SSH key is correct
- Check key is authorized on VPS
- Ensure VPS IP is correct

**Key not deleted:**
- Script has trap handler for cleanup
- Manually check: `ls /dev/shm/temp_ssh*`
- Remove if found: `rm -f /dev/shm/temp_ssh*`

## Security Considerations

### VPN Method
- ✅ Webhook only accessible from VPN network
- ✅ Request validated by source IP
- ✅ Auth token for additional security
- ✅ No SSH keys needed

### SSH Method
- ✅ Keys stored in RAM only
- ✅ Automatic deletion guaranteed
- ✅ 3-pass secure shred
- ✅ No permanent traces

## Best Practices

1. **Always disconnect original Pi** before configuring clone
2. **Use VPN method** when possible (more secure)
3. **Test webhook** before deployment
4. **Keep auth token** secret and rotate regularly
5. **Monitor VPS logs** for configuration attempts

## Summary

The dual-method approach provides:
- **Convenience** - VPN method for easy cloned deployments
- **Flexibility** - SSH fallback for any situation
- **Security** - No permanent credentials on Pi
- **Reliability** - Automatic fallback if primary fails

The script intelligently chooses the best method and handles all configuration automatically, making deployment both secure and user-friendly.