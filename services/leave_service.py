"""Leave service: Leave request management including approval, rejection, and balance."""

from datetime import date, datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from models.leave import LeaveRequest
from schemas.leave import LeaveRequestRead, LeaveRequestCreate


# Annual leave days per year - configurable constant
ANNUAL_LEAVE_DAYS = 14


def _count_leave_days(start_date: date, end_date: date) -> int:
    """Count the number of days in a leave period (inclusive)."""
    return (end_date - start_date).days + 1


def create_leave_request(db: Session, leave_data: LeaveRequestCreate) -> LeaveRequestRead:
    """Create a new leave request."""
    leave_request = LeaveRequest(
        employee_id=leave_data.employee_id,
        leave_type=leave_data.leave_type,
        start_date=leave_data.start_date,
        end_date=leave_data.end_date,
        reason=leave_data.reason,
        status="pending",
    )

    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)

    return LeaveRequestRead.model_validate(leave_request)


def get_leave_request(db: Session, leave_id: int) -> LeaveRequestRead:
    """Get a single leave request by ID."""
    leave_request = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_id
    ).first()
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave request with ID {leave_id} not found",
        )
    return LeaveRequestRead.model_validate(leave_request)


def get_leave_requests(
    db: Session,
    status_filter: str | None = None,
    employee_id: int | None = None,
) -> list[LeaveRequestRead]:
    """Get leave requests with optional filters."""
    query = db.query(LeaveRequest)

    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)
    if employee_id:
        query = query.filter(LeaveRequest.employee_id == employee_id)

    items = query.order_by(LeaveRequest.id.desc()).all()
    return [LeaveRequestRead.model_validate(lr) for lr in items]


def get_pending_requests(db: Session) -> list[LeaveRequestRead]:
    """Get all pending leave requests."""
    items = (
        db.query(LeaveRequest)
        .filter(LeaveRequest.status == "pending")
        .order_by(LeaveRequest.start_date)
        .all()
    )
    return [LeaveRequestRead.model_validate(lr) for lr in items]


def get_leave_balance(
    db: Session, employee_id: int, year: int
) -> dict:
    """Calculate remaining leave balance for an employee in a given year."""
    from models.employee import Employee
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found",
        )

    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)

    # Sum approved annual leave days used this year
    used_days = 0
    approved_leaves = (
        db.query(LeaveRequest)
        .filter(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.leave_type == "annual",
            LeaveRequest.status == "approved",
            LeaveRequest.start_date >= year_start,
            LeaveRequest.start_date <= year_end,
        )
        .all()
    )

    for leave in approved_leaves:
        leave_days = _count_leave_days(leave.start_date, leave.end_date)
        used_days += leave_days

    remaining = max(0, ANNUAL_LEAVE_DAYS - used_days)

    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "year": year,
        "total_annual_leave": ANNUAL_LEAVE_DAYS,
        "used_days": used_days,
        "remaining_days": remaining,
    }


def approve_leave(db: Session, leave_id: int, approved_by: int) -> LeaveRequestRead:
    """Approve a leave request."""
    leave_request = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_id
    ).first()
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave request with ID {leave_id} not found",
        )
    if leave_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Leave request is already {leave_request.status}",
        )

    leave_request.status = "approved"
    leave_request.approved_by = approved_by
    db.commit()
    db.refresh(leave_request)

    return LeaveRequestRead.model_validate(leave_request)


def reject_leave(db: Session, leave_id: int, reason: str | None = None) -> LeaveRequestRead:
    """Reject a leave request."""
    leave_request = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_id
    ).first()
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Leave request with ID {leave_id} not found",
        )
    if leave_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Leave request is already {leave_request.status}",
        )

    leave_request.status = "rejected"
    db.commit()
    db.refresh(leave_request)

    return LeaveRequestRead.model_validate(leave_request)