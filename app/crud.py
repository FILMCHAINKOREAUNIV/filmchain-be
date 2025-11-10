from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Optional
from app import models, schemas
from scheduler.youtube_client import fetch_video_stats

def get_shorts_by_video_id(db: Session, video_id: str) -> models.Shorts | None:
    return db.query(models.Shorts).filter(models.Shorts.video_id == video_id).first()

def create_shorts(db: Session, video_id: str, url: str, hashtags: Optional[str] = None, fetch_views: bool = True) -> models.Shorts:
    # POST /shorts/
    db_shorts_exists = get_shorts_by_video_id(db=db, video_id=video_id)
    if db_shorts_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 영상입니다."
        )
    
    # 초기값으로 등록 (해시태그 포함)
    db_shorts = models.Shorts(video_id=video_id, url=url, view_count=0, hashtags=hashtags)

    try:
        db.add(db_shorts)
        db.commit()
        db.refresh(db_shorts)
        
        # 등록 후 즉시 조회수 조회
        if fetch_views:
            try:
                stats_map = fetch_video_stats([video_id])
                if video_id in stats_map:
                    data = stats_map[video_id]
                    db_shorts.view_count = int(data.get("view_count", 0))
                    # YouTube API에서 가져온 제목 저장
                    title = data.get("title")
                    if title is not None:
                        db_shorts.title = title
                    # YouTube API에서 가져온 해시태그가 있으면 병합, 없으면 요청으로 받은 해시태그 유지
                    youtube_hashtags = data.get("hashtags")
                    if youtube_hashtags is not None:
                        # 기존 해시태그와 YouTube 해시태그 병합
                        if db_shorts.hashtags:
                            # 중복 제거를 위해 집합 사용
                            existing_tags = set(db_shorts.hashtags.split())
                            youtube_tags = set(youtube_hashtags.split())
                            all_tags = existing_tags | youtube_tags
                            db_shorts.hashtags = " ".join(sorted(all_tags))
                        else:
                            db_shorts.hashtags = youtube_hashtags
                    db.commit()
                    db.refresh(db_shorts)
            except Exception as e:
                # YouTube API 호출 실패해도 등록은 성공 (조회수는 0으로 유지)
                print(f"조회수 조회 실패 (영상 등록은 성공): {e}")
        
        return db_shorts
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 등록된 영상입니다.."
        )
def get_shorts_by_views(db: Session, limit: int = 100) -> list[models.Shorts]:
    # GET /shorts
    return db.query(models.Shorts)\
        .order_by(models.Shorts.view_count.desc())\
        .limit(limit)\
        .all()

def update_shorts_views(db: Session, video_id: str) -> models.Shorts:
    """특정 영상의 조회수를 즉시 업데이트"""
    db_shorts = get_shorts_by_video_id(db=db, video_id=video_id)
    if not db_shorts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 영상을 찾을 수 없습니다."
        )
    
    try:
        stats_map = fetch_video_stats([video_id])
        if video_id in stats_map:
            data = stats_map[video_id]
            db_shorts.view_count = int(data.get("view_count", db_shorts.view_count or 0))
            # YouTube API에서 가져온 제목 업데이트
            title = data.get("title")
            if title is not None:
                db_shorts.title = title
            hashtags = data.get("hashtags")
            if hashtags is not None:
                db_shorts.hashtags = hashtags
            db.commit()
            db.refresh(db_shorts)
        return db_shorts
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"조회수 업데이트 실패: {str(e)}"
        )

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

def get_shorts_by_hashtag(db: Session, tag: str, limit: int = 100) -> list[models.Shorts]:
    """해시태그로 쇼츠 목록 조회"""
    clean_tag = tag.strip().lstrip('#')
    search_pattern = f"%#{clean_tag}%"
    return db.query(models.Shorts)\
        .filter(models.Shorts.hashtags.ilike(search_pattern))\
        .order_by(models.Shorts.view_count.desc())\
        .limit(limit)\
        .all()