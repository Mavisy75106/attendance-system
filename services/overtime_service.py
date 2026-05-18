"""Overtime service: Overtime request management including approval and hours calculation."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from attendance_system.models.overtime import OvertimeRequest
from attendance_system.schemas.overtime import OvertimeRequestRead, OvertimeRequestCreate


def create_overtime_request(db: Session, overtime_data: OvertimeRequestCreate) -> OvertimeRequestRead:
    """Create a new overtime request with auto-calculated hours."""
    overtime_request = OvertimeRequest(
        employee_id=overtime_data.employee_id,
        date=overtime_data.date,
        start_time=overtime_data.start_time,
        end_time=overtime_data.end_time,
        reason=overtime_data.reason,
        hours=OvertimeRequest.calculate_hours(overtime_data.start_time, overtime_data.end_time),
        status="pending",
    )

    db.add(overtime_request)
    db.commit()
    db.refresh(overtime_request)

    return OvertimeRequestRead.model_validate(overtime_request)


def get_overtime_request(db: Session, overtime_id: int) -> OvertimeRequestRead:
    """Get a single overtime request by ID."""
    overtime_request = db.query(OvertimeRequest).filter(
        OvertimeRequest.id == overtime_id
    ).first()
    if not overtime_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Overtime request with ID {overtime_id} not found",
        )
    return OvertimeRequestRead.model_validate(overtime_request)


def get_overtime_requests(
    db: Session,
    status_filter: str | None = None,
    employee_id: int | None = None,
) -> list[OvertimeRequestRead]:
    """Get overtime requests with optional filters."""
    query = db.query(OvertimeRequest)

    if status_filter:
        query = query.filter(OvertimeRequest.status == status_filter)
    if employee_id:
        query = query.filter(OvertimeRequest.employee_id == employee_id)

    items = query.order_by(OvertimeRequest.id.desc()).all()
    return [OvertimeRequestRead.model_validate(ot) for ot in items]


def get_pending_requests(db: Session) -> list[OvertimeRequestRead]:
    """Get all pending overtime requests."""
    items = (
        db.query(OvertimeRequest)
        .filter(OvertimeRequest.status == "pending")
        .order_by(OvertimeRequest.date)
        .all()
    )
    return [OvertimeRequestRead.model_validate(ot) for ot in items]


def approve_overtime(db: Session, overtime_id: int, approved_by: int) -> OvertimeRequestRead:
    """Approve an overtime request."""
    overtime_request = db.query(OvertimeRequest).filter(
        OvertimeRequest.id == overtime_id
    ).first()
    if not overtime_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Overtime request with ID {overtime_id} not found",
        )
    if overtime_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Overtime request is already {overtime_request.status}",
        )

    overtime_request.status = "approved"
    db.commit()
    db.refresh(overtime_request)

    return OvertimeRequestRead.model_validate(overtime_request)


def reject_overtime(db: Session, overtime_id: int, approved_by: int) -> OvertimeRequestRead:
    """Reject an overtime request."""
    overtime_request = db.query(OvertimeRequest).filter(
        OvertimeRequest.id == overtime_id
    ).first()
    if not overtime_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Overtime request with ID {overtime_id} not found",
        )
    if overtime_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Overtime request is already {overtime_request.status}",
        )

    overtime_request.status = "rejected"
    db.commit()
    db.refresh(overtime_request)

    return OvertimeRequestRead.model_validate(overtime_request)