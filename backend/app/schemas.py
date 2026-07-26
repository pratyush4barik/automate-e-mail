from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime


# -------------------------
# Register Request
# -------------------------
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


# -------------------------
# Login Request
# -------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", "password", mode="before")
    @classmethod
    def not_blank(cls, value):
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValueError("Please enter email and password.")
        return value


# -------------------------
# User Response
# -------------------------
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    is_verified: bool
    is_active: bool
    created_at: datetime


# -------------------------
# JWT Token Response
# -------------------------
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# -------------------------
# Generic Message
# -------------------------
class MessageResponse(BaseModel):
    message: str