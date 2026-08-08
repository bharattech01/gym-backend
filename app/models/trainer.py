from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Trainer(Base):

    __tablename__ = "trainers"

    id = Column(Integer, primary_key=True, index=True)

    gym_id = Column(Integer, ForeignKey("gyms.id"))

    name = Column(String, nullable=False)

    image = Column(String)

    specialization = Column(String)

    experience = Column(Integer)

    rating = Column(Float)

    certification = Column(String)

    description = Column(String)

    gym = relationship("Gym")