import pytest
import wave
import io
import asyncio
from unittest.mock import patch, MagicMock

from medisync.ai_engine.speech_to_text import SpeechProcessor, TranscriptionResult
from medisync.core.config import Settings
from medisync.core.errors import SpeechProcessingError

@pytest.fixture
def mock_settings():
    return Settings(
        use_mock_ai=True,
        mongodb_url="mongodb://localhost:27017",
        jwt_secret_key="secret"
    )

@pytest.fixture
def processor(mock_settings):
    return SpeechProcessor(mock_settings)

def create_mock_wav(duration_sec=1.0, channels=1, sample_rate=16000):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2) # 16-bit
        wf.setframerate(sample_rate)
        # write empty frames
        frames = int(duration_sec * sample_rate)
        wf.writeframes(b"\x00" * frames * 2 * channels)
    return buffer.getvalue()

class TestSpeechProcessor:
    @pytest.mark.asyncio
    async def test_empty_audio_raises(self, processor):
        with pytest.raises(SpeechProcessingError, match="empty"):
            await processor.transcribe_audio(b"")

    @pytest.mark.asyncio
    async def test_unsupported_format_raises(self, processor):
        with pytest.raises(SpeechProcessingError, match="Unsupported audio format"):
            await processor.transcribe_audio(b"dummy data", audio_format="flac")

    @pytest.mark.asyncio
    async def test_mock_transcribe_returns_result(self, processor):
        dummy_audio = b"dummy audio data with sufficient length to bypass the length check " * 100
        result = await processor.transcribe_audio(dummy_audio)
        assert isinstance(result, TranscriptionResult)
        assert result.text == "Patient reports chest pain"
        assert result.confidence == 1.0

    @pytest.mark.asyncio
    async def test_mock_transcribe_too_short_raises(self, processor):
        dummy_audio = b"short"
        with pytest.raises(SpeechProcessingError, match="too short"):
            await processor.transcribe_audio(dummy_audio)

    @pytest.mark.asyncio
    async def test_text_simulation(self, processor):
        result = await processor.transcribe_text_simulation("Hello world")
        assert result.text == "Hello world"
        assert result.confidence == 1.0

class TestAudioQualityDetection:
    @pytest.mark.asyncio
    async def test_detect_empty_audio(self, processor):
        result = await processor.detect_audio_quality(b"")
        assert result["is_valid"] is False
        assert result["duration_seconds"] == 0.0

    @pytest.mark.asyncio
    async def test_detect_valid_wav(self, processor):
        wav_data = create_mock_wav(duration_sec=2.0, sample_rate=44100)
        result = await processor.detect_audio_quality(wav_data)
        assert result["is_valid"] is True
        assert result["sample_rate"] == 44100
        assert result["channels"] == 1
        assert abs(result["duration_seconds"] - 2.0) < 0.1
        assert result["noise_level"] == "low"

    @pytest.mark.asyncio
    async def test_detect_invalid_format(self, processor):
        # random bytes instead of wav
        result = await processor.detect_audio_quality(b"RIFF but not a real wav format 1234567890 1234567890 1234567890")
        assert result["is_valid"] is True # The fallback case sets is_valid=True with 0 stats
        assert result["sample_rate"] == 0
