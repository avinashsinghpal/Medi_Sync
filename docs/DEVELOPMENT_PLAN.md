# MediSync AI — Team Development Plan
## 4-Person Team | Dependency-Driven Assignment

---

## Team Roles

| Person | Role | Expertise |
|---|---|---|
| **Dev A** | Backend Foundation & AI Engine | Python, FastAPI, NLP/ML |
| **Dev B** | Patient & Appointment Systems | Python, Backend, MongoDB |
| **Dev C** | API Layer & Integration | Python, FastAPI, REST APIs |
| **Dev D** | Frontend & Dashboard | React.js, UI/UX, JavaScript |

---

## Phase 1 — Foundation *(All work in parallel, no blocking)*

All Phase 1 tasks have **zero interdependencies** — the entire team can start simultaneously.

### Dev A — Core Domain & AI Models
**Files:** `specs/core/`, `specs/ai_engine/`

| Task | Spec | File |
|---|---|---|
| Implement `core/types.py` | SPEC_types.md | All domain dataclasses and enums |
| Implement `core/config.py` | SPEC_config.md | Settings singleton |
| Implement `core/errors.py` | SPEC_errors.md | Exception hierarchy |
| Implement `core/security.py` | SPEC_security.md | JWT + password hashing |
| Implement `ai_engine/speech_to_text.py` | SPEC_speech_to_text.md | Whisper integration |
| Write `tests/unit/test_types.py` | SPEC_conftest.md | All type validation tests |
| Write `tests/unit/test_security.py` | SPEC_security.md | Auth tests |
| Write `tests/unit/test_speech.py` | SPEC_speech_to_text.md | Speech mock tests |

---

### Dev B — Patient & Appointment Systems
**Files:** `specs/patient/`, `specs/appointment/`

| Task | Spec | File |
|---|---|---|
| Design MongoDB schemas (collections, indexes) | SPEC_types.md | `storage/patient_repository.py` |
| Implement `storage/appointment_repository.py` | SPEC_types.md | MongoDB CRUD for appointments |
| Write `tests/unit/test_patient.py` stubs | SPEC_patient_management.md | All patient test cases |
| Write `tests/unit/test_appointment.py` stubs | SPEC_appointment_system.md | All appointment test cases |

> ⚠️ **Blocked by Dev A:** `patient_management.py` and `appointment_system.py` require Dev A's `core/types.py` and `core/errors.py`. MongoDB schema design and test stubs can be written before that is ready.

---

### Dev C — API Layer Setup
**Files:** `specs/api/`, `medisync/api/`

| Task | Spec | File |
|---|---|---|
| Setup FastAPI project structure | SPEC_api.md | `api/app.py`, `api/dependencies.py` |
| Write all Pydantic request/response schemas | SPEC_api.md | `api/schemas/*.py` |
| Write router stubs (empty endpoints) | SPEC_api.md | `api/routers/*.py` |
| Write `tests/integration/test_api.py` stubs | SPEC_api.md | All API test cases |
| Configure CORS, error handlers, middleware | SPEC_api.md | `api/app.py` |

> ⚠️ **Blocked by Dev B:** Router implementations cannot be wired until Dev B's services exist. Schemas and stubs can be written independently.

---

### Dev D — Frontend Foundation
**Files:** `specs/frontend/`

| Task | Spec | File |
|---|---|---|
| Initialize Vite + React project | SPEC_frontend.md | `frontend/` setup |
| Setup React Router, Zustand, React Query | SPEC_frontend.md | `store/`, `hooks/` |
| Implement `authStore.js` | SPEC_frontend.md | Login state management |
| Build `shared/` components | SPEC_frontend.md | `PriorityBadge`, `Navbar`, `LoadingSpinner`, etc. |
| Build `LoginPage.jsx` | SPEC_frontend.md | Auth flow UI |
| Design CSS design system | SPEC_frontend.md | `index.css` with tokens |

> ⚠️ **Blocked by Dev C:** Pages that display real data require live API endpoints. UI shells and static components can be built before that.

---

## Phase 2 — Core Features *(Sequential dependencies begin)*

Start Phase 2 tasks as soon as their upstream dependencies from Phase 1 are completed — no need to wait for all of Phase 1 to finish.

### Dev A — NLP Engine & Priority Engine
**Unblocked by:** Own Phase 1 work (`core/types.py` done).

| Task | Spec | File |
|---|---|---|
| Implement `ai_engine/nlp_engine.py` | SPEC_nlp_engine.md | spaCy + LLM entity extraction |
| Implement `ai_engine/priority_engine.py` | SPEC_priority_engine.md | Risk scoring + prioritization |
| Write `tests/unit/test_nlp.py` | SPEC_nlp_engine.md | All extraction test cases |
| Write `tests/unit/test_priority.py` | SPEC_priority_engine.md | Priority classification tests |

---

### Dev B — Patient & Appointment Services
**Unblocked by:** Dev A's `core/types.py` and `core/errors.py`.

| Task | Spec | File |
|---|---|---|
| Implement `patient/patient_management.py` | SPEC_patient_management.md | All CRUD + search operations |
| Implement `appointment/appointment_system.py` | SPEC_appointment_system.md | Booking + state machine |
| Integration-test against real MongoDB | SPEC_conftest.md | `tests/integration/` |
| Hand off service interfaces to Dev C | — | Document `PatientManager` API |

---

### Dev C — API Endpoint Implementation
**Unblocked by:** Dev B's `patient_management.py` and `appointment_system.py`.

