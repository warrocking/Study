# Fleet JSON v0.6 전체 규약

> 이 문서는 TurtleBot 협업 제어 시스템의 공식 통신 규약입니다.
> v0.5.1 대비 변경 사항: 포트 4003 추가, 맵 디렉토리 이름 규칙, `mapping_complete_notification`,
> `map_list` 메타데이터 응답, `map_image_select` 신규 action.

---

## 1. 버전 식별자

모든 JSON 메시지에 반드시 포함:

```json
{
  "v": 6,
  "schema": "fleet_json_v0.6"
}
```

**서버 수락 범위 (인바운드):** `v=5` 또는 `v=6` 모두 수락 (전환기 하위 호환)
**서버 발신 (아웃바운드):** 항상 `v=6, schema=fleet_json_v0.6` 사용

---

## 2. 네트워크 기본 규칙

```
프로토콜: TCP + UTF-8 + NDJSON
JSON 1개 = 한 줄 (\n 으로 끝남)
Pretty JSON (들여쓰기) 절대 금지 — 반드시 한 줄로 전송
연결: 명령 1회 → 응답 1회 → 연결 종료 (단, 4003은 단방향 알림)
```

---

## 3. 포트 전체 목록

| 채널 | 방향 | 대상 IP | 포트 | 용도 |
|------|------|---------|------|------|
| Control Health | 제어 → 서버 | 192.168.3.61 | **4000** | 서버 생존 확인 |
| Control Command | 제어 → 서버 | 192.168.3.61 | **4001** | 터틀봇 명령 전달 (map_list / map_image_select 포함) |
| Control Data | 제어 → 서버 | 192.168.3.61 | **4002** | 카메라 이미지/로그 요청 전용 (image_request) |
| **Client Event** | **클라이언트 → 서버** | **192.168.3.61** | **4003** | **맵핑 완료 통지** |
| Client Health | 서버 → 클라이언트 | 192.168.3.63 | **5000** | 클라이언트 생존 확인 |
| Client Command | 서버 → 클라이언트 | 192.168.3.63 | **5001** | TurtleBot 명령 실행 |
| Client Data | 서버 → 클라이언트 | 192.168.3.63 | **5002** | 파일 목록/경로 요청 |

> **포트 4003은 방향이 반대입니다.** 클라이언트가 서버에 먼저 연결합니다.
>
> ⚠️ **포트 4001 vs 4002 혼동 주의:**
> `map_list` 와 `map_image_select` 는 **포트 4001** (Control Command) 을 통해 `control_command_request` 로 전송합니다.
> 포트 4002 (Control Data) 는 **카메라 이미지/로그 조회 전용** 이며, 맵 목록/맵 이미지 선택에는 사용하지 않습니다.
> 포트 5000–5002 는 서버 ↔ 클라이언트 전용이며, 제어 UI 는 절대 사용하지 않습니다.

---

## 4. 메시지 타입 전체 목록

### 4-1. 제어 UI ↔ 서버

| 메시지 타입 | 방향 | 포트 | 설명 |
|------------|------|------|------|
| `control_health_request` | 제어→서버 | 4000 | 헬스 요청 |
| `control_health_response` | 서버→제어 | 4000 | 헬스 응답 |
| `control_command_request` | 제어→서버 | 4001 | 명령 요청 (v6 방식) |
| `operator_request` | 제어→서버 | 4001 | 명령 요청 (v5 호환) |
| `operator_response` | 서버→제어 | 4001 | 명령 응답 |
| `control_data_request` | 제어→서버 | 4002 | 데이터 요청 |
| `control_data_response` | 서버→제어 | 4002 | 데이터 응답 |

### 4-2. 서버 ↔ 클라이언트 (기존)

| 메시지 타입 | 방향 | 포트 | 설명 |
|------------|------|------|------|
| `client_heartbeat_request` | 서버→클라이언트 | 5000 | 헬스 요청 |
| `client_heartbeat_response` | 클라이언트→서버 | 5000 | 헬스 응답 |
| `server_command` | 서버→클라이언트 | 5001 | TurtleBot 명령 |
| `agent_result` | 클라이언트→서버 | 5001 | 명령 결과 |
| `client_data_prepare_request` | 서버→클라이언트 | 5002 | 파일 목록 요청 |
| `client_data_prepare_response` | 클라이언트→서버 | 5002 | 파일 목록 응답 |

