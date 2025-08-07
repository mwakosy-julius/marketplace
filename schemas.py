from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import UserRole, ContentType, PricingModel

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CreatorProfileCreate(BaseModel):
    bio: Optional[str] = None
    organization: Optional[str] = None
    website: Optional[str] = None
    research_areas: Optional[List[str]] = []

class CreatorProfileResponse(BaseModel):
    id: int
    bio: Optional[str]
    organization: Optional[str]
    website: Optional[str]
    research_areas: List[str]
    total_earnings: float
    total_downloads: int
    rating: float

    class Config:
        from_attributes = True

class ContentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    content_type: ContentType
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    pricing_model: PricingModel = PricingModel.FREE
    price: float = 0.0
    requirements: Optional[Dict[str, Any]] = {}

class ContentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    content_type: ContentType
    category: Optional[str]
    tags: List[str]
    pricing_model: PricingModel
    price: float
    version: str
    download_count: int
    usage_count: int
    rating: float
    review_count: int
    is_published: bool
    is_featured: bool
    created_at: datetime
    creator: UserResponse

    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    rating: int
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class UsageRecordCreate(BaseModel):
    content_id: int
    usage_type: str
    metadata: Optional[Dict[str, Any]] = {}

class Token(BaseModel):
    access_token: str
    token_type: str
