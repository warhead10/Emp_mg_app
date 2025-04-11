from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select  # added for async queries
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import bcrypt
from db import get_db
import models
from models import UserRole, EmpStatus 

router = APIRouter(prefix="/employees")

class EmployeeBase(BaseModel):
    name: str
    email: str
    address: str
    phone_no: str
    status: EmpStatus = EmpStatus.ACTIVE  

class EmployeeCreate(EmployeeBase):
    name: str
    email: str
    address: str
    phone_no: str
    status: EmpStatus = EmpStatus.ACTIVE
    password: str 
    role: UserRole = UserRole.USER  

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    phone_no: Optional[str] = None
    status: Optional[EmpStatus] = None  

class EmployeeResponse(EmployeeBase):
    id: int
    joined_on: datetime
    created_at: datetime
    updated_at: datetime
    role: UserRole 

    class Config:
        from_attributes = True

@router.post("/register", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def create_employee(
    employee: EmployeeCreate, 
    db: Session = Depends(get_db),
):
    result = await db.execute(select(models.Employee).filter(models.Employee.email == employee.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already exists")
    
    hashed_password = bcrypt.hashpw(employee.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    db_employee = models.Employee(
        name=employee.name,
        email=employee.email,
        password=hashed_password,
        role=employee.role,
        address=employee.address,
        phone_no=employee.phone_no,
        status=employee.status,
    )
    
    db.add(db_employee)
    await db.commit()
    await db.refresh(db_employee)
    return db_employee

@router.get("/employees", response_model=List[EmployeeResponse])
async def read_employees(
    db: Session = Depends(get_db),
):
    result = await db.execute(select(models.Employee))
    employees = result.scalars().all()
    return employees

@router.get("/{employee_id}", response_model=EmployeeResponse)
async def read_employee(
    employee_id: int, 
    db: Session = Depends(get_db),
):
    result = await db.execute(select(models.Employee).filter(models.Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if employee:
        return employee
    else:
        raise HTTPException(status_code=404, detail="Employee not found")






@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int, 
    employee: EmployeeUpdate, 
    db: Session = Depends(get_db),
):
    result = await db.execute(select(models.Employee).filter(models.Employee.id == employee_id))
    db_employee = result.scalar_one_or_none()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if employee.name is not None:
        db_employee.name = employee.name
    if employee.email is not None:
        if db_employee.email != employee.email:
            result = await db.execute(select(models.Employee).filter(models.Employee.email == employee.email))
            if result.scalar_one_or_none():
                raise HTTPException(status_code=409, detail="Email already in use")
        db_employee.email = employee.email
    if employee.address is not None:
        db_employee.address = employee.address
    if employee.phone_no is not None:
        db_employee.phone_no = employee.phone_no
    if employee.status is not None:
        db_employee.status = employee.status

    await db.commit()
    await db.refresh(db_employee)
    return db_employee







@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_employee(
    employee_id: int, 
    db: Session = Depends(get_db),
):
    result = await db.execute(select(models.Employee).filter(models.Employee.id == employee_id))
    db_employee = result.scalar_one_or_none()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    await db.delete(db_employee)
    await db.commit()
    return {"message": "Employee deleted successfully"}
