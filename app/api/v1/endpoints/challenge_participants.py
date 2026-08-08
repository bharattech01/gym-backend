from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.challenge import Challenge
from app.models.challenge_participant import ChallengeParticipant
from app.models.user import User

router = APIRouter()
@router.post("/join")
def join_challenge(
    challenge_id: int,
    user_id: int,
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

    already_joined = db.query(ChallengeParticipant).filter(
        ChallengeParticipant.challenge_id == challenge_id,
        ChallengeParticipant.user_id == user_id
    ).first()

    if already_joined:
        raise HTTPException(
            status_code=400,
            detail="Already joined this challenge"
        )

    participant = ChallengeParticipant(
        challenge_id=challenge_id,
        user_id=user_id
    )

    db.add(participant)

    challenge.participants += 1

    db.commit()

    return {
        "message": "Joined successfully"
    }


@router.get("/{challenge_id}/leaderboard")
def leaderboard(
    challenge_id: int,
    db: Session = Depends(get_db)
):

    leaderboard = (
        db.query(
            ChallengeParticipant.rank,
            ChallengeParticipant.score,
            User.name
        )
        .join(User)
        .filter(
            ChallengeParticipant.challenge_id == challenge_id
        )
        .order_by(
            ChallengeParticipant.rank
        )
        .all()
    )

    return leaderboard


@router.get("/{challenge_id}/my-rank")
def my_rank(
    challenge_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):

    participant = db.query(
        ChallengeParticipant
    ).filter(
        ChallengeParticipant.challenge_id == challenge_id,
        ChallengeParticipant.user_id == user_id
    ).first()

    if not participant:
        raise HTTPException(
            status_code=404,
            detail="User has not joined this challenge"
        )

    return {
        "rank": participant.rank,
        "score": participant.score
    }

@router.get("/my/{user_id}")
def my_challenges(
    user_id: int,
    db: Session = Depends(get_db)
):

    challenges = (
        db.query(Challenge)
        .join(
            ChallengeParticipant,
            Challenge.id == ChallengeParticipant.challenge_id
        )
        .filter(
            ChallengeParticipant.user_id == user_id
        )
        .all()
    )

    return challenges