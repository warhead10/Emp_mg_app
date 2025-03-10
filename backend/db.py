from base import Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import models
import psycopg2

engine = create_engine("postgresql+psycopg2://postgres:root@localhost:5432/employee_db")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def setup_database():
   
    Base.metadata.create_all(bind=engine)  
    print("Database Tables Created")
    print("Database Connection Established")

if __name__ == "__main__":
    setup_database()