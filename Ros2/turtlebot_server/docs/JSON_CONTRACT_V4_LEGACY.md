# Fleet JSON v0.4 Contract

이 문서는 TurtleBot 3대 Fleet Server 프로젝트의 현재 기준 통신 JSON 계약입니다.

현재 서버 코드는 v4 `operator_request`, `operator_response`, `server_command`, `agent_result`, `heartbeat_request`, `heartbeat_response`, `state_report` 흐름을 기준으로 동작합니다. 일부 legacy v1/v3 처리 경로와 `mock_robot_agent.py`는 비교/테스트용으로 남아 있지만, 새로 작성하는 제어 UI와 Robot Agent 클라이언트 코드는 이 문서의 v4 구조를 사용해야 합니다.

현재 검증된 범위:

```text
Control UI -> Fleet Server v4 JSON 통신
Fleet Server -> Control UI 이미지 rsync server_push
Control UI image_view_closed 보고
Fleet Server -> Robot Agent v4 server_command 생성
Robot Agent -> Fleet Server v4 agent_result 수신 구조
heartbeat_response/state_report 수신 구조
```

아직 실제 TurtleBot 클라이언트와 추가 합의/구현이 필요한 범위:

```text
실제 ROS2 SLAM map save
Robot Agent -> Fleet Server map 파일 동기화
Navigation2 goal 실제 수행
장시간 실주행 안전 검증
```

## 1. 통신 방식

모든 통신은 TCP + UTF-8 + NDJSON으로 통일합니다.

```text
JSON 객체 1개 = 한 줄
각 메시지는 반드시 \n 으로 끝남
수신자는 줄 단위로 JSON 파싱
인코딩은 UTF-8
```

예:

```text
{"v":4,"mt":"operator_request","msg_id":"MSG_20260619_000001",...}\n
```

## 2. 공통 필드

가능한 모든 메시지는 아래 공통 필드를 가집니다.

```json
{
  "v": 4,
  "mt": "operator_request",
  "msg_id": "MSG_20260619_000001",
  "ts": "2026-06-19T12:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4"
}
```

고정값:

```text
v = 4
schema = fleet_json_v0.4
```

허용 `source` / `dest`:

```text
control_ui
fleet_server
robot_command_client
```

메시지 타입 `mt`:

```text
operator_request
operator_response
server_command
agent_result
heartbeat_request
heartbeat_response
state_report
file_sync_report
error_report
```

주의:

```text
job_status_request는 mt로 쓰지 않습니다.
상태 조회도 mt="operator_request" 안의 command.action="job_status_request"로 처리합니다.
```

## 3. Action Enum

서버가 인식해야 하는 action 목록입니다.

```text
status_request
robot_state_request
job_status_request
ping

emergency_stop
all_stop
robot_stop
stop

pause_all
pause_robot
resume_all
resume_robot

cancel_job
reset_all_jobs
clear_error
clear_emergency

move_forward
move_backward
turn_left
turn_right
custom_move

start_mapping
stop_mapping
mapping_status
save_map
rsync_map
image_request
image_view_closed
file_cleanup_report
map_status
map_list

nav_goal
nav_status
nav_cancel
```

명명 규칙:

```text
robot_state는 상태 이름입니다. 명령 이름은 robot_state_request입니다.
job_status는 조회 개념입니다. 명령 이름은 job_status_request입니다.
```

## 4. stop / robot_stop 정규화

`stop`과 `robot_stop`은 아래처럼 구분합니다.

```text
stop:
Control UI에서 보낼 수 있는 편의용 alias

robot_stop:
서버 내부 표준 action
Robot Agent로 보내는 표준 op
```

처리 흐름:

```text
UI action = stop
↓ 서버 정규화
normalized_action = robot_stop
↓ Agent 전송
server_command.command.op = robot_stop
```

서버의 action policy와 server_command는 `robot_stop` 기준으로 처리합니다.

## 5. UI와 Priority 규칙

Control UI는 최종 priority를 결정하지 않습니다.

Control UI가 보내는 핵심 정보:

```text
action
target_scope
targets
params
user
command_id
job_id
command_seq
```

서버가 action_policy_table로 결정하는 정보:

```text
server_priority
blocking_type
interrupt_policy
allowed_operating_modes
```

