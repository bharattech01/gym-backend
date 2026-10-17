from datetime import date, time
from pydantic import BaseModel, EmailStr, Field


class DemoBookingRequest(BaseModel):
    date: date
    time: time
    contact_name: str | None = Field(default=None, max_length=200)
    contact_email: EmailStr | None = None


class DemoBookingResponse(BaseModel):
    message: str
    booking_id: int
    date: date
    time: time
