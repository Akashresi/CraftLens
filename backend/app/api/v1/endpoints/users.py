from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.core.security import get_password_hash, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas.common import APIResponse
from app.schemas.user import PasswordChange, UserOut, UserUpdate

router = APIRouter()


@router.get("/me", response_model=APIResponse[UserOut])
def get_user_me(current_user: User = Depends(get_current_active_user)):
    """Returns the current authenticated user's profile."""
    return APIResponse(
        success=True,
        message="User profile retrieved",
        data=UserOut.model_validate(current_user),
    )


@router.put("/me", response_model=APIResponse[UserOut])
def update_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Updates basic personal details and preferred regional language."""
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.phone is not None:
        current_user.phone = user_in.phone
    if user_in.preferred_language is not None:
        current_user.preferred_language = user_in.preferred_language

    db.commit()
    db.refresh(current_user)

    return APIResponse(
        success=True,
        message="Profile updated successfully",
        data=UserOut.model_validate(current_user),
    )


@router.put("/me/password", response_model=APIResponse[bool])
def change_user_password(
    password_in: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Changes password after verifying existing Argon2id hash."""
    if not verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password verification failed",
        )

    current_user.hashed_password = get_password_hash(password_in.new_password)
    db.commit()

    return APIResponse(
        success=True,
        message="Password changed successfully",
        data=True,
    )
