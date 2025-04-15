from fastapi import APIRouter, Depends, HTTPException, status 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import bcrypt
from jose import jwt

from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel
from db import get_db
import models


class login(BaseModel):
    username: str
    password: str


router = APIRouter(prefix="/auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

SECRET = "PASSWORD"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30




async def create_access_token(data: dict):
    from datetime import datetime, timedelta, timezone

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET, algorithm=ALGORITHM)
    return encoded_jwt






@router.post("/token")
async def login( form_data:login = Depends(), 
                db:Session =Depends(get_db),
                ):
    try:
        user = await db.execute(select(models.Employee).filter(models.Employee.email == form_data.username))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=400, detail="No user found with this email")
        if not bcrypt.checkpw(form_data.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=400, detail="Incorrect password")
        if user.status != models.EmpStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="User is not active")
        # Create a token and return it
        access_token = await create_access_token(data={"sub": user.email, "id": user.id})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/users/me")
async def get_current_user(token: str = Depends(oauth2_scheme), db:Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        print(payload)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = await db.execute(select(models.Employee).filter(models.Employee.email == user_id))
        user = user.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return {"user_id": user.id, "email": user.email, "role": user.role, "status": user.status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))