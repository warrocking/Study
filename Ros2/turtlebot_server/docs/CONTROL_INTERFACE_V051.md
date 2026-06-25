# Control UI v0.5.1 인터페이스 가이드

제어 UI 담당자가 Fleet Server에 명령을 보내고 응답을 해석하는 방법입니다.

---

## 1. 네트워크 기준

```
프로토콜: TCP + UTF-8 + NDJSON
JSON 1개 = 한 줄 (\n 종료). Pretty JSON 금지.
제어 UI가 서버에 접속 (제어가 connect, 서버가 listen)
```

| 포트 | 용도 | 보내는 mt | 받는 mt |
|------|------|----------|---------|
| 4000 | Health | `control_health_request` | `control_health_response` |
| 4001 | Command | `operator_request` 또는 `control_command_request` | `operator_response` |
| 4002 | Data | `control_data_request` | `control_data_response` |

서버 IP: `192.168.3.61`

---

## 2. Health 체크 (포트 4000)

제어 UI는 주기적으로 서버 상태를 확인합니다.

### 요청

```json
{
  "v": 5, "mt": "control_health_request",
  "msg_id": "MSG_20260624_CTRL_HB_000001",
  "ref": null,
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "control_ui", "dest": "fleet_server",
  "schema": "fleet_json_v0.5",
  "request": {
    "include_server_time": true,
    "include_client_state": true,
    "include_robot_states": true
  }
}
```

### 응답 (정상)

```json
{
  "v": 5, "mt": "control_health_response",
  "msg_id": "MSG_...", "ref": "MSG_20260624_CTRL_HB_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "fleet_server", "dest": "control_ui",
  "schema": "fleet_json_v0.5",
  "ok": true, "code": "R_HEALTH_OK",
  "message": "fleet_server is alive",
  "server": {
    "server_time": "2026-06-24T12:00:00+09:00",
    "global_state": "NORMAL",
    "uptime_sec": 3600.0,
    "public_ip": "192.168.3.61",
    "control_health_port": 4000,
    "control_command_port": 4001,
    "control_data_port": 4002
  },
  "client": {
    "id": "robot_command_client",
    "ip": "192.168.3.63",
    "connection_state": "CONNECTED",
    "code": "R_CLIENT_ALIVE"
  },
  "robots": {
    "tb1": {
      "enabled": true,
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

**`server.global_state` 값 처리:**

| 값 | UI 처리 |
|----|---------|
| `"NORMAL"` | 정상, 모든 버튼 활성화 |
| `"EMERGENCY"` | 비상 팝업 표시, 이동/맵핑/네비 버튼 비활성화 |

---

## 3. 명령 전송 (포트 4001)

모든 명령 요청의 공통 구조:

```json
{
  "v": 5, "mt": "control_command_request",
  "msg_id": "MSG_20260624_CTRL_CMD_000001",
  "ref": null,
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "control_ui", "dest": "fleet_server",
  "schema": "fleet_json_v0.5",
  "command": {
    "action": "<action명>",
    "targets": ["tb1"],
    "target_scope": "single",
    "params": { }
  }
}
```

`targets`: 로봇 목록. 전체 대상은 `["all"]`이고 `target_scope`를 `"all"`로 설정.  
`target_scope`: `"single"` | `"multi"` | `"all"`

---

## 4. 명령별 요청 예시

### 4-1. 이동 명령

#### 전진

```json
{
  "command": {
    "action": "move_forward", "targets": ["tb1"], "target_scope": "single",
    "params": { "lx": 0.05, "dur": 2.0, "hz": 10, "stop": true }
  }
}
```

#### 후진

```json
{ "command": { "action": "move_backward", "targets": ["tb1"], "target_scope": "single",
    "params": { "lx": 0.05, "dur": 2.0, "hz": 10, "stop": true } } }
```

#### 좌회전

```json
{ "command": { "action": "turn_left", "targets": ["tb1"], "target_scope": "single",
    "params": { "az": 0.5, "dur": 2.0, "hz": 10, "stop": true } } }
```

#### 우회전

```json
{ "command": { "action": "turn_right", "targets": ["tb1"], "target_scope": "single",
    "params": { "az": 0.5, "dur": 2.0, "hz": 10, "stop": true } } }
```

#### 직접 속도 지정 (custom_move)

```json
{ "command": { "action": "custom_move", "targets": ["tb1"], "target_scope": "single",
    "params": { "lx": 0.03, "az": 0.2, "dur": 3.0, "hz": 10, "stop": true } } }