### 4-3. 클라이언트 → 서버 (v0.6 신규, 포트 4003)

| 메시지 타입 | 방향 | 포트 | 설명 |
|------------|------|------|------|
| `mapping_complete_notification` | **클라이언트→서버** | **4003** | 맵핑 완료 알림 |
| `mapping_complete_ack` | 서버→클라이언트 | 4003 | 알림 수신 확인 |

---

## 5. 공통 헤더

모든 JSON 메시지에 포함해야 하는 공통 필드:

```json
{
  "v": 6,
  "mt": "<message_type>",
  "msg_id": "MSG_20260624_ACTION_ROBOT_000001",
  "ref": null,
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.6"
}
```

| 필드 | 설명 |
|------|------|
| `v` | 버전 (6) |
| `mt` | 메시지 타입 |
| `msg_id` | 이 메시지의 고유 ID |
| `ref` | 응답이면 원본 msg_id, 요청이면 null 또는 생략 |
| `ts` | ISO 8601 타임스탬프 |
| `source` | 발신자: `control_ui` \| `fleet_server` \| `robot_command_client` |
| `dest` | 수신자: 위와 동일 |
| `schema` | `fleet_json_v0.6` |

---

## 6. 로봇 ID 규칙

```
제어 UI가 쓰는 이름 : tb1
서버→클라이언트 wire robot_id : "14"
ROS_DOMAIN_ID : 14
ROS namespace : /tb1
cmd_vel topic : /tb1/cmd_vel
```

제어 UI는 명령의 `targets` 필드에 `"tb1"` 또는 `"14"` 모두 사용 가능합니다.
서버가 클라이언트로 보내는 `server_command.command.robot_id`는 항상 `"14"`입니다.

---

## 7. 제어 UI → 서버 명령 기본 구조

```json
{
  "v": 6,
  "mt": "control_command_request",
  "msg_id": "MSG_MOVE_FORWARD_TB1_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.6",
  "command": {
    "command_id": "CMD_MOVE_FORWARD_TB1_000001",
    "command_revision": 0,
    "action": "<action_name>",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": {},
    "timeout_sec": 5.0
  }
}
```

| 필드 | 필수 | 설명 |
|------|------|------|
| `command.action` | ✅ | 수행할 명령 이름 |
| `command.target_scope` | ✅ | `"single"` / `"multi"` / `"all"` |
| `command.targets` | ✅ | 로봇 이름 배열 (`["tb1"]` 또는 `["all"]`) |
| `command.params` | - | 명령별 파라미터 |
| `command.timeout_sec` | - | 서버 대기 시간 (초) |

---

## 8. 서버 → 제어 응답 기본 구조

```json
{
  "v": 6,
  "mt": "operator_response",
  "msg_id": "MSG_RESPONSE_...",
  "ref": "MSG_MOVE_FORWARD_TB1_000001",
  "ts": "2026-06-24T12:00:01+09:00",
  "source": "fleet_server",
  "dest": "control_ui",
  "schema": "fleet_json_v0.6",
  "ok": true,
  "code": "R_DONE",
  "message": "move_forward 완료",
  "command": {
    "command_id": "CMD_MOVE_FORWARD_TB1_000001",
    "action": "move_forward"
  },
  "results": {
    "tb1": {
      "ok": true,
      "code": "R_DONE",
      "operating_mode": "MANUAL",
      "robot_state": "IDLE",
      "job_state": "DONE"
    }
  },
  "err": [],
  "ui_hint": {
    "summary": "move_forward 완료",
    "severity": "info",
    "highlight_robots": ["tb1"]
  }
}
```

---

## 9. operating_mode 상태 전이

```
STARTUP    → MANUAL      (부팅 완료)
MANUAL     → MAPPING     (start_mapping 성공)
MANUAL     → NAVIGATION  (nav_goal 성공, 지도 있을 때)
MAPPING    → MANUAL      (stop_mapping 성공)
NAVIGATION → MANUAL      (nav_cancel 또는 목표 도달)
ANY        → PAUSED      (pause_robot / pause_all)
PAUSED     → (이전 모드)  (resume_robot / resume_all)
ANY        → EMERGENCY   (emergency_stop)
EMERGENCY  → MANUAL      (clear_emergency 후)
```

