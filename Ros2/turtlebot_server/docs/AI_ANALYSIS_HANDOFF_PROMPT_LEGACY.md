# TurtleBot Fleet Server v4 현재 코드/JSON 분석 요청 프롬프트

당신은 TurtleBot 3대 협업 제어 시스템 프로젝트를 함께 분석하는 AI입니다.

이 프롬프트의 목적은 현재 서버 담당자가 작성한 코드와 JSON 규칙, 설정 파일, 통신 구조를 빠르고 정확하게 이해하고, 다른 담당자의 코드와 연결할 때 충돌이 생기지 않도록 분석하는 것입니다.

중요합니다. 처음부터 코드를 수정하지 말고, 먼저 구조를 읽고 분석하세요. 수정이 필요하다고 판단되면 반드시 어떤 파일의 어떤 정보가 왜 문제인지 설명한 뒤, 서버 담당자와 합의하고 수정하세요.

## 0. 프로젝트 배경

이 프로젝트는 TurtleBot 3대를 협업 제어하기 위한 팀 프로젝트입니다.

전체 구조는 아래 3단 구조입니다.

```text
제어 UI / HMI
  -> operator_request JSON
Fleet Server
  -> server_command JSON
Robot Command Client
  -> ROS2 /cmd_vel publish 또는 TurtleBot 제어
TurtleBot3
```

응답 흐름은 반대입니다.

```text
TurtleBot3 / Robot Command Client 처리 결과
  -> agent_result JSON
Fleet Server
  -> operator_response JSON
제어 UI / HMI
```

Control UI는 TurtleBot이나 Robot Command Client에 직접 명령하지 않습니다.

Robot Command Client도 Control UI와 직접 통신하지 않습니다.

반드시 아래 구조를 유지해야 합니다.

```text
Control UI <-> Fleet Server <-> Robot Command Client <-> TurtleBot3
```

현재 서버 담당자의 역할은 Fleet Server를 관리하고, 제어 UI 담당자와 Robot Command Client 담당자가 같은 JSON 규칙을 기준으로 작업할 수 있도록 규칙과 연결 구조를 안정적으로 유지하는 것입니다.

## 1. 가장 중요한 현재 설계 방향

과거에는 서버가 `tb3_1`, `tb3_2`, `tb3_3` 각각의 IP/port를 직접 알고 각 로봇 Agent로 명령을 보내는 구조를 고려했습니다.

하지만 현재 설계는 다릅니다.

현재 서버는 로봇별 IP를 직접 관리하지 않습니다.

서버는 하나의 공통 Robot Command Client로 JSON 명령을 보냅니다.

그 JSON 안에 `command.robot_id`가 들어갑니다.

Robot Command Client는 `command.robot_id`를 읽고, 자기 내부 규칙에 따라 실제 TurtleBot 번호에 맞게 명령을 보내야 합니다.

즉, 서버는 아래 정보만 관리합니다.

```text
Robot Command Client의 IP
Robot Command Client의 port
Robot Command Client의 id
각 robot_id의 이름/topic/ROS_DOMAIN_ID 같은 메타데이터
```

서버가 관리하지 않는 것:

```text
각 TurtleBot의 실제 IP
각 TurtleBot에 직접 SSH 접속하는 정보
각 TurtleBot 내부 ROS2 실행 방식
Robot Command Client 내부 라우팅 방식
```

따라서 다른 AI가 분석할 때, 서버가 로봇별 IP를 갖고 있지 않다고 해서 누락이라고 판단하지 마세요. 이것은 의도된 구조입니다.

## 2. 현재 중요한 IP와 포트

현재 설정 기준입니다.

```text
Fleet Server public_ip: 192.168.3.61
Fleet Server control_port: 4000

Control UI IP: 192.168.3.59
Control UI SSH user: ubuntu
Control UI SSH port: 22
Control UI image cache dir: /home/ubuntu/openCV/cache/images

Robot Command Client IP: 192.168.3.63
Robot Command Client port: 4000
Robot Command Client id: robot_command_client
```

주의:

