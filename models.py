from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.relationship import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class UserRole(enum.Enum):
    USER = "user"
    CREATOR = "creator"
    ADMIN = "admin"

class ContentType(enum.Enum):
    TOOL = "tool"
    PIPELINE = "pipeline"
    DATASET = "dataset"

class PricingModel(enum.Enum):
    FREE = "free"
    PAY_PER_USE = "pay_per_use"
    SUBSCRIPTION = "subscription"
    ONE_TIME = "one_time"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Creator profile
    creator_profile = relationship("CreatorProfile", back_populates="user", uselist=False)
    created_content = relationship("Content", back_populates="creator")
    usage_records = relationship("UsageRecord", back_populates="user")

class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    bio = Column(Text)
    organization = Column(String)
    website = Column(String)
    research_areas = Column(JSON)  # List of research areas
    total_earnings = Column(Float, default=0.0)
    total_downloads = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="creator_profile")

class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(Enum(ContentType), nullable=False)
    category = Column(String)  # genomics, proteomics, etc.
    tags = Column(JSON)  # List of tags

    # Pricing
    pricing_model = Column(Enum(PricingModel), default=PricingModel.FREE)
    price = Column(Float, default=0.0)

    # Metadata
    version = Column(String, default="1.0.0")
    file_path = Column(String)  # Path to uploaded files
    docker_image = Column(String)  # For containerized tools
    requirements = Column(JSON)  # Dependencies, system requirements

    # Stats
    download_count = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)

    # Status
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    creator = relationship("User", back_populates="created_content")
    reviews = relationship("Review", back_populates="content")
    usage_records = relationship("UsageRecord", back_populates="content")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Integer)  # 1-5 stars
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    content = relationship("Content", back_populates="reviews")

class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    usage_type = Column(String)  # download, execution, view
    cost = Column(Float, default=0.0)
    metadata = Column(JSON)  # Execution details, parameters used
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="usage_records")
    content = relationship("Content", back_populates="usage_records")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    creator_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("content.id"))
    amount = Column(Float, nullable=False)
    platform_fee = Column(Float, default=0.0)
    creator_earnings = Column(Float, nullable=False)
    transaction_id = Column(String, unique=True)  # External payment processor ID
    status = Column(String, default="pending")  # pending, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
