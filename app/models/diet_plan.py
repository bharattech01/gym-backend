from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class DietPlan(Base):

    __tablename__ = "diet_plans"

    id = Column(Integer, primary_key=True, index=True)

    gym_id = Column(Integer, ForeignKey("gyms.id"))

    title = Column(String, nullable=False)

    goal = Column(String)

    calories = Column(Integer)

    duration = Column(String)

    breakfast = Column(String)

    lunch = Column(String)

    dinner = Column(String)

    snacks = Column(String)

    description = Column(String)

    gym = relationship("Gym")