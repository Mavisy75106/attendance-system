from datetime import date

from pydantic import BaseModel, Field


class LeaveRequestBase(BaseModel):
    employee_id: int = Field(..., gt=0)
    leave_type: str = Field(..., pattern="^(annual|sick|personal|others)$")
    start_date: date = Field(...)
    end_date: date = Field(...)
    reason: str | None = Field(None, max_length=500)
    status: str = Field(default="pending", pattern="^(pending|approved|rejected)$")


class LeaveRequestCreate(LeaveRequestBase):
    """Schema for creating a new leave request."""

    def model_validator(self, mode="before") -> "LeaveRequestCreate":
        """Validate that end_date is not before start_date."""
        if isinstance(self, dict):
            start = self.get("start_date")
            end = self.get("end_date")
        else:
            start = self.start_date
            end = self.end_date
        if start and end and end < start:
            raise ValueError("end_date must not be before start_date")
        return self


class LeaveRequestUpdate(BaseModel):
    """Schema for updating an existing leave request. All fields optional."""
    leave_type: str | None = Field(None, pattern="^(annual|sick|personal|others)$")
    start_date: date | None = None
    end_date: date | None = None
    reason: str | None = Field(None, max_length=500)
    status: str | None = Field(None, pattern="^(pending|approved|rejected)$")
    approved_by: int | None = None


class LeaveRequestRead(BaseModel):
    """Schema for reading leave request data."""
    id: int
    employee_id: int
    leave_type: str
    start_date: date
    end_date: date
    reason: str | None
    status: str
    approved_by: int | None

    model_config = {
        "from_attributes": True,
    }
