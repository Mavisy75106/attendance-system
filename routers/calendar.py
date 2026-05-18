from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..database import get_db
from ..schemas.calendar_event import CalendarEventCreate, CalendarEventRead
from ..services.calendar_service import add_calendar_event, get_events_by_month, import_holiday

router = APIRouter(prefix="/calendar", tags=["行事曆管理"])

@router.post("/events", response_model=CalendarEventRead)
def add_event(
    event: CalendarEventCreate,
    db: Session = Depends(get_db)
):
    """新增行事曆事件"""
    return add_calendar_event(db, event)

@router.get("/events", response_model=List[CalendarEventRead])
def get_events(
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份"),
    db: Session = Depends(get_db)
):
    """查詢行事曆事件"""
    return get_events_by_month(db, year, month)

@router.post("/import-holiday/{year}", response_model=dict)
def import_holidays(year: int, db: Session = Depends(get_db)):
    """匯入國定假日"""
    return import_holiday(db, year)