### 모드별 허용 action

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
| map_list / map_image_select / status_request / ping 등 | ANY |

---

## 10. Action 전체 명세

### 10-1. 이동 명령 (허용 모드: MANUAL, MAPPING)

#### move_forward

```json
{
  "action": "move_forward",
  "target_scope": "single",
  "targets": ["tb1"],
  "params": { "lx": 0.05, "dur": 2.0, "hz": 10, "stop": true }
}
```

| 파라미터 | 기본값 | 최대값 | 설명 |
|---------|--------|--------|------|
| `lx` | 0.05 | 0.1 | 선속도 m/s |
| `dur` | 2.0 | 5.0 | 지속 시간 초 |
| `hz` | 10 | 50 | publish 주기 |
| `stop` | true | - | 완료 후 정지 전송 여부 |

성공: `ok=true, code=R_DONE`

#### move_backward
`lx`에 서버가 자동으로 음수 부호 적용.

#### turn_left
`az` (각속도 rad/s, 양수). 서버가 양수 유지.

#### turn_right
`az` 서버가 음수로 변환.

#### custom_move
```json
{ "params": { "lx": 0.03, "az": 0.2, "dur": 3.0, "hz": 10, "stop": true } }
```
lx, az 모두 제어가 직접 지정. 서버가 부호 변경하지 않음.

---

### 10-2. 정지 명령 (허용 모드: ANY)

#### robot_stop
```json
{ "action": "robot_stop", "target_scope": "single", "targets": ["tb1"] }
```
성공: `code=R_STOPPED`

#### all_stop
```json
{ "action": "all_stop", "target_scope": "all", "targets": ["all"] }
```
서버가 각 로봇에 `op=robot_stop` fanout.

#### emergency_stop
```json
{ "action": "emergency_stop", "target_scope": "all", "targets": ["all"] }
```
이후 이동/맵핑/네비 명령은 `E_SYSTEM_EMERGENCY`로 서버 거부.

---

### 10-3. 맵핑 명령

#### start_mapping (허용 모드: MANUAL, AUTO, SERVICE)

```json
{
  "action": "start_mapping",
  "target_scope": "single",
  "targets": ["tb1"],
  "params": {
    "mode": "mapping",
    "mapping_engine": "cartographer",
    "explore": true
  }
}
```

| 파라미터 | 설명 |
|---------|------|
| `mode` | `"mapping"` (필수) |
| `mapping_engine` | `"cartographer"` 권장 |
| `explore` / `auto_explore` | `true`이면 SLAM 시작 후 자율 탐색. 없으면 수동 탐색. |
| `map_name` | 선택, 저장 시 사용할 이름 |

클라이언트 성공 응답:
```json
{
  "ok": true, "code": "R_STARTED",
  "state": { "operating_mode": "MAPPING", "robot_state": "MAPPING", "job_state": "RUNNING" }
}
```

#### stop_mapping (허용 모드: MAPPING, PAUSED)

```json
{ "action": "stop_mapping", "target_scope": "single", "targets": ["tb1"] }
```

클라이언트 성공 응답:
```json
{
  "ok": true, "code": "R_DONE",
  "state": { "operating_mode": "MANUAL", "robot_state": "IDLE", "job_state": "DONE" }
}
```

#### save_map (허용 모드: MAPPING, SERVICE)

```json
{
  "action": "save_map",
  "target_scope": "single",
  "targets": ["tb1"],
  "params": { "map_name": "lab_map_01" }
}
```

> **주의:** SLAM이 실행 중인 상태에서만 사용 가능. stop_mapping 이전에 실행해야 합니다.

클라이언트 성공 응답:
```json
{
  "ok": true, "code": "R_MAP_LOCAL_SAVED",
  "state": { "operating_mode": "MAPPING" }
}
```
→ save_map 후에도 operating_mode는 MAPPING 유지.

#### rsync_map (허용 모드: MAPPING, SERVICE)

운영자가 명시적으로 서버에 파일 pull을 요청하는 구 방식. v0.6에서는 `mapping_complete_notification` (자동 방식)으로 대체 권장.