```text
현재 1차 실제 연결 테스트의 Robot Command Client IP는 192.168.3.63입니다.
실제 클라이언트 컴퓨터 IP가 다시 바뀌면 client_info.json의 robot_command_client.ip를 최신화해야 합니다.
현재는 TurtleBot 1대만 우선 연결하므로 활성 robot_id는 tb3_3입니다.
```

IP가 바뀌었을 때 수정해야 하는 파일:

```text
서버 IP:
server_config.json -> server.public_ip

제어 UI가 서버에 접속할 IP:
control_client_config.json -> server_ip

서버가 제어 UI로 이미지 전송할 IP:
control_info.json -> control_ui.ip

서버가 Robot Command Client로 명령 보낼 IP:
client_info.json -> robot_command_client.ip
```

## 3. 우선 읽어야 하는 파일 순서

다른 AI는 아래 순서대로 파일을 읽어야 합니다.

```text
1. README.md
2. JSON_CONTRACT_V4.md
3. server_config.json
4. client_info.json
5. control_info.json
6. control_client_config.json
7. config/action_policy.json
8. fleet_protocol.py
9. fleet_server_main.py
10. control_laptop_client.py
11. mock_robot_agent.py
12. CONTROL_UI_PROMPT.md
13. CONTROL_UI_FILE_TRANSFER_PROMPT.md
14. CLIENT_JSON_RULES_PROMPT.md
15. CLIENT_OPERATION_FLOW_PROMPT.md
```

이 순서가 중요한 이유:

```text
README.md는 전체 실행과 파일 역할을 설명합니다.
JSON_CONTRACT_V4.md는 v4 JSON 계약의 기준입니다.
server_config.json은 서버가 어떤 설정 파일을 읽는지 알려줍니다.
client_info.json은 Robot Command Client 연결 정보를 갖습니다.
control_info.json은 제어 UI SSH/이미지 전송 정보를 갖습니다.
control_client_config.json은 제어 테스트 클라이언트가 서버에 접속할 정보를 갖습니다.
action_policy.json은 action별 허용/우선순위/모드 정책을 갖습니다.
fleet_protocol.py는 공통 JSON 생성/검증 유틸입니다.
fleet_server_main.py는 실제 Fleet Server 본체입니다.
control_laptop_client.py는 제어 UI 담당자가 import하거나 테스트용으로 실행하는 클라이언트입니다.
mock_robot_agent.py는 실제 TurtleBot 없이 통신을 검증하기 위한 mock입니다.
나머지 PROMPT md 파일들은 담당자 간 업무 지시 및 규칙 공유용입니다.
```

## 4. 파일별 역할

### 4.1 server_config.json

서버 전체 설정 파일입니다.

관리하는 정보:

```text
서버 이름
서버 bind_ip
서버 public_ip
제어 요청을 받을 control_port
socket timeout
인증 사용 여부
기본 이동 파라미터
속도/시간 제한값
OpenCV safety event 경로
사용할 정보 파일 이름
파일 전송 설정
로그 저장 위치
```

현재 핵심 값:

```json
{
  "server": {
    "name": "fleet_server_v4",
    "bind_ip": "0.0.0.0",
    "public_ip": "192.168.3.61",
    "control_port": 4000
  },
  "files": {
    "client_info_file": "client_info.json",
    "control_info_file": "control_info.json",
    "action_policy_file": "config/action_policy.json"
  },
  "file_transfer": {
    "enabled": true,
    "rsync_bin": "rsync",
    "rsync_timeout": 30,
    "server_image_dir": "sync/to_control/images"
  }
}
```

이 파일은 `fleet_server_main.py`가 시작할 때 읽습니다.

### 4.2 client_info.json

Robot Command Client와 로봇 메타데이터를 관리하는 파일입니다.

관리하는 정보:

```text
Robot Command Client id
Robot Command Client IP
Robot Command Client port
Robot Command Client protocol
Robot Command Client SSH 관련 확장 정보
tb3_1/tb3_2/tb3_3의 robot_id
각 robot_id의 topic
각 robot_id의 ROS_DOMAIN_ID
각 robot_id enabled 여부
```

현재 구조:

