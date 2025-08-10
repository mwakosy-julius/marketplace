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
    dataset: ContentCreate,
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
    data = Content(
        creator_id=current_user.id,
        title=dataset.title,
        description=dataset.description,
        content_type=ContentType.TOOL,
        category=dataset.category,
        tags=dataset.tags,
        pricing_model=dataset.pricing_model,
        price=dataset.price,
        file_path=file_path,
        requirements=dataset.requirements
    )

    db.add(data)
    db.commit()
    db.refresh(data)

    return data

@router.get("/", response_model=List[ContentResponse])
async def list_datasets(
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Content).filter(Content.content_type == ContentType.TOOL, Content.is_published == True)

    if category:
        query = query.filter(Content.category == category)

    datasets = query.offset(skip).limit(limit).all()
    return datasets

@router.get("/{data_id}", response_model=ContentResponse)
async def get_pipeline(data_id: int, db: Session = Depends(get_db)):
    data = db.query(Content).filter(Content.id == data_id, Content.content_type == ContentType.TOOL).first()
    if not data:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return data
