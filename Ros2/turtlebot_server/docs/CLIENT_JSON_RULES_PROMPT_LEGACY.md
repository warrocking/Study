# TurtleBot Fleet Server v4 - Robot Agent Client JSON 상세 규칙 프롬프트

당신은 TurtleBot 3대 협업 제어 시스템의 Robot Agent 클라이언트 담당자입니다.

이 문서는 Fleet Server와 Robot Agent 클라이언트가 주고받는 JSON 상세 규칙입니다. 필드명, 메시지 타입, action/op 이름, 응답 구조를 임의로 바꾸지 말고 아래 규칙을 그대로 사용하세요.

## 1. 통신 기본 규칙

Fleet Server와 Robot Agent 클라이언트의 통신은 TCP + UTF-8 + NDJSON입니다.

```text
JSON 객체 1개 = 한 줄
각 JSON 메시지는 반드시 \n 으로 끝남
인코딩은 UTF-8
pretty JSON 여러 줄 전송 금지
```

Python 전송 예:

```python
payload = json.dumps(message, ensure_ascii=False, separators=(",", ":")) + "\n"
sock.sendall(payload.encode("utf-8"))
```

수신은 줄 단위로 처리하세요.

```python
line = file_obj.readline()
message = json.loads(line)
```

## 2. 서버와 클라이언트 역할

Robot Agent 클라이언트는 TCP 서버로 대기합니다.

```text
Fleet Server -> Robot Agent Client
server_command 또는 heartbeat_request 전송

Robot Agent Client -> Fleet Server
agent_result 또는 heartbeat_response/state_report 응답
```

현재 서버의 Robot Agent 대상 정보:

```text
robot_command_client: 192.168.3.63:4000
```

클라이언트는 4000 포트에서 listen 하고, 서버가 보낸 `command.robot_id`를 읽어 어느 TurtleBot에 명령할지 판단해야 합니다. 현재 1차 실제 연결 테스트에서는 `tb3_3`만 활성 로봇으로 사용합니다. 서버는 TurtleBot별 IP를 관리하지 않습니다.

## 3. 공통 필드

모든 v4 메시지는 아래 공통 필드를 사용합니다.

```json
{
  "v": 4,
  "mt": "server_command",
  "msg_id": "MSG_20260622_EXAMPLE_000001",
  "ts": "2026-06-22T12:00:00+09:00",
  "source": "fleet_server",
  "dest": "robot_command_client",
  "schema": "fleet_json_v0.4"
}
```

고정값:

```text
v = 4
schema = fleet_json_v0.4
```

허용 source/dest:

```text
fleet_server
robot_command_client
```

Robot Agent 관련 메시지 타입:

```text
server_command
agent_result
heartbeat_request
heartbeat_response
state_report
file_sync_report
error_report
```

## 4. server_command 수신 규칙

Fleet Server가 Robot Agent 클라이언트로 보내는 명령입니다.

클라이언트는 `mt == "server_command"`인 JSON을 받으면 `command.op`를 해석해서 ROS2 명령 실행 또는 내부 상태 처리를 수행하고, 같은 TCP 연결에서 `agent_result`를 한 줄 JSON으로 응답해야 합니다.

### 필수 구조

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

### server_command.command 필수 필드

```text
command_id
command_revision
op
server_priority
blocking_type
interrupt_policy
robot_id
ros
params
timeout_sec
```

### 클라이언트 검증 규칙

클라이언트는 최소한 아래를 확인하세요.

```text
v == 4
mt == "server_command"
schema == "fleet_json_v0.4"
dest == "robot_command_client"
command.robot_id가 tb3_1/tb3_2/tb3_3 중 하나임
command.ros.topic == 자신이 publish할 /cmd_vel topic
```

검증 실패 시에도 연결을 그냥 끊지 말고 `agent_result`를 `ok=false`로 응답하세요.

## 5. heartbeat_request 수신 규칙

Fleet Server가 클라이언트 생존 확인을 위해 보내는 메시지입니다.

```json
{
  "v": 4,
  "mt": "heartbeat_request",
  "msg_id": "MSG_20260622_HEARTBEAT_TB3_1_000001",
  "ts": "2026-06-22T12:00:00+09:00",
  "source": "fleet_server",
  "dest": "robot_command_client",
  "schema": "fleet_json_v0.4",
  "robot_id": "tb3_1",
  "include_state_report": true
}
```

클라이언트는 같은 TCP 연결에서 먼저 `heartbeat_response`를 보내고, `include_state_report == true`이면 이어서 `state_report`를 한 줄 더 보낼 수 있습니다.

## 6. agent_result 응답 규칙

Robot Agent가 `server_command` 처리 결과를 Fleet Server로 보내는 응답입니다.

### 성공 응답 예시

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

### agent_result 필수 필드

```text
v
mt
msg_id
ref
ts
source
dest
schema
robot_id
command
ok
code
message
state
perf
err
```

### agent_result.command 필수 필드

```text
command_id
op
```

아래 필드는 가능하면 서버가 보낸 값을 그대로 되돌려주세요.

```text
parent_command_id
group_id
job_id
```

