from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.repositories.database import get_db
from app.repositories.models import user_orm

router = APIRouter()

@router.post("/")
def create_review(resource_id: int, rating: int, comment: str, db: Session = Depends(get_db)):
    # 1. Verify the rating is between 1 and 5
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
    # 2. Verify the resource actually exists
    resource = db.query(user_orm.Resource).filter(user_orm.Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
        
    # 3. Save the review
    new_review = user_orm.Review(
        resource_id=resource_id,
        rating=rating,
        comment=comment
    )
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

@router.get("/{resource_id}")
def get_resource_reviews(resource_id: int, db: Session = Depends(get_db)):
    reviews = db.query(user_orm.Review).filter(user_orm.Review.resource_id == resource_id).all()
    return reviews