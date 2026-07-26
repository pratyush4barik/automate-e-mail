from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from backend.app.database.database import Base, engine
from routers.auth import router as auth_router
from backend.app.routers.otp import router as otp_router
from routers.google_auth import router as google_auth_router
from routers.music import router as music_router

# Import models so SQLAlchemy knows about them
import backend.app.database.models as models
import os

from dotenv import load_dotenv

load_dotenv()


# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Automation API",
    version="1.0.0",
    description="Backend API for the Automation Platform"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY")
)

@app.exception_handler(RequestValidationError)
async def login_validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path == "/auth/login":
        return JSONResponse(
            status_code=400,
            content={"detail": "Please enter email and password."},
        )

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# -----------------------------
# CORS Configuration
# -----------------------------
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://tiny-root-360385.framer.app/login"
    # "https://your-project.framer.website",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def root():
    return {
        "message": "Automation API is running 🚀"
    }

# -----------------------------
# Health Check
# -----------------------------
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

# -----------------------------
# Register Routers
# -----------------------------
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

app.include_router(
    otp_router,
    prefix="/otp",
    tags=["OTP"]
)

app.include_router(
    google_auth_router,
    prefix="/google",
    tags=["Google Authentication"]
)

app.include_router(
    music_router,
    prefix="/music",
    tags=["Music"]
)