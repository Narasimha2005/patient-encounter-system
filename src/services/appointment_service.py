from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.models import Appointment, Doctor, Patient
from src.services.utils import ensure_utc


def create_appointment(db: Session, data):
    # 1. Future check
    if data.appointment_start_datetime <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Appointment must be in the future")

    # 2. Doctor validation
    doctor = db.get(Doctor, data.doctor_id)
    if not doctor or not doctor.active_status:
        raise HTTPException(status_code=400, detail="Doctor unavailable")

    # 3. Patient validation
    if not db.get(Patient, data.patient_id):
        raise HTTPException(status_code=400, detail="Patient not found")

    new_start = data.appointment_start_datetime
    new_end = new_start + timedelta(minutes=data.appointment_duration)

    # 4. Conflict detection (DB-agnostic)
    existing_appointments = (
        db.execute(select(Appointment).where(Appointment.doctor_id == data.doctor_id))
        .scalars()
        .all()
    )

    for appt in existing_appointments:
        existing_start = ensure_utc(appt.appointment_start_datetime)
        existing_end = existing_start + timedelta(minutes=appt.appointment_duration)

        if new_start < existing_end and new_end > existing_start:
            raise HTTPException(
                status_code=409,
                detail="Appointment conflict",
            )

    # 5. Create appointment
    appt = Appointment(**data.model_dump())
    db.add(appt)
    db.commit()
    db.refresh(appt)

    # 6. Normalize datetimes for SQLite
    appt.created_at = ensure_utc(appt.created_at)
    appt.appointment_start_datetime = ensure_utc(appt.appointment_start_datetime)

    return appt


def list_appointments(db: Session, date, doctor_id=None):
    start = datetime.combine(date, datetime.min.time(), tzinfo=timezone.utc)
    end = datetime.combine(date, datetime.max.time(), tzinfo=timezone.utc)

    stmt = select(Appointment).where(
        Appointment.appointment_start_datetime.between(start, end)
    )

    if doctor_id:
        stmt = stmt.where(Appointment.doctor_id == doctor_id)

    return db.scalars(stmt).all()
