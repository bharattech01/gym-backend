import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

router = APIRouter()
security = HTTPBearer()

UPLOAD_DIR = Path("uploads/profile_photos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


@router.post("/profile/setup")
def setup_profile(
    name: str = Form(...),
    fitness_goal: str = Form(...),
    fitness_level: str = Form(...),
    gender: str = Form(...),
    profile_photo: UploadFile | None = File(default=None),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    if not SECRET_KEY:
        raise HTTPException(
            status_code=500,
            detail="JWT secret is not configured",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    saved_path = None

    if profile_photo and profile_photo.filename:
        if profile_photo.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Only JPEG, PNG and WebP images are allowed",
            )

        content = profile_photo.file.read(MAX_FILE_SIZE + 1)

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="Profile image must be 5 MB or smaller",
            )

        extension = ALLOWED_CONTENT_TYPES[profile_photo.content_type]
        filename = f"{uuid.uuid4().hex}{extension}"
        destination = UPLOAD_DIR / filename

        with destination.open("wb") as file:
            file.write(content)

        saved_path = f"/uploads/profile_photos/{filename}"

    try:
        user.name = name.strip()
        user.gender = gender.strip()
        user.fitness_goal = fitness_goal.strip()
        user.fitness_level = fitness_level.strip()

        if saved_path:
            user.profile_photo = saved_path

        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()

        if saved_path:
            (Path(".") / saved_path.lstrip("/")).unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Could not update profile",
        )

    return {
        "message": "Profile setup completed",
        "user": {
            "id": user.id,
            "name": user.name,
            "mobile": user.mobile,
            "gender": user.gender,
            "fitness_goal": user.fitness_goal,
            "fitness_level": user.fitness_level,
            "profile_photo": user.profile_photo,
        },
    }