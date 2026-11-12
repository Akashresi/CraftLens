import pytest
from fastapi.security import OAuth2PasswordRequestForm

from app.api.v1.endpoints.auth import get_current_user_profile, register_user
from app.api.v1.endpoints.health import health_check
from app.core.security import create_access_token, decode_token, get_password_hash, verify_password
from app.models import ArtisanProfile, Category, CraftOrigin, Role, User
from app.schemas.user import UserLogin, UserRegister


def test_password_hashing_argon2id():
    """Verify Argon2id memory-hard hashing algorithm and verification."""
    password = "SuperSecretArtisanPassword#2026"
    hashed = get_password_hash(password)
    assert hashed.startswith("$argon2id$")
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_jwt_token_generation_and_decode():
    """Verify JWT access and refresh token lifecycle."""
    user_id = "test-artisan-uuid-1234"
    access_token = create_access_token(subject=user_id)
    assert access_token is not None
    payload = decode_token(access_token)
    assert payload is not None
    assert payload["sub"] == user_id
    assert payload["type"] == "access"


def test_health_check_endpoint(db):
    """Verify health endpoint database query and response schema."""
    response = health_check(db=db)
    assert response.status == "ok"
    assert response.version == "2.0.0"
    assert response.database_connected is True
    assert response.ai_service_available is True


def test_seeded_data(db):
    """Verify initial database seed contains all 4 core roles, categories, and GI origins."""
    roles = db.query(Role).all()
    assert len(roles) >= 4
    role_codes = {r.code for r in roles}
    assert {"ADMIN", "ARTISAN", "RETAIL_BUYER", "WHOLESALE_BUYER"}.issubset(role_codes)

    categories = db.query(Category).all()
    assert len(categories) >= 6

    origins = db.query(CraftOrigin).all()
    assert len(origins) >= 6


def test_user_registration_and_profile_flow(db):
    """Verify registration defaults to RETAIL_BUYER, Argon2id storage, and profile access."""
    register_in = UserRegister(
        email="ramu.buyer@craftlens.org",
        phone="+919841234567",
        password="WeaverPassword#123",
        full_name="Ramu Buyer",
        preferred_language="ta",
    )
    reg_response = register_user(user_in=register_in, db=db)
    assert reg_response.success is True
    user_data = reg_response.data
    assert user_data.email == "ramu.buyer@craftlens.org"
    assert user_data.full_name == "Ramu Buyer"
    assert any(r.code == "RETAIL_BUYER" for r in user_data.roles)

    # Verify buyer profile created in database
    created_user = db.query(User).filter(User.email == "ramu.buyer@craftlens.org").first()
    assert created_user is not None
    assert created_user.buyer_profile is not None

    # Test get profile
    profile_response = get_current_user_profile(current_user=created_user)
    assert profile_response.success is True
    assert profile_response.data.id == created_user.id
