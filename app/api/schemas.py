from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    role: str

class ResourceCreate(BaseModel):
    name: str
    description: str
    category_id: int

class BookingCreate(BaseModel):
    user_id: int
    resource_id: int
    start_time: datetime
    end_time: datetime