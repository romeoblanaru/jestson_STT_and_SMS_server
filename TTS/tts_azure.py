#!/usr/bin/env python3
"""
Azure Text-to-Speech Module with Low Latency Configuration
Optimized for real-time phone call responses
"""

import azure.cognitiveservices.speech as speechsdk
import logging
import numpy as np
import queue
import threading
import time
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class AzureTTS:
    """Azure TTS provider with real-time streaming support"""

    def __init__(self, config: dict):
        """
        Initialize Azure TTS with configuration
        Args:
            config: Configuration dict from voice_config_manager
        """
        self.config = config
        self.tts_url = config.get('tts_access_link', '')
        self.api_key = config.get('tts_secret_key', '')
        self.language = config.get('language', 'en')
        self.voice_settings = config.get('voice_settings', {})

        # Parse Azure endpoint from URL
        if 'cognitiveservices.azure.com' in self.tts_url:
            # Extract region from URL
            # Format: https://REGION.tts.speech.microsoft.com/cognitiveservices/v1
            parts = self.tts_url.split('.')
            self.region = parts[0].replace('https://', '')
        else:
            self.region = 'westeurope'  # Default region

        # Azure voice mapping
        self.voice_map = {
            'lt': {  # Lithuanian
                'male': 'lt-LT-LeonasNeural',
                'female': 'lt-LT-OnaNeural',
                'default': 'lt-LT-OnaNeural'
            },
            'ro': {  # Romanian
                'male': 'ro-RO-EmilNeural',
                'female': 'ro-RO-AlinaNeural',
                'default': 'ro-RO-AlinaNeural'
            },
            'en': {  # English
                'male': 'en-US-GuyNeural',
                'female': 'en-US-JennyNeural',
                'default': 'en-US-JennyNeural'
            },
            'es': {  # Spanish
                'male': 'es-ES-AlvaroNeural',
                'female': 'es-ES-ElviraNeural',
                'default': 'es-ES-ElviraNeural'
            }
        }

        # Audio format from config (dynamic)
        # Config provides format name like "Raw8Khz16BitMonoPcm"
        # Convert to Azure SDK enum
        audio_format_name = config.get('audio_format', 'Raw16Khz16BitMonoPcm')
        try:
            self.audio_format = getattr(speechsdk.SpeechSynthesisOutputFormat, audio_format_name)
            logger.info(f"Audio format set to: {audio_format_name}")
        except AttributeError:
            logger.warning(f"Unknown audio format '{audio_format_name}', using Raw16Khz16BitMonoPcm")
            self.audio_format = speechsdk.SpeechSynthesisOutputFormat.Raw16Khz16BitMonoPcm
            audio_format_name = 'Raw16Khz16BitMonoPcm'

        # Extract sample rate from format name (e.g., "Raw8Khz..." -> 8000)
        if '8Khz' in audio_format_name:
            self.sample_rate = 8000
        elif '16Khz' in audio_format_name:
            self.sample_rate = 16000
        elif '24Khz' in audio_format_name:
            self.sample_rate = 24000
        elif '48Khz' in audio_format_name:
            self.sample_rate = 48000
        else:
            self.sample_rate = 16000  # Default

        # Initialize synthesizer
        self.synthesizer = None
        self.setup_synthesizer()

        # Streaming queue for real-time audio
        self.audio_queue = queue.Queue()
        self.is_streaming = False

        logger.info(f"✅ Azure TTS initialized: region={self.region}, language={self.language}, format={audio_format_name}, sample_rate={self.sample_rate}Hz")

    def setup_synthesizer(self):
        """Setup Azure Speech synthesizer with optimal settings"""
        try:
            # Create speech config
            if self.api_key:
                speech_config = speechsdk.SpeechConfig(
                    subscription=self.api_key,
                    region=self.region
                )
            else:
                # Use managed identity or default credentials
                speech_config = speechsdk.SpeechConfig(
                    region=self.region,
                    auth_token=self.get_auth_token()
                )

            # Set output format for lowest latency
            speech_config.set_speech_synthesis_output_format(self.audio_format)

            # Get voice name
            voice_name = self.get_voice_name()
            speech_config.speech_synthesis_voice_name = voice_name

            # Enable streaming for real-time synthesis
            # Use pull audio output stream for lowest latency
            self.pull_stream = speechsdk.audio.PullAudioOutputStream()
            audio_config = speechsdk.audio.AudioOutputConfig(stream=self.pull_stream)

            # Create synthesizer with streaming support
            self.synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )

            # Connect events for real-time streaming
            self.synthesizer.synthesis_started.connect(self.on_synthesis_started)
            self.synthesizer.synthesizing.connect(self.on_synthesizing)
            self.synthesizer.synthesis_completed.connect(self.on_synthesis_completed)

            logger.info(f"Synthesizer configured: voice={voice_name}, format=Raw16Khz16BitMonoPcm")

        except Exception as e:
            logger.error(f"Failed to setup synthesizer: {e}")
            raise

    def get_voice_name(self) -> str:
        """Get Azure voice name based on configuration"""
        lang_voices = self.voice_map.get(self.language, self.voice_map['en'])

        # Check if specific voice is configured
        configured_voice = self.voice_settings.get('voice', 'default')

        if configured_voice in lang_voices:
            return lang_voices[configured_voice]
        else:
            return lang_voices['default']

    def get_auth_token(self) -> Optional[str]:
        """Get authentication token for managed identity (optional)"""
        # Implement if using managed identity
        return None

    def on_synthesis_started(self, evt):
        """Called when synthesis starts"""
        logger.debug("Synthesis started")
        self.is_streaming = True

    def on_synthesizing(self, evt):
        """Called when audio data is being generated (streaming)"""
        # Get audio chunk
        audio_data = evt.result.audio_data

        if audio_data and len(audio_data) > 0:
            # Convert to numpy array (16-bit PCM)
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            # Normalize to float32 [-1, 1]
            audio_float = audio_np.astype(np.float32) / 32768.0

            # Put in queue for immediate playback
            self.audio_queue.put(audio_float)

            logger.debug(f"Streaming chunk: {len(audio_float)} samples")

    def on_synthesis_completed(self, evt):
        """Called when synthesis completes"""
        logger.debug("Synthesis completed")
        self.is_streaming = False
        self.audio_queue.put(None)  # Signal end of stream

    def synthesize_stream(self, text: str, callback: Optional[Callable] = None):
        """
        Synthesize text with streaming (lowest latency)
        Args:
            text: Text to synthesize
            callback: Optional callback for each audio chunk
        Returns:
            Generator yielding audio chunks
        """
        logger.info(f"Starting streaming synthesis: {text[:50]}...")

        # Apply SSML for better control
        ssml = self.build_ssml(text)

        # Start async synthesis
        result_future = self.synthesizer.speak_ssml_async(ssml)

        # Yield audio chunks as they arrive
        start_time = time.time()
        first_chunk_time = None
        total_samples = 0

        while True:
            try:
                # Get chunk with timeout
                chunk = self.audio_queue.get(timeout=0.1)

                if chunk is None:
                    # End of stream
                    break

                if first_chunk_time is None:
                    first_chunk_time = time.time() - start_time
                    logger.info(f"⚡ First audio chunk in {first_chunk_time*1000:.0f}ms")

                total_samples += len(chunk)

                # Yield chunk for playback
                yield chunk

                # Call callback if provided
                if callback:
                    callback(chunk)

            except queue.Empty:
                # Check if synthesis is still running
                if not self.is_streaming:
                    break

        # Get final result
        result = result_future.get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            duration_sec = total_samples / self.sample_rate
            total_time = time.time() - start_time
            logger.info(f"✅ Synthesis complete: {duration_sec:.1f}s audio in {total_time:.1f}s")
        else:
            logger.error(f"Synthesis failed: {result.reason}")

    def synthesize_to_file(self, text: str, output_file: str):
        """
        Synthesize text to file (for caching)
        Args:
            text: Text to synthesize
            output_file: Output WAV file path
        """
        ssml = self.build_ssml(text)

        # Use file output for this
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
        file_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.synthesizer._speech_config,
            audio_config=audio_config
        )

        result = file_synthesizer.speak_ssml_async(ssml).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            logger.info(f"Saved to file: {output_file}")
            return True
        else:
            logger.error(f"Failed to synthesize: {result.reason}")
            return False

    def synthesize_to_array(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize text to numpy array
        Args:
            text: Text to synthesize
        Returns:
            Audio as numpy array or None if failed
        """
        ssml = self.build_ssml(text)

        result = self.synthesizer.speak_ssml_async(ssml).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Get all audio data
            audio_data = result.audio_data

            # Convert to numpy
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            audio_float = audio_np.astype(np.float32) / 32768.0

            duration = len(audio_float) / self.sample_rate
            logger.info(f"Synthesized {duration:.1f}s of audio")

            return audio_float
        else:
            logger.error(f"Synthesis failed: {result.reason}")
            return None

    def build_ssml(self, text: str) -> str:
        """
        Build SSML markup for better control
        Args:
            text: Plain text to convert
        Returns:
            SSML formatted string
        """
        voice_name = self.get_voice_name()
        speed = self.voice_settings.get('speed', 1.0)
        pitch = self.voice_settings.get('pitch', 1.0)

        # Convert speed and pitch to percentages
        speed_percent = int((speed - 1.0) * 100)
        pitch_percent = int((pitch - 1.0) * 100)

        # Build SSML
        ssml = f"""
        <speak version='1.0' xml:lang='{self.language}'>
            <voice name='{voice_name}'>
                <prosody rate='{speed_percent:+d}%' pitch='{pitch_percent:+d}%'>
                    {text}
                </prosody>
            </voice>
        </speak>
        """

        return ssml.strip()

    def test_latency(self):
        """Test TTS latency"""
        test_text = "Testing audio latency"

        logger.info("="*50)
        logger.info("AZURE TTS LATENCY TEST")
        logger.info("="*50)

        # Test streaming latency
        logger.info("\n1. Streaming synthesis (lowest latency):")
        start = time.time()
        first_chunk = None

        for i, chunk in enumerate(self.synthesize_stream(test_text)):
            if i == 0:
                first_chunk = time.time() - start
                logger.info(f"   First chunk: {first_chunk*1000:.0f}ms")

        total = time.time() - start
        logger.info(f"   Total time: {total*1000:.0f}ms")

        # Test full synthesis
        logger.info("\n2. Full synthesis:")
        start = time.time()
        audio = self.synthesize_to_array(test_text)
        total = time.time() - start
        logger.info(f"   Total time: {total*1000:.0f}ms")

        if audio is not None:
            duration = len(audio) / self.sample_rate
            logger.info(f"   Audio duration: {duration:.1f}s")
            logger.info(f"   RTF: {total/duration:.2f}x")

        logger.info("="*50)


# Test function
def test_azure_tts():
    """Test Azure TTS with sample configuration"""
    config = {
        'tts_model': 'azure',
        'tts_access_link': 'https://westeurope.tts.speech.microsoft.com/cognitiveservices/v1',
        'tts_secret_key': '',  # Add your key here for testing
        'language': 'ro',
        'voice_settings': {
            'voice': 'female',
            'speed': 1.0,
            'pitch': 1.0
        }
    }

    # Initialize TTS
    tts = AzureTTS(config)

    # Test latency
    tts.test_latency()

    # Test Romanian
    print("\n🇷🇴 Testing Romanian:")
    text_ro = "Bună ziua! Acesta este un test pentru sistemul de sinteză vocală."
    for i, chunk in enumerate(tts.synthesize_stream(text_ro)):
        if i == 0:
            print(f"Got first chunk: {len(chunk)} samples")

    # Test Lithuanian
    config['language'] = 'lt'
    tts_lt = AzureTTS(config)
    print("\n🇱🇹 Testing Lithuanian:")
    text_lt = "Labas! Tai yra balso sintezės sistemos testas."
    audio = tts_lt.synthesize_to_array(text_lt)
    if audio is not None:
        print(f"Generated {len(audio)/tts_lt.sample_rate:.1f}s of Lithuanian audio")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_azure_tts()