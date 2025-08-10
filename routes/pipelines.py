from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os

from database import get_db
from models import User, Content, ContentType, UserRole
from schemas import ContentCreate, ContentResponse
from routes.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ContentResponse)
async def create_tool(
    pipeline_data: ContentCreate,
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only creators can upload tools")

    # Handle file upload
    file_path = None
    if file:
        upload_dir = f"uploads/pipelines/{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = f"{upload_dir}/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # Create tool
    pipeline = Content(
        creator_id=current_user.id,
        title=pipeline_data.title,
        description=pipeline_data.description,
        content_type=ContentType.TOOL,
        category=pipeline_data.category,
        tags=pipeline_data.tags,
        pricing_model=pipeline_data.pricing_model,
        price=pipeline_data.price,
        file_path=file_path,
        requirements=pipeline_data.requirements
    )

    db.add(pipeline)
    db.commit()
    db.refresh(pipeline)

    return pipeline

@router.get("/", response_model=List[ContentResponse])
async def list_pipelines(
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Content).filter(Content.content_type == ContentType.TOOL, Content.is_published == True)

    if category:
        query = query.filter(Content.category == category)

    pipelines = query.offset(skip).limit(limit).all()
    return pipelines

@router.get("/{pipeline_id}", response_model=ContentResponse)
async def get_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    pipeline = db.query(Content).filter(Content.id == pipeline_id, Content.content_type == ContentType.TOOL).first()
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipeline
