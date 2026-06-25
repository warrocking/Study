# Fleet JSON v0.5.1 전체 규약

> v0.5를 기반으로 실제 운용에서 확인된 명령 구조, 상태 전이, 파라미터 규칙을 정리한 공식 규약입니다.
> 와이어 포맷(v=5, schema="fleet_json_v0.5")은 그대로 유지되므로 기존 코드와 하위 호환됩니다.

---

## 1. 공통 규칙

### 1-1. 네트워크

```
프로토콜: TCP + UTF-8 + NDJSON
JSON 1개 = 한 줄 (\n 으로 끝남)
Pretty JSON (들여쓰기) 금지 — 반드시 한 줄로 전송
```

| 채널 | 방향 | IP | 포트 |
|------|------|----|------|
| Control Health | 제어 → 서버 | 192.168.3.61 | 4000 |
| Control Command | 제어 → 서버 | 192.168.3.61 | 4001 |
| Control Data | 제어 → 서버 | 192.168.3.61 | 4002 |
| **Client Event** | **클라이언트 → 서버** | **192.168.3.61** | **4003** |
| Client Health | 서버 → 클라이언트 | 192.168.3.63 | 5000 |
| Client Command | 서버 → 클라이언트 | 192.168.3.63 | 5001 |
| Client Data | 서버 → 클라이언트 | 192.168.3.63 | 5002 |

### 1-2. 공통 헤더 (모든 JSON에 포함)

```json
{
  "v": 5,
  "mt": "<message_type>",
  "msg_id": "<고유 ID>",
  "ref": "<응답이면 원본 msg_id, 요청이면 null>",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "<발신자>",
  "dest": "<수신자>",
  "schema": "fleet_json_v0.5"
}
```

`source` / `dest` 가능 값: `"control_ui"` | `"fleet_server"` | `"robot_command_client"`

### 1-3. 로봇 ID 규칙

```
제어 UI / 사람이 쓰는 이름 : tb1
서버가 클라이언트에 보내는 wire robot_id : "14"
ROS namespace  : /tb1
ROS_DOMAIN_ID  : 14
cmd_vel topic  : /tb1/cmd_vel
```

---

## 2. 메시지 타입

### 제어 UI ↔ 서버

| 메시지 타입 | 방향 | 포트 |
|------------|------|------|
| `control_health_request` | 제어→서버 | 4000 |
| `control_health_response` | 서버→제어 | 4000 |
| `operator_request` / `control_command_request` | 제어→서버 | 4001 |
| `operator_response` | 서버→제어 | 4001 |
| `control_data_request` | 제어→서버 | 4002 |
| `control_data_response` | 서버→제어 | 4002 |

### 서버 ↔ 클라이언트

| 메시지 타입 | 방향 | 포트 |
|------------|------|------|
| `client_heartbeat_request` | 서버→클라이언트 | 5000 |
| `client_heartbeat_response` | 클라이언트→서버 | 5000 |
| `server_command` | 서버→클라이언트 | 5001 |
| `agent_result` | 클라이언트→서버 | 5001 |
| `client_data_prepare_request` | 서버→클라이언트 | 5002 |
| `client_data_prepare_response` | 클라이언트→서버 | 5002 |

---

## 3. operating_mode 상태 전이

```
STARTUP    → MANUAL      (부팅 완료)
MANUAL     → MAPPING     (start_mapping 성공)
MANUAL     → NAVIGATION  (nav_goal 성공, 지도 로드된 경우)
MAPPING    → MANUAL      (stop_mapping 성공)
NAVIGATION → MANUAL      (nav_cancel 또는 목표 도달)
ANY        → PAUSED      (pause_robot / pause_all)
PAUSED     → (이전 모드)  (resume_robot / resume_all)
ANY        → EMERGENCY   (emergency_stop)
EMERGENCY  → MANUAL      (clear_emergency 후)
```

### 모드별 허용 action 요약

| action | 허용 operating_mode |
|--------|-------------------|
| move_forward / move_backward / turn_left / turn_right / custom_move | MANUAL, MAPPING |
| start_mapping | MANUAL, AUTO, SERVICE |
| stop_mapping | MAPPING, PAUSED |
| save_map | MAPPING, SERVICE |
| rsync_map | MAPPING, SERVICE |
| nav_goal | AUTO, MANUAL |
| nav_cancel | NAVIGATION, PAUSED |
| robot_stop / all_stop / emergency_stop | ANY |
| pause_all / pause_robot | AUTO, MANUAL, MAPPING, NAVIGATION |
| resume_all / resume_robot | PAUSED |
| clear_emergency / reset_all_jobs | EMERGENCY, SERVICE |
| status_request / ping / mapping_status / map_status / nav_status 등 | ANY |

---

## 4. Action 명세

### 4-1. 이동 명령 (허용 모드: MANUAL, MAPPING)

#### move_forward

```json
{
  "action": "move_forward",
  "targets": ["tb1"],
  "target_scope": "single",
  "params": { "lx": 0.05, "dur": 2.0, "hz": 10, "stop": true }
}
```

| 파라미터 | 기본값 | 최대값 | 설명 |
|---------|--------|--------|------|
| `lx` | 0.05 | 0.1 | 선속도 m/s (서버가 절댓값 적용) |
| `dur` | 2.0 | 5.0 | 지속 시간 초 |
| `hz` | 10 | 50 | cmd_vel publish 주기 |
| `stop` | true | - | 완료 후 정지 명령 전송 여부 |

성공: `ok=true, code=R_DONE, state.robot_state=IDLE`

#### move_backward

move_forward와 동일. 서버가 lx에 음수 부호를 자동 적용.

#### turn_left

```json
{ "action": "turn_left", "params": { "az": 0.5, "dur": 2.0, "hz": 10, "stop": true } }
```

`az`: 각속도 rad/s (양수). 서버가 양수 부호 적용.

#### turn_right

turn_left와 동일. 서버가 az에 음수 부호를 자동 적용.

#### custom_move

```json
{ "action": "custom_move", "params": { "lx": 0.03, "az": 0.2, "dur": 3.0, "hz": 10, "stop": true } }
```

lx, az 모두 제어가 직접 지정. 서버는 부호를 변경하지 않음.

---

### 4-2. 정지 명령 (허용 모드: ANY)

#### robot_stop — 단일 로봇 정지

```json
{ "action": "robot_stop", "targets": ["tb1"], "target_scope": "single" }
```

성공: `ok=true, code=R_STOPPED, state.robot_state=STOPPED`

#### all_stop — 전체 로봇 정지

```json
{ "action": "all_stop", "targets": ["all"], "target_scope": "all" }
```

서버 내부에서 각 로봇에 `op=robot_stop` fanout.

#### emergency_stop — 긴급 정지 (최우선)

```json
{ "action": "emergency_stop", "targets": ["all"], "target_scope": "all" }
```

성공 후 서버 `global_state = "EMERGENCY"` 전환.
이후 이동·맵핑·네비 명령은 서버에서 `E_SYSTEM_EMERGENCY`로 거부.

---

### 4-3. 맵핑 명령

#### start_mapping — SLAM 시작 (허용 모드: MANUAL, AUTO, SERVICE)

```json
{
  "action": "start_mapping",
  "targets": ["tb1"],
  "target_scope": "single",
  "params": { "mode": "mapping" }
}
```

**자동 탐색 포함 시** (제어 UI가 명시적으로 추가):

```json
{ "params": { "mode": "mapping", "explore": true } }
```

- `explore: true` 없으면 SLAM만 시작, 이동은 수동 조작
- `explore: true` 있으면 클라이언트가 자율 탐색 실행
- 서버는 params를 그대로 전달 (수정 없음)

클라이언트 성공 응답:

```json
{
  "ok": true, "code": "R_STARTED",
  "state": {
    "operating_mode": "MAPPING", "robot_state": "MAPPING",
    "job_state": "RUNNING", "accept_state": "ACCEPTING", "ui_mode": "BUSY_QUEUEABLE"
  }
}
```

클라이언트 실패 응답 (이미 맵핑 중):

```json
{
  "ok": false, "code": "E_ROBOT_BUSY",
  "state": { "operating_mode": "MAPPING", "robot_state": "MAPPING", "job_state": "REJECTED", "accept_state": "BLOCKED" }
}
```

#### stop_mapping — SLAM 중단 (허용 모드: MAPPING, PAUSED)

```json
{ "action": "stop_mapping", "targets": ["tb1"], "target_scope": "single" }
```

클라이언트 성공 응답:

```json
{
  "ok": true, "code": "R_DONE",
  "state": { "operating_mode": "MANUAL", "robot_state": "IDLE", "job_state": "DONE", "accept_state": "ACCEPTING", "ui_mode": "READY" }
}
```

#### save_map — 맵 로컬 저장 (허용 모드: MAPPING, SERVICE)

```json
{
  "action": "save_map",
  "targets": ["tb1"],
  "target_scope": "single",
  "params": { "map_name": "lab_map_01" }
}
```

`map_name`: 저장 파일 이름 (선택, 없으면 클라이언트 기본값)

클라이언트 성공 응답:

```json
{
  "ok": true, "code": "R_MAP_LOCAL_SAVED",
  "state": { "operating_mode": "MAPPING", "robot_state": "MAPPING", "job_state": "DONE" }
}
```

> SLAM은 아직 실행 중이므로 operating_mode는 MAPPING을 유지합니다.
> save_map 후에도 rsync_map이 MAPPING 모드를 요구하므로 MANUAL로 전환하면 안 됩니다.

#### rsync_map — 서버가 맵 파일 pull (허용 모드: MAPPING, SERVICE)

```json
{ "action": "rsync_map", "targets": ["tb1"], "target_scope": "single" }
```

흐름:
1. 서버 → 클라이언트 5001: `op=rsync_map` server_command
2. 클라이언트 → 서버: `R_FILE_SYNC_REPORTED` agent_result
3. 서버 → 클라이언트 5002: `client_data_prepare_request`
4. 클라이언트 → 서버: 파일 목록/경로 응답
5. 서버가 rsync over SSH로 클라이언트 파일 pull
6. 서버가 결과를 제어 UI에 전달

클라이언트 성공 응답 (1단계):

```json
{
  "ok": true, "code": "R_FILE_SYNC_REPORTED",
  "state": { "operating_mode": "MAPPING", "robot_state": "MAPPING", "job_state": "DONE" }
}
```

#### 맵핑 전체 흐름 요약

```
제어: start_mapping ──────────────────── 서버: R_STARTED      (MAPPING 모드 진입)
      ↓
제어: move_forward / turn_left 등 ────── 수동으로 맵 영역 탐색  (MAPPING 모드 유지)
      ↓  (또는 explore:true면 자동 탐색)
제어: save_map ───────────────────────── 서버: R_MAP_LOCAL_SAVED  (클라이언트 저장, MAPPING 유지)
      ↓
제어: rsync_map ──────────────────────── 서버: 파일 pull 완료  (MAPPING 유지)
      ↓
제어: stop_mapping ───────────────────── 서버: R_DONE          (MANUAL 복귀)
```

**주의: save_map, rsync_map은 반드시 stop_mapping 이전에 실행해야 합니다.**
save_map과 rsync_map은 `allowed_operating_modes = ["MAPPING", "SERVICE"]`이므로
stop_mapping 후 MANUAL 모드에서는 서버가 `E_MODE_BLOCKED`로 거부합니다.

---

