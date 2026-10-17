
import uuid
from pathlib import Path

import qrcode
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.membership import Membership
from app.schemas.membership import MembershipCreate

router = APIRouter()

UPLOAD_DIR = Path("uploads/qr_codes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/add")
def add_membership(
    data: MembershipCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user["user_id"]

    qr_code = str(uuid.uuid4())

    # Generate an actual QR image containing the membership identifier
    image = qrcode.make(qr_code)
    image_path = UPLOAD_DIR / f"{qr_code}.png"
    image.save(image_path)

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
        "qr_code": membership.qr_code,
        "qr_image_url": f"/uploads/qr_codes/{qr_code}.png"
    }
