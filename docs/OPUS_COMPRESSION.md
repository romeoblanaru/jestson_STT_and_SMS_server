# Opus OGG Audio Compression for VPS Transmission

**Date:** October 26, 2025
**Purpose:** Compress voice call audio for efficient transmission to VPS over VPN for transcription

---

## Overview

Converting 16kHz mono PCM WAV files to Opus OGG format achieves **~12x compression** with **92% bandwidth savings**. This enables fast transmission of voice chunks to VPS for Whisper transcription processing.

---

## Compression Results (Test Call: call_1761507557)

### Individual VAD Chunks

| File | WAV Size | OGG Size | Compression | Duration | Encoding Time |
|------|----------|----------|-------------|----------|---------------|
| Chunk #1 | 21K | 1.9K | **11.3x** | 0.65s | ~0.08s |
| Chunk #2 | 32K | 2.8K | **11.6x** | 1.01s | ~0.13s |
| Chunk #3 | 188K | 16K | **12.3x** | 6.00s | ~0.38s |
| Chunk #4 | 9.5K | 980B | **9.8x** | 0.30s | ~0.04s |
| Chunk #5 | 30K | 2.6K | **11.6x** | 0.93s | ~0.12s |

### Full Call Recording

- **WAV:** 528K (540,204 bytes) - 16.88 seconds
- **OGG:** 43K (43,691 bytes)
- **Compression:** 12.4x smaller
- **Bandwidth savings:** 92% reduction
- **Encoding time:** ~1 second

---

## VPS Transmission Benefits

**Network Performance:**
- Typical 3-second chunk: **3KB OGG** vs 30KB WAV
- Upload time on 4G (5 Mbps up): **~0.005s** vs 0.05s (10x faster)
- Full 17s call: **43KB** vs 528KB (sends in ~0.07s vs 0.8s)
- **92% less VPN bandwidth usage**

**Why This Matters:**
- Faster upload = quicker transcription response
- Lower VPN bandwidth = more stable connection
- Reduced mobile data usage when on cellular backup

---

## Opus Codec Configuration

### Target Specification (VoIP Optimized)

✅ **Sample rate:** 16 kHz
✅ **Bitrate:** 20-24 kbps CBR/VBR
✅ **Frame duration:** 20 ms (default)
✅ **Channels:** 1 (mono)
✅ **Application:** VoIP optimized

---

## Encoding Settings Comparison

### Original Settings (Good Quality, Slower)

```bash
ffmpeg -i input.wav \
  -c:a libopus \
  -b:a 20k \
  -ar 16000 \
  -ac 1 \
  -frame_duration 20 \
  -application voip \
  -vbr off \
  output.ogg
```

**Performance (6-second audio):**
- Encoding speed: **15.6x real-time**
- Real encoding time: **~1.04s** (0.38s for 6s audio)
- Output size: **16K**
- Bitrate: **20 kbps CBR**

### ⚡ RECOMMENDED: Fast Settings (Better Performance)

```bash
ffmpeg -i input.wav \
  -c:a libopus \
  -b:a 24k \
  -ar 16000 \
  -ac 1 \
  -application voip \
  -vbr on \
  -compression_level 0 \
  output.ogg
```

**Performance (6-second audio):**
- Encoding speed: **90x real-time** ✅
- Real encoding time: **~0.74s** (0.07s for 6s audio) ✅
- Output size: **12K** (25% smaller!) ✅
- Bitrate: **~16 kbps VBR** (adaptive)

**Improvements:**
- **5.7x faster encoding** (90x vs 15.6x real-time)
- **0.31 seconds saved per 6-second chunk**
- **25% smaller files** (VBR adapts to content)
- Still excellent quality for VoIP

**Key Changes:**
- `vbr on` - Variable bitrate adapts to speech patterns (more efficient)
- `compression_level 0` - Minimal CPU processing (fastest)
- `-b:a 24k` - Slightly higher bitrate for less aggressive compression
- Removed `-frame_duration 20` - Uses optimal default

---

## Important Timing Clarification

**⚠️ Don't confuse audio duration with encoding time!**

When ffmpeg shows: `time=00:00:06.01 bitrate=20.9kbits/s speed=16.7x`

- `time=00:00:06.01` = **Duration of audio content** (not encoding time)
- `speed=16.7x` = **Encoding speed multiplier** (16.7x faster than real-time)
- **Actual encoding time** = 6.01s ÷ 16.7 = **0.36 seconds**

