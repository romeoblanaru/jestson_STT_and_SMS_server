# Parakeet ASR Language and Hotwords Configuration Guide

## Overview

This document explains how to configure the language and update biasing hotwords for the Parakeet-TDT-0.6B-v3 ASR server running on your NVIDIA Jetson Orin Nano.

## System Architecture

The Parakeet ASR server uses:
- **Language selection**: Controlled via `/home/rom/.env` file
- **Hotwords/biasing**: Language-specific text files with domain phrases
- **Boosting tree**: NeMo's phrase biasing system with 4.0x boost factor
- **Zero runtime cost**: Hotwords compiled into n-grams at startup

## Changing the Language

### Step 1: Edit the .env File

```bash
nano /home/rom/.env
```

Change the `LANGUAGE` value to either `ro` (Romanian) or `lt` (Lithuanian):

```bash
# For Romanian
LANGUAGE=ro

# For Lithuanian
LANGUAGE=lt
```

### Step 2: Restart the Server

```bash
# Stop any running servers
docker ps -q | xargs -r docker stop

# Start the server with new language
./start_parakeet_server.sh
```

The server will automatically:
1. Load the appropriate hotwords file (`hotwords_ro.txt` or `hotwords_lt.txt`)
2. Configure the decoding strategy for the selected language
3. Compile the boosting tree with your hotwords

## Updating Biasing Hotwords

### Hotword Files Location

- Romanian: `/home/rom/hotwords_ro.txt`
- Lithuanian: `/home/rom/hotwords_lt.txt`

### Adding or Modifying Hotwords

1. **Edit the appropriate file:**
```bash
# For Romanian hotwords
nano /home/rom/hotwords_ro.txt

# For Lithuanian hotwords
nano /home/rom/hotwords_lt.txt
```

2. **Add phrases (one per line):**
```
bună ziua aș vrea să fac o programare
aveți loc liber săptămâna asta
vreau manichiură
pot să vin pentru coafură de seară
```

3. **Save the file** (Ctrl+O, Enter, Ctrl+X in nano)

4. **Restart the server:**
```bash
docker ps -q | xargs -r docker stop
./start_parakeet_server.sh
```

### Hotword Guidelines

**Do:**
- Use complete, natural phrases (not single words)
- Focus on domain-specific vocabulary
- Include common variations of requests
- Keep phrases between 3-15 words

**Don't:**
- Add too many phrases (recommended: 20-50 phrases)
- Use very short phrases (< 3 words)
- Duplicate similar phrases
- Include punctuation or special characters

## Startup Logs

When the server starts, you'll see:

```
Loading Parakeet-TDT-0.6B-v3 model...
Target language: Romanian (ro)
Decoding strategy configured for: ro
Loading biasing hotwords from: /workspace/hotwords_ro.txt
Configuring boosting tree with 42 hotwords for Romanian language...
Boosting tree configured in 0.16s (language: ro, phrases: 42)
```

This confirms:
- Which language is active
- Which hotwords file was loaded
- How many phrases were compiled
- Compilation time

## Testing the Configuration

### Test with curl:

```bash
# Romanian example
curl -X POST -F "audio=@test_audio.ogg" -F "language=ro" \
  http://192.168.1.9:9001/transcribe

# Lithuanian example
curl -X POST -F "audio=@test_audio.ogg" -F "language=lt" \
  http://192.168.1.9:9001/transcribe
```

### Check server health:

```bash
curl http://192.168.1.9:9001/health
```

## Technical Details

### How Boosting Tree Works

1. **Compilation**: At startup, hotwords are tokenized and built into an n-gram tree structure
2. **Runtime**: During transcription, the decoder boosts probabilities when matching phrases appear
3. **Boost factor**: Set to 4.0x (configurable in `parakeet_wrapper.py:75`)
4. **Performance**: Zero runtime latency after initial compilation

### Configuration in Code

Location: `/home/rom/parakeet_wrapper.py` (lines 62-82)

```python
# Load biasing hotwords via boosting_tree configuration
hotwords_file = f"/workspace/hotwords_{language}.txt"
if os.path.exists(hotwords_file):
    with open(hotwords_file, 'r', encoding='utf-8') as f:
        phrases = [line.strip() for line in f if line.strip()]

    # Update decoding configuration with boosting tree
    with open_dict(model.cfg.decoding):
        model.cfg.decoding.greedy.boosting_tree.key_phrases_list = phrases
        model.cfg.decoding.greedy.boosting_tree.context_score = 4.0  # Boost factor
        model.cfg.decoding.greedy.boosting_tree.use_triton = False
        model.cfg.decoding.greedy.boosting_tree_alpha = 1.0  # Enable boosting

    model.change_decoding_strategy(model.cfg.decoding)
```

### Supported Languages

Parakeet-TDT-0.6B-v3 supports 25 European languages:
- Romanian (ro), Lithuanian (lt), English (en)
- Spanish (es), French (fr), German (de), Italian (it)
- Portuguese (pt), Polish (pl), Dutch (nl), Czech (cs)
- Slovak (sk), Hungarian (hu), Bulgarian (bg), Croatian (hr)
- Slovenian (sl), Estonian (et), Latvian (lv), Finnish (fi)
- Swedish (sv), Danish (da), Norwegian (no), Greek (el)
- Ukrainian (uk), Russian (ru)

Currently configured hotwords: **Romanian** and **Lithuanian** only.

## Troubleshooting

### Server won't start after changing language:
- Check `.env` syntax: `LANGUAGE=ro` (no spaces, lowercase)
- Verify hotwords file exists for that language
- Check Docker logs: `docker logs $(docker ps -q --filter ancestor=parakeet-server)`

### Hotwords not being applied:
- Verify hotwords file is in `/home/rom/` directory
- Check file encoding is UTF-8
- Look for compilation message in startup logs
- Ensure phrases are properly formatted (one per line, no empty lines between)

### Server crashes during hotword compilation:
- Reduce number of phrases (keep under 100)
- Remove very long phrases (> 20 words)
- Check for special characters or malformed UTF-8

## Update Frequency

**Testing phase** (Romanian): Multiple updates per day expected
**Production** (Lithuanian): Monthly updates expected

The boosting tree compiles in < 0.5s, making frequent updates practical.

## Contact & Support

For issues or questions about this configuration:
- Check server logs: `docker logs $(docker ps -q --filter ancestor=parakeet-server)`
- Verify files exist: `ls -la /home/rom/*.txt /home/rom/.env`
- Test manually: `cat /home/rom/hotwords_ro.txt`
