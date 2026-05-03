import asyncio
import argparse
from datetime import datetime, date, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from medisync.core.config import get_settings
from medisync.storage.patient_repository import PatientRepository
from medisync.storage.appointment_repository import AppointmentRepository
from medisync.patient.patient_management import PatientManager
from medisync.appointment.appointment_system import AppointmentSystem
from medisync.ai_engine.nlp_engine import NLPEngine
from medisync.ai_engine.priority_engine import PriorityEngine
from medisync.core.types import PatientProfile, Appointment, ConsultationType, AppointmentStatus, PriorityLevel, ConsultationLog

async def seed_data():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]

    patient_repo = PatientRepository(db)
    appointment_repo = AppointmentRepository(db)
    
    await patient_repo.setup_indexes()
    await appointment_repo.setup_indexes()

    patient_manager = PatientManager(patient_repo, settings)
    nlp_engine = NLPEngine(settings)
    priority_engine = PriorityEngine(nlp_engine, settings)
    appointment_system = AppointmentSystem(appointment_repo, patient_manager, priority_engine, settings)

    print("Seeding database...")

    # 1. Create 10 demo patients
    patients = []
    patient_data = [
        ("Aarav Patel", date(1985, 4, 12), "male", "aarav.p@example.com", "+919876543210"),
        ("Isha Sharma", date(1992, 8, 22), "female", "isha.sharma@example.com", "+919876543211"),
        ("Rohan Gupta", date(1978, 11, 5), "male", "rohan.g@example.com", "+919876543212"),
        ("Priya Singh", date(1989, 2, 14), "female", "priya.s@example.com", "+919876543213"),
        ("Vikram Verma", date(1965, 7, 30), "male", "vikram.v@example.com", "+919876543214"),
        ("Ananya Desai", date(2001, 1, 19), "female", "ananya.d@example.com", "+919876543215"),
        ("Karan Mehta", date(1995, 9, 8), "male", "karan.m@example.com", "+919876543216"),
        ("Sneha Joshi", date(1982, 5, 25), "female", "sneha.j@example.com", "+919876543217"),
        ("Amit Kumar", date(1971, 12, 12), "male", "amit.k@example.com", "+919876543218"),
        ("Neha Reddy", date(1998, 3, 17), "female", "neha.r@example.com", "+919876543219"),
    ]

    from medisync.patient.patient_management import CreatePatientRequest
    for data in patient_data:
        p = CreatePatientRequest(
            full_name=data[0],
            date_of_birth=data[1].strftime("%Y-%m-%d"),
            gender=data[2],
            contact_email=data[3],
            contact_phone=data[4]
        )
        try:
            created_p = await patient_manager.create_patient(p)
            patients.append(created_p)
            print(f"Created patient: {created_p.full_name} ({created_p.patient_id})")
        except Exception as e:
            print(f"Error creating patient {data[0]}: {e}")
            existing_p = await patient_repo.collection.find_one({"contact.email": data[3]})
            if existing_p:
                from medisync.core.types import PatientProfile
                patients.append(PatientProfile(**existing_p))
                print(f"Found existing patient: {data[0]}")

    if not patients:
        print("No patients created. Aborting.")
        return

    # 2. Create 20 appointments across priority levels
    symptoms_pool = [
        "mild headache for 2 days", "severe chest pain and shortness of breath",
        "routine follow up", "fever and chills", "persistent back pain",
        "dizziness and nausea", "allergic reaction with rash", "stomach pain",
        "sprained ankle", "high blood pressure review"
    ]
    
    appointments = []
    base_time = datetime.now(timezone.utc).replace(hour=9, minute=0, second=0, microsecond=0)
    
    for i in range(20):
        p = patients[i % len(patients)]
        symptoms = symptoms_pool[i % len(symptoms_pool)]
        
        # Schedule them every 30 mins
        scheduled_time = base_time + timedelta(minutes=30 * i)
        
        app_req = Appointment(
            patient_id=p.patient_id,
            scheduled_at=scheduled_time,
            consultation_type=ConsultationType.IN_PERSON,
            symptoms_description=symptoms,
            estimated_duration_minutes=0  # will be auto-calculated
        )
        
        try:
            created_app = await appointment_system.book_appointment(app_req)
            appointments.append(created_app)
            print(f"Booked appointment for {p.full_name} at {scheduled_time.isoformat()} - Priority: {created_app.priority_level}")
        except Exception as e:
            print(f"Error booking appointment for {p.full_name}: {e}")

    # 3. Simulate 5 completed consultations
    doctor_id = "D-DEMO01"
    for i in range(5):
        if i >= len(appointments):
            break
        app = appointments[i]
        try:
            await appointment_system.confirm_appointment(app.appointment_id, doctor_id)
            await appointment_system.start_consultation(app.appointment_id)
            
            # Create a mock ConsultationLog directly to simulate the output of the AI pipeline
            log = ConsultationLog(
                patient_id=app.patient_id,
                doctor_id=doctor_id,
                started_at=app.scheduled_at,
                extracted_symptoms=["headache", "fever"] if "fever" in app.symptoms_description else ["chest pain"] if "chest" in app.symptoms_description else ["pain"],
                extracted_medications=["paracetamol"] if "fever" in app.symptoms_description else ["aspirin"] if "chest" in app.symptoms_description else ["ibuprofen"],
                extracted_dosages={"paracetamol": "500mg"} if "fever" in app.symptoms_description else {"aspirin": "75mg"} if "chest" in app.symptoms_description else {"ibuprofen": "400mg"},
                estimated_duration_minutes=15,
                notes="Patient advised to rest.",
                appointment_id=app.appointment_id,
                ended_at=app.scheduled_at + timedelta(minutes=15),
                raw_transcript="Patient reports symptoms... I am prescribing medication.",
                diagnosis="Common flu" if "fever" in app.symptoms_description else "Angina" if "chest" in app.symptoms_description else "General pain",
                prescription_text="Take medication as prescribed.",
                priority_level=app.priority_level,
                consultation_summary="Patient presented with symptoms. Diagnosed and prescribed medication."
            )
            await patient_repo.create_consultation_log(log)
            
            await appointment_system.complete_consultation(app.appointment_id, log.consultation_id)
            print(f"Simulated completed consultation for {app.appointment_id}")
        except Exception as e:
            print(f"Error simulating consultation for {app.appointment_id}: {e}")

    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_data())
