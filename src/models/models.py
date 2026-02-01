from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.database import Base


class Patient(Base):
    """
    Represents a patient in the clinic.
    """

    __tablename__ = "narasimha_patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Must be unique and indexed (read-heavy)
    email_address: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )

    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # NO cascade delete (domain rule: patients with appointments must not be deleted)
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="patient",
        passive_deletes=True,
    )


class Doctor(Base):
    """
    Represents a doctor in the clinic.
    """

    __tablename__ = "narasimha_doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    medical_specialization: Mapped[str] = mapped_column(String(100), nullable=False)

    # Doctors are active by default
    active_status: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment",
        back_populates="doctor",
        passive_deletes=True,
    )


class Appointment(Base):
    """
    Represents a scheduled medical encounter.
    """

    __tablename__ = "narasimha_appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("narasimha_patients.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("narasimha_doctors.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Must be timezone-aware
    appointment_start_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )

    # Duration in minutes (15–180 enforced in service layer)
    appointment_duration: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="appointments")
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments")


# Composite index for fast conflict detection & schedule queries
Index(
    "idx_doctor_start_time",
    Appointment.doctor_id,
    Appointment.appointment_start_datetime,
)
