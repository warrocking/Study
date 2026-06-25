# Robot Command Client v0.5.1 작업 지시 프롬프트

당신은 TurtleBot 협업 제어 시스템의 **Robot Command Client** 담당자입니다.

Fleet Server v0.5.1이 준비되어 있습니다. 클라이언트는 서버가 보내는 JSON을 수신하고, 해당 명령을 실제 TurtleBot ROS2로 실행한 뒤 결과를 JSON으로 반환해야 합니다.

---

## 로봇 기준 정보

```
display alias  : tb1
wire robot_id  : 14        ← 서버가 JSON에 넣어 보내는 실제 ID
ROS namespace  : /tb1
cmd_vel topic  : /tb1/cmd_vel
ROS_DOMAIN_ID  : 14
```

제어 UI나 사람은 "tb1"이라고 부르지만, 서버가 클라이언트에 보내는 `command.robot_id`는 항상 `"14"`입니다.

---

## 1. 네트워크 기준

```
프로토콜: TCP + UTF-8 + NDJSON
JSON 1개 = 한 줄 (\n 종료). Pretty JSON 절대 금지.
서버가 접속해 옴 (클라이언트가 listen)
```

| 포트 | 방향 | 역할 | 요청 mt | 응답 mt |
|------|------|------|---------|---------|
| 5000 | 서버 → 클라이언트 | Health | `client_heartbeat_request` | `client_heartbeat_response` |
| 5001 | 서버 → 클라이언트 | Command | `server_command` | `agent_result` |
| 5002 | 서버 → 클라이언트 | Data | `client_data_prepare_request` | `client_data_prepare_response` |
| **4003** | **클라이언트 → 서버** | **맵핑 완료 통지** | `mapping_complete_notification` | `mapping_complete_ack` |

서버가 보내는 연결 (5000/5001/5002): 서버가 명령마다 새 TCP 연결을 열고, JSON 1줄 송신 → 응답 1줄 수신 후 연결을 닫습니다.

클라이언트가 보내는 연결 (4003): 맵핑이 완료되면 **클라이언트가** 서버 IP:4003에 TCP 연결을 열고, `mapping_complete_notification` 1줄 전송 → ACK 수신 후 연결을 닫습니다.

---

## 2. Health 포트 (5000)

### 수신: client_heartbeat_request

```json
{
  "v": 5, "mt": "client_heartbeat_request",
  "msg_id": "MSG_CLIENT_HB_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "fleet_server", "dest": "robot_command_client",
  "schema": "fleet_json_v0.5",
  "request": {
    "include_robot_states": true,
    "robots": ["14"]
  }
}
```

### 반환: client_heartbeat_response

```json
{
  "v": 5, "mt": "client_heartbeat_response",
  "msg_id": "MSG_CLIENT_HB_RESP_000001",
  "ref": "MSG_CLIENT_HB_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "robot_command_client", "dest": "fleet_server",
  "schema": "fleet_json_v0.5",
  "ok": true,
  "code": "R_CLIENT_ALIVE",
  "message": "robot command client alive",
  "client": {
    "connection_state": "CONNECTED"
  },
  "robots": {
    "14": {
      "connection_state": "CONNECTED",
      "operating_mode": "MANUAL",
      "robot_state": "IDLE",
      "job_state": "NONE",
      "accept_state": "ACCEPTING",
      "ui_mode": "READY"
    }
  }
}
```

**터틀봇과 연결되지 않은 경우:**

```json
{
  "ok": false,
  "code": "E_AGENT_DISCONNECTED",
  "client": { "connection_state": "DISCONNECTED" },
  "robots": {
    "14": {
      "connection_state": "DISCONNECTED",
      "operating_mode": "MANUAL",
      "robot_state": "DISCONNECTED",
      "job_state": "NONE",
      "accept_state": "BLOCKED",
      "ui_mode": "OFFLINE"
    }
  }
}
```

