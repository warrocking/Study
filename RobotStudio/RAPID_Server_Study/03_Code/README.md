# ABB RAPID Bridge Lab

이 프로젝트는 RAPID, TCP 프레이밍, HTTP API, RWS의 역할을 분리해 학습하는 Python 3.12 실습 코드입니다. 기본 모드는 실제 로봇 대신 `MockController`를 사용합니다.

## 구조

- `src/abb_bridge/main.py`: FastAPI 애플리케이션과 라이프사이클
- `service.py`: HTTP와 TCP가 함께 사용하는 명령 처리 계층
- `socket_gateway.py`: `asyncio` TCP 서버
- `protocol.py`: CRLF 구분 RAPID 프레임과 NDJSON 프레임
- `rws_client.py`: RW6의 RWS 1.x와 RW7/8의 RWS 2.0 차이를 고려한 최소 클라이언트
- `rapid/`: RobotStudio Virtual Controller에서 검토할 RAPID 모듈
- `tailscale/`: 연구실용 최소 권한 정책 예시. 그대로 적용하지 말고 주소와 계정을 교체해야 합니다.

## 1. 설치

PowerShell에서 다음을 실행합니다.

```powershell
cd C:\dev\Study\RobotStudio\RAPID_Server_Study\03_Code
uv sync --all-groups
Copy-Item .env.example .env
```

`.env`의 API 키를 바꾸고, 첫 실습에서는 `ABB_BRIDGE_CONTROLLER_MODE=mock`을 유지합니다.

## 2. 서버 실행

```powershell
$env:ABB_BRIDGE_START_TCP_GATEWAY='true'
uv run python -m abb_bridge
```

- 상태 확인: `http://127.0.0.1:8000/health`
- Swagger UI: `http://127.0.0.1:8000/docs`
- TCP 게이트웨이: `127.0.0.1:9100`

## 3. 클라이언트 실습

다른 PowerShell 창에서:

```powershell
uv run python scripts\tcp_client.py --format pipe
uv run python scripts\tcp_client.py --format json
uv run python scripts\http_client.py --key lab-only-change-me
```

RAPID 클라이언트는 `rapid/SocketBridgeClient.mod`를 사용합니다. Virtual Controller와 Python 서버가 서로 다른 컴퓨터에 있으면 `SERVER_IP`를 서버 노트북의 Tailscale IP 또는 MagicDNS 이름으로 바꾸고, 방화벽과 Tailscale Grants가 TCP 9100을 허용하는지 확인합니다.

## 4. 테스트와 정적 검사

```powershell
uv run pytest -q
uv run ruff check .
```

## 프로토콜

RAPID용 짧은 ASCII 프레임:

```text
PING|rapid-001\r\n
STATUS|rapid-002\r\n
SET_DO|rapid-003|doGrip|1\r\n
```

Python용 NDJSON 프레임:

```json
{"version":1,"id":"cmd-001","type":"ping","payload":{}}
```

TCP는 메시지 단위가 아닌 바이트 스트림이므로 `send()` 한 번과 `recv()` 한 번이 반드시 대응하지 않습니다. 이 실습은 각 메시지를 LF 또는 CRLF로 끝내고, 최대 8 KiB를 넘는 프레임을 거부합니다.

## RWS 연결 전 체크

1. RobotWare 버전과 RWS API 버전을 확인합니다. RW7/8은 RWS 2.0의 HTTPS와 버전 미디어 타입을 우선합니다.
2. Virtual Controller에서 읽기 전용 `get_system()`과 `get_rapid_symbol()`부터 확인합니다.
3. 실제 컨트롤러의 자체 서명 인증서를 무조건 우회하지 말고, 신뢰할 인증서 또는 제한된 실습 환경을 준비합니다.
4. `ABB_BRIDGE_RWS_ALLOW_WRITES=false`를 유지한 상태에서 연결과 응답 파싱을 먼저 검증합니다.
5. 쓰기·실행·모션 기능은 UAS 권한, mastership, 운전 모드, 셀 안전 검토를 별도로 거친 뒤 확장합니다.

## 안전 경계

이 코드는 통신과 서버 구조를 가르치는 교육용 예제입니다. 비상 정지, 보호 정지, 안전 속도, 안전 구역, 펜스·도어 인터록 같은 안전 기능을 구현하거나 대체하지 않습니다. Tailscale 연결 성공은 로봇 운전 허가가 아니며, WAN/VPN 경로는 결정론적 모션 제어 루프로 사용하지 않습니다. 실제 로봇에서는 ABB 매뉴얼, 위험성 평가, 현장 안전 절차와 권한 체계를 우선해야 합니다.

