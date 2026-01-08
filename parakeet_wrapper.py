#!/usr/bin/env python3
"""
Parakeet-TDT-0.6B-v3 Wrapper - Accepts OGG audio files and returns transcriptions
Automatically converts OGG to WAV format before transcription
Supports 25 European languages including Romanian and Lithuanian with auto-detection

Usage (inside Docker container):
    python3 /workspace/parakeet_wrapper.py

Then send OGG files via:
    curl -X POST -F "audio=@file.ogg" -F "language=ro" http://192.168.1.9:9001/transcribe
"""

from flask import Flask, request, jsonify
import tempfile
import os
import sys
import time
from datetime import datetime
import threading

app = Flask(__name__)

# Lock for thread-safe transcription (model not safe for concurrent use)
transcribe_lock = threading.Lock()

# Global model instance (loaded once at startup)
model = None
MODEL_NAME = "Parakeet-TDT-0.6B-v3"
MODEL_PATH = "/models/parakeet-tdt-0.6b-v3.nemo"

# Global hotwords for fuzzy matching post-processing
hotwords_phrases = []
# Read from environment variable (default: enabled)
fuzzy_correction_enabled = os.getenv('ENABLE_FUZZY_CORRECTION', 'true').lower() in ('true', '1', 'yes')

def fuzzy_correct_transcription(text, hotwords, threshold=85):
    """
    Apply fuzzy matching to correct transcription using hotword list

    Args:
        text: Transcribed text from ASR
        hotwords: List of correct phrases to match against
        threshold: Similarity threshold (0-100), higher = more strict

    Returns:
        tuple: (corrected_text, corrections_made, details)
    """
    from rapidfuzz import fuzz, process
    import re

    if not text or not hotwords:
        return text, [], {}

    corrections_made = []
    details = {
        'original_length': len(text),
        'matches_found': 0,
        'corrections_applied': 0
    }

    # Split text into words
    words = text.lower().split()
    corrected_text = text

    # For each phrase in text, try to find fuzzy matches
    for n in range(len(words), 0, -1):  # Try longest matches first
        for i in range(len(words) - n + 1):
            phrase = ' '.join(words[i:i+n])

            # Find best match from hotwords
            best_match = process.extractOne(
                phrase,
                [hw.lower() for hw in hotwords],
                scorer=fuzz.ratio,
                score_cutoff=threshold
            )

            if best_match:
                matched_hotword, score, idx = best_match
                original_hotword = hotwords[idx]  # Get original casing

                details['matches_found'] += 1

                # Only correct if there's an actual difference
                if phrase != matched_hotword:
                    # Replace in corrected_text (case-insensitive)
                    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                    new_text = pattern.sub(original_hotword, corrected_text, count=1)

                    if new_text != corrected_text:
                        corrections_made.append({
                            'original': phrase,
                            'corrected': original_hotword,
                            'score': score,
                            'position': i
                        })
                        corrected_text = new_text
                        details['corrections_applied'] += 1

    details['final_length'] = len(corrected_text)
    return corrected_text, corrections_made, details

