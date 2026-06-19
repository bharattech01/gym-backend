from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.workout import Workout

from app.schemas.workout import WorkoutCreate

router = APIRouter()

@router.post("/add")
def add_workout(
data: WorkoutCreate,
current_user=Depends(get_current_user),
db: Session = Depends(get_db)
):


    user_id = current_user["user_id"]

    workout = Workout(
        user_id=user_id,
        exercise=data.exercise,
        sets=data.sets,
        reps=data.reps
    )

    db.add(workout)
    db.commit()

    return {
        "message": "Workout added successfully"
    }

