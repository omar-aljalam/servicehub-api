import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import (
    String, Boolean, Float, Integer,
    ForeignKey, Text, DateTime, func
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional

from app.database import Base

class BusinessStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    BANNED = "banned"

class User(Base):
    """
    User model representing a user in the system.
    It is connected with the Business model through a one-to-many relationship, where one user can own multiple businesses.
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID]= mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default= lambda: datetime.now(timezone.utc)
        )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
        )
    businesses: Mapped[List["Business"]] = relationship(back_populates="owner")

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default= lambda: datetime.now(timezone.utc)    )

    businesses: Mapped[List["Business"]] = relationship(back_populates="category")

class Business(Base):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id",ondelete="CASCADE")
    )
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL")
    )

    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    email: Mapped[Optional[str]] = mapped_column(String(255))
    website: Mapped[Optional[str]] = mapped_column(String(500))

    status: Mapped[BusinessStatus] = mapped_column(default=BusinessStatus.PENDING)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default= lambda: datetime.now(timezone.utc)
        )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
        )
    
    owner: Mapped["User"] = relationship(back_populates="businesses")
    category: Mapped[Optional["Category"]] = relationship(back_populates="businesses")
    locations: Mapped[List["BusinessLocation"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan"
    )

    images: Mapped[List["BusinessImage"]] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        order_by="BusinessImage.display_order"
    )
class BusinessLocation(Base):
    __tablename__ = "business_locations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True
    )
    street: Mapped[Optional[str]] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100), index=True)
    country: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[Optional[str]] = mapped_column(String(20))
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)

    business: Mapped["Business"] = relationship(back_populates="locations")

class BusinessImage(Base):
    __tablename__= "business_images"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, server_default=func.gen_random_uuid())
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True
    )
    url: Mapped[str] = mapped_column(String(1000))
    alt_text: Mapped[Optional[str]] = mapped_column(String(255))
    is_logo: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc)
    )

    business: Mapped["Business"] = relationship(back_populates="images")