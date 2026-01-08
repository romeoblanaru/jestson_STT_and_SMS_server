# Audio Output Locations

## Persistent Audio Recordings (WAV format)
**Location**: `/home/rom/audio_wav/`

**What's saved here**:
1. **Incoming raw audio**: `call_XXXXX_incoming_raw_TIMESTAMP.wav`
   - Raw PCM audio from caller (before VAD processing)
   - Continuous stream from call start to end
   - 8kHz, 16-bit, mono

2. **Incoming VAD chunks**: `call_XXXXX_incoming_vad_chunks_TIMESTAMP.wav`
   - Only the chunks detected as speech by WebRTC VAD
   - Exact audio sent to Whisper for transcription
   - Useful for debugging VAD sensitivity

3. **Outgoing TTS audio**: `call_XXXXX_outgoing_tts_TIMESTAMP.wav`
   - All Azure TTS audio sent to caller
   - Combined stream of all bot responses
   - Useful for debugging welcome message silence/noise issues

**Usage**:
```bash
# List all audio recordings
ls -lh /home/rom/audio_wav/

# Play on computer (transfer via scp)
scp rom@pi:/home/rom/audio_wav/*.wav .

# Analyze in Audacity or similar tool
```

## Temporary TTS Files (RAW PCM format)
**Location**: `/tmp/tts_CALLID_TIMESTAMP.raw`

**What's saved here**:
- Raw PCM audio from Azure TTS (before playback)
- **Automatically deleted** after being played to caller
- 8kHz, 16-bit signed, little-endian, mono
- These are temporary working files, NOT for analysis

**Note**: These files are captured and saved to `/home/rom/audio_wav/` as WAV format by the audio recorder, so you don't need to access them directly.

## Call Profiling Data (JSON format)
**Location**: `/var/log/voice_bot_ram/call_profiles/`
**Shortcut**: `/home/rom/timing_analysis/` (symlink)

**What's saved here**:
- Millisecond-precision timing for all events during call
- TTS latencies (time to first chunk, total processing time)
- VAD chunk detection timing
- Whisper transcription latencies
- Complete event timeline

**Usage**:
```bash
# View all call profiles (shortcut)
cat ~/timing_analysis/call_*.json | jq .

# View latest call only
cat ~/timing_analysis/call_*.json | tail -1 | jq .

# Extract TTS latencies
cat ~/timing_analysis/call_*.json | jq '.summary.tts_avg_latency_ms'

# View summary stats
cat ~/timing_analysis/call_*.json | jq '.summary'

# List all profiles
ls -lh ~/timing_analysis/
```

## Logs (Text format)
**TTS API logs**: `/var/log/voice_bot_ram/unified_api.log`
- Azure TTS timing: "⏱️ First TTS chunk received in XXXms"
- Total processing time: "📁 TTS audio saved to..."

**Voice bot logs**: `/var/log/voice_bot_ram/sim7600_voice_bot.log`
- Call events, VAD detection, audio playback

## Summary of Audio Flow

```
1. Caller speaks → /home/rom/audio_wav/incoming_raw.wav
                 ↓
2. VAD detects speech → /home/rom/audio_wav/incoming_vad_chunks.wav
                       ↓
3. Whisper transcribes → (timing in call_profile JSON)
                        ↓
4. VPS generates response → (timing in unified_api.log)
                          ↓
5. Azure TTS generates audio → /tmp/tts_*.raw (temporary)
                             ↓
6. Audio played to caller → /home/rom/audio_wav/outgoing_tts.wav
```

## Debugging Welcome Message Issues

**Problem**: Silence or noise at start of call

**Debug steps**:
1. **Check TTS output**: Listen to `outgoing_tts.wav` - does it start with silence/noise?
2. **Check TTS latency**: `grep "First TTS chunk" /var/log/voice_bot_ram/unified_api.log`
3. **Check call profile**: Look for delays in TTS request timing
4. **Analyze in Audacity**: Import `outgoing_tts.wav` and visualize waveform

**Expected behavior**:
- TTS first chunk: <500ms (Azure streaming)
- Audio should start immediately with voice (no leading silence)
- No noise artifacts at beginning
