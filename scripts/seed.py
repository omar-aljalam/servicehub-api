"""
Populate the database with realistic fake data.
Made using Claude Code
"""
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
import random
from faker import Faker
import bcrypt
from slugify import slugify
from sqlalchemy.orm import Session

from app.database import engine, SessionLocal, Base
from app.models.models import User, Category, Business, BusinessLocation, BusinessImage, BusinessStatus

fake = Faker()

# ─────────────────────────────────────────────────────────────
# SEED DATA CONSTANTS
# ─────────────────────────────────────────────────────────────

CATEGORIES = [
    {"name": "Plumbing", "description": "Pipe installation, repairs, and water systems"},
    {"name": "Electrical", "description": "Wiring, installation, and electrical repairs"},
    {"name": "Home Cleaning", "description": "Residential and commercial cleaning services"},
    {"name": "Landscaping", "description": "Garden design, lawn care, and outdoor maintenance"},
    {"name": "Carpentry", "description": "Furniture, fixtures, and woodworking"},
    {"name": "Painting", "description": "Interior and exterior painting services"},
    {"name": "HVAC", "description": "Heating, ventilation, and air conditioning"},
    {"name": "Moving Services", "description": "Residential and commercial moving and packing"},
]

# Placeholder images from a public source — safe for development use
PLACEHOLDER_LOGO_URLS = [
    "https://placehold.co/200x200/3B82F6/FFFFFF?text=LOGO",
    "https://placehold.co/200x200/10B981/FFFFFF?text=LOGO",
    "https://placehold.co/200x200/8B5CF6/FFFFFF?text=LOGO",
    "https://placehold.co/200x200/F59E0B/FFFFFF?text=LOGO",
    "https://placehold.co/200x200/EF4444/FFFFFF?text=LOGO",
]

PLACEHOLDER_GALLERY_URLS = [
    "https://placehold.co/800x600/CBD5E1/475569?text=Work+Photo",
    "https://placehold.co/800x600/D1FAE5/065F46?text=Work+Photo",
    "https://placehold.co/800x600/EDE9FE/4C1D95?text=Work+Photo",
]

STATUSES = [BusinessStatus.ACTIVE, BusinessStatus.ACTIVE, BusinessStatus.ACTIVE, BusinessStatus.PENDING, BusinessStatus.INACTIVE]
# Weighted: most businesses should be active, some pending, few inactive.


# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────

def make_unique_slug(base: str, existing_slugs: set) -> str:
    """
    Generate a URL slug that doesn't already exist in the DB.
    """
    slug = slugify(base)
    candidate = slug
    counter = 1
    while candidate in existing_slugs:
        candidate = f"{slug}-{counter}"
        counter += 1
    existing_slugs.add(candidate)
    return candidate


def create_categories(db: Session) -> list[Category]:
    """Insert all service categories."""
    categories = []
    slugs = set()
    for cat_data in CATEGORIES:
        slug = make_unique_slug(cat_data["name"], slugs)
        category = Category(
            id=uuid.uuid4(),
            name=cat_data["name"],
            slug=slug,
            description=cat_data["description"],
        )
        db.add(category)
        categories.append(category)
    db.commit()
    print(f"  ✓ Created {len(categories)} categories")
    return categories


def create_users(db: Session, count: int = 10) -> list[User]:
    """
    Insert fake users with hashed passwords.
    """
    users = []
    password = "password123".encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password, salt).decode("utf-8")
    for _ in range(count):
        user = User(
            id=uuid.uuid4(),
            email=fake.unique.email(),
            password_hash=hashed_pw,
            full_name=fake.name(),
        )
        db.add(user)
        users.append(user)
    db.commit()
    print(f"  ✓ Created {len(users)} users (password: 'password123' for all)")
    return users


def create_businesses(
    db: Session,
    users: list[User],
    categories: list[Category],
    count: int = 30
) -> list[Business]:
    """
    Insert fake businesses with locations and images.
    """
    businesses = []
    slugs = set()

    for _ in range(count):
        owner = random.choice(users)
        category = random.choice(categories)
        business_name = fake.company()
        slug = make_unique_slug(business_name, slugs)

        business = Business(
            id=uuid.uuid4(),
            owner_id=owner.id,
            category_id=category.id,
            name=business_name,
            slug=slug,
            description=fake.paragraph(nb_sentences=3),
            phone=fake.phone_number()[:20],  # truncate to column length
            email=fake.company_email(),
            website=fake.url(),
            status=random.choice(STATUSES),
        )
        db.add(business)
        db.flush()

        # Primary location
        location = BusinessLocation(
            id=uuid.uuid4(),
            business_id=business.id,
            street=fake.street_address(),
            city=fake.city(),
            country=fake.country(),
            postal_code=fake.postcode(),
            latitude=float(fake.latitude()),
            longitude=float(fake.longitude()),
            is_primary=True,
        )
        db.add(location)

        # Logo image
        logo = BusinessImage(
            id=uuid.uuid4(),
            business_id=business.id,
            url=random.choice(PLACEHOLDER_LOGO_URLS),
            alt_text=f"{business_name} logo",
            is_logo=True,
            display_order=0,
        )
        db.add(logo)

        # 0-3 gallery images (random)
        gallery_count = random.randint(0, 3)
        for j in range(gallery_count):
            gallery_img = BusinessImage(
                id=uuid.uuid4(),
                business_id=business.id,
                url=random.choice(PLACEHOLDER_GALLERY_URLS),
                alt_text=f"{business_name} work photo {j + 1}",
                is_logo=False,
                display_order=j + 1,
            )
            db.add(gallery_img)

        db.commit()
        businesses.append(business)

    print(f"  ✓ Created {len(businesses)} businesses with locations and images")
    return businesses


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def seed():
    print("\n=== Marketplace DB Seeder ===\n")
    print(f"HELO THIS IS: {engine}")
    print("Step 1: Dropping and recreating all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("  ✓ Tables created\n")

    db = SessionLocal()
    try:
        print("Step 2: Seeding categories...")
        categories = create_categories(db)

        print("\nStep 3: Seeding users...")
        users = create_users(db, count=10)

        print("\nStep 4: Seeding businesses...")
        businesses = create_businesses(db, users, categories, count=30)

        print("\n=== Done ===")
        print(f"  {len(categories)} categories")
        print(f"  {len(users)} users")
        print(f"  {len(businesses)} businesses")
        print("\nAll users have password: password123")

    except Exception as e:
        db.rollback()
        print(f"\nError during seeding: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
