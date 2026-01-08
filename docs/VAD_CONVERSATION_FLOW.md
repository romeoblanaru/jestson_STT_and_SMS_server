# VAD-Based Conversation Flow Control

## Problem Statement
During phone conversations, the bot and caller must not speak simultaneously. Without conversation flow control, the bot might start talking while the caller is still speaking, creating an unprofessional and confusing experience.

## Solution: Smart Playback with VAD

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    CONVERSATION FLOW                         │
│                                                               │
│  Caller speaks → VAD detects → 800ms silence → Bot speaks   │
│       ↓              ↓              ↓              ↓          │
│   Capture        Analyze       Signal         Playback       │
│   Audio          Speech        Ready          TTS            │
└─────────────────────────────────────────────────────────────┘
```

### Components

#### 1. **Audio Capture with VAD (Thread 1)**
- Reads 20ms audio frames from `/dev/ttyUSB4`
- Runs WebRTC VAD on each frame
- Detects speech vs silence
- Tracks silence duration
- Sets `caller_is_silent` event after 800ms silence
- Queues complete utterances for transcription

**Key Features:**
- Real-time speech detection using WebRTC VAD (lightweight, telephony-optimized)
- 800ms silence threshold (configurable)
- Energy-based fallback if WebRTC VAD unavailable
- Thread-safe state management

#### 2. **Smart Audio Playback (Thread 2)**
- Monitors `audio_out_queue` for TTS responses
- **CRITICAL**: Waits for `caller_is_silent` event before playing
- Prevents talking over the caller
- Continues playing subsequent chunks without interruption
- Marks when bot finishes speaking

**Key Features:**
- Detects start of new messages (queue empty → not empty)
- Waits up to 10 seconds for caller to finish
- Double-checks recent speech activity
- Thread-safe playback decisions

#### 3. **Conversation State (Thread-Safe)**
```python
self.caller_is_silent = threading.Event()  # Set when 800ms silence
self.bot_is_speaking = False               # True during playback
self.last_speech_time = 0                  # Timestamp of last speech
self.playback_lock = threading.Lock()      # Atomic state changes
```

## Flow Diagram

### Scenario 1: Normal Conversation
```
Time: 0ms
Caller: "Hello, I'd like to book an appointment"
VAD: Speech detected → Clear caller_is_silent
Capture: Collecting audio...

Time: 3000ms
Caller: [finishes speaking]
VAD: Silence detected...

Time: 3800ms
VAD: 800ms silence reached → Set caller_is_silent
Capture: Queue audio for transcription
STT: Transcribe → "I'd like to book an appointment"
VPS: Process → Generate response
TTS: "Of course! What time works for you?"

Playback: New message in queue
Playback: Wait for caller_is_silent ✅ (already set)
Playback: Start speaking → Set bot_is_speaking
Playback: Playing audio chunks...
Playback: Queue empty → Clear bot_is_speaking

Time: 8000ms
Bot: [finished speaking]
Caller: "How about 2 PM?"
VAD: Speech detected → Clear caller_is_silent
[Cycle repeats...]
```

### Scenario 2: Caller Still Speaking When Response Ready
```
Time: 0ms
Caller: "I'm looking for a haircut, maybe color too..."
VAD: Speech detected
TTS: [Response ready from previous turn] "Here are our services"

Playback: New message in queue
Playback: Wait for caller_is_silent ⏳ (not set - caller still speaking)
Playback: Waiting... (up to 10 seconds)

Time: 2000ms
Caller: "...and perhaps highlights"
VAD: Still detecting speech
Playback: Still waiting...

Time: 2500ms
Caller: [finishes]
VAD: Silence detected...

Time: 3300ms
VAD: 800ms silence → Set caller_is_silent
Playback: caller_is_silent set ✅
Playback: Start speaking → "Here are our services"
```

### Scenario 3: Timeout (Caller Won't Stop)
```
Time: 0ms
TTS: Response ready
Playback: Wait for caller_is_silent ⏳

Time: 10000ms (10 seconds elapsed)
Playback: Timeout! ⚠️
Playback: Check last_speech_time
  - If < 2 seconds ago: Wait 2 more seconds
  - If > 2 seconds ago: Proceed anyway

