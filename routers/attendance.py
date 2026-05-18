from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date, time
from ..database import get_db
from ..schemas.attendance import (
    AttendanceRecordCreate, AttendanceRecordUpdate, AttendanceRecordRead
)
from ..services.attendance_service import (
    check_in, check_out, get_attendance_records, get_attendance_by_employee
)

router = APIRouter(prefix="/attendance", tags=["打卡管理"])

@router.post("/check-in", response_model=AttendanceRecordRead)
def clock_in(
    employee_id: int,
    check_date: date = Query(..., description="打卡日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """上班打卡"""
    return check_in(db, employee_id, check_date)

@router.post("/check-out", response_model=AttendanceRecordRead)
def clock_out(
    employee_id: int,
    check_date: date = Query(..., description="打卡日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """下班打卡"""
    return check_out(db, employee_id, check_date)

@router.get("/records", response_model=List[AttendanceRecordRead])
def get_records(
    start_date: date = Query(None),
    end_date: date = Query(None),
    employee_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """查詢打卡記錄"""
    return get_attendance_records(db, start_date, end_date, employee_id)

@router.get("/employee/{employee_id}", response_model=List[AttendanceRecordRead])
def get_employee_records(
    employee_id: int,
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
):
    """查詢指定員工的打卡記錄"""
    return get_attendance_by_employee(db, employee_id, start_date, end_date)
