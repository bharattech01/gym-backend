from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.schemas.auth import VerifyOTPRequest
from app.models.user import User
from app.utils.jwt import create_access_token
import random

from app.schemas.auth import SendOTPRequest
from app.core.database import get_db        # ✅ FIX 1
from app.models.otp import OTP              # ✅ FIX 2

router = APIRouter()

from fastapi import HTTPException
import traceback

@router.post("/send-otp")
def send_otp(data: SendOTPRequest, db: Session = Depends(get_db)):
    try:
        mobile = data.mobile

        otp = str(random.randint(100000, 999999))

        otp_entry = OTP(
            mobile=mobile,
            otp=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            is_used=False
        )

        db.add(otp_entry)
        db.commit()
        db.refresh(otp_entry)

        print("OTP:", otp)

        return {
            "message": "OTP sent successfully",
            "otp": otp,
            "expires_in": 300
        }

    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-otp")
def verify_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db)
):

    otp_record = db.query(OTP)\
        .filter(OTP.mobile == data.mobile)\
        .order_by(OTP.id.desc())\
        .first()

    # OTP NOT FOUND
    if not otp_record:
        raise HTTPException(
            status_code=400,
            detail="OTP not found"
        )

    # OTP ALREADY USED
    if otp_record.is_used:
        raise HTTPException(
            status_code=400,
            detail="OTP already used"
        )

    # OTP EXPIRED
    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="OTP expired"
        )

    # INVALID OTP
    if otp_record.otp != data.otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP"
        )

    # MARK OTP USED
    otp_record.is_used = True
    db.commit()

    # CHECK USER EXISTS
    user = db.query(User)\
        .filter(User.mobile == data.mobile)\
        .first()

    # CREATE USER IF NOT EXISTS
    if not user:
        user = User(
            mobile=data.mobile
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    # CREATE JWT TOKEN
    token = create_access_token({
        "user_id": user.id
    })

    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "mobile": user.mobile
        }
    }