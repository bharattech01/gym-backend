from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.gym_member import GymMember
from app.schemas.gym_member import GymMemberCreate

router = APIRouter()


@router.post("/")
def join_gym(
    member: GymMemberCreate,
    db: Session = Depends(get_db)
):

    gym_member = GymMember(
        user_id=member.user_id,
        gym_id=member.gym_id,
        membership_type=member.membership_type,
        join_date=member.join_date,
        status=member.status
    )

    db.add(gym_member)
    db.commit()
    db.refresh(gym_member)

    return {
        "message": "Gym joined successfully",
        "membership_id": gym_member.id
    }


    from app.models.user import User

@router.get("/gym/{gym_id}")
def get_gym_members(
    gym_id: int,
    db: Session = Depends(get_db)
):

    members = (
        db.query(
            User.id,
            User.name,
            User.age,
            User.gender,
            User.profile_image,
            User.fitness_goal,
            User.experience_level
        )
        .join(GymMember, GymMember.user_id == User.id)
        .filter(
            GymMember.gym_id == gym_id,
            GymMember.status == "Active"
        )
        .all()
    )

    return members