---

## 3. Command 포트 (5001) — server_command 구조

서버가 클라이언트에 보내는 명령 공통 구조:

```json
{
  "v": 5, "mt": "server_command",
  "msg_id": "MSG_20260624_SERVER_COMMAND_TB1_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "fleet_server", "dest": "robot_command_client",
  "schema": "fleet_json_v0.5",
  "command": {
    "command_id": "CMD_...",
    "parent_command_id": null,
    "group_id": null,
    "job_id": "JOB_...",
    "command_seq": null,
    "command_revision": 0,
    "op": "<action명>",
    "server_priority": 40,
    "blocking_type": "SOFT",
    "interrupt_policy": "reject_if_busy",
    "robot_id": "14",
    "ros": { "domain_id": 14, "namespace": "/tb1", "topic": "/tb1/cmd_vel" },
    "params": { },
    "timeout_sec": 5.0
  }
}
```

### agent_result 필수 매칭 규칙

```
agent_result.ref                == server_command.msg_id
agent_result.robot_id           == server_command.command.robot_id  ("14")
agent_result.command.command_id == server_command.command.command_id
agent_result.command.op         == server_command.command.op
```

이 4개가 맞지 않으면 서버가 `E_STATE_MISMATCH`로 처리합니다.

### agent_result 공통 구조

```json
{
  "v": 5, "mt": "agent_result",
  "msg_id": "MSG_AGENT_RESULT_...",
  "ref": "<server_command.msg_id>",
  "ts": "2026-06-24T12:00:01+09:00",
  "source": "robot_command_client", "dest": "fleet_server",
  "schema": "fleet_json_v0.5",
  "robot_id": "14",
  "command": {
    "command_id": "<server_command.command.command_id>",
    "parent_command_id": null,
    "group_id": null,
    "job_id": "<server_command.command.job_id>",
    "op": "<server_command.command.op>"
  },
  "ok": true,
  "code": "R_DONE",
  "message": "처리 결과 메시지",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MANUAL",
    "robot_state": "IDLE",
    "job_state": "DONE",
    "accept_state": "ACCEPTING",
    "ui_mode": "READY"
  },
  "perf": { "elapsed_ms": 100 },
  "err": []
}
```

---

## 4. op별 처리 명세

### 4-1. 이동 명령 (move_forward / move_backward / turn_left / turn_right / custom_move)

서버가 보내는 params:

| op | params 내용 |
|----|------------|
| `move_forward` | `lx`(양수), `az=0`, `dur`, `hz`, `stop` |
| `move_backward` | `lx`(음수), `az=0`, `dur`, `hz`, `stop` |
| `turn_left` | `lx=0`, `az`(양수), `dur`, `hz`, `stop` |
| `turn_right` | `lx=0`, `az`(음수), `dur`, `hz`, `stop` |
| `custom_move` | `lx`, `az`, `dur`, `hz`, `stop` |

서버가 이미 방향 부호를 적용해서 보냅니다. 클라이언트는 받은 lx, az를 그대로 cmd_vel에 publish.

성공 응답:

```json
{
  "ok": true, "code": "R_DONE",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MANUAL",
    "robot_state": "IDLE",
    "job_state": "DONE",
    "accept_state": "ACCEPTING",
    "ui_mode": "READY"
  },
  "perf": { "elapsed_ms": 2100, "dur": 2.0, "hz": 10, "pub": 20, "sent_cmd_vel_zero": true }
}
```

`dur`초 동안 cmd_vel publish 후, `stop=true`이면 `lx=0, az=0` 한 번 더 publish.

---

### 4-2. 정지 명령 (robot_stop / emergency_stop)

```
op: robot_stop 또는 emergency_stop
params: { lx: 0.0, az: 0.0, dur: 0.0, hz: 10, stop: true, reason: "..." }
```

즉시 `lx=0, az=0` publish 후 응답.

성공 응답:

