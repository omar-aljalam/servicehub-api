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
from app.models.models import Business, BusinessImage, BusinessLocation, Category, BusinessStatus
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

@router.get("/{slug}", response_model=BusinessResponse)
def get_business(slug: str, db: Session = Depends(get_db)):
    business = db.query(Business).filter(Business.slug == slug).first()
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with slug '{slug} not found'"
        )
    return business


@router.post("/", response_model=BusinessCreate, status_code=status.HTTP_201_CREATED)
def create_business(payload: BusinessCreate, db: Session = Depends(get_db)):
    slug = make_unique_slug(payload.name, db)
    
    business = Business(
        # Hardcoded owner for now — replace with auth token in production
        owner_id=db.query(Business).first.owner_id if db.query(Business).first() else uuid.uuid4,
        name=payload.name,
        slug=slug,
        description=payload.description,
        category_id=payload.category_id,
        phone=payload.phone,
        email=payload.email,
        website=payload.website,
        status=BusinessStatus.PENDING,
    )
    db.add(business)
    db.flush()

    # Create location if provided
    if payload.location:
        loc = payload.location
        location = BusinessLocation(
            street=loc.street,
            city=loc.city,
            country=loc.country,
            postal_code=loc.postal_code,
            latitude=loc.latitude,
            longitude=loc.longitude,
            is_primary=True,
            business=business
        )
        db.add(location)

    db.commit()
    db.refresh(business)
    return business

@router.patch("/{business_id}", response_model=BusinessListResponse)
def update_business(
    business_id: uuid.UUID,
    payload: BusinessUpdate,
    db: Session=Depends(get_db),
):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Business not found")
    
    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data:
        update_data["slug"] = make_unique_slug(update_data["name"], db, exclude_id=business_id)

    for field, value in update_data.items():
        setattr(business, field, value)

    db.commit()
    db.refresh(business)
    return business

@router.post("/{business_id}/images", response_model=dict)
def upload_image(
    business_id: uuid.UUID,
    is_logo: bool=False,
    file: UploadFile = File(...),
    db: Session=Depends(get_db)
):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Business not found")
    
    allowed_types = {".jpg", ".jpeg", ".png", ".webp"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{ext}' not allowed. Use {', '.join(allowed_types)}"
        )
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    max_order = db.query(BusinessImage).filter(
        BusinessImage.business_id == business_id
    ).count()

    image = BusinessImage(
        business_id=business_id,
        url=f"/static/uploads/{filename}",
        alt_text=file.filename,
        is_logo=is_logo,
        display_order=max_order,
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    return {"url": f"/static/uploads/{filename}", "image_id": str(image.id)}

    
@router.delete("/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business(business_id: uuid.UUID, db: Session=Depends(get_db)):
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Business not found")
    
    db.delete(business)
    db.commit
