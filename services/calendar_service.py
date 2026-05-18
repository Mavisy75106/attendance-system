"""Calendar service: Calendar events and public holidays management."""

from datetime import date, datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from attendance_system.models.calendar_event import CalendarEvent
from attendance_system.schemas.calendar_event import (
    CalendarEventCreate,
    CalendarEventRead,
)


def add_calendar_event(db: Session, event_data: CalendarEventCreate) -> CalendarEventRead:
    """Add a new calendar event."""
    calendar_event = CalendarEvent(
        event_date=event_data.event_date,
        event_type=event_data.event_type,
        title=event_data.title,
        description=event_data.description,
        location=event_data.location,
        attendees=event_data.attendees,
    )

    db.add(calendar_event)
    db.commit()
    db.refresh(calendar_event)

    return CalendarEventRead.model_validate(calendar_event)


def get_events_by_date(
    db: Session, event_date: date
) -> list[CalendarEventRead]:
    """Get all calendar events for a specific date."""
    events = (
        db.query(CalendarEvent)
        .filter(CalendarEvent.event_date == event_date)
        .order_by(CalendarEvent.created_at.desc())
        .all()
    )
    return [CalendarEventRead.model_validate(ev) for ev in events]


def get_events_by_month(
    db: Session, year: int, month: int
) -> list[CalendarEventRead]:
    """Get all calendar events for a specific month."""
    # Calculate month boundaries
    from datetime import timedelta
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year, 12, 31)
    else:
        next_month_start = date(year, month + 1, 1)
        end_date = next_month_start - timedelta(days=1)

    events = (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.event_date >= start_date,
            CalendarEvent.event_date <= end_date,
        )
        .order_by(CalendarEvent.event_date, CalendarEvent.created_at.desc())
        .all()
    )
    return [CalendarEventRead.model_validate(ev) for ev in events]


def get_public_holidays(db: Session, year: int) -> list[CalendarEventRead]:
    """Get all public holidays for a specific year."""
    events = (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.event_date >= date(year, 1, 1),
            CalendarEvent.event_date <= date(year, 12, 31),
            CalendarEvent.event_type == "public_holiday",
        )
        .order_by(CalendarEvent.event_date)
        .all()
    )
    return [CalendarEventRead.model_validate(ev) for ev in events]


def get_all_holidays_for_month(
    db: Session, year: int, month: int
) -> list[CalendarEventRead]:
    """Get all holidays (public + company) for a specific month."""
    from datetime import timedelta

    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year, 12, 31)
    else:
        next_month_start = date(year, month + 1, 1)
        end_date = next_month_start - timedelta(days=1)

    events = (
        db.query(CalendarEvent)
        .filter(
            CalendarEvent.event_date >= start_date,
            CalendarEvent.event_date <= end_date,
            CalendarEvent.event_type.in_(["public_holiday", "company_holiday"]),
        )
        .order_by(CalendarEvent.event_date)
        .all()
    )
    return [CalendarEventRead.model_validate(ev) for ev in events]


def delete_calendar_event(db: Session, event_id: int) -> dict:
    """Delete a calendar event."""
    event = db.query(CalendarEvent).filter(
        CalendarEvent.id == event_id
    ).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calendar event with ID {event_id} not found",
        )

    db.delete(event)
    db.commit()

    return {"message": f"Calendar event '{event.title}' deleted", "deleted_id": event_id}


def import_holiday(db: Session, year: int) -> dict:
    """Import public holidays for a given year (Taiwan)."""
    # Simplified list of Taiwan public holidays
    holidays = {
        # 2026
        2026: [
            (1, 1, "元旦"),
            (2, 17, "春節假期"),
            (2, 18, "春節假期"),
            (2, 19, "春節假期"),
            (2, 20, "春節假期"),
            (2, 21, "春節假期"),
            (2, 27, "和平紀念日"),
            (4, 4, "兒童節"),
            (4, 5, "清明節"),
            (4, 6, "清明節假期"),
            (5, 5, "劳动节"),
            (5, 26, "端午節"),
            (6, 10, "中秋節"),
            (9, 25, "國慶日"),
        ]
    }
    
    if year not in holidays:
        return {"message": f"No holidays available for year {year}"}
    
    for month, day, title in holidays[year]:
        event_date = date(year, month, day)
        # Check if already exists
        existing = db.query(CalendarEvent).filter(
            CalendarEvent.event_date == event_date,
            CalendarEvent.event_type == "public_holiday",
        ).first()
        if not existing:
            event = CalendarEvent(
                event_date=event_date,
                event_type="public_holiday",
                title=title,
            )
            db.add(event)
    
    db.commit()
    
    return {"message": f"Imported holidays for {year}", "year": year}
