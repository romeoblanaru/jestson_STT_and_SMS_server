#!/usr/bin/env python3
"""
VAD Configuration for EC25 Voice Bot
Adjust these settings to fine-tune voice activity detection
"""

# Audio Settings
SAMPLE_RATE = 16000  # 16kHz as required
AUDIO_FORMAT = "wav"  # WAV format

# VAD Settings
VAD_THRESHOLD = 0.5  # Speech probability threshold (0.0-1.0)
                     # Lower = more sensitive, higher = less sensitive

PAUSE_THRESHOLD_MS = 800  # Pause detection threshold in milliseconds
                          # Will cut audio segments when pause > this value

MIN_SPEECH_DURATION_MS = 250  # Minimum speech duration to consider as speech
                              # Shorter segments will be filtered out

MIN_SILENCE_DURATION_MS = 800  # Minimum silence duration to split segments
                               # Must match or exceed PAUSE_THRESHOLD_MS

# Debug Settings
DEBUG_MODE = True  # Set to False to disable saving debug audio chunks
                   # Can also be controlled via DEBUG_MODE environment variable

# Directory Settings
AUDIO_DIR = "/home/rom/Audio_wav"
DEBUG_DIR = "/home/rom/Audio_wav/debug"

# Whisper Integration (for future use)
WHISPER_MODEL = "base"  # Model size: tiny, base, small, medium, large
WHISPER_LANGUAGE = "en"  # Language code

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
# - VAD_THRESHOLD: Adjust if VAD is too sensitive or not sensitive enough
#   0.3-0.4 = Very sensitive (might catch background noise)
#   0.5 = Balanced (recommended)
#   0.6-0.7 = Less sensitive (might miss quiet speech)
#
# - MIN_SPEECH_DURATION_MS: Filter out very short audio blips
#   Increase to reduce noise, decrease to catch all speech
