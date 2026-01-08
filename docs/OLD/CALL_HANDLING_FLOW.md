# Complete Call Handling Flow

## Critical Change: NO MORE LAZY LOADING

### ❌ OLD APPROACH (Wrong):
- Voice config loaded on first phone call
- Welcome message was hardcoded
- answer_after_rings couldn't be changed dynamically
- No way to reject calls programmatically

### ✅ NEW APPROACH (Correct):
- **Unified API**: Loads config at STARTUP (ready immediately)
- **Voice Bot**: Fetches FRESH config on EVERY RING (from VPS webhook)
- **Dynamic control**: answer_after_rings can change per call
- **Selective answering**: answer_after_rings = -1 means DON'T answer

---

## Complete Flow: From RING to Conversation

### Phase 1: System Startup

#### Unified API (Port 8088)
```
Service starts
    ↓
Load voice_config.json
    ↓
Initialize Azure TTS
    ↓
Start TTS processor thread
    ↓
✅ Ready to handle TTS requests
```

**Logs:**
```
INFO - Loading voice configuration at startup...
INFO - Loaded voice config: azure for en
INFO - ✅ Azure TTS initialized
INFO - ✅ TTS processor started at startup
```

#### Voice Bot (SIM7600)
```
Service starts
    ↓
Wait for port mapping from detector
    ↓
Stop smstools
    ↓
Open /dev/ttyUSB2
    ↓
Initialize modem:
  - AT → Test
  - AT+CLIP=1 → Enable caller ID
  (Note: ATS0 NOT set here!)
    ↓
✅ Ready to receive calls
```

**Logs:**
```
INFO - Stopping smstools to take over serial port...
INFO - Opening serial port: /dev/ttyUSB2
INFO - SIM7600 initialized (ATS0 will be set on RING)
INFO - Starting modem monitor
```

---

### Phase 2: Incoming Call (RING Detected)

```
📞 RING arrives
    ↓
Extract caller ID from +CLIP
    ↓
📡 FETCH FRESH CONFIG FROM VPS
```

**Critical Step: Config Fetch**
```python
# This happens IMMEDIATELY on RING, before answering
GET http://my-bookings.co.uk/webhooks/get_voice_config.php?ip=10.100.0.11&include_key=1

Response:
{
  "success": true,
  "data": {
    "answer_after_rings": 3,      ← Can be changed per call
    "welcome_message": "Hello!",   ← Fresh greeting
    "language": "en",
    "tts_model": "azure",
    // ...
  }
}
```

**Logs:**
```
INFO - 📞 RING detected from +44XXXXXXXXX
INFO - Fetching fresh voice configuration from VPS...
INFO - ✅ Fresh voice config fetched from VPS
INFO -   Language: en
INFO -   Answer after: 3 rings
INFO -   Welcome message: Hello! You have reached...
```

---

### Phase 3: Decision Point

#### Scenario A: answer_after_rings = -1 (DON'T ANSWER)

```
Config: answer_after_rings = -1
    ↓
🚫 Log: "NOT answering this call"
    ↓
Send notification to VPS:
  {
    "event": "call_rejected",
    "caller": "+44XXXXXXXXX",
    "reason": "answer_after_rings set to -1"
  }
    ↓
Return (don't answer)
    ↓
Modem: Call rings out, caller gets no answer
```

**Use cases for -1:**
- Outside business hours
- Specific caller blocked
- System maintenance
- Queue full
- Emergency override

**Logs:**
```
INFO - Answer setting: -1 rings
INFO - 🚫 answer_after_rings = -1: NOT answering this call
INFO - VPS notified: call_rejected
```

---

#### Scenario B: answer_after_rings = 1-10 (ANSWER)

```
Config: answer_after_rings = 3
    ↓
Configure modem:
  ATS0=3  ← Answer after 3 rings
    ↓
Wait for 3 rings...
    ↓
Modem auto-answers
    ↓
✅ Call connected
```

**Logs:**
```
INFO - Answer setting: 3 rings
INFO - Configuring modem to answer after 3 rings...
INFO - Waiting for 3 rings...
INFO - ✅ Call answered: call_1760285123
```

---

### Phase 4: After Answering

```
Call connected
    ↓
Generate call_id & session_id
    ↓
Set in_call = True
    ↓
Start 3 audio threads:
  - Audio capture (from phone)
  - Audio playback (to phone)
  - Transcription (Whisper STT)
    ↓
📢 Play welcome message
```

**Welcome Message Flow:**
```
welcome_message from config:
  "Hello! You have reached our beauty salon. How can I help you?"
    ↓
Request TTS (priority=high):
  POST http://localhost:8088/phone_call
  {
    "callId": "call_1760285123",
    "text": "Hello! You have reached...",
    "action": "speak",
    "priority": "high"
  }
    ↓
Unified API TTS processor:
  - Azure TTS synthesis
  - Stream audio chunks
  - First chunk: ~631ms
    ↓
Audio chunks → voice bot → /dev/ttyUSB4
    ↓
🔊 Caller hears welcome message
```

