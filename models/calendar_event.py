from datetime import date, datetime

from sqlalchemy import String, Date, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_type: Mapped[str] = mapped_column(
        Enum(
            "meeting",
            "public_holiday",
            "company_holiday",
            "leave",
            "overtime",
            "attendance",
            name="calendar_event_type",
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    location: Mapped[str] = mapped_column(String(255), nullable=True, default=None)
    attendees: Mapped[str] = mapped_column(String(500), nullable=True, default=None)
    is_imported: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id"), nullable=True, default=None
    )
