from datetime import date, time

from pydantic import BaseModel, Field


class AttendanceRecordBase(BaseModel):
    employee_id: int = Field(..., gt=0)
    date: date = Field(...)
    clock_in: time | None = None
    clock_out: time | None = None
    status: str = Field(default="absent", pattern="^(present|late|early_absent|absent)$")
    notes: str | None = Field(None, max_length=500)


class AttendanceRecordCreate(AttendanceRecordBase):
    """Schema for creating a new attendance record."""


class AttendanceRecordUpdate(BaseModel):
    """Schema for updating an existing attendance record. All fields optional."""
    clock_in: time | None = None
    clock_out: time | None = None
    status: str | None = Field(None, pattern="^(present|late|early_absent|absent)$")
    notes: str | None = Field(None, max_length=500)


class AttendanceRecordRead(BaseModel):
    """Schema for reading attendance record data."""
    id: int
    employee_id: int
    date: date
    clock_in: time | None
    clock_out: time | None
    status: str
    notes: str | None

    model_config = {
        "from_attributes": True,
    }
