## Purpose
AI Consultation Assistant — converts doctor speech (audio or text) into
structured medical data using speech-to-text + NLP.

**Doctor speaks naturally. System extracts clinical entities automatically.**

## File Location
`medisync/ai_engine/speech_to_text.py`

## Dependencies
- `medisync/core/types.py` → `ConsultationLog`
- `medisync/core/errors.py` → `SpeechProcessingError`
- `medisync/core/config.py` → `Settings`
- `openai-whisper` or `faster-whisper` (based on `settings.speech_provider`)
- `tempfile`, `pathlib`, `io`

---

## Class: `SpeechProcessor`

```python
class SpeechProcessor:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._model = None  # Lazy-loaded on first use

    def _load_model(self):
        """Load whisper model lazily on first transcription request."""
        ...
```

---

## Methods to Implement

### `async transcribe_audio(audio_data: bytes, audio_format: str = "wav") -> TranscriptionResult`
**Input:** Raw audio bytes (WAV, MP3, M4A, WebM supported)
**Flow:**
1. Write audio bytes to temp file
2. Load Whisper model if not already loaded
3. Call transcription with language="en" (configurable)
4. Extract confidence score from segments
5. Clean and return transcript
6. Delete temp file in finally block

**Output:**
```python
@dataclass
class TranscriptionResult:
    text: str              # Full transcribed text
    language: str          # Detected or forced language
    confidence: float      # Average segment confidence (0.0–1.0)
    duration_seconds: float  # Audio duration
    segments: list[dict]   # Raw Whisper segments for debugging
```

**Raises:**
- `SpeechProcessingError` if audio is too short (< 1 second)
- `SpeechProcessingError` if audio is too long (> 3600 seconds)
- `SpeechProcessingError` if transcription returns empty text
- `SpeechProcessingError` if model loading fails

### `async transcribe_text_simulation(text: str) -> TranscriptionResult`
- For testing and demo purposes: treats input text AS the transcript
- Returns a `TranscriptionResult` with `confidence=1.0` and simulated metadata
- Used when `settings.use_mock_ai=True`

### `async transcribe_stream(audio_chunks: AsyncIterator[bytes]) -> AsyncIterator[str]`
- Real-time streaming transcription (stretch goal)
- Yields partial transcripts as audio chunks arrive
- Minimum chunk size: 0.5 seconds of audio

### `async detect_audio_quality(audio_data: bytes) -> dict`
- Returns quality metrics before transcription:
```python
{
  "is_valid": bool,
  "duration_seconds": float,
  "sample_rate": int,
  "channels": int,
  "noise_level": str,      # "low" | "medium" | "high"
  "recommendation": str    # Human-readable quality advice
}
```

---

## Supported Audio Formats

| Format | Extension | Notes |
|---|---|---|
| WAV | .wav | Preferred. No quality loss. |
| MP3 | .mp3 | Common. Slight quality loss. |
| M4A | .m4a | iOS voice memos format. |
| WebM | .webm | Browser MediaRecorder API default. |
| OGG | .ogg | Open-source alternative. |

---

## Mock Implementation (for `use_mock_ai=True`)

When `settings.use_mock_ai` is True, the SpeechProcessor MUST:
1. Skip all actual audio processing
2. Return a realistic `TranscriptionResult` with mock data
3. Simulate a 500ms delay to mimic real processing
4. Still validate input (raise errors for empty audio)

---

## Edge Case Handling

| Scenario | Expected Behavior |
|---|---|
| Empty audio bytes | `SpeechProcessingError` ("Audio data is empty") |
| Audio < 1 second | `SpeechProcessingError` ("Audio too short for transcription") |
| Unsupported format | `SpeechProcessingError` ("Unsupported audio format: {format}") |
| Very noisy audio | Return transcript with low confidence score |
| Multiple speakers | Transcribe all speech; no speaker diarization (not in scope) |
| Non-English audio | Transcribe anyway; report detected language in result |

---

## Expected Test Outcomes (from `tests/unit/test_speech.py`)

| Test | Input | Expected Output |
|---|---|---|
| transcribe_audio empty | b"" | `SpeechProcessingError` |
| transcribe_text_simulation | "Patient has chest pain" | TranscriptionResult with text and confidence=1.0 |
| detect_audio_quality valid | valid WAV bytes | dict with is_valid=True |
| transcribe_audio short | < 1s audio | `SpeechProcessingError` |
| mock mode | settings.use_mock_ai=True | Returns mock result, no model loaded |