Playback: Play message (caller may still be talking)
```

## Configuration

### VAD Parameters (in audio_capture_thread)
```python
vad_mode = 3                  # Aggressiveness (0-3, 3=most aggressive)
silence_duration_ms = 800     # Pause threshold
min_speech_frames = 10        # Minimum 200ms of speech
```

### Playback Timeouts (in audio_playback_thread)
```python
silence_wait_timeout = 10.0   # Max wait for caller silence (seconds)
fallback_wait = 2.0           # Additional wait if caller still speaking
```

### Fallback (No VAD Available)
```python
# Simple energy-based detection
energy = np.abs(audio_int16).mean()
is_speech = energy > 500  # Adjust threshold as needed
```

## Benefits

1. **No Overlap** - Bot never talks over caller
2. **Natural Flow** - 800ms pause feels natural
3. **Responsive** - Bot speaks immediately after pause
4. **Robust** - Handles edge cases (long silence, no pause, etc.)
5. **Fallback** - Works without PyTorch using energy detection

## Logs Examples

### Normal Operation
```
INFO - 🎤 Speech started
DEBUG - Speech detected (WebRTC VAD: True)
INFO - 🔇 800ms silence detected - caller finished speaking (145 speech frames)
INFO - Queued 145 frames (46400 bytes) for transcription
DEBUG - 📢 New message ready - waiting for caller silence...
INFO - 🔊 Bot started speaking
DEBUG - Played 8000 bytes to caller
INFO - ✅ Bot finished speaking
```

### Waiting for Silence
```
DEBUG - 📢 New message ready - waiting for caller silence...
WARN - ⚠️ Timeout waiting for silence - checking if caller still speaking...
INFO - No recent speech detected - proceeding with playback
INFO - 🔊 Bot started speaking
```

### VAD Disabled
```
WARN - WebRTC VAD not available - VAD will be disabled
INFO - WebRTC VAD enabled: False
INFO - Using energy-based speech detection (fallback)
```

## Testing

### Test 1: Normal Conversation
```bash
# Monitor logs
sudo journalctl -f -u sim7600-voice-bot

# Make test call
# Speak: "Hello" → Wait 1 second → Expect bot response
# Verify log: "800ms silence detected"
# Verify log: "Bot started speaking"
```

### Test 2: No Pause (Continuous Speech)
```bash
# Speak continuously for 10+ seconds without pause
# Verify: Bot waits entire time
# Verify log: "Timeout waiting for silence"
# Verify: Bot plays after timeout
```

### Test 3: Interrupt During Bot Speech
```bash
# Let bot start speaking
# Start speaking while bot talks
# Verify: Bot continues (doesn't stop mid-sentence)
# Verify: After bot finishes, your speech is captured
```

## Troubleshooting

### Bot Never Speaks
**Symptom:** Caller finishes, but bot doesn't respond
**Cause:** `caller_is_silent` never set
**Check:** VAD logs - is silence being detected?
**Fix:** Adjust `vad_threshold` or `silence_duration_ms`

### Bot Talks Over Caller
**Symptom:** Overlap occurs
**Cause:** VAD not detecting speech properly
**Check:** Log shows `is_speech = False` during actual speech
**Fix:** Lower `vad_mode` (try mode 1 or 2 instead of 3)

### Bot Takes Too Long to Respond
**Symptom:** Long delay after caller finishes
**Cause:** Silence threshold too high
**Fix:** Reduce `silence_duration_ms` from 800ms to 500ms

## Future Enhancements

1. **Barge-In Detection** - Stop bot mid-sentence if caller interrupts urgently
2. **Adaptive Thresholds** - Adjust VAD sensitivity based on line noise
3. **Turn-Taking Signals** - Detect conversational cues ("um", "uh", rising intonation)
4. **Priority Messages** - Emergency messages skip silence wait
5. **Noise Cancellation** - Pre-process audio to improve VAD accuracy

## Code References

- **VAD Integration:** `/home/rom/sim7600_voice_bot.py:440-558`
- **Smart Playback:** `/home/rom/sim7600_voice_bot.py:560-643`
- **Conversation State:** `/home/rom/sim7600_voice_bot.py:91-99`
- **VAD Loading:** `/home/rom/sim7600_voice_bot.py:211-234`

## WebRTC VAD Migration (October 2025)

**Important:** This system now uses **WebRTC VAD** instead of Silero VAD.

### Why the Change?
- **150x faster startup** (<1ms vs 12+ seconds)
- **4x lower CPU usage** (1-2% vs 5-8%)
- **15x lower memory** (10MB vs 150MB)
- **Optimized for telephony** (designed for 8kHz PCM audio)
- **No heavy dependencies** (no PyTorch, ONNX, or CUDA)

### When to Use Silero VAD vs WebRTC VAD
- ✅ **Use WebRTC VAD**: Clean telephony audio (default, recommended)
- ❌ **Use Silero VAD**: Only if explicitly requested or dealing with very noisy audio

### Terminology Clarification
⚠️ **Always clarify when discussing VAD:**
- User says "VAD" or "vad silero" → **Ask: "Do you mean WebRTC VAD or Silero VAD?"**
- User might say "silero" out of habit when referring to our current WebRTC implementation
- **Default assumption**: WebRTC VAD (current system)

For complete details on the migration, see: `/home/rom/docs/WEBRTC_VAD_MIGRATION.md`
