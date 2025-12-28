"""Tests for audio/TTS module."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.audio import ElevenLabsTTS, TTSProvider, get_tts_provider
from src.audio.tts import MockTTS
from src.config import Config, TTSConfig


class TestMockTTS:
    """Tests for mock TTS provider."""

    @pytest.fixture
    def mock_tts(self):
        config = TTSConfig(provider="mock")
        return MockTTS(config)

    def test_generate_creates_file(self, mock_tts, tmp_path):
        output_path = tmp_path / "test.mp3"
        result = mock_tts.generate("Hello, world!", output_path)

        assert result == output_path
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_generate_stream_yields_bytes(self, mock_tts):
        chunks = list(mock_tts.generate_stream("Hello"))
        assert len(chunks) > 0
        assert all(isinstance(chunk, bytes) for chunk in chunks)

    def test_get_available_voices(self, mock_tts):
        voices = mock_tts.get_available_voices()
        assert len(voices) > 0
        assert "voice_id" in voices[0]
        assert "name" in voices[0]


class TestGetTTSProvider:
    """Tests for TTS provider factory."""

    def test_returns_mock_provider(self):
        config = Config()
        config.tts.provider = "mock"
        provider = get_tts_provider(config)
        assert isinstance(provider, MockTTS)

    def test_raises_for_unknown_provider(self):
        config = Config()
        config.tts.provider = "unknown_provider"
        with pytest.raises(ValueError, match="Unknown TTS provider"):
            get_tts_provider(config)

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test_key"})
    def test_returns_elevenlabs_with_api_key(self):
        config = Config()
        config.tts.provider = "elevenlabs"
        provider = get_tts_provider(config)
        assert isinstance(provider, ElevenLabsTTS)


class TestElevenLabsTTS:
    """Tests for ElevenLabs TTS provider."""

    @pytest.fixture
    def config(self):
        return TTSConfig(
            provider="elevenlabs",
            model="eleven_multilingual_v2",
        )

    def test_init_requires_api_key(self, config):
        # Clear env var if set
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ELEVENLABS_API_KEY", None)
            with pytest.raises(ValueError, match="API key required"):
                ElevenLabsTTS(config)

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test_key"})
    def test_init_with_env_api_key(self, config):
        tts = ElevenLabsTTS(config)
        assert tts.api_key == "test_key"

    def test_init_with_explicit_api_key(self, config):
        tts = ElevenLabsTTS(config, api_key="explicit_key")
        assert tts.api_key == "explicit_key"

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test_key"})
    def test_estimate_cost(self, config):
        tts = ElevenLabsTTS(config)

        # 1000 characters should cost about $0.30
        cost = tts.estimate_cost("a" * 1000)
        assert 0.2 < cost < 0.4  # Approximately $0.30

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test_key"})
    def test_default_voice_id(self, config):
        tts = ElevenLabsTTS(config)
        assert tts.voice_id is not None

    @patch.dict(os.environ, {"ELEVENLABS_API_KEY": "test_key"})
    def test_custom_voice_id(self, config):
        config.voice_id = "custom_voice_123"
        tts = ElevenLabsTTS(config)
        assert tts.voice_id == "custom_voice_123"


class TestTTSWithScript:
    """Tests for generating TTS from script scenes."""

    @pytest.fixture
    def mock_tts(self):
        config = TTSConfig(provider="mock")
        return MockTTS(config)

    @pytest.fixture
    def sample_voiceover_texts(self):
        return [
            "Every time you send a message to ChatGPT, something remarkable happens.",
            "LLM inference has two distinct phases.",
            "The solution is elegant: compute each Key and Value exactly once.",
        ]

    def test_generate_multiple_scenes(self, mock_tts, sample_voiceover_texts, tmp_path):
        """Test generating audio for multiple script scenes."""
        audio_files = []

        for i, text in enumerate(sample_voiceover_texts):
            output_path = tmp_path / f"scene_{i + 1}.mp3"
            result = mock_tts.generate(text, output_path)
            audio_files.append(result)

        # All files should be created
        assert len(audio_files) == 3
        assert all(f.exists() for f in audio_files)

    def test_total_audio_generation(self, mock_tts, tmp_path):
        """Test generating audio for a full script."""
        # Simulate a full script worth of voiceover
        full_voiceover = """
        Every time you send a message to ChatGPT, something remarkable happens.
        A neural network with billions of parameters generates a response,
        one token at a time. The naive approach gives us forty tokens per second.
        What the best systems achieve? Over three thousand five hundred.
        This is how they do it.
        """

        output_path = tmp_path / "full_script.mp3"
        result = mock_tts.generate(full_voiceover, output_path)

        assert result.exists()
        # For real TTS, we'd check duration matches expected
