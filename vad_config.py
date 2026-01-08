#!/usr/bin/env python3
"""
VAD Configuration for Voice Bots
Adjust these settings to fine-tune voice activity detection using WebRTC VAD
"""

# Audio Settings
SAMPLE_RATE = 16000  # 16kHz (WebRTC VAD supports 8/16/32kHz)
AUDIO_FORMAT = "wav"  # WAV format

# WebRTC VAD Settings
VAD_MODE = 3  # Aggressiveness mode (0-3)
              # 0 = Least aggressive (quality mode)
              # 1 = Low aggressive
              # 2 = Moderate aggressive
              # 3 = Most aggressive (recommended for telephony)

PAUSE_THRESHOLD_MS = 800  # Pause detection threshold in milliseconds
                          # Will cut audio segments when pause > this value

FRAME_DURATION_MS = 30  # Frame duration for VAD processing (10/20/30ms)
                        # WebRTC VAD only supports these specific durations

# Debug Settings
DEBUG_MODE = True  # Set to False to disable saving debug audio chunks
                   # Can also be controlled via DEBUG_MODE environment variable

# Directory Settings
AUDIO_DIR = "/home/rom/Audio_wav"
DEBUG_DIR = "/home/rom/Audio_wav/debug"

# Whisper Integration (for future use)
WHISPER_MODEL = "base"  # Model size: tiny, base, small, medium, large
WHISPER_LANGUAGE = "en"  # Language code
WHISPER_DEVICE = "cpu"  # Device: cpu, cuda (if GPU available)

# Audio File Naming
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"  # Format for call_id timestamps

# Performance Settings
FFMPEG_BUFFER_SIZE = 4096  # FFmpeg buffer size in bytes
PROCESSING_THREADS = 2  # Number of threads for audio processing

# Notes:
# - PAUSE_THRESHOLD_MS: The main setting to adjust conversation flow
#   Increase if you want longer pauses before cutting
#   Decrease if you want more responsive chunking
#
# - VAD_MODE: Adjust if VAD is too sensitive or not sensitive enough
#   0 = Least aggressive (quality mode, may catch more background noise)
#   1 = Low aggressive (balanced for clean audio)
#   2 = Moderate aggressive (good for noisy environments)
#   3 = Most aggressive (recommended for telephony, filters noise aggressively)
#
# - FRAME_DURATION_MS: WebRTC VAD only supports 10ms, 20ms, or 30ms
#   Shorter frames = more responsive but higher CPU usage
#   Longer frames = more stable detection with lower CPU usage
#   30ms is recommended for telephony applications
