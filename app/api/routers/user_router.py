from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.repositories.database import get_db
from app.repositories.models import user_orm
from app.api.schemas import UserCreate

router = APIRouter()

@router.post("/", response_model=None)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = user_orm.User(name=user.name, email=user.email, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return db.query(user_orm.User).all()

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(user_orm.User).filter(user_orm.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"message": f"User {user_id} deleted successfully"}