from pydantic import BaseModel
from datetime import datetime


class ChatCreate(BaseModel):
    pass


class ChatResponse(BaseModel):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True