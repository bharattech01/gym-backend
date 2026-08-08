from datetime import date
from pydantic import BaseModel


class ChallengeCreate(BaseModel):

    gym_id: int | None = None

    title: str

    description: str

    challenge_type: str

    prize: str

    start_date: date

    end_date: date

    participants: int = 0

    status: str = "Active"