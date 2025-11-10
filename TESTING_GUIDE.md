# 백엔드-프론트엔드 연결 테스트 가이드

## 개요
이 가이드는 릴스 URL을 입력하면 조회수가 즉시 조회되는 기능을 테스트하는 방법을 설명합니다.

## 주요 변경사항
- **즉시 조회수 조회**: URL 등록 시 YouTube API를 호출하여 조회수를 즉시 가져옵니다.
- **조회수 업데이트 엔드포인트**: 이미 등록된 영상의 조회수를 수동으로 업데이트할 수 있는 API가 추가되었습니다.

## 사전 준비

### 1. 환경 변수 설정
`.env` 파일에 다음 환경 변수가 설정되어 있어야 합니다:

```env
# 데이터베이스 설정
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# YouTube API 키 (필수)
YOUTUBE_API_KEY=your_youtube_api_key
```

### 2. YouTube API 키 발급
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 프로젝트 생성 또는 기존 프로젝트 선택
3. YouTube Data API v3 활성화
4. API 키 생성
5. `.env` 파일에 `YOUTUBE_API_KEY`로 설정

## 백엔드 실행 방법

### 방법 1: Docker Compose 사용 (권장)

```bash
cd filmchain-be
docker-compose up
```

이 명령으로 다음이 실행됩니다:
- PostgreSQL 데이터베이스 (포트 5434)
- FastAPI 서버 (포트 8000)
- 조회수 업데이트 스케줄러 (10분마다 실행)

### 방법 2: 로컬 실행

#### 1. 데이터베이스 설정
PostgreSQL이 설치되어 있고 실행 중이어야 합니다.

#### 2. Python 가상 환경 설정
```bash
cd filmchain-be
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. 데이터베이스 연결 설정
`app/database.py`에서 데이터베이스 연결 정보를 확인하세요.

#### 4. 서버 실행
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 프론트엔드 설정

### API URL 설정
`filmchain_prototype/flutter_application_1/lib/config/api_config.dart` 파일에서 API URL을 설정하세요:

```dart
class ApiConfig {
  // 로컬 개발 (웹/데스크톱)
  static const String baseUrl = 'http://localhost:8000';
  
  // Android 에뮬레이터
  // static const String baseUrl = 'http://10.0.2.2:8000';
  
  // iOS 시뮬레이터
  // static const String baseUrl = 'http://localhost:8000';
  
  // 실제 디바이스 (컴퓨터의 IP 주소로 변경)
  // 예: static const String baseUrl = 'http://192.168.0.100:8000';
}
```

**실제 디바이스에서 테스트하는 경우:**
1. 백엔드 서버가 실행 중인 컴퓨터의 IP 주소 확인
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig` 또는 `ip addr`
2. `api_config.dart`에서 해당 IP 주소로 변경
3. 백엔드 서버가 `--host 0.0.0.0`으로 실행되었는지 확인

## 테스트 방법

### 1. 백엔드 API 테스트

#### API 서버 상태 확인
```bash
curl http://localhost:8000/
```

예상 응답:
```json
{"message": "API 서버가 실행 중입니다."}
```

#### 릴스 URL 등록 테스트
```bash
curl -X POST http://localhost:8000/shorts \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'
```

예상 응답:
```json
{
  "id": 1,
  "video_id": "VIDEO_ID",
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "hashtags": "#tag1 #tag2",
  "view_count": 12345,
  "created_at": "2024-01-01T00:00:00"
}
```

**중요**: `view_count`가 0이 아닌 실제 조회수가 표시되어야 합니다.

#### 특정 영상 조회
```bash
curl http://localhost:8000/shorts/VIDEO_ID
```

#### 조회수 업데이트 (수동)
```bash
curl -X PUT http://localhost:8000/shorts/VIDEO_ID/refresh
```

### 2. 프론트엔드 테스트

#### 1. 프론트엔드 실행
```bash
cd filmchain_prototype/flutter_application_1
flutter run
```

#### 2. 릴스 등록 테스트
1. 앱에서 "릴스 등록하기" 버튼 클릭
2. YouTube URL 입력 (예: `https://www.youtube.com/watch?v=VIDEO_ID`)
3. "등록" 버튼 클릭
4. 조회수가 즉시 표시되는지 확인

#### 3. 조회수 확인
- 등록 직후 조회수가 표시되어야 합니다
- 조회수가 0이 아닌 실제 YouTube 조회수가 표시되어야 합니다
- 좌우 항목의 조회수를 비교하는 바가 정상적으로 표시되어야 합니다

## 문제 해결

### 조회수가 0으로 표시됨
1. **YouTube API 키 확인**
   - `.env` 파일에 `YOUTUBE_API_KEY`가 설정되어 있는지 확인
   - API 키가 유효한지 확인
   - YouTube Data API v3가 활성화되어 있는지 확인

2. **백엔드 로그 확인**
   - 백엔드 콘솔에서 오류 메시지 확인
   - "조회수 조회 실패" 메시지가 있는지 확인

3. **네트워크 확인**
   - 백엔드 서버가 YouTube API에 접근할 수 있는지 확인
   - 방화벽 설정 확인

### CORS 오류
- 백엔드 `main.py`에 CORS 미들웨어가 추가되어 있는지 확인
- `allow_origins=["*"]` 설정 확인

### 네트워크 연결 오류
- 백엔드 서버가 실행 중인지 확인
- API URL이 올바른지 확인
- 실제 디바이스에서 테스트하는 경우 IP 주소가 올바른지 확인
- 방화벽 설정 확인

### 중복 등록 오류
- 이미 등록된 영상의 경우 409 Conflict 오류가 발생합니다
- 다른 영상으로 테스트하거나, 데이터베이스에서 해당 레코드를 삭제하세요

## 지원하는 YouTube URL 형식

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- `https://m.youtube.com/watch?v=VIDEO_ID`

## API 엔드포인트

### POST /shorts
YouTube URL을 등록하고 조회수를 즉시 조회합니다.

**요청:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**응답:**
```json
{
  "id": 1,
  "video_id": "VIDEO_ID",
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "hashtags": "#tag1 #tag2",
  "view_count": 12345,
  "created_at": "2024-01-01T00:00:00"
}
```

### GET /shorts/{video_id}
특정 영상 정보를 조회합니다.

### PUT /shorts/{video_id}/refresh
특정 영상의 조회수를 즉시 업데이트합니다.

### GET /shorts/compare
해시태그별 조회수 통계를 조회합니다.

## 다음 단계

- [ ] 조회수 실시간 업데이트 기능 (WebSocket 또는 폴링)
- [ ] 에러 처리 개선
- [ ] 로딩 상태 개선
- [ ] 조회수 변경 히스토리 추적

