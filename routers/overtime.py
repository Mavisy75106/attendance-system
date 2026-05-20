from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from database import get_db
from schemas.overtime import (
    OvertimeRequestCreate, OvertimeRequestUpdate, OvertimeRequestRead
)
from services.overtime_service import (
    create_overtime_request, approve_overtime, reject_overtime, get_overtime_requests
)

router = APIRouter(prefix="/overtime", tags=["加班管理"])

@router.post("/", response_model=OvertimeRequestRead)
def submit_overtime(
    overtime: OvertimeRequestCreate,
    db: Session = Depends(get_db)
):
    """申請加班"""
    return create_overtime_request(db, overtime)

@router.get("/", response_model=List[OvertimeRequestRead])
def get_overtimes(
    status: str = Query(None),
    employee_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """查詢加班申請"""
    return get_overtime_requests(db, status, employee_id)

@router.put("/{overtime_id}/approve", response_model=OvertimeRequestRead)
def approve_overtime_request(
    overtime_id: int,
    approved_by: int = Query(..., description="核准人員工ID"),
    db: Session = Depends(get_db)
):
    """核准加班"""
    return approve_overtime(db, overtime_id, approved_by)

@router.put("/{overtime_id}/reject", response_model=OvertimeRequestRead)
def reject_overtime_request(
    overtime_id: int,
    approved_by: int = Query(..., description="核准人員工ID"),
    db: Session = Depends(get_db)
):
    """駁回加班"""
    return reject_overtime(db, overtime_id, approved_by)