# Quick Reference - Voice Bot with VAD

## Check Status

```bash
# Service status
systemctl status ec25-voice-bot.service

# Live logs
journalctl -u ec25-voice-bot.service -f

# Recent logs (last 50 lines)
journalctl -u ec25-voice-bot.service -n 50
```

## Control Service

```bash
# Restart with new settings
sudo systemctl restart ec25-voice-bot.service

# Stop service
sudo systemctl stop ec25-voice-bot.service

# Start service
sudo systemctl start ec25-voice-bot.service
```

## Audio Files Location

```bash
# Main directory
ls -lh /home/rom/Audio_wav/

# Debug segments
ls -lh /home/rom/Audio_wav/debug/

# Latest files
ls -lht /home/rom/Audio_wav/ | head -10
```

## Debug Mode Control

```bash
# Enable debug mode (saves audio chunks)
echo "DEBUG_MODE=true" | sudo tee -a /etc/environment
sudo systemctl restart ec25-voice-bot.service

# Disable debug mode (no chunks saved)
echo "DEBUG_MODE=false" | sudo tee -a /etc/environment
sudo systemctl restart ec25-voice-bot.service
```

## Test Audio Recording

```bash
# Run comprehensive test
python3 /home/rom/to_test/test_vad_audio.py

# Quick FFmpeg test (5 seconds)
ffmpeg -f alsa -i default -ar 16000 -ac 1 -t 5 test.wav

# Quick ALSA test
arecord -D default -f cd -d 5 -t wav test.wav
```

## Configuration

```bash
# Edit VAD settings
nano /home/rom/vad_config.py

# Main settings to adjust:
# - PAUSE_THRESHOLD_MS = 800    (pause detection)
# - VAD_THRESHOLD = 0.5         (sensitivity)
# - DEBUG_MODE = True           (save chunks)
```

## Common Adjustments

### More Responsive (shorter pauses)
```python
PAUSE_THRESHOLD_MS = 500
MIN_SILENCE_DURATION_MS = 500
```

### Less Responsive (longer pauses)
```python
PAUSE_THRESHOLD_MS = 1200
MIN_SILENCE_DURATION_MS = 1200
```

### More Sensitive (quiet speech)
```python
VAD_THRESHOLD = 0.4
```

### Less Sensitive (noisy environment)
```python
VAD_THRESHOLD = 0.6
```

## File Naming Pattern

```
call_YYYYMMDD_HHMMSS_raw.wav          - Original FFmpeg recording
call_YYYYMMDD_HHMMSS_processed.wav    - VAD processed full audio
call_YYYYMMDD_HHMMSS_segment_NNN.wav  - Individual segments (debug mode)
```

## Troubleshooting

### No audio files created
```bash
# Check FFmpeg is installed
ffmpeg -version

# Check ALSA devices
arecord -l

# Test audio capture
arecord -D default -d 3 test.wav && aplay test.wav
```

### VAD not working
```bash
# Check Silero installation
python3 -c "from silero_vad import load_silero_vad; print('OK')"

# Check logs for VAD messages
journalctl -u ec25-voice-bot.service | grep -i vad
```

### Service not starting
```bash
# Check for errors
journalctl -u ec25-voice-bot.service -n 100 --no-pager

# Test manually
python3 /home/rom/ec25_voice_bot_v3.py
```

## Monitor Call Processing

```bash
# Watch for incoming calls
journalctl -u ec25-voice-bot.service -f | grep -E "Ring|ATA|audio|VAD|segment"
```

## Clean Up Old Audio Files

```bash
# Delete files older than 7 days
find /home/rom/Audio_wav -name "*.wav" -type f -mtime +7 -delete

# Delete debug segments older than 3 days
find /home/rom/Audio_wav/debug -name "*.wav" -type f -mtime +3 -delete

# Keep only last 10 calls
cd /home/rom/Audio_wav && ls -t call_*_raw.wav | tail -n +11 | xargs rm -f
```

## Integration Status

- ✅ Call answering (1 ring)
- ✅ Fast hangup detection (1 second)
- ✅ Audio recording (16kHz WAV)
- ✅ FFmpeg capture
- ✅ Silero VAD processing
- ✅ 800ms pause detection
- ✅ Audio segmentation
- ✅ Debug mode (save chunks)
- ⏳ Whisper transcription (pending)

## Key Files

| File | Purpose |
|------|---------|
| `/home/rom/ec25_voice_bot_v3.py` | Main voice bot script |
| `/home/rom/vad_config.py` | VAD configuration |
| `/home/rom/to_test/test_vad_audio.py` | Test script |
| `/home/rom/docs/Audio_Recording_VAD_Guide.md` | Full documentation |
| `/etc/systemd/system/ec25-voice-bot.service` | Service definition |

## Performance Metrics

- **Audio file size**: ~1.9 MB per minute (16kHz WAV)
- **VAD processing**: 2-5 seconds per call minute (RPi 4)
- **Memory usage**: ~150 MB (model + runtime)
- **CPU usage**: Minimal during call, burst during VAD processing

## Next Steps (Whisper Integration)

1. Install Whisper model
2. Implement transcription pipeline
3. Process audio segments
4. Return transcribed text
5. Trigger conversation flow based on text

Current placeholder in code:
```python
def prepare_for_whisper(self, audio_segment, segment_id):
    # Ready for implementation when Whisper is installed
    pass
```