def load_model():
    """Load NeMo ASR Parakeet model with CUDA support"""
    global model, hotwords_phrases
    import nemo.collections.asr as nemo_asr
    import torch
    from omegaconf import open_dict

    # Read language from .env file
    language = os.getenv('LANGUAGE', 'ro').lower()
    if language not in ['ro', 'lt']:
        print(f"Warning: Invalid LANGUAGE={language}, defaulting to 'ro'")
        language = 'ro'

    language_names = {'ro': 'Romanian', 'lt': 'Lithuanian'}

    print("=" * 60)
    print("Loading Parakeet-TDT-0.6B-v3 model...")
    print(f"Target language: {language_names[language]} ({language})")
    start = time.time()

    model = nemo_asr.models.ASRModel.restore_from(MODEL_PATH)
    model.eval()

    # Configure decoding strategy for selected language
    # This skips LID and gives ~40-120ms faster response
    with open_dict(model.cfg.decoding):
        model.cfg.decoding.language = language
    model.change_decoding_strategy(model.cfg.decoding)
    print(f"Decoding strategy configured for: {language}")

    # Load biasing hotwords via boosting_tree configuration
    hotwords_file = f"/workspace/hotwords_{language}.txt"
    if os.path.exists(hotwords_file):
        print(f"Loading biasing hotwords from: {hotwords_file}")
        with open(hotwords_file, 'r', encoding='utf-8') as f:
            phrases = [line.strip() for line in f if line.strip()]

        # Store hotwords globally for fuzzy matching post-processing
        hotwords_phrases.clear()
        hotwords_phrases.extend(phrases)
        print(f"Loaded {len(hotwords_phrases)} phrases for post-processing fuzzy correction")

        print(f"Configuring boosting tree with {len(phrases)} hotwords for {language_names[language]} language...")
        bias_start = time.time()

        # Create complete greedy config with boosting_tree structure
        from omegaconf import OmegaConf
        greedy_cfg = OmegaConf.create({
            'max_symbols': model.cfg.decoding.greedy.max_symbols if hasattr(model.cfg.decoding.greedy, 'max_symbols') else 10,
            'boosting_tree': {
                'key_phrases_list': phrases,
                'context_score': 4.0,  # Boost factor for phrase matching
                'use_triton': True,  # Enable Triton for CUDA graphs compatibility
                'source_lang': language  # Language code
            },
            'boosting_tree_alpha': 1.0  # Enable boosting (1.0 = full boosting, 0.0 = disabled)
        })

        # Update model configuration
        with open_dict(model.cfg.decoding):
            model.cfg.decoding.greedy = greedy_cfg

        # Apply configuration change
        model.change_decoding_strategy(model.cfg.decoding)
        bias_time = time.time() - bias_start
        print(f"Boosting tree configured in {bias_time:.2f}s (language: {language}, phrases: {len(phrases)})")
    else:
        print(f"No hotwords file found at {hotwords_file}, skipping biasing")

    # Move to GPU if available
    if torch.cuda.is_available():
        model = model.cuda()
        device_name = torch.cuda.get_device_name()
    else:
        device_name = "CPU"

    load_time = time.time() - start
    print(f"Model '{MODEL_NAME}' loaded in {load_time:.2f}s")
    print(f"Device: {device_name}")
    print(f"Model type: {type(model).__name__}")

    # Warmup CUDA graphs with dummy transcription
    print("Warming up CUDA graphs...")
    import numpy as np
    import soundfile as sf
    warmup_file = "/tmp/warmup_audio.wav"
    # Create 1 second of silence at 16kHz
    sf.write(warmup_file, np.zeros(16000, dtype=np.float32), 16000)
    warmup_start = time.time()
    model.transcribe([warmup_file])
    warmup_time = time.time() - warmup_start
    os.unlink(warmup_file)
    print(f"CUDA warmup complete in {warmup_time:.2f}s")
    print("=" * 60)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    import torch
    try:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        return jsonify({
            'status': 'healthy',
            'model': MODEL_NAME,
            'device': device,
            'message': 'Parakeet ASR wrapper is running'
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
        - audio: Audio file (OGG, WAV, MP3, etc.) - passed directly to Parakeet
        - language: Language code for logging (decoding configured at startup)

    Returns:
        JSON with transcription and timing information
    """
    start_time = time.time()

    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    language = request.form.get('language', 'ro')  # For logging/tracking

    # Convert BCP-47 format (ro-RO, lt-LT) to ISO 639-1 (ro, lt)
    if '-' in language:
        language = language.split('-')[0]

    if audio_file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Get file extension from filename
    filename = audio_file.filename.lower()
    if filename.endswith('.ogg'):
        suffix = '.ogg'
    elif filename.endswith('.wav'):
        suffix = '.wav'
    elif filename.endswith('.mp3'):
        suffix = '.mp3'
    else:
        suffix = '.ogg'  # Default

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_audio:
        temp_audio_path = temp_audio.name
        audio_file.save(temp_audio_path)

    try:
        # Get audio file size
        audio_size_kb = os.path.getsize(temp_audio_path) / 1024

        # Use lock to prevent concurrent transcription issues
        with transcribe_lock:
            # Transcribe with Parakeet (handles OGG/WAV/MP3 directly)
            transcription_start = time.time()
            result = model.transcribe([temp_audio_path])

            # Extract transcription text from result
            if isinstance(result, list) and len(result) > 0:
                if hasattr(result[0], 'text'):
                    transcription = result[0].text
                else:
                    transcription = str(result[0])
            else:
                transcription = ""

        transcription = transcription.strip()
        transcription_time = time.time() - transcription_start

        # Apply fuzzy matching post-processing if enabled
        original_transcription = transcription
        corrections_made = []
        correction_time = 0.0

        if fuzzy_correction_enabled and hotwords_phrases and transcription:
            correction_start = time.time()
            transcription, corrections_made, correction_details = fuzzy_correct_transcription(
                transcription,
                hotwords_phrases,
                threshold=85
            )
            correction_time = time.time() - correction_start

        total_time = time.time() - start_time

        # Log latency information with detailed monitoring
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if corrections_made:
            # DETAILED LOG: Corrections were applied
            print(f"[CORRECTION] {timestamp} | Lang: {language} | "
                  f"Corrections: {len(corrections_made)} | Time: {correction_time*1000:.2f}ms")
            print(f"[CORRECTION] Input:  '{original_transcription}'")
            print(f"[CORRECTION] Output: '{transcription}'")
            for i, corr in enumerate(corrections_made, 1):
                print(f"[CORRECTION]   #{i}: '{corr['original']}' -> '{corr['corrected']}' (score: {corr['score']:.1f}%)")
            sys.stdout.flush()
        elif fuzzy_correction_enabled and transcription:
            # LOG: Correction ran but no changes needed
            print(f"[CORRECTION] {timestamp} | Lang: {language} | No corrections needed | Time: {correction_time*1000:.2f}ms")
            sys.stdout.flush()

        # Log latency information
        print(f"[LATENCY] {timestamp} | Lang: {language} | Size: {audio_size_kb:.1f}KB | "
              f"ASR: {transcription_time:.3f}s | Correction: {correction_time:.3f}s | Total: {total_time:.3f}s | "
              f"Text: {transcription[:50]}...")
        sys.stdout.flush()

        return jsonify({
            'success': True,
            'transcription': transcription,
            'language': language,
            'latency': {
                'transcription_ms': round(transcription_time * 1000, 1),
                'correction_ms': round(correction_time * 1000, 1),
                'total_ms': round(total_time * 1000, 1)
            },
            'corrections': {
                'applied': len(corrections_made),
                'details': corrections_made if corrections_made else None
            } if corrections_made else None
        }), 200

    except Exception as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[ERROR] {timestamp} | Transcription failed | {str(e)}")
        sys.stdout.flush()
        return jsonify({
            'error': 'Transcription failed',
            'details': str(e)
        }), 500

    finally:
        # Cleanup temporary file
        if os.path.exists(temp_audio_path):
            os.unlink(temp_audio_path)

@app.route('/languages', methods=['GET'])
def languages():
    """List supported language codes (Parakeet auto-detects)"""
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
            'pl': 'Polish',
            'nl': 'Dutch',
            'cs': 'Czech',
            'sk': 'Slovak',
            'hu': 'Hungarian',
            'bg': 'Bulgarian',
            'hr': 'Croatian',
            'sl': 'Slovenian',
            'et': 'Estonian',
            'lv': 'Latvian',
            'fi': 'Finnish',
            'sv': 'Swedish',
            'da': 'Danish',
            'no': 'Norwegian',
            'el': 'Greek',
            'uk': 'Ukrainian',
            'ru': 'Russian',
        },
        'note': 'Parakeet-TDT-0.6B-v3 supports 25 European languages with automatic detection.'
    }), 200

@app.route('/diagnostic', methods=['GET'])
def diagnostic():
    """Diagnostic endpoint to inspect decoder's boosting tree state"""
    try:
        from omegaconf import OmegaConf

        result = {
            'model_type': type(model).__name__,
            'decoding_object_type': type(model.decoding).__name__ if hasattr(model, 'decoding') else 'NOT_FOUND',
            'config': {},
            'decoder_state': {}
        }

        # Check configuration
        if hasattr(model, 'cfg') and hasattr(model.cfg, 'decoding'):
            if hasattr(model.cfg.decoding, 'greedy'):
                greedy_cfg = model.cfg.decoding.greedy
                result['config']['greedy_type'] = str(type(greedy_cfg))

                if hasattr(greedy_cfg, 'boosting_tree'):
                    boost_cfg = greedy_cfg.boosting_tree
                    result['config']['boosting_tree'] = {
                        'exists': True,
                        'key_phrases_count': len(boost_cfg.key_phrases_list) if hasattr(boost_cfg, 'key_phrases_list') and boost_cfg.key_phrases_list else 0,
                        'context_score': boost_cfg.context_score if hasattr(boost_cfg, 'context_score') else None,
                        'use_triton': boost_cfg.use_triton if hasattr(boost_cfg, 'use_triton') else None,
                        'source_lang': boost_cfg.source_lang if hasattr(boost_cfg, 'source_lang') else None,
                        'first_phrase': boost_cfg.key_phrases_list[0] if hasattr(boost_cfg, 'key_phrases_list') and boost_cfg.key_phrases_list and len(boost_cfg.key_phrases_list) > 0 else None
                    }
                else:
                    result['config']['boosting_tree'] = {'exists': False}

                if hasattr(greedy_cfg, 'boosting_tree_alpha'):
                    result['config']['boosting_tree_alpha'] = greedy_cfg.boosting_tree_alpha
                else:
                    result['config']['boosting_tree_alpha'] = None

        # Check decoder object state
        if hasattr(model, 'decoding'):
            decoding = model.decoding
            result['decoder_state']['has_decoding'] = True
            result['decoder_state']['parent_attributes'] = [x for x in dir(decoding) if not x.startswith('_') and 'boost' in x.lower() or 'tree' in x.lower() or 'context' in x.lower()][:20]

            # Check parent for boosting tree
            if hasattr(decoding, 'boosting_tree_model'):
                boost_model = decoding.boosting_tree_model
                result['decoder_state']['parent_boosting_tree'] = {
                    'exists': True,
                    'is_active': boost_model is not None,
                    'type': type(boost_model).__name__ if boost_model is not None else 'None'
                }

            # Check inner decoding object (greedy decoder)
            if hasattr(decoding, 'decoding'):
                inner_decoder = decoding.decoding
                result['decoder_state']['inner_decoder_type'] = type(inner_decoder).__name__

                # Check for boosting tree model
                if hasattr(inner_decoder, 'boosting_tree_model'):
                    boost_model = inner_decoder.boosting_tree_model
                    result['decoder_state']['boosting_tree_model'] = {
                        'exists': True,
                        'is_active': boost_model is not None,
                        'type': type(boost_model).__name__ if boost_model is not None else 'None'
                    }

                    # If active, get details
                    if boost_model is not None and hasattr(boost_model, 'cfg'):
                        cfg = boost_model.cfg
                        result['decoder_state']['boosting_tree_model']['config'] = {
                            'phrases_count': len(cfg.key_phrases_list) if hasattr(cfg, 'key_phrases_list') and cfg.key_phrases_list else 0,
                            'context_score': cfg.context_score if hasattr(cfg, 'context_score') else None,
                            'use_triton': cfg.use_triton if hasattr(cfg, 'use_triton') else None
                        }
                else:
                    result['decoder_state']['boosting_tree_model'] = {'exists': False}

                # Check for boosting_tree_alpha
                if hasattr(inner_decoder, 'boosting_tree_alpha'):
                    result['decoder_state']['boosting_tree_alpha'] = inner_decoder.boosting_tree_alpha
                else:
                    result['decoder_state']['boosting_tree_alpha'] = None

                # List available attributes
                result['decoder_state']['decoder_attributes'] = [x for x in dir(inner_decoder) if not x.startswith('_')][:30]
            else:
                result['decoder_state']['inner_decoder_type'] = 'NOT_FOUND'
        else:
            result['decoder_state']['has_decoding'] = False

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            'error': 'Diagnostic failed',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Parakeet-TDT-0.6B-v3 OGG Wrapper Service")
    print("=" * 60)
    print(f"Model: {MODEL_NAME}")
    print(f"Model path: {MODEL_PATH}")
    print(f"Listening on: 0.0.0.0:9001")
    print("")
    print("Endpoints:")
    print("  GET  /health      - Health check")
    print("  POST /transcribe  - Transcribe audio")
    print("  GET  /languages   - List supported languages")
    print("  GET  /diagnostic  - Inspect boosting tree state")
    print("")
    print("Example usage:")
    print("  curl -X POST -F 'audio=@file.ogg' -F 'language=ro' http://192.168.1.9:9001/transcribe")
    print("=" * 60)
    print("")

    # Load model before starting server
    load_model()

    app.run(host='0.0.0.0', port=9001, debug=False)
