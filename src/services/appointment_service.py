from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.models import Appointment, Doctor, Patient
from src.services.utils import ensure_utc


def create_appointment(db: Session, data):
    """
    Create a medical appointment while enforcing domain rules:
    - Appointment must be in the future
    - Doctor must be active
    - Patient must exist
    - No overlapping appointments for the same doctor
    """

    # 1️⃣ Appointment must be scheduled in the future
    if data.appointment_start_datetime <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400,
            detail="Appointment must be in the future",
        )

    # 2️⃣ Doctor must exist and be active
    doctor = db.get(Doctor, data.doctor_id)
    if not doctor or not doctor.active_status:
        raise HTTPException(
            status_code=400,
            detail="Doctor unavailable",
        )

    # 3️⃣ Patient must exist
    patient = db.get(Patient, data.patient_id)
    if not patient:
        raise HTTPException(
            status_code=400,
            detail="Patient not found",
        )

    # 4️⃣ Calculate new appointment start time and end time
    appointment_start_time = data.appointment_start_datetime
    appointment_duration_minutes = data.appointment_duration
    appointment_end_time = (
        appointment_start_time
        + timedelta(minutes=appointment_duration_minutes)
    )

    # 5️⃣ Fetch existing appointments for the doctor
    existing_appointments = (
        db.execute(
            select(Appointment).where(
                Appointment.doctor_id == data.doctor_id
            )
        )
        .scalars()
        .all()
    )

    # 6️⃣ Check for overlapping appointments using start time and duration
    for existing_appointment in existing_appointments:
        existing_start_time = ensure_utc(
            existing_appointment.appointment_start_datetime
        )
        existing_duration_minutes = existing_appointment.appointment_duration
        existing_end_time = (
            existing_start_time
            + timedelta(minutes=existing_duration_minutes)
        )

        # Overlap condition:
        # Two appointments overlap if their time windows intersect
        if not (
            appointment_end_time <= existing_start_time
            or appointment_start_time >= existing_end_time
        ):
            raise HTTPException(
                status_code=409,
                detail="Appointment conflict",
            )

    # 7️⃣ Persist appointment
    appointment = Appointment(**data.model_dump())
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    # 8️⃣ Normalize datetime fields to UTC (SQLite safety)
    appointment.created_at = ensure_utc(appointment.created_at)
    appointment.appointment_start_datetime = ensure_utc(
        appointment.appointment_start_datetime
    )

    return appointment


def list_appointments(db: Session, date, doctor_id=None):
    """
    Retrieve appointments for a given date.
    Optionally filter by doctor.
    """

    start_of_day = datetime.combine(
        date, datetime.min.time(), tzinfo=timezone.utc
    )
    end_of_day = datetime.combine(
        date, datetime.max.time(), tzinfo=timezone.utc
    )

    stmt = select(Appointment).where(
        Appointment.appointment_start_datetime.between(
            start_of_day, end_of_day
        )
    )

    if doctor_id is not None:
        stmt = stmt.where(Appointment.doctor_id == doctor_id)

    return db.scalars(stmt).all()