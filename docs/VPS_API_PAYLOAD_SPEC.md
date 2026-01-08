# VPS Transcription API - Payload Specification

**Endpoint:** `POST http://10.100.0.1:9000/api/transcribe`
**Content-Type:** `application/json`
**Timeout:** 10 seconds

---

## Message Type 1: Audio Chunk (550ms threshold)

### Request from Raspberry Pi

```json
{
  "call_id": "call_1761507557",
  "chunk_number": 1,
  "audio": "T2dnUwACAAAAAAAAAAC...",
  "language": "ro",
  "context": "caller: previous text\nbot: previous response",
  "caller_id": "+447504128961",
  "end_sentence": false,
  "metadata": {
    "timestamp": 1730064560,
    "duration_ms": 2300,
    "sample_rate": 8000
  }
}
```

**Field descriptions:**
- `audio`: Base64-encoded OGG Opus file
- `end_sentence`: `false` = chunk only, Whisper should start
- `chunk_number`: Sequential number (1, 2, 3...)
- `sample_rate`: 8000 Hz (from modem PCM)

### Expected Response from VPS

```json
{
  "status": "processing",
  "call_id": "call_1761507557",
  "chunk_received": 1,
  "message": "Chunk received, transcribing..."
}
```

**VPS should:**
1. Decode base64 → OGG bytes
2. Store chunk in memory (keyed by `call_id` + `chunk_number`)
3. Start Whisper transcription **async** (don't block response!)
4. Return acknowledgment immediately

---

## Message Type 2: End Signal (800ms threshold)

### Request from Raspberry Pi

```json
{
  "call_id": "call_1761507557",
  "chunk_number": 1,
  "audio": null,
  "language": "ro",
  "context": "caller: previous text\nbot: previous response",
  "caller_id": "+447504128961",
  "end_sentence": true,
  "metadata": {
    "timestamp": 1730064562,
    "silence_duration_ms": 800,
    "type": "end_signal"
  }
}
```

**Field descriptions:**
- `audio`: **null** (no audio, signal only!)
- `end_sentence`: `true` = sentence complete, run LLM
- `chunk_number`: References the chunk(s) sent earlier

### Expected Response from VPS

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

**Response field descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | string | Yes | "success" or "error" |
| `call_id` | string | Yes | Echo back the call ID for validation |
| `transcription` | string | Yes | Combined text from all chunks |
| `response` | string | Yes | LLM-generated bot response |
| `continue` | boolean | Yes | `true` = continue call, `false` = hang up |
| `processing_time_ms` | integer | Yes | Total processing time |
| `chunks` | array | Yes | Per-chunk transcription details |
| `timing` | object | Yes | Breakdown of processing times |

**Chunks array (each element):**
- `chunk_number`: Which chunk this is
- `transcription`: Text from this chunk
- `transcription_time_ms`: How long Whisper took for this chunk
- `audio_duration_ms`: Length of audio in this chunk

**Timing object:**
- `total_transcription_time_ms`: Total Whisper time (all chunks, parallel)
- `llm_processing_time_ms`: LLM processing time
- `total_time_ms`: Sum of transcription + LLM

**VPS should:**
1. Retrieve stored chunk(s) from memory
2. Wait for Whisper if not done (should be done already!)
3. Combine transcriptions from all chunks
4. Send combined text + context to LLM
5. Return full response with timing breakdown
6. Clean up stored chunks

---

## Multiple Chunks Example (Progressive Transcription)

**Scenario:** Caller speaks for 12 seconds

### Messages sent to VPS:

**1. Chunk #1 (at 4.5s + 550ms):**
```json
{
  "call_id": "call_1761507557",
  "chunk_number": 1,
  "audio": "T2dnU...",
  "end_sentence": false,
  "metadata": {"duration_ms": 4500}
}
```

**2. Chunk #2 (at 9s + 550ms):**
```json
{
  "call_id": "call_1761507557",
  "chunk_number": 2,
  "audio": "T2dnU...",
  "end_sentence": false,
  "metadata": {"duration_ms": 4500}
}
```

**3. Chunk #3 (at 12s + 550ms):**
```json
{
  "call_id": "call_1761507557",
  "chunk_number": 3,
  "audio": "T2dnU...",
  "end_sentence": false,
  "metadata": {"duration_ms": 3000}
}
```

**4. End signal (at 12s + 800ms):**
```json
{
  "call_id": "call_1761507557",
  "chunk_number": 3,
  "audio": null,
  "end_sentence": true
}
```

### Expected VPS Response (for end signal):

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

**Key insight:**
- Chunks processed **in parallel**, not sequentially
- `total_transcription_time_ms` = MAX(580, 620, 450) = 620ms (slowest chunk)
- NOT 580 + 620 + 450 = 1650ms (would be sequential)
- This is why progressive transcription saves ~2-3 seconds!

---

## Error Response

```json
{
  "status": "error",
  "call_id": "call_1761507557",
  "error": "Whisper timeout / Connection failed / etc",
  "fallback_response": "Ne cerem scuze, vă rog să repetați",
  "continue": true
}
```

**Raspberry Pi will:**
- Play `fallback_response` via TTS
- Continue or end call based on `continue` flag

---

## Implementation Notes for VPS

### State Management

```python
# Store chunks in memory (keyed by call_id)
active_calls = {
    "call_1761507557": {
        "chunks": {
            1: {"audio": b"...", "transcription": None, "whisper_task": AsyncTask},
            2: {"audio": b"...", "transcription": None, "whisper_task": AsyncTask}
        },
        "context": "caller: hello\nbot: hi"
    }
}
```

### Processing Flow

**On audio chunk received:**
```python
# 1. Decode base64 → bytes
ogg_bytes = base64.b64decode(request.json['audio'])

# 2. Store chunk
call_id = request.json['call_id']
chunk_num = request.json['chunk_number']
active_calls[call_id]['chunks'][chunk_num] = {
    'audio': ogg_bytes,
    'transcription': None
}

# 3. Start Whisper async (don't wait!)
task = asyncio.create_task(whisper_transcribe(ogg_bytes))
active_calls[call_id]['chunks'][chunk_num]['whisper_task'] = task

# 4. Return immediately
return {"status": "processing", "chunk_received": chunk_num}
```

**On end signal received:**
```python
# 1. Wait for all Whisper tasks to complete
call_data = active_calls[call_id]
for chunk_num, chunk in call_data['chunks'].items():
    if chunk['whisper_task']:
        chunk['transcription'] = await chunk['whisper_task']

# 2. Combine all transcriptions
full_text = " ".join([c['transcription'] for c in chunks.values()])

# 3. Send to LLM
llm_start = time.time()
bot_response = await llm_process(full_text, context)
llm_time = (time.time() - llm_start) * 1000

# 4. Build response
return {
    "status": "success",
    "transcription": full_text,
    "response": bot_response,
    "chunks": [...],
    "timing": {...}
}

# 5. Cleanup
del active_calls[call_id]
```

---

## Raspberry Pi Code Reference

**Dual-threshold VAD implementation:** `/home/rom/sim7600_voice_bot.py:996-1077`
**VPS transcription thread:** `/home/rom/sim7600_voice_bot.py:1292-1450`
**Complete documentation:** `/home/rom/docs/DUAL_THRESHOLD_VAD.md`
