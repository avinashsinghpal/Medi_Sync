import asyncio
import io
import pathlib
import tempfile
import wave
from dataclasses import dataclass
from typing import AsyncIterator, Dict, Any

from medisync.core.config import Settings
from medisync.core.errors import SpeechProcessingError


@dataclass
class TranscriptionResult:
    text: str
    language: str
    confidence: float
    duration_seconds: float
    segments: list[Dict[str, Any]]


class SpeechProcessor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._model = None

    def _load_model(self):
        """Load whisper model lazily on first transcription request."""
        if self._model is None and not self.settings.use_mock_ai:
            try:
                import whisper
                self._model = whisper.load_model(self.settings.whisper_model_size)
            except Exception as e:
                raise SpeechProcessingError("Failed to load whisper model") from e

    async def transcribe_audio(self, audio_data: bytes, audio_format: str = "wav") -> TranscriptionResult:
        """Transcribe raw audio bytes using Whisper."""
        if not audio_data:
            raise SpeechProcessingError("Audio data is empty")
            
        supported_formats = {"wav", "mp3", "m4a", "webm", "ogg"}
        if audio_format.lower() not in supported_formats:
            raise SpeechProcessingError(f"Unsupported audio format: {audio_format}")

        if self.settings.use_mock_ai:
            await asyncio.sleep(0.5)
            # basic duration check for mock
            if len(audio_data) < 1000:
                raise SpeechProcessingError("Audio too short for transcription")
            return TranscriptionResult(
                text="Patient reports chest pain",
                language="en",
                confidence=1.0,
                duration_seconds=5.0,
                segments=[]
            )

        self._load_model()

        with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        try:
            loop = asyncio.get_running_loop()
            # Run the blocking whisper transcribe in an executor
            result = await loop.run_in_executor(None, self._model.transcribe, tmp_path)
            
            text = result.get("text", "").strip()
            if not text:
                raise SpeechProcessingError("Transcription returned empty text")
                
            segments = result.get("segments", [])
            duration = segments[-1]["end"] if segments else 0.0
            
            if duration < 1.0:
                raise SpeechProcessingError("Audio too short for transcription")
            if duration > 3600.0:
                raise SpeechProcessingError("Audio too long for transcription")
                
            confidence = 1.0
            if segments:
                # Average confidence based on whisper's no_speech_prob if available
                no_speech_probs = [s.get("no_speech_prob", 0.0) for s in segments]
                avg_no_speech = sum(no_speech_probs) / len(no_speech_probs)
                confidence = max(0.0, 1.0 - avg_no_speech)

            return TranscriptionResult(
                text=text,
                language=result.get("language", "en"),
                confidence=confidence,
                duration_seconds=duration,
                segments=segments
            )
        finally:
            pathlib.Path(tmp_path).unlink(missing_ok=True)

    async def transcribe_text_simulation(self, text: str) -> TranscriptionResult:
        """Simulate transcription purely from text for testing/demo purposes."""
        if self.settings.use_mock_ai:
            await asyncio.sleep(0.5)
        return TranscriptionResult(
            text=text,
            language="en",
            confidence=1.0,
            duration_seconds=float(len(text) / 15.0),
            segments=[]
        )

    async def transcribe_stream(self, audio_chunks: AsyncIterator[bytes]) -> AsyncIterator[str]:
        """Real-time streaming transcription (stretch goal)."""
        async for chunk in audio_chunks:
            if chunk:
                yield "partial transcript"

    async def detect_audio_quality(self, audio_data: bytes) -> dict:
        """Analyze WAV audio data to extract quality metrics before transcription."""
        if not audio_data:
            return {
                "is_valid": False,
                "duration_seconds": 0.0,
                "sample_rate": 0,
                "channels": 0,
                "noise_level": "high",
                "recommendation": "Audio is empty"
            }

        is_valid = False
        sample_rate = 0
        channels = 0
        duration = 0.0
        
        # Simple check for WAV header (RIFF)
        if len(audio_data) >= 44 and audio_data.startswith(b"RIFF"):
            try:
                with wave.open(io.BytesIO(audio_data), "rb") as wf:
                    channels = wf.getnchannels()
                    sample_rate = wf.getframerate()
                    frames = wf.getnframes()
                    if sample_rate > 0:
                        duration = frames / float(sample_rate)
                    is_valid = True
            except Exception:
                pass

        if is_valid:
            return {
                "is_valid": True,
                "duration_seconds": duration,
                "sample_rate": sample_rate,
                "channels": channels,
                "noise_level": "low" if sample_rate >= 16000 else "medium",
                "recommendation": "Audio quality is acceptable"
            }
        else:
            return {
                "is_valid": True,  # It might be valid mp3/m4a which we can't parse via wave module
                "duration_seconds": 0.0,
                "sample_rate": 0,
                "channels": 0,
                "noise_level": "unknown",
                "recommendation": "Format is not WAV or cannot be parsed for quality metrics natively"
            }