### 4-4. 네비게이션

#### nav_goal — 자율 이동 (허용 모드: AUTO, MANUAL)

저장된 지도 기반으로 목표 좌표까지 자율 이동.

```json
{
  "action": "nav_goal",
  "targets": ["tb1"],
  "target_scope": "single",
  "params": { "x": 1.5, "y": 0.8, "theta": 0.0 }
}
```

| 파라미터 | 설명 |
|---------|------|
| `x`, `y` | 지도 좌표계 기준 목표 위치 (m) |
| `theta` | 목표 방향 rad (0.0 = 정면) |

클라이언트 성공 응답 (이동 시작):

```json
{
  "ok": true, "code": "R_STARTED",
  "state": { "operating_mode": "NAVIGATION", "robot_state": "NAVIGATING", "job_state": "RUNNING", "accept_state": "ACCEPTING" }
}
```

#### nav_cancel — 네비게이션 취소 (허용 모드: NAVIGATION, PAUSED)

```json
{ "action": "nav_cancel", "targets": ["tb1"], "target_scope": "single" }
```

성공: `ok=true, code=R_CANCELED, state.operating_mode=MANUAL`

---

### 4-5. 상태 조회 (허용 모드: ANY)

| action | 설명 | 성공 코드 |
|--------|------|----------|
| `status_request` | 전체 서버+로봇 상태 | `R_STATUS` |
| `robot_state_request` | 특정 로봇 상태 | `R_STATUS` |
| `mapping_status` | 맵핑 진행 상태 | `R_STATUS` |
| `map_status` | 저장된 맵 정보 | `R_STATUS` |
| `map_list` | 저장된 맵 목록 | `R_STATUS` |
| `nav_status` | 네비게이션 진행 상태 | `R_STATUS` |
| `ping` | 연결 확인 | `R_PONG` |

---

### 4-6. 일시정지 / 재개

| action | target_scope | 허용 모드 | 성공 코드 |
|--------|-------------|----------|----------|
| `pause_robot` | single | AUTO, MANUAL, MAPPING, NAVIGATION | `R_PAUSED` |
| `pause_all` | all | AUTO, MANUAL, MAPPING, NAVIGATION | `R_PAUSED` |
| `resume_robot` | single | PAUSED | `R_RESUMED` |
| `resume_all` | all | PAUSED | `R_RESUMED` |

성공 후 `state.operating_mode`:
- pause → `PAUSED`
- resume → 이전 모드로 복귀 (클라이언트가 기억하여 보고)

---

### 4-7. 긴급 해제 및 초기화

#### clear_emergency (허용 모드: EMERGENCY, SERVICE)

```json
{ "action": "clear_emergency", "targets": ["all"], "target_scope": "all" }
```

성공 후 서버 `global_state = "NORMAL"` 복귀.

#### reset_all_jobs (허용 모드: PAUSED, SERVICE, ERROR)

```json
{ "action": "reset_all_jobs", "targets": ["all"], "target_scope": "all" }
```

현재 작업 큐 초기화. emergency 상태는 해제하지 않음.

---

### 4-8. 이미지 요청

#### image_request (허용 모드: ANY)

```json
{
  "action": "image_request",
  "targets": ["tb1"],
  "target_scope": "single",
  "params": { "data_type": "image" }
}
```

서버가 rsync로 이미지를 제어 PC `/home/ubuntu/openCV/cache/images`로 push.
성공: `ok=true, code=R_TRANSFER_DONE`

---

## 5. server_command 전체 구조

