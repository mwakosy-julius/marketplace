from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, CreatorProfile, UserRole
from schemas import CreatorProfileCreate, CreatorProfileResponse, UserResponse
from routes.auth import get_current_user

router = APIRouter()

@router.post("/profile", response_model=CreatorProfileResponse)
async def create_creator_profile(
    profile_data: CreatorProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if profile already exists
    existing_profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="Creator profile already exists")

    # Update user role to creator
    current_user.role = UserRole.CREATOR

    # Create profile
    profile = CreatorProfile(
        user_id=current_user.id,
        bio=profile_data.bio,
        organization=profile_data.organization,
        website=profile_data.website,
        research_areas=profile_data.research_areas
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile

@router.get("/profile", response_model=CreatorProfileResponse)
async def get_creator_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = db.query(CreatorProfile).filter(CreatorProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    return profile

@router.get("/", response_model=List[CreatorProfileResponse])
async def list_creators(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    profiles = db.query(CreatorProfile).offset(skip).limit(limit).all()
    return profiles
