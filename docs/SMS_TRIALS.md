## ?? Future Implementation: Faster SMS Reception (AT+CNMI)

**Status**: OPTIONAL - Not currently implemented, for future optimization only

### AT+CNMI Message Routing

`AT+CNMI=2,0,0,2,1` controls how SMS messages are delivered to your application.

**Command Breakdown:**
```
AT+CNMI = <mode>,<mt>,<bm>,<ds>,<bfr>
```

**Parameters:**
1. **mode=2**: Forward new SMS unsolicited result codes
2. **mt=0**: SMS storage
   - `0` = Store in default location (SM/ME)
   - `1` = Send SMS directly to serial port (no storage)
   - `2` = Store AND send notification
3. **bm=0**: Cell broadcast messages handling
4. **ds=2**: SMS-STATUS-REPORT routing
5. **bfr=1**: Buffer handling when connection unavailable

### Why It Matters

**Without CNMI (current default):**
- SMS arrives ? Stored silently ? SMSTools polls for new messages periodically
- Works reliably, slight polling delay

**With CNMI=2,0,0,2,1:**
- SMS arrives ? Modem immediately notifies "New SMS!" ? SMSTools processes instantly
- **Result**: Faster SMS reception, no polling delays (milliseconds improvement)

### Implementation

**To enable (future):**
```bash
# In /etc/smsd.conf, change init2 to:
init2 = AT+CPMS="SM";+CNMI=2,0,0,2,1
```

**Current Status**: Not needed - SMSTools polling is efficient enough for current use case. Only implement if real-time SMS alerts become critical.

 Problem 1: SMSTools doesn't support semicolon syntax. Earlier we tried:
  init2 = AT+CPMS="SM";+CSCS="UCS2"
  And it failed with "Unknown setting" error.

  Problem 2: The +CMTI notifications that are slowing down SMS sending are already coming from CNMI. Current modem setting is:
  +CNMI: 2,1,0,0,0
  This means mt=1 which sends +CMTI notifications when SMS arrives. These notifications interrupt delivery report handling.

  Potential Solution:

  Let me try a different approach:
  1. First, restore ME storage so SMS works
  2. Then test if changing CNMI to 2,0,0,0,0 (mt=0 instead of mt=1) stops the +CMTI interference

  Should I:
  1. Change back to AT+CPMS="ME","ME","ME" to restore SMS functionality
  2. Add init3 or replace init with AT+CNMI=2,0,0,0,0 to disable +CMTI notifications
  3. Test if this speeds up SMS sending
