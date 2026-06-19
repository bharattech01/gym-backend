from pydantic import BaseModel

class StatsCreate(BaseModel):

    steps: int
    heart_rate: int
    calories: int
    streak: int

