from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from models import Base
from models import Employee, UserRole, EmpStatus
import asyncpg

engine = create_async_engine("postgresql+asyncpg://postgres:root@localhost:5432/employee_db")


SessionLocal = sessionmaker(
    bind=engine, 
    expire_on_commit=False,
    class_=AsyncSession,
)

async def get_db():
    async with SessionLocal() as db:
        yield db

async def setup_database():
   async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Database Tables Created")
        print("Database Connection Established")

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_database())
    