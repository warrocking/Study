# TurtleBot Fleet Communication Server

이 디렉토리는 서버 노트북 담당자가 관리하는 통신 코드입니다.

Fleet JSON v0.4 계약은 `JSON_CONTRACT_V4.md`에 고정합니다. 현재 `control_laptop_client.py`는 v4 `operator_request`를 생성하고, `fleet_server_main.py`는 v4 요청을 v4 `operator_response`로 처리합니다. Robot Agent 클라이언트는 v4 `server_command`를 받아 v4 `agent_result`를 반환해야 합니다. `mock_robot_agent.py`는 실제 ROS2 제어가 아니라 이 v4 통신 구조를 확인하기 위한 테스트용 Agent입니다.

목표는 제어용 노트북 담당자가 UI/UX를 따로 만들더라도, 아래 파일을 실행하거나 import해서 서버와 바로 통신할 수 있게 만드는 것입니다.

```bash
python3 control_laptop_client.py
```

서버 노트북에서는 아래 파일을 실행합니다.

```bash
python3 fleet_server_main.py
```

## 파일 구성

```text
server/
├── fleet_server_main.py        # 서버 노트북에서 실행하는 Fleet Server
├── fleet_protocol.py           # 서버/Agent 공통 JSONL 통신 유틸
├── control_laptop_client.py    # 제어용 노트북 담당자에게 넘길 수 있는 단독 실행 클라이언트
├── mock_robot_agent.py         # ROS2 없이 통신 구조만 검증하는 테스트용 Robot Agent
├── server_config.json          # 서버 포트, 제한값, 안전 설정
├── client_info.json            # Robot Command Client IP/port와 robot_id 목록
├── control_info.json           # 제어 UI 컴퓨터 IP/SSH/이미지 수신 경로
├── config/
│   └── action_policy.json      # Fleet JSON v0.4 action 우선순위/허용 모드 정책표
├── JSON_CONTRACT_V4.md         # Fleet JSON v0.4 고정 계약 문서
├── CLIENT_JSON_RULES_PROMPT.md # Robot Agent 담당자용 JSON 상세 규칙
├── CLIENT_OPERATION_FLOW_PROMPT.md # Robot Agent 담당자용 전체 구동 흐름
├── CONTROL_UI_FILE_TRANSFER_PROMPT.md # 제어 UI 이미지 전송/닫기 보고 규칙
└── control_client_config.json  # 제어용 노트북 클라이언트 기본 접속 설정
```

## 통신 규칙

전송 방식은 TCP + UTF-8 + NDJSON입니다.

```text
1. TCP socket을 연결한다.
2. JSON 객체 1개를 한 줄 문자열로 보낸다.
3. 메시지 끝은 반드시 \n 이다.
4. 응답도 JSON 객체 1개 + \n 으로 받는다.
5. 숫자는 숫자로, true/false는 boolean으로 보낸다.
```

즉, 실제 전송 데이터는 이런 형태입니다.

```text
{"v":4,"mt":"operator_request","msg_id":"MSG_20260619_OPERATOR_REQUEST_000001",...}\n
```

## 제어용 노트북 -> 서버

제어용 노트북은 v4 `operator_request`를 보냅니다.

```json
{
  "v": 4,
  "mt": "operator_request",
  "msg_id": "MSG_20260619_OPERATOR_REQUEST_000001",
  "ts": "2026-06-19T10:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "auth": {
    "token": "team_demo_token"
  },
  "user": "operator_1",
  "command": {
    "command_id": "CMD_20260619_MOVE_FORWARD_TB3_1_000001",
    "group_id": null,
    "job_id": null,
    "command_seq": null,
    "command_revision": 0,
    "action": "move_forward",
    "target_scope": "single",
    "targets": ["tb3_1"],
    "params": {
      "lx": 0.05,
      "az": 0.0,
      "dur": 2.0,
      "hz": 10,
      "stop": true
    },
    "expects": {
      "response_type": "sync",
      "status_followup": false
    },
    "timeout_sec": 5.0
  },
  "ui_context": {
    "client": "control_laptop_client.py",
    "screen": "main_control",
    "button": "forward"
  }
}
```

지원 action:

```text
move_forward
move_backward
turn_left
turn_right
custom_move
robot_stop
all_stop
status_request
ping
```

UI 버튼 이름은 `stop`을 써도 됩니다. `control_laptop_client.py`는 전송 전에 v4 표준 action인 `robot_stop`으로 정규화합니다.

지원 target:

```text
tb3_1
tb3_2
tb3_3
all
```

현재 1차 실제 연결 테스트에서는 `client_info.json`에서 `tb3_3`만 활성화했습니다. 제어 UI 기본 대상도 `tb3_3`으로 맞춰 두었습니다.

