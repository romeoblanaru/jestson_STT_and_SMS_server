# Audio Configuration & Characteristics

**Document Date:** October 26, 2025
**Version:** v3.1 - Caller-First Conversation Flow
**Last Successful Call:** call_1761503579

---

## Table of Contents
1. [Audio File Characteristics](#audio-file-characteristics)
2. [Current Configuration](#current-configuration)
3. [Conversation Flow Settings](#conversation-flow-settings)
4. [Silence Detection Thresholds](#silence-detection-thresholds)
5. [Discussion: Welcome Message vs VAD Chunking Timeout](#discussion-welcome-message-vs-vad-chunking-timeout)

---

## Audio File Characteristics

### Sample Call: call_1761503579 (Oct 26, 2025 18:32:59)

**Overall Call Stats:**
- **Total Duration:** 22.8 seconds
- **VAD Chunks Saved:** 4 separate files
- **Welcome Message Triggered:** After 6.6 seconds (896ms speech detected)
- **Audio Quality:** Clear and audible ✅

---

### Incoming Raw Audio (Complete Call Recording)

**File:** `call_1761503579_incoming_raw_1761503581.wav`

```
Format:             WAVE audio, Microsoft PCM
Sample Rate:        16000 Hz (16 kHz)
Bit Depth:          16-bit
Channels:           Mono
File Size:          485 KB
Duration:           15.5 seconds
Samples:            248,000

Audio Levels:
- Maximum amplitude:  0.362 (36.2% of full scale)
- Minimum amplitude: -0.350 (35.0% of full scale)
- RMS amplitude:      0.023 (2.3% - includes silence periods)
- Mean norm:          0.0056
```

**Characteristics:**
- Clean audio capture with good dynamic range
- Relatively low RMS due to silence periods between speech
- Peak levels indicate healthy speech input without clipping
- No saturation (max amplitude well below 1.0)

---

### Outgoing TTS Audio (Bot's Voice)

**File:** `call_1761503579_outgoing_tts_1761503581.wav`

```
Format:             WAVE audio, Microsoft PCM
Sample Rate:        16000 Hz (16 kHz)
Bit Depth:          16-bit
Channels:           Mono
File Size:          81 KB
Duration:           2.57 seconds
Samples:            41,169

Audio Levels:
- Maximum amplitude:  0.417 (41.7% of full scale)
- Minimum amplitude: -0.502 (50.2% of full scale)
- RMS amplitude:      0.083 (8.3% - continuous speech)
- Mean norm:          0.038
- Maximum delta:      0.693 (large dynamics)
```

**Characteristics:**
- Azure TTS voice (Romanian, female)
- Higher RMS than incoming (continuous speech, no pauses)
- Good dynamic range with natural-sounding variations
- No clipping (max amplitude < 1.0)
- Large maximum delta indicates expressive TTS output

---

### VAD Chunk #1 (First Utterance - Too Short)

**File:** `call_1761503579_vad_chunk_1_1761503583.wav`

```
Duration:           0.61 seconds (599ms actual speech)
File Size:          20 KB
Samples:            9,760

Audio Levels:
- Maximum amplitude:  0.362
- Minimum amplitude: -0.350
- RMS amplitude:      0.048
- Mean norm:          0.022
```

**Analysis:**
- **Result:** Too short for welcome message (< 680ms threshold)
- System waited for longer utterance
- Clean speech segment saved correctly

---

### VAD Chunk #2 (Second Utterance - Triggered Welcome)

**File:** `call_1761503579_vad_chunk_2_1761503585.wav`

```
Duration:           0.92 seconds (896ms actual speech)
File Size:          29 KB
Samples:            14,720

Audio Levels:
- Maximum amplitude:  0.335
- Minimum amplitude: -0.290
- RMS amplitude:      0.054
- Mean norm:          0.030
```

**Analysis:**
- **Result:** ✅ Triggered welcome message (896ms > 680ms threshold)
- Followed by 600ms pause → bot played greeting
- Good speech quality with consistent amplitude

---

### VAD Chunk #3 (Longest Response)

**File:** `call_1761503579_vad_chunk_3_1761503589.wav`

```
Duration:           2.07 seconds (2059ms speech)
File Size:          65 KB
Samples:            33,120

Audio Levels:
- Maximum amplitude:  0.343
- Minimum amplitude: -0.246
- RMS amplitude:      0.040
- Mean norm:          0.018
```

**Analysis:**
- Caller's response after hearing welcome message
- Longest continuous speech segment in call
- Slightly lower RMS (more varied speech pattern)

---

### VAD Chunk #4 (Final Utterance)

**File:** `call_1761503579_vad_chunk_4_1761503591.wav`

```
Duration:           0.65 seconds (638ms speech)
File Size:          21 KB
Samples:            10,400

Audio Levels:
- Maximum amplitude:  Similar to other chunks
- Consistent quality throughout call
```

---

## Current Configuration

### Audio Format Settings

**Sample Rate:** Dynamic (configured from VPS webhook)
- **8kHz:** Default fallback (AT+CPCMFRM=0)
- **16kHz:** Used when `audio_format` contains "Raw16Khz16BitMonoPc" (AT+CPCMFRM=1)
- **Current Active:** 16kHz (Romanian voice config)

**Bit Depth:** 16-bit PCM (signed integer, little-endian)

**Channels:** Mono

**Audio Port:** `/dev/ttyUSB4` (serial PCM audio from SIM7600)

---

### AT Commands for Audio

**Initialization (startup):**
```
AT+CLVL=5              # Speaker volume (output only, 0-9 scale)
AT+CPCMFRM=1           # PCM format: 1=16kHz, 0=8kHz
```

**During Call:**
```
AT+CPCMREG=1           # Enable PCM audio routing to ttyUSB4
```

**Call Cleanup:**
```
AT+CPCMREG=0           # Disable PCM audio
```

**Note:** No microphone gain commands currently used (AT+CMIC, AT+CMUT not configured)

---

### Recording Configuration

**Raw Audio Recorder:**
- **Gain:** 1.0 (no software amplification)
- **Output:** `/home/rom/audio_wav/call_XXX_incoming_raw_TIMESTAMP.wav`
- **Purpose:** Complete call recording (continuous)

**VAD Chunk Recorder:**
- **Method:** Separate WAV file per speech segment
- **Output:** `/home/rom/audio_wav/call_XXX_vad_chunk_N_TIMESTAMP.wav`
- **Purpose:** Individual utterances for transcription

**TTS Playback Recorder:**
- **Gain:** 1.0 (no amplification)
- **Output:** `/home/rom/audio_wav/call_XXX_outgoing_tts_TIMESTAMP.wav`
- **Purpose:** Record what bot said to caller

---

## Conversation Flow Settings

### Call Answer & Initialization

**Answer Mode:** Instant (answer on first RING)
- No fake rings playback
- Immediate ATA command (< 100ms)

**Extra Added Delay:** 2 seconds
- **Purpose:** Allow Silero VAD initialization and audio system preparation
- **Event Name:** `extra_added_delay` (not `call_fully_established`)
- **Timing:** Between ATA and AT+CPCMREG=1

**PCM Enable:** AT+CPCMREG=1
- **Timeout:** 3 seconds
- **Typical Duration:** ~800ms
- **Total ATA → PCM Ready:** ~2.8 seconds

---

### Caller-First Flow

**Initial State:**
```python
caller_is_silent.clear()        # NOT set - waiting for caller
caller_has_spoken = False       # No speech detected yet
pending_welcome_message = "..."  # Stored, not played
```

**Conversation Sequence:**
1. **Call answered** → 2s initialization delay
2. **Bot listens silently** → Waiting for caller to speak
3. **Caller speaks** → Speech detection starts
4. **Speech tracking:**
   - Mark `caller_has_spoken = True` on first speech
   - Monitor speech duration
5. **Pause detection (600ms):**
   - If speech duration ≥ 680ms → Play welcome message
   - If speech duration < 680ms → Wait for longer utterance
6. **Welcome message plays** → Clear `pending_welcome_message`
7. **Normal conversation continues** → VAD chunking and transcription

---

## Silence Detection Thresholds

### Multi-Tier VAD System

**WebRTC VAD Settings:**
- **Mode:** 3 (most aggressive - telephony-optimized)
- **Frame Size:** 20ms (320 bytes at 8kHz, 640 bytes at 16kHz)
- **Sample Rate:** Matches call configuration (8kHz or 16kHz)

---

### Tier 1: Normal Pause (End of Utterance)

**Threshold:** 550ms silence (27-28 frames × 20ms) ⚠️ **Experimental**

**Purpose:**
- Detect end of caller's utterance
- Trigger VAD chunk save
- Set `caller_is_silent` flag (bot can speak)
- **Trigger welcome message** (if first utterance ≥ 680ms)

**Configuration:**
```python
normal_pause_ms = self.voice_config.get('silence_timeout', 550)  # Default: 550ms (testing)
```

**Change Note:** Reduced from 600ms on Oct 26, 2025 for responsiveness testing.

**Behavior:**
- Requires minimum 10 frames (200ms) of speech before detecting pause
- Saves audio chunk to separate WAV file
- Allows bot to respond

---

### Tier 2: Phrase Pause (Progressive Transcription)

**Threshold:** 350ms silence (17 frames × 20ms)

**Purpose:**
- Detect phrase boundaries during long speech (> 4.5s)
- Enable progressive transcription without interrupting caller
- Send intermediate chunks every ~4.5 seconds

**Configuration:**
```python
phrase_pause_ms = self.voice_config.get('phrase_pause_ms', 350)  # Default: 350ms
long_speech_threshold_ms = 4500  # Activate after 4.5s of continuous speech
```

**Behavior:**
- Does NOT set `caller_is_silent` flag (caller still speaking)
- Sends chunk to transcription queue
- Continues collecting audio without interruption

---

### Tier 3: Maximum Speech Duration (Noise Timeout)

**Threshold:** 6500ms continuous speech

**Purpose:**
- Prevent runaway VAD from background noise
- Detect prolonged noise (not genuine speech)
- Protect system from infinite speech detection

**Configuration:**
```python
max_speech_duration_ms = self.voice_config.get('max_speech_duration_ms', 6500)  # Default: 6.5s
```

**Behavior:**
- If speech exceeds 6.5s, assume background noise
- Set `caller_is_silent` flag
- Play error message: "Sorry, it's too noisy and I can't understand..."
- Discard buffered audio

---

### Welcome Message Trigger

**Special Condition:** First utterance detection

**Requirements:**
1. `caller_has_spoken = True` (first speech detected)
2. `pending_welcome_message` is set (not None)
3. Speech duration ≥ 680ms (minimum valid utterance)
4. Normal pause detected (550ms silence) ⚠️ **Experimental**

**Threshold:** 680ms minimum speech

**Rationale:**
- Prevents false triggers from short sounds (coughs, background noise)
- Validates genuine caller engagement
- Ensures welcome message plays after meaningful speech

**Example Timeline:**
```
0.0s  - Call answered
2.0s  - PCM enabled, listening starts
3.0s  - Caller speaks (599ms) → 550ms pause → TOO SHORT, wait
4.5s  - Caller speaks again (896ms) → 550ms pause → ✅ PLAY WELCOME MESSAGE
```

---

## Discussion: Welcome Message vs VAD Chunking Timeout

### Current Configuration ⚠️ Updated Oct 26, 2025

**Welcome Message Pause:** 550ms (same as VAD normal pause) - **Testing**
**VAD Chunking Pause:** 550ms (Tier 1 threshold) - **Testing**
**Minimum Speech Duration:** 680ms (welcome message only)

**Status:** ✅ Currently aligned (both use 550ms experimental value)
**Previous:** Both used 600ms (worked well, reducing for responsiveness test)

---

### Question: Should We Lower the Welcome Message Timeout?

#### Option 1: Keep Current (600ms for both)

**Advantages:**
- ✅ Consistent behavior - welcome message uses same detection as VAD chunks
- ✅ Well-tested threshold (600ms is standard for telephony pause detection)
- ✅ Allows bot to respond quickly after caller finishes speaking
- ✅ Natural conversation feel

**Disadvantages:**
- ⚠️ Might be slightly slow for very brief caller greetings
- ⚠️ 600ms pause feels longer on phone than in-person

**Recommendation:** **Keep as-is** unless user feedback indicates slowness

---

#### Option 2: Lower Welcome Timeout to 350ms (Match Phrase Pause)

**Advantages:**
- ⚡ Faster response (350ms vs 600ms = 250ms time savings)
- ⚡ More responsive feel for short greetings
- 🔄 Reuses existing Tier 2 threshold (no new config needed)

**Disadvantages:**
- ❌ **DANGER:** May trigger mid-sentence (caller takes natural breath)
- ❌ Bot interrupts caller during normal speech pauses
- ❌ Phrase pause (350ms) designed for LONG speech, not initial greeting
- ❌ Creates inconsistent behavior (greeting at 350ms, rest at 600ms)

**Recommendation:** **Do NOT implement** - will cause interruptions

---

#### Option 3: Lower Welcome Timeout to 400-500ms (Middle Ground)

**Advantages:**
- ⚡ Moderately faster than 600ms
- ✅ Still safe from mid-sentence triggering
- ✅ Good balance between speed and reliability

**Disadvantages:**
- ⚠️ Adds another configurable threshold (complexity)
- ⚠️ Minimal improvement (only 100-200ms faster)
- ⚠️ Not significantly better than 600ms

**Recommendation:** **Consider if user feedback requests faster greeting**

---

#### Option 4: Dynamic Timeout Based on Speech Energy

**Concept:**
- Detect end of speech using both silence AND energy drop
- Higher confidence = faster trigger
- Lower confidence = wait full 600ms

**Advantages:**
- 🎯 More intelligent detection
- ⚡ Fast response when speech clearly ended
- ✅ Safe fallback when uncertain

**Disadvantages:**
- 🔧 Complex implementation
- 🧪 Requires extensive testing
- ⚠️ May introduce edge cases

**Recommendation:** **Future enhancement** (not current priority)

---

### Final Recommendation ⚠️ Updated Oct 26, 2025

**Current testing configuration:**
- Welcome message timeout: 550ms (same as VAD normal pause) - **Experimental**
- Minimum speech duration: 680ms
- VAD chunking: 550ms - **Experimental**

**Rationale for testing 550ms:**
1. Original 600ms worked well (proven in call_1761503579)
2. 550ms = 8% faster response time (50ms improvement)
3. Still safe from mid-sentence interruption (significantly above 350ms phrase pause)
4. Good middle ground between speed and reliability

**Monitoring during test period:**
- ✅ Collect user feedback on perceived responsiveness
- ⚠️ Watch for false triggers (bot interrupting mid-sentence)
- 📊 Compare call quality metrics vs 600ms baseline

**Rollback to 600ms if:**
- Bot interrupts callers mid-sentence
- No noticeable improvement in responsiveness
- User feedback is negative

**Avoid:** 350ms (too aggressive, will cause interruptions)

---

## Configuration Summary Table

| Parameter | Current Value | Purpose | Configurable? |
|-----------|---------------|---------|---------------|
| **Sample Rate** | 16kHz (dynamic) | Audio quality | ✅ Via VPS webhook |
| **Bit Depth** | 16-bit | Audio quality | ❌ Fixed |
| **Extra Delay** | 2000ms | VAD initialization | ❌ Hardcoded |
| **Normal Pause** | 550ms ⚠️ | End of utterance | ✅ Via `silence_timeout` |
| **Phrase Pause** | 350ms | Progressive transcription | ✅ Via `phrase_pause_ms` |
| **Max Speech** | 6500ms | Noise timeout | ✅ Via `max_speech_duration_ms` |
| **Min Speech (Welcome)** | 680ms | Valid greeting | ❌ Hardcoded |
| **Welcome Timeout** | 550ms ⚠️ | Same as normal pause | ✅ Via `silence_timeout` |

⚠️ **Note:** Changed from 600ms to 550ms on Oct 26, 2025 for testing. See "Experimental Changes" section below.

---

## Audio Quality Checklist

**✅ Working Correctly:**
- Sample rate detection (8kHz vs 16kHz)
- PCM audio capture from ttyUSB4
- WebRTC VAD speech detection
- Multi-tier silence detection
- Separate VAD chunk files
- TTS playback recording
- Audio levels (no clipping, good dynamic range)

**⚠️ Not Currently Configured:**
- Microphone gain control (AT+CMIC)
- Microphone mute check (AT+CMUT)
- Software gain amplification (hardcoded to 1.0)

**🔧 Future Enhancements:**
- Software gain boost for quiet callers (1.5x or 2.0x)
- Dynamic VAD sensitivity based on ambient noise
- Echo cancellation (if needed for full-duplex)

---

## Experimental Changes

### October 26, 2025 - 18:55 UTC

**Change:** Reduced normal pause detection from 600ms to 550ms

**Rationale:**
- Original 600ms configuration worked well (proven in call_1761503579)
- Testing 550ms to evaluate responsiveness improvement
- 50ms reduction (8% faster) should maintain safety while feeling more responsive
- Still well above 350ms phrase pause threshold (no risk of mid-sentence interruption)

**Impact:**
- **Normal VAD chunking:** 600ms → 550ms (all regular speech segments)
- **Welcome message trigger:** 600ms → 550ms (same threshold)
- **Phrase pause:** 350ms (unchanged - only for long speech)
- **Max speech:** 6500ms (unchanged)

**Testing Period:**
- Monitor for false triggers (bot interrupting mid-sentence)
- Collect user feedback on perceived responsiveness
- Compare call quality metrics

**Expected Outcome:**
- Faster bot response (50ms improvement)
- No increase in interruptions (550ms still safe)
- More natural conversation flow

**Rollback Criteria:**
- If bot interrupts callers mid-sentence → revert to 600ms
- If no noticeable improvement → revert to 600ms
- If user feedback is negative → revert to 600ms

**Configuration:**
```python
normal_pause_ms = self.voice_config.get('silence_timeout', 550)  # Changed from 600
```

---

**Document Maintained By:** Claude Code
**Last Updated:** October 26, 2025
