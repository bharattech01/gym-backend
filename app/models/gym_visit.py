from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class GymVisit(Base):
    __tablename__ = "gym_visits"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    gym_id = Column(
        Integer,
        ForeignKey("gyms.id"),
        nullable=False,
        index=True
    )

    check_in_time = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    check_out_time = Column(
        DateTime(timezone=True),
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="Inside"
    )

    user = relationship("User")
    gym = relationship("Gym")