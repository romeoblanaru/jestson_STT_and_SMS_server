# Pi Send Message Script Documentation

## Overview
`pi_send_message.sh` is a versatile notification script for Raspberry Pi systems that sends alerts and system status messages to the email notification system.

## Installation
```bash
# Copy script to Pi
scp pi_send_message.sh pi@YOUR_PI_IP:/home/pi/

# Make executable
chmod +x /home/pi/pi_send_message.sh
```

## Usage

### Basic Syntax
```bash
./pi_send_message.sh [command] [options]
```

### Quick Custom Messages
Send custom messages with optional severity level:
```bash
# Default severity (info)
./pi_send_message.sh "Your message here"

# With severity level
./pi_send_message.sh "Backup failed" error
./pi_send_message.sh "Temperature high" warning
./pi_send_message.sh "System crashed" critical
```

### Pre-defined Commands

#### 1. System Monitoring
```bash
# Quick system health check (one line)
./pi_send_message.sh system

# Comprehensive system report (detailed)
./pi_send_message.sh system-full
```

#### 2. Network Checks
```bash
# Check VPN connectivity
./pi_send_message.sh vpn

# Check general network connectivity
./pi_send_message.sh network
```

#### 3. Service Monitoring
```bash
# Check if a service is running
./pi_send_message.sh service ssh
./pi_send_message.sh service openvpn
./pi_send_message.sh service nginx
```

#### 4. Hardware Monitoring
```bash
# Check EC25 modem status
./pi_send_message.sh ec25
```

#### 5. Testing
```bash
# Send test message
./pi_send_message.sh test
```

## Severity Levels
Messages can have four severity levels:
- `info` (blue badge) - Default if not specified
- `warning` (yellow badge)
- `error` (orange badge)
- `critical` (red badge)

## Using from Other Scripts

### Example: Backup Script
```bash
#!/bin/bash
# backup_script.sh

# Run backup
if rsync -av /home/data /backup/; then
    /home/pi/pi_send_message.sh "Daily backup completed successfully"
else
    /home/pi/pi_send_message.sh "Backup failed - check logs" error
fi
```

### Example: Temperature Monitor
```bash
#!/bin/bash
# temp_monitor.sh

temp=$(vcgencmd measure_temp | cut -d'=' -f2 | cut -d"'" -f1)
temp_int=${temp%.*}

if [ "$temp_int" -gt 80 ]; then
    /home/pi/pi_send_message.sh "CPU temperature critical: ${temp}°C" critical
elif [ "$temp_int" -gt 70 ]; then
    /home/pi/pi_send_message.sh "CPU temperature warning: ${temp}°C" warning
fi
```

### Example: Service Watchdog
```bash
#!/bin/bash
# service_watchdog.sh

services=("ssh" "openvpn" "nginx")

for service in "${services[@]}"; do
    if ! systemctl is-active --quiet "$service"; then
        /home/pi/pi_send_message.sh "Service $service is down" error
        # Try to restart
        sudo systemctl restart "$service"
    fi
done
```

## Automated Monitoring with Cron

Add to crontab (`crontab -e`):
```bash
# System health check every 30 minutes
*/30 * * * * /home/pi/pi_send_message.sh system

# Full system report daily at 6 AM
0 6 * * * /home/pi/pi_send_message.sh system-full

# Check VPN every 5 minutes
*/5 * * * * /home/pi/pi_send_message.sh vpn

# Monitor critical services every 10 minutes
*/10 * * * * /home/pi/pi_send_message.sh service ssh
*/10 * * * * /home/pi/pi_send_message.sh service openvpn

# Custom monitoring script hourly
0 * * * * /home/pi/custom_monitor.sh
```

## System-Full Report Details
The comprehensive system report includes:
- **System Stats**: CPU usage, temperature, memory, disk usage
- **Network Info**: Local IP, Gateway, VPN IP
- **EC25 Status**: Modem detection and signal strength
- **Listening Ports**: Active services and ports
- **Top Processes**: CPU-intensive processes
- **Recent Errors**: System errors from the last hour

## Configuration
Edit the script to modify:
- `API_URL`: Change endpoint (default uses VPN internal IP)
- `SERVICE`: Change service identifier (default: "raspberry-pi-vpn")

## Troubleshooting

### Message not sending
```bash
# Test connectivity
curl -X POST http://10.100.0.1:5000/api/send \
  -H "Content-Type: application/json" \
  -d '{"hostname":"test","service":"test","severity":"info","message":"test"}'

# Check script permissions
ls -la /home/pi/pi_send_message.sh

# Run with debug
bash -x /home/pi/pi_send_message.sh test
```

### View sent messages
Visit the web interface:
- https://voice.rom2.co.uk/email
- Filter by IP to see only your Pi's messages

## Examples Summary
```bash
# Quick custom messages
./pi_send_message.sh "Deployment successful"
./pi_send_message.sh "Low disk space" warning
./pi_send_message.sh "Database error" error
./pi_send_message.sh "System overheating" critical

# System monitoring
./pi_send_message.sh system          # Quick status
./pi_send_message.sh system-full     # Full report

# Service checks
./pi_send_message.sh service mysql
./pi_send_message.sh vpn
./pi_send_message.sh network

# Hardware
./pi_send_message.sh ec25            # Modem status
```