from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from database.database import Base
import uuid
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = Column(
        String(255),
        nullable=False
    )

    is_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    otp = Column(
        String(6),
        nullable=True
    )

    otp_expires_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    def __repr__(self):
        return f"<User(email='{self.email}')>"
    
class GoogleUser(Base):
    __tablename__ = "google_users"

    id = Column(Integer, primary_key=True, index=True)

    google_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)

    profile_picture = Column(String)
    verified_email = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)

class UserDetails(Base):
    __tablename__ = "user_details"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    college = Column(String, nullable=True)
    degree = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    resume_link = Column(String, nullable=True)
    github_link = Column(String, nullable=True)
    linkedin_link = Column(String, nullable=True)
    drive_link = Column(String, nullable=True)
    roll_number = Column(String, nullable=True)
    year = Column(String, nullable=True)
    cgpa = Column(Float, nullable=True)
    skills = Column(String, nullable=True)
    projects = Column(String, nullable=True)
    research_interests = Column(String, nullable=True)

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    subject = Column(String, nullable=True)
    body = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
