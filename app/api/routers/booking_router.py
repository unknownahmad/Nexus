from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.repositories.database import get_db
from app.repositories.models import user_orm
from app.services.resource_service import check_booking_conflict, is_weather_safe
from app.api.schemas import BookingCreate

router = APIRouter()

@router.post("/")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    resource = db.query(user_orm.Resource).filter(user_orm.Resource.id == booking.resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    conflict = check_booking_conflict(db, booking.resource_id, booking.start_time, booking.end_time)
    if conflict:
        raise HTTPException(status_code=400, detail="Time slot already booked")
        
    safe, msg = is_weather_safe()
    if not safe:
        raise HTTPException(status_code=400, detail=msg)

    new_booking = user_orm.Booking(
        user_id=booking.user_id,
        resource_id=booking.resource_id,
        start_time=booking.start_time,
        end_time=booking.end_time
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

@router.get("/")
def list_bookings(db: Session = Depends(get_db)):
    return db.query(user_orm.Booking).all()