```json
{ "action": "rsync_map", "target_scope": "single", "targets": ["tb1"] }
```

#### 맵핑 흐름 (운영자 수동 방식)

```
제어: start_mapping → 서버: R_STARTED         (MAPPING 모드 진입)
제어: move_forward 등 → 수동 탐색             (MAPPING 유지)
      (또는 explore:true이면 자율 탐색)
제어: save_map     → 서버: R_MAP_LOCAL_SAVED  (클라이언트 로컬 저장, MAPPING 유지)
제어: rsync_map    → 서버: 파일 pull 완료      (MAPPING 유지)
제어: stop_mapping → 서버: R_DONE             (MANUAL 복귀)
```

#### 맵핑 흐름 (v0.6 자동 방식 — 권장)

```
제어: start_mapping (explore:true) → SLAM + 자율 탐색 시작
클라이언트: 완료 조건 감지 → SLAM 종료 → 맵 로컬 저장
클라이언트: mapping_complete_notification → 서버:4003
서버: 백그라운드 SSH rsync로 맵 pull → data/maps/ 저장
제어: map_list → 목록 확인
제어: map_image_select → 원하는 맵 이미지 수신
```

---

### 10-4. 맵 디렉토리 이름 규칙 (v0.6 신규)

```
YYYYMMDD_HHMMSS_turtlebotName_saveMethod_saveNumber
```

| 필드 | 설명 | 예시 |
|------|------|------|
| YYYYMMDD | 맵핑 **시작** 날짜 | 20260624 |
| HHMMSS | 맵핑 **시작** 시간 | 164951 |
| turtlebotName | 터틀봇 별칭 | tb1 / tb2 / tb3 |
| saveMethod | 저장 방식 | autoSave / stop / emergency |
| saveNumber | 클라이언트 누적 맵핑 횟수 | 1, 2, 3, ... |

예시: `20260624_164951_tb1_autoSave_1`
```
data/maps/20260624_164951_tb1_autoSave_1/
├─ map.pgm
└─ map.yaml
```

| saveMethod 값 | 설명 |
|--------------|------|
| `autoSave` | 클라이언트가 완료 조건 판단하여 자동 저장 |
| `stop` | 운영자 stop_mapping 명령 후 저장 |
| `emergency` | 긴급정지 후 저장 |

---

### 10-5. 맵핑 완료 통지 (v0.6 신규, 클라이언트 → 서버, 포트 4003)

SLAM 완료 후 클라이언트가 서버 IP:4003에 TCP 연결하여 전송.

**클라이언트 → 서버:**

```json
{
  "v": 6,
  "mt": "mapping_complete_notification",
  "msg_id": "MSG_MAPPING_COMPLETE_TB1_001",
  "ts": "2026-06-24T16:52:30+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.6",
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
  "v": 6,
  "mt": "mapping_complete_ack",
  "ref": "MSG_MAPPING_COMPLETE_TB1_001",
  "ok": true,
  "code": "R_ACCEPTED",
  "message": "mapping complete notification received for 20260624_164951_tb1_autoSave_1, sync will begin"
}
```

| notification 필드 | 필수 | 설명 |
|------------------|------|------|
| `robot_alias` | 권장 | tb1 / tb2 / tb3 |
| `robot_id` | 선택 | "14" 등 wire robot_id |
| `map_dir_name` | **필수** | 클라이언트가 생성한 디렉토리 이름 (이름 규칙 준수) |
| `save_method` | 권장 | autoSave / stop / emergency |
| `map_start_ts` | 권장 | 맵핑 시작 시각 ISO 8601 |
| `client_map_dir` | **필수** | 클라이언트에서 해당 디렉토리의 절대 경로 |
| `files` | 선택 | 저장된 파일 목록 |

---

### 10-6. 맵 목록 조회 — 포트 4001 (control_command_request) (v0.6 강화, 허용 모드: ANY)

