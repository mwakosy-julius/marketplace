from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional

from database import get_db
from models import Content, UsageRecord, User
from schemas import ContentResponse, UsageRecordCreate
from routes.auth import get_current_user

router = APIRouter()

@router.get("/featured", response_model=List[ContentResponse])
async def get_featured_content(db: Session = Depends(get_db)):
    content = db.query(Content).filter(Content.is_featured == True, Content.is_published == True).limit(10).all()
    return content

@router.get("/trending", response_model=List[ContentResponse])
async def get_trending_content(db: Session = Depends(get_db)):
    # Get content with highest usage in last 30 days
    content = db.query(Content).filter(Content.is_published == True).order_by(desc(Content.usage_count)).limit(20).all()
    return content

@router.get("/search", response_model=List[ContentResponse])
async def search_content(
    q: str,
    content_type: Optional[str] = None,
    category: Optional[str] = None,
    min_rating: Optional[float] = None,
    max_price: Optional[float] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Content).filter(Content.is_published == True)

    # Text search in title and description
    query = query.filter(
        (Content.title.ilike(f"%{q}%")) | (Content.description.ilike(f"%{q}%"))
    )

    if content_type:
        query = query.filter(Content.content_type == content_type)

    if category:
        query = query.filter(Content.category == category)

    if min_rating:
        query = query.filter(Content.rating >= min_rating)

    if max_price:
        query = query.filter(Content.price <= max_price)

    content = query.offset(skip).limit(limit).all()
    return content

@router.post("/use/{content_id}")
async def use_content(
    content_id: int,
    usage_data: UsageRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    # Calculate cost
    cost = 0.0
    if content.pricing_model.value == "pay_per_use":
        cost = content.price

    # Create usage record
    usage_record = UsageRecord(
        user_id=current_user.id,
        content_id=content_id,
        usage_type=usage_data.usage_type,
        cost=cost,
        metadata=usage_data.metadata
    )

    # Update content stats
    content.usage_count += 1

    db.add(usage_record)
    db.commit()

    return {"message": "Content used successfully", "cost": cost}
