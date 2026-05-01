## Purpose
Utility scripts for database seeding, demo data generation, and system verification.

## Files

### `scripts/seed_demo_data.py`
Seeds the database with realistic demo data for presentations:
- 10 demo patients with varied medical histories
- 20 appointments across different priority levels
- 5 completed consultations with full transcripts
- Run: `python scripts/seed_demo_data.py`

### `scripts/reset_db.py`
Drops and recreates all MongoDB collections with proper indexes.
WARNING: Destructive. For dev/test use only.
- Run: `python scripts/reset_db.py --confirm`

### `scripts/verify_system.py`
Runs a quick smoke test against a running backend:
1. Creates a test patient
2. Books an appointment
3. Processes a text consultation
4. Verifies output JSON structure
5. Cleans up test data
- Run: `python scripts/verify_system.py --base-url http://localhost:8000`

### `scripts/export_patients.py`
Exports all patient summaries to CSV for reporting.
Sanitizes PII according to GDPR guidelines (no raw contact info).
- Run: `python scripts/export_patients.py --output report.csv`

---

## Makefile Targets

```makefile
make dev          # Start backend with uvicorn --reload
make frontend     # Start Vite dev server (frontend/)
make test-unit    # Run unit tests (no Docker needed)
make test-int     # Run integration tests (requires Docker)
make seed         # Run seed_demo_data.py
make verify       # Run verify_system.py against localhost
make reset-db     # Reset database (with confirmation prompt)
```
