import time
from typing import Iterable, List

from app.database import SessionLocal, engine
from app.models import Base, Shorts
from app.user.models import User
from scheduler.youtube_client import fetch_video_stats


def _chunks(items: List[str], size: int) -> Iterable[List[str]]:
    for i in range(0, len(items), size):
        yield items[i : i + size]


def update_views():
    """
    DB에 저장된 모든 Shorts 레코드의 video_id를 모아
    YouTube API로 조회수/좋아요 수/태그를 가져와 view_count, hashtags를 갱신
    50개씩 배치로 호출하여 API 호출 한도를 고려
    """
    print("스케줄러: 'update_views' 작업 시작..")

    # 안전하게 테이블이 없으면 생성
    Base.metadata.create_all(bind=engine, checkfirst=True)

    # 스케줄러에서도 DB 스키마 업데이트 (like_count 컬럼 추가)
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE shorts ADD COLUMN IF NOT EXISTS like_count BIGINT DEFAULT 0"))
            conn.commit()
        except Exception as e:
            print(f"스케줄러: DB 스키마 업데이트 실패 (이미 존재할 수 있음): {e}")

    db = SessionLocal()
    try:
        # 업데이트 대상(Shorts 테이블의 모든 행)을 불러옴
        rows: List[Shorts] = db.query(Shorts).all()
        if not rows:
            print("스케줄러: 업데이트 대상이 없습니다.")
            return

        # 유효한 video_id만 추출
        video_ids = [r.video_id for r in rows if r.video_id]
        total_updated = 0

        for batch_ids in _chunks(video_ids, 50):
            stats_map = fetch_video_stats(batch_ids)

            for r in rows:
                data = stats_map.get(r.video_id)
                if not data:
                    continue
                # 조회수 갱신 (값이 없으면 기존 값 유지)
                r.view_count = int(data.get("view_count", r.view_count or 0))
                r.like_count = int(data.get("like_count", r.like_count or 0))
                # 제목 갱신 (None이면 변경하지 않음)
                title = data.get("title")
                if title is not None:
                    r.title = title
                # 해시태그 문자열 갱신 (None이면 변경하지 않음)
                # YouTube API에서 가져온 해시태그를 그대로 사용 (실제 영상에 달린 해시태그)
                hashtags = data.get("hashtags")
                if hashtags is not None:
                    r.hashtags = hashtags
                total_updated += 1

            db.commit()

        print(f"스케줄러: {total_updated}개 항목 업데이트 완료.")
    except Exception as e:
        db.rollback()
        print(f"스케줄러: 작업 중 오류 발생 - {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_views()
