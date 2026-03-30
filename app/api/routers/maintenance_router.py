from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.repositories.database import get_db
from app.repositories.models import user_orm

router = APIRouter()

@router.post("/")
def create_maintenance_record(resource_id: int, status: str, db: Session = Depends(get_db)):
    # 1. Verify the resource exists
    resource = db.query(user_orm.Resource).filter(user_orm.Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    # 2. Restrict status to specific keywords for clean data
    valid_statuses = ["Active", "Broken", "In Repair"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of: {valid_statuses}")

    # 3. Save the maintenance log
    new_log = user_orm.Maintenance(
        resource_id=resource_id,
        status=status
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

@router.get("/{resource_id}")
def get_maintenance_history(resource_id: int, db: Session = Depends(get_db)):
    logs = db.query(user_orm.Maintenance).filter(user_orm.Maintenance.resource_id == resource_id).all()
    return logs