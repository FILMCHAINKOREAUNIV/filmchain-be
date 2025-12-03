from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, crud, services
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine, checkfirst=True)

app = FastAPI(
    title="쇼츠 조회수 확인 API",
)

@app.on_event("startup")
def startup_event():
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            # like_count 컬럼 확인 및 추가
            conn.execute(text("ALTER TABLE shorts ADD COLUMN IF NOT EXISTS like_count BIGINT DEFAULT 0"))
            # user_id 컬럼 확인 및 추가 (혹시 없는 경우를 대비)
            conn.execute(text("ALTER TABLE shorts ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"))
            conn.commit()
            print("Startup: Database schema updated (columns added if missing).")
        except Exception as e:
            print(f"Startup: Database schema update failed: {e}")

app.include_router(user_router.router)

# CORS 설정 추가 (프론트엔드 연동을 위해 필수)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경용 (프로덕션에서는 특정 도메인만 허용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/shorts", response_model=schemas.Shorts, status_code=status.HTTP_201_CREATED)
def create_shorts_entry(
    shorts_request: schemas.ShortsCreateRequest,
    db: Session = Depends(get_db)
):
    # URL 파싱
    video_id = services.parse_video_id(url=shorts_request.url)

    # DB에 저장 및 즉시 조회수 조회
    db_shorts = crud.create_shorts(
        db=db, 
        video_id=video_id, 
        url=shorts_request.url, 
        hashtags=shorts_request.hashtags,  # 추가
        fetch_views=True
    )
    return db_shorts

# 조회수 높은 순으로 쇼츠 목록 반환
# @app.get("/shorts", response_model=List[schemas.Shorts])
# def read_shorts_dashboard(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     shorts_list = crud.get_shorts_by_views(db=db, limit=limit)
#     return shorts_list

@app.get("/shorts/compare", response_model=List[schemas.HashtagStat])
def compare_hashtag_stats(
    tags: List[str] = Query(..., alias="tag"),
    db: Session = Depends(get_db)
):
    #호출 예시: GET http://localhost:3000/shorts/compare?tag=movie1&tag=movie2
    # 태그별 조회수 통계 반환
    stats = crud.get_stats_for_hashtags(db=db, tags=tags)
    return stats

@app.get("/shorts/by-hashtag", response_model=List[schemas.Shorts])
def get_shorts_by_hashtag_endpoint(
    tag: str = Query(..., description="해시태그"),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """해시태그별 쇼츠 목록 조회"""
    # 호출 예시: GET http://localhost:3000/shorts/by-hashtag?tag=귀멸의칼날
    shorts_list = crud.get_shorts_by_hashtag(db=db, tag=tag, limit=limit)
    return shorts_list

@app.get("/shorts/votes", response_model=List[schemas.HashtagVoteResponse])
def get_votes_endpoint(
    tags: List[str] = Query(..., alias="tag"),
    db: Session = Depends(get_db)
):
    """
    여러 해시태그의 투표수 조회
    호출 예시: GET http://localhost:3000/shorts/votes?tag=연세대&tag=고려대
    """
    return crud.get_votes_for_hashtags(db, tags)

@app.delete("/shorts/vote", response_model=schemas.HashtagVoteResponse)
def cancel_vote_endpoint(
    tag: str = Query(..., description="취소할 해시태그"),
    db: Session = Depends(get_db)
):
    """
    특정 해시태그 투표 취소 (-1)
    호출 예시: DELETE http://localhost:3000/shorts/vote?tag=귀멸의칼날
    """
    return crud.cancel_vote(db, tag)


@app.put("/shorts/{video_id}/refresh", response_model=schemas.Shorts)
def refresh_shorts_views(video_id: str, db: Session = Depends(get_db)):
    """특정 영상의 조회수를 즉시 업데이트"""
    return crud.update_shorts_views(db=db, video_id=video_id)

@app.get("/shorts/{video_id}", response_model=schemas.Shorts)
def get_shorts_by_video_id_endpoint(video_id: str, db: Session = Depends(get_db)):
    """특정 영상 정보 조회"""
    db_shorts = crud.get_shorts_by_video_id(db=db, video_id=video_id)
    if not db_shorts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 영상을 찾을 수 없습니다."
        )
    return db_shorts

@app.get("/")
def read_root():
    return {"message": "API 서버가 실행 중입니다."}




@app.post("/shorts/vote", response_model=schemas.HashtagVoteResponse, status_code=status.HTTP_201_CREATED)
def vote_hashtag_endpoint(
    tag: str = Query(..., description="투표할 해시태그"),
    db: Session = Depends(get_db)
):
    
    """
    해시태그 투표 +1
    호출 예시: POST http://localhost:3000/shorts/vote?tag=귀멸의칼날
    """

    clean = tag.strip().lstrip('#')
    if not clean:
        raise HTTPException(status_code=400, detail="해시태그가 비어 있습니다.")

    return crud.vote_hashtag(db, clean)
    return crud.vote_hashtag(db, tag)


