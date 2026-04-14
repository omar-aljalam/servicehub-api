from fastapi import (APIRouter, Depends, HTTPException,
                     UploadFile, File, status, Query
                     )
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
import uuid
import os
import shutil
from slugify import slugify

from app.database import get_db
from app.models.models import Business, BusinessImage, BusinessLocation, Category
from app.schemas.schemas import (
    BusinessCreate, BusinessUpdate,
    BusinessResponse, BusinessListResponse
)

router = APIRouter(prefix="/businesses", tags=["businesses"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def make_unique_slug(name: str, db: Session, exclude_id=None) -> str:
    "Generate a unique slug, checking the DB for collisions"
    base = slugify(name)
    slug = base
    counter = 1
    while True:
        query = db.query(Business).filter(Business.slug == slug)
        if exclude_id:
            query = query.filter(Business.id != exclude_id)
        if not query.first():
            break
        slug = f"{base}-{counter}"
        counter += 1
    return slug


@router.get("/", response_model=list[BusinessListResponse])
def list_businesses(
    db: Session = Depends(get_db),
    city: Optional[str] = Query(None, description="Filter by city"),
    category_slug: Optional[str] = Query(
        None, description="Filter by category"),
    search: Optional[str] = Query(
        None, description="Search by name or description"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(20, le=100, description="Max results per page"),
    offset: int = Query(0, description=("Pagination offset"))
    ):
    
    query = db.query(Business)

    # Filter by status
    if status:
        query = query.filter(Business.status == status)

    # Filter by category
    if category_slug:
        query = query.join(Business.category).filter(Category.slug == category_slug)

    # Filter by city
    if city:
        query = query.join(Business.locations).filter(
            BusinessLocation.city.ilike(f"%{city}%")
        )
    
    # Search on name or descritpion
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Business.name.ilike(search_term),
                Business.description.ilike(search_term)
            )
        )
    
    return query.offset(offset).limit(limit).distinct().all()