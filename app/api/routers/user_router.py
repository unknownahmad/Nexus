from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.repositories.database import get_db
from app.repositories.models import user_orm

router = APIRouter()

@router.post("/", response_model=None)
def create_user(name: str, email: str, role: str, db: Session = Depends(get_db)):
    new_user = user_orm.User(name=name, email=email, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/")
def list_users(db: Session = Depends(get_db)):
    return db.query(user_orm.User).all()