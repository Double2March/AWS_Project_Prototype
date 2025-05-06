# 접속주소


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

### 초기개발 환경
```
sudo apt update

- git
sudo apt install git
git config -- global user.name "Name"
git config --global user.email "Email"

- aws cli
sudo apt install awscli -y
aws configure
aws sts get-caller-identity

- node Js
sudo apt install - y nodejs (20.19.x 버전이상)

-python
sudo apt install python
sudo apt install python3-pip

```
### front-end 환경설정
```

npm install vite
npm install axios react-router-dom
npm install -D @types/react-router-dom

npm run dev

npm install --save-dev @types/node << 환경변수 에러날 시
```
### back-end 환경설정
```

sudo apt install python-is-python3 << python3으로 default
sudo apt install [파이썬버전]-venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt << 가상환경 안에 설치


uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
### lambda
```
개발중
```
