from fastapi import FastAPI
from app.repositories.database import engine
from app.repositories.models import user_orm
from app.api.routers import user_router, weather_router, resource_router, booking_router, review_router, maintenance_router

user_orm.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus Resource Management")

@app.get("/")
def read_root():
    return {
        "status": "Nexus API is Online", 
        "location": "Barcelona",
        "architecture": "Layered (A+ Standard)"
    }

app.include_router(weather_router.router, tags=["Weather"])
app.include_router(user_router.router, prefix="/users", tags=["Users"])
app.include_router(resource_router.router, tags=["Resources"])
app.include_router(booking_router.router, prefix="/bookings", tags=["Bookings"])
app.include_router(review_router.router, prefix="/reviews", tags=["Reviews"])
app.include_router(maintenance_router.router, prefix="/maintenance", tags=["Maintenance"])