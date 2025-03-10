from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from base import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"  

class EmpStatus(str,enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String(128), nullable=False)  # Ensure this line is present
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    address = Column(String, nullable=False)  
    phone_no = Column(String, nullable=False)  
    joined_on = Column(DateTime, nullable=False, default=func.now()) 
    status = Column(Enum(EmpStatus), nullable=False, default="active")

    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

