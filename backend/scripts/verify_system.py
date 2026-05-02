import argparse
import urllib.request
import urllib.error
import json
import time

def parse_args():
    parser = argparse.ArgumentParser(description="Smoke test for MediSync AI Backend")
    parser.add_argument("--base-url", type=str, default="http://localhost:8000", help="Base URL of the API")
    return parser.parse_args()

def do_request(method, url, data=None):
    req = urllib.request.Request(url, method=method)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/json')
    
    body = json.dumps(data).encode('utf-8') if data else None
    
    try:
        with urllib.request.urlopen(req, data=body) as response:
            resp_body = response.read().decode('utf-8')
            return response.status, json.loads(resp_body) if resp_body else {}
    except urllib.error.HTTPError as e:
        resp_body = e.read().decode('utf-8')
        print(f"HTTPError {e.code}: {resp_body}")
        return e.code, json.loads(resp_body) if resp_body else {}
    except urllib.error.URLError as e:
        print(f"URLError: {e.reason}")
        return 0, {}

def run_smoke_test(base_url):
    print("=== MediSync Smoke Test ===")
    
    # 1. Create Patient
    print("\n1. Creating test patient...")
    patient_data = {
        "full_name": "Smoke Test Patient",
        "date_of_birth": "1990-01-01",
        "gender": "other",
        "contact_email": f"smoketest_{int(time.time())}@example.com",
        "contact_phone": "+1000000000"
    }
    status, p_res = do_request('POST', f"{base_url}/api/patients", patient_data)
    if status not in (200, 201):
        print("❌ Failed to create patient")
        return
    
    patient_id = p_res.get("patient_id")
    print(f"✅ Created patient: {patient_id}")

    # 2. Book Appointment
    print("\n2. Booking appointment...")
    appointment_data = {
        "patient_id": patient_id,
        "scheduled_at": "2030-01-01T10:00:00Z",
        "consultation_type": "teleconsult",
        "symptoms_description": "mild fever and cough"
    }
    status, a_res = do_request('POST', f"{base_url}/api/appointments", appointment_data)
    if status not in (200, 201):
        print("❌ Failed to book appointment")
        return
    
    appointment_id = a_res.get("appointment_id")
    print(f"✅ Booked appointment: {appointment_id}")

    # 3. Doctor Confirms and Starts
    print("\n3. Starting consultation...")
    doctor_id = "D-SMOKE"
    status, _ = do_request('PATCH', f"{base_url}/api/appointments/{appointment_id}/confirm", {"doctor_id": doctor_id})
    if status != 200:
        print("❌ Failed to confirm appointment")
        return
        
    status, _ = do_request('PATCH', f"{base_url}/api/appointments/{appointment_id}/start")
    if status != 200:
        print("❌ Failed to start consultation")
        return
    print("✅ Consultation started")

    # 4. Process Consultation
    print("\n4. Processing consultation text...")
    consultation_data = {
        "appointment_id": appointment_id,
        "text_input": "Patient reports mild fever and dry cough. Rest and fluids advised."
    }
    status, c_res = do_request('POST', f"{base_url}/api/consultation/process", consultation_data)
    if status != 200:
        print("❌ Failed to process consultation")
        return
        
    print(f"✅ Consultation processed. AI Priority: {c_res.get('priority_level')}")
    consultation_id = c_res.get("consultation_id")

    # 5. Complete Consultation
    print("\n5. Completing consultation...")
    status, _ = do_request('PATCH', f"{base_url}/api/appointments/{appointment_id}/complete", {"consultation_id": consultation_id})
    if status != 200:
        print("❌ Failed to complete appointment")
        return
    print("✅ Consultation completed successfully")

    print("\n🎉 Smoke test passed!")

if __name__ == "__main__":
    args = parse_args()
    # Ensure backend is running before hitting this script
    run_smoke_test(args.base_url)
