from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    content: str = Field(..., min_length=1, max_length=5000)


class PostRead(BaseModel):
    id: int
    author_id: int
    title: str
    content: str
    like_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HotPostRead(BaseModel):
    post_id: int
    score: float


class LikeActionResponse(BaseModel):
    post_id: int
    liked: bool
    like_count: int
