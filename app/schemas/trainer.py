from pydantic import BaseModel


class TrainerCreate(BaseModel):

    gym_id: int

    name: str

    image: str

    specialization: str

    experience: int

    rating: float

    certification: str

    description: str