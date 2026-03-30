from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.repositories.database import get_db
from app.repositories.models import user_orm

router = APIRouter()

# --- CATEGORY ENDPOINTS ---
@router.post("/categories/")
def create_category(name: str, db: Session = Depends(get_db)):
    new_category = user_orm.Category(name=name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/categories/")
def list_categories(db: Session = Depends(get_db)):
    return db.query(user_orm.Category).all()

# --- RESOURCE (GEAR) ENDPOINTS ---
@router.post("/resources/")
def create_resource(name: str, description: str, category_id: int, db: Session = Depends(get_db)):
    new_resource = user_orm.Resource(
        name=name, 
        description=description, 
        category_id=category_id
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource

@router.get("/resources/")
def list_resources(db: Session = Depends(get_db)):
    return db.query(user_orm.Resource).all()


@router.delete("/resources/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(user_orm.Resource).filter(user_orm.Resource.id == resource_id).first()
    if not resource:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Resource not found")
    
    db.delete(resource)
    db.commit()
    return {"message": f"Resource {resource_id} deleted successfully"}