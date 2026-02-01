from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    email_address: EmailStr
    phone_number: str


class PatientRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email_address: EmailStr
    phone_number: str
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at")
    @classmethod
    def must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("Datetime must be timezone-aware")
        return value

    class Config:
        from_attributes = True