**Fast settings achieve speed=90x:**
- 6-second audio takes only **0.07 seconds to encode**
- Encoding adds negligible latency to voice bot response

---

## Implementation Plan for VPS Integration

### Current Flow (Local Whisper)
1. VAD detects speech pause
2. Audio chunk saved as WAV
3. Whisper transcribes locally (18-59s per chunk) ❌ **SLOW**

### Proposed Flow (VPS Transcription)
1. VAD detects speech pause
2. **Convert WAV → Opus OGG (~0.1s)** ✅
3. **Send OGG to VPS via VPN (~0.01s)** ✅
4. VPS transcribes with faster hardware (~2-5s) ✅
5. VPS returns transcription + TTS audio response
6. Bot plays TTS response

**Expected Latency:**
- Encoding: ~0.1s
- Upload (4G): ~0.01s
- VPS Whisper: ~2-5s (GPU accelerated)
- Download TTS: ~0.1s
- **Total: ~2-3 seconds** (vs 18-59s locally)

### VPS Endpoint Structure

**POST /api/transcribe**

Request:
```json
{
  "call_id": "call_1761507557",
  "chunk_number": 1,
  "audio": "<base64 encoded OGG>",
  "language": "ro",
  "stt_model": "WHISPER_BASE"
}
```

Response:
```json
{
  "transcription": "Cum înțeva?",
  "duration": 2.3,
  "tts_audio": "<base64 encoded TTS response>",
  "continue": true
}
```

---

## File Locations

**Test Files:**
- WAV files: `/home/rom/audio_wav/call_1761507557_vad_chunk_*.wav`
- OGG files: `/home/rom/audio_wav/call_1761507557_vad_chunk_*.ogg`
- Conversion script: `/home/rom/convert_to_opus.sh`

**Related Documentation:**
- `/home/rom/docs/AUDIO_CONFIGURATION.md` - VAD and audio settings
- `/home/rom/docs/VAD_CONVERSATION_FLOW.md` - Conversation flow implementation
- `/home/rom/CALL_HANDLING_FLOW.md` - Complete call handling workflow

---

## Next Steps

1. ✅ **Compression testing complete** - Opus OGG achieves 12x compression
2. ✅ **Fast encoding validated** - 90x real-time with compression_level 0
3. ⏳ **Integrate into voice bot** - Replace local Whisper with VPS API call
4. ⏳ **Implement VPS endpoint** - Transcription + TTS response API
5. ⏳ **Test end-to-end latency** - Measure actual call response time
6. ⏳ **Handle network failures** - Fallback to local Whisper or cached responses

---

## Technical Notes

**Why Opus for VoIP?**
- Designed for real-time voice (low latency codec)
- Excellent quality at 16-24 kbps for speech
- Handles packet loss gracefully (important for VPN)
- Wide compatibility (WebRTC, VoIP systems)

**Why compression_level 0?**
- Opus encoding is CPU-intensive by default
- Level 10 (default) optimizes file size aggressively
- Level 0 still produces excellent quality for speech
- Trade-off: 4KB larger files for 5.7x faster encoding

**Why VBR over CBR?**
- Speech has variable complexity (pauses vs talking)
- VBR allocates more bits to complex segments
- Results in smaller files with better quality
- CBR wastes bits during silence

---

## Testing Command Reference

**Convert single file (fast settings):**
```bash
ffmpeg -i input.wav -c:a libopus -b:a 24k -ar 16000 -ac 1 -application voip -vbr on -compression_level 0 output.ogg -y
```

**Batch convert all VAD chunks:**
```bash
cd /home/rom/audio_wav
for file in call_*_vad_chunk_*.wav; do
  ffmpeg -i "$file" -c:a libopus -b:a 24k -ar 16000 -ac 1 -application voip -vbr on -compression_level 0 "${file%.wav}.ogg" -y
done
```

**Compare sizes:**
```bash
for file in call_*_vad_chunk_*.wav; do
  echo "$file: $(stat -c%s "$file") bytes → ${file%.wav}.ogg: $(stat -c%s "${file%.wav}.ogg") bytes"
done
```

**Test encoding speed:**
```bash
time ffmpeg -i test.wav -c:a libopus -b:a 24k -ar 16000 -ac 1 -application voip -vbr on -compression_level 0 test.ogg -y
```
