from datetime import datetime

from pydantic import BaseModel, field_validator


class DoctorCreate(BaseModel):
    full_name: str
    medical_specialization: str
    active_status: bool = True


class DoctorRead(BaseModel):
    id: int
    full_name: str
    medical_specialization: str
    active_status: bool
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("Datetime must be timezone-aware")
        return value
