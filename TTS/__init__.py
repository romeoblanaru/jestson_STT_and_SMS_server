"""
TTS (Text-to-Speech) Module

This package contains various TTS provider implementations:
- tts_azure: Azure Cognitive Services TTS
- tts_openai: OpenAI TTS
- tts_google: Google Cloud TTS
- tts_liepa: Liepa TTS (Lithuanian)
- tts_base: Base abstract class for TTS providers
"""

__all__ = ['tts_azure', 'tts_openai', 'tts_google', 'tts_liepa', 'tts_base']