UI가 priority 값을 보내더라도 서버는 신뢰하지 않고 서버 정책값으로 덮어씁니다.

## 6. operator_request

Control UI가 Fleet Server로 보내는 요청입니다.

단발성 이동 명령 예:

```json
{
  "v": 4,
  "mt": "operator_request",
  "msg_id": "MSG_20260619_000010",
  "ts": "2026-06-19T12:01:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "auth": {
    "token": "team_demo_token"
  },
  "user": "operator_1",
  "command": {
    "command_id": "CMD_20260619_000010",
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
  }
}
```

단발성 명령에서 `job_id`가 없으면 `command_seq`는 `null` 또는 생략 가능합니다.

## 7. all_stop operator_request

`all_stop`은 아래 구조로 통일합니다.

```json
{
  "v": 4,
  "mt": "operator_request",
  "msg_id": "MSG_20260619_ALL_STOP_0001",
  "ts": "2026-06-19T12:02:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "auth": {
    "token": "team_demo_token"
  },
  "user": "operator_1",
  "command": {
    "command_id": "CMD_20260619_ALL_STOP_0001",
    "group_id": "GRP_20260619_ALL_STOP_0001",
    "job_id": null,
    "command_seq": null,
    "command_revision": 0,
    "action": "all_stop",
    "target_scope": "all",
    "targets": ["all"],
    "params": {
      "reason": "operator_all_stop"
    },
    "expects": {
      "response_type": "sync",
      "status_followup": true
    },
    "timeout_sec": 3.0
  }
}
```

서버 해석:

```text
target_scope = all
targets = ["all"]
↓
resolved_targets = ["tb3_1", "tb3_2", "tb3_3"]
```

child command_id 규칙:

```text
parent_command_id = CMD_20260619_ALL_STOP_0001
group_id = GRP_20260619_ALL_STOP_0001

CMD_20260619_ALL_STOP_0001_TB3_1
CMD_20260619_ALL_STOP_0001_TB3_2
CMD_20260619_ALL_STOP_0001_TB3_3
```

## 8. action_policy_table

서버는 action별 정책표를 가져야 합니다. 이후 구현 단계에서 `action_policy.json` 분리를 권장합니다.

필수 정책 요약:

```text
emergency_stop priority=1  HARD interrupt_current scope=all
all_stop       priority=2  HARD interrupt_current scope=all
robot_stop     priority=3  HARD interrupt_current scope=single,multi

pause_all      priority=4  SOFT interrupt_current scope=all
pause_robot    priority=5  SOFT interrupt_current scope=single,multi
cancel_job     priority=6  HARD interrupt_current scope=single,multi,all
nav_cancel     priority=6  HARD interrupt_current scope=single,multi
reset_all_jobs priority=7  HARD interrupt_current scope=all
clear_emergency priority=7 HARD status_only scope=all

status_request      priority=10 NONE status_only scope=single,multi,all
robot_state_request priority=10 NONE status_only scope=single,multi,all
job_status_request  priority=10 NONE status_only scope=single,multi,all

resume_all   priority=20 SOFT replace_same_job scope=all
resume_robot priority=20 SOFT replace_same_job scope=single,multi

move_forward  priority=30 SOFT reject_if_busy scope=single
move_backward priority=30 SOFT reject_if_busy scope=single
turn_left     priority=30 SOFT reject_if_busy scope=single
turn_right    priority=30 SOFT reject_if_busy scope=single
custom_move   priority=30 SOFT reject_if_busy scope=single

start_mapping  priority=40 SOFT reject_if_busy scope=single
stop_mapping   priority=40 HARD interrupt_current scope=single
mapping_status priority=40 NONE status_only scope=single,multi,all

save_map   priority=50 SINGLE reject_if_busy scope=single
rsync_map  priority=55 SINGLE queue_if_busy scope=single
image_request      priority=56 SINGLE queue_if_busy scope=single
image_view_closed  priority=57 NONE status_only scope=single,multi,all
file_cleanup_report priority=58 NONE status_only scope=single,multi,all
map_status priority=60 NONE status_only scope=single,multi,all
map_list   priority=60 NONE status_only scope=all

nav_goal   priority=70 SOFT reject_if_busy scope=single
nav_status priority=70 NONE status_only scope=single,multi,all
```

