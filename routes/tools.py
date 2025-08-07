from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
import os

from database import get_db
from models import User, Content, ContentType, UserRole
from schemas import ContentCreate, ContentResponse
from routers.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=ContentResponse)
async def create_tool(
    tool_data: ContentCreate,
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [UserRole.CREATOR, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only creators can upload tools")

    # Handle file upload
    file_path = None
    if file:
        upload_dir = f"uploads/tools/{current_user.id}"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = f"{upload_dir}/{file.filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    # Create tool
    tool = Content(
        creator_id=current_user.id,
        title=tool_data.title,
        description=tool_data.description,
        content_type=ContentType.TOOL,
        category=tool_data.category,
        tags=tool_data.tags,
        pricing_model=tool_data.pricing_model,
        price=tool_data.price,
        file_path=file_path,
        requirements=tool_data.requirements
    )

    db.add(tool)
    db.commit()
    db.refresh(tool)

    return tool

@router.get("/", response_model=List[ContentResponse])
async def list_tools(
    skip: int = 0,
    limit: int = 50,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Content).filter(Content.content_type == ContentType.TOOL, Content.is_published == True)

    if category:
        query = query.filter(Content.category == category)

    tools = query.offset(skip).limit(limit).all()
    return tools

@router.get("/{tool_id}", response_model=ContentResponse)
async def get_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = db.query(Content).filter(Content.id == tool_id, Content.content_type == ContentType.TOOL).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool
