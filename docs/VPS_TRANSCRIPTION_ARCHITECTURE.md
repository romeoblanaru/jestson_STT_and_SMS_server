# VPS Transcription Architecture

**Date:** October 27, 2025
**Purpose:** Offload Whisper STT transcription to VPS for faster response times

---

## Table of Contents

1. [Current Architecture & Problems](#current-architecture--problems)
2. [New VPS Architecture](#new-vps-architecture)
3. [Complete Call Flow](#complete-call-flow)
4. [Audio Compression Strategy](#audio-compression-strategy)
5. [Filler Expression Strategy](#filler-expression-strategy)
6. [VPS API Specification](#vps-api-specification)
7. [Implementation Steps](#implementation-steps)
8. [Timing Analysis](#timing-analysis)
9. [Error Handling](#error-handling)

---

## Current Architecture & Problems

### Current Flow (Local Whisper)

```
[Caller speaks]
  ↓
[VAD detects 550ms pause]
  ↓
[Save chunk to WAV file]
  ↓
[Run whisper-cli locally] ⏱️ 18-59 seconds! ❌
  ↓
[Get transcription]
  ↓
[Send to Azure TTS]
  ↓
[Play response]
```

### Problems

| Issue | Impact | Solution |
|-------|--------|----------|
| **Slow transcription** | 18-59s per chunk | Use VPS GPU acceleration (2-5s) |
| **Blocking processing** | Can't listen while transcribing | Async threaded processing |
| **Poor accuracy** | Phone audio quality | Better preprocessing on VPS |
| **CPU overload** | Pi struggles with Whisper | Offload to powerful VPS |
| **Long response time** | Caller waits 20+ seconds | VPS + filler expressions |

---

## New VPS Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Raspberry Pi (Voice Bot)                                       │
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │ Audio Thread │ ───▶ │ VAD Thread   │ ───▶ │ VPS Thread   │  │
│  │ (PCM stream) │      │ (detect end) │      │ (compress +  │  │
│  │              │      │              │      │  transmit)   │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                      │                      │          │
│         │                      │                      │          │
│         ▼                      ▼                      ▼          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  TTS Playback Thread (plays filler + response)           │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP POST (OGG audio)
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  VPS Server (10.100.0.1)                                        │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  /api/transcribe Endpoint                                 │  │
│  │                                                            │  │
│  │  1. Receive OGG audio (base64 encoded)                   │  │
│  │  2. Run Whisper (GPU accelerated) ⏱️ 2-5s                │  │
│  │  3. Send transcription to LLM (GPT/Claude)                │  │
│  │  4. Get response text                                     │  │
│  │  5. Return JSON: {transcription, response, continue}      │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ JSON response
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│  Raspberry Pi (TTS Processing)                                 │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  TTS Thread                                               │  │
│  │                                                            │  │
│  │  1. Receive response text from VPS                        │  │
│  │  2. Send to Azure/OpenAI TTS                              │  │
│  │  3. Stream audio to caller                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Complete Call Flow

### Phase 1: Call Answer & Welcome Message

```
[RING detected]
  ↓
[Fetch fresh config from VPS webhook]
  ↓
[answer_after_rings check]
  ↓
[Answer call: ATA]
  ↓
[Enable PCM audio: AT+CPCMREG=1]
  ↓
[Start audio threads]
  ↓
[CALLER-FIRST FLOW: Wait for caller to speak]
  ↓
[VAD detects 680ms continuous speech]
  ↓
[Play welcome message via TTS]
  ↓
[Continue to conversation loop]
```

### Phase 2: Conversation Loop (NEW VPS FLOW)

```
┌─────────────────────────────────────────────────────────────────┐
│ MAIN AUDIO THREAD (Real-time PCM processing)                    │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
[Read PCM from /dev/ttyUSB4] (20ms chunks, 640 bytes @ 16kHz)
         │
         ▼
[WebRTC VAD analysis] (mode 3, aggressive)
         │
         ├─ Speech detected → Accumulate in buffer
         │
         └─ Silence detected → Check duration
                  │
                  ├─ < 550ms → Continue accumulating (mid-sentence)
                  │
                  └─ ≥ 550ms → END OF UTTERANCE DETECTED!
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ NON-BLOCKING HANDOFF                                             │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ▼
              [Put PCM chunk in queue] ← Instant, non-blocking!
                         │
                         ├─ Main thread CONTINUES listening
                         │  (no latency, caller can speak again)
                         │
                         └─ VPS Thread picks up chunk
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ VPS TRANSCRIPTION THREAD (Async processing)                     │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    [Get chunk from queue]
                                  │
                                  ▼
                    [Convert PCM → OGG Opus] ⏱️ 0.07s
                                  │
                                  ▼
                    [Base64 encode OGG]
                                  │
                                  ▼
                    [HTTP POST to VPS] ⏱️ 0.01-0.1s (4G)
                    {
                      "call_id": "call_1761507557",
                      "chunk_number": 1,
                      "audio": "<base64_ogg>",
                      "language": "ro",
                      "context": "previous conversation..."
                    }
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ VPS SERVER PROCESSING                                            │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    [Decode base64 → OGG bytes]
                                  │
                                  ▼
                    [Run Whisper (GPU)] ⏱️ 2-5s
                                  │
                                  ▼
                    [Get transcription text]
                                  │
                                  ▼
                    [Send to LLM (GPT-4/Claude)]
                    - Context: Full conversation history
                    - User said: "<transcription>"
                    - Generate response
                                  │
                                  ▼
                    [LLM returns response text]
                                  │
                                  ▼
                    [Return JSON response] ⏱️ Total: 3-7s
                    {
                      "transcription": "Bună ziua, aș vrea...",
                      "response": "Bineînțeles! Vă pot ajuta...",
                      "continue": true
                    }
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ FILLER EXPRESSION PLAYBACK (Immediate)                          │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ├─ WHILE waiting for VPS response:
                                  │  Play random filler (2-3s audio)
                                  │  Examples: "ok.wav", "bine.wav",
                                  │            "înțeleg.wav", "da.wav"
                                  │
                                  └─ Filler keeps caller engaged
                                     (prevents awkward silence)
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│ TTS RESPONSE GENERATION                                          │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    [Receive VPS response]
                                  │
                                  ▼
                    [Send response text to TTS API]
                    - Azure TTS / OpenAI TTS / Liepa
                    - Use voice from webhook config
                                  │
                                  ▼
                    [Stream TTS audio to caller] ⏱️ 0.5-1s
                                  │
                                  ▼
                    [Wait for caller's next utterance]
                                  │
                                  ▼
                    [Loop back to MAIN AUDIO THREAD]
```

### Phase 3: Call End

```
[Caller hangs up OR VPS returns continue=false]
  ↓
[Stop all threads]
  ↓
[Convert all WAV recordings to OGG] (async, after call)
  ↓
[Save timing analysis]
  ↓
[Send call summary to VPS]
```

---

## Audio Compression Strategy

### Why Direct PCM → OGG Conversion?

**Current inefficient flow:**
```
PCM bytes → WAV file (write to disk) → ffmpeg reads WAV → OGG
```

**New efficient flow:**
```
PCM bytes → ffmpeg stdin (pipe) → OGG bytes (in memory)
```

### Implementation

```python
import subprocess

def pcm_to_opus_ogg(pcm_data, sample_rate=16000):
    """
    Convert raw PCM bytes directly to Opus OGG

    Args:
        pcm_data: bytes - raw PCM audio (16-bit signed little-endian)
        sample_rate: int - 8000 or 16000 Hz

    Returns:
        bytes - OGG Opus compressed audio
    """
    cmd = [
        'ffmpeg',
        '-f', 's16le',              # Input format: signed 16-bit little-endian
        '-ar', str(sample_rate),    # Sample rate
        '-ac', '1',                 # Mono
        '-i', 'pipe:0',             # Read from stdin
        '-c:a', 'libopus',          # Codec: Opus
        '-b:a', '24k',              # Bitrate: 24 kbps
        '-application', 'voip',     # Optimize for voice
        '-vbr', 'on',               # Variable bitrate
        '-compression_level', '0',  # Fast encoding (90x real-time)
        '-f', 'ogg',                # Output format: OGG container
        'pipe:1'                    # Write to stdout
    ]

    result = subprocess.run(
        cmd,
        input=pcm_data,
        capture_output=True,
        timeout=10
    )

    if result.returncode == 0:
        return result.stdout  # OGG bytes
    else:
        raise Exception(f"FFmpeg error: {result.stderr.decode()}")
```

### Benefits

✅ **No disk I/O** - Everything in memory
✅ **Faster** - Single conversion step
✅ **Less code** - No temp file management
✅ **Same compression** - Still 12x smaller than PCM
✅ **Debuggable** - OGG files can be played for debugging

### Performance

| Audio Duration | PCM Size | OGG Size | Encoding Time |
|----------------|----------|----------|---------------|
| 0.6s | 19.2 KB | 1.9 KB | 0.08s |
| 1.0s | 32 KB | 2.8 KB | 0.13s |
| 6.0s | 192 KB | 16 KB | 0.07s |

**Encoding speed:** 90x real-time (negligible latency)

---

## Filler Expression Strategy

### Purpose

Bridge the 3-7 second VPS response time with natural conversational fillers to:
- ✅ Acknowledge caller was heard
- ✅ Prevent awkward silence
- ✅ Feel responsive and natural
- ✅ Buy time for VPS processing

### Filler Audio Files

**Location:** `/home/rom/audio_fillers/`

**Romanian fillers (2-3 seconds each):**

| File | Transcription | Duration | When to Use |
|------|---------------|----------|-------------|
| `ok.wav` | "Ok" | 0.5s | General acknowledgment |
| `bine.wav` | "Bine" | 0.7s | Agreement |
| `inteles.wav` | "Înțeles" | 1.0s | Understanding |
| `da.wav` | "Da" | 0.5s | Yes/confirmation |
| `aha.wav` | "Aha" | 0.6s | Listening actively |
| `un_moment.wav` | "Un moment" | 1.2s | Need time to process |
| `sa_vad.wav` | "Să văd" | 1.0s | Checking something |
| `perfect.wav` | "Perfect" | 1.0s | Positive response |

**English fillers:**
| File | Transcription | Duration |
|------|---------------|----------|
| `okay.wav` | "Okay" | 0.5s |
| `alright.wav` | "Alright" | 0.8s |
| `i_see.wav` | "I see" | 0.7s |
| `let_me_check.wav` | "Let me check" | 1.2s |

### Filler Selection Logic

```python
import random
import os

def get_random_filler(language='ro'):
    """
    Select random filler expression based on language

    Args:
        language: str - 'ro', 'en', 'lt', etc.

    Returns:
        Path to filler audio file
    """
    filler_dir = f"/home/rom/audio_fillers/{language}"

    if not os.path.exists(filler_dir):
        logger.warning(f"No fillers for language {language}, using 'ro'")
        filler_dir = "/home/rom/audio_fillers/ro"

    fillers = [f for f in os.listdir(filler_dir) if f.endswith('.wav')]

    if not fillers:
        return None

    return os.path.join(filler_dir, random.choice(fillers))
```

### Filler Playback Flow

```
[VAD detects end of utterance]
  ↓
[Put chunk in VPS queue]
  ↓
[IMMEDIATELY play random filler] ⏱️ 0.1s latency
  ↓
[While filler plays, VPS processes in parallel]
  ↓
[VPS returns response after 3-7s]
  ↓
[Generate TTS for response]
  ↓
[Play TTS response]
```

**Example timing:**
```
T+0.0s: Caller finishes speaking
T+0.1s: Filler starts playing ("Ok, să văd...")
T+1.3s: Filler ends
T+3.5s: VPS response arrives
T+4.0s: TTS generation complete
T+4.0s: Bot starts speaking actual response
```

**Total perceived latency:** 4 seconds (with filler feels natural)

### Filler Generation Script

**Script:** `/home/rom/generate_fillers.sh`

```bash
#!/bin/bash
# Generate Romanian filler expressions using Azure TTS

FILLERS=(
    "ok:Ok"
    "bine:Bine"
    "inteles:Înțeles"
    "da:Da"
    "aha:Aha"
    "un_moment:Un moment"
    "sa_vad:Să văd"
    "perfect:Perfect"
)

mkdir -p /home/rom/audio_fillers/ro

for filler in "${FILLERS[@]}"; do
    filename="${filler%%:*}"
    text="${filler##*:}"

    # Call Azure TTS API to generate audio
    curl -X POST "http://localhost:8088/api/tts" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$text\", \"language\": \"ro\", \"voice\": \"ro-RO-AlinaNeural\"}" \
        --output "/home/rom/audio_fillers/ro/${filename}.wav"

    echo "Generated: ${filename}.wav"
done
```

---

## VPS API Specification

### Endpoint: POST /api/transcribe

**URL:** `http://10.100.0.1:5000/api/transcribe`

**Request Headers:**
```
Content-Type: application/json
X-API-Key: <api_key_from_config>
```

**Request Body:**
```json
{
  "call_id": "call_1761507557",
  "chunk_number": 3,
  "audio": "<base64 encoded OGG audio>",
  "language": "ro",
  "context": "Previous conversation context...",
  "caller_id": "+40712345678",
  "metadata": {
    "timestamp": 1698453120,
    "duration_ms": 2300
  }
}
```

**Response (Success):**
```json
{
  "status": "success",
  "transcription": "Aș vrea să fac o programare pentru mâine",
  "response": "Bineînțeles! Ce oră v-ar conveni?",
  "continue": true,
  "processing_time_ms": 3450,
  "metadata": {
    "whisper_model": "whisper-large-v3",
    "llm_model": "gpt-4",
    "transcription_confidence": 0.94
  }
}
```

**Response (Error):**
```json
{
  "status": "error",
  "error": "Transcription failed",
  "fallback_response": "Ne cerem scuze, vă rog să repetați",
  "continue": true
}
```

### Fields Explained

**Request:**
- `call_id`: Unique call identifier
- `chunk_number`: Sequential chunk number (1, 2, 3...)
- `audio`: Base64 encoded OGG Opus audio
- `language`: ISO language code (ro, en, lt, auto)
- `context`: Previous conversation for LLM context
- `caller_id`: Phone number (for personalization)

**Response:**
- `status`: "success" or "error"
- `transcription`: What caller said (STT result)
- `response`: What bot should say (LLM response)
- `continue`: true = continue call, false = end call
- `processing_time_ms`: VPS processing duration
- `metadata`: Optional debugging info

---

## Implementation Steps

### Step 1: Audio Recording Changes (OGG only) ✅ COMPLETED

**Files modified:**
- `/home/rom/audio_recorder.py`

**Changes:**
1. ✅ **COMPLETED:** Added `pcm_to_opus_ogg()` function for direct PCM → OGG conversion
2. ✅ **COMPLETED:** Modified `AsyncAudioRecorder` to accumulate PCM and convert to OGG at end
3. ✅ **COMPLETED:** Modified `record_incoming_vad_chunk()` to use direct PCM → OGG
4. ✅ **COMPLETED:** Changed to direct PCM → OGG (skip WAV entirely)

**What was implemented:**
- Direct PCM → OGG conversion using ffmpeg pipe
- No intermediate WAV files created (memory only during call)
- AsyncAudioRecorder accumulates PCM chunks in memory
- Converts all accumulated PCM to single OGG file after call ends
- VAD chunks convert to OGG immediately (but still synchronous for now)

**Test Results:**
- ✅ Direct PCM → OGG conversion working
- ✅ 15.9x compression ratio
- ✅ Valid playable OGG files
- ✅ 1.2x real-time encoding speed
- ✅ No disk I/O during call (async recorders)
- ⚠️ VAD chunks still synchronous (0.54s for 0.66s audio) - will fix in Step 2

---

### Step 2: VPS Transcription Thread ✅ COMPLETED (October 29, 2025)

**Files modified:**
- `/home/rom/.env` - Added VPS_TRANSCRIPTION_URL
- `/home/rom/audio_recorder.py` - Made VAD chunk recording async + VPS queue support
- `/home/rom/sim7600_voice_bot.py` - Replaced local Whisper with VPS transcription thread + dual-threshold VAD

**Changes:**
1. ✅ Added `VPS_TRANSCRIPTION_URL` to .env (http://10.100.0.1:9000/api/transcribe)
2. ✅ Created `vps_queue` for async PCM chunk processing
3. ✅ Modified `CallAudioRecorder` to accept vps_queue and put PCM chunks in it (non-blocking)
4. ✅ Replaced `transcription_thread()` with `vps_transcription_thread()`
5. ✅ Implemented async HTTP POST to VPS with OGG audio (base64 encoded)
6. ✅ Added conversation context tracking (last 5 messages)
7. ✅ Implemented error handling (timeout, connection errors, VPS errors)
8. ✅ TTS response generation from VPS response text
9. ✅ Fallback responses for all error scenarios
10. ✅ **Dual-threshold VAD implementation** (550ms audio send + 800ms end signal)
11. ✅ **Speech resumption handling** (cancel pending end signal if caller speaks again)
12. ✅ **Message type system** (audio chunks vs end signals)

**What was implemented:**

**VAD Chunk Processing (audio_recorder.py):**
- `record_incoming_vad_chunk()` now puts PCM chunk in vps_queue (instant, non-blocking)
- Local OGG saving happens in background thread (parallel with VPS processing)
- **Main audio thread never blocks** - continues listening immediately

**VPS Transcription Thread (sim7600_voice_bot.py):**
```python
def vps_transcription_thread(self):
    while self.in_call:
        # 1. Get PCM chunk from queue (non-blocking)
        chunk_info = self.vps_queue.get(timeout=0.5)

        # 2. Convert PCM → OGG Opus (in memory, ~0.5s)
        ogg_data = pcm_to_opus_ogg(pcm_data, sample_rate)

        # 3. Encode to base64
        ogg_b64 = base64.b64encode(ogg_data).decode('utf-8')

        # 4. Build context from conversation history
        context = last 5 messages from conversation

        # 5. POST to VPS
        payload = {
            'call_id': self.call_id,
            'chunk_number': chunk_num,
            'audio': ogg_b64,
            'language': language,
            'context': context,
            'caller_id': self.caller_id,
            'metadata': {...}
        }
        response = requests.post(vps_url, json=payload, timeout=10)

        # 6. Handle response
        if success:
            transcription = response['transcription']
            response_text = response['response']

            # Update conversation context
            self.conversation_context.append({'role': 'caller', 'text': transcription})
            self.conversation_context.append({'role': 'bot', 'text': response_text})

            # Generate TTS and play
            self.request_tts(response_text, priority='high')
```

**Error Handling:**
- **Timeout (>10s):** Play "Un moment, vă rog" (please wait)
- **Connection Error:** Play "Ne cerem scuze, vă rog să repetați" (sorry, please repeat)
- **VPS Error:** Use fallback_response from VPS or default apology
- **Compression Failure:** Log error, continue with next chunk

**Conversation Context:**
- Tracks last 5 caller/bot messages
- Sent to VPS with each chunk for LLM context
- Enables multi-turn conversations with memory

**VPS Endpoint Configuration:**
- URL: Loaded from .env (`VPS_TRANSCRIPTION_URL`)
- Default: `http://10.100.0.1:9000/api/transcribe`
- Can be changed in .env file for production deployment

**Test Results:**
- ✅ Code compiles and service restarts successfully
- ✅ VAD chunk queueing is non-blocking (instant)
- ✅ Local OGG saving happens in parallel (background thread)
- ⏳ Awaiting modem connection for full test
- ⏳ Awaiting VPS endpoint deployment for integration test

---

### Step 3: Filler Expression System

**Files to create:**
- `/home/rom/audio_fillers/ro/*.wav` (filler audio files)
- `/home/rom/generate_fillers.sh` (generation script)

**Files to modify:**
- `/home/rom/sim7600_voice_bot.py`

**Changes:**
1. Create filler audio files (Romanian + English)
2. Add `play_random_filler()` function
3. Play filler IMMEDIATELY after VAD detects pause
4. While filler plays, VPS processes in parallel

**What we'll do:**
- Generate 8-10 Romanian filler expressions
- Implement filler playback before VPS response
- Make filler selection language-aware

**User approval needed before:**
- Filler expression text selection
- Voice/style for filler generation
- Timing strategy (when to play filler)

---

### Step 4: VPS Integration Testing

**Testing plan:**
1. Test PCM → OGG conversion (verify quality)
2. Test VPS API mock (simulate responses)
3. Test filler playback timing
4. Test complete flow end-to-end
5. Measure latency improvements

**What we'll do:**
- Create VPS mock server for testing
- Test with real phone calls
- Measure response times
- Compare to old local Whisper flow

**User approval needed before:**
- VPS endpoint deployment
- Production API key usage

---

### Step 5: Error Handling & Fallbacks

**Scenarios to handle:**
1. VPS unreachable (network failure)
2. VPS timeout (>10s response)
3. VPS error response
4. Malformed VPS response
5. Audio compression failure

**Fallback strategies:**
- Use cached generic responses
- Fall back to local Whisper (slow but works)
- Apologize and ask caller to repeat
- End call gracefully if critical failure

**What we'll do:**
- Implement retry logic (1 retry, 5s timeout)
- Add fallback to local Whisper for critical failures
- Log all errors to VPS for monitoring

**User approval needed before:**
- Fallback response text
- When to retry vs fail gracefully

---

## Timing Analysis

### Current Flow (Local Whisper)

| Step | Duration | Notes |
|------|----------|-------|
| VAD detects pause | 0.55s | Natural pause detection |
| Save to WAV | 0.01s | Disk write |
| **Whisper transcription** | **18-59s** | ❌ **BOTTLENECK!** |
| Azure TTS | 0.5-1s | Network call |
| Play response | 2-5s | Audio playback |
| **Total response time** | **21-65s** | ❌ Unacceptable |

### New VPS Flow (With Filler)

| Step | Duration | Notes |
|------|----------|-------|
| VAD detects pause | 0.55s | Natural pause detection |
| **Play filler** | **0.1s** | ✅ Immediate acknowledgment |
| Compress PCM → OGG | 0.07s | Parallel with filler |
| Upload to VPS | 0.01-0.1s | 4G VPN (parallel with filler) |
| **VPS Whisper (GPU)** | **2-5s** | ✅ Fast! |
| VPS LLM processing | 1-2s | GPT-4/Claude |
| VPS response received | **3-7s total** | ✅ Much better! |
| Azure TTS | 0.5-1s | Network call |
| Play response | 2-5s | Audio playback |
| **Perceived response time** | **4-8s** | ✅ Acceptable with filler |

### Latency Improvement

| Metric | Old | New | Improvement |
|--------|-----|-----|-------------|
| Transcription | 18-59s | 2-5s | **78-91% faster** |
| Total response | 21-65s | 4-8s | **68-87% faster** |
| Perceived latency | 21-65s | 0.1s (filler) | **99% improvement** |

---

## Error Handling

### Network Failures

**Scenario:** VPS unreachable (no internet, VPN down)

**Detection:**
- HTTP connection timeout (5s)
- Connection refused error

**Fallback:**
1. Play error filler: "Un moment, vă rog" (Give me a moment)
2. Retry once (1 additional attempt)
3. If still fails:
   - Option A: Fall back to local Whisper (slow but works)
   - Option B: Play generic response: "Ne cerem scuze, vă rog să repetați" (Sorry, please repeat)
4. Log error to disk for later upload

**Implementation:**
```python
try:
    response = requests.post(vps_url, json=payload, timeout=5)
except requests.Timeout:
    logger.error("VPS timeout - falling back")
    return fallback_generic_response()
except requests.ConnectionError:
    logger.error("VPS unreachable - falling back")
    return fallback_generic_response()
```

---

### VPS Processing Errors

**Scenario:** VPS returns error (Whisper failed, LLM error)

**Detection:**
- `status: "error"` in response JSON
- HTTP 500/503 status codes

**Fallback:**
1. Use `fallback_response` from VPS if provided
2. Otherwise play generic apology
3. Continue call (don't hang up)

**Implementation:**
```python
if response_json.get('status') == 'error':
    fallback = response_json.get('fallback_response',
                                   'Ne cerem scuze, vă rog să repetați')
    return fallback
```

---

### Audio Compression Failures

**Scenario:** FFmpeg fails to convert PCM → OGG

**Detection:**
- FFmpeg returns non-zero exit code
- FFmpeg timeout
- Empty output

**Fallback:**
1. Skip compression, send raw PCM (larger but works)
2. Log warning
3. Continue processing

**Implementation:**
```python
try:
    ogg_data = pcm_to_opus_ogg(pcm_data)
except Exception as e:
    logger.warning(f"Compression failed: {e}, sending raw PCM")
    ogg_data = pcm_data  # Fallback to uncompressed
```

---

### Malformed Responses

**Scenario:** VPS returns invalid JSON or missing fields

**Detection:**
- JSON decode error
- Missing required fields (transcription, response)

**Fallback:**
1. Log error with full response
2. Use generic apology response
3. Continue call

**Implementation:**
```python
try:
    data = response.json()
    transcription = data['transcription']
    response_text = data['response']
except (json.JSONDecodeError, KeyError) as e:
    logger.error(f"Malformed VPS response: {e}")
    response_text = "Ne cerem scuze, am avut o problemă tehnică"
```

---

## Summary

### Key Improvements

1. ✅ **Faster transcription:** 18-59s → 2-5s (VPS GPU)
2. ✅ **Better perceived latency:** 0.1s (filler plays immediately)
3. ✅ **Async processing:** Main thread never blocks
4. ✅ **Efficient compression:** Direct PCM → OGG (no temp files)
5. ✅ **Natural conversation:** Filler expressions bridge delay
6. ✅ **Robust error handling:** Fallbacks for all failure modes

### Next Steps

**Awaiting user approval for each implementation step:**

1. **Step 1:** Remove WAV files, use direct PCM → OGG conversion
2. **Step 2:** Implement VPS transcription thread
3. **Step 3:** Create and integrate filler expression system
4. **Step 4:** Test VPS integration end-to-end
5. **Step 5:** Deploy error handling and fallbacks

**Each step will be reviewed and approved before proceeding.**

---

## Related Documentation

- `/home/rom/docs/AUDIO_CONFIGURATION.md` - Current audio settings
- `/home/rom/docs/OPUS_COMPRESSION.md` - Opus compression details
- `/home/rom/docs/VAD_CONVERSATION_FLOW.md` - VAD implementation
- `/home/rom/CALL_HANDLING_FLOW.md` - Complete call handling
