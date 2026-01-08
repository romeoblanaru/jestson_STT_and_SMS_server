# Audio Hardware Requirements for EC25 Voice Bot

## Current Status

**Call Handling**: ✅ Working (answers calls, detects hangup)
**Audio Recording**: ❌ Not functional (no audio hardware)

## Problem

The EC25 modem does **not** expose a USB audio interface that can be captured directly by ALSA/FFmpeg. The modem handles voice calls internally, but the audio stream is not available to the Raspberry Pi without additional hardware or configuration.

## Why FFmpeg Fails

```
arecord -l
**** List of CAPTURE Hardware Devices ****
(empty - no capture devices)
```

The Raspberry Pi 4 has:
- HDMI audio output
- Headphone jack output
- **NO microphone/audio input**

The EC25 modem has:
- Internal voice processing
- PCM audio pins (hardware level)
- **NO USB audio streaming**

## Solutions

### Option 1: External USB Sound Card (Recommended for Testing)

**Hardware needed:**
- USB sound card with microphone input (~$5-15)
- 3.5mm audio cable
- EC25 audio breakout board OR direct PCM wiring

**Steps:**
1. Connect EC25 PCM audio pins to USB sound card input
2. Configure ALSA to use USB sound card
3. Update FFmpeg to use correct ALSA device

**Pros:**
- Simple hardware solution
- Works with existing FFmpeg code
- Good for testing

**Cons:**
- Requires hardware purchase
- Manual wiring needed
- Audio quality depends on connection

### Option 2: PJSUA SIP Bridge (Original Design)

**Configuration needed:**
- Route EC25 calls through PJSUA
- Configure PJSUA to handle EC25 audio
- Record from PJSUA's audio stream

**Steps:**
1. Configure PJSUA to connect with EC25
2. Set up audio routing in PJSUA config
3. Use PJSUA's built-in recording features

**Pros:**
- Software-only solution
- Professional audio handling
- PJSUA config already exists (`/home/rom/pjsua_config.cfg`)

**Cons:**
- More complex setup
- Requires SIP configuration
- May have latency

### Option 3: AT Command Internal Recording

**EC25 modem can record audio internally:**
```
AT+QAUDMOD=1               # Enable audio recording
AT+QAUDRD=1,"filename.wav" # Start recording
AT+QAUDRD=0                # Stop recording
AT+QFREAD="filename.wav"   # Retrieve file
```

**Pros:**
- No additional hardware needed
- Modem handles everything
- File is already in correct format

**Cons:**
- Limited storage on modem
- Must retrieve file after call
- Less real-time processing

### Option 4: Dummy Audio for Testing (Current Implementation)

**What's happening now:**
- Calls are answered and managed correctly
- Audio recording is skipped (no hardware)
- VAD/Whisper pipeline ready but not processing

**Temporary solution:**
- Voice bot manages calls successfully
- Can test Whisper with pre-recorded audio files
- Add proper audio hardware later

## Recommended Next Steps

### ✅ CHOSEN SOLUTION: Option 2 - PJSUA SIP Bridge

**This is the only viable option for real-time conversational bot.**

**Why PJSUA:**
- Real-time audio streaming (required for conversation flow)
- Software-only solution (no hardware needed)
- Professional audio handling
- Existing PJSUA config already in place
- Can process audio while call is active (not post-call)

**Implementation Plan:**
1. Configure PJSUA to handle EC25 calls
2. Set up audio routing through PJSUA
3. Capture audio stream in real-time
4. Feed to VAD for live segmentation
5. Send segments to Whisper as they complete
6. Generate responses and continue conversation

**Next Steps:**
1. Review existing PJSUA configuration
2. Configure EC25 modem to work with PJSUA
3. Set up audio capture from PJSUA
4. Integrate with VAD for real-time processing
5. Test call with live audio streaming

## Current System Status

```
┌────────────────────────────────────────┐
│ Voice Bot Status                       │
├────────────────────────────────────────┤
│ ✅ Ring detection working              │
│ ✅ Call answering working (2 rings)    │
│ ✅ Hangup detection working (1 sec)    │
│ ✅ SMS daemon handover working         │
│ ✅ Silero VAD loaded and ready         │
│ ❌ Audio capture: NO HARDWARE          │
│ ⏳ Whisper: Ready when audio available │
└────────────────────────────────────────┘
```

## Testing Without Audio Hardware

