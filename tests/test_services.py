from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models.models import Doctor, Patient
from src.schemas.appointment import AppointmentCreate
from src.services.appointment_service import create_appointment


# ------------------------
# DB Fixture
# ------------------------
@pytest.fixture(scope="function")
def db_session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)

    SessionLocalTest = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocalTest()

    yield db

    db.close()


# ------------------------
# Helpers
# ------------------------
def create_patient(db):
    patient = Patient(
        first_name="Test",
        last_name="Patient",
        email_address="patient@test.com",
        phone_number="9999999999",
    )
    db.add(patient)
    db.commit()
    return patient


def create_doctor(db, active=True):
    doctor = Doctor(
        full_name="Dr. Test",
        medical_specialization="General",
        active_status=active,
    )
    db.add(doctor)
    db.commit()
    return doctor


# ------------------------
# Appointment Service Tests
# ------------------------
def test_service_creates_valid_appointment(db_session):
    patient = create_patient(db_session)
    doctor = create_doctor(db_session)

    data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=datetime.now(timezone.utc) + timedelta(hours=1),
        appointment_duration=30,
    )

    appointment = create_appointment(db_session, data)

    assert appointment.id is not None
    assert appointment.appointment_duration == 30


def test_service_rejects_past_appointment(db_session):
    patient = create_patient(db_session)
    doctor = create_doctor(db_session)

    data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=datetime.now(timezone.utc) - timedelta(minutes=10),
        appointment_duration=30,
    )

    with pytest.raises(HTTPException) as exc:
        create_appointment(db_session, data)

    assert exc.value.status_code == 400


def test_service_rejects_inactive_doctor(db_session):
    patient = create_patient(db_session)
    doctor = create_doctor(db_session, active=False)

    data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=datetime.now(timezone.utc) + timedelta(hours=1),
        appointment_duration=30,
    )

    with pytest.raises(HTTPException) as exc:
        create_appointment(db_session, data)

    assert exc.value.status_code == 400


def test_service_detects_overlapping_appointments(db_session):
    patient = create_patient(db_session)
    doctor = create_doctor(db_session)

    start_time = datetime.now(timezone.utc) + timedelta(hours=2)

    create_appointment(
        db_session,
        AppointmentCreate(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_start_datetime=start_time,
            appointment_duration=60,
        ),
    )

    overlapping = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=start_time + timedelta(minutes=30),
        appointment_duration=30,
    )

    with pytest.raises(HTTPException) as exc:
        create_appointment(db_session, overlapping)

    assert exc.value.status_code == 409


def test_service_allows_back_to_back_appointments(db_session):
    patient = create_patient(db_session)
    doctor = create_doctor(db_session)

    start_time = datetime.now(timezone.utc) + timedelta(hours=3)

    create_appointment(
        db_session,
        AppointmentCreate(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_start_datetime=start_time,
            appointment_duration=30,
        ),
    )

    second = create_appointment(
        db_session,
        AppointmentCreate(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_start_datetime=start_time + timedelta(minutes=30),
            appointment_duration=30,
        ),
    )

    assert second is not None
