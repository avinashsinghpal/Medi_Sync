## Purpose
End-to-end test suite for MediSync AI demonstrating the complete system workflow.
Requires a running backend and test database (Docker Compose).

## File Location
`tests/integration/test_e2e.py`

---

## Demo Scenario: Full Consultation Workflow

This test validates the entire patient journey from booking to completed consultation.

### Step 1 — Patient Registration
```
POST /api/patients
→ Patient created with ID "P-XXXXXXXX"
```

### Step 2 — Appointment Booking
```
POST /api/appointments
Body: { patient_id, scheduled_at, symptoms_description: "severe chest pain and dizziness" }
→ Appointment created with:
   - priority_level = "critical" (AI-detected)
   - estimated_duration_minutes > 15 (AI-estimated for complex case)
```

### Step 3 — Doctor Views Queue
```
GET /api/doctor/{doctor_id}/queue
→ New appointment appears first in queue (CRITICAL priority)
→ priority_badge_color = "red"
```

### Step 4 — Doctor Confirms & Starts Consultation
```
PATCH /api/appointments/{id}/confirm → status: CONFIRMED
PATCH /api/appointments/{id}/start   → status: IN_SESSION
```

### Step 5 — Consultation Processing (Text Simulation)
```
POST /api/consultation/process
Body: {
  appointment_id: ...,
  text_input: "Patient reports chest pain 8/10 severity radiating to left arm. Prescribe aspirin 75mg daily."
}
→ ConsultationResult with:
   - transcript: the text input
   - symptoms: ["chest pain"]
   - medications: ["aspirin"]
   - dosages: {"aspirin": "75mg daily"}
   - priority_level: "critical"
   - consultation_summary: non-empty string
```

### Step 6 — Complete Consultation
```
PATCH /api/appointments/{id}/complete
→ status: COMPLETED
```

### Step 7 — Verify History Updated
```
GET /api/patients/{patient_id}/history
→ New MedicalRecord visible with linked consultation_id
```

---

## Test: Priority Engine Accuracy

- Book 3 appointments with: "mild headache", "moderate back pain", "crushing chest pain"
- GET /api/doctor/{id}/queue
- Verify order: "crushing chest pain" first (CRITICAL), "moderate back pain" second, "mild headache" last

---

## Test: Data Isolation

- Create 2 patients with different emails
- Verify their histories are independent
- Verify search by name returns only the correct patient

---

## Required Test Environment

```yaml
# docker-compose.test.yml
services:
  mongodb:
    image: mongo:7
    ports: ["27017:27017"]
  backend:
    build: ./backend
    environment:
      MONGODB_URL: mongodb://mongodb:27017
      JWT_SECRET_KEY: test-secret-key
      USE_MOCK_AI: "true"
    depends_on: [mongodb]
```
