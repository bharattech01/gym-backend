from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class ChallengeParticipant(Base):

    __tablename__ = "challenge_participants"

    id = Column(Integer, primary_key=True, index=True)

    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    score = Column(Integer, default=0)

    rank = Column(Integer, nullable=True)

    status = Column(String, default="Joined")

    joined_at = Column(DateTime, default=datetime.utcnow)

    challenge = relationship("Challenge")

    user = relationship("User")