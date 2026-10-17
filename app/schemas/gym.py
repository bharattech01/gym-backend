
from pydantic import BaseModel


class GymCreate(BaseModel):
    name: str
    image: str
    address: str
    category: str
    monthly_fee: int
    rating: float
    distance: float
    crowd_status: str
    capacity: int
    current_occupancy: int = 0
    male_percentage: int
    female_percentage: int
    equipment_score: int
    trainer_rating: float
    success_rate: int
    opening_time: str
    closing_time: str
    amenities: str
    cleanliness_score: float
    transformation_score: float
    day_pass_price: int
    description: str
