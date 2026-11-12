from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str


class UserRegister(BaseModel):
    email: EmailStr
    phone: str | None = None
    password: str = Field(..., min_length=6)
    full_name: str
    role_code: str = Field(
        default="RETAIL_BUYER",
        description="RETAIL_BUYER or WHOLESALE_BUYER (ARTISAN and ADMIN cannot be chosen at registration)",
    )
    preferred_language: str = Field(default="ta", description="ta, hi, en, te, kn, ml")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    preferred_language: str | None = Field(None, description="ta, hi, en, te, kn, ml")


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None
    type: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    phone: str | None = None
    full_name: str
    preferred_language: str
    is_active: bool
    is_verified: bool
    roles: list[RoleOut] = []
    created_at: datetime
