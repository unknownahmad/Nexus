from fastapi import FastAPI, Depends, HTTPException
from fastapi.security.api_key import APIKeyHeader
import os
from app.repositories.database import engine
from app.repositories.models import user_orm
from app.api.routers import user_router, weather_router, resource_router, booking_router, review_router, maintenance_router

user_orm.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus Resource Management")

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(header_key: str = Depends(api_key_header)):
    if header_key == os.getenv("ADMIN_API_KEY"):
        return header_key
    raise HTTPException(status_code=403, detail="Could not validate credentials")

@app.get("/")
def read_root():
    return {
        "status": "Nexus API is Online", 
        "location": "Barcelona",
        "architecture": "Layered (A+ Standard)"
    }

app.include_router(user_router.router, prefix="/users", tags=["Users"], dependencies=[Depends(get_api_key)])
app.include_router(resource_router.router, prefix="/resources", tags=["Resources"], dependencies=[Depends(get_api_key)])
app.include_router(booking_router.router, prefix="/bookings", tags=["Bookings"], dependencies=[Depends(get_api_key)])
app.include_router(review_router.router, prefix="/reviews", tags=["Reviews"], dependencies=[Depends(get_api_key)])
app.include_router(maintenance_router.router, prefix="/maintenance", tags=["Maintenance"], dependencies=[Depends(get_api_key)])
app.include_router(weather_router.router, prefix="/weather", tags=["Weather"], dependencies=[Depends(get_api_key)])