#!/bin/bash

# 가상환경 생성 (이미 있으면 넘어감)
if [ ! -d "venv" ]; then
    echo "가상환경 생성 중..."
    python -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 필요한 라이브러리 설치 (이미 설치되어 있으면 넘어감)
pip install -r requirements.txt

# FastAPI 서버 실행
#uvicorn main:app --reload --host 0.0.0.0 --port 8000
nohup uvicorn main:app --host 0.0.0.0 --port 8000 &
