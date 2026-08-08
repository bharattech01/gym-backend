from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.membership import Membership
from app.models.user_stats import UserStats
from app.models.workout import Workout

router = APIRouter()


@router.get("/home")
def get_home_dashboard(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user_id = current_user["user_id"]

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    membership = db.query(Membership).filter(
        Membership.user_id == user_id
    ).first()

    stats = db.query(UserStats).filter(
        UserStats.user_id == user_id
    ).first()

    workouts = db.query(Workout).filter(
        Workout.user_id == user_id
    ).all()

    workout_list = []

    for workout in workouts:

        workout_list.append({
            "exercise": workout.exercise,
            "sets": workout.sets,
            "reps": workout.reps
        })

    return {

        "name": user.name if user else None,

        "membership": {
            "gym_name": membership.gym_name if membership else None,
            "valid_till": membership.valid_till if membership else None,
            "days_left": membership.days_left if membership else None,
            "qr_code": membership.qr_code if membership else None

        },

        "stats": {
            "steps": stats.steps if stats else 0,
            "heart_rate": stats.heart_rate if stats else 0,
            "calories": stats.calories if stats else 0,
            "streak": stats.streak if stats else 0
        },

        "quick_actions": [
            "AI Coach",
            "Community",
            "Challenges"
        ],

        "today_workout": workout_list
    }