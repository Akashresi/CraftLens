import secrets
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Body, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.config import settings
from app.core.rate_limit import rate_limit
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.core.upload_security import sanitize_text
from app.db.session import get_db
from app.models import AuditLog, Buyer, Role, User
from app.schemas.common import APIResponse
from app.schemas.user import Token, UserOut, UserRegister

router = APIRouter()


@router.get("/csrf-token", response_model=APIResponse[dict[str, str]])
def issue_csrf_token(response: Response):
    """Issues a double-submit CSRF cookie and matching token for browser cookie flows."""
    token = secrets.token_urlsafe(32)
    response.set_cookie(
        key="craftlens_csrf",
        value=token,
        httponly=False,
        samesite="lax",
        secure=settings.APP_ENV.lower() == "production",
    )
    return APIResponse(success=True, message="CSRF token issued", data={"csrf_token": token})


@router.post(
    "/register",
    response_model=APIResponse[UserOut],
    dependencies=[Depends(rate_limit("auth_register", max_requests=15, window_seconds=60))],
)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    """Registers a new buyer account (RETAIL_BUYER or WHOLESALE_BUYER) with Argon2id hashing."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists",
        )

    requested_role = (user_in.role_code or "RETAIL_BUYER").upper().strip()
    if requested_role in ["ARTISAN", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selecting ARTISAN or ADMIN role during registration is not permitted. Please register as a buyer and apply to become an artisan in your profile.",
        )

    if requested_role not in ["RETAIL_BUYER", "WHOLESALE_BUYER"]:
        requested_role = "RETAIL_BUYER"

    role = db.query(Role).filter(Role.code == requested_role).first()
    if not role:
        role = db.query(Role).filter(Role.code == "RETAIL_BUYER").first()

    clean_name = sanitize_text(user_in.full_name) or user_in.full_name
    new_user = User(
        email=user_in.email,
        phone=user_in.phone,
        full_name=clean_name,
        preferred_language=user_in.preferred_language,
        hashed_password=get_password_hash(user_in.password),
        is_active=True,
        is_verified=False,
    )
    if role:
        new_user.roles.append(role)

    db.add(new_user)
    db.flush()

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


@router.post(
    "/login",
    response_model=Token,
    dependencies=[Depends(rate_limit("auth_login", max_requests=20, window_seconds=60))],
)
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Standard OAuth2 password flow login with brute-force account lockout."""
    user = db.query(User).filter(User.email == form_data.username).first()
    now = datetime.now(UTC)

    if user and user.locked_until is not None:
        locked_until = user.locked_until
        if locked_until.tzinfo is None:
            locked_until = locked_until.replace(tzinfo=UTC)
        if locked_until > now:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account temporarily locked due to repeated failed login attempts. Try again later.",
            )

    if not user or not verify_password(form_data.password, user.hashed_password):
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                user.locked_until = now + timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
                ip = request.client.host if request.client else "unknown"
                db.add(
                    AuditLog(
                        user_id=user.id,
                        action="ACCOUNT_LOCKED",
                        resource=f"user:{user.id}",
                        ip_address=ip,
                        details={"failed_attempts": user.failed_login_attempts},
                    )
                )
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")

    if user.failed_login_attempts > 0 or user.locked_until is not None:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

    access_token = create_access_token(subject=user.id)
    refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


class RefreshTokenIn(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=Token)
def refresh_access_token(
    body: RefreshTokenIn | None = Body(default=None),
    refresh_token: str | None = None,
    db: Session = Depends(get_db),
):
    """Rotates refresh token and issues a new access token."""
    raw_token = body.refresh_token if body else refresh_token
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="refresh_token is required",
        )
    payload = decode_token(raw_token)
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
