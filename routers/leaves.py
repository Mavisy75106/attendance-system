from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from ..database import get_db
from ..schemas.leave import (
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestRead
)
from ..services.leave_service import (
    create_leave_request, approve_leave, reject_leave, get_leave_requests, get_leave_balance
)

router = APIRouter(prefix="/leaves", tags=["請假管理"])

@router.post("/", response_model=LeaveRequestRead)
def submit_leave(
    leave: LeaveRequestCreate,
    db: Session = Depends(get_db)
):
    """申請請假"""
    return create_leave_request(db, leave)

@router.get("/", response_model=List[LeaveRequestRead])
def get_leaves(
    status: str = Query(None),
    employee_id: int = Query(None),
    db: Session = Depends(get_db)
):
    """查詢請假申請"""
    return get_leave_requests(db, status, employee_id)

@router.get("/{leave_id}", response_model=LeaveRequestRead)
def get_leave_detail(leave_id: int, db: Session = Depends(get_db)):
    """查詢請假申請詳情"""
    leave = get_leave_requests(db, None, leave_id)[0]
    if not leave:
        raise HTTPException(status_code=404, detail="找不到該請假申請")
    return leave

@router.put("/{leave_id}/approve", response_model=LeaveRequestRead)
def approve_leave_request(
    leave_id: int,
    approved_by: int = Query(..., description="核准人員工ID"),
    db: Session = Depends(get_db)
):
    """核准請假"""
    return approve_leave(db, leave_id, approved_by)

@router.put("/{leave_id}/reject", response_model=LeaveRequestRead)
def reject_leave_request(
    leave_id: int,
    approved_by: int = Query(..., description="核准人員工ID"),
    db: Session = Depends(get_db)
):
    """駁回請假"""
    return reject_leave(db, leave_id, approved_by)
