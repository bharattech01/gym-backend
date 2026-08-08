from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Challenge(Base):

    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)

    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=True)

    title = Column(String, nullable=False)

    description = Column(String)

    challenge_type = Column(String)     # in-gym / out-gym

    prize = Column(String)

    start_date = Column(Date)

    end_date = Column(Date)

    participants = Column(Integer, default=0)

    status = Column(String, default="Active")

    gym = relationship("Gym")