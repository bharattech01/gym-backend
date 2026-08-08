from datetime import date
from pydantic import BaseModel


class GymMemberCreate(BaseModel):

    user_id: int

    gym_id: int

    membership_type: str

    join_date: date

    status: str = "Active"