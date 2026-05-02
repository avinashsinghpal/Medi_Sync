import typing
from datetime import datetime, timezone, date
from motor.motor_asyncio import AsyncIOMotorDatabase
from medisync.core.types import PatientProfile, MedicalRecord, ConsultationLog

class PatientRepository:
    """Raw DB operations for Patient domain models."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.patients = db["patients"]
        self.medical_records = db["medical_records"]
        self.consultation_logs = db["consultation_logs"]

    async def setup_indexes(self):
        # Patient indexes
        await self.patients.create_index("patient_id", unique=True)
        await self.patients.create_index("contact_email", unique=True)
        await self.patients.create_index(
            [("full_name", "text"), ("contact_email", "text"), ("patient_id", "text")],
            name="patient_text_search"
        )
        # MedicalRecord indexes
        await self.medical_records.create_index("record_id", unique=True)
        await self.medical_records.create_index("patient_id")
        await self.medical_records.create_index([("recorded_at", -1)])
        # ConsultationLog indexes
        await self.consultation_logs.create_index("consultation_id", unique=True)
        await self.consultation_logs.create_index("patient_id")
        await self.consultation_logs.create_index([("started_at", -1)])

    async def create_patient(self, patient: PatientProfile) -> None:
        doc = self._to_dict(patient)
        await self.patients.insert_one(doc)

    async def get_patient_by_id(self, patient_id: str) -> typing.Optional[PatientProfile]:
        doc = await self.patients.find_one({"patient_id": patient_id})
        return self._from_dict(PatientProfile, doc) if doc else None

    async def get_patient_by_email(self, email: str) -> typing.Optional[PatientProfile]:
        doc = await self.patients.find_one({"contact_email": {"$regex": f"^{email}$", "$options": "i"}})
        return self._from_dict(PatientProfile, doc) if doc else None

    async def update_patient(self, patient: PatientProfile) -> None:
        doc = self._to_dict(patient)
        await self.patients.replace_one({"patient_id": patient.patient_id}, doc)

    async def search_patients(self, query: str, limit: int) -> list[PatientProfile]:
        cursor = self.patients.find({"$text": {"$search": query}})
        cursor.sort([("score", {"$meta": "textScore"})])
        cursor.limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._from_dict(PatientProfile, doc) for doc in docs]

    async def create_medical_record(self, record: MedicalRecord) -> None:
        doc = self._to_dict(record)
        await self.medical_records.insert_one(doc)

    async def get_medical_records(self, patient_id: str, limit: int, offset: int = 0) -> list[MedicalRecord]:
        cursor = self.medical_records.find({"patient_id": patient_id})
        cursor.sort("recorded_at", -1)
        cursor.skip(offset)
        cursor.limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._from_dict(MedicalRecord, doc) for doc in docs]

    async def create_consultation_log(self, log: ConsultationLog) -> None:
        doc = self._to_dict(log)
        await self.consultation_logs.insert_one(doc)

    async def get_consultation_logs(self, patient_id: str, limit: int) -> list[ConsultationLog]:
        cursor = self.consultation_logs.find({"patient_id": patient_id})
        cursor.sort("started_at", -1)
        cursor.limit(limit)
        docs = await cursor.to_list(length=limit)
        return [self._from_dict(ConsultationLog, doc) for doc in docs]

    def _to_dict(self, obj: typing.Any) -> dict:
        import dataclasses
        if dataclasses.is_dataclass(obj):
            doc = dataclasses.asdict(obj)
            # Motor handles datetimes. For 'date' objects in date_of_birth we convert to datetime.
            for k, v in doc.items():
                if isinstance(v, date) and not isinstance(v, datetime):
                    doc[k] = datetime(v.year, v.month, v.day)
            return doc
        return obj

    def _from_dict(self, cls: typing.Type, doc: dict) -> typing.Any:
        import dataclasses
        if not doc:
            return None
        doc.pop("_id", None)
        fields = {f.name for f in dataclasses.fields(cls)}
        filtered_doc = {k: v for k, v in doc.items() if k in fields}
        
        # Convert datetime back to date for date_of_birth
        if 'date_of_birth' in filtered_doc and isinstance(filtered_doc['date_of_birth'], datetime):
            filtered_doc['date_of_birth'] = filtered_doc['date_of_birth'].date()
            
        return cls(**filtered_doc)
