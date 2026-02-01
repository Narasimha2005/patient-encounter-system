from sqlalchemy.orm import Session

from src.models.models import Patient
from src.services.utils import ensure_utc


def create_patient(db: Session, data):
    patient = Patient(**data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)

    patient.created_at = ensure_utc(patient.created_at)
    patient.updated_at = ensure_utc(patient.updated_at)

    return patient


def get_patient(db: Session, patient_id: int):
    return db.get(Patient, patient_id)
