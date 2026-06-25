# Fleet JSON v0.6 팀 공유 프롬프트

> **역할:** 이 프롬프트를 Claude/GPT에게 먼저 넣어 주세요.
> 그러면 AI가 Fleet JSON v0.6 규약을 이해하고 코드 작성/검토를 도와줍니다.
> 제어 UI, 서버, 클라이언트 개발자 모두 공통 사용.
>
> **배포:** 팀원 전원에게 이 파일을 공유하세요.
> `docs/JSON_CONTRACT_V06.md` 도 함께 참고하면 더 정확합니다.

---

## 시스템 배경

```
[제어 UI (192.168.3.59)] ↔ [Fleet Server (192.168.3.61)] ↔ [Robot Command Client (192.168.3.63)] → TurtleBot3
```

- Fleet Server: Python (`fleet_server_main.py`) — 제어와 클라이언트 사이 중계
- Robot Command Client: Python (`fleet_client_main.py`) — ROS2 pub/sub 실행
- 제어 UI: 운영자 PC — JSON TCP 소켓 통신

---

## 1. 프로토콜 기본 규칙

```
- TCP + UTF-8 + NDJSON (JSON 1개 = 한 줄 + \n)
- Pretty JSON (들여쓰기) 절대 금지 — 항상 한 줄로 직렬화
- 요청 → 응답 1:1 원칙 (ok=false라도 반드시 응답)
- code 값: R_* (성공) 또는 E_* (실패) 만 사용
```

---

## 2. 버전 식별자 (모든 메시지 필수)

```json
{ "v": 6, "schema": "fleet_json_v0.6" }
```

**서버 수락:** v=5 또는 v=6 모두 수락 (전환기)
**서버 발신:** 항상 v=6 전송
**제어 / 클라이언트 발신:** v=6 전환 권장 (v=5도 현재 수락됨)

---

## 3. 포트 전체 목록

| 채널 | 방향 | 포트 | 용도 |
|------|------|------|------|
| Control Health | 제어→서버 | **4000** | 서버 생존 확인 |
| Control Command | 제어→서버 | **4001** | 터틀봇 명령 (map_list / map_image_select 포함) |
| Control Data | 제어→서버 | **4002** | 카메라 이미지/로그 요청 전용 (image_request) |
| **Client Event** | **클라이언트→서버** | **4003** | **맵핑 완료 알림** ← v0.6 신규 |
| Client Health | 서버→클라이언트 | **5000** | 클라이언트 생존 확인 |
| Client Command | 서버→클라이언트 | **5001** | TurtleBot 명령 실행 |
| Client Data | 서버→클라이언트 | **5002** | 파일 목록/경로 요청 |

> 포트 4003은 **클라이언트가 서버로 먼저 연결**합니다 (방향 주의).
>
> ⚠️ **포트 4001 vs 4002:** `map_list` 와 `map_image_select` 는 **포트 4001** (command) 사용.
> 포트 4002 는 카메라 이미지/로그 전용 — 맵 목록/맵 이미지 선택에는 사용하지 않습니다.
> 포트 5000–5002 는 서버↔클라이언트 전용 — 제어 UI 는 절대 사용하지 않습니다.

---

## 4. 로봇 ID 규칙

```
제어 UI가 쓰는 이름: tb1
server_command의 robot_id: "14"
ROS_DOMAIN_ID: 14
ROS namespace: /tb1
cmd_vel topic: /tb1/cmd_vel
```

---

## 5. 공통 헤더

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

`source` / `dest` 값: `control_ui` | `fleet_server` | `robot_command_client`

---

## 6. 메시지 타입 목록

| 메시지 타입 | 방향 | 포트 |
|------------|------|------|
| `control_health_request` | 제어→서버 | 4000 |
| `control_health_response` | 서버→제어 | 4000 |
| `control_command_request` | 제어→서버 | 4001 |
| `operator_request` | 제어→서버 (v5 호환) | 4001 |
| `operator_response` | 서버→제어 | 4001 |
| `control_data_request` | 제어→서버 | 4002 |
| `control_data_response` | 서버→제어 | 4002 |
| `mapping_complete_notification` | **클라이언트→서버** | **4003** |
| `mapping_complete_ack` | 서버→클라이언트 | 4003 |
| `client_heartbeat_request` | 서버→클라이언트 | 5000 |
| `client_heartbeat_response` | 클라이언트→서버 | 5000 |
| `server_command` | 서버→클라이언트 | 5001 |
| `agent_result` | 클라이언트→서버 | 5001 |
| `client_data_prepare_request` | 서버→클라이언트 | 5002 |
| `client_data_prepare_response` | 클라이언트→서버 | 5002 |

---

## 7. 제어 UI → 서버 명령 구조 (포트 4001)

```json
{
  "v": 6,
  "mt": "control_command_request",
  "msg_id": "MSG_START_MAPPING_TB1_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.6",
  "command": {
    "command_id": "CMD_START_MAPPING_TB1_000001",
    "command_revision": 0,
    "action": "start_mapping",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": { "mode": "mapping", "explore": true },
    "timeout_sec": 40.0
  }
}
```

