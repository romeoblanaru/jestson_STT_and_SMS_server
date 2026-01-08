# Audio Recording & VAD Integration Guide

## Overview

The EC25 Voice Bot now includes audio recording with WebRTC VAD (Voice Activity Detection) for intelligent speech segmentation.

## Features

### 1. Audio Recording
- **Format**: WAV, 16kHz mono, PCM 16-bit
- **Source**: ALSA default audio device via FFmpeg
- **Location**: `/home/rom/Audio_wav/`

### 2. Voice Activity Detection (WebRTC VAD)
- **Library**: WebRTC VAD (Google WebRTC project)
- **Framework**: Lightweight C library with Python bindings
- **Features**:
  - Real-time speech vs silence detection
  - Segments audio based on pauses (800ms default)
  - Optimized for telephony applications
  - Low CPU and memory footprint
  - Prepares chunks for Whisper transcription

### 3. Debug Mode
- **Enabled by default**
- Saves individual speech segments to: `/home/rom/Audio_wav/debug/`
- Toggle via `DEBUG_MODE` environment variable

## File Structure

```
/home/rom/Audio_wav/
├── call_YYYYMMDD_HHMMSS_raw.wav          # Raw recording from FFmpeg
├── call_YYYYMMDD_HHMMSS_processed.wav    # VAD-processed full audio
└── debug/
    ├── call_YYYYMMDD_HHMMSS_segment_000.wav
    ├── call_YYYYMMDD_HHMMSS_segment_001.wav
    └── call_YYYYMMDD_HHMMSS_segment_002.wav
```

## Configuration

Edit `/home/rom/vad_config.py` to adjust settings:

```python
# Key Settings
PAUSE_THRESHOLD_MS = 800      # Pause detection (milliseconds)
VAD_MODE = 3                  # Aggressiveness mode (0-3)
FRAME_DURATION_MS = 30        # Frame duration for VAD (10/20/30ms)
DEBUG_MODE = True             # Save debug segments
```

### Tuning VAD Mode

| Mode | Aggressiveness | Use Case |
|------|----------------|----------|
| 0 | Least | Clean studio audio, may catch background noise |
| 1 | Low | High-quality calls |
| 2 | Moderate | Normal calls, balanced |
| 3 | Most | **Telephony (recommended)** - filters noise aggressively |

### Tuning Pause Threshold

| Value | Behavior | Use Case |
|-------|----------|----------|
| 300-500ms | Very responsive | Quick back-and-forth conversation |
| 800ms | Balanced | **Recommended default** |
| 1000-1500ms | Patient | Allows for thinking pauses |

## How It Works

### Call Flow

1. **Ring Detection** → Voice bot takes control of modem
2. **Call Answered** → FFmpeg starts recording to WAV file
3. **Conversation** → Audio captured at 16kHz
4. **Call Ends** → FFmpeg stopped
5. **VAD Processing** → WebRTC VAD analyzes audio frame-by-frame
6. **Segmentation** → Audio split at 800ms+ pauses
7. **Storage** → Segments saved (debug mode only)
8. **Whisper Ready** → Segments queued for transcription

### VAD Processing Steps

```python
# 1. Load audio file
with wave.open("call_20251008_134500_raw.wav", 'rb') as wf:
    sample_rate = wf.getframerate()
    audio_data = wf.readframes(wf.getnframes())

# 2. Initialize WebRTC VAD
vad = webrtcvad.Vad(3)  # Mode 3 = most aggressive

# 3. Process frame by frame (30ms frames)
frame_duration_ms = 30
frame_size = int(sample_rate * frame_duration_ms / 1000) * 2

for i in range(0, len(audio_data), frame_size):
    frame = audio_data[i:i+frame_size]
    is_speech = vad.is_speech(frame, sample_rate)
    # Detect 800ms pauses to segment audio
    # Save segments for Whisper
```

## Dependencies

### Installed Packages
```bash
webrtcvad==2.0.10          # WebRTC VAD library (lightweight)
numpy==2.3.3               # Array operations
soundfile==0.13.1          # Audio I/O (optional, for advanced features)
```

### System Requirements
```bash
ffmpeg                     # Audio capture
python3-pip                # Package management
```

## Usage

### Normal Operation
Voice bot runs automatically as systemd service:
```bash
sudo systemctl status ec25-voice-bot.service
```

### Manual Testing
```bash
# Enable debug mode
export DEBUG_MODE=true
python3 /home/rom/ec25_voice_bot_v3.py
```

### Disable Debug Mode
```bash
# Disable saving audio chunks
export DEBUG_MODE=false
sudo systemctl restart ec25-voice-bot.service
```

### View Logs
```bash
# Real-time logs
journalctl -u ec25-voice-bot.service -f

# Recent logs
journalctl -u ec25-voice-bot.service -n 50
```

## Audio Files

### Raw Recording
- **File**: `call_YYYYMMDD_HHMMSS_raw.wav`
- **Content**: Full call audio as captured by FFmpeg
- **Format**: 16kHz, mono, WAV
- **Use**: Backup, debugging

### Processed Audio
- **File**: `call_YYYYMMDD_HHMMSS_processed.wav`
- **Content**: Full audio after VAD processing
- **Format**: 16kHz, mono, WAV
- **Use**: Archive, analysis

### Debug Segments (Debug Mode Only)
- **Files**: `call_YYYYMMDD_HHMMSS_segment_NNN.wav`
- **Content**: Individual speech segments
- **Naming**: Sequential 000, 001, 002...
- **Use**: Verify VAD segmentation, Whisper input

