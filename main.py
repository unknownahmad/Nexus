from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import db_models
from database import engine, get_db
from logic import is_weather_safe, check_booking_conflict

# This command creates the tables in Cloud SQL if they don't exist yet
db_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus Resource Management")

@app.get("/")
def read_root():
    return {"status": "Nexus API is Online", "location": "Barcelona"}

@app.get("/check-weather")
def get_weather():
    safe, message = is_weather_safe()
    return {"safe": safe, "message": message}

@app.post("/users/")
def create_user(name: str, email: str, role: str, db: Session = Depends(get_db)):
    new_user = db_models.User(name=name, email=email, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/")
def list_users(db: Session = Depends(get_db)):
    return db.query(db_models.User).all()