```

| 파라미터 | 기본값 | 최대 | 설명 |
|---------|--------|------|------|
| `lx` | 0.05 | 0.1 | 선속도 m/s |
| `az` | 0.5 | 1.0 | 각속도 rad/s |
| `dur` | 2.0 | 5.0 | 지속 시간 초 |
| `hz` | 10 | 50 | 명령 주기 |
| `stop` | true | - | 완료 후 정지 여부 |

---

### 4-2. 정지 명령

#### 단일 로봇 정지

```json
{ "command": { "action": "robot_stop", "targets": ["tb1"], "target_scope": "single" } }
```

#### 전체 로봇 정지

```json
{ "command": { "action": "all_stop", "targets": ["all"], "target_scope": "all" } }
```

#### 긴급 정지 (최우선)

```json
{ "command": { "action": "emergency_stop", "targets": ["all"], "target_scope": "all" } }
```

긴급 정지 후 서버 `global_state = "EMERGENCY"`. 이후 이동/맵핑/네비 명령 불가.

---

### 4-3. 맵핑

#### 맵핑 시작 (수동 탐색)

```json
{
  "command": {
    "action": "start_mapping", "targets": ["tb1"], "target_scope": "single",
    "params": { "mode": "mapping" }
  }
}
```

#### 맵핑 시작 (자동 탐색 포함)

```json
{
  "command": {
    "action": "start_mapping", "targets": ["tb1"], "target_scope": "single",
    "params": { "mode": "mapping", "explore": true }
  }
}
```

- `explore: true` 없으면 SLAM만 시작 — 수동으로 move_forward 등을 써서 직접 탐색
- `explore: true` 있으면 로봇이 자동으로 미탐색 영역을 탐색하며 맵 생성

#### 맵핑 중단

```json
{ "command": { "action": "stop_mapping", "targets": ["tb1"], "target_scope": "single" } }
```

허용 모드: `MAPPING` (맵핑 중이어야 함)

#### 맵 저장 (클라이언트 로컬)

```json
{
  "command": {
    "action": "save_map", "targets": ["tb1"], "target_scope": "single",
    "params": { "map_name": "lab_map_01" }
  }
}
```

허용 모드: `MAPPING`

#### 맵 파일 서버로 가져오기

```json
{ "command": { "action": "rsync_map", "targets": ["tb1"], "target_scope": "single" } }
```

허용 모드: `MAPPING`  
완료 후 서버 `data/map/incoming/` 에 맵 파일 저장됨.

#### 맵핑 권장 순서

```
1. start_mapping (explore 여부 결정)
2. [수동] move_forward / turn_left 등으로 공간 탐색
   [자동] explore:true 경우 로봇이 자동 탐색
