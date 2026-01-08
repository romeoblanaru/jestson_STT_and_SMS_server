#!/usr/bin/env python3
"""
Example: How to use your Riva STT server
Test with: python3 test_stt.py
"""

import riva.client

# Connect to your Riva server
auth = riva.client.Auth(uri='localhost:9000')

# Create STT service
asr_service = riva.client.ASRService(auth)

# Example 1: Recognize from audio file
def transcribe_file(audio_file):
    config = riva.client.RecognitionConfig(
        language_code="lt-LT",  # Lithuanian - change to "ro-RO" for Romanian, "en-US" for English
        max_alternatives=1,
        enable_automatic_punctuation=True,
    )
    
    with open(audio_file, 'rb') as f:
        response = asr_service.offline_recognize(f.read(), config)
        print(f"Transcription: {response.results[0].alternatives[0].transcript}")

# Example 2: Streaming recognition from microphone
def transcribe_streaming():
    config = riva.client.StreamingRecognitionConfig(
        config=riva.client.RecognitionConfig(
            language_code="en-US",
            max_alternatives=1,
            enable_automatic_punctuation=True,
        ),
        interim_results=True,
    )
    
    # This requires microphone access
    riva.client.ASRService(auth).streaming_response_generator(
        audio_chunks=get_audio_chunks_from_mic(),
        streaming_config=config
    )

print("Riva STT Client Examples")
print("=" * 50)
print(f"Server: localhost:9000")
print(f"Supported languages: Lithuanian (lt-LT), Romanian (ro-RO), English (en-US), and 100+ more")
print("\nTo use:")
print("1. Install client: pip3 install nvidia-riva-client")
print("2. Prepare audio file (WAV format recommended)")
print("3. Call transcribe_file('your_audio.wav')")
