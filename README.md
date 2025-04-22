# 접속주소
### http://3.88.117.24:5173/

<br/>

# 진행상황
|Front|Backend|api|
|-|-|-|
|React|python|fast api|

```
- 채팅주고 받는 서비스 클라이언트 완성 (사실상 로컬서버)

- 클라우드 아키텍처 생성하고 API키 입력하면 됨 (25일 목표)
```

|![Image](https://github.com/user-attachments/assets/3aaf3bd6-0cca-4748-a38c-5c0731245c94)|![Image](https://github.com/user-attachments/assets/9784421b-82ae-431f-8f3a-6555d51a3707)|![Image](https://github.com/user-attachments/assets/59a2aea2-b6a6-4b25-a66a-fe618d241523)|
|-|-|-|

<br>

# Build 방법

### git reposotory
```
git clone https://github.com/Double2March/AWS_Project_Prototype.git
```
### front-end 환경설정
```
npm create vite@latest . -- --template react-ts
npm install axios react-router-dom
npm install -D @types/react-router-dom

npm run dev
```
### back-end 환경설정
```python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
### lambda
```
개발중
```