3. save_map       ← MAPPING 모드에서 실행 (stop_mapping 전에 반드시)
4. rsync_map      ← MAPPING 모드에서 실행 (서버가 맵 파일을 받아옴)
5. stop_mapping   ← SLAM 종료, MANUAL 모드 복귀
6. image_request  ← 맵 이미지를 제어 화면에 표시
```

⚠️ **save_map과 rsync_map은 반드시 stop_mapping 이전에 실행해야 합니다.**
stop_mapping 후에는 MANUAL 모드가 되어 save_map / rsync_map이 거부됩니다.

---

### 4-4. 네비게이션

#### 목표 지점 이동

```json
{
  "command": {
    "action": "nav_goal", "targets": ["tb1"], "target_scope": "single",
    "params": { "x": 1.5, "y": 0.8, "theta": 0.0 }
  }
}
```

허용 모드: `MANUAL`, `AUTO` (저장된 지도 필요)

| 파라미터 | 설명 |
|---------|------|
| `x`, `y` | 지도 좌표계 목표 위치 (m) |
| `theta` | 목표 방향 rad (0.0 = 정면) |

#### 네비게이션 취소

```json
{ "command": { "action": "nav_cancel", "targets": ["tb1"], "target_scope": "single" } }
```

허용 모드: `NAVIGATION`

---

### 4-5. 상태 조회

```json
{ "command": { "action": "status_request", "targets": ["tb1"], "target_scope": "single" } }
```

기타 조회 액션:

| action | 설명 |
|--------|------|
| `robot_state_request` | 로봇 상태 조회 |
| `mapping_status` | 맵핑 진행 상태 |
| `map_status` | 저장 맵 정보 |
| `map_list` | 저장 맵 목록 |
| `nav_status` | 네비게이션 진행 상태 |
| `ping` | 연결 확인 |

---

### 4-6. 일시정지 / 재개

```json
{ "command": { "action": "pause_robot", "targets": ["tb1"], "target_scope": "single" } }
{ "command": { "action": "resume_robot", "targets": ["tb1"], "target_scope": "single" } }
{ "command": { "action": "pause_all", "targets": ["all"], "target_scope": "all" } }
{ "command": { "action": "resume_all", "targets": ["all"], "target_scope": "all" } }
```

---

### 4-7. 긴급 해제

```json
{ "command": { "action": "clear_emergency", "targets": ["all"], "target_scope": "all" } }
```

허용 모드: `EMERGENCY`. 성공 후 `global_state = "NORMAL"` 복귀.

---

## 5. operator_response 해석

모든 명령에 대한 응답 구조:

```json
{
  "v": 5, "mt": "operator_response",
  "ref": "<요청 msg_id>",
  "ok": true,
  "code": "R_DONE",
  "message": "start_mapping command completed",
  "command": {
    "action": "start_mapping",
    "resolved_targets": ["tb1"]
  },
  "system": {
    "global_state": "NORMAL"
  },
  "results": {
    "tb1": {
      "ok": true,
      "code": "R_STARTED",
      "connection_state": "CONNECTED",
      "operating_mode": "MAPPING",
      "robot_state": "MAPPING",
      "job_state": "RUNNING",
      "accept_state": "ACCEPTING",
      "ui_mode": "BUSY_QUEUEABLE",
      "message": "tb1 start_mapping 시작됨"
    }
  },
  "err": [],
  "ui_hint": {
    "summary": "start_mapping command completed",
    "severity": "info",
    "highlight_robots": ["tb1"],
    "disable_buttons": [],
    "enable_buttons": ["status_request"]
  }
}
```

### 핵심 필드

| 필드 | 설명 |
|------|------|
| `ok` | 전체 성공 여부 |
| `code` | 전체 결과 코드 |
| `system.global_state` | 서버 전체 상태 (`NORMAL` / `EMERGENCY`) |
| `results.tb1.operating_mode` | 명령 후 로봇 모드 |
| `results.tb1.ok` | 해당 로봇 명령 성공 여부 |
| `ui_hint.disable_buttons` | UI에서 비활성화할 버튼 목록 |
| `ui_hint.enable_buttons` | UI에서 활성화할 버튼 목록 |

### 오류 응답 예시 (맵핑 중 이동 불가)

```json
{
  "ok": false,
  "code": "E_MODE_BLOCKED",
  "message": "move_forward is blocked by operating_mode",
  "results": {
    "tb1": { "ok": false, "code": "E_MODE_BLOCKED", "operating_mode": "NAVIGATION" }
  },
  "ui_hint": {
    "severity": "error",
    "disable_buttons": ["start_mapping", "nav_goal"]
  }
}
```

---

## 6. 이미지 요청 (포트 4002)

맵 이미지를 제어 PC로 받아오는 방법:

```json
{
  "v": 5, "mt": "control_data_request",
  "msg_id": "MSG_...", "ref": null,
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "control_ui", "dest": "fleet_server",
  "schema": "fleet_json_v0.5",
  "request": {
    "data_type": "image",
    "target": "tb1"
  }
}
```

또는 4001 포트 command로도 가능:

```json
{ "command": { "action": "image_request", "targets": ["tb1"], "target_scope": "single" } }
```

성공 시 서버가 rsync로 이미지를 제어 PC `/home/ubuntu/openCV/cache/images`에 push.

---

## 7. UI 상태 표시 가이드

### operating_mode → UI 표시

| operating_mode | 표시 |
|---------------|------|
| `MANUAL` | 수동 조작 모드 |
| `MAPPING` | 맵핑 중 |
| `NAVIGATION` | 자율 이동 중 |
| `PAUSED` | 일시정지 |
| `EMERGENCY` | 긴급 정지 |
| `DISCONNECTED` | 오프라인 |

### global_state → UI 처리

| global_state | 처리 |
|-------------|------|
| `NORMAL` | 정상 운영 |
| `EMERGENCY` | 🚨 비상 팝업 표시, 이동/맵핑/네비 버튼 비활성화, clear_emergency 버튼만 활성화 |

### 버튼 활성화 기준

| 상태 | 활성 버튼 |
|------|----------|
| MANUAL | 이동, start_mapping, nav_goal, all_stop |
| MAPPING | 이동(수동 탐색 시), stop_mapping, save_map, rsync_map, all_stop |
| NAVIGATION | nav_cancel, all_stop |
| PAUSED | resume_robot, all_stop |
| EMERGENCY | clear_emergency, emergency_stop만 허용 |

---

## 8. 결과 코드 해석

### 성공 코드 (ok=true)

| 코드 | 의미 | 대표 상황 |
|------|------|----------|
| `R_DONE` | 완료 | 이동, stop_mapping |
| `R_STARTED` | 시작됨 | start_mapping, nav_goal |
| `R_STOPPED` | 정지됨 | robot_stop, emergency_stop |
| `R_PAUSED` | 일시정지됨 | pause_robot |
| `R_RESUMED` | 재개됨 | resume_robot |
| `R_CANCELED` | 취소됨 | nav_cancel |
| `R_MAP_LOCAL_SAVED` | 맵 저장됨 | save_map |
| `R_TRANSFER_DONE` | 파일 전송됨 | image_request, rsync_map |

### 오류 코드 (ok=false)

| 코드 | 의미 | 대처 |
|------|------|------|
| `E_MODE_BLOCKED` | 현재 모드에서 불허 | 모드 확인 후 재시도 |
| `E_SYSTEM_EMERGENCY` | 서버 긴급 상태 | clear_emergency 후 재시도 |
| `E_ROBOT_BUSY` | 로봇이 다른 작업 중 | 완료 대기 또는 stop 후 재시도 |
| `E_AGENT_DISCONNECTED` | 클라이언트 연결 없음 | 연결 상태 확인 |
| `E_TIMEOUT` | 응답 시간 초과 | 재시도 |
| `E_UNKNOWN_ACTION` | 지원 안 하는 명령 | 클라이언트 업데이트 필요 |

---

## 9. 맵 목록 조회 및 이미지 선택

### 9-1. 맵 목록 조회 (포트 4001)

클라이언트가 맵핑을 완료하면 서버에 자동으로 백업됩니다. 제어 UI는 저장된 맵 목록을 요청합니다.

```json
{
  "v": 5,
  "mt": "control_command_request",
  "msg_id": "MSG_MAP_LIST_001",
  "ts": "2026-06-24T17:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "command": {
    "command_id": "CMD_MAP_LIST_001",
    "action": "map_list",
    "target_scope": "all",
    "targets": ["all"],
    "params": {
      "robot": "tb1"
    }
  }
}
```

`params.robot` 생략 시 전체 로봇의 맵을 반환합니다.

**응답 (operator_response):**

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

제어 UI 표시 예시 (터미널 선택 메뉴):

```
=== 저장된 맵 목록 ===
[1] 2026-06-24 16:49:51 | tb1 | autoSave | #1
[2] 2026-06-25 09:10:30 | tb1 | stop | #2
번호를 입력하세요:
```

### 9-2. 맵 이미지 선택 전송 (포트 4001)

사용자가 번호를 입력하면 해당 맵을 서버에서 제어 컴퓨터로 전송 요청합니다.

```json
{
  "v": 5,
  "mt": "control_command_request",
  "msg_id": "MSG_MAP_SELECT_001",
  "ts": "2026-06-24T17:01:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "command": {
    "command_id": "CMD_MAP_SELECT_001",
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

**응답 (ok=true인 경우):**

```json
{
  "ok": true,
  "code": "R_FILE_SYNC_REPORTED",
  "message": "map directory 20260624_164951_tb1_autoSave_1 sent to control"
}
```

서버는 해당 디렉토리를 SSH rsync로 아래 경로에 전송합니다:
```
제어 컴퓨터: /home/ubuntu/turtlebot_control/data/maps/20260624_164951_tb1_autoSave_1/
├─ map.pgm
└─ map.yaml
```

제어 UI는 응답이 `ok=true`이면 해당 경로에서 map.pgm / map.yaml을 읽어 이미지로 표시합니다.

### 9-3. 전체 맵 표시 흐름

```
1. 제어: map_list 요청 (4001)
2. 서버: 저장된 맵 목록 JSON 응답
3. 제어: 목록 표시, 사용자가 번호 선택
4. 제어: map_image_select 요청 (4001, params.index=N)
5. 서버: SSH rsync로 선택 디렉토리를 제어 컴퓨터에 전송
6. 서버: ok=true 응답
7. 제어: /home/ubuntu/turtlebot_control/data/maps/<dir_name>/ 에서 파일 로드
8. 제어: map.pgm 또는 map.yaml 기반으로 지도 이미지 표시
```
