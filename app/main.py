from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.api import api_router
from app.core.database import Base, engine

# Import models so SQLAlchemy registers their tables.
from app.models.user import User
from app.models.otp import OTP
from app.models.membership import Membership
from app.models.user_stats import UserStats
from app.models.workout import Workout
from app.models.gym import Gym
from app.models.trainer import Trainer
from app.models.cart import Cart
from app.models.challenge import Challenge
from app.models.challenge_participant import ChallengeParticipant
from app.models.diet_plan import DietPlan
from app.models.gym_member import GymMember
from app.models.product import Product
from app.models.chat import Chat
from app.models.chat_message import ChatMessage
from app.models.partner import Partner
from app.models.demo_booking import DemoBooking


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Connecting to database...")
    Base.metadata.create_all(bind=engine)
    yield
    print("Application shutting down...")


app = FastAPI(lifespan=lifespan)

# Create the profile image upload directory.
Path("uploads/profile_photos").mkdir(parents=True, exist_ok=True)

# Serve uploaded files.
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads",
)

# Register API routes.
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Gym Backend API Running"}
