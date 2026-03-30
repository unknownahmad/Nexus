from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.repositories.database import get_db
from app.repositories.models import user_orm
from app.services.resource_service import check_booking_conflict, is_weather_safe

router = APIRouter()

@router.post("/")
def create_booking(user_id: int, resource_id: int, start_time: datetime, end_time: datetime, db: Session = Depends(get_db)):
    resource = db.query(user_orm.Resource).filter(user_orm.Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    conflict = check_booking_conflict(db, resource_id, start_time, end_time)
    if conflict:
        raise HTTPException(status_code=400, detail="Time slot already booked")
        
    safe, msg = is_weather_safe()
    if not safe:
        raise HTTPException(status_code=400, detail=msg)

    new_booking = user_orm.Booking(
        user_id=user_id,
        resource_id=resource_id,
        start_time=start_time,
        end_time=end_time
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

@router.get("/")
def list_bookings(db: Session = Depends(get_db)):
    return db.query(user_orm.Booking).all()