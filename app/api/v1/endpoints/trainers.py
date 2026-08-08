from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.trainer import Trainer
from app.schemas.trainer import TrainerCreate

router = APIRouter()


@router.post("/")
def create_trainer(
    trainer: TrainerCreate,
    db: Session = Depends(get_db)
):

    new_trainer = Trainer(
        gym_id=trainer.gym_id,
        name=trainer.name,
        image=trainer.image,
        specialization=trainer.specialization,
        experience=trainer.experience,
        rating=trainer.rating,
        certification=trainer.certification,
        description=trainer.description
    )

    db.add(new_trainer)
    db.commit()
    db.refresh(new_trainer)

    return {
        "message": "Trainer created successfully",
        "trainer_id": new_trainer.id
    }

@router.get("/gym/{gym_id}")
def get_gym_trainers(
    gym_id: int,
    db: Session = Depends(get_db)
):

    trainers = db.query(Trainer).filter(
        Trainer.gym_id == gym_id
    ).all()

    return trainers