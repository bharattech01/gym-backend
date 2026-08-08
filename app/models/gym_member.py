from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship

from app.core.database import Base


class GymMember(Base):

    __tablename__ = "gym_members"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    gym_id = Column(Integer, ForeignKey("gyms.id"), nullable=False)

    membership_type = Column(String)

    join_date = Column(Date)

    status = Column(String, default="Active")

    user = relationship("User")
    gym = relationship("Gym")