```json
{
  "v": 5,
  "mt": "server_command",
  "msg_id": "MSG_20260624_SERVER_COMMAND_TB1_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "fleet_server",
  "dest": "robot_command_client",
  "schema": "fleet_json_v0.5",
  "command": {
    "command_id": "CMD_START_MAPPING_20260624_...",
    "parent_command_id": null,
    "group_id": null,
    "job_id": "JOB_START_MAPPING_TB1_...",
    "command_seq": null,
    "command_revision": 0,
    "op": "start_mapping",
    "server_priority": 40,
    "blocking_type": "SOFT",
    "interrupt_policy": "reject_if_busy",
    "robot_id": "14",
    "ros": {
      "domain_id": 14,
      "namespace": "/tb1",
      "topic": "/tb1/cmd_vel"
    },
    "params": { "mode": "mapping" },
    "timeout_sec": 5.0
  }
}
```

---

## 6. agent_result 전체 구조 및 매칭 규칙

```json
{
  "v": 5,
  "mt": "agent_result",
  "msg_id": "MSG_AGENT_RESULT_...",
  "ref": "<server_command.msg_id>",
  "ts": "2026-06-24T12:00:01+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
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
  "message": "tb1 완료",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MANUAL",
    "robot_state": "IDLE",
    "job_state": "DONE",
    "accept_state": "ACCEPTING",
    "ui_mode": "READY"
  },
  "perf": {
    "elapsed_ms": 120,
    "dur": 2.0,
    "hz": 10,
    "pub": 20,
    "sent_cmd_vel_zero": true
  },
  "err": []
}
```

### 필수 매칭 규칙 (어기면 서버가 E_STATE_MISMATCH 처리)

```
agent_result.ref                == server_command.msg_id
agent_result.robot_id           == server_command.command.robot_id  ("14")
agent_result.command.command_id == server_command.command.command_id
agent_result.command.op         == server_command.command.op
```

---

## 7. 상태 필드 값 정의

### operating_mode

| 값 | 의미 |
|----|------|
| `STARTUP` | 부팅 중 |
| `MANUAL` | 수동 조작 가능 (기본) |
| `MAPPING` | SLAM 맵핑 중 |
| `NAVIGATION` | 자율 네비게이션 중 |
| `AUTO` | 자율 모드 대기 |
| `PAUSED` | 일시정지 |
| `SERVICE` | 정비 모드 |
| `EMERGENCY` | 긴급 정지 상태 |
| `SHUTDOWN` | 종료 중 |

### robot_state

| 값 | 의미 |
|----|------|
| `IDLE` | 대기 중 |
| `MOVING` | 이동 중 |
| `MAPPING` | 맵핑 중 |
| `NAVIGATING` | 네비게이션 중 |
| `SAVING_MAP` | 맵 저장 중 |
| `SYNCING_FILE` | 파일 전송 중 |
| `STOPPED` | 정지됨 |
| `PAUSED` | 일시정지됨 |
| `EMERGENCY` | 긴급 정지 |
| `ERROR` | 오류 상태 |
| `DISCONNECTED` | 미연결 |

### job_state

| 값 | 의미 |
|----|------|
| `NONE` | 작업 없음 |
| `RUNNING` | 실행 중 |
| `DONE` | 완료 |
| `FAILED` | 실패 |
| `REJECTED` | 거부됨 |
| `CANCELED` | 취소됨 |
| `PAUSED` | 일시정지됨 |

---

## 8. 결과 코드 전체 목록

### 성공 코드 (R_)

| 코드 | 의미 |
|------|------|
| `R_DONE` | 명령 정상 완료 |
| `R_STARTED` | 백그라운드 작업 시작 (맵핑, 네비 등) |
| `R_STOPPED` | 정지 완료 |
| `R_PAUSED` | 일시정지 완료 |
| `R_RESUMED` | 재개 완료 |
| `R_CANCELED` | 취소 완료 |
| `R_STATUS` | 상태 조회 완료 |
| `R_PONG` | ping 응답 |
| `R_MAP_LOCAL_SAVED` | 맵 클라이언트 로컬 저장 완료 |
| `R_FILE_SYNC_REPORTED` | 파일 동기화 보고 완료 |
| `R_TRANSFER_DONE` | 파일 서버→제어 전송 완료 |
| `R_CLIENT_ALIVE` | 클라이언트 헬스 응답 |

