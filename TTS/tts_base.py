#!/usr/bin/env python3
"""
Base TTS Interface for Multiple Providers
Provides unified interface for Azure, OpenAI, Liepa, Google TTS
"""

from abc import ABC, abstractmethod
import numpy as np
import logging
from typing import Optional, Generator, Callable

logger = logging.getLogger(__name__)

class BaseTTS(ABC):
    """Abstract base class for TTS providers"""

    def __init__(self, config: dict):
        """
        Initialize TTS provider
        Args:
            config: Configuration dict from voice_config_manager
        """
        self.config = config
        self.language = config.get('language', 'en')
        self.voice_settings = config.get('voice_settings', {})
        self.api_key = config.get('tts_secret_key', '')
        self.endpoint = config.get('tts_access_link', '')

    @abstractmethod
    def synthesize_stream(self, text: str, callback: Optional[Callable] = None) -> Generator[np.ndarray, None, None]:
        """
        Synthesize text with streaming (lowest latency)
        Args:
            text: Text to synthesize
            callback: Optional callback for each audio chunk
        Yields:
            Audio chunks as numpy arrays (16kHz, mono, float32)
        """
        pass

    @abstractmethod
    def synthesize_to_array(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize text to numpy array
        Args:
            text: Text to synthesize
        Returns:
            Audio as numpy array (16kHz, mono, float32) or None if failed
        """
        pass

    @abstractmethod
    def synthesize_to_file(self, text: str, output_file: str) -> bool:
        """
        Synthesize text to file
        Args:
            text: Text to synthesize
            output_file: Output file path
        Returns:
            True if successful
        """
        pass

    def get_voice_name(self) -> str:
        """Get voice name for current language"""
        return self.voice_settings.get('voice', 'default')

    def get_speed(self) -> float:
        """Get speech speed multiplier"""
        return self.voice_settings.get('speed', 1.0)

    def get_pitch(self) -> float:
        """Get pitch multiplier"""
        return self.voice_settings.get('pitch', 1.0)