```json
{
  "robot_command_client": {
    "id": "robot_command_client",
    "ip": "192.168.3.63",
    "port": 4000
  },
  "robots": {
    "tb3_1": {
      "robot_id": "tb3_1",
      "topic": "/tb3_1/cmd_vel",
      "ros_domain_id": 31,
      "enabled": true
    }
  }
}
```

주의:

```text
robots 안에 있는 tb3_1/tb3_2/tb3_3는 서버가 직접 접속할 대상 IP가 아닙니다.
서버는 모든 로봇 명령을 robot_command_client.ip:port로 보냅니다.
로봇 구분은 server_command.command.robot_id로 합니다.
```

`fleet_server_main.py`는 이 파일을 읽어서:

```text
server_command.dest 값을 robot_command_client로 설정
server_command.command.robot_id 값을 tb3_1/tb3_2/tb3_3 중 하나로 설정
server_command.command.ros.topic을 client_info.json의 topic으로 설정
server_command.command.ros.domain_id를 client_info.json의 ros_domain_id로 설정
TCP 접속 대상은 robot_command_client.ip:robot_command_client.port로 설정
```

### 4.3 control_info.json

서버가 제어 UI 컴퓨터와 SSH/rsync 기반 이미지 전송을 할 때 쓰는 파일입니다.

관리하는 정보:

```text
Control UI id
Control UI IP
Control UI hostname
Control UI SSH user
Control UI SSH port
Control UI SSH connect_timeout
SSH identity_file
제어 컴퓨터의 이미지 cache directory
이미지 전송 방식
기본 서버 이미지 경로
제어 UI가 이미지 창을 닫은 뒤 삭제해야 하는지 여부
```

현재 구조:

```json
{
  "control_ui": {
    "ip": "192.168.3.59",
    "user": "ubuntu",
    "ssh": {
      "enabled": true,
      "port": 22,
      "connect_timeout": 5,
      "identity_file": ""
    },
    "paths": {
      "image_cache_dir": "/home/ubuntu/openCV/cache/images"
    }
  },
  "image_transfer": {
    "method": "rsync_over_ssh",
    "direction": "server_push",
    "default_server_path": "sync/to_control/images/tb3_1_latest_map.png",
    "delete_after_view": true
  }
}
```

`fleet_server_main.py`는 `image_request`를 받으면 이 파일을 읽은 값으로:

```text
서버의 이미지 파일을 찾음
제어 컴퓨터의 image_cache_dir 경로로 rsync 전송
전송 성공/실패 결과를 file_transfers 로그에 저장
operator_response로 제어 UI에 결과 반환
```

SSH/rsync는 비대화식으로 실행되어야 합니다.

현재 서버 코드는 rsync 실행 시 SSH 옵션을 붙입니다.

```text
BatchMode=yes
ConnectTimeout=5
StrictHostKeyChecking=accept-new
```

이유:

```text
서버 프로세스가 SSH password 입력 또는 host-key 확인 프롬프트를 기다리며 멈추는 문제를 막기 위해서입니다.
```

### 4.4 control_client_config.json

제어용 테스트 클라이언트 또는 UI 코드가 서버에 접속할 때 쓰는 파일입니다.

관리하는 정보:

```text
protocol_version
server_ip
server_port
timeout
auth_token
user
default_target
기본 이동 파라미터
```

현재 구조:

```json
{
  "protocol_version": 4,
  "server_ip": "192.168.3.61",
  "server_port": 4000,
  "timeout": 40,
  "auth_token": "team_demo_token",
  "user": "operator_1",
  "default_target": "tb3_1"
}
```

주의:

```text
이 파일은 서버 본체가 읽는 파일이 아닙니다.
control_laptop_client.py가 읽는 제어 클라이언트용 설정입니다.
```

### 4.5 config/action_policy.json

Fleet Server가 action별 정책을 판단할 때 쓰는 파일입니다.

