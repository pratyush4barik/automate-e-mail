from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request
from database.database import get_db
from database.models import User
from database.schemas import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)
from security.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token
)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ==========================================================
# Register
# ==========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == request.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered."
        )

    new_user = User(
        full_name=request.full_name,
        email=request.email,
        password_hash=hash_password(request.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ==========================================================
# Login
# ==========================================================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    if not verify_password(
        request.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ==========================================================
# Get Current User
# ==========================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = verify_access_token(token)

    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")

    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        raise credentials_exception

    return user


# ==========================================================
# Current User
# ==========================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):

    return current_user



