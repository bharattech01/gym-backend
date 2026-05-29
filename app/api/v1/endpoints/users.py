from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session
from jose import jwt

import os
from dotenv import load_dotenv

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import ProfileSetupRequest

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter()

security = HTTPBearer()


@router.post("/profile/setup")
def setup_profile(
    data: ProfileSetupRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):

    token = credentials.credentials

    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    user_id = payload.get("user_id")

    user = db.query(User)\
        .filter(User.id == user_id)\
        .first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.name = data.name
    user.fitness_goal = data.fitness_goal
    user.fitness_level = data.fitness_level

    db.commit()
    db.refresh(user)

    return {
        "message": "Profile setup completed",
        "user": {
            "id": user.id,
            "name": user.name,
            "mobile": user.mobile,
            "fitness_goal": user.fitness_goal,
            "fitness_level": user.fitness_level
        }
    }
    