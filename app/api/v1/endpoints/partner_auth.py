from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.gym import Gym
from app.models.partner import Partner
from app.schemas.partner import (
    PartnerRegisterRequest,
    PartnerRegisterResponse,
)

router = APIRouter()
password_hash = PasswordHash.recommended()


@router.post(
    "/register",
    response_model=PartnerRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_partner(
    request: PartnerRegisterRequest,
    db: Session = Depends(get_db),
):
    email = str(request.email).lower()

    existing_partner = (
        db.query(Partner)
        .filter(Partner.email == email)
        .first()
    )

    if existing_partner:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists",
        )

    now = datetime.now(timezone.utc)

    try:
        gym = Gym(name=request.gym_name.strip())
        db.add(gym)
        db.flush()

        partner = Partner(
            first_name=request.first_name.strip(),
            last_name=request.last_name.strip(),
            email=email,
            password_hash=password_hash.hash(request.password),
            gym_id=gym.id,
            trial_starts_at=now,
            trial_ends_at=now + timedelta(days=14),
        )

        db.add(partner)
        db.commit()
        db.refresh(partner)

        return PartnerRegisterResponse(
            message="Partner account created successfully",
            partner_id=partner.id,
            gym_id=gym.id,
            trial_ends_at=partner.trial_ends_at,
        )

    except Exception:
        db.rollback()
        raise
