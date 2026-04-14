from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    
    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category name cannot be blank")
        return v.strip()
    

class CategoryResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v
    

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LocationCreate(BaseModel):
    street: Optional[str] = None
    city: str
    country: str
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_primary: bool = True

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v):
        if v is not None and not (-90 <= v <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v):
        if v is not None and not (-180 <= v <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return v
    
class LocationResponse(BaseModel):
    id: UUID
    street: Optional[str] = None
    city: str
    country: str
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_primary: bool = True

    model_config = ConfigDict(from_attributes=True)


class ImageResponse(BaseModel):
    id: UUID
    url: str
    alt_text: Optional[str]
    is_logo: bool
    display_order: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BusinessCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    location: Optional[LocationCreate] = None

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Business name cannot be blank")
        return v.strip()

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[UUID] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    location: Optional[LocationCreate] = None

class BusinessResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    status: str
    category: Optional[CategoryResponse]
    locations: list[LocationResponse]
    images: list[ImageResponse]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BusinessListResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    status: str
    category: Optional[CategoryResponse]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
