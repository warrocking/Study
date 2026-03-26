# OpenCV 결과 서버 (분리 버전)

`portfolio.py` 원본을 건드리지 않고, 게임 결과를 웹 링크(QR)로 공유하기 위한 서버 구성입니다.

## 파일 구조
- `app.py`: Flask + SQLite 서버
- `templates/result_view.html`: 공유 링크 결과 페이지
- `static/result.css`: 결과 페이지 스타일
- `data/users_seed.json`: 기본 로그인 계정 시드
- `requirements.txt`: 서버 의존성
- `Procfile`: PaaS 실행 명령
- `render.yaml.example`: Render 배포 예시
- `run_server.bat`: 로컬 서버 실행

클라이언트 업로드 스크립트:`r`n- `../server_client/publish_latest_result_to_server.py``r`n- `../server_client/publish_latest_result_to_server.bat` (로컬 테스트용)``r`n- `../server_client/publish_to_public_server.bat` (배포 서버용)

## 1) 로컬 테스트
### 1-1. 의존성 설치
```powershell
C:\Study\OpenCV\.venv\Scripts\python.exe -m pip install -r C:\Study\OpenCV\Code\server_app\requirements.txt
```

### 1-2. 서버 실행
```powershell
C:\Study\OpenCV\Code\server_app\run_server.bat
```

### 1-3. 최신 결과 업로드 + 공유 QR 생성
```powershell
C:\Study\OpenCV\Code\server_client\publish_latest_result_to_server.bat
```

생성 파일:
- `C:\Study\OpenCV\Resource\Data\ServerShareQR\latest_share_url.txt`
- `C:\Study\OpenCV\Resource\Data\ServerShareQR\latest_share_qr.png`

## 2) Render 배포 절차 (핵심)
1. GitHub에 코드 업로드
2. Render에서 `New +` -> `Web Service`
3. 저장소 연결 후 아래 설정
   - Root Directory: `Code/server_app`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
4. Environment Variables 설정
   - `PUBLIC_BASE_URL=https://<발급도메인>`
   - `GAME_SERVER_DB_PATH=/var/data/game_server.db`
   - `ADMIN_LOGIN_ID=admin` (예시)
   - `ADMIN_PASSWORD=1234` (예시)
   - `ADMIN_NICKNAME=admin`
5. Persistent Disk 추가
   - Mount Path: `/var/data`
   - Size: 1GB 이상
6. 배포 완료 후 `https://<도메인>/api/health` 확인

## 3) 클라이언트에서 서버 주소 변경
`publish_latest_result_to_server.bat`에서:
```bat
set GAME_SERVER_URL=https://<발급도메인>
```
로 바꾼 뒤 실행하면, 공유 QR이 공용 인터넷 링크로 생성됩니다.

## 4) API 요약
- `GET /api/health`
- `POST /api/login`
- `POST /api/results`
- `GET /api/results/latest/<login_id>`
- `POST /api/results/<result_id>/share`
- `GET /api/share/<share_code>`
- `GET /r/<share_code>`

## 5) 운영 전 주의
- 현재 비밀번호는 데모용 평문 비교입니다.
- 실제 운영은 `bcrypt` 해시 + HTTPS 필수입니다.
- 공유 코드 만료시간(`expire_minutes`) 정책을 운영 기준으로 조정하세요.