기본 설정에서는 `target=all` 이동 명령은 막혀 있습니다. `all_stop`은 허용됩니다.

## 서버 -> Robot Agent

v4 `operator_request`로 들어온 요청은 v4 `server_command`로 Robot Command Client에 전달합니다. 서버는 TurtleBot별 IP를 관리하지 않습니다. 서버는 `client_info.json`의 공통 클라이언트 IP/port로 접속하고, JSON 안의 `command.robot_id`로 `tb3_1`, `tb3_2`, `tb3_3` 중 어느 로봇 명령인지 전달합니다.

Robot Command Client는 `command.robot_id`를 읽고 자기 코드/설정에 따라 해당 TurtleBot에 ROS2 명령을 내려야 합니다. 처리 결과는 v4 `agent_result`로 서버에 반환합니다. 현재 `mock_robot_agent.py`는 이 v4 흐름을 통신 테스트용으로 지원합니다.

서버는 v4 `heartbeat_request`로 Robot Agent 생존 상태를 확인할 수 있습니다. 요청에 `include_state_report=true`가 포함되면 Agent는 같은 TCP 연결에서 `heartbeat_response` 다음 줄에 `state_report`를 함께 반환할 수 있습니다.

### Legacy 참고용

과거 v1/v3 구조는 현재 팀 작업 기준이 아닙니다. 새 제어 UI와 새 Robot Agent 클라이언트는 반드시 v4 `operator_request` / `server_command` / `agent_result`를 사용하세요.

과거 legacy 경로에서는 아래 조건으로 결과를 비교했습니다. 새 구현에서는 `JSON_CONTRACT_V4.md`의 v4 매칭 규칙을 따릅니다.

```text
command.id == result.ref
command.job == result.job
command.to == result.from
command.op == result.op
```

## 서버 응답

제어용 노트북은 항상 `operator_response`를 받습니다.

v4 서버 응답은 `operator_response`입니다. 핵심 필드는 아래입니다.

```text
v
mt
msg_id
ref
source
dest
schema
ok
code
message
command
results
err
ui_hint
trace
```

성공 예시는 `JSON_CONTRACT_V4.md`의 `operator_response` 절을 기준으로 보세요.

## 실행 순서

서버 노트북:

```bash
cd ~/openCV/server
python3 fleet_server_main.py
```

제어용 노트북이 요청을 보내면 서버 터미널에는 아래 흐름이 보입니다.

```text
[CONTROL CONNECT] ...
[LOG] operator_requests/operator_request ...
[OPERATOR REQUEST] ...
[LOG] commands/server_command ...
[COMMAND OUT] ...
[LOG] results/agent_result ...
[RESULT IN] ...
[LOG] operator_responses/operator_response ...
[OPERATOR RESPONSE] ...
[CONTROL CLOSE] ...
```

`status_request`처럼 서버 상태만 묻는 요청은 `commands/results` 없이 `operator_requests/operator_responses`만 남습니다.

제어용 노트북:

```bash
python3 control_laptop_client.py
```

서버 IP가 다르면 `control_client_config.json`의 `server_ip`를 수정합니다.

## 통신만 로컬 테스트

실제 Robot Agent 클라이언트가 아직 없으면 터미널 3개로 mock 통신 테스트를 할 수 있습니다. 이 테스트는 JSON 통신 구조 검증용이며 실제 TurtleBot 동작 검증이 아닙니다.

터미널 1:

```bash
cd ~/openCV/server
python3 mock_robot_agent.py
```

터미널 2:

```bash
cd ~/openCV/server
python3 fleet_server_main.py
```

터미널 3:

```bash
cd ~/openCV/server
python3 control_laptop_client.py --server-ip 127.0.0.1
```

로컬 mock 테스트를 할 때만 서버의 `4000` 포트와 충돌하지 않도록 `client_info.json`의 `robot_command_client.ip`를 `127.0.0.1`, `port`를 `5000`으로 임시 변경할 수 있습니다. 실제 클라이언트 연결 설정은 `192.168.3.63:4000`입니다.

## UI 담당자가 import해서 쓰는 방법

UI 버튼 이벤트에서 아래처럼 호출하면 됩니다.

```python
from control_laptop_client import ControlServerClient

client = ControlServerClient("192.168.3.61", 4000, timeout=40.0)

def on_forward_button():
    response = client.move_forward("tb3_3")
    print(response)

def on_all_stop_button():
    response = client.all_stop()
    print(response)
```

UI/UX는 이 응답의 `ok`, `code`, `message`, `results`, `err`, `ui_hint`를 우선 화면에 표시하면 됩니다.

제어용 UI 담당자에게 새 작업을 지시할 때는 `CONTROL_UI_PROMPT.md`, `CONTROL_UI_FILE_TRANSFER_PROMPT.md`, `JSON_CONTRACT_V4.md`를 함께 전달하세요.
