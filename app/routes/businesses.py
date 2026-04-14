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
    