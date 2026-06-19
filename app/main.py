from fastapi import FastAPI

from app.api.v1.api import api_router

from app.core.database import Base, engine

from app.models.user import User
from app.models.otp import OTP
from app.models.membership import Membership
from app.models.user_stats import UserStats
from app.models.workout import Workout

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(
    api_router,
    prefix="/api/v1"
)


@app.get("/")
def root():

    return {
        "message": "Gym Backend API Running"
    }