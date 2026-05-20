from datetime import date, time

from sqlalchemy import String, Date, Time, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    record_date: Mapped[date] = mapped_column(Date, nullable=False)
    clock_in: Mapped[time] = mapped_column(Time, nullable=True)
    clock_out: Mapped[time] = mapped_column(Time, nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(
            "present",
            "late",
            "early_absent",
            "absent",
            name="attendance_status",
        ),
        nullable=False,
        default="absent",
    )
    notes: Mapped[str] = mapped_column(String(500), nullable=True, default=None)

    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="attendance_records")
