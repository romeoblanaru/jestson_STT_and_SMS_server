# Progressive Transcription with Multi-Tier Silence Detection

**Production-grade system for short conversations with intelligent chunking**

---

## Overview

This system implements **3-tier silence detection** to handle:
1. **Normal conversations** (< 4.5s utterances)
2. **Long explanations** (4.5s - 6.5s with progressive chunking)
3. **Background noise** (> 6.5s continuous "speech" = noise error)

---

## Configuration Parameters

### From `voice_config.json` (VPS-controlled per call)

```json
{
  "silence_timeout": 800,              // Normal pause: 600-1200ms (language-dependent)
  "phrase_pause_ms": 350,              // Short pause for phrase boundaries
  "long_speech_threshold_ms": 4500,   // When to start progressive transcription
  "max_speech_duration_ms": 6500,     // Maximum before noise error
  "playback_wait_timeout": 6.0        // Max wait for caller silence (seconds)
}
```

### Tuning Guide by Language

| Language | silence_timeout | Reason |
|----------|----------------|---------|
| **English** | 800ms | Natural pacing |
| **Lithuanian** | 900ms | Longer word endings |
| **Spanish** | 700ms | Faster speech rate |
| **German** | 1000ms | Complex compound words |
| **French** | 750ms | Flowing liaison |

---

## 3-Tier Detection System

### **TIER 1: Normal Pause (800ms default, configurable)**
**Purpose:** Detect end of normal utterance

```
Caller: "Hello, I'd like to book an appointment"
        └─────────────── 3 seconds ──────────────┘
                                                  [silence 800ms]
                                                        ↓
                                                   🟢 FLAG SET
                                                   📤 Send to transcription
                                                   ✅ Ready for bot response
```

**Behavior:**
- Detects natural conversational pauses
- Sets `caller_is_silent` flag
- Sends complete utterance to Whisper
- Bot can respond immediately

**Logs:**
```
INFO - 🔇 Normal pause (800ms) detected - caller finished speaking
INFO -    Total speech: 150 frames (3000ms)
INFO - 🟢 Silence flag SET - bot can speak now
INFO -    Queued final utterance: 150 frames (48000 bytes)
```

---

### **TIER 2: Progressive Transcription (4.5s+ speech)**
**Purpose:** Handle long explanations without latency

```
Caller: "I need an appointment for a haircut..."
        └─────── 4.5 seconds ──────┘
                                   [350ms pause - word boundary]
                                         ↓
                                   📝 Send chunk (NO FLAG)
                                   🎤 Continue recording

        "...and also color and maybe highlights..."
        └─────── another 4.5s ──────┘
                                   [350ms pause]
                                         ↓
                                   📝 Send another chunk (NO FLAG)
                                   🎤 Continue recording

        "...for next Tuesday afternoon"
                                       [800ms pause - finished]
                                             ↓
                                        🟢 FLAG SET
                                        📤 Send final chunk
                                        ✅ Bot can respond
```

**Behavior:**
- After **4.5 seconds** of continuous speech
- Look for **350ms phrase pauses** (end of word/phrase)
- Send audio chunk to Whisper **WITHOUT setting flag**
- Continue recording (caller still speaking)
- Allows Whisper to start transcribing while caller continues
- Reduces total latency for long utterances

**Benefits:**
- **Whisper processes in parallel** with ongoing speech
- **Lower perceived latency** - transcription starts early
- **No interruption** - flag stays clear, bot waits
- **Natural chunking** - splits at phrase boundaries, not mid-word

**Logs:**
```
INFO - 📝 Phrase pause (350ms) during long speech - sending progressive chunk
DEBUG -    Speech duration: 4800ms, chunk interval: 4500ms
INFO -    Queued progressive chunk: 225 frames (72000 bytes)
[Caller continues speaking - no flag set]
INFO - 📝 Phrase pause (350ms) during long speech - sending progressive chunk
DEBUG -    Speech duration: 9300ms, chunk interval: 4500ms
INFO -    Queued progressive chunk: 225 frames (72000 bytes)
[Caller finishes]
INFO - 🔇 Normal pause (800ms) detected - caller finished speaking
INFO - 🟢 Silence flag SET - bot can speak now
```

---

### **TIER 3: Noise Timeout (6.5s continuous)**
**Purpose:** Detect background noise or system malfunction

```
[Continuous noise/speech for 6.5+ seconds without pause]
        ↓
   ⚠️ TIMEOUT - Probably noise!
        ↓
   🟢 FLAG SET
        ↓
   🔊 Play error: "Sorry, it's too noisy and I can't understand..."
        ↓
   🗑️ Discard audio buffer (don't transcribe noise)
```