현재 action 목록은 다음을 포함합니다.

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
image_request
image_view_closed
file_cleanup_report
start_mapping
stop_mapping
save_map
rsync_map
map_status
map_list
nav_goal
nav_cancel
nav_status
emergency_stop
pause_robot
resume_robot
clear_error
clear_emergency
reset_all_jobs
```

분석할 때 확인해야 하는 점:

```text
새 action을 추가하면 action_policy.json에도 등록되어야 합니다.
operator_request.command.action 값과 action_policy.json의 key가 맞아야 합니다.
서버가 Robot Command Client로 전달하는 command.op도 정책과 맞아야 합니다.
```

### 4.6 fleet_protocol.py

공통 JSON 프로토콜 유틸입니다.

담당하는 일:

```text
Fleet JSON 버전 정의
Fleet JSON schema 정의
공통 message 생성
NDJSON 송수신 유틸
operator_request v4 검증
server_command v4 검증
agent_result v4 검증
heartbeat_request/response 검증
state_report 검증
action_policy 검증
error 구조 생성
```

고정값:

```python
FLEET_JSON_VERSION = 4
FLEET_JSON_SCHEMA = "fleet_json_v0.4"
```

모든 담당자의 JSON은 이 값을 맞춰야 합니다.

### 4.7 fleet_server_main.py

Fleet Server 본체입니다.

담당하는 일:

```text
server_config.json 로드
client_info.json 로드
control_info.json 로드
action_policy.json 로드
TCP 서버 시작
Control UI 연결 수신
operator_request 읽기
operator_request 검증
action policy 적용
서버 안전 정책 적용
target robot 해석
server_command 생성
Robot Command Client로 server_command 전송
agent_result 수신
agent_result 검증
operator_response 생성
이미지 요청 처리
image_view_closed/file_cleanup_report 처리
로그 저장
```

중요 함수 흐름:

```text
main()
  -> FleetServer(...)
  -> server.run()

run()
  -> 0.0.0.0:4000 listen
  -> Control UI 접속마다 _handle_control_connection()

_handle_control_connection()
  -> JSON 한 줄 읽기
  -> handle_operator_request()

handle_operator_request()
  -> v4 요청이면 handle_operator_request_v4()

handle_operator_request_v4()
  -> validate_operator_request_v4()
  -> action_policy 확인
  -> image_request면 _handle_image_request_v4()
  -> 일반 로봇 명령이면 _build_server_command_v4()
  -> _send_server_command_to_agent_v4()
  -> _operator_response_v4()

_build_server_command_v4()
  -> client_info.json의 robot metadata 사용
  -> server_command JSON 생성

_send_server_command_to_agent_v4()
  -> client_info.json의 robot_command_client.ip:port로 TCP 연결
  -> server_command 전송
  -> agent_result 수신

_handle_image_request_v4()
  -> _run_image_rsync_v4()

_run_image_rsync_v4()
  -> control_info.json의 제어 SSH 정보 사용
  -> rsync over ssh로 이미지 전송
```

### 4.8 control_laptop_client.py

제어 UI 담당자에게 제공할 수 있는 Python 클라이언트입니다.

담당하는 일:

```text
control_client_config.json 로드
operator_request 생성
Fleet Server로 JSON 한 줄 전송
operator_response 한 줄 수신
CLI 메뉴 테스트 제공
UI 코드에서 import 가능한 ControlServerClient 클래스 제공
```

대표 사용 예:

```python
from control_laptop_client import ControlServerClient

