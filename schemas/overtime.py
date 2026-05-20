from datetime import date as date_type, time as time_type
from typing import Optional

from pydantic import BaseModel, Field


class OvertimeRequestBase(BaseModel):
    employee_id: int = Field(..., gt=0)
    overtime_date: date_type = Field(...)
    start_time: time_type = Field(...)
    end_time: time_type = Field(...)
    reason: Optional[str] = Field(None, max_length=500)
    status: str = Field(default="pending", pattern="^(pending|approved|rejected)$")

    def model_validator(self, mode="before") -> "OvertimeRequestBase":
        """Validate that end_time is after start_time."""
        if isinstance(self, dict):
            start = self.get("start_time")
            end = self.get("end_time")
        else:
            start = self.start_time
            end = self.end_time
        if start and end:
            start_seconds = start.hour * 3600 + start.minute * 60 + start.second
            end_seconds = end.hour * 3600 + end.minute * 60 + end.second
            if end_seconds <= start_seconds:
                raise ValueError("end_time must be after start_time")
        return self


class OvertimeRequestCreate(OvertimeRequestBase):
    """Schema for creating a new overtime request."""


class OvertimeRequestUpdate(BaseModel):
    """Schema for updating an existing overtime request. All fields optional."""
    overtime_date: date_type | None = None
    start_time: time_type | None = None
    end_time: time_type | None = None
    reason: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(pending|approved|rejected)$")


class OvertimeRequestRead(BaseModel):
    """Schema for reading overtime request data."""
    id: int
    employee_id: int
    overtime_date: date_type
    start_time: time_type
    end_time: time_type
    reason: Optional[str] = None
    hours: float
    status: str

    model_config = {
        "from_attributes": True,
    }