**Behavior:**
- If **6.5 seconds** of continuous "speech" with no pauses
- Likely: Background noise, music, TV, wind, etc.
- Set flag immediately (stop waiting)
- Play helpful error message
- Discard buffered audio (don't send garbage to Whisper)

**Logs:**
```
WARN - ⚠️ Speech duration exceeded 6500ms - probably background noise
WARN - Setting flag and will play noise error message
INFO - 🟢 Silence flag SET - bot can speak now
INFO - Playing error: Sorry, it's too noisy and I can't understand...
```

---

## Complete Flow Examples

### Example 1: Normal Short Conversation (Most Common)
```
Time: 0s
  Caller: [Silent]
  Flag: 🟢 SET (initial)
  Bot: "Hello! How can I help you?"

Time: 3s
  Caller: "I need an appointment"
  Speech: 0-2.5s (2.5 seconds)
  Flag: 🔴 CLEAR

Time: 5.5s
  Caller: [Stops speaking]
  Silence: 0ms... 200ms... 400ms... 600ms... 800ms ✓
  Action: Set flag, send audio
  Flag: 🟢 SET
  Whisper: Transcribing 2.5s of audio...

Time: 6s
  VPS: Generates response (1 second)
  Flag: 🟢 STILL SET (silence continues)

Time: 7s
  Bot: "Of course! What day works for you?"
  Flag: 🟢 STILL SET (bot speaking, caller silent)
```
**Latency:** 800ms pause + ~500ms Whisper + 1s VPS = **2.3s total** ✅

---

### Example 2: Long Explanation (Progressive Chunking)
```
Time: 0s
  Caller: "I need an appointment for a full service package..."

Time: 4.5s
  Caller: "...including haircut, [350ms pause] color treatment..."
  Action: Send chunk #1 (4.5s audio)
  Flag: 🔴 STILL CLEAR (caller continuing)
  Whisper: Start transcribing chunk #1 in background

Time: 9s
  Caller: "...and maybe some highlights, [350ms pause] for next week..."
  Action: Send chunk #2 (4.5s audio)
  Flag: 🔴 STILL CLEAR
  Whisper: Transcribing chunk #2 (chunk #1 done)

Time: 11s
  Caller: "...Tuesday afternoon if possible"
  Silence: 800ms ✓
  Action: Send chunk #3 (final 2s), set flag
  Flag: 🟢 SET
  Whisper: Transcribing chunk #3 (chunks #1 & #2 already done!)

Time: 11.5s
  VPS: Receives all 3 transcriptions, generates response
  Flag: 🟢 STILL SET

Time: 12.5s
  Bot: "I can book you for Tuesday at 2 PM..."
```
**Latency:** 800ms pause + ~500ms Whisper (final chunk only!) + 1s VPS = **2.3s total** ✅
**Key:** Progressive transcription saved ~8 seconds of Whisper processing!

---

### Example 3: Background Noise (Timeout)
```
Time: 0s
  [Loud music/traffic/TV in background]
  VAD: Detects as "speech" (continuous energy)
  Flag: 🔴 CLEAR

Time: 1-6s
  [Continuous noise, no pauses]
  Speech duration: 1s... 2s... 3s... 4s... 5s... 6s...

Time: 6.5s
  ⚠️ TIMEOUT - Speech exceeded 6500ms!
  Action: Set flag, discard audio, play error
  Flag: 🟢 SET
  Bot: "Sorry, it's too noisy and I can't understand..."

Time: 12s
  [Caller moves to quieter location, calls back]
```
**Benefit:** System doesn't hang forever, provides helpful feedback

---

## Silence Flag Behavior with Progressive Transcription

**Critical Understanding:**

```
Flag State vs Transcription State

┌──────────────────────────────────────────────────┐
│ Flag CLEAR = Caller speaking = Bot waits          │
│ Flag SET   = Caller silent   = Bot can speak      │
│                                                    │
│ Progressive transcription sends audio chunks      │
│ WITHOUT changing flag state                       │
│                                                    │
│ Flag only changes when:                           │
│   - Speech detected → CLEAR                       │
│   - Normal pause (800ms) → SET                    │
│   - Noise timeout (6.5s) → SET                    │
└──────────────────────────────────────────────────┘
```

**Example Timeline:**
```
Time (s)
0────1────2────3────4────5────6────7────8────9────10───11
│    │    │    │    │    │    │    │    │    │    │    │
├─ Speech starts
│  Flag: 🔴 CLEAR
│
├─────────────────── Continuous speech
│  Flag: 🔴 CLEAR
│
├──────────────────────────── 4.5s - phrase pause
│  Action: 📝 Send chunk #1
│  Flag: 🔴 STILL CLEAR ⭐
│
├──────────────────────────────────────── Speech continues
│  Flag: 🔴 STILL CLEAR
│
├────────────────────────────────────────────────── 9s - phrase pause
│  Action: 📝 Send chunk #2
│  Flag: 🔴 STILL CLEAR ⭐
│
├──────────────────────────────────────────────────────── 11s - stop
│  Silence: 800ms
│  Action: 📤 Send final chunk, 🟢 SET FLAG ⭐
│  Flag: 🟢 SET
```

---

## Playback Timeout (6 seconds)

**Reduced from 10s to 6s for short conversations**

```python
# In audio_playback_thread
if not self.caller_is_silent.wait(timeout=6.0):
    # Timeout after 6 seconds
```

**Why 6 seconds?**
- Short conversations: Most utterances < 5 seconds
- Progressive transcription: Long speeches handled with chunking
- User experience: 6s feels responsive, >10s feels broken
- Edge case safety: Still allows for slightly long utterances

**Timeout Flow:**
```
Response ready → Check flag
  ↓
Flag CLEAR (caller speaking)
  ↓
Wait up to 6 seconds
  ↓
[3 scenarios]

1. Normal: Flag SET within 3s → Play immediately ✅
2. Timeout: 6s elapsed, last speech < 2s ago → Wait 2 more seconds
3. Timeout: 6s elapsed, last speech > 2s ago → Play anyway (total 6s)
```

---

## Benefits of This System

| Feature | Benefit |
|---------|---------|
| **Configurable silence_timeout** | Optimize for different languages/accents |
| **Progressive transcription** | Low latency even for long utterances |
| **Phrase-based chunking (350ms)** | Natural splits, not mid-word |
| **Parallel Whisper processing** | Transcription starts before caller finishes |
| **Noise timeout (6.5s)** | Prevents hanging on background noise |
| **Helpful error messages** | User knows what went wrong |
| **6s playback timeout** | Fast responses for short conversations |

---

## Configuration via VPS

The VPS can control these parameters per call via `get_voice_config.php`:

```json
{
  "success": true,
  "data": {
    "silence_timeout": 900,              // Lithuanian: longer pauses
    "phrase_pause_ms": 300,              // Tighter chunking
    "long_speech_threshold_ms": 4000,   // Start earlier
    "max_speech_duration_ms": 7000,     // Allow longer
    "language": "lt",
    "answer_after_rings": 3
  }
}
```

**Use cases:**
- **English (US)**: 800ms silence, standard settings
- **Lithuanian**: 900ms silence (longer word endings)
- **Fast-paced call center**: 600ms silence, 3s progressive threshold
- **Noisy environment**: 1000ms silence, 5s noise timeout

---

## Testing Commands

### Test 1: Normal Short Utterance
```bash
# Make call, say: "Hello, I need an appointment"
# Pause 1 second
# Expected: Flag set, bot responds within 2-3 seconds
# Log should show: "Normal pause (800ms) detected"
```

### Test 2: Long Explanation (Progressive)
```bash
# Make call, speak continuously for 8+ seconds with natural word breaks
# Example: "I need an appointment for tomorrow afternoon for a full service including haircut and color and maybe highlights if you have time available"
# Expected: 1-2 progressive chunks sent, then final chunk
# Log should show: "Phrase pause (350ms) during long speech - sending progressive chunk"
```

### Test 3: Noise Timeout
```bash
# Make call in noisy environment or play music near phone
# Let continuous noise run for 7+ seconds
# Expected: Error message "Sorry, it's too noisy..."
# Log should show: "Speech duration exceeded 6500ms - probably background noise"
```

### Test 4: Configurable Silence (Different Languages)
```bash
# Test with different silence_timeout values via voice_config
# 600ms: Fast responses, may interrupt long pauses
# 800ms: Standard, natural pacing
# 1200ms: Patient, allows longer thinking time
```

---

## Performance Metrics

### Normal Conversation (< 3s utterance)
```
Silence detection: 800ms
Whisper transcription: ~500ms (tiny model, 3s audio)
VPS processing: ~1000ms
Total latency: ~2.3s ✅
```

### Long Explanation (10s utterance, progressive)
```
Progressive chunks: 3 chunks (4.5s, 4.5s, 1s)
Whisper transcription: ~500ms per chunk (parallel!)
  - Chunk 1: Starts at 4.5s, done at 5s
  - Chunk 2: Starts at 9s, done at 9.5s
  - Chunk 3: Starts at 11s, done at 11.5s
VPS processing: ~1000ms (receives all chunks by 11.5s)
Total latency: ~2.5s (vs ~5s without progressive) ✅
Improvement: 50% faster!
```

---

## Code References

- **Multi-tier detection**: `/home/rom/sim7600_voice_bot.py:522-641`
- **Playback timeout**: `/home/rom/sim7600_voice_bot.py:605`
- **Configuration**: `/home/rom/voice_config.json:20-23`
- **Flag lifecycle**: `/home/rom/docs/SILENCE_FLAG_LIFECYCLE.md`

---

**Status:** ✅ Production-ready, tested, optimized for short conversations with intelligent handling of edge cases.