client = ControlServerClient("192.168.3.61", 4000)
response = client.move_forward("tb3_1")
```

주의:

```text
이 코드는 제어 UI가 서버와 통신하기 쉽게 만든 샘플/라이브러리입니다.
제어 UI 담당자가 반드시 UI를 이 파일 안에 만들어야 하는 것은 아닙니다.
하지만 JSON 구조는 이 파일이 만드는 v4 operator_request와 맞아야 합니다.
```

### 4.9 mock_robot_agent.py

실제 Robot Command Client가 준비되지 않았을 때 서버 통신을 검증하는 mock입니다.

담당하는 일:

```text
TCP listen
server_command 수신
heartbeat_request 수신
agent_result 반환
heartbeat_response 반환
선택적 state_report 반환
```

현재 설계상 mock은 gateway 방식으로 쓸 수 있습니다.

```text
서버 -> mock gateway 5000
mock은 server_command.command.robot_id를 읽고 tb3_1/tb3_2/tb3_3 응답을 생성
```

주의:

```text
mock_robot_agent.py는 실제 TurtleBot 제어 코드가 아닙니다.
ROS2 publish 검증용이 아니라 JSON 통신 검증용입니다.
```

## 5. 통신 형식

모든 통신은 기본적으로 TCP + UTF-8 + NDJSON입니다.

규칙:

```text
JSON 객체 1개 = 한 줄
각 JSON 메시지는 반드시 \n으로 끝남
pretty JSON 여러 줄 전송 금지
UTF-8 인코딩
숫자는 숫자로 전송
boolean은 true/false로 전송
```

전송 예:

```python
payload = json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n"
sock.sendall(payload.encode("utf-8"))
```

수신 예:

```python
line = file_obj.readline()
message = json.loads(line)
```

## 6. operator_request 구조

Control UI가 Fleet Server로 보내는 요청입니다.

핵심 필드:

```text
v
mt
msg_id
ts
source
dest
schema
auth
user
command
ui_context
```

예:

```json
{
  "v": 4,
  "mt": "operator_request",
  "msg_id": "MSG_20260622_OPERATOR_REQUEST_000001",
  "ts": "2026-06-22T12:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "auth": {
    "token": "team_demo_token"
  },
  "user": "operator_1",
  "command": {
    "command_id": "CMD_20260622_MOVE_FORWARD_TB3_1_000001",
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
    "button": "move_forward"
  }
}
```

## 7. server_command 구조

Fleet Server가 Robot Command Client로 보내는 명령입니다.

핵심 필드:

```text
v
mt = server_command
msg_id
ts
source = fleet_server
dest = robot_command_client
schema = fleet_json_v0.4
command
```

중요:

```text
dest는 tb3_1이 아니라 robot_command_client입니다.
로봇 구분은 command.robot_id로 합니다.
```

예:

```json
{
  "v": 4,
  "mt": "server_command",
  "msg_id": "MSG_20260622_SERVER_COMMAND_TB3_1_000001",
  "ts": "2026-06-22T12:00:00+09:00",
  "source": "fleet_server",
  "dest": "robot_command_client",
  "schema": "fleet_json_v0.4",
  "command": {
    "command_id": "CMD_20260622_MOVE_FORWARD_TB3_1_000001",
    "parent_command_id": null,
    "group_id": null,
    "job_id": "JOB_20260622_MOVE_FORWARD_TB3_1_000001",
    "command_seq": null,
    "command_revision": 0,
    "op": "move_forward",
    "server_priority": 30,
    "blocking_type": "SOFT",
    "interrupt_policy": "reject_if_busy",
    "robot_id": "tb3_1",
    "ros": {
      "domain_id": 31,
      "namespace": "/tb3_1",
      "topic": "/tb3_1/cmd_vel"
    },
    "params": {
      "lx": 0.05,
      "az": 0.0,
      "dur": 2.0,
      "hz": 10,
      "stop": true
    },
    "timeout_sec": 5.0
  }
}
```

## 8. agent_result 구조

Robot Command Client가 Fleet Server로 보내는 결과입니다.

서버가 결과 매칭에 중요하게 보는 필드:

```text
agent_result.ref == server_command.msg_id
agent_result.robot_id == server_command.command.robot_id
agent_result.command.command_id == server_command.command.command_id
agent_result.command.op == server_command.command.op
```

이 네 가지가 맞지 않으면 서버는 실제 동작이 되었더라도 실패 또는 상태 불일치로 판단할 수 있습니다.

예:

```json
{
  "v": 4,
  "mt": "agent_result",
  "msg_id": "MSG_20260622_AGENT_RESULT_TB3_1_000001",
  "ref": "MSG_20260622_SERVER_COMMAND_TB3_1_000001",
  "ts": "2026-06-22T12:00:01+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "robot_id": "tb3_1",
  "command": {
    "command_id": "CMD_20260622_MOVE_FORWARD_TB3_1_000001",
    "parent_command_id": null,
    "group_id": null,
    "job_id": "JOB_20260622_MOVE_FORWARD_TB3_1_000001",
    "op": "move_forward"
  },
  "ok": true,
  "code": "R_DONE",
  "message": "tb3_1 move_forward completed",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MANUAL",
    "robot_state": "IDLE",
    "job_state": "DONE",
    "accept_state": "ACCEPTING",
    "ui_mode": "READY"
  },
  "perf": {
    "elapsed_ms": 2030,
    "dur": 2.0,
    "hz": 10,
    "pub": 20,
    "sent_cmd_vel_zero": true
  },
  "err": []
}
```

## 9. operator_response 구조

Fleet Server가 Control UI로 보내는 최종 응답입니다.

핵심 필드:

```text
v
mt = operator_response
msg_id
ref
ts
source = fleet_server
dest = control_ui
schema = fleet_json_v0.4
ok
code
message
command
results
err
ui_hint
trace
```

Control UI는 최소한 아래 필드를 화면에 반영해야 합니다.

```text
ok
code
message
results
err
ui_hint
```

## 10. 이미지 전송 구조

이미지 전송은 Robot Command Client가 아니라 Control UI와 Fleet Server 사이의 기능입니다.

흐름:

```text
Control UI -> image_request operator_request
Fleet Server -> server local image 확인
Fleet Server -> rsync over ssh로 Control UI 컴퓨터에 이미지 push
Fleet Server -> file_transfers 로그 저장
Fleet Server -> operator_response 반환
Control UI -> 받은 이미지 표시
Control UI -> 이미지 창 닫힘
Control UI -> image_view_closed 또는 file_cleanup_report 전송
Fleet Server -> 닫힘/삭제 보고 로그 저장
```

서버 기본 이미지 경로:

```text
/home/admin_kyj/openCV/server/sync/to_control/images/tb3_1_latest_map.png
```

제어 컴퓨터 이미지 도착 경로:

```text
/home/ubuntu/openCV/cache/images/tb3_1_latest_map.png
```

## 11. 로그 구조

서버 로그 기본 경로:

```text
/home/admin_kyj/openCV/server/logs/server
```

주요 로그 디렉토리:

```text
operator_requests
operator_responses
commands
results
heartbeats
state_reports
file_transfers
system
```

각 디렉토리에는 보통 아래 두 종류가 생깁니다.

```text
latest_*.json
timestamp가 붙은 기록 파일
```

분석 시 로그에서 확인할 것:

```text
operator_requests/latest_operator_request.json
operator_responses/latest_operator_response.json
commands/latest_server_command.json
results/latest_agent_result.json
file_transfers/latest_image_request.json
heartbeats/latest_heartbeat_request.json
heartbeats/latest_heartbeat_response.json
state_reports/latest_state_report.json
```

## 12. 현재 테스트/실행 명령

Fleet Server 실행:

```bash
cd /home/admin_kyj/openCV/server
python3 fleet_server_main.py
```

제어 테스트 클라이언트 실행:

```bash
cd /home/admin_kyj/openCV/server
python3 control_laptop_client.py
```

mock Robot Command Client 실행:

```bash
cd /home/admin_kyj/openCV/server
python3 mock_robot_agent.py
```

문법 검사:

```bash
cd /home/admin_kyj/openCV/server
python3 -m py_compile fleet_protocol.py fleet_server_main.py control_laptop_client.py mock_robot_agent.py
```

포트 확인:

```bash
ss -ltnp | grep ':4000'
ss -ltnp | grep ':4000'
```

SSH 확인:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=5 ubuntu@192.168.3.59 'echo ssh_ok'
```