중요:

```text
READY는 ui_mode입니다. allowed_operating_modes에 넣지 않습니다.
move_forward/move_backward/turn_left/turn_right/custom_move는 AUTO에서 허용하지 않습니다.
수동 이동은 MANUAL 또는 MAPPING에서만 허용합니다.
```

## 9. 상태 Enum

### ui_mode

```text
OFFLINE
READY
BUSY_QUEUEABLE
BUSY_BLOCKED
PAUSED
EMERGENCY
```

### operating_mode

```text
STARTUP
AUTO
MANUAL
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

### global_state

```text
NORMAL
PAUSED_ALL
EMERGENCY
SERVICE
SHUTDOWN
```

## 10. clear_emergency / reset_all_jobs

두 명령은 같은 동작이 아닙니다.

```text
clear_emergency:
긴급 상태를 해제합니다.
안전 상태 확인 후 global_state를 EMERGENCY에서 NORMAL 또는 SERVICE로 바꿉니다.
작업 큐를 자동으로 재시작하지 않습니다.

reset_all_jobs:
작업 큐와 job 상태를 초기화합니다.
긴급 상태 해제 자체와는 별개입니다.
이전 작업을 자동 재시작하지 않습니다.
```

권장 흐름:

```text
emergency_stop 발생
→ global_state = EMERGENCY
→ 일반 명령 거부
→ clear_emergency 요청
→ 안전 상태 확인
→ global_state = NORMAL 또는 SERVICE
→ 필요하면 reset_all_jobs
→ 새 작업은 사용자가 다시 명령
```

## 11. 서버 판단 순서

Fleet Server는 operator_request를 받으면 아래 순서로 판단합니다.

```text
1. TCP NDJSON 한 줄 파싱
2. JSON 형식 검증
3. v, mt, msg_id, ts 필수 필드 확인
4. auth token 확인
5. action alias 정규화(stop → robot_stop)
6. command_id 중복 확인
7. job_id와 command_seq 검증
8. action_policy_table에서 action 정책 조회
9. 서버 정책값으로 priority / blocking_type / interrupt_policy 결정
10. global_state 확인
11. target_scope / targets 유효성 확인
12. operating_mode 허용 여부 확인
13. robot_state / job_state / accept_state 확인
14. current_job priority와 새 명령 priority 비교
15. blocking_type 확인
16. interrupt_policy 적용
17. 실행 / 큐 등록 / 거부 / fan-out 결정
18. operator_response 생성
19. 로그 저장
```

## 12. operator_response

서버가 Control UI로 보내는 응답입니다.

```json
{
  "v": 4,
  "mt": "operator_response",
  "msg_id": "MSG_20260619_000011",
  "ref": "MSG_20260619_000010",
  "ts": "2026-06-19T12:01:00+09:00",
  "source": "fleet_server",
  "dest": "control_ui",
  "schema": "fleet_json_v0.4",
  "ok": true,
  "code": "R_STARTED",
  "message": "명령이 시작되었습니다.",
  "command": {
    "command_id": "CMD_20260619_000010",
    "group_id": null,
    "job_id": "JOB_20260619_TB3_1_MOVE_0001",
    "action": "move_forward",
    "normalized_action": "move_forward",
    "server_priority": 30,
    "blocking_type": "SOFT",
    "interrupt_policy": "reject_if_busy"
  },
  "system": {
    "global_state": "NORMAL"
  },
  "results": {
    "tb3_1": {
      "ok": true,
      "code": "R_STARTED",
      "connection_state": "CONNECTED",
      "operating_mode": "MANUAL",
      "robot_state": "MOVING",
      "job_state": "RUNNING",
      "accept_state": "QUEUEABLE",
      "ui_mode": "BUSY_QUEUEABLE",
      "message": "tb3_1 전진 명령 실행 중입니다."
    }
  },
  "ui_hint": {
    "summary": "tb3_1 전진 실행 중",
    "severity": "info",
    "highlight_robots": ["tb3_1"],
    "disable_buttons": ["start_mapping", "nav_goal"],
    "enable_buttons": ["stop", "robot_stop", "status_request"]
  }
}
```

`R_MOVE_STARTED` 같은 세부 코드는 쓰지 않고 우선 `R_STARTED`를 사용합니다. 세부 설명은 `message`에 적습니다.

## 13. Partial Success

```text
ok = true:
전체 대상이 모두 성공

