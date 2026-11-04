import pytest
from app.models import User, ArtisanProfile, Buyer
from app.schemas.user import UserRegister, UserUpdate, PasswordChange
from app.schemas.artisan import ArtisanProfileUpdate, ArtisanVerificationCreate
from app.schemas.buyer import BuyerProfileUpdate, BuyerBusinessProfileUpdate
from app.api.v1.endpoints.auth import register_user
from app.api.v1.endpoints.users import update_user_me, change_user_password
from app.api.v1.endpoints.artisans import get_my_artisan_profile, update_my_artisan_profile, submit_artisan_verification
from app.api.v1.endpoints.buyers import get_my_buyer_profile, update_my_buyer_profile, update_my_business_profile


def test_artisan_profile_and_verification_flow(db):
    # 1. Register new artisan
    reg = register_user(
        user_in=UserRegister(
            email="lakshmi.potter@craftlens.org",
            password="TerracottaCraft#2026",
            full_name="Lakshmi Potter",
            role_code="ARTISAN",
            preferred_language="hi"
        ),
        db=db
    )
    user = db.query(User).filter(User.email == "lakshmi.potter@craftlens.org").first()
    assert user is not None

    # 2. Update artisan profile
    profile_update = ArtisanProfileUpdate(
        craft_specialization="Traditional Terracotta Cookware & Murals",
        bio="Practicing heritage wheel throwing and wood-fired pottery for over 15 years.",
        experience_years=15,
        studio_address="Gram Panchayat, Pottery Lane",
        city="Gorakhpur",
        state="Uttar Pradesh",
        pincode="273001",
        bank_account_configured=True
    )
    res = update_my_artisan_profile(profile_in=profile_update, db=db, current_user=user)
    assert res.success is True
    assert res.data.experience_years == 15
    assert res.data.city == "Gorakhpur"
    assert res.data.bank_account_configured is True

    # 3. Submit verification document
    verif_in = ArtisanVerificationCreate(
        document_type="PEHCHAN_CARD",
        document_number="PEH-UP-123456",
        document_url="https://craftlens-storage.org/docs/pehchan_card.pdf"
    )
    verif_res = submit_artisan_verification(verification_in=verif_in, db=db, current_user=user)
    assert verif_res.success is True
    assert verif_res.data.status == "PENDING"
    assert verif_res.data.document_type == "PEHCHAN_CARD"

    # Verify artisan verification level updated to SUBMITTED
    profile_check = get_my_artisan_profile(db=db, current_user=user)
    assert profile_check.data.verification_level == "SUBMITTED"


def test_buyer_wholesale_profile_flow(db):
    # 1. Register wholesale buyer
    reg = register_user(
        user_in=UserRegister(
            email="procurement@heritageexports.com",
            password="B2BBuyerSecure#123",
            full_name="Rajesh Corporate Buyer",
            role_code="WHOLESALE_BUYER",
            preferred_language="en"
        ),
        db=db
    )
    user = db.query(User).filter(User.email == "procurement@heritageexports.com").first()
    assert user is not None

    # 2. Update buyer addresses
    address_in = BuyerProfileUpdate(
        default_shipping_address={"street": "12 Commercial Blvd", "city": "Mumbai", "pincode": "400001"},
        default_billing_address={"street": "12 Commercial Blvd", "city": "Mumbai", "pincode": "400001"}
    )
    buyer_res = update_my_buyer_profile(profile_in=address_in, db=db, current_user=user)
    assert buyer_res.success is True
    assert buyer_res.data.default_shipping_address["city"] == "Mumbai"

    # 3. Configure B2B business details
    business_in = BuyerBusinessProfileUpdate(
        company_name="Heritage Handicrafts Export Ltd",
        gst_number="27AABCU9603R1ZM",
        pan_number="AABCU9603R",
        website="https://heritageexports.com"
    )
    biz_res = update_my_business_profile(business_in=business_in, db=db, current_user=user)
    assert biz_res.success is True
    assert biz_res.data.company_name == "Heritage Handicrafts Export Ltd"
    assert biz_res.data.gst_number == "27AABCU9603R1ZM"
