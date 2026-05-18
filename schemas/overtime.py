from datetime import date, time

from pydantic import BaseModel, Field


class OvertimeRequestBase(BaseModel):
    employee_id: int = Field(..., gt=0)
    date: date = Field(...)
    start_time: time = Field(...)
    end_time: time = Field(...)
    reason: str | None = Field(None, max_length=500)
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
    date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    reason: str | None = Field(None, max_length=500)
    status: str | None = Field(None, pattern="^(pending|approved|rejected)$")


class OvertimeRequestRead(BaseModel):
    """Schema for reading overtime request data."""
    id: int
    employee_id: int
    date: date
    start_time: time
    end_time: time
    reason: str | None
    hours: float
    status: str

    model_config = {
        "from_attributes": True,
    }