---

## 8. 서버 → 제어 응답 구조

```json
{
  "v": 6,
  "mt": "operator_response",
  "ref": "MSG_START_MAPPING_TB1_000001",
  "ok": true,
  "code": "R_STARTED",
  "message": "start_mapping 시작",
  "source": "fleet_server",
  "dest": "control_ui",
  "schema": "fleet_json_v0.6",
  "results": {
    "tb1": {
      "ok": true,
      "code": "R_STARTED",
      "operating_mode": "MAPPING",
      "robot_state": "MAPPING",
      "job_state": "RUNNING"
    }
  }
}
```

---

## 9. 서버 → 클라이언트 명령 구조 (포트 5001)

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
    "job_id": "JOB_START_MAPPING_TB1_000001",
    "command_revision": 0,
    "op": "start_mapping",
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

## 10. 클라이언트 → 서버 결과 구조 (포트 5001)

```json
{
  "v": 6,
  "mt": "agent_result",
  "ref": "MSG_SERVER_CMD_TB1_000001",
  "robot_id": "14",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.6",
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

### 필수 매칭 규칙 (위반 시 서버가 E_STATE_MISMATCH 처리)
```
agent_result.ref                == server_command.msg_id
agent_result.robot_id           == server_command.command.robot_id
agent_result.command.command_id == server_command.command.command_id
agent_result.command.op         == server_command.command.op
```

---

## 11. 맵 디렉토리 이름 규칙 (v0.6 신규)

```
YYYYMMDD_HHMMSS_turtlebotName_saveMethod_saveNumber
```

- `YYYYMMDD` / `HHMMSS`: 맵핑 **시작** 시각 (저장 시각 아님)
- `saveMethod`: `autoSave` | `stop` | `emergency`
- `saveNumber`: 클라이언트가 자체 카운트하는 누적 번호

예: `20260624_164951_tb1_autoSave_1` → 내부에 `map.pgm`, `map.yaml`

---

## 12. 맵핑 완료 알림 (v0.6 신규, 포트 4003)

클라이언트가 SLAM 완료 후 서버 192.168.3.61:4003에 TCP 연결하여 전송.

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
    "robot_alias": "tb1",
    "robot_id": "14",
    "map_dir_name": "20260624_164951_tb1_autoSave_1",
    "save_method": "autoSave",
    "map_start_ts": "2026-06-24T16:49:51+09:00",
    "client_map_dir": "/home/ubuntu/turtlebot_client/data/maps/20260624_164951_tb1_autoSave_1",
    "files": ["map.pgm", "map.yaml"]
  }
}
```

**서버 ACK:**
```json
{
  "v": 6,
  "mt": "mapping_complete_ack",
  "ref": "MSG_MAPPING_COMPLETE_TB1_001",
  "ok": true,
  "code": "R_ACCEPTED",
  "message": "sync will begin"
}
```

필수 필드: `notification.map_dir_name`, `notification.client_map_dir`

---

## 13. 맵 목록 조회 (v0.6 강화)

**요청 (포트 4001):**
```json
{
  "command": {
    "action": "map_list",
    "target_scope": "all",
    "targets": ["all"],
    "params": { "robot": "tb1" }
  }
}
```

**응답:**
```json
{
  "ok": true,
  "code": "R_STATUS",
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
      }
    ],
    "map_total": 1
  }
}
```

---

## 14. 맵 이미지 선택 전송 (v0.6 신규) — 포트 4001 (control_command_request)

**요청 (포트 4001):**
```json
{
  "command": {
    "action": "map_image_select",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": { "index": 1 }
  }
}
```

또는 `"params": { "dir_name": "20260624_164951_tb1_autoSave_1" }`

성공: `ok=true, code=R_FILE_SYNC_REPORTED`
서버가 SSH rsync로 제어 컴퓨터 `control_map_receive_dir/<dir_name>/` 에 전송.

---

## 15. 맵핑 전체 흐름

### 방식 A — 자동 완료 (v0.6 권장)
```
제어: start_mapping (explore:true) → R_STARTED, MAPPING 모드
클라이언트: 자율 탐색 후 완료 감지 → 맵 저장
클라이언트: mapping_complete_notification → 서버:4003
서버: 백그라운드 rsync pull → data/maps/ 저장
제어: map_list → 목록 표시
제어: map_image_select → 맵 이미지 수신
```

### 방식 B — 수동 완료
```
제어: start_mapping → R_STARTED, MAPPING 모드
제어: move_forward 등 → 수동 탐색 (MAPPING 유지)
제어: save_map → R_MAP_LOCAL_SAVED (MAPPING 유지)
제어: rsync_map → 파일 pull
제어: stop_mapping → R_DONE, MANUAL 복귀
```

> `save_map` / `rsync_map`은 반드시 `stop_mapping` **이전**에 실행 (MAPPING 모드 필요)

