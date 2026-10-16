from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

AppointmentStatus = Literal["SCHEDULED", "CHECKED_IN", "COMPLETED", "CANCELLED", "NO_SHOW"]


# ---------- Doctors ----------
class DoctorCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    specialty: str = Field(min_length=2, max_length=80)
    room: str = Field(default="", max_length=20)
    active: bool = True


class DoctorUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    specialty: str | None = Field(default=None, min_length=2, max_length=80)
    room: str | None = Field(default=None, max_length=20)
    active: bool | None = None


class DoctorOut(DoctorCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Patients ----------
class PatientCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(default="", max_length=30)
    date_of_birth: date | None = None


class PatientUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    date_of_birth: date | None = None


class PatientOut(PatientCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Appointments ----------
class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    scheduled_at: datetime
    duration_minutes: int = Field(default=30, ge=10, le=240)
    reason: str = Field(min_length=2, max_length=200)
    notes: str = ""


class AppointmentUpdate(BaseModel):
    scheduled_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, ge=10, le=240)
    reason: str | None = Field(default=None, min_length=2, max_length=200)
    status: AppointmentStatus | None = None
    notes: str | None = None


class AppointmentOut(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    patient_name: str
    doctor_name: str
    specialty: str
    scheduled_at: datetime
    duration_minutes: int
    reason: str
    status: AppointmentStatus
    notes: str
    created_at: datetime
    updated_at: datetime


class DoctorLoad(BaseModel):
    doctor_id: int
    doctor_name: str
    specialty: str
    upcoming: int


class AppointmentStats(BaseModel):
    total: int
    today: int
    scheduled: int
    checked_in: int
    completed: int
    cancelled: int
    no_show: int
    patients: int
    active_doctors: int
    doctor_load: list[DoctorLoad]