ok = false:
전체 실패 또는 부분 실패 포함

code = R_PARTIAL_SUCCESS:
일부 성공, 일부 실패
```

따라서 아래 응답은 유효합니다.

```json
{
  "ok": false,
  "code": "R_PARTIAL_SUCCESS"
}
```

UI는 `ok=false`만 보고 완전 실패로 판단하지 말고, `code`, `group_result`, `results`를 함께 봅니다.

## 14. all_stop operator_response

`all_stop` 결과에는 반드시 `group_result`를 포함합니다.

```json
{
  "v": 4,
  "mt": "operator_response",
  "msg_id": "MSG_20260619_ALL_STOP_RESULT_0001",
  "ref": "MSG_20260619_ALL_STOP_0001",
  "ts": "2026-06-19T12:02:01+09:00",
  "source": "fleet_server",
  "dest": "control_ui",
  "schema": "fleet_json_v0.4",
  "ok": false,
  "code": "R_PARTIAL_SUCCESS",
  "message": "전체 정지 명령 중 일부 로봇에서 실패가 발생했습니다.",
  "command": {
    "command_id": "CMD_20260619_ALL_STOP_0001",
    "group_id": "GRP_20260619_ALL_STOP_0001",
    "action": "all_stop",
    "normalized_action": "all_stop",
    "server_priority": 2,
    "resolved_targets": ["tb3_1", "tb3_2", "tb3_3"]
  },
  "group_result": {
    "group_id": "GRP_20260619_ALL_STOP_0001",
    "total": 3,
    "success": 2,
    "failed": 1,
    "status": "PARTIAL_SUCCESS"
  },
  "results": {
    "tb3_1": {
      "ok": true,
      "code": "R_STOPPED",
      "robot_state": "STOPPED",
      "ui_mode": "READY",
      "message": "tb3_1 정지 완료"
    },
    "tb3_2": {
      "ok": false,
      "code": "E_AGENT_DISCONNECTED",
      "robot_state": "DISCONNECTED",
      "ui_mode": "OFFLINE",
      "message": "tb3_2 Agent 연결 실패"
    },
    "tb3_3": {
      "ok": true,
      "code": "R_STOPPED",
      "robot_state": "STOPPED",
      "ui_mode": "READY",
      "message": "tb3_3 정지 완료"
    }
  },
  "ui_hint": {
    "summary": "전체 정지 부분 성공: tb3_2 연결 실패",
    "severity": "warning",
    "highlight_robots": ["tb3_2"],
    "disable_buttons": [],
    "enable_buttons": ["status_request", "reset_all_jobs"]
  }
}
```

## 15. server_command

서버가 Robot Agent로 보내는 명령입니다.

```json
{
  "v": 4,
  "mt": "server_command",
  "msg_id": "MSG_20260619_000030",
  "ts": "2026-06-19T12:03:00+09:00",
  "source": "fleet_server",
  "dest": "robot_command_client",
  "schema": "fleet_json_v0.4",
  "command": {
    "command_id": "CMD_20260619_ALL_STOP_0001_TB3_1",
    "parent_command_id": "CMD_20260619_ALL_STOP_0001",
    "group_id": "GRP_20260619_ALL_STOP_0001",
    "job_id": null,
    "command_seq": null,
    "command_revision": 0,
    "op": "robot_stop",
    "server_priority": 3,
    "blocking_type": "HARD",
    "interrupt_policy": "interrupt_current",
    "robot_id": "tb3_1",
    "ros": {
      "domain_id": 31,
      "namespace": "/tb3_1",
      "topic": "/tb3_1/cmd_vel"
    },
    "params": {
      "lx": 0.0,
      "az": 0.0,
      "dur": 0.0,
      "stop": true,
      "reason": "all_stop_fanout"
    },
    "timeout_sec": 2.0
  }
}
```

## 16. agent_result

Robot Agent가 Fleet Server로 보내는 결과입니다.

```json
{
  "v": 4,
  "mt": "agent_result",
  "msg_id": "MSG_20260619_000031",
  "ref": "MSG_20260619_000030",
  "ts": "2026-06-19T12:03:00+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "robot_id": "tb3_1",
  "command": {
    "command_id": "CMD_20260619_ALL_STOP_0001_TB3_1",
    "parent_command_id": "CMD_20260619_ALL_STOP_0001",
    "group_id": "GRP_20260619_ALL_STOP_0001",
    "job_id": null,
    "op": "robot_stop"
  },
  "ok": true,
  "code": "R_STOPPED",
  "message": "cmd_vel 0 publish 완료",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MANUAL",
    "robot_state": "STOPPED",
    "job_state": "NONE",
    "accept_state": "ACCEPTING",
    "ui_mode": "READY"
  },
  "perf": {
    "elapsed_ms": 35,
    "sent_cmd_vel_zero": true
  },
  "err": null
}
```

## 17. heartbeat_response / state_report

heartbeat는 생존 확인용입니다.

```json
{
  "v": 4,
  "mt": "heartbeat_response",
  "msg_id": "MSG_20260619_HB_0002",
  "ref": "MSG_20260619_HB_0001",
  "ts": "2026-06-19T12:04:00+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "robot_id": "tb3_1",
  "ok": true,
  "agent_alive": true
}
```

state_report는 자세한 상태 보고용입니다.

```json
{
  "v": 4,
  "mt": "state_report",
  "msg_id": "MSG_20260619_STATE_0001",
  "ts": "2026-06-19T12:04:01+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "robot_id": "tb3_1",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MAPPING",
    "robot_state": "MAPPING",
    "job_state": "RUNNING",
    "accept_state": "QUEUEABLE",
    "ui_mode": "BUSY_QUEUEABLE",
    "battery_level": null
  },
  "current_job": {
    "job_id": "JOB_20260619_TB3_1_MAP_0001",
    "action": "start_mapping",
    "started_at": "2026-06-19T12:00:00+09:00"
  }
}
```

권장 heartbeat 주기:

```text
READY / IDLE: 2~5초
MOVING / NAVIGATING: 0.5~1초
MAPPING: 1~2초
DISCONNECTED: 3~5초 재시도
```

서버 상태와 Agent 보고 상태가 충돌하면 `E_STATE_MISMATCH`로 경고 처리할 수 있습니다.

## 18. Map / File Sync

Map 파일 동기화는 현재 구조와 action policy만 준비되어 있습니다. 실제 TurtleBot 클라이언트가 생성한 map 파일을 서버로 가져오는 방식은 Robot Agent 담당자와 경로/권한/전송 방향을 합의한 뒤 구현해야 합니다.

Control UI 이미지 전송은 아래 `18.1 Image Transfer Over Rsync` 규칙을 따르며, 2026-06-22 기준으로 서버 -> 제어 컴퓨터 `server_push` 방식이 성공 로그로 확인되었습니다.

```text
map 파일은 JSON에 직접 넣지 않습니다.
map.pgm, map.yaml 등은 rsync/scp/HTTP upload 같은 별도 방식으로 전송합니다.
MAP_READY 최종 판정 권한은 서버에 있습니다.
클라이언트의 file_sync_report는 전송 시도 결과 보고일 뿐입니다.
```

MAP_READY 조건:

```text
1. transfer.done 존재
2. map.yaml 존재
3. map.pgm 존재
4. map_metadata.json 존재
5. 필수 파일 크기가 0이 아님
6. map_id와 map_version 중복 없음
```

경로는 `~/` 문자열 그대로 쓰지 않고 절대경로로 변환해서 사용합니다.

### 18.1 Image Transfer Over Rsync

이미지 파일은 JSON에 직접 넣지 않습니다.

```text
JSON:
이미지 전송 요청, 전송 결과, 창 닫기, 로컬 삭제 보고에 사용합니다.