```json
{
  "ok": true, "code": "R_STOPPED",
  "state": {
    "operating_mode": "MANUAL",
    "robot_state": "STOPPED",
    "job_state": "DONE",
    "accept_state": "ACCEPTING"
  }
}
```

---

### 4-3. start_mapping

```
op: start_mapping
params: { "mode": "mapping" }
  또는: { "mode": "mapping", "explore": true }
```

- `explore` 없음 → Cartographer SLAM 시작만. 이동은 수동.
- `explore: true` → SLAM + 자율 탐색(explore) 함께 실행.

성공 응답:

```json
{
  "ok": true, "code": "R_STARTED",
  "state": {
    "operating_mode": "MAPPING",
    "robot_state": "MAPPING",
    "job_state": "RUNNING",
    "accept_state": "ACCEPTING",
    "ui_mode": "BUSY_QUEUEABLE"
  }
}
```

**중요: `operating_mode=MAPPING`을 반드시 보고해야 합니다.**
이 값이 없으면 서버가 이후 save_map / rsync_map / stop_mapping 명령을 거부합니다.

**올바른 실행 순서: save_map → rsync_map → stop_mapping**
save_map과 rsync_map은 MAPPING 모드에서만 허용됩니다.
stop_mapping을 먼저 보내면 MANUAL 모드로 전환되어 save_map이 거부됩니다.

---

### 4-4. stop_mapping

```
op: stop_mapping
params: {}
```

Cartographer SLAM 중단.

성공 응답:

```json
{
  "ok": true, "code": "R_DONE",
  "state": {
    "operating_mode": "MANUAL",
    "robot_state": "IDLE",
    "job_state": "DONE",
    "accept_state": "ACCEPTING",
    "ui_mode": "READY"
  }
}
```

---

### 4-5. save_map

```
op: save_map
params: { "map_name": "lab_map_01" }  (map_name 없을 수도 있음)
```

맵 파일을 클라이언트 로컬에 저장 (yaml + pgm).
SLAM은 아직 실행 중이므로 operating_mode는 MAPPING을 유지합니다.

성공 응답:

```json
{
  "ok": true, "code": "R_MAP_LOCAL_SAVED",
  "state": {
    "operating_mode": "MAPPING",
    "robot_state": "MAPPING",
    "job_state": "DONE"
  }
}
```

---

### 4-6. rsync_map

```
op: rsync_map
params: {}
```

서버가 포트 5002로 별도 연결해서 파일 목록을 요청합니다.
클라이언트는 **agent_result만 먼저 반환**하고 5002 요청을 기다립니다.

```json
{
  "ok": true, "code": "R_FILE_SYNC_REPORTED",
  "state": {
    "operating_mode": "MAPPING",
    "robot_state": "MAPPING",
    "job_state": "DONE"
  }
}
```

**5002 포트에서의 추가 처리** (client_data_prepare_request 수신 시):

```json
{
  "v": 5, "mt": "client_data_prepare_response",
  "ok": true,
  "files": [
    { "name": "tb1_map.yaml", "path": "/home/user/maps/tb1_map.yaml", "size_bytes": 512 },
    { "name": "tb1_map.pgm",  "path": "/home/user/maps/tb1_map.pgm",  "size_bytes": 204800 }
  ],
  "map_source_dir": "/home/user/maps"
}
```

그 후 서버가 rsync over SSH로 해당 경로에서 파일을 가져갑니다.

---

### 4-7. nav_goal

```
op: nav_goal
params: { "x": 1.5, "y": 0.8, "theta": 0.0 }
```

저장된 지도 기반 Nav2 목표 전송.

성공 응답 (이동 시작):

```json
{
  "ok": true, "code": "R_STARTED",
  "state": {
    "operating_mode": "NAVIGATION",
    "robot_state": "NAVIGATING",
    "job_state": "RUNNING",
    "accept_state": "ACCEPTING",
    "ui_mode": "BUSY_QUEUEABLE"
  }
}
```

