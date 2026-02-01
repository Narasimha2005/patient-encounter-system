from sqlalchemy.orm import Session

from src.models.models import Doctor
from src.services.utils import ensure_utc


def create_doctor(db: Session, data):
    doctor = Doctor(**data.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    doctor.created_at = ensure_utc(doctor.created_at)

    return doctor


def get_doctor(db: Session, doctor_id: int):
    return db.get(Doctor, doctor_id)
