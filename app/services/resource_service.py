import requests
from sqlalchemy.orm import Session
from db_models import Booking
from datetime import datetime

# 1. Weather Check Logic
def is_weather_safe(city="Barcelona"):
    # Using a free weather API (Open-Meteo)
    url = f"https://api.open-meteo.com/v1/forecast?latitude=41.3887&longitude=2.159&current_weather=true"
    response = requests.get(url).json()
    weather_code = response['current_weather']['weathercode']
    
    # Codes > 50 usually mean rain or snow
    if weather_code > 50:
        return False, "It's raining! Outdoor gear booking is restricted."
    return True, "Weather is clear."

# 2. Conflict Detection Logic
def check_booking_conflict(db: Session, resource_id: int, start: datetime, end: datetime):
    # Check if any existing booking overlaps with the requested times
    conflict = db.query(Booking).filter(
        Booking.resource_id == resource_id,
        Booking.start_time < end,
        Booking.end_time > start
    ).first()
    
    if conflict:
        return True # There is a conflict
    return False # No conflict