#!/usr/bin/env python3
"""
scripts/seed_demo_data.py
Seeds the database with realistic demo data for presentations:
- 10 demo patients with varied medical histories
- 20 appointments across different priority levels
- 5 completed consultations with full transcripts

Run:
    python scripts/seed_demo_data.py [--base-url http://localhost:8000]
"""
import sys
import json
import argparse
import urllib.request
import urllib.error
import random
from datetime import datetime, timezone, timedelta

def _request(method: str, url: str, body: dict | None = None, token: str | None = None):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {"detail": str(e)}
    except Exception as e:
        return 0, {"detail": str(e)}

def login_doctor(base: str):
    status, data = _request("POST", f"{base}/api/auth/login", {
        "email": "doctor@medisync.com",
        "password": "doctor123",
    })
    if status == 200:
        return data["token"], data["user_id"]
    print(f"Failed to login doctor: {data}")
    sys.exit(1)

def seed_patients(base: str, token: str):
    patients = [
        {"full_name": "Eleanor Rigby", "dob": "1945-02-14", "gender": "female"},
        {"full_name": "John Doe", "dob": "1980-05-20", "gender": "male"},
        {"full_name": "Alice Wonderland", "dob": "1992-11-01", "gender": "female"},
        {"full_name": "Bob Builder", "dob": "1975-08-30", "gender": "male"},
        {"full_name": "Charlie Chaplin", "dob": "1950-04-16", "gender": "male"},
        {"full_name": "Diana Prince", "dob": "1988-03-22", "gender": "female"},
        {"full_name": "Edward Scissorhands", "dob": "1995-12-15", "gender": "male"},
        {"full_name": "Fiona Shrek", "dob": "1990-07-07", "gender": "female"},
        {"full_name": "George Jetson", "dob": "1962-09-18", "gender": "male"},
        {"full_name": "Hannah Abbott", "dob": "2000-01-25", "gender": "female"},
    ]
    patient_ids = []
    print("Seeding 10 demo patients...")
    for i, p in enumerate(patients):
        status, data = _request("POST", f"{base}/api/patients", {
            "full_name": p["full_name"],
            "date_of_birth": p["dob"],
            "gender": p["gender"],
            "contact_email": f"demo{i}@medisync.com",
            "contact_phone": f"55500010{i}",
        }, token=token)
        if status == 201:
            patient_ids.append(data["patient_id"])
        else:
            print(f"Failed to create patient {p['full_name']}: {data}")
    return patient_ids

def seed_appointments(base: str, token: str, doctor_id: str, patient_ids: list):
    symptoms = [
        "Routine checkup, no issues",
        "Mild headache and runny nose",
        "Moderate back pain after lifting boxes",
        "Severe chest pain and shortness of breath",
        "Skin rash on left arm",
        "Follow-up for hypertension",
        "Fever of 101F and chills",
        "Sprained ankle from running",
        "Sudden loss of vision in right eye",
        "Persistent cough for 3 weeks",
    ]
    appointment_ids = []
    print("Seeding 20 appointments...")
    now = datetime.now(timezone.utc)
    for i in range(20):
        # Stagger appointments over today and tomorrow
        days_offset = i % 2
        hours_offset = 9 + (i % 8) # 9 AM to 4 PM
        sched = now.replace(hour=hours_offset, minute=0, second=0, microsecond=0) + timedelta(days=days_offset)
        
        status, data = _request("POST", f"{base}/api/appointments", {
            "patient_id": random.choice(patient_ids),
            "doctor_id": doctor_id,
            "scheduled_at": sched.isoformat(),
            "consultation_type": random.choice(["in_person", "video", "emergency"]),
            "symptoms_description": random.choice(symptoms),
        }, token=token)
        if status in (200, 201):
            appointment_ids.append(data["appointment_id"])
        else:
            print(f"Failed to book appointment: {data}")
    return appointment_ids

def seed_consultations(base: str, token: str, appointment_ids: list):
    transcripts = [
        "Patient presents with severe chest pain and left arm numbness. Prescribe Aspirin 75mg daily. Urgent cardiology referral required.",
        "Routine follow-up for diabetes. Blood sugar is well controlled. Continue Metformin 500mg twice daily.",
        "Patient complains of seasonal allergies. Eyes itchy. Prescribed Cetirizine 10mg once daily. Recommend avoiding pollen exposure.",
        "Moderate back pain reported after heavy lifting. No neurological deficits. Recommend ibuprofen and rest for 3 days.",
        "Patient presents with fever and cough. Lungs are clear. Likely viral infection. Advise rest, hydration, and paracetamol for fever."
    ]
    print("Seeding 5 completed consultations...")
    
    # Process the first 5 appointments
    for i in range(5):
        if i >= len(appointment_ids): break
        app_id = appointment_ids[i]
        
        # 1. Start appointment
        _request("PATCH", f"{base}/api/appointments/{app_id}/start", token=token)
        
        # 2. Process text
        status, data = _request("POST", f"{base}/api/consultation/process-text", {
            "text": transcripts[i]
        }, token=token)
        
        if status == 200:
            # Complete consultation using the consultation result isn't currently 
            # fully wired in a single mock API, we just process it to generate history records
            # Wait, the verify_system uses /api/consultation/process with appointment_id
            c_status, c_data = _request("POST", f"{base}/api/consultation/process", {
                "appointment_id": app_id,
                "text_input": transcripts[i]
            }, token=token)
            
            if c_status == 200 and "consultation_id" in c_data:
                # 3. Complete
                _request("PATCH", f"{base}/api/appointments/{app_id}/complete", {
                    "consultation_id": c_data["consultation_id"]
                }, token=token)
            else:
                print(f"Failed to process consultation {i}: {c_data}")
        else:
            print(f"Failed to run NLP {i}: {data}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()

    print(f"Connecting to {args.base_url}...")
    token, doctor_id = login_doctor(args.base_url)
    print(f"Logged in as doctor: {doctor_id}")

    patient_ids = seed_patients(args.base_url, token)
    if not patient_ids:
        print("Failed to seed patients.")
        sys.exit(1)
        
    app_ids = seed_appointments(args.base_url, token, doctor_id, patient_ids)
    if not app_ids:
        print("Failed to seed appointments.")
        sys.exit(1)
        
    seed_consultations(args.base_url, token, app_ids)
    print("✅ Demo data seeded successfully.")

if __name__ == "__main__":
    main()
