# SIM7600G-H Audio Solution

## Problem Identified

**The SIM7600G-H does NOT use USB Audio Class like EC25!**

### EC25 Audio Architecture:
- ✅ USB Audio Class device
- ✅ Enumerates as `hw:EC25AUX`
- ✅ Standard ALSA interface (arecord/aplay works)
- ✅ AT+QPCMV=1,2 enables USB audio

### SIM7600G-H Audio Architecture:
- ❌ NO USB Audio Class device
- ❌ No `hw:SIM7600` device
- ✅ Uses **serial port for raw PCM audio**
- ✅ Audio port: **/dev/ttyUSB4** (Interface 06)
- ✅ Command: **AT+CPCMREG=1** (not CUSBAUDIO!)

---

## How SIM7600 Audio Works

### 1. Audio Port Identification

The SIM7600 in PID 9011 mode creates 5 serial ports:
- ttyUSB0 (Interface 02) - Diagnostic
- ttyUSB1 (Interface 03) - GPS/NMEA
- ttyUSB2 (Interface 04) - AT Commands
- ttyUSB3 (Interface 05) - PPP/Modem
- **ttyUSB4 (Interface 06) - PCM AUDIO** ⭐

### 2. Audio Data Format

- **Sample Rate:** 8000 Hz (8kHz)
- **Bit Depth:** 16-bit signed integer
- **Channels:** 1 (Mono)
- **Encoding:** Linear PCM
- **Byte Order:** Little-endian

### 3. Audio Workflow

**During a voice call:**

1. Answer call: `ATA`
2. Wait for: `VOICE CALL: BEGIN`
3. **Enable PCM audio:** `AT+CPCMREG=1`
4. **Read audio from /dev/ttyUSB4** (raw PCM bytes)
5. **Write audio to /dev/ttyUSB4** (for playback)
6. When call ends: `AT+CPCMREG=0`

---

## Solution: Raw PCM Audio Recording

### Step 1: Enable PCM Audio During Call

```bash
# After answering call (ATA)
echo -e "AT+CPCMREG=1\r\n" > /dev/ttyUSB2  # Enable PCM on audio port
```

### Step 2: Record Audio from Serial Port

```bash
# Read raw PCM from audio port
cat /dev/ttyUSB4 > recording.raw &

# Or with timeout (30 seconds):
timeout 30 cat /dev/ttyUSB4 > recording.raw &
```

### Step 3: Convert Raw PCM to WAV (for playback)

```bash
# Convert raw PCM to WAV file
sox -r 8000 -e signed-integer -b 16 -c 1 recording.raw recording.wav
```

### Step 4: Play Audio Back During Call

```bash
# Convert WAV to raw PCM
sox input.wav -r 8000 -e signed-integer -b 16 -c 1 output.raw

# Play to caller
cat output.raw > /dev/ttyUSB4
```

---

## Python Implementation

### Simple Audio Recorder

```python
import serial
import wave

# Open audio port
audio_port = serial.Serial('/dev/ttyUSB4', baudrate=115200, timeout=1)

# Record for 30 seconds
duration = 30
sample_rate = 8000
samples_to_read = duration * sample_rate * 2  # 2 bytes per sample

# Read PCM data
pcm_data = audio_port.read(samples_to_read)

# Save as WAV
with wave.open('recording.wav', 'wb') as wf:
    wf.setnchannels(1)  # Mono
    wf.setsampwidth(2)  # 16-bit = 2 bytes
    wf.setframerate(8000)  # 8kHz
    wf.writeframes(pcm_data)

# Close port
audio_port.close()
```

### With Voice Activity Detection (VAD)

```python
import serial
import webrtcvad
import wave
import struct

# Initialize VAD
vad = webrtcvad.Vad(3)  # Aggressive mode

# Open audio port
audio_port = serial.Serial('/dev/ttyUSB4', baudrate=115200, timeout=1)

# Frame duration in ms (10, 20, or 30)
frame_duration_ms = 30
frame_size = int(8000 * frame_duration_ms / 1000) * 2  # 2 bytes per sample

audio_chunks = []
silence_frames = 0
max_silence_frames = 20  # 600ms silence = end of speech

while True:
    # Read one frame
    frame = audio_port.read(frame_size)

    if len(frame) < frame_size:
        break

    # Check for speech
    is_speech = vad.is_speech(frame, 8000)

    if is_speech:
        audio_chunks.append(frame)
        silence_frames = 0
    else:
        silence_frames += 1
        if silence_frames > max_silence_frames:
            break  # End of speech
        audio_chunks.append(frame)

# Save audio
with wave.open('recording.wav', 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(8000)
    wf.writeframes(b''.join(audio_chunks))

audio_port.close()
```

---

## Integration with ec25_voice_bot_v3.py

### Required Modifications

**File:** `/home/rom/ec25_voice_bot_v3.py`

