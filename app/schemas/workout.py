from pydantic import BaseModel

class WorkoutCreate(BaseModel):

    exercise: str
    sets: int
    reps: int