**Logs:**
```
INFO - Playing welcome message: Hello! You have reached our beauty...
INFO - Queued TTS for call call_1760285123
INFO - Processing TTS: Hello! You have reached...
INFO - ⚡ First audio chunk in 631ms
INFO - ✅ Synthesis complete: 2.5s audio in 0.7s
```

---

### Phase 5: Conversation Loop

```
Caller speaks
    ↓
Audio capture → VAD detects speech
    ↓
Silence detected (800ms)
    ↓
Whisper transcription
    ↓
Send to VPS:
  POST http://10.100.0.1:8088/webhook/phone_call/receive
  {
    "event": "transcription",
    "callId": "call_1760285123",
    "text": "I'd like to book an appointment"
  }
    ↓
VPS processes with LLM
    ↓
VPS responds:
  POST http://10.100.0.11:8088/phone_call
  {
    "callId": "call_1760285123",
    "text": "Of course! What time works for you?",
    "action": "speak"
  }
    ↓
TTS synthesis
    ↓
🔊 Caller hears response
    ↓
🔄 Loop continues...
```

---

### Phase 6: Call Ends

```
Either party hangs up
    ↓
Modem sends: NO CARRIER
    ↓
Voice bot detects
    ↓
in_call = False
    ↓
Stop all audio threads
    ↓
Send to VPS:
  POST http://10.100.0.1:8088/webhook/phone_call/receive
  {
    "event": "call_ended",
    "callId": "call_1760285123"
  }
    ↓
✅ Ready for next call
```

---

## Configuration Control

### VPS Can Control Per-Call:

```json
{
  "answer_after_rings": 3,      // 1-10 = answer, -1 = don't answer
  "welcome_message": "Hello!",  // Played after answering
  "language": "en",             // For STT/TTS
  "tts_model": "azure",         // Which TTS engine
  "voice_settings": {           // Voice characteristics
    "voice": "en-US-AriaNeural",
    "pitch": 1.0,
    "speed": 1.2
  }
}
```

### Dynamic Scenarios:

**Scenario 1: Business Hours**
```
9 AM - 5 PM:  answer_after_rings = 2
5 PM - 9 AM:  answer_after_rings = -1  (don't answer)
```

**Scenario 2: Queue Management**
```
Queue < 5:    answer_after_rings = 2
Queue >= 5:   answer_after_rings = -1  (at capacity)
```

**Scenario 3: Caller-Specific**
```
VIP caller:   answer_after_rings = 1  (immediate)
Blocked:      answer_after_rings = -1 (never answer)
Normal:       answer_after_rings = 3  (standard)
```

---

## Key Benefits

1. **Fresh config every call** - No stale settings
2. **Dynamic control** - VPS can change behavior instantly
3. **Selective answering** - Full control over which calls to take
4. **Custom greetings** - Per-call welcome messages
5. **No lazy loading** - Everything ready from startup

---

## Testing Commands

**Test answer_after_rings = -1:**
```bash
# Temporarily set to -1
jq '.answer_after_rings = -1' /home/rom/voice_config.json > /tmp/config.json
sudo mv /tmp/config.json /home/rom/voice_config.json

# Make a test call - should NOT be answered
# Check logs:
tail -f /var/log/sim7600_voice_bot.log
# Should see: "🚫 answer_after_rings = -1: NOT answering this call"
```

**Test custom welcome message:**
```bash
# Update welcome message
jq '.welcome_message = "Test greeting from Pi!"' /home/rom/voice_config.json > /tmp/config.json
sudo mv /tmp/config.json /home/rom/voice_config.json

# Make a test call
# Should hear new greeting
```

**Monitor live flow:**
```bash
# Terminal 1: Voice bot
sudo journalctl -f -u sim7600-voice-bot

# Terminal 2: Unified API
sudo journalctl -f -u sms-api

# Terminal 3: Detector
tail -f /var/log/sim7600_detector.log
```

---

## Architecture Summary

```
┌─────────────────────────────────────────────────────────┐
│                    RING DETECTED                         │
│                          ↓                               │
│              Fetch Fresh Config from VPS                 │
│                          ↓                               │
│              Check answer_after_rings                    │
│                    ↙         ↘                          │
│            = -1               1-10                      │
│             ↓                  ↓                        │
│      DON'T ANSWER          ANSWER                      │
│      Notify VPS            After N rings               │
│      Return                     ↓                      │
│                         Play Welcome Message            │
│                                 ↓                       │
│                      Start Conversation                │
│                                 ↓                       │
│                    Audio ↔ Transcription ↔ VPS        │
└─────────────────────────────────────────────────────────┘
```

**Everything is ready for production!**
