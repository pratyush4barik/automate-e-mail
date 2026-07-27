from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import Email as EmailModel
from database.schemas import EmailCreate, EmailResponse, EmailUpdate

router = APIRouter()


@router.post("/", response_model=EmailResponse, status_code=status.HTTP_201_CREATED)
def create_email(payload: EmailCreate, db: Session = Depends(get_db)):
    existing_email = (
        db.query(EmailModel)
        .filter(EmailModel.chat_id == payload.chat_id)
        .first()
    )

    if existing_email:
        existing_email.email = payload.email
        if payload.subject is not None:
            existing_email.subject = payload.subject
        if payload.body is not None:
            existing_email.body = payload.body
        existing_email.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_email)
        return existing_email

    new_email = EmailModel(
        chat_id=payload.chat_id,
        email=payload.email,
        subject=payload.subject,
        body=payload.body,
    )
    db.add(new_email)
    db.commit()
    db.refresh(new_email)
    return new_email


@router.get("/{chat_id}", response_model=EmailResponse)
def get_email_by_chat_id(chat_id: int, db: Session = Depends(get_db)):
    email_record = db.query(EmailModel).filter(EmailModel.chat_id == chat_id).first()

    if email_record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

    return email_record


@router.put("/{chat_id}", response_model=EmailResponse)
def update_email_by_chat_id(
    chat_id: int,
    payload: EmailUpdate,
    db: Session = Depends(get_db),
):
    email_record = db.query(EmailModel).filter(EmailModel.chat_id == chat_id).first()

    if email_record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

    if payload.email is not None:
        email_record.email = payload.email
    if payload.subject is not None:
        email_record.subject = payload.subject
    if payload.body is not None:
        email_record.body = payload.body

    email_record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(email_record)
    return email_record


@router.delete("/{chat_id}", status_code=status.HTTP_200_OK)
def delete_email_by_chat_id(chat_id: int, db: Session = Depends(get_db)):
    email_record = db.query(EmailModel).filter(EmailModel.chat_id == chat_id).first()

    if email_record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")

    db.delete(email_record)
    db.commit()

    return {"message": "Email deleted successfully"}