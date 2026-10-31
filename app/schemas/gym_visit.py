
from pydantic import BaseModel, Field


class CrowdLocationRequest(BaseModel):
    gym_id: int

    latitude: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Member's current GPS latitude"
    )

    longitude: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Member's current GPS longitude"
    )
