import sys
import os
import uuid

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.core.security import get_password_hash
from app.models import (
    Role, User, Category, CraftOrigin, ArtisanProfile, ArtisanApplication
)


def init_db(db: Session) -> None:
    # Create all tables in target database
    Base.metadata.create_all(bind=engine)

    # 1. Seed Roles
    roles = [
        {"code": "ADMIN", "name": "System Administrator", "description": "Platform governance and moderation"},
        {"code": "ARTISAN", "name": "Traditional Artisan", "description": "Craftsperson, weaver, or SHG member"},
        {"code": "RETAIL_BUYER", "name": "Retail Consumer", "description": "Individual marketplace shopper"},
        {"code": "WHOLESALE_BUYER", "name": "B2B / Wholesale Buyer", "description": "Retailer, exporter, or corporate procurement"},
    ]
    role_map = {}
    for r in roles:
        existing = db.query(Role).filter(Role.code == r["code"]).first()
        if not existing:
            role = Role(code=r["code"], name=r["name"], description=r["description"])
            db.add(role)
            db.flush()
            role_map[r["code"]] = role
        else:
            role_map[r["code"]] = existing

    # 2. Seed Default Craft Categories
    categories = [
        {"name": "Handloom & Textiles", "slug": "handloom-textiles", "description": "Authentic handwoven sarees, dupattas, stoles, and organic fabrics"},
        {"name": "Terracotta & Pottery", "slug": "terracotta-pottery", "description": "Clay cookware, decorative earthen lamps, and studio pottery"},
        {"name": "Woodcraft & Toys", "slug": "woodcraft-toys", "description": "Lacquered wooden toys, sandalwood carving, and carved home decor"},
        {"name": "Metal & Brassware", "slug": "metal-brassware", "description": "Lost-wax cast Dhokra, Moradabad brass, and bronze sculptures"},
        {"name": "Cane & Bamboo", "slug": "cane-bamboo", "description": "Eco-friendly baskets, lampshades, and sustainable furniture"},
        {"name": "Traditional Painting", "slug": "traditional-painting", "description": "Madhubani, Tanjore, Pattachitra, and Warli folk paintings"},
    ]
    for c in categories:
        existing = db.query(Category).filter(Category.slug == c["slug"]).first()
        if not existing:
            cat = Category(name=c["name"], slug=c["slug"], description=c["description"])
            db.add(cat)

    # 3. Seed Geographical Indication (GI) Craft Origins
    origins = [
        {"name": "Kanchipuram", "state": "Tamil Nadu", "geographical_indication_code": "GI-001", "history_notes": "Renowned for pure mulberry silk sarees woven with contrast zuri borders."},
        {"name": "Banaras", "state": "Uttar Pradesh", "geographical_indication_code": "GI-002", "history_notes": "Historic weaving center famous for intricate gold and silver brocade work."},
        {"name": "Channapatna", "state": "Karnataka", "geographical_indication_code": "GI-003", "history_notes": "Known as Gombegala Ooru (toy-town), handcrafted using Wrightia tinctoria wood and natural dyes."},
        {"name": "Madhubani", "state": "Bihar", "geographical_indication_code": "GI-004", "history_notes": "Folk art characterized by geometrical patterns created using natural pigments and dyes."},
        {"name": "Bastar Dhokra", "state": "Chhattisgarh", "geographical_indication_code": "GI-005", "history_notes": "Ancient non-ferrous metal casting using the lost-wax technique dating back 4,000 years."},
        {"name": "Jaipur Blue Pottery", "state": "Rajasthan", "geographical_indication_code": "GI-006", "history_notes": "Traditional glaze pottery formulated without clay using Egyptian paste and quartz powder."},
    ]
    for o in origins:
        existing = db.query(CraftOrigin).filter(CraftOrigin.geographical_indication_code == o["geographical_indication_code"]).first()
        if not existing:
            orig = CraftOrigin(
                name=o["name"],
                state=o["state"],
                geographical_indication_code=o["geographical_indication_code"],
                history_notes=o["history_notes"]
            )
            db.add(orig)

    # 4. Seed Administrator User
    admin_email = "admin@craftlens.org"
    admin_user = db.query(User).filter(User.email == admin_email).first()
    if not admin_user:
        admin_user = User(
            email=admin_email,
            full_name="CraftLens Administrator",
            phone="+919876543210",
            hashed_password=get_password_hash("CraftLensAdmin@2026"),
            preferred_language="en",
            is_active=True,
            is_verified=True
        )
        admin_user.roles.append(role_map["ADMIN"])
        db.add(admin_user)

    # 5. Seed Demonstration Artisan User
    artisan_email = "artisan@craftlens.org"
    artisan_user = db.query(User).filter(User.email == artisan_email).first()
    if not artisan_user:
        artisan_user = User(
            email=artisan_email,
            full_name="Meenakshi Ammal",
            phone="+919841012345",
            hashed_password=get_password_hash("Artisan@2026"),
            preferred_language="ta",
            is_active=True,
            is_verified=True
        )
        artisan_user.roles.append(role_map["ARTISAN"])
        db.add(artisan_user)
        db.flush()

        profile = ArtisanProfile(
            user_id=artisan_user.id,
            craft_specialization="Traditional Kanchipuram Silk Weaving",
            bio="Third-generation master weaver specializing in temple border korvai sarees with natural silk.",
            experience_years=24,
            city="Kanchipuram",
            state="Tamil Nadu",
            pincode="631501",
            verification_level="GOVT_ID_VERIFIED"
        )
        db.add(profile)

    db.commit()
    print("Database schema created and initial seed data populated successfully!")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()