### 서버가 결과를 매칭하는 핵심 조건

Fleet Server는 아래 네 가지가 맞는지 검사합니다.

```text
agent_result.ref == server_command.msg_id
agent_result.robot_id == server_command.command.robot_id
agent_result.command.command_id == server_command.command.command_id
agent_result.command.op == server_command.command.op
```

하나라도 다르면 서버는 `E_STATE_MISMATCH`로 처리할 수 있습니다.

## 7. 실패 agent_result 예시

명령을 실행할 수 없거나 검증에 실패한 경우에도 반드시 `agent_result`를 응답하세요.

```json
{
  "v": 4,
  "mt": "agent_result",
  "msg_id": "MSG_20260622_AGENT_RESULT_TB3_1_000002",
  "ref": "MSG_20260622_SERVER_COMMAND_TB3_1_000002",
  "ts": "2026-06-22T12:00:01+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "robot_id": "tb3_1",
  "command": {
    "command_id": "CMD_20260622_MOVE_FORWARD_TB3_1_000002",
    "parent_command_id": null,
    "group_id": null,
    "job_id": "JOB_20260622_MOVE_FORWARD_TB3_1_000002",
    "op": "move_forward"
  },
  "ok": false,
  "code": "E_ROS_PUBLISH_FAILED",
  "message": "failed to publish /cmd_vel",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MANUAL",
    "robot_state": "ERROR",
    "job_state": "FAILED",
    "accept_state": "BLOCKED",
    "ui_mode": "ERROR"
  },
  "perf": {
    "elapsed_ms": 12,
    "sent_cmd_vel_zero": false
  },
  "err": [
    {
      "code": "E_ROS_PUBLISH_FAILED",
      "msg": "failed to publish /cmd_vel",
      "where": "robot_command_client",
      "detail": {
        "topic": "/tb3_1/cmd_vel"
      }
    }
  ]
}
```

## 8. heartbeat_response 응답 규칙

`heartbeat_request`에 대한 응답입니다.

```json
{
  "v": 4,
  "mt": "heartbeat_response",
  "msg_id": "MSG_20260622_HEARTBEAT_RESPONSE_TB3_1_000001",
  "ref": "MSG_20260622_HEARTBEAT_TB3_1_000001",
  "ts": "2026-06-22T12:00:00+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "robot_id": "tb3_1",
  "ok": true,
  "agent_alive": true,
  "code": "R_PONG",
  "message": "tb3_1 heartbeat ok",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MANUAL",
    "robot_state": "IDLE",
    "job_state": "NONE",
    "accept_state": "ACCEPTING",
    "ui_mode": "READY"
  }
}
```

필수 필드:

```text
ref
robot_id
ok
agent_alive
```

`code`, `message`, `state`는 서버 상태 표시 품질을 위해 포함하는 것을 권장합니다.

## 9. state_report 보고 규칙

상태 보고용 메시지입니다. heartbeat 응답 직후 같은 TCP 연결에서 보낼 수 있습니다.

```json
{
  "v": 4,
  "mt": "state_report",
  "msg_id": "MSG_20260622_STATE_TB3_1_000001",
  "ts": "2026-06-22T12:00:00+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "ref": "MSG_20260622_HEARTBEAT_TB3_1_000001",
  "robot_id": "tb3_1",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MANUAL",
    "robot_state": "IDLE",
    "job_state": "NONE",
    "accept_state": "ACCEPTING",
    "ui_mode": "READY",
    "battery_level": null
  },
  "current_job": {
    "job_id": null,
    "action": null,
    "started_at": null
  }
}
```

필수 필드:

```text
robot_id
state
```

## 10. 상태 enum 규칙

`state` 객체의 기본 필드는 아래 값을 사용하세요.

### connection_state

```text
CONNECTED
DISCONNECTED
```

### operating_mode

```text
MANUAL
AUTO
MAPPING
NAVIGATION
PAUSED
SERVICE
ERROR
EMERGENCY
SHUTDOWN
```

### robot_state

```text
IDLE
MOVING
MAPPING
NAVIGATING
SAVING_MAP
SYNCING_FILE
STOPPED
PAUSED
ERROR
DISCONNECTED
EMERGENCY
```

### job_state

```text
NONE
PENDING
ACCEPTED
QUEUED
RUNNING
PAUSING
PAUSED
RESUMING
STOPPING
DONE
FAILED
CANCELING
CANCELED
ABORTED
REJECTED
```

### accept_state

```text
ACCEPTING
QUEUEABLE
BLOCKED
```

### ui_mode

권장값:

```text
READY
BUSY
BUSY_QUEUEABLE
PAUSED
OFFLINE
ERROR
EMERGENCY
```

## 11. op 목록

Robot Agent가 받을 수 있는 주요 `command.op` 목록입니다.

```text
move_forward
move_backward
turn_left
turn_right
custom_move
robot_stop
emergency_stop
pause_robot
resume_robot
cancel_job
nav_cancel
status_request
robot_state_request
job_status_request
ping
mapping_status
map_status
map_list
nav_status
start_mapping
stop_mapping
save_map
rsync_map
nav_goal
clear_error
clear_emergency
reset_all_jobs
```

