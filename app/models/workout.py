from sqlalchemy import Column, Integer, String, ForeignKey

from app.core.database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    exercise = Column(String)

    sets = Column(Integer)

    reps = Column(Integer)

