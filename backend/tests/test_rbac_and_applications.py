import pytest
from fastapi import HTTPException

from app.api.deps import require_role
from app.api.v1.endpoints.artisan_applications import (
    approve_artisan_application,
    get_my_artisan_application,
    list_artisan_applications_admin,
    reject_artisan_application,
    submit_artisan_application,
)
from app.api.v1.endpoints.auth import register_user
from app.api.v1.endpoints.pricing import calculate_price_breakdown
from app.models import ArtisanApplication, ArtisanProfile, AuditLog, Buyer, Role, User
from app.schemas.artisan_application import ArtisanApplicationCreate, ArtisanApplicationReviewIn
from app.schemas.pricing import PricingCalculateIn
from app.schemas.user import UserRegister


def test_1_buyer_registration_defaults_to_retail_buyer(db):
    """Test 1: Buyer registration defaults to RETAIL_BUYER role."""
    reg = register_user(
        user_in=UserRegister(
            email="retail.buyer1@craftlens.org",
            password="SecurePassword#2026",
            full_name="Priya Sharma",
            phone="+919811122233",
            preferred_language="en",
        ),
        db=db,
    )
    assert reg.success is True
    user = db.query(User).filter(User.email == "retail.buyer1@craftlens.org").first()
    assert user is not None
    assert len(user.roles) == 1
    assert user.roles[0].code == "RETAIL_BUYER"

    # Verify Buyer profile is created
    buyer = db.query(Buyer).filter(Buyer.user_id == user.id).first()
    assert buyer is not None


def test_2_public_registration_blocks_artisan_and_admin(db):
    """Test 2: Public registration fails with 400 when attempting to register as ARTISAN or ADMIN."""
    # Attempting ARTISAN
    with pytest.raises(HTTPException) as exc_info_artisan:
        register_user(
            user_in=UserRegister(
                email="hacker.artisan@craftlens.org",
                password="SecurePassword#2026",
                full_name="Fake Artisan",
                role_code="ARTISAN",
            ),
            db=db,
        )
    assert exc_info_artisan.value.status_code == 400
    assert "Selecting ARTISAN or ADMIN role during registration is not permitted" in exc_info_artisan.value.detail

    # Attempting ADMIN
    with pytest.raises(HTTPException) as exc_info_admin:
        register_user(
            user_in=UserRegister(
                email="hacker.admin@craftlens.org",
                password="SecurePassword#2026",
                full_name="Fake Admin",
                role_code="ADMIN",
            ),
            db=db,
        )
    assert exc_info_admin.value.status_code == 400


def test_3_buyer_submits_artisan_application(db):
    """Test 3: Buyer submits an artisan application and it is saved with PENDING status."""
    reg = register_user(
        user_in=UserRegister(
            email="artisan.applicant@craftlens.org",
            password="SecurePassword#2026",
            full_name="Ramesh Channapatna",
            phone="+919845012345",
        ),
        db=db,
    )
    user = db.query(User).filter(User.email == "artisan.applicant@craftlens.org").first()

    app_in = ArtisanApplicationCreate(
        full_name="Ramesh Channapatna",
        craft_specialization="Channapatna Wooden Toys & Lacquerware",
        experience_years=8,
        city="Ramanagara",
        state="Karnataka",
        portfolio_url="https://craftlens.org/ramesh-portfolio",
        craft_description="Specialist in non-toxic vegetable-dyed turnwood lacquer toys.",
        supporting_documents_url="https://craftlens-storage.org/docs/artisan_card.pdf",
    )

    res = submit_artisan_application(app_in=app_in, db=db, current_user=user)
    assert res.success is True
    assert res.data.status == "PENDING"
    assert res.data.craft_specialization == "Channapatna Wooden Toys & Lacquerware"
    assert res.data.experience_years == 8

    # Query application via GET /me
    my_app = get_my_artisan_application(db=db, current_user=user)
    assert my_app.success is True
    assert my_app.data.status == "PENDING"
    assert my_app.data.full_name == "Ramesh Channapatna"


