from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import users
from app.api.v1.endpoints import dashboard
from app.api.v1.endpoints import memberships
from app.api.v1.endpoints import workouts
from app.api.v1.endpoints import stats
from app.api.v1.endpoints import gyms
from app.api.v1.endpoints import trainers
from app.api.v1.endpoints import gym_members
from app.api.v1.endpoints import diet_plans
from app.api.v1.endpoints import challenges
from app.api.v1.endpoints import challenge_participants
from app.api.v1.endpoints import products
from app.api.v1.endpoints import cart
from app.api.v1.endpoints import ai_chat

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router,prefix="/users",tags=["Users"])
api_router.include_router(dashboard.router,prefix="/dashboard",tags=["Dashboard"])
api_router.include_router(memberships.router,prefix="/memberships",tags=["Memberships"])
api_router.include_router(stats.router,prefix="/stats",tags=["Stats"])
api_router.include_router(workouts.router,prefix="/workouts",tags=["Workouts"])
api_router.include_router(gyms.router,prefix="/gyms",tags=["Gyms"])
api_router.include_router(trainers.router,prefix="/trainers",tags=["Trainers"])
api_router.include_router(gym_members.router, prefix="/gym-members", tags=["Gym Members"])
api_router.include_router(diet_plans.router,prefix="/diet-plans",tags=["Diet Plans"])
api_router.include_router(challenges.router,prefix="/challenges",tags=["Challenges"])
api_router.include_router(challenge_participants.router,prefix="/challenge-participants",tags=["Challenge Participants"])
api_router.include_router(products.router,prefix="/products",tags=["Products"])
api_router.include_router(cart.router,prefix="/cart",tags=["Cart"])
api_router.include_router(ai_chat.router,prefix="/ai-chat",tags=["AI Chat"])

