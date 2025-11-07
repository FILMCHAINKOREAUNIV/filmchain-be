# Dockerfile
FROM python:3.10-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

# B개발자도 쓸 라이브러리 포함
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# A개발자의 app, B개발자의 scheduler 폴더를 모두 복사
COPY ./app /code/app
COPY ./scheduler /code/scheduler

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]