def test_4_duplicate_pending_application_prevented(db):
    """Test 4: Submitting another application while one is PENDING raises 400."""
    user = db.query(User).filter(User.email == "artisan.applicant@craftlens.org").first()
    app_in = ArtisanApplicationCreate(
        full_name="Ramesh Duplicate",
        craft_specialization="Channapatna Wooden Toys",
        experience_years=9,
        city="Ramanagara",
        state="Karnataka",
        craft_description="Second application attempt.",
    )
    with pytest.raises(HTTPException) as exc_info:
        submit_artisan_application(app_in=app_in, db=db, current_user=user)
    assert exc_info.value.status_code == 400
    assert "already have a pending artisan application" in exc_info.value.detail


def test_5_submitting_application_does_not_grant_artisan_role(db):
    """Test 5: Submitting application leaves buyer role unchanged."""
    user = db.query(User).filter(User.email == "artisan.applicant@craftlens.org").first()
    db.refresh(user)
    role_codes = [r.code for r in user.roles]
    assert "ARTISAN" not in role_codes
    assert "RETAIL_BUYER" in role_codes


def test_6_buyer_cannot_access_artisan_endpoints(db):
    """Test 6: Buyer cannot access artisan endpoints (e.g. Pricing calculate or Studio)."""
    user = db.query(User).filter(User.email == "artisan.applicant@craftlens.org").first()

    # Direct require_role check raises 403
    artisan_guard = require_role("ARTISAN")
    with pytest.raises(HTTPException) as exc_guard:
        artisan_guard(user)
    assert exc_guard.value.status_code == 403
    assert "ARTISAN" in exc_guard.value.detail

    # Attempting to call Pricing calculate as buyer
    pricing_in = PricingCalculateIn(
        material_cost=300.0, labor_hours=4.0, labor_hourly_rate=150.0, packaging_cost=50.0, transportation_cost=80.0
    )
    with pytest.raises(HTTPException) as exc_pricing:
        calculate_price_breakdown(pricing_in=pricing_in, db=db, current_user=user)
    assert exc_pricing.value.status_code == 403
    assert "ARTISAN" in exc_pricing.value.detail


def test_7_non_admin_cannot_review_applications(db):
    """Test 7: Regular buyer or artisan cannot list or approve artisan applications."""
    buyer_user = db.query(User).filter(User.email == "artisan.applicant@craftlens.org").first()

    # Buyer attempts to list admin applications
    with pytest.raises(HTTPException) as exc_list:
        list_artisan_applications_admin(db=db, current_user=buyer_user)
    assert exc_list.value.status_code == 403
    assert "ADMIN" in exc_list.value.detail

    # Buyer attempts to approve
    app_record = db.query(ArtisanApplication).filter(ArtisanApplication.user_id == buyer_user.id).first()
    with pytest.raises(HTTPException) as exc_app:
        approve_artisan_application(
            application_id=app_record.id,
            review_in=ArtisanApplicationReviewIn(reviewer_notes="Self approval attempt"),
            db=db,
            current_user=buyer_user,
        )
    assert exc_app.value.status_code == 403


def test_8_admin_can_list_and_filter_applications(db):
    """Test 8: Admin can view applications and filter by PENDING."""
    admin_user = db.query(User).filter(User.email == "admin@craftlens.org").first()
    assert admin_user is not None

    res = list_artisan_applications_admin(status_filter="PENDING", db=db, current_user=admin_user)
    assert res.success is True
    assert len(res.data) >= 1
    found = any(a.full_name == "Ramesh Channapatna" for a in res.data)
    assert found is True


def test_9_admin_approves_application_and_role_converts(db):
    """Test 9: Admin approves application -> status becomes APPROVED, user role converts to ARTISAN, ArtisanProfile is created."""
    admin_user = db.query(User).filter(User.email == "admin@craftlens.org").first()
    applicant = db.query(User).filter(User.email == "artisan.applicant@craftlens.org").first()
    app_record = db.query(ArtisanApplication).filter(ArtisanApplication.user_id == applicant.id).first()

    res = approve_artisan_application(
        application_id=app_record.id,
        review_in=ArtisanApplicationReviewIn(reviewer_notes="Authentic GI craft verified. Approved."),
        db=db,
        current_user=admin_user,
    )
    assert res.success is True
    assert res.data.status == "APPROVED"
    assert res.data.reviewed_by_user_id == admin_user.id
    assert res.data.reviewer_notes == "Authentic GI craft verified. Approved."

    # Verify applicant's role changed to ARTISAN
    db.refresh(applicant)
    role_codes = [r.code for r in applicant.roles]
    assert "ARTISAN" in role_codes
    assert "RETAIL_BUYER" not in role_codes

    # Verify ArtisanProfile was created with application details
    profile = db.query(ArtisanProfile).filter(ArtisanProfile.user_id == applicant.id).first()
    assert profile is not None
    assert profile.craft_specialization == "Channapatna Wooden Toys & Lacquerware"
    assert profile.experience_years == 8
    assert profile.city == "Ramanagara"
    assert profile.state == "Karnataka"

    # Verify AuditLog created
    audit = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == admin_user.id, AuditLog.action == "ARTISAN_APPLICATION_APPROVED")
        .first()
    )
    assert audit is not None


