# MediSync AI — Unified Intelligent Patient History System

> *"Transforming fragmented healthcare into intelligent, real-time clinical support."*

---

## 🏥 What is MediSync AI?

MediSync AI is a Python-based, AI-powered healthcare platform that unifies fragmented patient records across hospitals, enabling:

- **Centralized patient health records** — one patient, one intelligent profile
- **AI-powered consultation assistant** — doctor speech → structured clinical data
- **Smart appointment scheduling** — guided booking with AI-predicted wait times
- **Patient prioritization engine** — 🔴 Critical / 🟡 Moderate / 🟢 Routine classification
- **Doctor dashboard** — real-time priority queue, patient summaries, one-click access

---

## 📁 Project Structure

```
MediSync_AI/
├── specs/                    # 📋 Binding TDD specification documents
│   ├── 00_SPEC_INDEX.md      # Master index + TDD workflow
│   ├── core/                 # Data types, config, security, errors
│   ├── patient/              # Patient management spec
│   ├── appointment/          # Appointment system spec
│   ├── ai_engine/            # Speech, NLP, priority engine specs
│   ├── dashboard/            # Doctor dashboard spec
│   ├── api/                  # FastAPI REST layer spec
│   ├── frontend/             # React.js frontend spec
│   ├── tests/                # Test fixture and e2e scenario specs
│   └── scripts/              # Utility scripts spec
│
├── backend/
│   ├── pyproject.toml        # Python dependencies
│   └── medisync/
│       ├── core/             # types.py, config.py, security.py, errors.py
│       ├── patient/          # patient_management.py
│       ├── appointment/      # appointment_system.py
│       ├── ai_engine/        # speech_to_text.py, nlp_engine.py, priority_engine.py
│       ├── dashboard/        # dashboard.py
│       ├── storage/          # MongoDB repositories
│       └── api/              # FastAPI app, routers, schemas
│
├── frontend/
│   └── src/                  # React components, pages, hooks, store
│
├── tests/                    # pytest unit + integration tests
├── scripts/                  # Seed, verify, export utilities
├── docs/                     # Architecture diagrams, API docs
├── .env.example              # Environment variable template
├── docker-compose.yml        # MongoDB + Redis + Backend
└── Makefile                  # Developer shortcuts
```

---

## ⚡ Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd MediSync_AI
cp .env.example .env  # Add MONGODB_URL and JWT_SECRET_KEY

# 2. Start infrastructure
docker-compose up -d  # MongoDB + Redis

# 3. Install backend
cd backend
pip install -e ".[dev]"
python -m spacy download en_core_web_sm

# 4. Seed demo data
make seed

# 5. Run backend
make dev   # → http://localhost:8000/api/docs

# 6. Run frontend (separate terminal)
cd frontend
npm install
make frontend  # → http://localhost:5173
```

---

## 🧪 Running Tests

```bash
make test-unit   # Fast unit tests, no Docker needed
make test-int    # Integration tests (requires running MongoDB)
make test-all    # Full suite
```

---

## 📋 Development Status

> Python and JavaScript source files are empty stubs.
> Read the spec files in `specs/` to understand implementation requirements.
> Follow TDD: read spec → write tests → implement module.

---

## 👥 Team Development Plan

See `docs/DEVELOPMENT_PLAN.md` for 4-person team allocation with dependency mapping.
