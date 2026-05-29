from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    mobile = Column(String, unique=True, index=True)

    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    city = Column(String, nullable=True)

    is_active = Column(Boolean, default=True)
    # PROFILE DATA

    name = Column(String, nullable=True)

    fitness_goal = Column(String, nullable=True)

    fitness_level = Column(String, nullable=True)

    profile_photo = Column(String, nullable=True)