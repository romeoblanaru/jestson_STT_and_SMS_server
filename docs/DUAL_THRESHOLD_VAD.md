# Dual-Threshold VAD with Progressive VPS Transcription

**Date:** October 27, 2025
**Status:** ✅ **IMPLEMENTATION COMPLETE** (October 29, 2025)
**Purpose:** Send audio chunks early to VPS for parallel Whisper processing, then signal sentence completion

---

## ✅ Implementation Status

**Raspberry Pi Side:** ✅ Complete
- Dual-threshold VAD detection implemented in `/home/rom/sim7600_voice_bot.py:996-1077`
- Speech resumption handling added (lines 907-911)
- VPS queue messages with both audio and end signals
- Service tested and restarted successfully

**VPS Side:** ⏳ Pending
- Need to implement `/api/transcribe` endpoint at `http://10.100.0.1:9000/api/transcribe`
- Must handle state management for accumulating chunks
- Must process both audio chunks and end signals
- Must return LLM responses

---

## Table of Contents

1. [Overview](#overview)
2. [The Problem](#the-problem)
3. [The Solution](#the-solution)
4. [Complete Flow](#complete-flow)
5. [Message Types](#message-types)
6. [VPS API Specification](#vps-api-specification)
7. [Implementation Details](#implementation-details)
8. [Timing Analysis](#timing-analysis)
9. [Error Handling](#error-handling)
10. [Testing](#testing)

---

## Overview

**Dual-threshold VAD system sends audio to VPS in two stages:**

1. **First threshold (550ms silence):** Send audio chunk → VPS starts Whisper
2. **Second threshold (800ms silence):** Send end signal → VPS processes through LLM

**Key benefit:** Whisper transcription runs **in parallel** with waiting for sentence completion = **1.2 seconds saved per utterance!**

---

## The Problem

### Single Threshold Approach

Current system waits for full 800ms before sending anything:

```
Caller speaks: "Bună ziua"
  ↓
[Waits 800ms in silence]
  ↓
Sends audio to VPS
  ↓
VPS runs Whisper (2s)
  ↓
VPS runs LLM (1s)
  ↓
Bot responds

Total time from end of speech: 3.8 seconds
```

**Problems:**
- ❌ 800ms wasted waiting before sending
- ❌ Whisper can't start until 800ms passes
- ❌ Sequential processing (wait → transcribe → LLM)

---

## The Solution

### Dual-Threshold Approach

Send audio early at 550ms, signal completion at 800ms:

```
Caller speaks: "Bună ziua"
  ↓
[550ms silence] → Send audio immediately
  ↓              VPS starts Whisper (runs in background)
  ↓
[250ms more passes, now 800ms total]
  ↓
Send end_sentence signal
  ↓
VPS: Whisper already done! Just run LLM
  ↓
Bot responds

Total time from end of speech: 2.6 seconds
Savings: 1.2 seconds (31% faster!)
```

**Benefits:**
- ✅ Audio sent 250ms earlier
- ✅ Whisper runs while waiting for 800ms
- ✅ Parallel processing (transcribe WHILE waiting)
- ✅ VPS already has transcription when end signal arrives

---

## Complete Flow

### Visual Timeline

```
T+0.0s   Caller starts speaking: "Bună ziua"
T+2.3s   Caller stops speaking
         │
         ├─ [SPEECH ENDS - Silence begins]
         │
T+2.5s   Silence: 200ms
T+2.7s   Silence: 400ms
         │
T+2.85s  🎯 THRESHOLD 1: 550ms silence detected
         │
         ├─ ACTION: Send audio chunk to VPS
         │  ├─ Type: 'audio'
         │  ├─ PCM data: <2.3s of audio>
         │  ├─ end_sentence: false
         │  └─ POST to VPS
         │
         ├─ VPS receives audio
         │  ├─ Stores chunk in memory
         │  ├─ Starts Whisper transcription (async)
         │  └─ Returns acknowledgment
         │
         ├─ Bot continues listening (no response yet)
         │
T+2.9s   Silence: 600ms (continues...)
T+3.0s   Silence: 700ms (continues...)
         │
T+3.1s   🎯 THRESHOLD 2: 800ms total silence detected
         │
         ├─ ACTION: Send end-of-sentence signal
         │  ├─ Type: 'end_sentence'
         │  ├─ PCM data: null (no audio!)
         │  ├─ end_sentence: true
         │  ├─ References chunk_number: 1
         │  └─ POST to VPS
         │
         ├─ VPS receives end signal
         │  ├─ Whisper already completed! (started at T+2.85s)
         │  ├─ Retrieves transcription: "Bună ziua"
         │  ├─ Sends to LLM with context
         │  ├─ LLM processes (1s)
         │  └─ Returns response text
         │
T+4.1s   Bot receives response
         │
         ├─ Generates TTS
         └─ Plays to caller: "Bună ziua! Cu ce vă pot ajuta?"
```

---

## Message Types

### Type 1: Audio Chunk Message (550ms threshold)

**Purpose:** Send audio early so VPS can start Whisper

**When sent:** Silence duration reaches 550ms

**Queue message structure:**
```python
{
    'type': 'audio',
    'pcm_data': b'\x00\x01\x02...',  # Raw PCM bytes
    'chunk_num': 1,
    'timestamp': 1730064560,
    'sample_rate': 16000,
    'duration': 2.3,  # seconds
    'end_sentence': False  # Not complete yet!
}
```

**HTTP payload to VPS:**
```json
{
  "call_id": "call_1761507557",
  "chunk_number": 1,
  "audio": "T2dnUwACAAAAAAAAAAC...",
  "language": "ro",
  "context": "caller: previous\nbot: response",
  "caller_id": "+447504128961",
  "end_sentence": false,
  "metadata": {
    "timestamp": 1730064560,
    "duration_ms": 2300,
    "sample_rate": 16000
  }
}
```

**VPS response:**
```json
{
  "status": "processing",
  "call_id": "call_1761507557",
  "chunk_received": 1,
  "message": "Chunk received, transcribing..."
}
```

**VPS actions:**
1. Decode base64 → OGG bytes
2. Store chunk in memory (keyed by call_id + chunk_number)
3. Start Whisper transcription (async, don't block)
4. Return acknowledgment immediately

---

### Type 2: End-of-Sentence Signal (800ms threshold)

**Purpose:** Tell VPS "sentence is complete, process through LLM"

**When sent:** Silence duration reaches 800ms (250ms after audio sent)

**Queue message structure:**
```python
{
    'type': 'end_sentence',
    'chunk_num': 1,  # References the chunk
    'timestamp': 1730064562,
    'silence_duration_ms': 800
}
```

**HTTP payload to VPS:**
```json
{
  "call_id": "call_1761507557",
  "chunk_number": 1,
  "audio": null,
  "language": "ro",
  "context": "caller: previous\nbot: response",
  "caller_id": "+447504128961",
  "end_sentence": true,
  "metadata": {
    "timestamp": 1730064562,
    "silence_duration_ms": 800,
    "type": "end_signal"
  }
}
```

**VPS response:**
```json
{
  "status": "success",
  "call_id": "call_1761507557",
  "transcription": "Bună ziua",
  "response": "Bună ziua! Cu ce vă pot ajuta?",
  "continue": true,
  "processing_time_ms": 1200,
  "chunks": [
    {
      "chunk_number": 1,
      "transcription": "Bună ziua",
      "transcription_time_ms": 450,
      "audio_duration_ms": 2300
    }
  ],
  "timing": {
    "total_transcription_time_ms": 450,
    "llm_processing_time_ms": 1200,
    "total_time_ms": 1650
  }
}
```

**VPS actions:**
1. Retrieve chunk from memory (call_id + chunk_number)
2. Wait for Whisper if not done yet (should be done already!)
3. Get transcription result
4. Send transcription + context to LLM
5. Return LLM response
6. Clean up stored chunk

---

## VPS API Specification

### Endpoint

**URL:** `POST http://10.100.0.1:9000/api/transcribe`
**Content-Type:** `application/json`
**Timeout:** 10 seconds

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `call_id` | string | Yes | Unique call identifier |
| `chunk_number` | integer | Yes | Sequential chunk number |
| `audio` | string \| null | Conditional | Base64 OGG (null for end signals) |
| `language` | string | Yes | Language code (ro, en, lt, auto) |
| `context` | string | No | Conversation history |
| `caller_id` | string | Yes | Phone number or "unknown" |
| `end_sentence` | boolean | Yes | false=chunk, true=complete |
| `metadata` | object | Yes | Additional info |

### Metadata Fields

| Field | Type | When | Description |
|-------|------|------|-------------|
| `timestamp` | integer | Always | Unix timestamp |
| `duration_ms` | integer | Audio chunks | Audio duration |
| `sample_rate` | integer | Audio chunks | 8000 or 16000 Hz |
| `silence_duration_ms` | integer | End signals | Total silence detected |
| `type` | string | End signals | "end_signal" identifier |

### Response Types

**Audio Chunk Response:**
```json
{
  "status": "processing",
  "call_id": "call_1761507557",
  "chunk_received": 1,
  "message": "Chunk received, transcribing..."
}
```

**End Signal Response (Success):**
```json
{
  "status": "success",
  "call_id": "call_1761507557",
  "transcription": "Complete sentence",
  "response": "Bot response from LLM",
  "continue": true,
  "processing_time_ms": 1650,
  "chunks": [
    {
      "chunk_number": 1,
      "transcription": "Complete sentence",
      "transcription_time_ms": 450,
      "audio_duration_ms": 2300
    }
  ],
  "timing": {
    "total_transcription_time_ms": 450,
    "llm_processing_time_ms": 1200,
    "total_time_ms": 1650
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "call_id": "call_1761507557",
  "error": "Error description",
  "fallback_response": "Ne cerem scuze, vă rog să repetați",
  "continue": true
}
```

---

## Complete Response Examples

### Example 1: Single Short Utterance

**Caller says:** "Bună ziua" (2.3 seconds)

**Message flow:**
1. **550ms silence** → Audio chunk sent
2. **800ms silence** → End signal sent

**VPS Response:**
```json
{
  "status": "success",
  "call_id": "call_1761507557",
  "transcription": "Bună ziua",
  "response": "Bună ziua! Cu ce vă pot ajuta?",
  "continue": true,
  "processing_time_ms": 1650,
  "chunks": [
    {
      "chunk_number": 1,
      "transcription": "Bună ziua",
      "transcription_time_ms": 450,
      "audio_duration_ms": 2300
    }
  ],
  "timing": {
    "total_transcription_time_ms": 450,
    "llm_processing_time_ms": 1200,
    "total_time_ms": 1650
  }
}
```

---

### Example 2: Progressive Transcription (Multiple Chunks)

**Caller says:** "Bună ziua, aș vrea să programez o întâlnire pentru săptămâna viitoare" (12 seconds)

**Message flow:**
1. **0s-4.5s:** Speech + 550ms silence → Chunk #1 sent
2. **5s-9.5s:** Speech continues + 550ms silence → Chunk #2 sent
3. **10s-12s:** Speech continues + 550ms silence → Chunk #3 sent
4. **12s + 800ms:** Final silence → End signal sent

**VPS Response:**
```json
{
  "status": "success",
  "call_id": "call_1761507557",
  "transcription": "Bună ziua, aș vrea să programez o întâlnire pentru săptămâna viitoare",
  "response": "Bineînțeles! Pentru ce zi doriți programarea?",
  "continue": true,
  "processing_time_ms": 2850,
  "chunks": [
    {
      "chunk_number": 1,
      "transcription": "Bună ziua, aș vrea să",
      "transcription_time_ms": 580,
      "audio_duration_ms": 4500
    },
    {
      "chunk_number": 2,
      "transcription": "programez o întâlnire pentru",
      "transcription_time_ms": 620,
      "audio_duration_ms": 4500
    },
    {
      "chunk_number": 3,
      "transcription": "săptămâna viitoare",
      "transcription_time_ms": 450,
      "audio_duration_ms": 3000
    }
  ],
  "timing": {
    "total_transcription_time_ms": 1650,
    "llm_processing_time_ms": 1200,
    "total_time_ms": 2850
  }
}
```

**Key points:**
- Each chunk transcribed in parallel (not sequentially!)
- Total transcription time = slowest chunk (620ms), NOT sum
- LLM only runs after end signal
- Bot can respond in ~2.85s instead of ~5s (if waiting for all chunks sequentially)

---

### Example 3: Speech Resumption (Cancelled End Signal)

**Caller says:** "Bună..." [pause] "...ziua" (thinks mid-sentence)

**Message flow:**
1. **550ms silence after "Bună"** → Chunk #1 sent
2. **650ms silence** → About to send end signal...
3. **670ms:** Caller speaks again! → End signal cancelled, reset state
4. **800ms silence after "ziua"** → Chunk #2 sent (new utterance)
5. **1050ms silence** → End signal sent

**VPS receives:** 2 separate utterances, processes as 2 chunks

---

## Implementation Details

### 1. VAD State Machine (audio_capture_thread)

```python
class VADStateTracker:
    """Tracks silence and manages dual-threshold detection"""

    def __init__(self):
        self.silence_start_time = None  # When silence started
        self.audio_chunk_sent = False   # Did we send at 550ms?
        self.end_signal_sent = False    # Did we send at 800ms?
        self.accumulated_audio = []     # PCM frames
        self.current_chunk_num = 0

    def process_frame(self, audio_frame, is_speech):
        """Process each 20ms audio frame"""

        if not is_speech:
            # SILENCE DETECTED
            if self.silence_start_time is None:
                self.silence_start_time = time.time()

            silence_ms = (time.time() - self.silence_start_time) * 1000

            # THRESHOLD 1: 550ms - Send audio
            if silence_ms >= 550 and not self.audio_chunk_sent:
                self.send_audio_chunk()
                self.audio_chunk_sent = True

            # THRESHOLD 2: 800ms - Send end signal
            elif silence_ms >= 800 and self.audio_chunk_sent and not self.end_signal_sent:
                self.send_end_signal()
                self.end_signal_sent = True
                self.reset_for_next_utterance()

        else:
            # SPEECH DETECTED
            if self.silence_start_time is not None:
                # Speech resumed before thresholds - cancel pending signals
                if not self.audio_chunk_sent:
                    # Speech resumed before 550ms - just continue
                    self.silence_start_time = None
                else:
                    # Speech resumed after 550ms but before 800ms
                    # Audio already sent, cancel end signal
                    self.audio_chunk_sent = False
                    self.silence_start_time = None

            self.accumulated_audio.append(audio_frame)

    def send_audio_chunk(self):
        """Send audio chunk at 550ms threshold"""
        pcm_data = b''.join(self.accumulated_audio)
        self.current_chunk_num += 1

        message = {
            'type': 'audio',
            'pcm_data': pcm_data,
            'chunk_num': self.current_chunk_num,
            'timestamp': int(time.time()),
            'sample_rate': self.sample_rate,
            'duration': len(pcm_data) / (self.sample_rate * 2),
            'end_sentence': False
        }

        try:
            self.vps_queue.put_nowait(message)
            logger.info(f"📤 Chunk #{self.current_chunk_num} queued (550ms, {len(pcm_data)} bytes)")
        except queue.Full:
            logger.warning(f"⚠️ VPS queue full - chunk #{self.current_chunk_num} dropped")

    def send_end_signal(self):
        """Send end-of-sentence signal at 800ms threshold"""
        message = {
            'type': 'end_sentence',
            'chunk_num': self.current_chunk_num,
            'timestamp': int(time.time()),
            'silence_duration_ms': 800
        }

        try:
            self.vps_queue.put_nowait(message)
            logger.info(f"🏁 End signal queued for chunk #{self.current_chunk_num} (800ms total)")
        except queue.Full:
            logger.warning(f"⚠️ VPS queue full - end signal dropped")

    def reset_for_next_utterance(self):
        """Reset state for next utterance"""
        self.silence_start_time = None
        self.audio_chunk_sent = False
        self.end_signal_sent = False
        self.accumulated_audio = []
```

---

### 2. VPS Thread Processing

```python
def vps_transcription_thread(self):
    """Process both audio chunks and end signals"""

    import base64
    from audio_recorder import pcm_to_opus_ogg

    logger.info("🚀 VPS transcription thread started")

    while self.in_call:
        try:
            message = self.vps_queue.get(timeout=0.5)

            if message['type'] == 'audio':
                self.handle_audio_chunk(message)

            elif message['type'] == 'end_sentence':
                self.handle_end_sentence(message)

        except queue.Empty:
            continue
        except Exception as e:
            logger.error(f"VPS thread error: {e}")

def handle_audio_chunk(self, message):
    """Handle audio chunk (550ms threshold)"""

    pcm_data = message['pcm_data']
    chunk_num = message['chunk_num']
    sample_rate = message['sample_rate']
    duration = message['duration']

    logger.info(f"📤 Processing audio chunk #{chunk_num} ({duration:.2f}s)")

    try:
        # Convert PCM → OGG
        start = time.time()
        ogg_data = pcm_to_opus_ogg(pcm_data, sample_rate, output_path=None)
        compress_time = time.time() - start

        if not ogg_data:
            logger.error(f"❌ Compression failed for chunk #{chunk_num}")
            return

        # Encode to base64
        ogg_b64 = base64.b64encode(ogg_data).decode('utf-8')

        logger.info(f"   Compressed: {len(pcm_data)/1024:.1f}KB → {len(ogg_data)/1024:.1f}KB in {compress_time:.2f}s")

        # Build payload
        payload = {
            'call_id': self.call_id,
            'chunk_number': chunk_num,
            'audio': ogg_b64,
            'language': self.voice_config.get('language'),
            'context': self.get_conversation_context(),
            'caller_id': self.caller_id or 'unknown',
            'end_sentence': False,
            'metadata': {
                'timestamp': message['timestamp'],
                'duration_ms': int(duration * 1000),
                'sample_rate': sample_rate
            }
        }

        # POST to VPS
        start = time.time()
        response = requests.post(self.vps_transcription_url, json=payload, timeout=10)
        post_time = time.time() - start

        if response.status_code == 200:
            logger.info(f"✅ Chunk #{chunk_num} sent to VPS ({post_time:.2f}s)")
        else:
            logger.error(f"❌ VPS error {response.status_code} for chunk #{chunk_num}")

    except requests.Timeout:
        logger.error(f"❌ VPS timeout for chunk #{chunk_num}")
    except Exception as e:
        logger.error(f"❌ Error processing chunk #{chunk_num}: {e}")

def handle_end_sentence(self, message):
    """Handle end-of-sentence signal (800ms threshold)"""

    chunk_num = message['chunk_num']

    logger.info(f"🏁 Processing end signal for chunk #{chunk_num}")

    try:
        # Build payload (NO AUDIO)
        payload = {
            'call_id': self.call_id,
            'chunk_number': chunk_num,
            'audio': None,
            'language': self.voice_config.get('language'),
            'context': self.get_conversation_context(),
            'caller_id': self.caller_id or 'unknown',
            'end_sentence': True,
            'metadata': {
                'timestamp': message['timestamp'],
                'silence_duration_ms': message['silence_duration_ms'],
                'type': 'end_signal'
            }
        }

        # POST to VPS
        start = time.time()
        response = requests.post(self.vps_transcription_url, json=payload, timeout=10)
        post_time = time.time() - start

        if response.status_code == 200:
            data = response.json()

            if data.get('status') == 'success':
                transcription = data.get('transcription', '')
                response_text = data.get('response', '')
                processing_time = data.get('processing_time_ms', 0)

                logger.info(f"✅ End signal processed ({post_time:.2f}s, VPS: {processing_time}ms)")
                logger.info(f"   Transcription: {transcription}")
                logger.info(f"   Response: {response_text}")

                # Update conversation context
                self.conversation_context.append({'role': 'caller', 'text': transcription})
                self.conversation_context.append({'role': 'bot', 'text': response_text})

                # Generate TTS and play
                if response_text:
                    self.request_tts(response_text, priority='high')

                # Check if VPS wants to end call
                if not data.get('continue', True):
                    logger.info("🛑 VPS requested call end")
                    self.in_call = False

            else:
                # VPS error
                error_msg = data.get('error', 'Unknown error')
                fallback = data.get('fallback_response', 'Ne cerem scuze, vă rog să repetați')
                logger.error(f"❌ VPS error: {error_msg}")
                self.request_tts(fallback, priority='high')

        else:
            logger.error(f"❌ VPS HTTP {response.status_code}")
            self.request_tts("Ne cerem scuze, am avut o problemă tehnică", priority='high')

    except requests.Timeout:
        logger.error(f"❌ VPS timeout for end signal")
        self.request_tts("Un moment, vă rog", priority='high')
    except Exception as e:
        logger.error(f"❌ Error processing end signal: {e}")
        self.request_tts("Ne cerem scuze, am avut o problemă", priority='high')

def get_conversation_context(self):
    """Build context string from conversation history"""
    messages = []
    for msg in self.conversation_context[-5:]:  # Last 5 messages
        messages.append(f"{msg['role']}: {msg['text']}")
    return "\n".join(messages)
```

---

## Timing Analysis

### Comparison: Old vs New

**Old System (Single 800ms threshold):**
```
T+0.0s   Caller speaks
T+2.3s   Caller stops
T+3.1s   [800ms silence] Send to VPS
         VPS: Decompress audio (0.1s)
         VPS: Whisper transcribe (2.0s)
         VPS: LLM process (1.0s)
T+6.2s   Bot responds

Total: 3.9s from end of speech
```

**New System (Dual 550ms/800ms thresholds):**
```
T+0.0s   Caller speaks
T+2.3s   Caller stops
T+2.85s  [550ms silence] Send audio
         VPS: Starts Whisper (async)
T+3.1s   [800ms silence] Send end signal
         VPS: Whisper already done!
         VPS: LLM process (1.0s)
T+4.1s   Bot responds

Total: 2.8s from end of speech
Savings: 1.1 seconds (28% faster!)
```

### Per-Stage Breakdown

| Stage | Old | New | Delta |
|-------|-----|-----|-------|
| Wait for threshold | 800ms | 550ms | -250ms |
| Send audio | 100ms | 100ms | 0ms |
| VPS: Decompress | 100ms | 100ms | 0ms |
| VPS: Whisper | 2000ms | 0ms* | -2000ms* |
| Send end signal | 0ms | 100ms | +100ms |
| VPS: LLM | 1000ms | 1000ms | 0ms |
| **Total** | **4000ms** | **2850ms** | **-1150ms** |

*Whisper runs in parallel with waiting for 800ms, so effective time is 0ms when end signal arrives

---

## Error Handling

### Scenario 1: Audio chunk fails to send

**Problem:** Network error at 550ms

**Handling:**
```python
try:
    response = requests.post(vps_url, json=audio_payload, timeout=10)
except requests.ConnectionError:
    logger.error("Failed to send audio chunk")
    # Still send end signal with audio included
    self.failed_chunk_numbers.add(chunk_num)
```

**Fallback:** Include audio in end_sentence payload as backup

---

### Scenario 2: End signal fails to send

**Problem:** Network error at 800ms

**Handling:**
- Retry once (5s timeout)
- If still fails, use generic response
- Log error for monitoring

---

### Scenario 3: Caller resumes speaking between thresholds

**Timeline:**
```
T+0.0s   Caller: "Bună"
T+0.55s  [550ms pause] → Send audio chunk #1
T+0.70s  Caller resumes: "ziua"
         → Cancel end signal for chunk #1
         → Continue accumulating
T+3.2s   [550ms pause] → Send audio chunk #2 (contains "ziua")
T+4.0s   [800ms pause] → Send end signal for chunk #2
```

**Code:**
```python
if speech_detected and audio_chunk_sent and not end_signal_sent:
    # Cancel pending end signal
    audio_chunk_sent = False
    silence_start_time = None
    logger.debug("Speech resumed - cancelled pending end signal")
```

**VPS behavior:**
- Receives chunk #1 (partial: "Bună")
- Receives chunk #2 (continuation: "ziua")
- Receives end signal (chunk #2)
- Combines: "Bună ziua"
- Processes through LLM

---

### Scenario 4: VPS overwhelmed (slow Whisper)

**Problem:** Whisper not done when end signal arrives

**VPS handling:**
```python
def handle_end_signal(call_id, chunk_num):
    # Wait for Whisper with timeout
    for i in range(20):  # Wait up to 2 seconds
        if chunks[call_id][chunk_num].whisper_done:
            break
        time.sleep(0.1)

    if not chunks[call_id][chunk_num].whisper_done:
        logger.warning("Whisper not done yet - waiting longer")
        # Wait up to 5s total
        time.sleep(3)

    # Proceed with whatever we have
    transcription = chunks[call_id][chunk_num].transcription or ""
```

---

## Testing

### Test 1: Single-chunk sentence

**Input:** "Bună ziua" (short, one chunk)

**Expected behavior:**
```
T+0.55s: POST {chunk_number: 1, audio: <data>, end_sentence: false}
         Response: {"status": "processing"}

T+0.80s: POST {chunk_number: 1, audio: null, end_sentence: true}
         Response: {"transcription": "Bună ziua", "response": "Bună ziua! Cu ce vă pot ajuta?"}
```

**Verification:**
- Log shows "📤 Chunk #1 queued (550ms)"
- Log shows "🏁 End signal queued for chunk #1 (800ms)"
- Log shows "✅ End signal processed"
- Bot responds with TTS

---

### Test 2: Multi-chunk sentence (caller pauses mid-sentence)

**Input:** "Bună ziua" [550ms] "aș vrea" [550ms] "o programare" [800ms]

**Expected behavior:**
```
T+0.55s: POST chunk #1 ("Bună ziua")
T+1.10s: POST chunk #2 ("aș vrea")
T+1.65s: POST chunk #3 ("o programare")
T+1.90s: POST end_sentence (chunk #3)
         VPS combines: "Bună ziua aș vrea o programare"
```

---

### Test 3: False start (speech resumes before 800ms)

**Input:** "Bună" [550ms] [speech resumes] "ziua aș vrea o programare" [800ms]

**Expected behavior:**
```
T+0.55s: POST chunk #1 ("Bună")
T+0.70s: [Speech resumes - cancel end signal]
T+3.85s: POST chunk #2 ("ziua aș vrea o programare")
T+4.65s: POST end_sentence (chunk #2)
         VPS combines all chunks
```

---

### Test 4: Network failure at 550ms

**Input:** Network error when sending audio chunk

**Expected behavior:**
```
T+0.55s: POST chunk #1 → ConnectionError
         Log: "Failed to send audio chunk"
T+0.80s: POST end_sentence with audio included as fallback
         VPS: Processes normally
```

---

### Test 5: VPS slow response

**Input:** VPS takes 8s to respond (slower than 10s timeout)

**Expected behavior:**
```
T+0.55s: POST chunk #1 → VPS starts Whisper
T+0.80s: POST end_sentence
         [Wait for VPS]
T+8.8s:  VPS responds (just before 10s timeout)
         Bot: Plays response
```

---

## Performance Metrics

### Expected Latencies

**Compression (PCM → OGG):**
- 2s audio: ~0.5s
- 5s audio: ~0.6s

**Network (4G VPN):**
- Upload 3KB: ~0.01s
- Upload 10KB: ~0.03s

**VPS Processing:**
- Whisper (GPU): 1-2s
- LLM: 0.5-1.5s

**Total Response Time:**
- Old: 3.9s from end of speech
- New: 2.8s from end of speech
- **Improvement: 1.1s (28% faster)**

---

## Summary

### Key Changes

✅ **Dual thresholds:** 550ms (send audio) + 800ms (signal end)
✅ **Two message types:** audio chunks + end signals
✅ **Parallel processing:** Whisper runs while waiting for 800ms
✅ **No audio in end signal:** Only send audio once at 550ms
✅ **Faster responses:** 1.1s latency improvement

### Files Modified

- `/home/rom/sim7600_voice_bot.py` - VAD state machine + VPS thread
- `/home/rom/audio_recorder.py` - Queue message handling
- `/home/rom/.env` - VPS endpoint URL

### Deployment Checklist

- [ ] Deploy code to voice bot
- [ ] Test with single-chunk sentences
- [ ] Test with multi-chunk sentences
- [ ] Test with false starts (speech resumes)
- [ ] Test network failure scenarios
- [ ] Deploy VPS endpoint
- [ ] Measure real-world latency improvements
- [ ] Tune thresholds if needed

---

**Status:** ✅ Documented and ready for implementation
