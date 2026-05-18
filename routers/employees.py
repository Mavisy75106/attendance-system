from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeRead, EmployeeList
)
from ..services.employee_service import (
    create_employee, get_employee, list_employees, update_employee, delete_employee
)

router = APIRouter(prefix="/employees", tags=["員工管理"])

@router.post("/", response_model=EmployeeRead)
def create_new_employee(emp: EmployeeCreate, db: Session = Depends(get_db)):
    return create_employee(db, emp)

@router.get("/", response_model=List[EmployeeRead])
def get_employees(
    search: str = Query(None, description="搜尋姓名或工號"),
    department: str = Query(None, description="部門篩選"),
    status: str = Query(None, description="狀態篩選 (active/leave/resigned)"),
    db: Session = Depends(get_db)
):
    return list_employees(db, search=search, department=department, status_filter=status)

@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee_detail(employee_id: int, db: Session = Depends(get_db)):
    emp = get_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="找不到該員工")
    return emp

@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee_detail(
    employee_id: int,
    emp: EmployeeUpdate,
    db: Session = Depends(get_db)
):
    return update_employee(db, employee_id, emp)

@router.delete("/{employee_id}", summary="刪除員工")
def delete_employee_detail(employee_id: int, db: Session = Depends(get_db)):
    deleted = delete_employee(db, employee_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="找不到該員工")
    return {"message": f"員工 {employee_id} 已刪除"}
