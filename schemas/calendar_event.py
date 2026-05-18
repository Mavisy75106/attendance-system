from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class CalendarEventBase(BaseModel):
    event_date: date
    event_type: str
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[str] = None

class CalendarEventCreate(CalendarEventBase):
    pass

class CalendarEventUpdate(BaseModel):
    event_date: Optional[date] = None
    event_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    attendees: Optional[str] = None

class CalendarEventRead(CalendarEventBase):
    id: int
    is_imported: bool
    imported_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True