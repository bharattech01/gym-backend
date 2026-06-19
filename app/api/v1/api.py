from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import users
from app.api.v1.endpoints import dashboard
from app.api.v1.endpoints import memberships
from app.api.v1.endpoints import workouts
from app.api.v1.endpoints import stats
api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router,prefix="/users",tags=["Users"])
api_router.include_router(dashboard.router,prefix="/dashboard",tags=["Dashboard"])
api_router.include_router(memberships.router,prefix="/memberships",tags=["Memberships"])
api_router.include_router(stats.router,prefix="/stats",tags=["Stats"])
api_router.include_router(workouts.router,prefix="/workouts",tags=["Workouts"])