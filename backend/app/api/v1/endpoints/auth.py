from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models import User, Role, ArtisanProfile, Buyer
from app.schemas.user import UserRegister, UserLogin, Token, UserOut
from app.schemas.common import APIResponse
from app.api.deps import get_current_active_user

router = APIRouter()


@router.post("/register", response_model=APIResponse[UserOut])
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    """Registers a new user (Artisan, Retail Buyer, or Wholesale Buyer) with Argon2id password hashing."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists",
        )

    # Resolve assigned role - public registration is strictly for buyers
    requested_role = (user_in.role_code or "RETAIL_BUYER").upper().strip()
    if requested_role in ["ARTISAN", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selecting ARTISAN or ADMIN role during registration is not permitted. Please register as a buyer and apply to become an artisan in your profile.",
        )
    if requested_role != "WHOLESALE_BUYER":
        requested_role = "RETAIL_BUYER"

    role = db.query(Role).filter(Role.code == requested_role).first()
    if not role:
        role = db.query(Role).filter(Role.code == "RETAIL_BUYER").first()

    new_user = User(
        email=user_in.email,
        phone=user_in.phone,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        preferred_language=user_in.preferred_language,
        is_active=True,
        is_verified=False,
    )
    if role:
        new_user.roles.append(role)
    db.add(new_user)
    db.flush()

    # Automatically create buyer profile
    buyer_profile = Buyer(
        user_id=new_user.id,
        buyer_type="WHOLESALE" if role and role.code == "WHOLESALE_BUYER" else "RETAIL",
    )
    db.add(buyer_profile)

    db.commit()
    db.refresh(new_user)

    return APIResponse(
        success=True,
        message="User account registered successfully",
        data=UserOut.model_validate(new_user),
    )


@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Standard OAuth2 password flow login."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account"
        )

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=Token)
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """Rotates refresh token and issues a new access token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    new_access_token = create_access_token(subject=user.id)
    new_refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=APIResponse[UserOut])
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Returns currently authenticated user profile and roles."""
    return APIResponse(
        success=True,
        message="Profile retrieved successfully",
        data=UserOut.model_validate(current_user),
    )

