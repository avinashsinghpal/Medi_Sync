import typing
from datetime import datetime, date, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from medisync.core.types import Appointment, AppointmentStatus

class AppointmentRepository:
    """Raw DB operations for Appointment domain models."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.appointments = db["appointments"]

    async def setup_indexes(self):
        await self.appointments.create_index("appointment_id", unique=True)
        await self.appointments.create_index("patient_id")
        await self.appointments.create_index(
            [("doctor_id", 1), ("scheduled_at", 1)],
            name="doctor_schedule_index"
        )
        await self.appointments.create_index("status")

    async def create(self, appointment: Appointment) -> None:
        doc = self._to_dict(appointment)
        await self.appointments.insert_one(doc)

    async def get_by_id(self, appointment_id: str) -> typing.Optional[Appointment]:
        doc = await self.appointments.find_one({"appointment_id": appointment_id})
        return self._from_dict(Appointment, doc) if doc else None

    async def get_by_patient_id(self, patient_id: str, status_filter: typing.Optional[AppointmentStatus] = None) -> list[Appointment]:
        query = {"patient_id": patient_id}
        if status_filter:
            query["status"] = status_filter
        
        cursor = self.appointments.find(query)
        cursor.sort("scheduled_at", 1)
        docs = await cursor.to_list(length=1000)
        return [self._from_dict(Appointment, doc) for doc in docs]

    async def get_by_doctor_and_date(self, doctor_id: str, target_date: date) -> list[Appointment]:
        start_of_day = datetime(target_date.year, target_date.month, target_date.day, tzinfo=timezone.utc)
        end_of_day = start_of_day + timedelta(days=1)
        
        query = {
            "doctor_id": doctor_id,
            "scheduled_at": {"$gte": start_of_day, "$lt": end_of_day},
            "status": {"$in": [AppointmentStatus.CONFIRMED, AppointmentStatus.IN_SESSION]}
        }
        
        cursor = self.appointments.find(query)
        # Sort by priority and then time will be done in the service layer 
        # or we could do it here if we use aggregation, but doing it in memory is fine for small queues.
        # Let's do a basic sort by time here.
        cursor.sort("scheduled_at", 1)
        docs = await cursor.to_list(length=1000)
        return [self._from_dict(Appointment, doc) for doc in docs]

    async def update(self, appointment: Appointment) -> None:
        doc = self._to_dict(appointment)
        await self.appointments.replace_one({"appointment_id": appointment.appointment_id}, doc)

    async def get_overlapping(self, doctor_id: str, start_time: datetime, end_time: datetime) -> list[Appointment]:
        """
        Get appointments that overlap with [start_time, end_time].
        An appointment overlaps if:
        scheduled_at < end_time AND (scheduled_at + estimated_duration) > start_time.
        We'll do a basic query to fetch potential overlapping ones and filter in memory, 
        or we can write a more complex query.
        For simplicity, fetch appointments scheduled around that time.
        """
        search_start = start_time - timedelta(hours=4)
        search_end = end_time
        
        query = {
            "doctor_id": doctor_id,
            "scheduled_at": {"$gte": search_start, "$lt": search_end},
            "status": {"$in": [AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED, AppointmentStatus.IN_SESSION]}
        }
        
        cursor = self.appointments.find(query)
        docs = await cursor.to_list(length=100)
        
        overlapping = []
        for doc in docs:
            app = self._from_dict(Appointment, doc)
            app_start = app.scheduled_at
            app_end = app_start + timedelta(minutes=app.estimated_duration_minutes)
            if app_start < end_time and app_end > start_time:
                overlapping.append(app)
                
        return overlapping

    def _to_dict(self, obj: typing.Any) -> dict:
        import dataclasses
        if dataclasses.is_dataclass(obj):
            doc = dataclasses.asdict(obj)
            return doc
        return obj

    def _from_dict(self, cls: typing.Type, doc: dict) -> typing.Any:
        import dataclasses
        if not doc:
            return None
        doc.pop("_id", None)
        fields = {f.name for f in dataclasses.fields(cls)}
        filtered_doc = {k: v for k, v in doc.items() if k in fields}
        return cls(**filtered_doc)
