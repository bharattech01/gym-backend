from pydantic import BaseModel


class DietPlanCreate(BaseModel):

    gym_id: int

    title: str

    goal: str

    calories: int

    duration: str

    breakfast: str

    lunch: str

    dinner: str

    snacks: str

    description: str