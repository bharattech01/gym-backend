from sqlalchemy import Column, Integer, ForeignKey

from app.core.database import Base

class UserStats(Base):

    __tablename__ = "user_stats"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    steps = Column(Integer)

    heart_rate = Column(Integer)

    calories = Column(Integer)

    streak = Column(Integer)