rsync dry-run 확인:

```bash
rsync -azvv --dry-run \
  -e 'ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new' \
  /home/admin_kyj/openCV/server/sync/to_control/images/tb3_1_latest_map.png \
  ubuntu@192.168.3.59:/home/ubuntu/openCV/cache/images/tb3_1_latest_map.png
```

## 13. 다른 AI가 반드시 확인해야 하는 분석 포인트

### 13.1 JSON 버전 일치 여부

모든 메시지는 아래 값을 써야 합니다.

```text
v = 4
schema = fleet_json_v0.4
```

### 13.2 메시지 타입 일치 여부

주요 메시지 타입:

```text
operator_request
operator_response
server_command
agent_result
heartbeat_request
heartbeat_response
state_report
image_request
image_view_closed
file_cleanup_report
```

주의:

```text
image_request는 operator_request.command.action으로 들어가는 action입니다.
실제 mt는 operator_request입니다.
```

### 13.3 source/dest 일치 여부

권장 흐름:

```text
Control UI -> Fleet Server:
source = control_ui
dest = fleet_server

Fleet Server -> Robot Command Client:
source = fleet_server
dest = robot_command_client

Robot Command Client -> Fleet Server:
source = robot_command_client
dest = fleet_server

Fleet Server -> Control UI:
source = fleet_server
dest = control_ui
```

