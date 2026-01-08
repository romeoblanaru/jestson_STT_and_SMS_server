# SMSTools Management Strategy

## Critical Issue: Serial Port Exclusivity
SMSTools keeps `/dev/ttyUSB2` (and other serial ports) open EXCLUSIVELY. No other process can access them while smstools is running.

## Solution: Phased SMSTools Management

### Phase 1: Detection (sim7600_detector.py)
**Purpose:** Quickly verify if modem is SIM7600

```
smstools: RUNNING
    ↓
Stop smstools (2 seconds)
    ↓
Send AT commands:
  - AT → OK?
  - AT+CGMI → SIMCOM?
  - AT+CGMM → SIM7600?
    ↓
Restart smstools immediately
    ↓
smstools: RUNNING again
```

**Duration:** 2-3 seconds pause
**Impact:** Minimal - SMS functionality restored quickly

---

### Phase 2: Voice Bot Initialization (sim7600_voice_bot.py)
**Purpose:** Take full control for voice call handling

```
smstools: RUNNING
    ↓
Voice bot starts
    ↓
Stop smstools COMPLETELY
    ↓
Wait 2 seconds for port release
    ↓
Open serial port /dev/ttyUSB2
    ↓
Initialize modem:
  - AT → Test
  - ATE0 → Disable echo
  - AT+CEXTERNTONE=1 → External audio
  - AT+CLIP=1 → Enable caller ID
  - ATS0=3 → Auto-answer after 3 rings
  - AT+CLVL=5 → Set volume
    ↓
Keep serial port OPEN
    ↓
smstools: STOPPED (voice bot owns the port)
```

**Duration:** Indefinite - as long as voice bot runs
**Impact:** SMS via smstools disabled, but unified API still handles SMS on port 8088

---

### Phase 3: Voice Bot Running
**State:** smstools STOPPED, voice bot RUNNING

```
Voice Bot owns /dev/ttyUSB2:
  - Monitors for RING
  - Handles calls with ATA
  - Sends AT commands as needed
  - Full control of serial port
```

**SMS Handling:**
- ✅ SMS sending: Works via unified API port 8088
- ❌ SMS receiving: Disabled (modem busy with voice)
- Acceptable: During call handling, SMS is secondary

---

### Phase 4: Voice Bot Exit (clean or crash)
**Purpose:** Restore full SMS functionality

```
Voice bot shutting down...
    ↓
Close serial port /dev/ttyUSB2
    ↓
Start smstools
    ↓
Wait 1 second
    ↓
smstools: RUNNING
    ↓
SMS functionality restored
```

**Triggers:**
- Normal shutdown (Ctrl+C)
- Service restart
- Crash/error
- Systemd stop command

**Guaranteed:** `finally` block always runs

---

## Implementation

### In sim7600_voice_bot.py:

```python
def init_modem(self):
    # CRITICAL: Stop smstools first
    if not self.stop_smstools():
        logger.error("Cannot proceed - smstools blocking port")
        return False

    # Now safe to open serial port
    self.ser = serial.Serial(self.at_port, 115200)
    # ... AT commands ...

def main():
    bot = SIM7600VoiceBot()
    try:
        bot.monitor_modem()
    finally:
        # CRITICAL: Always restart smstools
        bot.restart_smstools()
```

---

## Benefits

1. **Clean separation:** Each component owns the port when needed
2. **No conflicts:** Port is never accessed by two processes
3. **Automatic recovery:** smstools always restarts on voice bot exit
4. **Production-ready:** Handles crashes gracefully

---

## Monitoring

**Check current state:**
```bash
# Is smstools running?
systemctl is-active smstools

# Is voice bot running?
systemctl is-active sim7600-voice-bot

# Who owns the port?
sudo lsof /dev/ttyUSB2
```

**Expected states:**
- **Idle (no modem):** smstools STOPPED, voice bot INACTIVE
- **Modem detected:** smstools RUNNING, voice bot STARTING
- **Voice bot active:** smstools STOPPED, voice bot RUNNING
- **Voice bot stopped:** smstools RUNNING, voice bot INACTIVE

---

## Edge Cases Handled

1. **Voice bot crashes:** `finally` block restarts smstools
2. **Service killed:** systemd restarts voice bot, which restarts smstools on exit
3. **Manual stop:** `systemctl stop sim7600-voice-bot` → smstools restarted
4. **Port busy:** Voice bot won't start if can't stop smstools

---

## Configuration

**Auto-answer rings:** Read from `/home/rom/voice_config.json`
```json
{
  "answer_after_rings": 3
}
```

Becomes: `ATS0=3` (auto-answer after 3 rings)
