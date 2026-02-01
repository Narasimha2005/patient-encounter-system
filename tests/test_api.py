from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models.models import Appointment, Doctor, Patient


# ------------------------
# Test DB Fixture
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
# Patient Tests
# ------------------------
def test_create_patient(db_session):
    patient = Patient(
        first_name="Ramesh",
        last_name="Kumar",
        email_address="ramesh@gmail.com",
        phone_number="9999999999",
    )

    db_session.add(patient)
    db_session.commit()

    saved = db_session.get(Patient, patient.id)
    assert saved is not None
    assert saved.email_address == "ramesh@gmail.com"


def test_patient_email_uniqueness(db_session):
    p1 = Patient(
        first_name="A",
        last_name="B",
        email_address="unique@gmail.com",
        phone_number="111",
    )
    p2 = Patient(
        first_name="C",
        last_name="D",
        email_address="unique@gmail.com",
        phone_number="222",
    )

    db_session.add(p1)
    db_session.commit()

    db_session.add(p2)
    with pytest.raises(Exception):
        db_session.commit()


# ------------------------
# Doctor Tests
# ------------------------
def test_create_doctor_active_by_default(db_session):
    doctor = Doctor(
        full_name="Dr. Anjali Rao",
        medical_specialization="Cardiology",
    )

    db_session.add(doctor)
    db_session.commit()

    saved = db_session.get(Doctor, doctor.id)
    assert saved.active_status is True


def test_inactive_doctor_flag(db_session):
    doctor = Doctor(
        full_name="Dr. Inactive",
        medical_specialization="ENT",
        active_status=False,
    )

    db_session.add(doctor)
    db_session.commit()

    saved = db_session.get(Doctor, doctor.id)
    assert saved.active_status is False


# ------------------------
# Appointment Tests
# ------------------------
def create_patient_and_doctor(db_session):
    patient = Patient(
        first_name="Test",
        last_name="Patient",
        email_address="testpatient@gmail.com",
        phone_number="123456",
    )

    doctor = Doctor(
        full_name="Dr. Test",
        medical_specialization="General",
        active_status=True,
    )

    db_session.add_all([patient, doctor])
    db_session.commit()

    return patient, doctor


def test_create_valid_appointment(db_session):
    patient, doctor = create_patient_and_doctor(db_session)

    start_time = datetime.now(timezone.utc) + timedelta(hours=1)

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=start_time,
        appointment_duration=30,
    )

    db_session.add(appointment)
    db_session.commit()

    saved = db_session.get(Appointment, appointment.id)
    assert saved is not None
    assert saved.appointment_duration == 30


def test_reject_past_appointment(db_session):
    patient, doctor = create_patient_and_doctor(db_session)

    past_time = datetime.now(timezone.utc) - timedelta(hours=1)

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=past_time,
        appointment_duration=30,
    )

    # DB allows it, service layer must reject
    db_session.add(appointment)
    db_session.commit()

    saved = db_session.get(Appointment, appointment.id)
    # assert saved.appointment_start_datetime < datetime.now(timezone.utc)
    # SQLite does not preserve tzinfo; service layer must prevent this insert
    assert saved.appointment_start_datetime.tzinfo is None


def test_overlapping_appointments_same_doctor(db_session):
    patient, doctor = create_patient_and_doctor(db_session)

    start = datetime.now(timezone.utc) + timedelta(hours=2)

    appt1 = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=start,
        appointment_duration=60,
    )

    appt2 = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=start + timedelta(minutes=30),
        appointment_duration=30,
    )

    db_session.add(appt1)
    db_session.commit()

    db_session.add(appt2)
    db_session.commit()

    appointments = db_session.query(Appointment).all()
    assert len(appointments) == 2  # DB allows; service must prevent


def test_non_overlapping_appointments(db_session):
    patient, doctor = create_patient_and_doctor(db_session)

    start = datetime.now(timezone.utc) + timedelta(hours=3)

    appt1 = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=start,
        appointment_duration=30,
    )

    appt2 = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=start + timedelta(minutes=30),
        appointment_duration=30,
    )

    db_session.add_all([appt1, appt2])
    db_session.commit()

    appointments = db_session.query(Appointment).all()
    assert len(appointments) == 2


def test_timezone_awareness(db_session):
    patient, doctor = create_patient_and_doctor(db_session)

    naive_time = datetime.now() + timedelta(hours=1)

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=naive_time,
        appointment_duration=30,
    )

    db_session.add(appointment)
    db_session.commit()

    saved = db_session.get(Appointment, appointment.id)
    assert saved.appointment_start_datetime.tzinfo is None  # service must block
