from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.diet_plan import DietPlan
from app.schemas.diet_plan import DietPlanCreate

router = APIRouter()

@router.post("/")
def create_diet_plan(
    diet: DietPlanCreate,
    db: Session = Depends(get_db)
):

    new_plan = DietPlan(
        gym_id=diet.gym_id,
        title=diet.title,
        goal=diet.goal,
        calories=diet.calories,
        duration=diet.duration,
        breakfast=diet.breakfast,
        lunch=diet.lunch,
        dinner=diet.dinner,
        snacks=diet.snacks,
        description=diet.description
    )

    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return {
        "message": "Diet Plan created successfully",
        "diet_plan_id": new_plan.id
    }

@router.get("/gym/{gym_id}")
def get_diet_plans(
    gym_id: int,
    db: Session = Depends(get_db)
):

    plans = db.query(DietPlan).filter(
        DietPlan.gym_id == gym_id
    ).all()

    return plans