### 1. Detect Modem Type

```python
def detect_modem_type(self):
    """Detect if EC25 or SIM7600"""
    try:
        # Check USB device
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if '2c7c:0125' in result.stdout:
            return 'EC25'
        elif '1e0e:9011' in result.stdout or '1e0e:9001' in result.stdout:
            return 'SIM7600'
    except:
        pass
    return 'UNKNOWN'
```

### 2. Enable Audio Based on Modem Type

```python
def enable_audio(self):
    """Enable audio for current modem type"""
    if self.modem_type == 'EC25':
        # EC25 uses USB Audio Class - no command needed
        self.audio_device = 'hw:EC25AUX'
        self.audio_method = 'alsa'

    elif self.modem_type == 'SIM7600':
        # SIM7600 uses serial port PCM
        self.send_at_command('AT+CPCMREG=1')
        self.audio_device = '/dev/ttyUSB4'
        self.audio_method = 'serial'
```

### 3. Record Audio Based on Method

```python
def record_audio(self):
    """Record audio using appropriate method"""
    if self.audio_method == 'alsa':
        # EC25: Use arecord
        self.audio_process = subprocess.Popen([
            'arecord',
            '-D', self.audio_device,
            '-f', 'S16_LE',
            '-r', '8000',
            '-c', '1',
            self.audio_file
        ])

    elif self.audio_method == 'serial':
        # SIM7600: Read from serial port
        self.audio_port = serial.Serial(self.audio_device, 115200, timeout=1)
        self.audio_data = []
        self.recording = True

        # Start recording thread
        self.recording_thread = threading.Thread(target=self._record_from_serial)
        self.recording_thread.start()

def _record_from_serial(self):
    """Background thread to read PCM from serial"""
    while self.recording:
        chunk = self.audio_port.read(320)  # 20ms frame at 8kHz
        if chunk:
            self.audio_data.append(chunk)
```

---

## Testing Commands

### Manual Test Sequence

```bash
# 1. Stop services
sudo systemctl stop smstools ec25-voice-bot

# 2. Answer incoming call
echo -e "ATA\r\n" | sudo picocom -b 115200 -x 2000 /dev/ttyUSB2

# 3. Enable PCM audio
echo -e "AT+CPCMREG=1\r\n" | sudo picocom -b 115200 -x 2000 /dev/ttyUSB2

# 4. Record audio (30 seconds)
timeout 30 cat /dev/ttyUSB4 > /tmp/test_audio.raw

# 5. Convert to WAV
sox -r 8000 -e signed-integer -b 16 -c 1 /tmp/test_audio.raw /tmp/test_audio.wav

# 6. Listen to recording
aplay /tmp/test_audio.wav

# 7. Hang up
echo -e "ATH\r\n" | sudo picocom -b 115200 -x 2000 /dev/ttyUSB2

# 8. Restart services
sudo systemctl start smstools ec25-voice-bot
```

---

## Comparison: EC25 vs SIM7600 Audio

| Feature | EC25-AUX | SIM7600G-H |
|---------|----------|------------|
| **Audio Interface** | USB Audio Class | Serial Port (Raw PCM) |
| **Device Name** | hw:EC25AUX | /dev/ttyUSB4 |
| **ALSA Support** | ✅ Yes | ❌ No |
| **Enable Command** | AT+QPCMV=1,2 | AT+CPCMREG=1 |
| **Recording Method** | arecord | cat / python serial |
| **Playback Method** | aplay | cat / python serial |
| **Complexity** | Low (standard ALSA) | Medium (raw PCM) |
| **VAD Integration** | Easy (PCM frames) | Easy (PCM frames) |

---

## Advantages of Serial Port Audio

1. **More control** - direct access to raw PCM data
2. **Lower latency** - no ALSA layer overhead
3. **Flexible processing** - can apply custom filters/codecs
4. **Works without ALSA** - pure Linux serial port

## Disadvantages

1. **No standard tools** - can't use arecord/aplay directly
2. **Manual format handling** - need to manage PCM format
3. **More code** - need custom recording/playback logic

---

## Next Steps

1. ✅ Research completed - understand SIM7600 audio architecture
2. **Create test script** - manual test of serial port audio recording
3. **Modify voice bot** - add SIM7600 audio support
4. **Test with real calls** - verify recording quality
5. **Integrate VAD** - add voice activity detection for SIM7600

---

## References

- SIM7100/SIM7500/SIM7600/SIM7800 Series USB AUDIO Application Note V2.00
- Linux kernel option driver (for SIM7600 serial ports)
- WebRTC VAD (for voice activity detection)
- Sox audio tool (for PCM conversion)

---

**Status:** Solution documented ✅
**Modem:** SIM7600G-H (PID 9011)
**Audio Port:** /dev/ttyUSB4
**Next Action:** Implement test script
