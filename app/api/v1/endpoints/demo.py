from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.demo_booking import DemoBooking
from app.schemas.demo import (
    DemoBookingRequest,
    DemoBookingResponse,
)

router = APIRouter()

# Initial configurable demo schedule.
DEMO_SLOTS = [
    time(10, 0),
    time(10, 30),
    time(11, 0),
    time(11, 30),
    time(14, 0),
    time(14, 30),
    time(15, 0),
]

BOOKING_WINDOW_DAYS = 14


def is_bookable_day(day: date) -> bool:
    today = date.today()
    return today <= day < today + timedelta(days=BOOKING_WINDOW_DAYS) and day.weekday() != 6


def get_booked_times(db: Session, day: date) -> set[time]:
    bookings = (
        db.query(DemoBooking)
        .filter(
            DemoBooking.demo_date == day,
            DemoBooking.status == "booked",
        )
        .all()
    )
    return {booking.demo_time for booking in bookings}


@router.get("/availability")
def get_demo_dates(db: Session = Depends(get_db)):
    today = date.today()
    dates = []

    for offset in range(BOOKING_WINDOW_DAYS):
        day = today + timedelta(days=offset)

        if day.weekday() == 6:
            continue

        booked = get_booked_times(db, day)
        available = any(slot not in booked for slot in DEMO_SLOTS)

        dates.append({
            "date": day.isoformat(),
            "available": available,
        })

    return {"dates": dates}


@router.get("/availability/{demo_date}")
def get_demo_slots(
    demo_date: date,
    db: Session = Depends(get_db),
):
    if not is_bookable_day(demo_date):
        raise HTTPException(
            status_code=400,
            detail="This date is outside the booking window or unavailable",
        )

    booked = get_booked_times(db, demo_date)

    slots = [
        slot.strftime("%H:%M")
        for slot in DEMO_SLOTS
        if slot not in booked
    ]

    return {
        "date": demo_date.isoformat(),
        "slots": slots,
    }


@router.post("/book", response_model=DemoBookingResponse, status_code=201)
def book_demo(
    request: DemoBookingRequest,
    db: Session = Depends(get_db),
):
    if not is_bookable_day(request.date):
        raise HTTPException(
            status_code=400,
            detail="This date is outside the booking window or unavailable",
        )

    if request.time not in DEMO_SLOTS:
        raise HTTPException(
            status_code=400,
            detail="This time slot is not offered",
        )

    if request.time <= datetime.now().time() and request.date == date.today():
        raise HTTPException(
            status_code=400,
            detail="This time slot has already passed",
        )

    existing = (
        db.query(DemoBooking)
        .filter(
            DemoBooking.demo_date == request.date,
            DemoBooking.demo_time == request.time,
            DemoBooking.status == "booked",
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="This demo slot is already booked",
        )

    booking = DemoBooking(
        demo_date=request.date,
        demo_time=request.time,
        contact_name=request.contact_name,
        contact_email=(
            str(request.contact_email).lower()
            if request.contact_email
            else None
        ),
        status="booked",
    )

    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This demo slot was just booked by someone else",
        )

    return DemoBookingResponse(
        message="Demo booked successfully",
        booking_id=booking.id,
        date=booking.demo_date,
        time=booking.demo_time,
    )