### 오류 코드 (E_)

| 코드 | 의미 |
|------|------|
| `E_UNKNOWN_ACTION` | 지원하지 않는 op |
| `E_ROBOT_BUSY` | 로봇이 다른 작업 중 |
| `E_MODE_BLOCKED` | 현재 operating_mode에서 불허 |
| `E_SYSTEM_EMERGENCY` | 서버가 EMERGENCY 상태 |
| `E_TIMEOUT` | 응답 시간 초과 |
| `E_AGENT_DISCONNECTED` | 클라이언트 연결 없음 |
| `E_TARGET_INVALID` | 잘못된 robot_id / target |
| `E_STATE_MISMATCH` | ref/robot_id/command_id/op 불일치 |
| `E_MAPPING_CONDITION` | 맵핑 조건 미충족 |
| `E_NAV_CONDITION` | 네비 조건 미충족 |
| `E_FILE_SYNC_FAILED` | 파일 동기화 실패 |
| `E_BAD_REQUEST` | JSON 구조 오류 |
| `E_DUPLICATE_COMMAND` | 중복 command_id |
| `E_INTERNAL_ERROR` | 서버/클라이언트 내부 오류 |

---

## 9. 맵핑 완료 자동화 흐름 (클라이언트 주도)

### 9-1. 맵 디렉토리 이름 규칙

```
YYYYMMDD_HHMMSS_turtlebotName_saveMethod_saveNumber
```

| 필드 | 설명 | 예시 |
|------|------|------|
| YYYYMMDD | 맵핑 시작 날짜 | 20260624 |
| HHMMSS | 맵핑 시작 시간 | 164951 |
| turtlebotName | 터틀봇 별칭 | tb1 / tb2 / tb3 |
| saveMethod | 저장 방식 | autoSave / stop / emergency |
| saveNumber | 누적 맵핑 횟수 (클라이언트 카운트) | 1 |

예시: `20260624_164951_tb1_autoSave_1`
```
20260624_164951_tb1_autoSave_1/
├─ map.pgm
└─ map.yaml
```

서버는 클라이언트에서 pull 받을 때 동일한 이름의 디렉토리로 저장합니다.

### 9-2. 클라이언트 → 서버 맵핑 완료 통지 (포트 4003)

맵핑 완료 후 클라이언트가 서버 IP:4003에 연결해 전송합니다.

**클라이언트 → 서버 요청:**

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

**서버 → 클라이언트 ACK:**

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

ACK 전송 후 서버는 백그라운드 스레드에서 SSH rsync로 해당 디렉토리를 pull합니다.

### 9-3. notification 필드 규칙

| 필드 | 필수 | 설명 |
|------|------|------|
| robot_alias | 권장 | tb1 / tb2 / tb3 |
| robot_id | 선택 | "14" 등 wire robot_id |
| map_dir_name | **필수** | 클라이언트가 생성한 디렉토리 이름 |
| save_method | 권장 | autoSave / stop / emergency |
| map_start_ts | 권장 | 맵핑 시작 시각 (ISO 8601) |
| client_map_dir | **필수** | 클라이언트의 해당 디렉토리 절대 경로 |
| files | 선택 | 저장된 파일 목록 |

### 9-4. 맵 목록 조회 (제어 → 서버 4001)

```json
{
  "v": 5,
  "mt": "control_command_request",
  "command": {
    "action": "map_list",
    "target_scope": "all",
    "targets": ["all"],
    "params": {
      "robot": "tb1"
    }
  }
}
```

`params.robot` 생략 시 전체 로봇의 맵 목록을 반환합니다.

**서버 응답 (operator_response):**

