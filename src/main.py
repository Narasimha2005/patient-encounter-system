from datetime import date

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.schemas.appointment import (
    AppointmentCreate,
    AppointmentRead,
)
from src.schemas.doctor import (
    DoctorCreate,
    DoctorRead,
)
from src.schemas.patient import (
    PatientCreate,
    PatientRead,
)
from src.services import appointment_service, doctor_service, patient_service

app = FastAPI(
    title="Patient Encounter System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/patients", response_model=PatientRead, status_code=201)
def create_patient(data: PatientCreate, db: Session = Depends(get_db)):
    return patient_service.create_patient(db, data)


@app.get("/patients/{patient_id}", response_model=PatientRead)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    p = patient_service.get_patient(db, patient_id)
    if not p:
        raise HTTPException(404)
    return p


@app.post("/doctors", response_model=DoctorRead, status_code=201)
def create_doctor(data: DoctorCreate, db: Session = Depends(get_db)):
    return doctor_service.create_doctor(db, data)


@app.get("/doctors/{doctor_id}", response_model=DoctorRead)
def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    d = doctor_service.get_doctor(db, doctor_id)
    if not d:
        raise HTTPException(404)
    return d


@app.post("/appointments", response_model=AppointmentRead, status_code=201)
def create_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    return appointment_service.create_appointment(db, data)


@app.get("/appointments")
def list_appointments(
    date: date,
    doctor_id: int | None = None,
    db: Session = Depends(get_db),
):
    return appointment_service.list_appointments(db, date, doctor_id)