You can still test the VAD and Whisper pipeline:

### 1. Record test audio on your phone
```bash
# Transfer a WAV file to the Pi
scp test_audio.wav rom@pi:/home/rom/Audio_wav/call_test_raw.wav
```

### 2. Process with VAD manually
```python
from pathlib import Path
from silero_vad import load_silero_vad, get_speech_timestamps, read_audio
import soundfile as sf

# Load model and audio
model = load_silero_vad()
wav = read_audio("/home/rom/Audio_wav/call_test_raw.wav", sampling_rate=16000)

# Get segments
segments = get_speech_timestamps(
    wav, model,
    sampling_rate=16000,
    min_silence_duration_ms=800
)

# Save segments
for i, seg in enumerate(segments):
    audio_seg = wav[seg['start']:seg['end']]
    sf.write(f"/home/rom/Audio_wav/debug/test_segment_{i:03d}.wav",
             audio_seg.numpy(), 16000)
```

### 3. Test Whisper integration (when installed)
```bash
# Process segments through Whisper
whisper /home/rom/Audio_wav/debug/test_segment_000.wav --model base --language en
```

## EC25 Audio Pins (Hardware Reference)

If you go with Option 1 (USB sound card):

```
EC25 PCM Audio Pins:
- Pin 47: PCM_OUT (audio from modem)
- Pin 48: PCM_IN  (audio to modem)
- Pin 49: PCM_CLK (clock)
- Pin 50: PCM_SYNC (frame sync)
- GND: Ground
```

You'll need:
1. EC25 breakout board or careful soldering
2. PCM to Line Level converter (or USB sound card with PCM support)
3. Proper wiring and testing

## Configuration Files

Current system files:
- `/home/rom/ec25_voice_bot_v3.py` - Voice bot (audio disabled)
- `/home/rom/pjsua_config.cfg` - PJSUA config (not active)
- `/home/rom/vad_config.py` - VAD settings (ready)

## Summary - UPDATED October 8, 2025

### 🎉 BREAKTHROUGH: EC25 USB Audio Successfully Enabled!

The voice bot is **fully functional for call handling** AND **now has real-time audio capture!**

**What Changed:**
- ❌ Option 1 (USB sound card) - NOT needed
- ✅ **Option 2 (Direct USB Audio)** - IMPLEMENTED successfully
- ❌ Option 3 (PJSUA) - NOT needed (was wrong approach)

### Implementation Completed

The EC25 modem now exposes a **USB Audio Class (UAC)** interface that appears as a standard ALSA sound card.

**Configuration Applied:**
```bash
AT+QCFG="USBCFG",0x2C7C,0x0125,1,1,1,1,1,1,1  # Enable UAC mode
AT+QPCMV=1,2                                   # Route audio to USB
AT+CFUN=1,1                                    # Reboot to apply
```

**Result:**
- ✅ Audio device: `hw:EC25AUX` (or `hw:3,0`)
- ✅ Sample rate: 8000 Hz
- ✅ Format: S16_LE mono
- ✅ Real-time bidirectional streaming
- ✅ No external hardware needed
- ✅ No PJSUA/Asterisk complexity

### Architecture (Final - Simplified)

```
Incoming Call → EC25 Modem → USB Audio Interface (hw:EC25AUX)
                                      ↓
                              ALSA → Python sounddevice
                                      ↓
                              Silero VAD (real-time)
                                      ↓
                              Whisper ASR
                                      ↓
                              Bot Logic
                                      ↓
                              TTS Response
                                      ↓
                              sounddevice → ALSA → EC25 → Caller
```

### Status

✅ **Call Handling**: Working
✅ **Audio Capture**: Working
✅ **Audio Playback**: Working
✅ **Silero VAD**: Ready
⏳ **Whisper Integration**: Next step
⏳ **Real-time conversation**: Ready to implement

### Documentation

- **Complete Setup Guide**: `/home/rom/docs/EC25_USB_AUDIO_SETUP.md`
- **Test Script**: `/home/rom/to_test/test_ec25_audio.py`
- **PDF Reference**: `/home/rom/docs/Quectel EC25 Modem.pdf`

### Testing

```bash
# Test audio capture
python3 /home/rom/to_test/test_ec25_audio.py

# Then call the modem and speak - you'll see audio levels!
```

**The path forward is clear: Direct USB Audio streaming enables real-time conversational bot without any external hardware or complex VoIP configuration!** 🚀
