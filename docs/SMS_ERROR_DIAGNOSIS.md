# SMS MODEM ERROR Diagnosis

## Critical Issue: MODEM ERROR when sending SMS from webpage

### Error Timeline
- **09:25:35-40**: "+CMS ERROR: Unknown error" (3 retry attempts)
- **09:26:33-36**: Next SMS worked fine (1 second send time)
- Pattern: Intermittent failures

### Root Causes Identified

## 1. ME Storage Performance Issue (PRIMARY)
**Current config**: `AT+CPMS="ME","ME","ME"`
- ME (modem internal memory) has severe access delays on SIM7600
- Causes 3-4 minute delays and intermittent CMS errors
- EC25 used SM (SIM card) storage - worked fine

## 2. CMS ERROR: Unknown error
This generic error typically means:
- Memory access timeout
- Storage corruption
- Modem busy/locked
- Internal modem state error

## 3. Web Interface Implications
When SMS fails with CMS ERROR:
1. SMSTools marks message as FAILED after retries
2. Web API might show "MODEM ERROR" to user
3. Message moved to /var/spool/sms/failed/

## Immediate Fix Actions

### Step 1: Clear and Switch Storage (DO THIS FIRST)
```bash
# Stop services
sudo systemctl stop smstools sim7600-voice-bot

# Clear ALL messages from ME storage
echo -e "AT+CMGD=1,4\r" > /dev/ttyUSB2
sleep 2

# Switch to SM (SIM card) storage
echo -e "AT+CPMS=\"SM\",\"SM\",\"SM\"\r" > /dev/ttyUSB2
sleep 1

# Verify change
echo -e "AT+CPMS?\r" > /dev/ttyUSB2
sleep 0.5
cat /dev/ttyUSB2

# Restart services
sudo systemctl start smstools sim7600-voice-bot
```

### Step 2: Update SMSTools Configuration
Edit `/etc/smsd.conf`:
```bash
# Change from:
init2 = AT+CPMS="ME","ME","ME"

# To:
init2 = AT+CPMS="SM","SM","SM"
```

### Step 3: Disable CMTI Interruptions
Add to `/etc/smsd.conf`:
```bash
init3 = AT+CNMI=2,0,0,0,0
```

### Step 4: Monitor Results
Run the timing monitor to verify improvements:
```bash
/home/rom/sms_timing_monitor_v2.sh
```

## Expected Results
- Before: 3-4 minute delays, CMS errors
- After: <6 second delays (like EC25)
- No more "MODEM ERROR" on webpage

## Long-term Solutions

1. **Implement Error Recovery in API**
   - Check /var/spool/sms/failed/ directory
   - Retry failed messages automatically
   - Alert on persistent failures

2. **Add Modem Health Check**
   - Regular AT+CPMS? checks
   - Monitor storage usage
   - Alert when ME/SM gets full

3. **Consider USB Composition Change**
   - Current: 9001 (voice priority)
   - Alternative: Test other modes for better SMS performance

## Testing Procedure
1. Send test SMS from webpage
2. Monitor with timing script
3. Check for CMS errors in logs
4. Verify <10 second total latency

## Emergency Fallback
If SM storage also fails:
```bash
# Try SR (Status Report) storage
init2 = AT+CPMS="SR","SR","SR"
```