#!/usr/bin/env python3
"""
whisper.cpp Wrapper - Accepts OGG audio files and returns transcriptions
Automatically converts OGG to WAV format before transcription

Usage:
    python3 whisper_cpp_wrapper.py

Then send OGG files via:
    curl -X POST -F "audio=@file.ogg" -F "language=ro" http://10.100.0.2:9003/transcribe
"""

from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import sys
import time
from datetime import datetime

app = Flask(__name__)

# whisper.cpp configuration
WHISPER_CPP_PATH = os.path.expanduser("~/whisper.cpp/build/bin/whisper-cli")
MODEL_PATH = os.path.expanduser("~/whisper.cpp/models/ggml-large-v3-turbo.bin")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'model': 'large-v3-turbo',
            'backend': 'whisper.cpp',
            'device': 'cuda',
            'message': 'whisper.cpp wrapper is running'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Transcribe audio file

    POST parameters:
        - audio: Audio file (OGG, WAV, MP3, etc.)
        - language: Language code (default: ro - Romanian)
                   Examples: ro (Romanian), lt (Lithuanian), en (English)

    Returns:
        JSON with transcription and timing information
    """
    start_time = time.time()

    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    language = request.form.get('language', 'ro')  # Default to Romanian

    # Convert BCP-47 format (ro-RO, lt-LT) to ISO 639-1 (ro, lt)
    # for compatibility with Riva-style requests
    if '-' in language:
        language = language.split('-')[0]

    if audio_file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_ogg:
        temp_ogg_path = temp_ogg.name
        audio_file.save(temp_ogg_path)

    # Convert to WAV format (16kHz, mono, 16-bit PCM)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
        temp_wav_path = temp_wav.name

    try:
        # Convert using ffmpeg
        conversion_start = time.time()
        subprocess.run([
            'ffmpeg', '-i', temp_ogg_path,
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',       # Mono
            '-sample_fmt', 's16',  # 16-bit PCM
            '-y',             # Overwrite output
            temp_wav_path
        ], check=True, capture_output=True)
        conversion_time = time.time() - conversion_start

        # Get audio file size
        audio_size_kb = os.path.getsize(temp_wav_path) / 1024

        # Transcribe with whisper.cpp (optimized for low latency)
        transcription_start = time.time()

        # whisper.cpp command with optimizations
        cmd = [
            WHISPER_CPP_PATH,
            '-m', MODEL_PATH,
            '-f', temp_wav_path,
            '-l', language,  # Specify language
            '-bs', '1',      # Batch size 1 for low latency
            '-t', '4',       # Use 4 threads
            '--no-timestamps',  # Skip timestamps for faster processing
            '-nt'            # No timestamps in output
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # Parse transcription from output
        # whisper.cpp outputs the transcription to stdout
        transcription = result.stdout.strip()

        # Remove any whisper.cpp metadata from output
        # The actual transcription is typically after the metadata
        lines = transcription.split('\n')
        # Filter out metadata lines and empty lines
        transcription_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('[') and 'whisper' not in line.lower():
                transcription_lines.append(line)

        transcription = ' '.join(transcription_lines).strip()

        transcription_time = time.time() - transcription_start
        total_time = time.time() - start_time

        # Log latency information
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[LATENCY] {timestamp} | Lang: {language} | Size: {audio_size_kb:.1f}KB | "
              f"Conversion: {conversion_time:.3f}s | Transcription: {transcription_time:.3f}s | "
              f"Total: {total_time:.3f}s | "
              f"Text: {transcription[:50]}...")
        sys.stdout.flush()

        return jsonify({
            'success': True,
            'transcription': transcription,
            'language': language,
            'latency': {
                'conversion_ms': round(conversion_time * 1000, 1),
                'transcription_ms': round(transcription_time * 1000, 1),
                'total_ms': round(total_time * 1000, 1)
            }
        }), 200

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[ERROR] {timestamp} | Transcription failed | {error_msg}")
        sys.stdout.flush()
        return jsonify({
            'error': 'Transcription failed',
            'details': error_msg
        }), 500

    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[ERROR] {timestamp} | Transcription failed | {str(e)}")
        sys.stdout.flush()
        return jsonify({
            'error': 'Transcription failed',
            'details': str(e)
        }), 500

    finally:
        # Cleanup temporary files
        if os.path.exists(temp_ogg_path):
            os.unlink(temp_ogg_path)
        if os.path.exists(temp_wav_path):
            os.unlink(temp_wav_path)

@app.route('/languages', methods=['GET'])
def languages():
    """List supported language codes"""
    return jsonify({
        'languages': {
            'ro': 'Romanian',
            'lt': 'Lithuanian',
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'nl': 'Dutch',
            'pl': 'Polish',
            'tr': 'Turkish',
            'vi': 'Vietnamese',
            # ... Whisper supports 99+ languages
        },
        'note': 'Whisper v3-turbo supports 99+ languages. Use ISO 639-1 language codes.'
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("whisper.cpp OGG Wrapper Service")
    print("=" * 60)
    print(f"Model: large-v3-turbo")
    print(f"Device: CUDA")
    print(f"Backend: whisper.cpp")
    print(f"Listening on: 0.0.0.0:9003")
    print("")
    print("Endpoints:")
    print("  GET  /health      - Health check")
    print("  POST /transcribe  - Transcribe audio")
    print("  GET  /languages   - List supported languages")
    print("")
    print("Example usage:")
    print("  curl -X POST -F 'audio=@file.ogg' -F 'language=ro' http://10.100.0.2:9003/transcribe")
    print("=" * 60)
    print("")

    app.run(host='0.0.0.0', port=9003, debug=False)
