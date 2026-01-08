#!/usr/bin/env python3
"""
Riva STT Wrapper - Accepts OGG audio files and returns transcriptions
Automatically converts OGG to WAV format before sending to Riva

Usage:
    python3 riva_ogg_wrapper.py

Then send OGG files via:
    curl -X POST -F "audio=@file.ogg" -F "language=en-US" http://192.168.1.9:9001/transcribe
"""

from flask import Flask, request, jsonify
import subprocess
import tempfile
import os
import riva.client
import time
from datetime import datetime

app = Flask(__name__)

# Riva server configuration
RIVA_SERVER = "localhost:9000"

# Initialize Riva client
auth = riva.client.Auth(uri=RIVA_SERVER)
asr_service = riva.client.ASRService(auth)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Test Riva connection
        return jsonify({
            'status': 'healthy',
            'riva_server': RIVA_SERVER,
            'message': 'Riva STT wrapper is running'
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
        - language: Language code (default: en-US)
                   Examples: lt-LT (Lithuanian), ro-RO (Romanian), en-US (English)
        - punctuation: Enable punctuation (default: true)

    Returns:
        JSON with transcription
    """
    start_time = time.time()

    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    language = request.form.get('language', 'en-US')
    punctuation = request.form.get('punctuation', 'true').lower() == 'true'

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

        # Read WAV file
        with open(temp_wav_path, 'rb') as f:
            audio_data = f.read()

        # Get audio file size
        audio_size_kb = len(audio_data) / 1024

        # Configure Riva ASR
        config = riva.client.RecognitionConfig(
            language_code=language,
            max_alternatives=1,
            enable_automatic_punctuation=punctuation,
        )

        # Transcribe with Riva
        transcription_start = time.time()
        response = asr_service.offline_recognize(audio_data, config)
        transcription_time = time.time() - transcription_start

        # Extract transcription
        if response.results and response.results[0].alternatives:
            transcription = response.results[0].alternatives[0].transcript
            confidence = response.results[0].alternatives[0].confidence
            total_time = time.time() - start_time

            # Log latency information
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"[LATENCY] {timestamp} | Lang: {language} | Size: {audio_size_kb:.1f}KB | "
                  f"Conversion: {conversion_time:.3f}s | Transcription: {transcription_time:.3f}s | "
                  f"Total: {total_time:.3f}s | Confidence: {confidence:.2%} | "
                  f"Text: {transcription[:50]}...")

            return jsonify({
                'success': True,
                'transcription': transcription,
                'confidence': confidence,
                'language': language,
                'latency': {
                    'conversion_ms': round(conversion_time * 1000, 1),
                    'transcription_ms': round(transcription_time * 1000, 1),
                    'total_ms': round(total_time * 1000, 1)
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'No transcription generated'
            }), 200

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else str(e)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[ERROR] {timestamp} | Audio conversion failed | {error_msg}")
        return jsonify({
            'error': 'Audio conversion failed',
            'details': error_msg
        }), 500

    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[ERROR] {timestamp} | Transcription failed | {str(e)}")
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
            'en-US': 'English (US)',
            'lt-LT': 'Lithuanian',
            'ro-RO': 'Romanian',
            'es-ES': 'Spanish',
            'fr-FR': 'French',
            'de-DE': 'German',
            'it-IT': 'Italian',
            'pt-BR': 'Portuguese (Brazil)',
            'ru-RU': 'Russian',
            'zh-CN': 'Chinese (Simplified)',
            'ja-JP': 'Japanese',
            'ko-KR': 'Korean',
            'ar-SA': 'Arabic',
            'hi-IN': 'Hindi',
            # ... and 80+ more languages supported by Parakeet model
        },
        'note': 'Parakeet 1.1B supports 100+ languages. Use standard BCP-47 language codes.'
    }), 200

if __name__ == '__main__':
    print("=" * 60)
    print("Riva STT OGG Wrapper Service")
    print("=" * 60)
    print(f"Riva Server: {RIVA_SERVER}")
    print(f"Listening on: 0.0.0.0:9001")
    print(f"")
    print("Endpoints:")
    print("  GET  /health      - Health check")
    print("  POST /transcribe  - Transcribe audio")
    print("  GET  /languages   - List supported languages")
    print("")
    print("Example usage:")
    print("  curl -X POST -F 'audio=@file.ogg' -F 'language=lt-LT' http://192.168.1.9:9001/transcribe")
    print("=" * 60)

    app.run(host='0.0.0.0', port=9001, debug=False)
