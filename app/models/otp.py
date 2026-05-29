from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.core.database import Base

class OTP(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True)
    mobile = Column(String, index=True)
    otp = Column(String)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)



