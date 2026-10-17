from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class PartnerRegisterRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    gym_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class PartnerRegisterResponse(BaseModel):
    message: str
    partner_id: int
    gym_id: int
    trial_ends_at: datetime

    model_config = ConfigDict(from_attributes=True)
