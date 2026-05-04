#!/usr/bin/env python3
"""
scripts/verify_system.py
MediSync smoke-test / system verification script.

Usage:
    python scripts/verify_system.py [--base-url http://localhost:8000]

Exit codes:
    0  — all checks passed
    1  — one or more checks failed
"""
import sys
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime, timezone


# ── ANSI colour helpers ──────────────────────────────────────────────────────

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def _ok(msg):  print(f"  {GREEN}✔{RESET}  {msg}")
def _fail(msg): print(f"  {RED}✗{RESET}  {msg}")
def _info(msg): print(f"  {CYAN}ℹ{RESET}  {msg}")
def _warn(msg): print(f"  {YELLOW}⚠{RESET}  {msg}")


# ── HTTP helpers ─────────────────────────────────────────────────────────────

def _request(method: str, url: str, body: dict | None = None, token: str | None = None):
    """Make an HTTP request and return (status_code, response_dict)."""
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = {"detail": str(e)}
        return e.code, body
    except Exception as e:
        return 0, {"detail": str(e)}


# ── Individual checks ────────────────────────────────────────────────────────

def check_health(base: str) -> bool:
    status, data = _request("GET", f"{base}/api/health")
    if status == 200 and data.get("status") == "ok":
        db_ok = data.get("db_connected", False)
        _ok(f"Health check passed — version {data.get('version', '?')} | DB connected: {db_ok}")
        if not db_ok:
            _warn("Database is not connected — some features may fail")
        return True
    _fail(f"Health check failed (HTTP {status}): {data.get('detail', data)}")
    return False


def check_docs(base: str) -> bool:
    req = urllib.request.Request(f"{base}/api/docs")
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                _ok("OpenAPI docs accessible at /api/docs")
                return True
    except Exception:
        pass
    _fail("OpenAPI docs not accessible at /api/docs")
    return False


def check_openapi_json(base: str) -> bool:
    status, data = _request("GET", f"{base}/openapi.json")
    if status == 200 and "paths" in data:
        n_paths = len(data["paths"])
        _ok(f"OpenAPI schema valid — {n_paths} endpoint paths defined")
        return True
    _fail(f"OpenAPI JSON unavailable or malformed (HTTP {status})")
    return False


def check_unauthorized_access(base: str) -> bool:
    status, data = _request("GET", f"{base}/api/patients")
    if status == 401:
        _ok("Unauthenticated request correctly returns 401")
        return True
    _fail(f"Expected 401 for unauthenticated request, got HTTP {status}")
    return False


def check_doctor_login(base: str) -> str | None:
    status, data = _request("POST", f"{base}/api/auth/login", {
        "email": "doctor@medisync.com",
        "password": "doctor123",
    })
    if status == 200 and "token" in data:
        _ok(f"Doctor login succeeded — user_id: {data.get('user_id', '?')}")
        return data["token"]
    _fail(f"Doctor login failed (HTTP {status}): {data.get('detail', data)}")
    return None


def check_patient_login(base: str) -> str | None:
    status, data = _request("POST", f"{base}/api/auth/login", {
        "email": "patient@medisync.com",
        "password": "patient123",
    })
    if status == 200 and "token" in data:
        _ok(f"Patient login succeeded — user_id: {data.get('user_id', '?')}")
        return data["token"]
    _fail(f"Patient login failed (HTTP {status}): {data.get('detail', data)}")
    return None


def check_list_doctors(base: str, token: str) -> bool:
    status, data = _request("GET", f"{base}/api/doctors", token=token)
    if status == 200:
        total = data.get("total", 0)
        _ok(f"GET /api/doctors — {total} doctor(s) found")
        if total == 0:
            _warn("No doctors in the database. Run: make seed")
        return True
    _fail(f"GET /api/doctors failed (HTTP {status}): {data.get('detail', data)}")
    return False


def check_list_patients(base: str, token: str) -> bool:
    status, data = _request("GET", f"{base}/api/patients", token=token)
    if status == 200:
        total = data.get("total", 0)
        _ok(f"GET /api/patients — {total} patient(s) found")
        if total == 0:
            _warn("No patients in the database. Run: make seed")
        return True
    _fail(f"GET /api/patients failed (HTTP {status}): {data.get('detail', data)}")
    return False


def check_patient_self_access(base: str, patient_token: str) -> bool:
    # Get our user_id first from token decode
    status, data = _request("GET", f"{base}/api/patients/P-DEMO01", token=patient_token)
    if status == 200:
        _ok(f"Patient can access own profile — {data.get('full_name', '?')}")
        return True
    if status == 403:
        _fail("Patient received 403 for own profile — check user_id in token")
        return False
    _fail(f"Patient self-access failed (HTTP {status}): {data.get('detail', data)}")
    return False


def check_dashboard_overview(base: str, token: str) -> bool:
    status, data = _request("GET", f"{base}/api/dashboard/overview?doctor_id=D-DEMO01", token=token)
    if status == 200:
        total = data.get("total_patients_today", 0)
        _ok(f"Dashboard overview — {total} patient(s) today")
        return True
    _fail(f"Dashboard overview failed (HTTP {status}): {data.get('detail', data)}")
    return False


