from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ShortsCreateRequest(BaseModel):
    url: str
    hashtags: Optional[str] = None

class ShortsBase(BaseModel):
    video_id: str
    url: str
    title: Optional[str] = None
    hashtags: Optional[str] = None
    view_count: int

class Shorts(ShortsBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class HashtagStat(BaseModel):
    hashtag: str
    total_views: int
