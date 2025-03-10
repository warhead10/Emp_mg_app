from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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
def create_employee(
    employee: EmployeeCreate, 
    db: Session = Depends(get_db),
):
    
    if db.query(models.Employee).filter(models.Employee.email == employee.email).first():
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
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.get("/", response_model=List[EmployeeResponse])
def read_employees(
    # skip: int = 0, 
    # limit: int = 100, 
    db: Session = Depends(get_db),
):
    return db.query(models.Employee).all()

@router.get("/{employee_id}", response_model=EmployeeResponse)
def read_employee(
    employee_id: int, 
    db: Session = Depends(get_db),
):
    if (
        employee := db.query(models.Employee)
        .filter(models.Employee.id == employee_id)
        .first()
    ):
        return employee
    else:
        raise HTTPException(status_code=404, detail="Employee not found")

@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int, 
    employee: EmployeeUpdate, 
    db: Session = Depends(get_db),
):
    
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    
 
    if employee.name is not None:
        db_employee.name = employee.name
    if employee.email is not None:
       
        if db_employee.email != employee.email and db.query(models.Employee).filter(
            models.Employee.email == employee.email
        ).first():
            raise HTTPException(status_code=409, detail="Email already in use")
        db_employee.email = employee.email
    if employee.address is not None:
        db_employee.address = employee.address
    if employee.phone_no is not None:
        db_employee.phone_no = employee.phone_no
    if employee.status is not None:
        db_employee.status = employee.status
    
    db.commit()
    db.refresh(db_employee)
    return db_employee

@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(
    employee_id: int, 
    db: Session = Depends(get_db),
):

    db_employee = (
        db.query(models.Employee)
        .filter(models.Employee.id == employee_id)
        .first()
    )
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(db_employee)
    db.commit()
    return {"message": "Employee deleted successfully"}