rsync over SSH:
실제 이미지 파일 전송에 사용합니다.
```

현재 서버 구현은 `server_push` 방식입니다.

```text
1. Control UI가 image_request JSON을 Fleet Server로 보냅니다.
2. Fleet Server가 서버 로컬 이미지 파일을 확인합니다.
3. Fleet Server가 rsync over SSH로 Control UI 컴퓨터에 이미지를 보냅니다.
4. Fleet Server가 operator_response와 file_transfers 로그를 남깁니다.
5. Control UI는 전달받은 control_path 이미지를 화면에 표시합니다.
6. 사용자가 이미지 창을 닫으면 Control UI가 로컬 파일을 삭제합니다.
7. Control UI가 image_view_closed 또는 file_cleanup_report JSON을 Fleet Server로 보냅니다.
8. Fleet Server가 닫기/삭제 보고를 file_transfers 로그에 남깁니다.
```

주의:

```text
이미지 창을 닫는 행동은 기존 TCP 연결을 닫는 신호가 아닙니다.
JSON 요청 연결과 rsync 연결은 각각 요청/응답 또는 파일 복사 완료 후 종료됩니다.
창 닫기 후에는 Control UI가 새 JSON 요청으로 닫기/삭제 결과를 보고합니다.
```

서버 설정:

```json
{
  "file_transfer": {
    "enabled": true,
    "rsync_bin": "rsync",
    "rsync_timeout": 30.0,
    "server_image_dir": "sync/to_control/images",
    "allowed_source_dirs": [
      "sync/to_control/images"
    ]
  }
}
```

`allowed_source_dirs` 밖의 파일은 서버가 rsync로 보내지 않습니다.

#### image_request

Control UI가 서버에 이미지 전송을 요청합니다.

```json
{
  "v": 4,
  "mt": "operator_request",
  "msg_id": "MSG_20260622_IMAGE_REQUEST_000001",
  "ts": "2026-06-22T10:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "auth": {
    "token": "team_demo_token"
  },
  "user": "operator_1",
  "command": {
    "command_id": "CMD_20260622_IMAGE_REQUEST_000001",
    "group_id": null,
    "job_id": null,
    "command_seq": null,
    "command_revision": 0,
    "action": "image_request",
    "target_scope": "single",
    "targets": ["tb3_1"],
    "params": {
      "server_path": "/home/admin_kyj/openCV/server/sync/to_control/images/tb3_1_latest_map.png",
      "image_type": "latest_map",
      "delete_after_view": true
    },
    "expects": {
      "response_type": "sync",
      "status_followup": false
    },
    "timeout_sec": 10.0
  }
}
```

서버 응답:

```json
{
  "v": 4,
  "mt": "operator_response",
  "source": "fleet_server",
  "dest": "control_ui",
  "schema": "fleet_json_v0.4",
  "ok": true,
  "code": "R_FILE_SYNC_REPORTED",
  "message": "image transferred to control computer",
  "file_transfer": {
    "session_id": "SYNC_20260622_IMAGE_TB3_1_000001",
    "method": "rsync_over_ssh",
    "direction": "server_push",
    "source_path": "/home/admin_kyj/openCV/server/sync/to_control/images/tb3_1_latest_map.png",
    "control_host": "192.168.3.59",
    "control_user": "ubuntu",
    "control_path": "/home/ubuntu/openCV/cache/images/tb3_1_latest_map.png",
    "delete_after_view": true,
    "ok": true
  }
}
```

#### image_view_closed

Control UI가 이미지 창 닫기와 로컬 파일 삭제 결과를 보고합니다.

```json
{
  "v": 4,
  "mt": "operator_request",
  "msg_id": "MSG_20260622_IMAGE_CLOSED_000001",
  "ts": "2026-06-22T10:01:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "auth": {
    "token": "team_demo_token"
  },
  "user": "operator_1",
  "command": {
    "command_id": "CMD_20260622_IMAGE_CLOSED_000001",
    "group_id": null,
    "job_id": null,
    "command_seq": null,
    "command_revision": 0,
    "action": "image_view_closed",
    "target_scope": "single",
    "targets": ["tb3_1"],
    "params": {
      "session_id": "SYNC_20260622_IMAGE_TB3_1_000001",
      "displayed": true,
      "closed_by": "user",
      "local_file_deleted": true,
      "local_path": "/home/ubuntu/openCV/cache/images/tb3_1_latest_map.png"
    },
    "expects": {
      "response_type": "sync",
      "status_followup": false
    },
    "timeout_sec": 3.0
  }
}
```

`file_cleanup_report`는 이미지 창 닫기와 파일 삭제 보고를 분리하고 싶을 때 사용합니다. 구조는 `image_view_closed`와 같고 `action`만 `file_cleanup_report`로 바꿉니다.

서버는 아래 로그를 남깁니다.

```text
logs/server/file_transfers/latest_image_request.json
logs/server/file_transfers/latest_image_view_closed.json
logs/server/file_transfers/latest_file_cleanup_report.json
```

## 19. Result Code Enum

성공/진행 코드:

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
R_MAP_READY
R_PARTIAL_SUCCESS
```

