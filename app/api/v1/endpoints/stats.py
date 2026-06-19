from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.user_stats import UserStats

from app.schemas.stats import StatsCreate

router = APIRouter()

@router.post("/add")
def add_stats(
data: StatsCreate,
current_user=Depends(get_current_user),
db: Session = Depends(get_db)
):


    user_id = current_user["user_id"]

    stats = UserStats(
        user_id=user_id,
        steps=data.steps,
        heart_rate=data.heart_rate,
        calories=data.calories,
        streak=data.streak
    )

    db.add(stats)
    db.commit()

    return {
        "message": "Stats added successfully"
    }