def test_10_approved_artisan_can_now_access_artisan_endpoints(db):
    """Test 10: Approved user can now access protected artisan endpoints."""
    artisan_user = db.query(User).filter(User.email == "artisan.applicant@craftlens.org").first()

    # Guard passes
    artisan_guard = require_role("ARTISAN")
    guarded_user = artisan_guard(artisan_user)
    assert guarded_user.id == artisan_user.id

    # Can access pricing
    pricing_in = PricingCalculateIn(
        material_cost=300.0, labor_hours=4.0, labor_hourly_rate=150.0, packaging_cost=50.0, transportation_cost=80.0
    )
    pricing_res = calculate_price_breakdown(pricing_in=pricing_in, db=db, current_user=artisan_user)
    assert pricing_res.success is True
    assert pricing_res.data.total_production_cost > 0


def test_11_admin_rejects_application_and_buyer_retains_role(db):
    """Test 11: Admin rejects application -> status is REJECTED, user retains Buyer role."""
    # Register another buyer
    reg = register_user(
        user_in=UserRegister(
            email="rejected.applicant@craftlens.org",
            password="SecurePassword#2026",
            full_name="Kavita Devi",
            phone="+919877788899",
        ),
        db=db,
    )
    applicant = db.query(User).filter(User.email == "rejected.applicant@craftlens.org").first()

    # Submit application
    app_in = ArtisanApplicationCreate(
        full_name="Kavita Devi",
        craft_specialization="General Souvenirs",
        experience_years=1,
        city="Patna",
        state="Bihar",
        craft_description="Handicrafts without verified traditional lineage.",
    )
    submit_artisan_application(app_in=app_in, db=db, current_user=applicant)
    app_record = db.query(ArtisanApplication).filter(ArtisanApplication.user_id == applicant.id).first()

    # Admin rejects
    admin_user = db.query(User).filter(User.email == "admin@craftlens.org").first()
    res = reject_artisan_application(
        application_id=app_record.id,
        review_in=ArtisanApplicationReviewIn(
            reviewer_notes="Ineligible craft. Requires authentic craft documentation."
        ),
        db=db,
        current_user=admin_user,
    )
    assert res.success is True
    assert res.data.status == "REJECTED"

    # User retains Buyer role
    db.refresh(applicant)
    role_codes = [r.code for r in applicant.roles]
    assert "RETAIL_BUYER" in role_codes
    assert "ARTISAN" not in role_codes

    # Audit log check
    audit = (
        db.query(AuditLog)
        .filter(AuditLog.user_id == admin_user.id, AuditLog.action == "ARTISAN_APPLICATION_REJECTED")
        .first()
    )
    assert audit is not None


def test_12_rejection_allows_reapplication(db):
    """Test 12: Rejected buyer can submit a new artisan application."""
    applicant = db.query(User).filter(User.email == "rejected.applicant@craftlens.org").first()

    new_app = ArtisanApplicationCreate(
        full_name="Kavita Devi",
        craft_specialization="Madhubani Folk Painting",
        experience_years=3,
        city="Madhubani",
        state="Bihar",
        craft_description="Studied under master artisan with authentic Mithila folk art certification.",
    )
    res = submit_artisan_application(app_in=new_app, db=db, current_user=applicant)
    assert res.success is True
    assert res.data.status == "PENDING"
    assert res.data.craft_specialization == "Madhubani Folk Painting"