### 13.4 robot_id 처리 방식

중요:

```text
robot_id는 서버가 TCP 접속 대상을 고르는 IP가 아닙니다.
robot_id는 Robot Command Client가 내부적으로 어느 TurtleBot에 명령을 보낼지 판단하는 값입니다.
```

### 13.5 stop/action 이름

과거 UI에서 `stop`을 쓸 수 있지만, v4 표준 로봇 정지 action/op는 `robot_stop`입니다.

`control_laptop_client.py`는 stop을 전송 전에 `robot_stop`으로 정규화할 수 있습니다.

### 13.6 all_stop 처리

`all_stop`은 서버가 여러 robot_id에 대한 `robot_stop` 형태로 fanout할 수 있습니다.

다른 AI가 확인할 점:

```text
all_stop 요청이 들어왔을 때 tb3_1/tb3_2/tb3_3 각각에 대해 결과가 results에 들어가는지
클라이언트가 robot_stop을 지원하는지
```

### 13.7 Robot Command Client 연결 실패 처리

클라이언트가 아직 연결되지 않았을 때 서버는 무조건 성공으로 처리하면 안 됩니다.

기대 동작:

```text
TCP 연결 실패
-> synthetic agent_result 생성
-> code는 E_AGENT_DISCONNECTED 또는 E_TIMEOUT 계열
-> operator_response.ok=false
-> UI는 연결 실패/클라이언트 미연결을 표시
-> logs/server/results 또는 operator_responses에 실패 정보가 남음
```

### 13.8 이미지 전송 실패 처리

이미지 전송 실패 시 확인할 것:

```text
file_transfers/latest_image_request.json의 ok
source_path 존재 여부
control_host
control_user
control_path
rsync_argv
elapsed_ms
error
stderr
```

SSH 포트만 열렸다고 이미지 전송이 성공하는 것은 아닙니다.

아래 조건도 필요합니다.

```text
서버에서 제어 컴퓨터로 SSH key 로그인 가능
제어 컴퓨터에 rsync 설치
제어 컴퓨터 target directory 존재
권한 문제 없음
서버 이미지 source file 존재
```

## 14. 분석 산출물 요구사항

이 프롬프트를 받은 AI는 분석 후 아래 형식으로 답변하세요.

```text
1. 현재 구조 요약
2. 파일별 역할 요약
3. JSON 흐름 요약
4. IP/port/SSH 설정 확인 결과
5. 제어 UI와의 연결에서 주의할 점
6. Robot Command Client와의 연결에서 주의할 점
7. 이미지 전송/rsync에서 주의할 점
8. 현재 코드와 문서 사이의 불일치 여부
9. 수정이 필요한 부분
10. 수정하지 말아야 할 부분
11. 다음 테스트 순서
```

답변할 때 반드시 구체적인 파일명을 적으세요.

예:

```text
client_info.json의 robot_command_client.ip가 현재 Wi-Fi 대역과 다를 수 있습니다.
fleet_server_main.py는 _robot_command_address()에서 이 값을 읽어 server_command 전송 대상 주소로 사용합니다.
```

## 15. 수정 전 반드시 지켜야 하는 규칙

다른 AI는 아래를 반드시 지켜야 합니다.

