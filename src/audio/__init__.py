"""Audio generation module - TTS and audio processing."""

from .tts import (
    TTSProvider,
    ElevenLabsTTS,
    MockTTS,
    TTSResult,
    WordTimestamp,
    get_tts_provider,
)

__all__ = [
    "TTSProvider",
    "ElevenLabsTTS",
    "MockTTS",
    "TTSResult",
    "WordTimestamp",
    "get_tts_provider",
]