실패/거부 코드:

```text
E_BAD_REQUEST
E_AUTH_FAILED
E_DUPLICATE_COMMAND
E_OUTDATED_COMMAND
E_JOB_ALREADY_CANCELED
E_UNKNOWN_ACTION
E_MODE_BLOCKED
E_ROBOT_BUSY
E_TARGET_INVALID
E_AGENT_DISCONNECTED
E_TIMEOUT
E_MAPPING_CONDITION
E_NAV_CONDITION
E_FILE_SYNC_FAILED
E_MAP_NOT_READY
E_SYSTEM_EMERGENCY
E_STATE_MISMATCH
E_INTERNAL_ERROR
```

## 20. Auth

실습용으로 `auth.token`을 지원합니다.

기본 token:

```text
team_demo_token
```

서버 설정:

```json
{
  "require_auth": false,
  "auth_token": "team_demo_token"
}
```

초기 개발 편의를 위해 `require_auth=false`이면 token이 없어도 동작하게 할 수 있습니다. 하지만 v4 `operator_request` 구조에는 `auth` 필드를 넣는 방향으로 작성합니다.

## 21. 현재 구현 상태

현재 구현/검증 상태는 아래와 같습니다.

```text
완료:
1. JSON_CONTRACT_V4.md 기준 v4 공통 구조 정리
2. fleet_protocol.py v4 검증 함수
3. action_policy.json 정책표
4. control_laptop_client.py v4 operator_request 생성
5. fleet_server_main.py v4 operator_request 처리
6. stop -> robot_stop 정규화
7. all_stop fan-out
8. operator_response v4 반환
9. mock_robot_agent.py v4 server_command/agent_result 지원
10. heartbeat_response/state_report 기본 구조
11. Control UI 이미지 요청/전송/닫기 보고 성공 로그 확인
```