| Task | Spec | File |
|---|---|---|
| Wire `patients.py` router → `PatientManager` | SPEC_api.md | All patient endpoints live |
| Wire `appointments.py` router → `AppointmentSystem` | SPEC_api.md | All appointment endpoints live |
| Implement JWT auth middleware | SPEC_security.md | Bearer token validation |
| Run integration tests | SPEC_api.md | `tests/integration/test_api.py` |

---

### Dev D — Doctor Dashboard UI
**Unblocked by:** Dev C's patient + appointment API endpoints (mock data acceptable initially).

| Task | Spec | File |
|---|---|---|
| Build `PatientSummaryCard.jsx` | SPEC_frontend.md | Patient card with risk flags |
| Build `PriorityQueue.jsx` | SPEC_frontend.md | Priority-sorted appointment list |
| Build `DashboardStats.jsx` | SPEC_frontend.md | Stats cards |
| Build `DoctorDashboard.jsx` page | SPEC_frontend.md | Full dashboard assembly |
| Wire React Query hooks to live API | SPEC_frontend.md | `usePatientData`, `useDashboard` |

---

## Phase 3 — AI Integration & Final Assembly *(All services converge)*

Start Phase 3 as soon as Phase 2 for the relevant person is complete.

### Dev A — Dashboard Service + Full AI Pipeline
**Unblocked by:** Dev B's services + Dev A's NLP/priority engine.

| Task | Spec | File |
|---|---|---|
| Implement `dashboard/dashboard.py` | SPEC_dashboard.md | Full aggregation service |
| Write `tests/unit/test_dashboard.py` | SPEC_dashboard.md | Dashboard service tests |
| Performance tuning: AI pipeline caching | — | Reduce NLP latency |

---

### Dev B — End-to-End Testing & Scripts
**Unblocked by:** All backend services are implemented.

| Task | Spec | File |
|---|---|---|
| Write `tests/integration/test_e2e.py` | SPEC_e2e.md | Full consultation scenario |
| Write `scripts/seed_demo_data.py` | SPEC_scripts.md | Demo data for presentations |
| Write `scripts/verify_system.py` | SPEC_scripts.md | Smoke test script |
| Bug fixes from integration tests | — | Cross-module issues |

---

### Dev C — Consultation API + Dashboard API
**Unblocked by:** Dev A's `dashboard.py` and AI engine.

| Task | Spec | File |
|---|---|---|
| Wire `consultation.py` router → `DoctorDashboard` | SPEC_api.md | Consultation processing endpoint |
| Wire `dashboard.py` router → `DoctorDashboard` | SPEC_api.md | Dashboard overview endpoint |
| API documentation review | SPEC_api.md | OpenAPI docs polish |
| End-to-end integration test with Dev B | SPEC_e2e.md | Full scenario test |

---

### Dev D — Patient Interface + Consultation UI
**Unblocked by:** Dev C's consultation + dashboard API endpoints.

| Task | Spec | File |
|---|---|---|
| Build `SpeechRecorder.jsx` | SPEC_frontend.md | Audio capture component |
| Build `ConsultationPanel.jsx` | SPEC_frontend.md | Full consultation workspace |
| Build patient booking flow | SPEC_frontend.md | `BookingForm`, `SymptomInput` |
| Build `PatientDashboard.jsx` | SPEC_frontend.md | Patient self-service portal |
| Connect to live consultation API | — | Real-time transcript display |

---

## Dependency Map

```
Phase 1 (Parallel — start together):
  Dev A ──▶ core/types ──────────────────────────────▶ [Unblocks Dev B]
  Dev A ──▶ speech_to_text (standalone)
  Dev B ──▶ MongoDB schemas + test stubs (no blocker)
  Dev C ──▶ API schemas + router stubs (no blocker)
  Dev D ──▶ Frontend foundation + shared components (no blocker)

Phase 2 (As soon as upstream is ready):
  Dev A.core ──▶ Dev B.patient_management ──▶ Dev C.patients_router ──▶ Dev D.PriorityQueue
  Dev A.nlp  ──▶ Dev A.priority_engine ────────────────────────────▶ [Used in Phase 3]

Phase 3 (Converge):
  Dev A.dashboard ──▶ Dev C.dashboard_router ──▶ Dev D.ConsultationPanel
  Dev B.e2e_tests ──▶ System verification
```

---

## Critical Path (must not slip)

1. **Dev A: `core/types.py`** — Everything depends on this. Complete it first before any other module.
2. **Dev B: `patient_management.py`** — Dev C's patient API cannot go live without it.
3. **Dev C: JWT middleware** — Frontend auth cannot work without it.
4. **Dev A: `nlp_engine.py` + `priority_engine.py`** — Dashboard service cannot function without AI.

---

## Communication Protocols

| Sync Point | Trigger | Who | Purpose |
|---|---|---|---|
| Kickoff standup | Before Phase 1 starts | All | Assign tasks, confirm interfaces |
| Interface review | After `core/types.py` is merged | A + B + C | Confirm service contracts |
| API contract freeze | Before Dev D connects to live API | B + C + D | Finalize endpoint shapes |
| Integration day | After Phase 2 is complete | All | Wire everything together |
| Demo rehearsal | After Phase 3 is complete | All | Full scenario walkthrough |

---

## Definition of Done (Project Level)

- [ ] All spec files have corresponding implemented modules
- [ ] `make test-unit` passes with ≥ 90% coverage
- [ ] `make test-int` passes the full e2e scenario
- [ ] Doctor dashboard shows real-time priority queue
- [ ] Patient booking → consultation → history update works end-to-end
- [ ] `make seed` + `make verify` complete without errors
- [ ] API docs available at `/api/docs`
