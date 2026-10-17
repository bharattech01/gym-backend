from datetime import datetime, timedelta
import random
import traceback

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.otp import OTP
from app.models.user import User
from app.schemas.auth import SendOTPRequest, VerifyOTPRequest
from app.utils.jwt import create_access_token

router = APIRouter()


@router.post("/send-otp")
def send_otp(data: SendOTPRequest, db: Session = Depends(get_db)):
    try:
        mobile = data.mobile
        otp = str(random.randint(100000, 999999))

        otp_entry = OTP(
            mobile=mobile,
            otp=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=5),
            is_used=False,
        )

        db.add(otp_entry)
        db.commit()
        db.refresh(otp_entry)

        # Development/testing only: do not expose OTPs in production.
        print("OTP generated successfully")

        return {
            "message": "OTP sent successfully",
            "otp": otp,
            "expires_in": 300,
        }

    except Exception:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Unable to send OTP",
        )


@router.post("/verify-otp")
def verify_otp(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db),
):
    otp_record = (
        db.query(OTP)
        .filter(OTP.mobile == data.mobile)
        .order_by(OTP.id.desc())
        .first()
    )

    if not otp_record:
        raise HTTPException(status_code=400, detail="OTP not found")

    if otp_record.is_used:
        raise HTTPException(status_code=400, detail="OTP already used")

    if otp_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="OTP expired")

    if otp_record.otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    try:
        # Find or create the user.
        user = (
            db.query(User)
            .filter(User.mobile == data.mobile)
            .first()
        )

        if not user:
            user = User(mobile=data.mobile)
            db.add(user)
            db.flush()

        # Profile completion is based on the onboarding fields.
        profile_complete = bool(
            user.name
            and user.fitness_goal
            and user.fitness_level
        )

        # Mark OTP used only after successful user lookup/creation.
        otp_record.is_used = True
        db.commit()
        db.refresh(user)

        token = create_access_token({"user_id": user.id})

        user_details = {
            "id": user.id,
            "mobile": user.mobile,
            "name": user.name,
            "email": user.email,
            "gender": user.gender,
            "city": user.city,
            "fitness_goal": user.fitness_goal,
            "fitness_level": user.fitness_level,
            "profile_photo": user.profile_photo,
        }

        response = {
            "message": "OTP verified successfully",
            "access_token": token,
            "token_type": "bearer",
            "profile_complete": profile_complete,
            "next_step": "home" if profile_complete else "profile_setup",
        }

        if profile_complete:
            response["user"] = user_details

        return response

    except HTTPException:
        raise
    except Exception:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Unable to verify OTP",
        )