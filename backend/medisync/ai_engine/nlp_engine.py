import re
from collections import OrderedDict
from dataclasses import dataclass, field
from medisync.core.types import ConsultationLog
from medisync.core.errors import NLPExtractionError
from medisync.core.config import Settings

_NLP_CACHE_MAX_SIZE = 256  # Maximum number of cached extraction results

@dataclass
class ExtractionResult:
    symptoms: list[str] = field(default_factory=list)
    medications: list[str] = field(default_factory=list)
    dosages: dict[str, str] = field(default_factory=dict)
    diagnoses: list[str] = field(default_factory=list)
    severity_indicators: list[str] = field(default_factory=list)
    medical_terms: list[str] = field(default_factory=list)
    negations: list[str] = field(default_factory=list)
    vitals: dict[str, str] = field(default_factory=dict)
    summary: str = ""
    confidence: float = 0.0

class NLPEngine:
    """
    Clinical NLP engine — extracts structured medical entities from free-form text.

    Uses an internal LRU cache (max 256 entries) to avoid reprocessing identical
    transcripts within a single session, reducing AI pipeline latency.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings   = settings
        # Bounded LRU cache: OrderedDict preserves insertion order for eviction
        self._cache: OrderedDict[str, ExtractionResult] = OrderedDict()
        self.abbreviations = {
            "sob": "shortness of breath",
            "bp":  "blood pressure",
            "hr":  "heart rate",
        }
        self.severity_keywords = {
            "critical": ["severe", "acute", "crushing", "loss of consciousness", "critical"],
            "high":     ["significant", "persistent", "worsening"],
            "moderate": ["moderate", "intermittent"],
            "low":      ["mild", "slight", "occasional"],
        }

    def clear_cache(self) -> None:
        """Flush the extraction cache — useful in tests or after model reloads."""
        self._cache.clear()

    def _cache_get(self, key: str) -> ExtractionResult | None:
        """Retrieve a cached result, promoting it to most-recently-used."""
        if key not in self._cache:
            return None
        self._cache.move_to_end(key)
        return self._cache[key]

    def _cache_set(self, key: str, result: ExtractionResult) -> None:
        """Store a result, evicting the oldest entry if at capacity."""
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = result
        if len(self._cache) > _NLP_CACHE_MAX_SIZE:
            self._cache.popitem(last=False)  # evict LRU (oldest) entry

    async def extract_from_text(self, text: str) -> ExtractionResult:
        """
        Extract clinical entities from free-form medical text.

        Results are cached by normalised text key (LRU, max 256 entries).

        Raises:
            NLPExtractionError: if *text* is empty or fewer than 10 characters.
        """
        if not text or len(text.strip()) < 10:
            raise NLPExtractionError("Text is too short or empty for NLP extraction.")

        cache_key = text.strip().lower()
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        if self.settings.use_mock_ai:
            result = ExtractionResult(
                symptoms=["chest pain", "dizziness"],
                medications=["aspirin"],
                dosages={"aspirin": "75mg daily"},
                confidence=0.85,
                summary="Patient reports chest pain and dizziness."
            )
            self._cache_set(cache_key, result)
            return result

        # Basic rule-based fallback when not mocked
        # In a real scenario, spaCy / LLM calls happen here
        text_lower = text.lower()
        
        result = ExtractionResult(confidence=0.7)
        
        # ── Symptom extraction (comprehensive keyword list) ──
        symptom_keywords = [
            "chest pain", "back pain", "headache", "head ache", "fever", "cough",
            "nausea", "vomiting", "dizziness", "fatigue", "shortness of breath",
            "abdominal pain", "stomach pain", "sore throat", "runny nose",
            "body ache", "body pain", "joint pain", "muscle pain", "weakness",
            "swelling", "rash", "itching", "insomnia", "anxiety", "depression",
            "weight loss", "weight gain", "blurred vision", "ear pain",
            "palpitations", "constipation", "diarrhea", "bloating",
            "numbness", "tingling", "loss of appetite", "chills",
            "throbbing", "migraine", "cramps", "sprain", "fracture",
        ]
        
        # Check negations first
        negation_patterns = [f"no {s}" for s in symptom_keywords] + [f"denies {s}" for s in symptom_keywords]
        negated_symptoms = set()
        for neg in negation_patterns:
            if neg in text_lower:
                symptom = neg.replace("no ", "").replace("denies ", "")
                negated_symptoms.add(symptom)
                result.negations.append(symptom)
        
        for symptom in symptom_keywords:
            if symptom in text_lower and symptom not in negated_symptoms:
                result.symptoms.append(symptom)
        
        # ── Severity indicators ──
        for level, keywords in self.severity_keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    result.severity_indicators.append(kw)
        
        # ── Medication extraction ──
        medication_keywords = [
            "aspirin", "ibuprofen", "paracetamol", "acetaminophen", "amoxicillin",
            "metformin", "lisinopril", "amlodipine", "omeprazole", "pantoprazole",
            "atorvastatin", "losartan", "hydrochlorothiazide", "prednisone",
            "azithromycin", "ciprofloxacin", "doxycycline", "metoprolol",
            "levothyroxine", "albuterol", "insulin", "warfarin", "clopidogrel",
            "gabapentin", "tramadol", "diclofenac", "naproxen", "cetirizine",
            "montelukast", "fluticasone", "salbutamol",
        ]
        
        for med in medication_keywords:
            if med in text_lower:
                result.medications.append(med)
                # Try to find dosage pattern near the medication name
                dosage_pattern = re.search(
                    rf'{med}\s+(\d+\s*(?:mg|ml|mcg|g|units?)(?:\s*(?:daily|twice|once|bd|tds|qid|od|hs|prn))?)',
                    text_lower
                )
                if dosage_pattern:
                    result.dosages[med] = dosage_pattern.group(1).strip()
        
        # ── Vitals extraction ──
        # Blood pressure: various formats
        bp_patterns = [
            re.search(r'(?:bp|blood pressure)\s*(?:is|of|:)?\s*(\d{2,3})\s*(?:/|over)\s*(\d{2,3})', text_lower),
            re.search(r'(\d{2,3})\s*(?:/|over)\s*(\d{2,3})\s*(?:mm\s*hg|mmhg)?', text_lower),
        ]
        for bp_match in bp_patterns:
            if bp_match:
                systolic, diastolic = int(bp_match.group(1)), int(bp_match.group(2))
                if 60 <= systolic <= 250 and 30 <= diastolic <= 150:
                    result.vitals["blood_pressure"] = f"{systolic}/{diastolic}"
                    break
        
        # Heart rate
        hr_match = re.search(r'(?:heart rate|hr|pulse)\s*(?:is|of|:)?\s*(\d{2,3})\s*(?:bpm)?', text_lower)
        if hr_match:
            result.vitals["heart_rate"] = f"{hr_match.group(1)} bpm"
        
        # Temperature
        temp_match = re.search(r'(?:temp|temperature)\s*(?:is|of|:)?\s*(\d{2,3}(?:\.\d)?)\s*(?:°?[fc]|degrees?)?', text_lower)
        if temp_match:
            result.vitals["temperature"] = f"{temp_match.group(1)}°F"
        
        # Pain scale
        pain_match = re.search(r'(\d{1,2})\s*(?:out of|/)\s*10\s*(?:on the pain scale|pain)?', text_lower)
        if pain_match:
            result.vitals["pain_scale"] = f"{pain_match.group(1)}/10"
        
        # ── Diagnoses (common patterns) ──
        diagnosis_keywords = [
            "common flu", "influenza", "hypertension", "diabetes", "migraine",
            "gastritis", "bronchitis", "pneumonia", "asthma", "arthritis",
            "sinusitis", "pharyngitis", "conjunctivitis", "urinary tract infection",
            "anxiety disorder", "tension headache", "vertigo",
        ]
        for diag in diagnosis_keywords:
            if diag in text_lower:
                result.diagnoses.append(diag)

        result.summary = await self.generate_consultation_summary(result, {})
        self._cache_set(cache_key, result)
        return result

    async def extract_from_consultation_log(self, log: ConsultationLog) -> ExtractionResult:
        """
        Extract entities from a ConsultationLog.

        Uses ``log.raw_transcript`` when available, falling back to ``log.notes``.

        Raises:
            NLPExtractionError: if both transcript and notes are empty.
        """
        text_to_process = log.raw_transcript or log.notes
        if not text_to_process:
            raise NLPExtractionError("Consultation log contains no transcript or notes.")
        return await self.extract_from_text(text_to_process)

    async def generate_consultation_summary(self, extraction: ExtractionResult, patient_context: dict) -> str:
        """
        Produce a human-readable 1-2 sentence consultation summary.

        Uses a rule-based template (LLM-enhanced when an API key is configured).
        """
        symptoms_str = ", ".join(extraction.symptoms) if extraction.symptoms else "no specific symptoms"
        risk_str = "No specific risk factors"
        if extraction.severity_indicators:
            risk_str = f"Severity indicators noted: {', '.join(extraction.severity_indicators)}"
        return f"Patient reports {symptoms_str}. {risk_str}."

    async def normalize_symptom(self, symptom: str) -> str:
        """
        Canonically normalise a symptom string.

        Example: "chest hurt" → "chest pain"
        """
        symptom_lower = symptom.lower().strip()
        if "hurt" in symptom_lower and "chest" in symptom_lower:
            return "chest pain"
        return symptom_lower
