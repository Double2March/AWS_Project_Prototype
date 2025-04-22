# 진행상황
|Front|Backend|api|
|-|-|-|
|React|python|fast api|
```
- 채팅주고 받는 서비스 클라이언트 완성 (사실상 로컬서버)

- 클라우드 아키텍처 생성하고 API키 입력하면 됨 (25일 목표)
```

<br>

# Build 방법

```
git reposotory

git clone https://github.com/Double2March/AWS_Project_Prototype.git
```
```
front-end 환경설정

npm create vite@latest . -- --template react-ts
npm install axios react-router-dom
npm install -D @types/react-router-dom

npm run dev
```
```python
back-end 환경설정

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8000

```
```
lambda 배포

```
---