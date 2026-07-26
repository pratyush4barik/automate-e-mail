from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from player import player, is_paused    
import vlc
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from starlette.requests import Request

from database import get_db
from models import GoogleUser, User
from schemas import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse
)
from security import (
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


@router.post("/toggle")
def toggle():
    global is_paused
    state = player.get_state()
    if state in [
        vlc.State.NothingSpecial,
        vlc.State.Stopped,
        vlc.State.Ended
    ]:
        player.play()
        is_paused = False
        
    elif state == vlc.State.Playing:
        player.pause()
        is_paused = True
        
    elif state == vlc.State.Paused:
        player.pause()
        is_paused = False

    return {
        "playing" : not is_paused
    }

@router.post("/forward")
def forward():
    current = player.get_time()
    player.set_time(current + 5000)
    return {"success": True}

@router.post("/backward")
def backward():
    current = player.get_time()
    player.set_time(current - 5000)
    return {"success": True}

@router.post("/stop")
def stop():
    player.stop()
    return {"success": True}

oauth = OAuth()

from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    },
)

@router.get("/google/login")
async def google_login(request: Request):

    redirect_uri = request.url_for("google_callback")

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    token = await oauth.google.authorize_access_token(request)

    user_info = token["userinfo"]

    google_id = user_info["sub"]
    email = user_info["email"]
    name = user_info["name"]
    picture = user_info["picture"]

    # Write the login flow here
    user = db.query(GoogleUser).filter(
        GoogleUser.google_id == google_id
    ).first()

    if not user:
        user = GoogleUser(
            google_id=google_id,
            email=email,
            name=name,
            profile_picture=picture,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    jwt = create_access_token(
        data={"sub": str(user.id)}

    )

    return RedirectResponse(
        f"https://tiny-root-360385.framer.app"
    )
