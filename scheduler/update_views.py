import time
from app.database import SessionLocal, engine
from app.models import Base

def update_views():
    print("스케줄러: 'update_views' 작업을 시작합니다...")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        pass
        print("스케줄러: 작업 완료.")
    except Exception as e:
        print(f"스케줄러: 작업 중 오류 발생 - {e}")
    finally:
        db.close()


if __name__ == "__main__":
    update_views()
    