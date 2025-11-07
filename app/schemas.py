from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ShortsCreateRequest(BaseModel):
    url: str

class ShortsBase(BaseModel):
    video_id: str
    url: str
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
