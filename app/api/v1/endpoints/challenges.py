from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.challenge import Challenge
from app.schemas.challenge import ChallengeCreate

router = APIRouter()

@router.post("/")
def create_challenge(
    challenge: ChallengeCreate,
    db: Session = Depends(get_db)
):

    new_challenge = Challenge(
        gym_id=challenge.gym_id,
        title=challenge.title,
        description=challenge.description,
        challenge_type=challenge.challenge_type,
        prize=challenge.prize,
        start_date=challenge.start_date,
        end_date=challenge.end_date,
        participants=challenge.participants,
        status=challenge.status
    )

    db.add(new_challenge)
    db.commit()
    db.refresh(new_challenge)

    return {
        "message": "Challenge created successfully",
        "challenge_id": new_challenge.id
    }

@router.get("/")
def get_challenges(
    challenge_type: str | None = Query(default=None),
    db: Session = Depends(get_db)
):

    query = db.query(Challenge)

    if challenge_type:
        query = query.filter(
            Challenge.challenge_type == challenge_type
        )

    return query.all()

@router.get("/{challenge_id}")
def get_challenge(
    challenge_id: int,
    db: Session = Depends(get_db)
):

    challenge = db.query(Challenge).filter(
        Challenge.id == challenge_id
    ).first()

    if not challenge:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found"
        )

    return challenge