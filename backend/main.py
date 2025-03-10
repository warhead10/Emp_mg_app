from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from employee import router
import uvicorn
from db import setup_database
from db import SessionLocal
app = FastAPI(title="Employee Management System")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Employee App"}

if __name__ == "__main__":
    setup_database()
    uvicorn.run(app, host="0.0.0.0", port=8000)