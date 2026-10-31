# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from app.core.database import get_db
# from app.models.gym_member import GymMember
# from app.schemas.gym_member import GymMemberCreate

# router = APIRouter()


# @router.post("/")
# def join_gym(
#     member: GymMemberCreate,
#     db: Session = Depends(get_db)
# ):

#     gym_member = GymMember(
#         user_id=member.user_id,
#         gym_id=member.gym_id,
#         membership_type=member.membership_type,
#         join_date=member.join_date,
#         status=member.status
#     )

#     db.add(gym_member)
#     db.commit()
#     db.refresh(gym_member)

#     return {
#         "message": "Gym joined successfully",
#         "membership_id": gym_member.id
#     }


#     from app.models.user import User

# @router.get("/gym/{gym_id}")
# def get_gym_members(
#     gym_id: int,
#     db: Session = Depends(get_db)
# ):

#     members = (
#         db.query(
#             User.id,
#             User.name,
#             User.age,
#             User.gender,
#             User.profile_image,
#             User.fitness_goal,
#             User.experience_level
#         )
#         .join(GymMember, GymMember.user_id == User.id)
#         .filter(
#             GymMember.gym_id == gym_id,
#             GymMember.status == "Active"
#         )
#         .all()
#     )

#     return members


import os
import math
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
from jose import jwt, JWTError
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.gym import Gym
from app.models.gym_member import GymMember
from app.models.gym_visit import GymVisit
from app.models.user import User
from app.schemas.gym_member import GymMemberCreate


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter()
security = HTTPBearer()


# Request body for check-in and check-out
class CrowdLocationRequest(BaseModel):
    gym_id: int
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials,
    db: Session
):
    if not SECRET_KEY or not ALGORITHM:
        raise HTTPException(
            status_code=500,
            detail="JWT configuration is missing"
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(User).filter(
        User.id == user_id,
        User.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive"
        )

    return user


# Calculate distance between two GPS coordinates
def calculate_distance(lat1, lon1, lat2, lon2):

    earth_radius = 6371000

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius * c


# Existing gym membership registration
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


# Existing gym members listing
@router.get("/gym/{gym_id}")
def get_gym_members(
    gym_id: int,
    db: Session = Depends(get_db)
):
    members = (
        db.query(
            User.id,
            User.name,
            User.gender,
            User.mobile,
            User.fitness_goal,
            User.fitness_level
        )
        .join(GymMember, GymMember.user_id == User.id)
        .filter(
            GymMember.gym_id == gym_id,
            GymMember.status == "Active"
        )
        .all()
    )

    return members


# MEMBER CHECK-IN
@router.post("/check-in")
def check_in(
    data: CrowdLocationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    user = get_authenticated_user(credentials, db)

    try:
        # Lock the gym row to serialize occupancy updates
        gym = (
            db.query(Gym)
            .filter(Gym.id == data.gym_id)
            .with_for_update()
            .first()
        )

        if not gym:
            raise HTTPException(
                status_code=404,
                detail="Gym not found"
            )

        if gym.latitude is None or gym.longitude is None:
            raise HTTPException(
                status_code=409,
                detail="Gym location has not been configured"
            )

        # Verify active membership
        membership = db.query(GymMember).filter(
            GymMember.user_id == user.id,
            GymMember.gym_id == gym.id,
            GymMember.status == "Active"
        ).first()

        if not membership:
            raise HTTPException(
                status_code=403,
                detail="No active membership for this gym"
            )

        # Verify member is within 100 metres
        distance = calculate_distance(
            data.latitude,
            data.longitude,
            gym.latitude,
            gym.longitude
        )

        if distance > 100:
            raise HTTPException(
                status_code=403,
                detail=f"You are outside the gym location radius ({round(distance)} metres away)"
            )

        # Prevent duplicate active visits
        existing_visit = db.query(GymVisit).filter(
            GymVisit.user_id == user.id,
            GymVisit.gym_id == gym.id,
            GymVisit.check_out_time.is_(None)
        ).first()

        if existing_visit:
            raise HTTPException(
                status_code=409,
                detail="You are already checked in"
            )

        # Check current occupancy
        active_count = db.query(GymVisit).filter(
            GymVisit.gym_id == gym.id,
            GymVisit.check_out_time.is_(None)
        ).count()

        if gym.capacity and active_count >= gym.capacity:
            raise HTTPException(
                status_code=409,
                detail="Gym capacity has been reached"
            )

        visit = GymVisit(
            user_id=user.id,
            gym_id=gym.id,
            status="Inside"
        )

        db.add(visit)
        db.flush()

        # Recalculate occupancy
        active_count += 1
        gym.current_occupancy = active_count

        db.commit()
        db.refresh(visit)

        crowd_percentage = (
            round((active_count / gym.capacity) * 100, 2)
            if gym.capacity and gym.capacity > 0
            else 0
        )

        return {
            "message": "Gym check-in successful",
            "visit_id": visit.id,
            "gym_id": gym.id,
            "current_occupancy": active_count,
            "capacity": gym.capacity,
            "crowd_percentage": crowd_percentage
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to process gym check-in"
        )


# MEMBER CHECK-OUT
@router.post("/check-out")
def check_out(
    data: CrowdLocationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    user = get_authenticated_user(credentials, db)

    try:
        # Lock gym row before updating occupancy
        gym = (
            db.query(Gym)
            .filter(Gym.id == data.gym_id)
            .with_for_update()
            .first()
        )

        if not gym:
            raise HTTPException(
                status_code=404,
                detail="Gym not found"
            )

        # Find the member's active visit
        visit = db.query(GymVisit).filter(
            GymVisit.user_id == user.id,
            GymVisit.gym_id == gym.id,
            GymVisit.check_out_time.is_(None)
        ).with_for_update().first()

        if not visit:
            raise HTTPException(
                status_code=404,
                detail="No active gym visit found"
            )

        # Record exit
        visit.check_out_time = datetime.now(timezone.utc)
        visit.status = "Completed"

        db.flush()

        # Recalculate occupancy from active visits
        active_count = db.query(GymVisit).filter(
            GymVisit.gym_id == gym.id,
            GymVisit.check_out_time.is_(None)
        ).count()

        gym.current_occupancy = active_count

        db.commit()

        crowd_percentage = (
            round((active_count / gym.capacity) * 100, 2)
            if gym.capacity and gym.capacity > 0
            else 0
        )

        return {
            "message": "Gym check-out successful",
            "gym_id": gym.id,
            "current_occupancy": active_count,
            "capacity": gym.capacity,
            "crowd_percentage": crowd_percentage
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to process gym check-out"
        )