---

### 4-8. nav_cancel

```
op: nav_cancel
params: {}
```

성공 응답:

```json
{
  "ok": true, "code": "R_CANCELED",
  "state": { "operating_mode": "MANUAL", "robot_state": "IDLE", "job_state": "CANCELED" }
}
```

---

### 4-9. 상태 조회 (status_request / robot_state_request / mapping_status / nav_status 등)

서버가 이 op들을 보내면 클라이언트는 현재 상태를 담아 즉시 응답.

```json
{
  "ok": true, "code": "R_STATUS",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MAPPING",
    "robot_state": "MAPPING",
    "job_state": "RUNNING",
    "accept_state": "ACCEPTING",
    "ui_mode": "BUSY_QUEUEABLE"
  }
}
```

---

### 4-10. pause_robot / resume_robot

pause:
```json
{ "ok": true, "code": "R_PAUSED", "state": { "operating_mode": "PAUSED", "robot_state": "PAUSED", "job_state": "PAUSED" } }
```

resume:
```json
{ "ok": true, "code": "R_RESUMED", "state": { "operating_mode": "<이전 모드>", "robot_state": "IDLE", "job_state": "NONE" } }
```

---

## 5. 에러 응답 공통 형식

op를 지원하지 않거나 실패할 경우:

```json
{
  "ok": false,
  "code": "E_UNKNOWN_ACTION",
  "message": "Unsupported op: <op명>",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MANUAL",
    "robot_state": "IDLE",
    "job_state": "FAILED",
    "accept_state": "ACCEPTING",
    "ui_mode": "READY"
  },
  "perf": { "elapsed_ms": 0 },
  "err": [
    { "code": "E_UNKNOWN_ACTION", "message": "Unsupported op: <op명>", "where": "robot_command_client" }
  ]
}
```

---

## 6. 사용 가능한 result code 목록

### 성공 (ok=true)

```
R_DONE            명령 완료
R_STARTED         백그라운드 작업 시작 (맵핑, 네비 등)
R_STOPPED         정지 완료
R_PAUSED          일시정지 완료
R_RESUMED         재개 완료
R_CANCELED        취소 완료
R_STATUS          상태 조회 완료
R_PONG            ping 응답
R_MAP_LOCAL_SAVED 맵 로컬 저장 완료
R_FILE_SYNC_REPORTED 파일 동기화 보고 완료
R_CLIENT_ALIVE    헬스 응답
```

### 실패 (ok=false)

```
E_UNKNOWN_ACTION  지원하지 않는 op
E_ROBOT_BUSY      로봇이 다른 작업 중
E_TIMEOUT         처리 시간 초과
E_INTERNAL_ERROR  내부 오류
E_AGENT_DISCONNECTED  터틀봇 연결 없음
E_MAPPING_CONDITION   맵핑 조건 미충족
E_NAV_CONDITION       네비 조건 미충족
```

**절대 금지 코드**: `"OK"`, `"DONE"`, `"ERROR"`, `"FAIL"` — 서버가 내부적으로 E_INTERNAL_ERROR로 치환합니다.

---

## 7. 맵핑 완료 통지 (클라이언트 → 서버 4003)

맵핑이 완료되고 맵을 로컬에 저장한 직후, 클라이언트가 서버에 알립니다.

### 디렉토리 이름 규칙

```
YYYYMMDD_HHMMSS_turtlebotName_saveMethod_saveNumber
```

| 필드 | 설명 |
|------|------|
| YYYYMMDD / HHMMSS | 맵핑 **시작** 시각 |
| turtlebotName | tb1 / tb2 / tb3 |
| saveMethod | autoSave (자동완료) / stop (운영자 정지) / emergency (긴급정지) |
| saveNumber | 클라이언트의 maps 디렉토리 내 누적 디렉토리 개수 + 1 |