주의:

```text
Control UI에서는 stop을 보낼 수 있지만, Robot Agent가 받는 표준 op는 robot_stop입니다.
all_stop은 서버가 각 로봇별 robot_stop으로 fanout해서 보냅니다.
```

## 12. params 규칙

이동 계열 op의 기본 params:

```json
{
  "lx": 0.05,
  "az": 0.0,
  "dur": 2.0,
  "hz": 10,
  "stop": true
}
```

정지 계열 op의 기본 params:

```json
{
  "lx": 0.0,
  "az": 0.0,
  "dur": 0.0,
  "hz": 10,
  "stop": true,
  "reason": "operator_stop"
}
```

클라이언트는 서버가 보낸 `params`를 우선 사용하세요. 자체 기본값을 임의로 덮어쓰지 마세요.

## 13. result code 권장 규칙

성공 코드:

```text
R_ACCEPTED
R_STARTED
R_RUNNING
R_DONE
R_STATUS
R_PONG
R_STOPPED
R_PAUSED
R_RESUMED
R_CANCELED
R_MAP_LOCAL_SAVED
R_MAP_SYNCING
R_FILE_SYNC_REPORTED
```

오류 코드:

```text
E_BAD_REQUEST
E_AUTH_FAILED
E_UNKNOWN_ACTION
E_TARGET_INVALID
E_AGENT_DISCONNECTED
E_TIMEOUT
E_BUSY
E_REJECTED
E_ROS_PUBLISH_FAILED
E_STATE_MISMATCH
E_INTERNAL_ERROR
E_FILE_SYNC_FAILED
E_MAP_SAVE_FAILED
E_NAV_FAILED
```

서버가 알 수 없는 code를 받으면 잘못된 결과로 처리할 수 있으므로, 위 코드 중에서 선택하세요.

## 14. heartbeat와 상태 보고 권장 주기

서버가 heartbeat_request를 보낼 때 즉시 응답하세요.

상태 보고 주기는 아래를 권장합니다.

```text
READY / IDLE: 2~5초
MOVING / NAVIGATING: 0.5~1초
MAPPING: 1~2초
DISCONNECTED: 3~5초 재시도
```

현재 서버 구현은 heartbeat 요청에 대한 응답과 선택적 state_report를 우선 사용합니다. 클라이언트가 주기적으로 별도 state_report를 보낼 경우에도 JSON 구조는 동일하게 유지하세요.

## 15. file_sync_report / error_report

맵 저장/동기화 등 파일 작업 결과를 보고할 때는 `file_sync_report` 또는 `agent_result`의 `err`를 사용할 수 있습니다.

이번 1차 연동에서는 반드시 구현해야 하는 최소 범위는 아래입니다.

```text
server_command 수신
agent_result 응답
heartbeat_request 수신
heartbeat_response 응답
선택적 state_report 응답
```

파일 동기화 세부 구현은 서버 담당자와 별도 합의 후 진행하세요.

## 16. 최소 구현 체크리스트

클라이언트 담당자는 아래를 만족해야 합니다.

```text
1. 담당 robot_id에 맞는 port에서 TCP listen
2. 서버가 보낸 JSON 한 줄 수신
3. mt가 server_command이면 command.op 실행 후 agent_result 한 줄 응답
4. mt가 heartbeat_request이면 heartbeat_response 한 줄 응답
5. include_state_report=true이면 state_report 한 줄 추가 응답
6. 모든 응답은 UTF-8 NDJSON, compact JSON, 마지막 \n 포함
7. 실패해도 연결 무응답 금지, ok=false JSON 응답
8. ref, robot_id, command.command_id, command.op 매칭 규칙 준수
```

## 17. 통신 예시 흐름

```text
Fleet Server connects to 192.168.3.63:4000
Fleet Server sends server_command JSON + \n
robot_command_client receives and validates it
robot_command_client reads command.robot_id
robot_command_client publishes ROS2 to the matching TurtleBot path
robot_command_client sends agent_result JSON + \n
Fleet Server closes the TCP request connection
```

heartbeat 흐름:

```text
Fleet Server connects to 192.168.3.63:4000
Fleet Server sends heartbeat_request JSON + \n
robot_command_client sends heartbeat_response JSON + \n
robot_command_client optionally sends state_report JSON + \n
Fleet Server closes the TCP request connection
```

## 18. 절대 바꾸면 안 되는 부분

```text
v
mt
msg_id
ts
source
dest
schema
command.command_id
command.op
command.robot_id
agent_result.ref
agent_result.robot_id
agent_result.command.command_id
agent_result.command.op
```

특히 아래 필드는 서버가 결과를 맞춰보는 키입니다.

```text
server_command.msg_id -> agent_result.ref
server_command.command.command_id -> agent_result.command.command_id
server_command.command.op -> agent_result.command.op
server_command.command.robot_id -> agent_result.robot_id
```

이 네 가지가 틀리면 서버는 로봇이 제대로 수행했더라도 실패 또는 상태 불일치로 판단할 수 있습니다.
