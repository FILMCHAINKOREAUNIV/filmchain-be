from sqlalchemy import Column, Integer, String, DateTime, func, BigInteger
from sqlalchemy.schema import UniqueConstraint
from app.database import Base

class Shorts(Base):
    __tablename__ = "shorts"
    
    id = Column(Integer, primary_key=True, index=True)

    #video_id: 유튜브 영상의 고유 ID
    video_id = Column(String, unique=True, index=True, nullable=False)

    url = Column(String, nullable=False)

    title = Column(String, nullable=True)  # 영상 제목

    hashtags = Column(String, nullable=True)

    view_count = Column(BigInteger, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class HashtagVote(Base):
    __tablename__ = "hastag_votes"

    id = Column(Integer, primary_key=True, index=True)
    hashtag = Column(String, unique=True, index=True, nullable=False)
    vote_count = Column(Integer, default=0)