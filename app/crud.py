from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List
from app import models, schemas

def create_shorts(db: Session, video_id: str, url: str) -> models.Shorts:
    # POST /shorts/
    db_shorts = models.Shorts(video_id=video_id, url=url, view_count=0)

    try:
        db.add(db_shorts)
        db.commit()
        db.refresh(db_shorts)
        return db_shorts
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 영상입니다."
        )
def get_shorts_by_views(db: Session, limit: int = 100) -> list[models.Shorts]:
    # GET /shorts
    return db.query(models.Shorts)\
        .order_by(models.Shorts.view_count.desc())\
        .limit(limit)\
        .all()

def get_stats_for_hashtags(db: Session, tags: List[str]) -> List[schemas.HashtagStat]:
    # GET /shorts/compare
    stats_list =[]

    if not tags:
        return []
    
    for tag in tags:
        clean_tag = tag.strip().lstrip('#')
        search_pattern = f"%#{clean_tag}%"
        total_views_query = db.query(func.sum(models.Shorts.view_count))\
            .filter(models.Shorts.hashtags.ilike(search_pattern))\
            
        total_views = total_views_query.scalar()

        if total_views is None:
            total_views = 0

        stats_list.append(schemas.HashtagStat(hashtag=clean_tag, total_views=total_views))
    
    return stats_list