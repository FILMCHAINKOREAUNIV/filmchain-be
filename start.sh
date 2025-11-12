#!/bin/sh

# sh 스크립트가 에러 발생 시 즉시 중지되도록 설정
set -e

echo "Starting Gunicorn API server in background..."
# 1. Gunicorn 서버를 "백그라운드"에서 실행 (&)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 &

echo "Starting Scheduler loop in foreground..."
# 2. DB가 준비될 때까지 10초 대기
sleep 10

#    (이 프로세스가 살아있는 한, Render는 Web Service를 "Running"으로 인식)
while true; do
    echo "Scheduler: 'update_views' 작업 실행..."
    python -m scheduler.update_views
    echo "Scheduler: 작업 완료. 10분(600초)간 대기..."
    sleep 600
done