```json
{
  "v": 6,
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

`params.robot` 생략 시 전체 로봇의 맵 반환.

**서버 응답:**

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

---

### 10-7. 맵 이미지 선택 및 전송 — 포트 4001 (control_command_request) (v0.6 신규, 허용 모드: ANY)

```json
{
  "v": 6,
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

또는 이름으로 직접 선택:

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

서버는 해당 디렉토리를 SSH rsync로 제어 컴퓨터에 전송:
```
제어 컴퓨터: /home/ubuntu/turtlebot_control/data/maps/20260624_164951_tb1_autoSave_1/
├─ map.pgm
└─ map.yaml
```

성공 응답: `ok=true, code=R_FILE_SYNC_REPORTED`

---

### 10-8. 네비게이션

#### nav_goal (허용 모드: AUTO, MANUAL)

```json
{
  "action": "nav_goal",
  "target_scope": "single",
  "targets": ["tb1"],
  "params": { "x": 1.5, "y": 0.8, "theta": 0.0 }
}
```

성공: `code=R_STARTED, state.operating_mode=NAVIGATION`

#### nav_cancel (허용 모드: NAVIGATION, PAUSED)

```json
{ "action": "nav_cancel", "target_scope": "single", "targets": ["tb1"] }
```

성공: `code=R_CANCELED, state.operating_mode=MANUAL`

---

### 10-9. 상태 조회 (허용 모드: ANY)

| action | 성공 코드 |
|--------|----------|
| `status_request` | `R_STATUS` |
| `robot_state_request` | `R_STATUS` |
| `mapping_status` | `R_STATUS` |
| `map_status` | `R_STATUS` |
| `map_list` | `R_STATUS` |
| `nav_status` | `R_STATUS` |
| `ping` | `R_PONG` |

---

### 10-10. 일시정지 / 재개

| action | target_scope | 허용 모드 | 성공 코드 |
|--------|-------------|----------|----------|
| `pause_robot` | single | AUTO, MANUAL, MAPPING, NAVIGATION | `R_PAUSED` |
| `pause_all` | all | AUTO, MANUAL, MAPPING, NAVIGATION | `R_PAUSED` |
| `resume_robot` | single | PAUSED | `R_RESUMED` |
| `resume_all` | all | PAUSED | `R_RESUMED` |

### 10-11. 긴급 해제 및 초기화

```json
{ "action": "clear_emergency", "target_scope": "all", "targets": ["all"] }
{ "action": "reset_all_jobs", "target_scope": "all", "targets": ["all"] }
```

---

## 11. server_command 전체 구조 (서버→클라이언트 5001)

```json
{
  "v": 6,
  "mt": "server_command",
  "msg_id": "MSG_SERVER_CMD_TB1_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "fleet_server",
  "dest": "robot_command_client",
  "schema": "fleet_json_v0.6",
  "command": {
    "command_id": "CMD_START_MAPPING_TB1_000001",
    "parent_command_id": null,
    "group_id": null,
    "job_id": "JOB_START_MAPPING_TB1_000001",
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
    "params": { "mode": "mapping", "explore": true },
    "timeout_sec": 40.0
  }
}
```

---

## 12. agent_result 전체 구조 (클라이언트→서버 5001)

```json
{
  "v": 6,
  "mt": "agent_result",
  "msg_id": "MSG_AGENT_RESULT_TB1_000001",
  "ref": "MSG_SERVER_CMD_TB1_000001",
  "ts": "2026-06-24T12:00:01+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.6",
  "robot_id": "14",
  "command": {
    "command_id": "CMD_START_MAPPING_TB1_000001",
    "job_id": "JOB_START_MAPPING_TB1_000001",
    "op": "start_mapping"
  },
  "ok": true,
  "code": "R_STARTED",
  "message": "SLAM started",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MAPPING",
    "robot_state": "MAPPING",
    "job_state": "RUNNING",
    "accept_state": "ACCEPTING",
    "ui_mode": "BUSY_QUEUEABLE"
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

## 13. 상태 필드 값 정의

### operating_mode

| 값 | 의미 |
|----|------|
| `STARTUP` | 부팅 중 |
| `MANUAL` | 수동 조작 (기본) |
| `MAPPING` | SLAM 맵핑 중 |
| `NAVIGATION` | 자율 네비게이션 중 |
| `AUTO` | 자율 모드 대기 |
| `PAUSED` | 일시정지 |
| `SERVICE` | 정비 모드 |
| `EMERGENCY` | 긴급 정지 |
| `SHUTDOWN` | 종료 중 |
| `ERROR` | 오류 상태 |

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

## 14. 결과 코드 전체 목록

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
| `R_ACCEPTED` | 알림/요청 수락 (mapping_complete_ack 등) |
| `R_MAP_LOCAL_SAVED` | 맵 클라이언트 로컬 저장 완료 |
| `R_FILE_SYNC_REPORTED` | 파일 동기화 보고 완료 |
| `R_TRANSFER_DONE` | 파일 전송 완료 |
| `R_CLIENT_ALIVE` | 클라이언트 헬스 응답 |

### 오류 코드 (E_)

| 코드 | 의미 |
|------|------|
| `E_UNKNOWN_ACTION` | 지원하지 않는 op |
| `E_ROBOT_BUSY` | 로봇이 다른 작업 중 |
| `E_MODE_BLOCKED` | 현재 operating_mode에서 불허 |
| `E_SYSTEM_EMERGENCY` | 서버 EMERGENCY 상태 |
| `E_TIMEOUT` | 응답 시간 초과 |
| `E_AGENT_DISCONNECTED` | 클라이언트 연결 없음 |
| `E_TARGET_INVALID` | 잘못된 robot_id / target |
| `E_STATE_MISMATCH` | ref/robot_id/command_id/op 불일치 |
| `E_MAPPING_CONDITION` | 맵핑 조건 미충족 |
| `E_NAV_CONDITION` | 네비 조건 미충족 |
| `E_FILE_SYNC_FAILED` | 파일 동기화 실패 |
| `E_BAD_REQUEST` | JSON 구조 오류 |
| `E_BAD_JSON` | JSON 파싱 불가 |
| `E_DUPLICATE_COMMAND` | 중복 command_id |
| `E_INTERNAL_ERROR` | 서버/클라이언트 내부 오류 |

---

## 15. v0.5.x → v0.6 마이그레이션 가이드

| 항목 | v0.5.x | v0.6 |
|------|--------|------|
| 버전 필드 | `"v": 5` | `"v": 6` |
| 스키마 필드 | `"schema": "fleet_json_v0.5.1"` | `"schema": "fleet_json_v0.6"` |
| 포트 4003 | 없음 | 클라이언트→서버 알림 |
| `map_list` 응답 | 단순 R_STATUS | 메타데이터 포함 전체 목록 |
| `map_list` 사용 포트 | 4002 (`control_data_request`, data_type=map) | **4001** (`control_command_request`, action=map_list) |
| `map_image_select` | 없음 | **신규 (포트 4001**, index/dir_name으로 선택) |
| 맵핑 완료 알림 | 없음 (수동 rsync_map) | `mapping_complete_notification` |
| 맵 디렉토리 이름 | 미정의 | `YYYYMMDD_HHMMSS_robot_method_N` |
| 포트 4002 용도 | 이미지/맵 요청 | 카메라 이미지/로그 요청 전용 (map 명령 제외) |

**전환기 중 서버 동작:**
- 서버 → 제어/클라이언트: 항상 v=6 전송
- 서버 ← 제어/클라이언트: v=5 또는 v=6 모두 수락
- 제어/클라이언트는 v5 또는 v6 중 하나로 보내도 동작하나, **v6 전환 권장**

---

## 16. 절대 규칙 요약

```
1. JSON 한 줄 (\n 종료). Pretty JSON 절대 금지.
2. 요청 수신 후 반드시 응답. 무응답 금지.
3. 실패해도 ok=false JSON으로 응답 (연결 그냥 끊으면 안 됨).
4. code는 R_* 또는 E_* 만 사용 ("OK", "DONE", "ERROR" 금지).
5. agent_result의 ref / robot_id / command_id / op 4개 매칭 필수.
6. start_mapping 성공 시 operating_mode=MAPPING 반드시 보고.
7. save_map / rsync_map은 stop_mapping 이전에 실행. (MAPPING 모드 필요)
8. explore:true는 제어 UI가 명시적으로 params에 추가, 서버는 수정 없이 전달.
9. 맵 디렉토리 이름은 YYYYMMDD_HHMMSS_robot_saveMethod_N 규칙 준수.
   (서버가 파싱 불가하면 map_list에 포함되지 않음)
10. mapping_complete_notification의 client_map_dir / map_dir_name은 필수 필드.
```
