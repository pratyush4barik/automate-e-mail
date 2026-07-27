from fastapi import APIRouter, Depends, HTTPException, Request, status
from dotenv import load_dotenv
import os
from authlib.integrations.starlette_client import OAuth
from starlette.requests import Request
from database.database import get_db
from database.models import GoogleUser
from security.security import create_access_token
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse


load_dotenv()
oauth = OAuth()

router = APIRouter()


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
#login route for google auth
@router.get("/login")
async def google_login(request: Request):

    redirect_uri = request.url_for("google_callback")

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )

#login callback route for google auth
@router.get("/callback")
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