def check_doctor_queue(base: str, token: str) -> bool:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    status, data = _request("GET", f"{base}/api/doctor/D-DEMO01/queue?d={today}", token=token)
    if status == 200:
        queue_len = len(data.get("queue", []))
        _ok(f"Doctor queue endpoint — {queue_len} appointment(s) in queue")
        return True
    _fail(f"Doctor queue failed (HTTP {status}): {data.get('detail', data)}")
    return False


def check_end_to_end_workflow(base: str, token: str) -> bool:
    # 1. Book appointment
    import random
    from datetime import datetime, timezone, timedelta
    offset = random.randint(10, 1000)
    future_date = (datetime.now(timezone.utc) + timedelta(days=offset)).replace(hour=10, minute=0, second=0).isoformat()
    status, data = _request("POST", f"{base}/api/appointments", {
        "patient_id": "P-DEMO01",
        "doctor_id": "D-DEMO01",
        "scheduled_at": future_date,
        "consultation_type": "in_person",
        "symptoms_description": "Headache and fever for two days, feeling unwell",
    }, token=token)
    if status not in (200, 201):
        _fail(f"Appointment booking failed (HTTP {status}): {data.get('detail', data)}")
        return False

    apt_id = data.get("appointment_id", "?")
    priority = data.get("priority_level", "?")
    _ok(f"Appointment booked — ID: {apt_id[:8]}... | Priority: {priority}")

    # 2. Process NLP
    import urllib.parse
    form_data = urllib.parse.urlencode({
        "appointment_id": apt_id,
        "text_input": "Patient reports severe chest pain and difficulty breathing since morning"
    }).encode("utf-8")
    
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
    headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(f"{base}/api/consultation/process", data=form_data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            c_status, c_data = resp.status, json.loads(resp.read())
    except Exception as e:
        _fail(f"NLP endpoint failed: {str(e)}")
        return False

    if c_status == 200:
        symptoms = c_data.get("structured_output", {}).get("symptoms", [])
        _ok(f"NLP endpoint — extracted {len(symptoms)} symptom(s): {symptoms[:3]}")
        return True

    _fail(f"NLP endpoint failed (HTTP {c_status}): {c_data.get('detail', c_data)}")
    return False


# ── Main runner ──────────────────────────────────────────────────────────────

def run_all_checks(base: str) -> int:
    start = datetime.now()
    failures = 0

    print(f"\n{BOLD}{CYAN}╔══════════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║        MediSync System Verification          ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════════════╝{RESET}")
    print(f"  Target: {BOLD}{base}{RESET}")
    print(f"  Time:   {start.strftime('%Y-%m-%d %H:%M:%S UTC')}\n")

    # ── Section 1: Infrastructure ────────────────────────────────────────
    print(f"{BOLD}[1/5] Infrastructure{RESET}")
    for fn in (check_health, check_docs, check_openapi_json):
        if not fn(base):
            failures += 1
    print()

    # ── Section 2: Auth ──────────────────────────────────────────────────
    print(f"{BOLD}[2/5] Authentication{RESET}")
    if not check_unauthorized_access(base):
        failures += 1
    doc_token = check_doctor_login(base)
    if not doc_token:
        failures += 1
    pat_token = check_patient_login(base)
    if not pat_token:
        failures += 1
    print()

    # ── Section 3: Data endpoints ────────────────────────────────────────
    print(f"{BOLD}[3/5] Patient & Doctor Data{RESET}")
    if doc_token:
        for fn in (check_list_doctors, check_list_patients):
            if not fn(base, doc_token):
                failures += 1
    else:
        _warn("Skipping data checks — doctor token unavailable")
        failures += 2
    if pat_token:
        if not check_patient_self_access(base, pat_token):
            failures += 1
    else:
        _warn("Skipping patient self-access — patient token unavailable")
        failures += 1
    print()

    # ── Section 4: Dashboard ─────────────────────────────────────────────
    print(f"{BOLD}[4/4] Dashboard & Queue{RESET}")
    if doc_token:
        for fn in (check_dashboard_overview, check_doctor_queue):
            if not fn(base, doc_token):
                failures += 1
    else:
        _warn("Skipping dashboard checks — doctor token unavailable")
        failures += 2
    print()

    # ── Section 5: End-to-End booking & AI ─────────────────────────────
    print(f"{BOLD}[5/5] End-to-End Appointment Booking & NLP{RESET}")
    if doc_token:
        # We need the doctor token to run the NLP processing step
        if not check_end_to_end_workflow(base, doc_token):
            failures += 1
    else:
        _warn("Skipping booking & NLP check — doctor token unavailable")
        failures += 1
    print()

    # ── Summary ──────────────────────────────────────────────────────────
    elapsed = (datetime.now() - start).total_seconds()
    if failures == 0:
        print(f"{BOLD}{GREEN}✔ All checks passed in {elapsed:.2f}s — system is healthy!{RESET}\n")
        return 0
    else:
        print(f"{BOLD}{RED}✗ {failures} check(s) failed in {elapsed:.2f}s — review output above.{RESET}\n")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="MediSync system verification script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the MediSync backend (default: http://localhost:8000)",
    )
    args = parser.parse_args()
    sys.exit(run_all_checks(args.base_url))


if __name__ == "__main__":
    main()
