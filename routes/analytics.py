from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from database import get_db
from models import User, Content, UsageRecord, Transaction, UserRole
from routers.auth import get_current_user

router = APIRouter()

@router.get("/creator/dashboard")
async def get_creator_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Access denied")

    # Get creator's content
    content_count = db.query(Content).filter(Content.creator_id == current_user.id).count()

    # Get total usage
    total_usage = db.query(func.sum(UsageRecord.cost)).filter(
        UsageRecord.content_id.in_(
            db.query(Content.id).filter(Content.creator_id == current_user.id)
        )
    ).scalar() or 0

    # Get recent activity
    recent_usage = db.query(UsageRecord).join(Content).filter(
        Content.creator_id == current_user.id
    ).order_by(desc(UsageRecord.created_at)).limit(10).all()

    return {
        "content_count": content_count,
        "total_earnings": total_usage,
        "recent_activity": recent_usage
    }

@router.get("/admin/platform")
async def get_platform_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    # Platform metrics
    total_users = db.query(User).count()
    total_creators = db.query(User).filter(User.role == UserRole.CREATOR).count()
    total_content = db.query(Content).count()
    total_revenue = db.query(func.sum(UsageRecord.cost)).scalar() or 0

    return {
        "total_users": total_users,
        "total_creators": total_creators,
        "total_content": total_content,
        "total_revenue": total_revenue
    }
