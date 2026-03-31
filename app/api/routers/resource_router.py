from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.repositories.database import get_db
from app.repositories.models import user_orm
from app.api.schemas import ResourceCreate

router = APIRouter()

class CategoryCreate(BaseModel):
    name: str

@router.post("/categories")
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    new_category = user_orm.Category(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    return db.query(user_orm.Category).all()

@router.post("/")
def create_resource(res: ResourceCreate, db: Session = Depends(get_db)):
    new_resource = user_orm.Resource(
        name=res.name, 
        description=res.description, 
        category_id=res.category_id
    )
    db.add(new_resource)
    db.commit()
    db.refresh(new_resource)
    return new_resource

@router.get("/")
def list_resources(db: Session = Depends(get_db)):
    return db.query(user_orm.Resource).all()

@router.delete("/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(user_orm.Resource).filter(user_orm.Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    db.delete(resource)
    db.commit()
    return {"message": f"Resource {resource_id} deleted successfully"}