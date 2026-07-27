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


# -------------------------
# UserDetails Schemas
# -------------------------
class UserDetailsBase(BaseModel):
    name: str | None = None
    college: str | None = None
    degree: str | None = None
    branch: str | None = None
    resume_link: str | None = None
    github_link: str | None = None
    linkedin_link: str | None = None
    drive_link: str | None = None
    roll_number: str | None = None
    year: str | None = None
    cgpa: float | None = None
    skills: list[str] | None = None
    projects: list[str] | None = None
    research_interests: list[str] | None = None


class UserDetailsCreate(UserDetailsBase):
    name: str


class UserDetailsUpdate(BaseModel):
    name: str | None = None
    college: str | None = None
    degree: str | None = None
    branch: str | None = None
    resume_link: str | None = None
    github_link: str | None = None
    linkedin_link: str | None = None
    drive_link: str | None = None
    roll_number: str | None = None
    year: str | None = None
    cgpa: float | None = None
    skills: list[str] | None = None
    projects: list[str] | None = None
    research_interests: list[str] | None = None


class UserDetailsResponse(UserDetailsBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    skills: list[str] = []
    projects: list[str] = []
    research_interests: list[str] = []

class EmailBase(BaseModel):
    chat_id: int
    email: EmailStr
    subject: str | None = None
    body: str | None = None


class EmailCreate(EmailBase):
    pass


class EmailUpdate(BaseModel):
    email: EmailStr | None = None
    subject: str | None = None
    body: str | None = None


class EmailResponse(EmailBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime