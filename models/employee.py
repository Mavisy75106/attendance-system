from datetime import date

from sqlalchemy import String, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("active", "leave", "resigned", name="employee_status"),
        nullable=False,
        default="active",
    )
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
    leave_requests: Mapped[list["LeaveRequest"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan", foreign_keys="[LeaveRequest.employee_id]"
    )
    overtime_requests: Mapped[list["OvertimeRequest"]] = relationship(
        back_populates="employee", cascade="all, delete-orphan"
    )
