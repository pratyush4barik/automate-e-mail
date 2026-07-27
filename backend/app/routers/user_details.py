import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import UserDetails

router = APIRouter()

from database.schemas import (
    UserDetailsBase,
    UserDetailsCreate,
    UserDetailsResponse,
    UserDetailsUpdate,
)

def _to_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except json.JSONDecodeError:
            return [item.strip() for item in value.split(",") if item.strip()]
    return [str(value)]


def _to_storage_list(value: list[str] | None) -> str | None:
    if value is None:
        return None
    return json.dumps(value)


def _to_response(user_details: UserDetails) -> UserDetailsResponse:
    return UserDetailsResponse(
        id=user_details.id,
        name=user_details.name,
        college=user_details.college,
        degree=user_details.degree,
        branch=user_details.branch,
        resume_link=user_details.resume_link,
        github_link=user_details.github_link,
        linkedin_link=user_details.linkedin_link,
        drive_link=user_details.drive_link,
        roll_number=user_details.roll_number,
        year=user_details.year,
        cgpa=user_details.cgpa,
        skills=_to_list(user_details.skills),
        projects=_to_list(user_details.projects),
        research_interests=_to_list(user_details.research_interests),
    )


@router.post("/create", response_model=UserDetailsResponse, status_code=status.HTTP_201_CREATED)
def create_user_details(
    payload: UserDetailsCreate,
    db: Session = Depends(get_db),
):
    user_details = UserDetails(
        name=payload.name,
        college=payload.college,
        degree=payload.degree,
        branch=payload.branch,
        resume_link=payload.resume_link,
        github_link=payload.github_link,
        linkedin_link=payload.linkedin_link,
        drive_link=payload.drive_link,
        roll_number=payload.roll_number,
        year=payload.year,
        cgpa=payload.cgpa,
        skills=_to_storage_list(payload.skills),
        projects=_to_storage_list(payload.projects),
        research_interests=_to_storage_list(payload.research_interests),
    )

    db.add(user_details)
    db.commit()
    db.refresh(user_details)

    return _to_response(user_details)


@router.get("/", response_model=list[UserDetailsResponse])
def get_all_user_details(
    db: Session = Depends(get_db),
):
    records = db.query(UserDetails).order_by(UserDetails.id.desc()).all()
    return [_to_response(record) for record in records]


@router.get("/{details_id}", response_model=UserDetailsResponse)
def get_user_details(
    details_id: int,
    db: Session = Depends(get_db),
):
    user_details = db.query(UserDetails).filter(UserDetails.id == details_id).first()

    if user_details is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User details not found."
        )

    return _to_response(user_details)


@router.put("/update/{details_id}", response_model=UserDetailsResponse)
def update_user_details(
    details_id: int,
    payload: UserDetailsUpdate,
    db: Session = Depends(get_db),
):
    user_details = db.query(UserDetails).filter(UserDetails.id == details_id).first()

    if user_details is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User details not found."
        )

    updates = payload.model_dump(exclude_unset=True)

    for field_name, field_value in updates.items():
        if field_name in {"skills", "projects", "research_interests"}:
            setattr(user_details, field_name, _to_storage_list(field_value))
        else:
            setattr(user_details, field_name, field_value)

    db.commit()
    db.refresh(user_details)

    return _to_response(user_details)


@router.delete("/{details_id}", status_code=status.HTTP_200_OK)
def delete_user_details(
    details_id: int,
    db: Session = Depends(get_db),
):
    user_details = db.query(UserDetails).filter(UserDetails.id == details_id).first()

    if user_details is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User details not found."
        )

    db.delete(user_details)
    db.commit()

    return {"message": "User details deleted successfully."}