```json
{
  "ok": true,
  "code": "R_STATUS",
  "message": "2 maps found (robot=tb1)",
  "status": {
    "maps": [
      {
        "index": 1,
        "dir_name": "20260624_164951_tb1_autoSave_1",
        "date": "2026-06-24",
        "time": "16:49:51",
        "robot": "tb1",
        "save_method": "autoSave",
        "save_number": 1,
        "files": ["map.pgm", "map.yaml"],
        "display": "2026-06-24 16:49:51 | tb1 | autoSave | #1"
      },
      {
        "index": 2,
        "dir_name": "20260625_091030_tb1_stop_2",
        "date": "2026-06-25",
        "time": "09:10:30",
        "robot": "tb1",
        "save_method": "stop",
        "save_number": 2,
        "files": ["map.pgm", "map.yaml"],
        "display": "2026-06-25 09:10:30 | tb1 | stop | #2"
      }
    ],
    "map_total": 2
  }
}
```

### 9-5. 맵 이미지 선택 및 제어로 전송 (제어 → 서버 4001)

제어 UI가 목록에서 원하는 맵을 번호로 선택합니다.

```json
{
  "v": 5,
  "mt": "control_command_request",
  "command": {
    "action": "map_image_select",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": {
      "index": 1
    }
  }
}
```

또는 디렉토리 이름으로 직접 선택:

```json
{
  "command": {
    "action": "map_image_select",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": {
      "dir_name": "20260624_164951_tb1_autoSave_1"
    }
  }
}
```

서버는 해당 디렉토리의 map.pgm + map.yaml을 SSH rsync로 제어 컴퓨터의 `control_map_receive_dir`에 전송합니다.

전송 경로: `제어:/home/ubuntu/turtlebot_control/data/maps/20260624_164951_tb1_autoSave_1/`

### 9-6. 전체 자동화 흐름 요약

```
1. 제어 → start_mapping → 서버 → 클라이언트 (SLAM 시작)
2. 클라이언트: 자율 탐색 중...
3. 클라이언트: 완료 조건 감지 → SLAM 종료 → 맵 로컬 저장
   (디렉토리 이름 규칙 적용: YYYYMMDD_HHMMSS_tb1_autoSave_N)
4. 클라이언트 → 서버:4003 mapping_complete_notification 전송
5. 서버: ACK 전송 → 백그라운드 SSH rsync로 맵 pull
   (data/maps/20260624_164951_tb1_autoSave_1/)
6. 제어 → map_list 요청 → 서버: 맵 목록 JSON 응답
7. 제어: 목록 표시, 사용자가 번호 입력
8. 제어 → map_image_select (index=N) 요청
9. 서버: SSH rsync로 해당 디렉토리 → 제어 컴퓨터 전송
10. 제어: map.pgm / map.yaml 수신 → 이미지로 가공 표시
```

---

## 10. 절대 규칙 요약

```
1. 모든 JSON은 한 줄 (\n 종료). Pretty JSON 금지.
2. 요청을 받으면 반드시 응답 후 연결 종료. 무응답 절대 금지.
3. 실패해도 ok=false agent_result 반드시 반환.
4. code 값은 "OK", "DONE", "ERROR" 사용 금지 → R_* 또는 E_* 만 사용.
5. agent_result의 ref / robot_id / command_id / op 4가지 매칭 필수.
6. start_mapping 성공 시 operating_mode=MAPPING 보고 필수.
   (이후 stop_mapping / save_map / rsync_map 허용 여부가 이 값에 달림)
7. explore: true 파라미터는 제어 UI가 명시적으로 보내야 함.
   서버는 params를 변경하지 않고 그대로 클라이언트에 전달.
8. 맵 저장 디렉토리 이름은 YYYYMMDD_HHMMSS_robotName_saveMethod_saveNumber 규칙을 반드시 따름.
   (서버가 파싱 불가하면 map_list에 포함되지 않음)
9. mapping_complete_notification의 client_map_dir / map_dir_name 두 필드는 필수.
```
