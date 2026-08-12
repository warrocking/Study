# ABB RAPID–Python 서버 종합 학습 패키지

ABB RobotStudio와 RAPID를 처음 배우는 단계에서 시작해 Python 서버, TCP/HTTP, Robot Web Services(RWS), Tailscale 기반 원격 연결까지 이어지는 교육 자료입니다. 설명 자료와 실행 코드는 같은 개념·명령 ID·오류 모델을 공유합니다.

> 안전 경계: 이 자료는 교육 및 Virtual Controller 검증용입니다. 실제 로봇 작업에서는 현장 안전교육, 위험성 평가, 승인된 운전 모드·속도·인터록·복구 절차가 우선합니다. Tailscale과 Python 서버는 로봇 안전 기능이 아닙니다.

## 권장 학습 순서

1. `01_PPT/01_RAPID_RobotStudio_기초.pptx`로 언어·실행 구조·작성 스타일을 익힙니다.
2. `02_DOCX/01_ABB_RAPID_Python_Server_종합교재.docx` 1~5장을 함께 읽습니다.
3. `01_PPT/02_RAPID_모션_좌표계_IO_오류.pptx`와 워크북의 Virtual Controller 실습을 진행합니다.
4. `01_PPT/03_TCP_HTTP_Tailscale_네트워크.pptx`로 연결 계층과 진단 순서를 익힙니다.
5. `03_Code`를 Mock 모드로 실행하고 HTTP/TCP 클라이언트를 시험합니다.
6. `01_PPT/04_Python_Server_RAPID_통합.pptx`와 워크북의 통합 실습을 진행합니다.
7. 마지막에 `02_DOCX/03_RAPID_Server_명령어_문제해결_빠른참조.docx`를 현장 체크용으로 사용합니다.

## 산출물

### PPT 4종 — 총 137장

- `01_RAPID_RobotStudio_기초.pptx` — 29장: 역사, RobotStudio/RobotWare, 문법, 구조, 스타일
- `02_RAPID_모션_좌표계_IO_오류.pptx` — 34장: robtarget, tool/workobject, MoveJ/L/C, I/O, 오류·복구
- `03_TCP_HTTP_Tailscale_네트워크.pptx` — 33장: IP/port, TCP stream/framing, HTTP/TLS, RWS, Tailscale
- `04_Python_Server_RAPID_통합.pptx` — 41장: FastAPI, asyncio gateway, Mock/RWS, 테스트, 배포·운영

모든 슬라이드에는 발표자 노트와 공식 출처가 들어 있습니다.

### Word 3종

- `01_ABB_RAPID_Python_Server_종합교재.docx` — 약 75페이지, 71개 학습 주제
- `02_RAPID_Server_단계별_실습워크북.docx` — 약 39페이지, 18개 단계별 실습
- `03_RAPID_Server_명령어_문제해결_빠른참조.docx` — 약 27페이지, 24개 1페이지 참조표

### 실행 코드

- FastAPI HTTP API와 asyncio TCP Gateway
- 두 프로토콜이 공유하는 `BridgeService`
- 기본값이 안전한 `MockController`
- RobotWare/RWS 버전을 설정으로 분리한 최소 RWS 클라이언트
- CRLF pipe frame과 NDJSON parser
- command ID 기반 중복 억제 예제
- RAPID Socket client, RWS mailbox, 모션·I/O 예제 모듈
- Tailscale grants 예제(HTTP 8000, TCP 9100)
- 자동 테스트 13개

## 코드 빠른 시작

PowerShell에서 다음 명령을 실행합니다.

```powershell
cd C:\dev\Study\RobotStudio\RAPID_Server_Study\03_Code
uv sync --all-groups
uv run pytest -q
uv run ruff check .
uv run python -m abb_bridge
```

다른 터미널에서:

```powershell
cd C:\dev\Study\RobotStudio\RAPID_Server_Study\03_Code
uv run python scripts/http_client.py
uv run python scripts/tcp_client.py
```

기본 bind 주소는 localhost이고 controller mode는 Mock입니다. 실제 컨트롤러 쓰기는 설정에서 명시적으로 활성화하지 않는 한 꺼져 있습니다.

## 통합 승격 순서

```text
자동 테스트 → localhost Mock → RobotStudio Virtual Controller
→ Tailscale/subnet router → 승인된 읽기 전용 실제 컨트롤러
→ 권한·모드·안전 검증 후 제한된 쓰기
```

문제가 생기면 전원/모드 → IP/route → port/listener → TLS/인증 → frame → command/state 순서로 첫 실패 계층을 찾습니다.

## 기준 버전과 한계

- 설명 기준: OmniCore / RobotWare 8 중심
- 호환성 관점: RobotWare 6·7 예제의 차이를 별도 표기
- RobotStudio 문서 조사 기준: 2026.2
- RWS 1.x와 RWS 2.0은 인증·미디어 타입·리소스 계약이 다르므로 섞어 쓰지 않습니다.
- EGM은 별도 UDP/protobuf motion-guidance 선택지이며 이 기본 서버 실습에 포함하지 않습니다.

세부 내용은 `04_References/compatibility_matrix.md`, `safety_boundary.md`, `official_sources.txt`를 확인하십시오.

## 검증 결과

- Python: `pytest` 13개 통과, `ruff` 통과
- PPTX: 4개 파일 총 137장 렌더링, 자동 overflow 검사 통과, speaker notes 137개 확인
- DOCX: ZIP/OOXML 구조, Letter 용지·여백, 스타일·번호 매기기·표 geometry, 접근성 감사 통과
- DOCX의 LibreOffice 기반 최종 페이지 렌더링은 이 작업 환경에 LibreOffice가 없어 실행하지 못했습니다. 대신 구조·접근성·스타일 검사를 통과시켰습니다.

검증 상세와 해시는 `04_References/verification_report.md`에 기록합니다.
