from datetime import date, time, timedelta

from sqlalchemy import String, Date, Time, ForeignKey, Enum, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def _calculate_hours(start: time, end: time) -> float:
    """Calculate hours between two time values."""
    start_dt = timedelta(hours=start.hour, minutes=start.minute, seconds=start.second)
    end_dt = timedelta(hours=end.hour, minutes=end.minute, seconds=end.second)
    diff = (end_dt - start_dt).total_seconds() / 3600
    return round(max(diff, 0), 2)


class OvertimeRequest(Base):
    __tablename__ = "overtime_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), nullable=False
    )
    overtime_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=True, default=None)
    hours: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("pending", "approved", "rejected", name="overtime_status"),
        nullable=False,
        default="pending",
    )

    # Relationships
    employee: Mapped["Employee"] = relationship(
        back_populates="overtime_requests"
    )

    # Auto-calculate hours before insert/update
    @staticmethod
    def calculate_hours(start: time, end: time) -> float:
        return _calculate_hours(start, end)
