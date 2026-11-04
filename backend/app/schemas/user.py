from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str


class UserRegister(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., min_length=6)
    full_name: str
    role_code: str = Field(default="ARTISAN", description="ARTISAN, RETAIL_BUYER, or WHOLESALE_BUYER")
    preferred_language: str = Field(default="ta", description="ta, hi, en, te, kn, ml")


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    preferred_language: Optional[str] = Field(None, description="ta, hi, en, te, kn, ml")


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    phone: Optional[str] = None
    full_name: str
    preferred_language: str
    is_active: bool
    is_verified: bool
    roles: List[RoleOut] = []
    created_at: datetime
