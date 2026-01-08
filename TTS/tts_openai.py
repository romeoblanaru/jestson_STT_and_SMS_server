#!/usr/bin/env python3
"""
OpenAI Text-to-Speech Module
Using OpenAI's TTS API with streaming support
"""

import requests
import numpy as np
import logging
import time
import json
from typing import Optional, Generator, Callable
from .tts_base import BaseTTS

logger = logging.getLogger(__name__)

class OpenAITTS(BaseTTS):
    """OpenAI TTS provider"""

    def __init__(self, config: dict):
        """Initialize OpenAI TTS"""
        super().__init__(config)

        # OpenAI specific settings
        self.model = self.voice_settings.get('model', 'tts-1')  # tts-1 or tts-1-hd
        self.voice = self.voice_settings.get('voice', 'alloy')  # alloy, echo, fable, onyx, nova, shimmer
        self.response_format = 'pcm'  # PCM for lowest latency (raw audio)

        # Endpoint
        if not self.endpoint:
            self.endpoint = 'https://api.openai.com/v1/audio/speech'

        logger.info(f"✅ OpenAI TTS initialized: model={self.model}, voice={self.voice}")

    def synthesize_stream(self, text: str, callback: Optional[Callable] = None) -> Generator[np.ndarray, None, None]:
        """
        Synthesize text with streaming
        Args:
            text: Text to synthesize
            callback: Optional callback for each audio chunk
        Yields:
            Audio chunks as numpy arrays
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': self.model,
            'input': text,
            'voice': self.voice,
            'response_format': self.response_format,
            'speed': self.get_speed()
        }

        logger.info(f"Starting OpenAI streaming synthesis: {text[:50]}...")
        start_time = time.time()
        first_chunk_time = None

        try:
            # Make streaming request
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=data,
                stream=True
            )

            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return

            # Process streaming response
            total_samples = 0
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    # Convert PCM bytes to numpy array
                    # PCM format is 24kHz, 16-bit, mono
                    audio_np = np.frombuffer(chunk, dtype=np.int16)

                    # Resample from 24kHz to 16kHz
                    # Simple decimation (not ideal but fast)
                    audio_16k = audio_np[::3] * 2  # Every 3rd sample, amplify

                    # Normalize to float32
                    audio_float = audio_16k.astype(np.float32) / 32768.0

                    if first_chunk_time is None:
                        first_chunk_time = time.time() - start_time
                        logger.info(f"⚡ First chunk in {first_chunk_time*1000:.0f}ms")

                    total_samples += len(audio_float)

                    # Yield chunk
                    yield audio_float

                    # Call callback if provided
                    if callback:
                        callback(audio_float)

            duration_sec = total_samples / 16000
            total_time = time.time() - start_time
            logger.info(f"✅ Synthesis complete: {duration_sec:.1f}s audio in {total_time:.1f}s")

        except Exception as e:
            logger.error(f"OpenAI TTS error: {e}")

    def synthesize_to_array(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize text to numpy array
        Args:
            text: Text to synthesize
        Returns:
            Audio as numpy array or None if failed
        """
        chunks = []
        for chunk in self.synthesize_stream(text):
            chunks.append(chunk)

        if chunks:
            return np.concatenate(chunks)
        return None

    def synthesize_to_file(self, text: str, output_file: str) -> bool:
        """
        Synthesize text to file
        Args:
            text: Text to synthesize
            output_file: Output file path
        Returns:
            True if successful
        """
        audio = self.synthesize_to_array(text)

        if audio is not None:
            # Save as WAV file
            import wave
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes((audio * 32768).astype(np.int16).tobytes())

            logger.info(f"Saved to: {output_file}")
            return True

        return False