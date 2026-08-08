from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.models.gym import Gym
from app.schemas.gym import GymCreate

router = APIRouter()


# ----------------------------
# CREATE GYM
# ----------------------------
@router.post("/")
def create_gym(
    gym: GymCreate,
    db: Session = Depends(get_db)
):

    new_gym = Gym(
        name=gym.name,
        image=gym.image,
        address=gym.address,
        category=gym.category,
        monthly_fee=gym.monthly_fee,
        rating=gym.rating,
        distance=gym.distance,
        crowd_status=gym.crowd_status,
        capacity=gym.capacity,
        male_percentage=gym.male_percentage,
        female_percentage=gym.female_percentage,
        equipment_score=gym.equipment_score,
        trainer_rating=gym.trainer_rating,
        success_rate=gym.success_rate,
        opening_time=gym.opening_time,
        closing_time=gym.closing_time,
        amenities=gym.amenities,
        cleanliness_score=gym.cleanliness_score,
        transformation_score=gym.transformation_score,
        day_pass_price=gym.day_pass_price,
        description=gym.description
    )

    db.add(new_gym)
    db.commit()
    db.refresh(new_gym)

    return {
        "message": "Gym created successfully",
        "gym_id": new_gym.id
    }


# ----------------------------
# GET ALL GYMS
# SEARCH + FILTER
# ----------------------------
@router.get("/")
def get_gyms(
    search: str = Query(default=None),
    category: str = Query(default=None),
    min_rating: float = Query(default=None),
    max_fee: int = Query(default=None),
    max_distance: float = Query(default=None),
    db: Session = Depends(get_db)
):

    query = db.query(Gym)

    # Search
    if search:
        query = query.filter(
            or_(
                Gym.name.ilike(f"%{search}%"),
                Gym.category.ilike(f"%{search}%"),
                Gym.address.ilike(f"%{search}%")
            )
        )

    # Category
    if category:
        query = query.filter(
            Gym.category.ilike(category)
        )

    # Rating
    if min_rating is not None:
        query = query.filter(
            Gym.rating >= min_rating
        )

    # Monthly Fee
    if max_fee is not None:
        query = query.filter(
            Gym.monthly_fee <= max_fee
        )

    # Distance
    if max_distance is not None:
        query = query.filter(
            Gym.distance <= max_distance
        )

    gyms = query.all()

    return gyms


# ----------------------------
# COMPARE GYMS
# ----------------------------
@router.get("/compare")
def compare_gyms(
    gym1: int = Query(...),
    gym2: int = Query(...),
    db: Session = Depends(get_db)
):

    first_gym = db.query(Gym).filter(Gym.id == gym1).first()
    second_gym = db.query(Gym).filter(Gym.id == gym2).first()

    if not first_gym:
        raise HTTPException(
            status_code=404,
            detail=f"Gym with id {gym1} not found"
        )

    if not second_gym:
        raise HTTPException(
            status_code=404,
            detail=f"Gym with id {gym2} not found"
        )

    return {
        "gym_1": {
            "id": first_gym.id,
            "name": first_gym.name,
            "category": first_gym.category,
            "rating": first_gym.rating,
            "monthly_fee": first_gym.monthly_fee,
            "distance": first_gym.distance,
            "crowd_status": first_gym.crowd_status,
            "capacity": first_gym.capacity,
            "male_percentage": first_gym.male_percentage,
            "female_percentage": first_gym.female_percentage,
            "equipment_score": first_gym.equipment_score,
            "trainer_rating": first_gym.trainer_rating,
            "success_rate": first_gym.success_rate,
            "opening_time": first_gym.opening_time,
            "closing_time": first_gym.closing_time,
            "amenities": first_gym.amenities,
            "image": first_gym.image,
            "address": first_gym.address
        },
        "gym_2": {
            "id": second_gym.id,
            "name": second_gym.name,
            "category": second_gym.category,
            "rating": second_gym.rating,
            "monthly_fee": second_gym.monthly_fee,
            "distance": second_gym.distance,
            "crowd_status": second_gym.crowd_status,
            "capacity": second_gym.capacity,
            "male_percentage": second_gym.male_percentage,
            "female_percentage": second_gym.female_percentage,
            "equipment_score": second_gym.equipment_score,
            "trainer_rating": second_gym.trainer_rating,
            "success_rate": second_gym.success_rate,
            "opening_time": second_gym.opening_time,
            "closing_time": second_gym.closing_time,
            "amenities": second_gym.amenities,
            "image": second_gym.image,
            "address": second_gym.address
        }
    }


# ----------------------------
# GYM DETAILS
# ----------------------------
@router.get("/{gym_id}")
def get_gym_details(
    gym_id: int,
    db: Session = Depends(get_db)
):

    gym = db.query(Gym).filter(Gym.id == gym_id).first()

    if not gym:
        raise HTTPException(
            status_code=404,
            detail="Gym not found"
        )

    return {
    "id": gym.id,
    "name": gym.name,
    "image": gym.image,
    "address": gym.address,
    "category": gym.category,
    "rating": gym.rating,
    "monthly_fee": gym.monthly_fee,
    "distance": gym.distance,
    "opening_time": gym.opening_time,
    "closing_time": gym.closing_time,

    "crowd": {
        "status": gym.crowd_status,
        "capacity": gym.capacity,
        "male_percentage": gym.male_percentage,
        "female_percentage": gym.female_percentage
    },

    "intelligence_scores": {
        "trainer_quality": gym.trainer_rating,
        "equipment_score": gym.equipment_score,
        "cleanliness_score": gym.cleanliness_score,
        "transformation_score": gym.transformation_score
    },

    "day_pass_price": gym.day_pass_price,

    "amenities": gym.amenities,

    "description": gym.description
}