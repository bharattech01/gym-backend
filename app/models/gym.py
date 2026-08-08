from sqlalchemy import Column, Integer, String, Float

from app.core.database import Base


class Gym(Base):

    __tablename__ = "gyms"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    image = Column(String)

    address = Column(String)

    category = Column(String)

    monthly_fee = Column(Integer)

    rating = Column(Float)

    distance = Column(Float)

    crowd_status = Column(String)

    capacity = Column(Integer)

    male_percentage = Column(Integer)

    female_percentage = Column(Integer)

    equipment_score = Column(Integer)

    trainer_rating = Column(Float)

    success_rate = Column(Integer)

    opening_time = Column(String)

    closing_time = Column(String)

    amenities = Column(String)
    cleanliness_score = Column(Float)

    transformation_score = Column(Float)

    day_pass_price = Column(Integer)

    description = Column(String)