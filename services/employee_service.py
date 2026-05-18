"""Employee service: CRUD operations for employees with department status handling."""

from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from attendance_system.models.employee import Employee
from attendance_system.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeRead,
)


def create_employee(db: Session, employee_data: EmployeeCreate) -> EmployeeRead:
    """Create a new employee record."""
    # Check for duplicate employee_id
    existing = db.query(Employee).filter(
        Employee.employee_id == employee_data.employee_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Employee with ID '{employee_data.employee_id}' already exists",
        )

    # Check for duplicate email
    existing_email = db.query(Employee).filter(
        Employee.email == employee_data.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{employee_data.email}' is already registered",
        )

    db_employee = Employee(
        name=employee_data.name,
        employee_id=employee_data.employee_id,
        department=employee_data.department,
        position=employee_data.position,
        email=employee_data.email,
        phone=employee_data.phone,
        status=employee_data.status,
        hire_date=employee_data.hire_date,
    )

    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)

    return EmployeeRead.model_validate(db_employee)


def get_employee(db: Session, employee_id: int) -> EmployeeRead:
    """Get a single employee by ID. Returns 404 if not found."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found",
        )
    return EmployeeRead.model_validate(employee)


def list_employees(
    db: Session,
    search: str | None = None,
    department: str | None = None,
    status_filter: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> dict:
    """List employees with optional filtering and pagination."""
    query = db.query(Employee)

    if search:
        query = query.filter(
            Employee.name.ilike(f"%{search}%") | Employee.employee_id.ilike(f"%{search}%")
        )
    if department:
        query = query.filter(Employee.department.ilike(f"%{department}%"))
    if status_filter:
        query = query.filter(Employee.status == status_filter)

    total = query.count()
    items = query.order_by(Employee.id).offset(skip).limit(limit).all()

    return {
        "total": total,
        "items": [EmployeeRead.model_validate(emp) for emp in items],
    }


def update_employee(
    db: Session, employee_id: int, employee_data: EmployeeUpdate
) -> EmployeeRead:
    """Update an existing employee record."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found",
        )

    # Validate status is one of the allowed values
    if employee_data.status is not None:
        allowed_statuses = {"active", "leave", "resigned"}
        if employee_data.status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Status must be one of: {', '.join(allowed_statuses)}",
            )

    # Check for duplicate employee_id (excluding current)
    if employee_data.employee_id and employee_data.employee_id != employee.employee_id:
        existing = db.query(Employee).filter(
            Employee.employee_id == employee_data.employee_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Employee ID '{employee_data.employee_id}' is already taken",
            )

    # Check for duplicate email (excluding current)
    if employee_data.email and employee_data.email != employee.email:
        existing_email = db.query(Employee).filter(
            Employee.email == employee_data.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{employee_data.email}' is already registered",
            )

    update_data = employee_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)

    employee.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(employee)

    return EmployeeRead.model_validate(employee)


def delete_employee(db: Session, employee_id: int) -> dict:
    """Delete an employee record."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with ID {employee_id} not found",
        )

    db.delete(employee)
    db.commit()

    return {
        "message": f"Employee '{employee.employee_id}' ({employee.name}) has been deleted",
        "deleted_employee_id": employee_id,
    }
