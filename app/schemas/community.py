
from typing import Optional
from pydantic import BaseModel, Field


class CommunityPostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=5000)
    category: str = Field(default="General", max_length=50)
    image_url: Optional[str] = Field(default=None, max_length=500)


class CommunityCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=3000)


class CommunityMessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=3000)
