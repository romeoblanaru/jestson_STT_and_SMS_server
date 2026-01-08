# SMS Delay Solutions - Priority Order to Try
## Problem: CMTI notifications interrupting SMS sending

### Solution 1: Disable CMTI Notifications (EASIEST & CLEANEST)
**Implementation**: Add to smsd.conf: `init3 = AT+CNMI=2,0,0,0,0`
**How it works**:
- Changes mt parameter from 1 to 0
- SMS still stored in modem memory but no +CMTI interruptions
- SMSTools polls for new messages every second (blocktime=1)
**Pros**:
- No code changes needed
- Clean separation of send/receive operations
- Already have check_memory_method=1 configured
**Cons**:
- Max 1 second delay for incoming SMS detection (negligible)
**Test command**:
```bash
sudo systemctl stop smstools
echo -e "AT+CNMI=2,0,0,0,0\r" > /dev/ttyUSB2
sudo systemctl start smstools
```

### Solution 2: Enable CNMI Buffer Management
**Implementation**: Add to smsd.conf: `init3 = AT+CNMI=2,1,0,0,1`
**How it works**:
- Last parameter (bfr=1) enables buffering of unsolicited results
- Notifications queued when DTE-DCE link is reserved
- Released after AT command completion
**Pros**:
- Keeps instant notifications but prevents interruptions
- No polling delay
**Cons**:
- May not be fully supported by SIM7600 firmware
- Need to test firmware support
**Test command**:
```bash
sudo systemctl stop smstools
echo -e "AT+CNMI=2,1,0,0,1\r" > /dev/ttyUSB2
sudo systemctl start smstools
```

### Solution 3: Dynamic CNMI Toggle Wrapper
**Implementation**: Create wrapper script that manages CNMI state
**How it works**:
- Before sending: Disable CNMI (AT+CNMI=2,0,0,0,0)
- Send SMS
- After sending: Re-enable CNMI (AT+CNMI=2,1,0,0,0)
**Pros**:
- Guaranteed no interruptions during send
- Maintains instant receive notifications when idle
**Cons**:
- Requires custom wrapper script
- More complex implementation
**Files to create**:
- `/usr/local/bin/sms_send_wrapper.sh`
- Modify SMSTools to use wrapper

### Solution 4: Modify SMSTools Source - Filter +CMTI
**Implementation**: Patch SMSTools3 source code
**How it works**:
- Add response parser that filters out +CMTI during AT+CMGS
- Cache CMTI notifications for processing after send complete
**Pros**:
- Most robust solution
- Handles all edge cases
**Cons**:
- Requires downloading SMSTools source
- Need to compile and maintain custom version
**Steps**:
1. Download smstools3 source
2. Modify src/modeminit.c or src/smsd_cfg.c
3. Compile and install

### Solution 5: Increase SMSTools Timeouts & Error Handling
**Implementation**: Modify smsd.conf parameters
**How it works**:
- Increase command timeouts to handle interruptions better
- Add more robust error recovery
**Pros**:
- Simple config change
- Might reduce impact of CMTI delays
**Cons**:
- Doesn't fix root cause, just mitigation
**Config changes**:
```
errorsleeptime = 3
send_retries = 1
blockafter = 1
```

### Solution 6: Use AT+CMGW (Write to Memory) Instead of Direct Send
**Implementation**: Change SMS sending method
**How it works**:
- Write SMS to memory first (AT+CMGW)
- Then send from memory (AT+CMSS)
- CMTI won't interrupt memory operations as much
**Pros**:
- More atomic operations
- Better error recovery
**Cons**:
- Requires SMSTools configuration change
- Uses modem memory

## Additional Ideas to Explore:

### Solution 7: Check if SIM7600 Supports AT+CSMP
**Test**: Set SMS parameters to ignore delivery reports temporarily
```bash
AT+CSMP=17,167,0,0  # Disable delivery reports
```

### Solution 8: Use AT+CMMS (More Messages to Send)
**Test**: Enable continuous SMS mode to reduce handshaking
```bash
AT+CMMS=2  # Keep SMS link active
```

## Testing Order:
1. Try Solution 1 first (simplest, most likely to work)
2. If partial improvement, try Solution 2
3. If still issues, implement Solution 3
4. Last resort: Solution 4 (compile custom SMSTools)

## Notes:
- PDU mode excluded (need TEXT for diacritics)
- Dual-port excluded (ttyUSB3 used by voice bot)
- Each solution should be tested with sending multiple SMS rapidly
- Monitor /var/log/smstools/smsd.log for timing improvements