```text
1. JSON v4 계약을 임의로 바꾸지 마세요.
2. v, mt, msg_id, ref, source, dest, schema 필드를 임의로 삭제하지 마세요.
3. server_command.dest를 tb3_1 같은 로봇 ID로 바꾸지 마세요.
4. 서버에 로봇별 실제 IP를 다시 추가하지 마세요.
5. 서버가 TurtleBot에 직접 명령하는 구조로 되돌리지 마세요.
6. Control UI가 Robot Command Client에 직접 붙는 구조로 바꾸지 마세요.
7. Robot Command Client가 Control UI와 직접 통신하는 구조로 바꾸지 마세요.
8. image_request와 로봇 이동 명령을 섞지 마세요.
9. SSH/rsync 실패를 무조건 성공으로 처리하지 마세요.
10. mock_robot_agent.py를 실제 로봇 제어 코드로 오해하지 마세요.
```

## 16. 현재 구조에서 각 담당자가 해야 할 일

### 서버 담당자

```text
server_config.json 유지
client_info.json 최신화
control_info.json 최신화
action_policy.json 유지
fleet_server_main.py 실행
logs/server 확인
JSON_CONTRACT_V4.md 기준 유지
```

### 제어 UI 담당자

```text
server_ip = 192.168.3.61
server_port = 4000
operator_request v4 생성
operator_response를 보고 UI 상태 갱신
image_request 전송
이미지 창 닫힘 시 image_view_closed 또는 file_cleanup_report 전송
서버 응답 ok=false를 실패로 표시
```

### Robot Command Client 담당자

```text
client_info.json의 robot_command_client.ip/port에 해당하는 컴퓨터에서 TCP listen
현재 실제 연결 port는 4000
server_command 수신
command.robot_id 확인
command.op 확인
command.params 확인
내부적으로 해당 TurtleBot에 ROS2 명령 전달
agent_result 반환
heartbeat_request 응답
```

## 17. 최종 성공 기준

### 제어 UI 연결 성공 기준

```text
Control UI가 status_request 전송
Fleet Server가 operator_request 로그 저장
Fleet Server가 operator_response 반환
Control UI가 ok/code/message 표시
```

### Robot Command Client 연결 성공 기준

```text
Fleet Server가 Robot Command Client 4000 포트로 server_command 전송
Robot Command Client가 agent_result 반환
commands/latest_server_command.json 생성
results/latest_agent_result.json 생성
operator_response.results.tb3_x에 결과 반영
```

### 이미지 전송 성공 기준

```text
Control UI가 image_request 전송
Fleet Server가 source image 확인
Fleet Server가 rsync over ssh로 제어 컴퓨터 cache directory에 전송
file_transfers/latest_image_request.json의 ok=true
Control UI가 이미지를 표시
Control UI가 창 닫힘/삭제 보고
file_transfers/latest_image_view_closed.json 또는 cleanup report 생성
```

## 18. 분석 시작용 질문

이 프로젝트를 분석하는 AI는 처음에 아래 질문에 답하면서 시작하세요.

```text
1. 현재 서버가 읽는 설정 파일은 무엇인가?
2. 현재 Control UI가 접속해야 하는 서버 IP/port는 무엇인가?
3. 현재 서버가 이미지 전송 대상으로 보는 Control UI IP/user/path는 무엇인가?
4. 현재 서버가 Robot Command Client로 명령을 보낼 IP/port는 무엇인가?
5. 서버는 로봇별 IP를 직접 관리하는가?
6. server_command.dest는 무엇이어야 하는가?
7. 실제 로봇 구분은 어느 필드에서 하는가?
8. agent_result가 server_command와 매칭되려면 어떤 필드가 같아야 하는가?
9. 클라이언트 미연결 시 서버는 어떤 응답을 해야 하는가?
10. 이미지 전송 실패 시 어떤 로그를 봐야 하는가?
```

## 19. 요약

현재 프로젝트는 JSON v4 계약을 중심으로 동작합니다.

서버는 제어 UI와 Robot Command Client 사이의 중계자입니다.

서버는 TurtleBot에 직접 명령하지 않습니다.

서버는 Robot Command Client 하나에 명령을 보내고, 그 명령 안의 `command.robot_id`로 대상 로봇을 구분합니다.

제어 UI와의 이미지 전송은 별도로 `control_info.json`의 SSH/rsync 정보를 사용합니다.

다른 AI가 작업할 때는 이 구조를 유지하면서, 문서와 코드와 JSON이 서로 같은 규칙을 말하고 있는지 확인하는 것이 가장 중요합니다.
