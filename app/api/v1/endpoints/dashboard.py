# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from app.core.database import get_db
# from app.core.security import get_current_user

# from app.models.user import User
# from app.models.membership import Membership
# from app.models.user_stats import UserStats
# from app.models.workout import Workout
# from pathlib import Path
# import qrcode

# router = APIRouter()


# @router.get("/home")
# def get_home_dashboard(
#     current_user=Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):

#     user_id = current_user["user_id"]

#     user = db.query(User).filter(
#         User.id == user_id
#     ).first()

#     membership = db.query(Membership).filter(
#         Membership.user_id == user_id
#     ).first()

#     stats = db.query(UserStats).filter(
#         UserStats.user_id == user_id
#     ).first()

#     workouts = db.query(Workout).filter(
#         Workout.user_id == user_id
#     ).all()

#     workout_list = []

#     for workout in workouts:

#         workout_list.append({
#             "exercise": workout.exercise,
#             "sets": workout.sets,
#             "reps": workout.reps
#         })

#     qr_image_url = None

#     if membership and membership.qr_code:
#         image_path = Path("uploads/qr_codes") / f"{membership.qr_code}.png"

#         # Generate an image for existing memberships if needed
#         if not image_path.exists():
#             image_path.parent.mkdir(parents=True, exist_ok=True)
#             image = qrcode.make(membership.qr_code)
#             image.save(image_path)

#         qr_image_url = (
#             f"/uploads/qr_codes/{membership.qr_code}.png"
#         )

#     return {

#         "name": user.name if user else None,

#         "membership": {
#             "gym_name": membership.gym_name if membership else None,
#             "valid_till": membership.valid_till if membership else None,
#             "days_left": membership.days_left if membership else None,
#             "qr_code": membership.qr_code if membership else None,
#             "qr_image_url": qr_image_url,

#         },

#         "stats": {
#             "steps": stats.steps if stats else 0,
#             "heart_rate": stats.heart_rate if stats else 0,
#             "calories": stats.calories if stats else 0,
#             "streak": stats.streak if stats else 0
#         },

#         # "quick_actions": [
#         #     "AI Coach",
#         #     "Community",
#         #     "Challenges"
#         # ],

#         "today_workout": workout_list
#     }




from pathlib import Path

import qrcode
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user import User
from app.models.membership import Membership
from app.models.user_stats import UserStats
from app.models.workout import Workout
from app.models.gym import Gym
from app.models.gym_member import GymMember

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

    # Find the logged-in user's active gym
    current_gym = (
        db.query(Gym)
        .join(
            GymMember,
            GymMember.gym_id == Gym.id
        )
        .filter(
            GymMember.user_id == user_id,
            GymMember.status == "Active"
        )
        .first()
    )

    # Calculate crowd percentage from current occupancy
    crowd_percentage = 0

    if (
        current_gym
        and current_gym.capacity
        and current_gym.capacity > 0
    ):
        crowd_percentage = round(
            (current_gym.current_occupancy / current_gym.capacity)
            * 100
        )

    # Generate a QR image for the user's membership if needed
    qr_image_url = None

    if membership and membership.qr_code:
        image_path = (
            Path("uploads/qr_codes")
            / f"{membership.qr_code}.png"
        )

        if not image_path.exists():
            image_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            image = qrcode.make(membership.qr_code)
            image.save(image_path)

        qr_image_url = (
            f"/uploads/qr_codes/{membership.qr_code}.png"
        )

    workout_list = [
        {
            "exercise": workout.exercise,
            "sets": workout.sets,
            "reps": workout.reps
        }
        for workout in workouts
    ]

    return {
        "name": user.name if user else None,

        "membership": {
            "gym_name": membership.gym_name if membership else None,
            "valid_till": membership.valid_till if membership else None,
            "days_left": membership.days_left if membership else None,
            "qr_code": membership.qr_code if membership else None,
            "qr_image_url": qr_image_url
        },

        "current_gym": {
            "id": current_gym.id,
            "name": current_gym.name,
            "image": current_gym.image,
            "address": current_gym.address,
            "crowd_percentage": crowd_percentage,
            "crowd_status": current_gym.crowd_status,
            "current_occupancy": current_gym.current_occupancy,
            "capacity": current_gym.capacity,
            "male_percentage": current_gym.male_percentage,
            "female_percentage": current_gym.female_percentage,
            "opening_time": current_gym.opening_time,
            "closing_time": current_gym.closing_time,
            "amenities": current_gym.amenities,
            "rating": current_gym.rating
        } if current_gym else None,

        "stats": {
            "steps": stats.steps if stats else 0,
            "heart_rate": stats.heart_rate if stats else 0,
            "calories": stats.calories if stats else 0,
            "streak": stats.streak if stats else 0
        },

        "today_workout": workout_list
    }
