import io
import wave
import pytest

from medisync.core.errors import SpeechProcessingError
from medisync.ai_engine.speech_to_text import SpeechProcessor


def create_valid_wav_bytes(duration_sec: float = 2.0, sample_rate: int = 16000) -> bytes:
    """Helper to generate valid WAV audio bytes in memory."""
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        num_frames = int(duration_sec * sample_rate)
        wf.writeframes(b'\x00' * (num_frames * 2))
    return buf.getvalue()


@pytest.mark.asyncio
async def test_transcribe_audio_empty(settings):
    processor = SpeechProcessor(settings)
    with pytest.raises(SpeechProcessingError, match="Audio data is empty"):
        await processor.transcribe_audio(b"")


@pytest.mark.asyncio
async def test_transcribe_text_simulation(settings):
    processor = SpeechProcessor(settings)
    text_input = "Patient has chest pain"
    result = await processor.transcribe_text_simulation(text_input)
    
    assert result.text == text_input
    assert result.confidence == 1.0


@pytest.mark.asyncio
async def test_detect_audio_quality_valid(settings):
    processor = SpeechProcessor(settings)
    wav_bytes = create_valid_wav_bytes(duration_sec=3.0)
    
    result = await processor.detect_audio_quality(wav_bytes)
    assert result["is_valid"] is True
    assert result["duration_seconds"] == 3.0
    assert result["channels"] == 1
    assert result["sample_rate"] == 16000


@pytest.mark.asyncio
async def test_transcribe_audio_short(settings):
    processor = SpeechProcessor(settings)
    short_audio = b"not enough bytes for 1 second"
    
    with pytest.raises(SpeechProcessingError, match="Audio too short for transcription"):
        await processor.transcribe_audio(short_audio)


@pytest.mark.asyncio
async def test_mock_mode(settings):
    # settings.use_mock_ai is already True from the fixture
    processor = SpeechProcessor(settings)
    
    # Send enough bytes so it passes the short mock check length
    valid_wav = create_valid_wav_bytes(duration_sec=2.0)
    result = await processor.transcribe_audio(valid_wav)
    
    assert result.text == "Patient reports chest pain"
    assert result.confidence == 1.0
    # No model should have been loaded
    assert processor._model is None
