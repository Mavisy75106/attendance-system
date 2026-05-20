from datetime import date as date_type, time as time_type
from typing import Optional

from pydantic import BaseModel, Field


class AttendanceRecordBase(BaseModel):
    employee_id: int = Field(..., gt=0)
    record_date: date_type = Field(...)
    clock_in: Optional[time_type] = None
    clock_out: Optional[time_type] = None
    status: str = Field(default="absent", pattern="^(present|late|early_absent|absent)$")
    notes: Optional[str] = Field(None, max_length=500)


class AttendanceRecordCreate(AttendanceRecordBase):
    """Schema for creating a new attendance record."""


class AttendanceRecordUpdate(BaseModel):
    """Schema for updating an existing attendance record. All fields optional."""
    clock_in: Optional[time_type] = None
    clock_out: Optional[time_type] = None
    status: Optional[str] = Field(None, pattern="^(present|late|early_absent|absent)$")
    notes: Optional[str] = Field(None, max_length=500)


class AttendanceRecordRead(BaseModel):
    """Schema for reading attendance record data."""
    id: int
    employee_id: int
    record_date: date_type
    clock_in: Optional[time_type] = None
    clock_out: Optional[time_type] = None
    status: str
    notes: Optional[str] = None

    model_config = {
        "from_attributes": True,
    }
