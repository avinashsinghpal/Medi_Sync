.PHONY: dev frontend test-unit test-int seed verify reset-db lint format

# ── Development ────────────────────────────────────────────────────────────
dev:
	cd backend && uvicorn medisync.api.app:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

# ── Testing ────────────────────────────────────────────────────────────────
test-unit:
	cd backend && pytest tests/unit/ -v --cov=medisync --cov-report=term-missing

test-int:
	cd backend && pytest tests/integration/ -v --cov=medisync

test-all:
	cd backend && pytest -v --cov=medisync --cov-report=term-missing

# ── Scripts ────────────────────────────────────────────────────────────────
seed:
	cd backend && python scripts/seed_demo_data.py

verify:
	cd backend && python scripts/verify_system.py --base-url http://localhost:8000

reset-db:
	cd backend && python scripts/reset_db.py --confirm

# ── Code Quality ───────────────────────────────────────────────────────────
lint:
	cd backend && ruff check medisync/ tests/

format:
	cd backend && ruff format medisync/ tests/

# ── Docker ─────────────────────────────────────────────────────────────────
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# ── Frontend Setup ─────────────────────────────────────────────────────────
install-frontend:
	cd frontend && npm install

install-backend:
	cd backend && pip install -e ".[dev]" && python -m spacy download en_core_web_sm