```text
진행/확인 필요:
1. 실제 Robot Command Client 192.168.3.63:4000 연결
2. 실제 ROS2 /cmd_vel publish 결과 검증
3. 실제 TurtleBot map save 결과 파일 생성
4. Robot Agent -> Fleet Server map 파일 전송 방식 확정
5. 전송된 map 파일을 Control UI 이미지 요청 대상으로 연결
```

## 22. 현재 범위 밖 또는 확장 예정

```text
실제 ROS2 SLAM 완성
실제 Navigation2 goal 수행
실제 Robot Agent map rsync 전체 구현
실제 map save 전체 구현
실제 안전 PLC 수준 emergency 구현
실제 TurtleBot 장시간 주행 테스트
```

현재 안정화된 기준 흐름:

```text
Control UI -> Fleet Server -> Robot Agent Client
```

Robot Agent Client가 준비되지 않았을 때만 `mock_robot_agent.py`로 v4 JSON 구조를 비교 테스트합니다. mock 결과는 실제 로봇 수행 결과로 간주하지 않습니다.

## 23. 절대 주의사항

```text
기존 코드를 크게 갈아엎지 않고 점진적으로 수정합니다.
실제 TurtleBot을 움직이는 코드를 자동 실행하지 않습니다.
mock_robot_agent.py는 통신 검증용이며 실제 Robot Agent 대체물이 아닙니다.
실제 로봇 테스트 전에는 robot_stop과 all_stop을 먼저 확인합니다.
UI가 보낸 priority를 신뢰하지 않습니다.
READY를 operating_mode로 사용하지 않습니다.
job_status_request를 mt로 만들지 않고 action으로 처리합니다.
R_MOVE_STARTED 같은 미등록 Result Code를 새로 쓰지 않고 R_STARTED를 사용합니다.
stop은 UI alias이고, 서버 내부 표준은 robot_stop입니다.
MAP_READY 최종 판정은 서버가 합니다.
```
