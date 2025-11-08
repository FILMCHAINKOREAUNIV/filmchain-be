from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, crud, services
from .database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="쇼츠 조회수 확인 API",
)

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

    # DB에 저장
    db_shorts = crud.create_shorts(db=db, video_id=video_id, url=shorts_request.url)
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
    #호출 예시: GET http://localhost:8000/shorts/compare?tag=movie1&tag=movie2
    # 태그별 조회수 통계 반환
    stats = crud.get_stats_for_hashtags(db=db, tags=tags)
    return stats

@app.get("/")
def read_root():
    return {"message": "API 서버가 실행 중입니다."}