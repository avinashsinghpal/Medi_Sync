import re
from dataclasses import dataclass, field
from typing import Optional
from medisync.core.types import PriorityLevel
from medisync.core.config import Settings
from medisync.ai_engine.nlp_engine import NLPEngine

CRITICAL_SYMPTOMS = [
    "chest pain",
    "heart attack",
    "cardiac arrest",
    "stroke",
    "loss of consciousness",
    "difficulty breathing",
    "anaphylaxis",
    "severe bleeding",
    "seizure",
    "suicidal ideation",
    "overdose",
]

@dataclass
class PriorityAssessment:
    priority_level: PriorityLevel
    risk_score: float
    estimated_duration_minutes: int
    risk_factors: list[str] = field(default_factory=list)
    urgent_flags: list[str] = field(default_factory=list)
    recommendation: str = ""
    confidence: float = 0.0

class PriorityEngine:
    def __init__(self, nlp_engine: NLPEngine, settings: Settings):
        self.nlp_engine = nlp_engine
        self.settings = settings

    async def predict_priority(self, symptoms_text: str, patient_history: Optional[dict] = None) -> PriorityAssessment:
        extraction = await self.nlp_engine.extract_from_text(symptoms_text)
        
        urgent_flags = []
        for sym in extraction.symptoms:
            if any(crit in sym.lower() for crit in CRITICAL_SYMPTOMS):
                urgent_flags.append(sym)
                
        # 2. Calculate symptom_severity_score
        symptom_score = 0.0
        if urgent_flags:
            symptom_score = 1.0
        elif extraction.severity_indicators:
            if any(x in ["severe", "acute", "crushing"] for x in extraction.severity_indicators):
                symptom_score = 0.9
            else:
                symptom_score = 0.6
        elif extraction.symptoms:
            symptom_score = 0.3
            
        # 3. Calculate history_risk_score
        history_risk_score = 0.0
        risk_factors = []
        if patient_history:
            if patient_history.get("age", 0) > 65:
                history_risk_score += 0.15
                risk_factors.append("Age > 65")
            if patient_history.get("prior_cardiac_history"):
                history_risk_score += 0.30
                risk_factors.append("Prior cardiac history")
            if patient_history.get("prior_stroke"):
                history_risk_score += 0.30
                risk_factors.append("Prior stroke")
            if patient_history.get("diabetes"):
                history_risk_score += 0.10
                risk_factors.append("Diabetes")
            if patient_history.get("hypertension"):
                history_risk_score += 0.10
                risk_factors.append("Hypertension")
            if patient_history.get("active_cancer"):
                history_risk_score += 0.25
                risk_factors.append("Active cancer")
            if patient_history.get("immunocompromised"):
                history_risk_score += 0.20
                risk_factors.append("Immunocompromised")
            if patient_history.get("prior_hospitalization_30d"):
                history_risk_score += 0.20
                risk_factors.append("Prior hospitalization in last 30 days")
                
        # 4. Combine risk score
        risk_score = min(1.0, 0.6 * symptom_score + 0.4 * history_risk_score)
        
        # 5 & 6. Apply priority thresholds and absolute critical symptoms
        priority_level = PriorityLevel.ROUTINE
        if urgent_flags:
            priority_level = PriorityLevel.CRITICAL
            risk_score = max(risk_score, self.settings.critical_symptom_threshold)
        elif risk_score >= self.settings.critical_symptom_threshold:
            priority_level = PriorityLevel.CRITICAL
        elif risk_score >= self.settings.moderate_symptom_threshold:
            priority_level = PriorityLevel.MODERATE
            
        # 7. Estimate duration
        duration = await self.estimate_duration(symptoms_text, patient_history)
        
        recommendation = "Schedule routine appointment."
        if priority_level == PriorityLevel.CRITICAL:
            recommendation = "Immediate medical attention required."
        elif priority_level == PriorityLevel.MODERATE:
            recommendation = "Schedule appointment within 24 hours."

        return PriorityAssessment(
            priority_level=priority_level,
            risk_score=round(risk_score, 2),
            estimated_duration_minutes=duration,
            risk_factors=risk_factors,
            urgent_flags=urgent_flags,
            recommendation=recommendation,
            confidence=0.85
        )

    async def estimate_duration(self, symptoms_text: str, patient_history: Optional[dict] = None) -> int:
        extraction = await self.nlp_engine.extract_from_text(symptoms_text)
        duration = 10
        
        # +5 min per unique symptom cluster
        duration += 5 * len(extraction.symptoms)
        
        if patient_history:
            # +10 min if patient has 3+ chronic conditions
            chronic_conditions = sum([
                patient_history.get("prior_cardiac_history", False),
                patient_history.get("prior_stroke", False),
                patient_history.get("diabetes", False),
                patient_history.get("hypertension", False),
                patient_history.get("active_cancer", False),
                patient_history.get("immunocompromised", False),
            ])
            if chronic_conditions >= 3:
                duration += 10
                
            if patient_history.get("age", 0) > 65:
                duration += 5
        else:
            # +5 min for first-time patient (no history)
            duration += 5
            
        # Temporarily check if it would be critical to add duration
        is_critical = False
        for sym in extraction.symptoms:
            if any(crit in sym.lower() for crit in CRITICAL_SYMPTOMS):
                is_critical = True
                break
        if is_critical or (extraction.severity_indicators and any(x in ["severe", "acute", "crushing"] for x in extraction.severity_indicators)):
             duration += 15
             
        if duration > self.settings.max_consultation_time_minutes:
            duration = self.settings.max_consultation_time_minutes
            
        return duration

    async def get_queue_order(self, patients: list[dict]) -> list[dict]:
        def priority_key(p):
            # Sort order: CRITICAL (0), MODERATE (1), ROUTINE (2)
            p_map = {PriorityLevel.CRITICAL: 0, PriorityLevel.MODERATE: 1, PriorityLevel.ROUTINE: 2}
            # Fallback for dicts that may contain string values instead of Enums
            level = p.get('priority_level')
            if isinstance(level, str):
                try:
                    level = PriorityLevel(level)
                except ValueError:
                    level = PriorityLevel.ROUTINE
                    
            return (p_map.get(level, 2), p.get('scheduled_at'))

        sorted_patients = sorted(patients, key=priority_key)
        for i, p in enumerate(sorted_patients):
            p['queue_position'] = i + 1
        return sorted_patients
