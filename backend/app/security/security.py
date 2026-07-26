from datetime import datetime, timedelta, timezone
import hashlib
import bcrypt
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60)
)


# -----------------------------
# Password Hashing
# -----------------------------
def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    password_digest = hashlib.sha256(password_bytes).digest()
    hashed_password = bcrypt.hashpw(password_digest, bcrypt.gensalt())
    return hashed_password.decode("utf-8")


# -----------------------------
# Password Verification
# -----------------------------
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    password_bytes = plain_password.encode("utf-8")
    password_digest = hashlib.sha256(password_bytes).digest()
    return bcrypt.checkpw(
        password_digest,
        hashed_password.encode("utf-8")
    )


# -----------------------------
# Create JWT Token
# -----------------------------
def create_access_token(data: dict):

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire
    })

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


# -----------------------------
# Decode JWT Token
# -----------------------------
def verify_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        return None