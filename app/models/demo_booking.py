from sqlalchemy import Column, Integer, String, Date, Time, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class DemoBooking(Base):
    __tablename__ = "demo_bookings"

    __table_args__ = (
        UniqueConstraint(
            "demo_date",
            "demo_time",
            name="uq_demo_booking_date_time"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    demo_date = Column(Date, nullable=False, index=True)
    demo_time = Column(Time, nullable=False)

    contact_name = Column(String(200), nullable=True)
    contact_email = Column(String(255), nullable=True)

    status = Column(String(20), nullable=False, default="booked")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