---

## 16. Action 목록 (요약)

| action | 허용 operating_mode | 성공 code |
|--------|-------------------|-----------|
| move_forward / move_backward | MANUAL, MAPPING | R_DONE |
| turn_left / turn_right | MANUAL, MAPPING | R_DONE |
| custom_move | MANUAL, MAPPING | R_DONE |
| robot_stop / all_stop | ANY | R_STOPPED |
| emergency_stop | ANY | R_STOPPED |
| start_mapping | MANUAL, AUTO, SERVICE | R_STARTED |
| save_map | MAPPING, SERVICE | R_MAP_LOCAL_SAVED |
| rsync_map | MAPPING, SERVICE | R_FILE_SYNC_REPORTED |
| stop_mapping | MAPPING, PAUSED | R_DONE |
| nav_goal | AUTO, MANUAL | R_STARTED |
| nav_cancel | NAVIGATION, PAUSED | R_CANCELED |
| pause_robot / pause_all | AUTO, MANUAL, MAPPING, NAVIGATION | R_PAUSED |
| resume_robot / resume_all | PAUSED | R_RESUMED |
| clear_emergency | EMERGENCY | R_DONE |
| reset_all_jobs | EMERGENCY, SERVICE | R_DONE |
| status_request / ping | ANY | R_STATUS / R_PONG |
| map_list | ANY | R_STATUS |
| map_image_select | ANY | R_FILE_SYNC_REPORTED |

---

## 17. operating_mode 상태 전이

```
STARTUP    → MANUAL      (부팅 완료)
MANUAL     → MAPPING     (start_mapping 성공)
MANUAL     → NAVIGATION  (nav_goal, 지도 있을 때)
MAPPING    → MANUAL      (stop_mapping 성공)
NAVIGATION → MANUAL      (nav_cancel 또는 목표 도달)
ANY        → PAUSED      (pause_robot / pause_all)
PAUSED     → (이전 모드)  (resume_robot / resume_all)
ANY        → EMERGENCY   (emergency_stop)
EMERGENCY  → MANUAL      (clear_emergency)
```

---

## 18. 결과 코드 요약

### 성공 (R_)
| 코드 | 의미 |
|------|------|
| R_DONE | 명령 완료 |
| R_STARTED | 백그라운드 작업 시작 (start_mapping, nav_goal 등) |
| R_STOPPED | 정지 완료 |
| R_PAUSED / R_RESUMED / R_CANCELED | 해당 동작 완료 |
| R_STATUS | 상태 조회 |
| R_PONG | ping 응답 |
| R_ACCEPTED | 알림 수신 (mapping_complete_ack) |
| R_MAP_LOCAL_SAVED | 클라이언트 로컬 맵 저장 완료 |
| R_FILE_SYNC_REPORTED | 파일 동기화 보고 완료 |
| R_TRANSFER_DONE | 파일 전송 완료 |
| R_CLIENT_ALIVE | 헬스 응답 |

### 오류 (E_)
| 코드 | 의미 |
|------|------|
| E_UNKNOWN_ACTION | 지원하지 않는 op |
| E_ROBOT_BUSY | 로봇 다른 작업 중 |
| E_MODE_BLOCKED | 현재 모드 불허 |
| E_SYSTEM_EMERGENCY | EMERGENCY 상태 |
| E_TIMEOUT | 응답 시간 초과 |
| E_AGENT_DISCONNECTED | 클라이언트 미연결 |
| E_TARGET_INVALID | 잘못된 robot_id |
| E_STATE_MISMATCH | agent_result 필드 불일치 |
| E_FILE_SYNC_FAILED | 파일 동기화 실패 |
| E_BAD_REQUEST / E_BAD_JSON | 요청 구조/파싱 오류 |
| E_INTERNAL_ERROR | 내부 오류 |

---

## 19. 절대 규칙

```
1. JSON 한 줄 (\n 종료). Pretty JSON 절대 금지.
2. 요청 수신 후 반드시 응답. 무응답 금지.
3. 실패해도 ok=false JSON으로 응답 (연결 그냥 끊으면 안 됨).
4. code는 R_* 또는 E_* 만 사용 ("OK", "DONE", "ERROR" 금지).
5. agent_result의 ref / robot_id / command_id / op 4개 매칭 필수.
6. start_mapping 성공 시 operating_mode=MAPPING 반드시 보고.
7. save_map / rsync_map은 stop_mapping 이전에 실행 (MAPPING 모드 필요).
8. explore:true는 제어 UI가 params에 추가, 서버는 수정 없이 클라이언트로 전달.
9. 맵 디렉토리 이름은 YYYYMMDD_HHMMSS_robot_saveMethod_N 규칙 준수.
   (서버가 파싱 불가하면 map_list에 포함되지 않음)
10. mapping_complete_notification의 client_map_dir / map_dir_name은 필수 필드.
11. 포트 4003 연결 방향: 클라이언트 → 서버 (서버가 listen, 클라이언트가 connect).
```