## Troubleshooting

### No Audio Files Created
```bash
# Check FFmpeg is running
ps aux | grep ffmpeg

# Check audio device
arecord -l

# Test ALSA recording
arecord -D default -f cd -d 5 test.wav
```

### VAD Not Loading
```bash
# Verify WebRTC VAD installation
python3 -c "import webrtcvad; print('WebRTC VAD OK')"

# Install if missing
pip3 install webrtcvad

# Check logs
journalctl -u ec25-voice-bot.service | grep VAD
```

### FFmpeg Errors
```bash
# Check ALSA permissions
groups rom | grep audio

# Test FFmpeg manually
ffmpeg -f alsa -i default -ar 16000 -ac 1 -t 5 test.wav
```

### Segments Not Saved
```bash
# Verify debug mode
journalctl -u ec25-voice-bot.service | grep "Debug mode"

# Check directory permissions
ls -la /home/rom/Audio_wav/debug/
```

## Whisper Integration (Future)

Currently implemented as placeholder:
```python
def prepare_for_whisper(self, audio_segment, segment_id):
    """Prepare audio segment for Whisper transcription"""
    duration = len(audio_segment) / self.sample_rate
    print(f"Segment {segment_id} ready for Whisper: {duration:.2f}s")
```

When Whisper is installed, this function will:
1. Queue audio segment for transcription
2. Send to Whisper model
3. Return transcribed text
4. Trigger conversation flow

## Performance Notes

### CPU Usage
- VAD processing: ~1-2 seconds per call minute (RPi 4)
- Real-time recording: Minimal overhead
- Segmentation: Post-call processing

### Storage
- Raw audio: ~1.9 MB per minute (16kHz WAV)
- Processed: Same size as raw
- Segments: Variable, typically 2-10 KB each

### Memory
- WebRTC VAD: ~1-2 MB RAM
- Audio buffer: <10 MB per call
- Total overhead: ~30 MB (down from ~200MB with Silero)

## Example Output

```
Ring 1 detected at 13:45:00
Answering call after 1 ring...
Stopping SMS daemon to take control of modem...
Voice bot has control of /dev/ttyUSB2
Sending ATA command...
Call answered - conversation active
Audio recording started for call: 20251008_134500
FFmpeg capturing to: /home/rom/Audio_wav/call_20251008_134500_raw.wav
Starting active call monitoring...
Call ended detected (no active calls)
Ending call...
FFmpeg recording stopped
Processing audio with WebRTC VAD: call_20251008_134500_raw.wav
Processing 2000 frames (30ms each)
Found 15 speech segments
Segment 1: Pause detected: 1.24s
Saved segment 0 to: call_20251008_134500_segment_000.wav (3.45s)
Segment 1 ready for Whisper
Segment 2: Pause detected: 0.95s
Saved segment 1 to: call_20251008_134500_segment_001.wav (2.12s)
Segment 1 ready for Whisper
...
Full processed audio saved: call_20251008_134500_processed.wav
Call terminated, SMS daemon restored
```

## Configuration Examples

### Quick Response (300ms pause)
```python
PAUSE_THRESHOLD_MS = 300
FRAME_DURATION_MS = 20  # Shorter frames for responsiveness
VAD_MODE = 2  # Moderate filtering
```

### Patient Conversation (1.5s pause)
```python
PAUSE_THRESHOLD_MS = 1500
FRAME_DURATION_MS = 30
VAD_MODE = 2  # Moderate filtering
```

### Noisy Environment
```python
PAUSE_THRESHOLD_MS = 800
FRAME_DURATION_MS = 30
VAD_MODE = 3  # Most aggressive filtering (recommended)
```

### Quiet/Clean Environment
```python
PAUSE_THRESHOLD_MS = 800
FRAME_DURATION_MS = 30
VAD_MODE = 1  # Low aggressive, more sensitive
```

## References

- [WebRTC VAD GitHub](https://github.com/wiseman/py-webrtcvad)
- [Google WebRTC VAD](https://chromium.googlesource.com/external/webrtc/+/branch-heads/43/webrtc/common_audio/vad/)
- [FFmpeg ALSA Documentation](https://ffmpeg.org/ffmpeg-devices.html#alsa)
- [Whisper GitHub](https://github.com/openai/whisper) (for future integration)

## WebRTC VAD Migration (October 2025)

**Important:** This system has been migrated from **Silero VAD** to **WebRTC VAD** as of October 13, 2025.

### Why the Change?
- **2x faster processing** (1-2s vs 2-5s per minute)
- **6x lower memory usage** (30MB vs 200MB)
- **Simpler deployment** (no PyTorch/ONNX dependencies)
- **Telephony-optimized** (designed for 8/16kHz voice calls)

### Key Differences
- **Silero**: Deep learning model, probability scores (0.0-1.0), flexible
- **WebRTC**: Rule-based algorithm, boolean output, fixed frames (10/20/30ms)

### When to Use Each
- ✅ **WebRTC VAD**: Clean telephony audio, real-time processing (default)
- ❌ **Silero VAD**: Very noisy audio, advanced features (only if explicitly needed)

### Terminology Note
⚠️ **Always clarify when discussing VAD:**
- User says "VAD" or "vad silero" → **Ask: "WebRTC VAD or Silero VAD?"**
- User might say "silero" out of habit when referring to current WebRTC implementation
- **Default**: WebRTC VAD

For complete migration details: `/home/rom/docs/WEBRTC_VAD_MIGRATION.md`
