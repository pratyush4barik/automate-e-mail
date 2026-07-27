from fastapi import APIRouter, Depends, HTTPException
from database.database import get_db
import random
import string
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from database.models import User
import os
import resend

from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

@router.post("/generate-otp")
def generate_otp_endpoint(email: str, db: Session = Depends(get_db)):
    """
    Endpoint to generate and send OTP to the user's email.
    """
    result = create_and_send_otp(email, db)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return {"message": result["message"]}

@router.post("/verify-otp")
def verify_otp_endpoint(email: str, otp_code: str, db: Session = Depends(get_db)):
    """
    Endpoint to verify the OTP code.
    """
    result = verify_otp(email, otp_code, db)
    if not result["valid"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"message": result["message"]}

@router.post("/resend-otp")
def resend_otp_endpoint(email: str, db: Session = Depends(get_db)):
    """
    Endpoint to resend OTP to the user's email.
    """
    result = resend_otp(email, db)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return {"message": result["message"]}



def generate_otp() -> str:
    """Generate a random 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(email: str, otp: str):
    """Send OTP to user email via Resend"""
    
    resend.api_key = os.getenv("RESEND_API_KEY")
    
    try:
        response = resend.Emails.send({
            "from": "noreply@helpdesk.auoris.online",
            "to": email,
            "subject": "Your OTP Code",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 400px; margin: 0 auto;">
                <h2>Verify Your Email</h2>
                <p>Your OTP code is:</p>
                <h1 style="color: #007bff; letter-spacing: 2px;">{otp}</h1>
                <p>This code will expire in 10 minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </div>
            """
        })
        return response
    except Exception as e:
        print(f"Error sending email: {e}")
        raise


def create_and_send_otp(email: str, db: Session) -> dict:
    """
    Generate OTP, save to database, and send via email
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return {"success": False, "message": "User not found"}
    
    # Generate OTP
    otp = generate_otp()
    
    # Set expiration time (10 minutes from now)
    otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Save to database
    user.otp = otp
    user.otp_expires_at = otp_expires_at
    db.commit()
    
    # Send email
    try:
        send_otp_email(email, otp)
        return {"success": True, "message": "OTP sent successfully"}
    except Exception as e:
        return {"success": False, "message": f"Failed to send OTP: {str(e)}"}


def verify_otp(email: str, otp_code: str, db: Session) -> dict:
    """
    Verify OTP code and mark user as verified
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return {"valid": False, "error": "User not found"}
    
    if not user.otp:
        return {"valid": False, "error": "No OTP found for this user"}
    
    # Check if OTP is expired
    if datetime.utcnow() > user.otp_expires_at:
        return {"valid": False, "error": "OTP has expired"}
    
    # Verify OTP code
    if user.otp != otp_code:
        return {"valid": False, "error": "Invalid OTP"}
    
    # Mark user as verified
    user.is_verified = True
    user.otp = None  # Clear OTP after verification
    user.otp_expires_at = None
    db.commit()
    
    return {"valid": True, "message": "Email verified successfully"}


def resend_otp(email: str, db: Session) -> dict:
    """
    Resend OTP to user (clears old OTP first)
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        return {"success": False, "message": "User not found"}
    
    # Clear old OTP
    user.otp = None
    user.otp_expires_at = None
    db.commit()
    
    # Generate and send new OTP
    return create_and_send_otp(email, db)