예시: `20260624_164951_tb1_autoSave_1`

```
/home/ubuntu/turtlebot_client/data/maps/
└─ 20260624_164951_tb1_autoSave_1/
   ├─ map.pgm
   └─ map.yaml
```

### 전송 절차

1. 맵 저장 완료 확인
2. 서버 IP:4003에 TCP 연결
3. `mapping_complete_notification` 전송 (한 줄)
4. `mapping_complete_ack` 수신 확인 (ok=true이면 성공)
5. 연결 종료

### 전송 JSON

```json
{
  "v": 5,
  "mt": "mapping_complete_notification",
  "msg_id": "MSG_MAPPING_COMPLETE_TB1_001",
  "ts": "2026-06-24T16:52:30+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "notification": {
    "robot_id": "14",
    "robot_alias": "tb1",
    "map_dir_name": "20260624_164951_tb1_autoSave_1",
    "save_method": "autoSave",
    "map_start_ts": "2026-06-24T16:49:51+09:00",
    "client_map_dir": "/home/ubuntu/turtlebot_client/data/maps/20260624_164951_tb1_autoSave_1",
    "files": ["map.pgm", "map.yaml"]
  }
}
```

### 서버 ACK

```json
{
  "v": 5,
  "mt": "mapping_complete_ack",
  "ref": "MSG_MAPPING_COMPLETE_TB1_001",
  "ok": true,
  "code": "R_ACCEPTED",
  "message": "mapping complete notification received for 20260624_164951_tb1_autoSave_1, sync will begin"
}
```

ACK를 받으면 서버가 백그라운드에서 SSH rsync로 디렉토리를 가져갑니다. 클라이언트는 별도 작업 없이 연결만 끊으면 됩니다.

---

## 8. 절대 지켜야 할 규칙

```
1. JSON 한 줄 전송. Pretty JSON 금지.
2. 모든 server_command에 반드시 agent_result 반환. 무응답 금지.
3. 실패해도 ok=false agent_result를 반환 (연결 그냥 끊으면 안 됨).
4. ref / robot_id / command_id / op 매칭 4개 필수.
5. start_mapping 성공 시 반드시 operating_mode=MAPPING 보고.
6. explore 파라미터는 서버가 넣어준 대로만 처리 (없으면 수동, 있으면 자율).
7. 맵 저장 디렉토리 이름은 YYYYMMDD_HHMMSS_robotName_saveMethod_N 규칙 필수.
8. mapping_complete_notification의 client_map_dir / map_dir_name 두 필드 필수.
```

---

## 9. 구현 완료 확인 체크리스트

```
[ ] 5000 포트 listen → client_heartbeat_response 반환
[ ] 5001 포트 listen → server_command 수신 → agent_result 반환
[ ] 5002 포트 listen → client_data_prepare_request 수신 → 파일 목록 반환
[ ] move_forward / move_backward / turn_left / turn_right / custom_move 처리
[ ] robot_stop / emergency_stop 처리
[ ] start_mapping (SLAM 시작) → R_STARTED + operating_mode=MAPPING 보고
[ ] stop_mapping (SLAM 중단) → R_DONE + operating_mode=MANUAL 보고
[ ] save_map (맵 로컬 저장) → R_MAP_LOCAL_SAVED
[ ] rsync_map (서버 pull 대기) → R_FILE_SYNC_REPORTED
[ ] nav_goal (Nav2 목표 전송) → R_STARTED + operating_mode=NAVIGATION
[ ] nav_cancel → R_CANCELED
[ ] status_request / robot_state_request / mapping_status 등 상태 조회 → R_STATUS
[ ] 알 수 없는 op → E_UNKNOWN_ACTION (서버 연결 끊지 않고 응답)
[ ] 맵핑 완료 후 서버 IP:4003에 mapping_complete_notification 전송
[ ] mapping_complete_ack 수신 확인 후 연결 종료
```
