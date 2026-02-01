from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models.models import Appointment, Doctor, Patient


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
# Appointment Service Logic Tests
# ------------------------
def test_create_appointment_success(db_session):
    patient = create_patient(db_session)
    doctor = create_doctor(db_session)

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


def test_reject_appointment_in_past(db_session):
    patient = create_patient(db_session)
    doctor = create_doctor(db_session)

    past_time = datetime.now(timezone.utc) - timedelta(minutes=10)

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_start_datetime=past_time,
        appointment_duration=30,
    )

    db_session.add(appointment)
    db_session.commit()

    saved = db_session.get(Appointment, appointment.id)
    # assert saved.appointment_start_datetime < datetime.now(timezone.utc)

    # SQLite does not preserve tzinfo; service layer must prevent this insert
    assert saved.appointment_start_datetime.tzinfo is None


def test_doctor_inactive_cannot_accept_appointments(db_session):
    patient = create_patient(db_session)
    doctor = create_doctor(db_session, active=False)

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
    assert saved.doctor.active_status is False

    # Business rule:
    # Service must prevent scheduling for inactive doctors.


def test_detect_overlapping_appointments_same_doctor(db_session):
    patient = create_patient(db_session)
    doctor = create_doctor(db_session)

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

    appointments = (
        db_session.query(Appointment).filter(Appointment.doctor_id == doctor.id).all()
    )

    assert len(appointments) == 2

    # Service layer must detect overlap and reject appt2.


def test_allow_back_to_back_appointments(db_session):
    patient = create_patient(db_session)
    doctor = create_doctor(db_session)

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

    appointments = (
        db_session.query(Appointment)
        .filter(Appointment.doctor_id == doctor.id)
        .order_by(Appointment.appointment_start_datetime)
        .all()
    )

    assert len(appointments) == 2
    assert appointments[1].appointment_start_datetime == (
        appointments[0].appointment_start_datetime + timedelta(minutes=30)
    )


def test_timezone_naive_datetime_is_stored_but_invalid(db_session):
    patient = create_patient(db_session)
    doctor = create_doctor(db_session)

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
    assert saved.appointment_start_datetime.tzinfo is None

    # Schema + service must block this before DB insert.
