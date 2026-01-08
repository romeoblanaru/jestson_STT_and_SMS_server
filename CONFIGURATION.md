# Configuration Guide

This document explains how to set up configuration files with your own credentials.

## Voice Configuration

### Create voice_config.json

The repository includes `voice_config.json.template` - copy and update it with your credentials:

```bash
cp voice_config.json.template voice_config.json
nano voice_config.json
```

### Required Settings

Update these values in `voice_config.json`:

1. **Azure Speech Services Key** (line 25):
   ```json
   "tts_secret_key": "YOUR_AZURE_SPEECH_SERVICES_KEY_HERE"
   ```
   - Get your key from: https://portal.azure.com
   - Navigate to: Cognitive Services → Speech Services
   - Copy the Key1 or Key2

2. **Workpoint Configuration**:
   - `workpoint_id`: Your unique workpoint identifier
   - `phone_number`: Phone number for this workpoint
   - `ip_address`: Local IP address
   - `workpoint_language`: Language code (ro, lt, en, etc.)

3. **TTS Settings**:
   - `tts_model`: "azure" or other supported TTS engine
   - `tts_access_link`: Azure region endpoint
   - `voice`: Azure Neural Voice (e.g., "ro-RO-AlinaNeural", "lt-LT-OnaNeural")

4. **STT Settings**:
   - `stt_model`: "WHISPER_TINY", "WHISPER_SMALL", "PARAKEET", etc.
   - `language`: Language code for transcription

5. **Voice Behavior**:
   - `pitch`: Voice pitch (0.5 - 2.0)
   - `speed`: Speaking speed (0.5 - 2.0)
   - `style`: Voice style ("friendly", "professional", etc.)

6. **VAD Configuration**:
   - `vad_threshold`: Voice activity detection sensitivity (0.0 - 1.0)
   - `silence_timeout`: Milliseconds of silence before ending (default 800)

### Example Configuration

```json
{
  "workpoint_id": 17,
  "workpoint_name": "Main Office",
  "phone_number": "+447768261021",
  "ip_address": "10.100.0.11",
  "workpoint_language": "ro",
  "tts_model": "azure",
  "tts_access_link": "https://westeurope.api.cognitive.microsoft.com/",
  "stt_model": "WHISPER_TINY",
  "language": "ro",
  "welcome_message": "Bună ziua! Cu ce vă pot ajuta?",
  "answer_after_rings": 1,
  "voice_settings": {
    "pitch": 1,
    "speed": 1.2,
    "style": "friendly",
    "voice": "ro-RO-AlinaNeural"
  },
  "vad_threshold": 0.5,
  "silence_timeout": 800,
  "audio_format": "Raw8Khz16BitMonoPcm",
  "buffer_size": 4096,
  "is_active": true,
  "tts_secret_key": "your_actual_azure_key_here"
}
```

## Runtime Configuration

Create `runtime_voice_config.json` if you need runtime-updatable settings:

```bash
cp voice_config.json runtime_voice_config.json
```

This file can be updated by the system at runtime without requiring service restarts.

## SMS Configuration

The SMS server configuration is in `config/etc/smsd.conf`. Update:

1. **Modem Device Path**:
   ```
   device = /dev/serial/by-id/usb-SimTech__Incorporated_*
   ```
   Find your modem: `ls -l /dev/serial/by-id/`

2. **VPS Webhook** in `config/sms_handler_unicode.py`:
   ```python
   VPS_WEBHOOK_URL = "https://your-vps-domain.com/webhook/sms"
   ```

## Environment Variables

Create `.env` file for additional secrets:

```bash
# Azure
AZURE_SPEECH_KEY=your_key_here
AZURE_SPEECH_REGION=westeurope

# VPS
VPS_WEBHOOK_URL=https://your-vps.com/webhook
VPS_API_KEY=your_vps_api_key

# Database (if used)
DB_HOST=localhost
DB_USER=your_db_user
DB_PASS=your_db_password
```

## Security Notes

⚠️ **IMPORTANT**:
- Never commit `voice_config.json`, `runtime_voice_config.json`, or `.env` to git
- These files are already in `.gitignore`
- Use templates for sharing configuration structure
- Rotate keys regularly
- Use environment-specific configurations for dev/staging/production

## Supported Azure Neural Voices

### Romanian (ro-RO)
- AlinaNeural (Female)
- EmilNeural (Male)

### Lithuanian (lt-LT)
- LeonasNeural (Male)
- OnaNeural (Female)

### English (en-GB)
- LibbyNeural (Female)
- RyanNeural (Male)
- SoniaNeural (Female)

Full list: https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/language-support

## Testing Configuration

After configuration, test with:

```bash
# Test TTS
python3 -c "from voice_config_manager import VoiceConfigManager; vcm = VoiceConfigManager(); print(vcm.config)"

# Test SMS
sudo systemctl status smstools

# Test voice bot
sudo systemctl status sim7600-voice-bot
```
