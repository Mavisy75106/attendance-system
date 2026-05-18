"""Attendance service: Check-in, check-out, daily records, and employee attendance."""

from datetime import datetime, time, date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from attendance_system.models.attendance import AttendanceRecord
from attendance_system.schemas.attendance import (
    AttendanceRecordCreate,
    AttendanceRecordRead,
)

LATE_THRESHOLD = time(9, 30)  # 09:30
EARLY_THRESHOLD = time(18, 0)  # 18:00


def _auto_set_status(clock_in: time | None, clock_out: time | None, status: str | None) -> str:
    """Auto-calculate attendance status based on clock-in/out times."""
    if status and status != "absent":
        return status

    # If no clock-in, still absent
    if not clock_in:
        return "absent"

    # Check if late (clock-in > 09:30)
    if clock_in > LATE_THRESHOLD:
        return "late"

    # Check if early absent (clock-out < 18:00)
    if clock_out and clock_out < EARLY_THRESHOLD:
        return "early_absent"

    return "present"


def get_attendance_records(
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
    employee_id: int | None = None,
) -> list:
    """Get attendance records with optional filtering."""
    query = db.query(AttendanceRecord)
    
    if start_date:
        query = query.filter(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.date <= end_date)
    if employee_id:
        query = query.filter(AttendanceRecord.employee_id == employee_id)
    
    records = query.order_by(AttendanceRecord.date.desc()).all()
    return [AttendanceRecordRead.model_validate(r) for r in records]


def check_in(db: Session, employee_id: int, check_date: date) -> AttendanceRecordRead:
    """Record a check-in for an employee on a given date. Sets late status if after 09:30."""
    employee_date = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.date == check_date,
    ).first()

    clock_in = datetime.utcnow().time()

    if employee_date:
        employee_date.clock_in = clock_in
        employee_date.status = _auto_set_status(
            clock_in, employee_date.clock_out, employee_date.status
        )
        employee_date.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(employee_date)
    else:
        attendance = AttendanceRecord(
            employee_id=employee_id,
            date=check_date,
            clock_in=clock_in,
            clock_out=None,
            status=_auto_set_status(clock_in, None, None),
        )
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        employee_date = attendance

    return AttendanceRecordRead.model_validate(employee_date)


def check_out(db: Session, employee_id: int, check_date: date) -> AttendanceRecordRead:
    """Record a check-out for an employee on a given date. Sets early_absent if before 18:00."""
    record = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id,
        AttendanceRecord.date == check_date,
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No check-in record found for employee {employee_id} on {check_date}",
        )

    # Only allow check_out if clock_in is set
    if not record.clock_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee has not checked in yet for this date",
        )

    clock_out = datetime.utcnow().time()

    record.clock_out = clock_out
    record.status = _auto_set_status(record.clock_in, clock_out, record.status)
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)

    return AttendanceRecordRead.model_validate(record)


def get_daily_attendance(
    db: Session,
    target_date: date | None = None,
    department: str | None = None,
) -> dict:
    """Get attendance records for a specific date, optionally filtered by department."""
    if target_date is None:
        target_date = datetime.utcnow().date()

    query = db.query(AttendanceRecord).filter(
        AttendanceRecord.date == target_date,
    )

    if department:
        # Join with employees to filter by department
        from attendance_system.models.employee import Employee
        query = query.join(Employee).filter(
            Employee.department.ilike(f"%{department}%")
        )

    records = query.all()

    return {
        "date": target_date,
        "total": len(records),
        "records": [
            AttendanceRecordRead.model_validate(record) for record in records
        ],
    }


def get_attendance_by_employee(
    db: Session,
    employee_id: int,
    start_date: date | None = None,
    end_date: date | None = None,
    skip: int = 0,
    limit: int = 100,
) -> dict:
    """Get attendance records for a specific employee with optional date range filtering."""
    # Verify employee exists
    from attendance_system.models.employee import Employee
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found",
        )

    query = db.query(AttendanceRecord).filter(
        AttendanceRecord.employee_id == employee_id,
    )

    if start_date:
        query = query.filter(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.date <= end_date)

    total = query.count()
    items = (
        query
        .order_by(AttendanceRecord.date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return {
        "employee_id": employee_id,
        "employee_name": employee.name,
        "total": total,
        "items": [
            AttendanceRecordRead.model_validate(record) for record in items
        ],
    }
