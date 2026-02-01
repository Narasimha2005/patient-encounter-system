from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class AppointmentCreate(BaseModel):
    patient_id: int = Field(..., gt=0)
    doctor_id: int = Field(..., gt=0)
    appointment_start_datetime: datetime
    appointment_duration: int = Field(
        ...,
        ge=15,
        le=180,
        description="Duration must be between 15 and 180 minutes",
    )

    @field_validator("appointment_start_datetime")
    @classmethod
    def must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("Datetime must be timezone-aware")
        return value


class AppointmentRead(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_start_datetime: datetime
    appointment_duration: int
    created_at: datetime

    @field_validator("appointment_start_datetime", "created_at")
    @classmethod
    def must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("Datetime must be timezone-aware")
        return value

    class Config:
        from_attributes = True
