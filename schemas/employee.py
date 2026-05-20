from datetime import date

from pydantic import BaseModel, EmailStr, Field


class EmployeeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    employee_id: str = Field(..., min_length=1, max_length=50)
    department: str = Field(..., min_length=1, max_length=100)
    position: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = Field(...)
    phone: str | None = Field(None, max_length=30)
    status: str = Field(default="active", pattern="^(active|leave|resigned)$")
    hire_date: date = Field(...)


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""


class EmployeeUpdate(BaseModel):
    """Schema for updating an existing employee. All fields optional."""
    name: str | None = Field(None, min_length=1, max_length=150)
    employee_id: str | None = Field(None, min_length=1, max_length=50)
    department: str | None = Field(None, min_length=1, max_length=100)
    position: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=30)
    status: str | None = Field(None, pattern="^(active|leave|resigned)$")
    hire_date: date | None = None


class EmployeeRead(BaseModel):
    """Schema for reading employee data."""
    id: int
    name: str
    employee_id: str
    department: str
    position: str
    email: str
    phone: str | None
    status: str
    hire_date: date

    model_config = {
        "from_attributes": True,
    }


class EmployeeList(BaseModel):
    """Schema for listing employees with pagination."""
    total: int
    items: list[EmployeeRead]

    model_config = {
        "from_attributes": True,
    }
