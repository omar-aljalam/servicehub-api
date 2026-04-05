import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Float, Integer,
    ForeignKey, Text, DateTime, Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database import Base


class User(Base):
    """
    User model representing a user in the system.
    It is connected with the Business model through a one-to-many relationship, where one user can own multiple businesses.
    """

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)

    created_at = Column(
        DateTime,
        default= lambda: datetime.now(timezone.utc),
        nullable=False
        )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
        )
    businesses = relationship("Business", back_populates="owner")

#TODO
class Category(Base):
    pass

class Business(Base):
    pass

class BusinessLocation(Base):
    pass

class BusinessImage(Base):
    pass
