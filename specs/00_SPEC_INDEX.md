# MediSync AI — Complete TDD Specification Suite

## How to Read These Specs

Every `.md` file in this `specs/` directory is a **binding specification**.
A module is **done** when:
1. All functions described in the spec are implemented.
2. All test cases listed in the corresponding test spec pass.
3. No test outside that module's boundary is broken.

## Spec → File → Test Mapping

| Spec File | Covers | Test File(s) |
|---|---|---|
| `core/SPEC_types.md` | `core/types.py` | `tests/unit/test_types.py` |
| `core/SPEC_config.md` | `core/config.py` | `tests/unit/test_config.py` |
| `core/SPEC_security.md` | `core/security.py` | `tests/unit/test_security.py` |
| `core/SPEC_errors.md` | `core/errors.py` | all modules |
| `patient/SPEC_patient_management.md` | `patient/patient_management.py` | `tests/unit/test_patient.py` |
| `appointment/SPEC_appointment_system.md` | `appointment/appointment_system.py` | `tests/unit/test_appointment.py` |
| `ai_engine/SPEC_speech_to_text.md` | `ai_engine/speech_to_text.py` | `tests/unit/test_speech.py` |
| `ai_engine/SPEC_nlp_engine.md` | `ai_engine/nlp_engine.py` | `tests/unit/test_nlp.py` |
| `ai_engine/SPEC_priority_engine.md` | `ai_engine/priority_engine.py` | `tests/unit/test_priority.py` |
| `dashboard/SPEC_dashboard.md` | `dashboard/dashboard.py` | `tests/unit/test_dashboard.py` |
| `api/SPEC_api.md` | All `api/` files | `tests/integration/test_api.py` |
| `frontend/SPEC_frontend.md` | All `frontend/` files | component specs |
| `tests/SPEC_conftest.md` | `tests/conftest.py` | shared fixtures |
| `tests/SPEC_e2e.md` | `tests/integration/test_e2e.py` | end-to-end |
| `scripts/SPEC_scripts.md` | All `scripts/` files | manual verification |

## TDD Workflow

```
1. Read module spec → understand contracts
2. Read test spec → understand what pass looks like
3. Write test stubs (failing)
4. Implement module until tests pass
5. Run full suite — no regressions allowed
```

## Definition of Done (per module)

- [ ] All functions from spec implemented with correct signatures
- [ ] All `MUST` requirements from spec met
- [ ] All test cases in test spec pass
- [ ] Type annotations on all public functions
- [ ] Docstring on every class and public method
- [ ] No direct cross-module imports that violate the dependency table
- [ ] `make test-unit` passes
- [ ] `make test-integration` passes (requires Docker / MongoDB Atlas)

## Module Dependency Table

```
core/types.py         ← no dependencies (pure domain)
core/config.py        ← no dependencies
core/security.py      ← core/config.py
core/errors.py        ← no dependencies

storage/              ← core/config.py

patient/              ← core/types.py, core/errors.py, storage/
appointment/          ← core/types.py, patient/
ai_engine/            ← core/types.py, patient/
dashboard/            ← patient/, appointment/, ai_engine/

api/                  ← ALL above modules (thin HTTP wrapper)
frontend/             ← api/ (REST client)
```
