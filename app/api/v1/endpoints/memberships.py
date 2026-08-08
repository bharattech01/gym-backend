from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user

from app.models.membership import Membership

from app.schemas.membership import MembershipCreate

router = APIRouter()

# @router.post("/add")
# def add_membership(
# data: MembershipCreate,
# current_user=Depends(get_current_user),
# db: Session = Depends(get_db)
# ):


#     user_id = current_user["user_id"]

#     membership = Membership(
#         user_id=user_id,
#         gym_name=data.gym_name,
#         valid_till=data.valid_till,
#         days_left=data.days_left
#     )

#     db.add(membership)
#     db.commit()

#     return {
#         "message": "Membership added successfully"
#     }

@router.post("/add")
def add_membership(
    data: MembershipCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user_id = current_user["user_id"]

    qr_code = str(uuid.uuid4())

    membership = Membership(
        user_id=user_id,
        gym_name=data.gym_name,
        valid_till=data.valid_till,
        days_left=data.days_left,
        qr_code=qr_code
    )

    db.add(membership)
    db.commit()
    db.refresh(membership)

    return {
        "message": "Membership added successfully",
        "membership_id": membership.id,
        "qr_code": membership.qr_code
    }


