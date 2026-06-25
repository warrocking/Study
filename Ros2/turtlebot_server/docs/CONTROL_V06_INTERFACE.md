# 제어 UI v0.6 인터페이스 가이드

> **대상:** 제어 UI (Control UI) 개발자
> **서버 IP:** 192.168.3.61 / 제어 PC IP: 192.168.3.59
>
> 이 문서는 Fleet JSON v0.6에 맞춰 제어 UI가 서버와 주고받는
> 모든 JSON 예시와 UI 흐름을 정리합니다.
> 전체 규약은 `docs/JSON_CONTRACT_V06.md` 참고.

---

## 1. 포트 구성 (제어 → 서버)

| 포트 | 용도 | 설명 |
|------|------|------|
| **4000** | Control Health | 서버 생존 확인 |
| **4001** | Control Command | 명령 전송 (이동 / 정지 / 맵핑 / **map_list / map_image_select** 포함) |
| **4002** | Control Data | 카메라 이미지/로그 요청 **전용** (image_request) |

> ⚠️ **포트 4001 vs 4002 혼동 주의:**
> `map_list` 와 `map_image_select` 는 **포트 4001** (Control Command) 을 통해 전송합니다.
> 포트 4002 는 카메라 이미지/로그 조회 전용이며, 맵 목록 조회 및 맵 이미지 선택에는 **사용하지 않습니다**.
>
> 제어 UI 는 포트 4003 을 사용하지 않습니다 (클라이언트 전용 이벤트 포트).
> 제어 UI 는 포트 5000–5002 를 사용하지 않습니다 (서버 ↔ 클라이언트 전용 포트).

---

## 2. 기본 메시지 구조

### 요청 (제어→서버, 포트 4001)

```json
{
  "v": 6,
  "mt": "control_command_request",
  "msg_id": "MSG_<ACTION>_<ROBOT>_<SEQ>",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.6",
  "command": {
    "command_id": "CMD_<ACTION>_<ROBOT>_<SEQ>",
    "command_revision": 0,
    "action": "<action_name>",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": {},
    "timeout_sec": 10.0
  }
}
```

### 응답 (서버→제어)

```json
{
  "v": 6,
  "mt": "operator_response",
  "ref": "<요청 msg_id>",
  "ok": true,
  "code": "R_DONE",
  "message": "명령 완료",
  "source": "fleet_server",
  "dest": "control_ui",
  "schema": "fleet_json_v0.6",
  "results": {
    "tb1": {
      "ok": true,
      "code": "R_DONE",
      "operating_mode": "MANUAL",
      "robot_state": "IDLE",
      "job_state": "DONE"
    }
  }
}
```

---

## 3. 헬스 확인 (포트 4000)

```json
{
  "v": 6,
  "mt": "control_health_request",
  "msg_id": "MSG_HEALTH_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.6"
}
```

**서버 응답:**

```json
{
  "v": 6,
  "mt": "control_health_response",
  "ok": true,
  "server": {
    "health_port": 4000,
    "command_port": 4001,
    "data_port": 4002,
    "client_event_port": 4003
  },
  "agents": {
    "tb1": {
      "connected": true,
      "operating_mode": "MANUAL",
      "robot_state": "IDLE"
    }
  }
}
```

---

## 4. 이동 명령

### move_forward

```json
{
  "command": {
    "action": "move_forward",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": { "lx": 0.05, "dur": 2.0, "hz": 10, "stop": true }
  }
}
```

| 파라미터 | 기본값 | 최대 | 설명 |
|---------|--------|------|------|
| lx | 0.05 | 0.1 | 선속도 m/s |
| dur | 2.0 | 5.0 | 지속 시간 초 |
| hz | 10 | 50 | publish 주기 |
| stop | true | - | 완료 후 정지 여부 |

성공: `ok=true, code=R_DONE`

### move_backward
`lx` 값 양수로 전송 (서버가 음수 변환).

### turn_left
```json
{ "params": { "az": 0.5, "dur": 1.5, "hz": 10, "stop": true } }
```
`az` 양수로 전송 (서버가 양수 유지).

### turn_right
`az` 양수로 전송 (서버가 음수 변환).

### custom_move
```json
{ "params": { "lx": 0.03, "az": 0.2, "dur": 3.0, "hz": 10, "stop": true } }
```
lx / az 부호를 제어 UI가 직접 지정. 서버 변환 없음.

---

## 5. 정지 명령

### robot_stop (단일 로봇)
```json
{
  "command": {
    "action": "robot_stop",
    "target_scope": "single",
    "targets": ["tb1"]
  }
}
```

### all_stop (전체 로봇)
```json
{
  "command": {
    "action": "all_stop",
    "target_scope": "all",
    "targets": ["all"]
  }
}
```

### emergency_stop
```json
{
  "command": {
    "action": "emergency_stop",
    "target_scope": "all",
    "targets": ["all"]
  }
}
```
이후 이동/맵핑/네비 명령은 서버가 `E_SYSTEM_EMERGENCY`로 거부.
해제: `clear_emergency`

---

## 6. 맵핑 명령

### start_mapping

```json
{
  "command": {
    "action": "start_mapping",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": {
      "mode": "mapping",
      "mapping_engine": "cartographer",
      "explore": true
    }
  }
}
```

> `explore: true` — 자율 탐색 모드. 클라이언트가 완료 후 자동으로 서버에 알림.
> `explore: false` (또는 생략) — 수동 탐색. 운영자가 직접 이동 명령 전송.

**성공 응답:**
```json
{
  "ok": true, "code": "R_STARTED",
  "results": {
    "tb1": { "operating_mode": "MAPPING", "robot_state": "MAPPING", "job_state": "RUNNING" }
  }
}
```

### save_map (MAPPING 모드에서만)

```json
{
  "command": {
    "action": "save_map",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": { "map_name": "lab_map" }
  }
}
```

성공: `code=R_MAP_LOCAL_SAVED`

### stop_mapping (MAPPING 또는 PAUSED에서만)

```json
{
  "command": {
    "action": "stop_mapping",
    "target_scope": "single",
    "targets": ["tb1"]
  }
}
```

성공: `code=R_DONE, operating_mode=MANUAL`

> **맵핑 명령 순서:**
> `start_mapping` → (이동 또는 자율 탐색) → `save_map` → `stop_mapping`
> save_map을 stop_mapping 이후에 보내면 E_MODE_BLOCKED 응답.

---

## 7. 맵 목록 조회 (포트 4001 — control_command_request)

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

`params.robot` 생략 시 전체 로봇 맵 반환.

**성공 응답:**
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

### UI 표시 예시

```
=== 저장된 맵 목록 (tb1) ===
[1] 2026-06-24 16:49:51 | tb1 | autoSave | #1
[2] 2026-06-25 09:10:30 | tb1 | stop | #2
번호를 선택하세요:
```

---

## 8. 맵 이미지 선택 및 수신 (포트 4001 — control_command_request)

맵 목록에서 번호 선택 후 해당 디렉토리를 요청합니다.

### index로 선택

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

### dir_name으로 선택 (index 없이)

```json
{
  "command": {
    "action": "map_image_select",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": { "dir_name": "20260624_164951_tb1_autoSave_1" }
  }
}
```

**성공 응답:**
```json
{
  "ok": true,
  "code": "R_FILE_SYNC_REPORTED",
  "message": "map directory synced to control: 20260624_164951_tb1_autoSave_1"
}
```

서버가 SSH rsync로 다음 경로에 파일을 전송합니다:
```
/home/ubuntu/turtlebot_control/data/maps/20260624_164951_tb1_autoSave_1/
├─ map.pgm
└─ map.yaml
```

### 파일 수신 후 UI 처리

```python
import os, subprocess

CONTROL_MAP_DIR = "/home/ubuntu/turtlebot_control/data/maps"

def show_map(dir_name: str):
    pgm_path = os.path.join(CONTROL_MAP_DIR, dir_name, "map.pgm")
    yaml_path = os.path.join(CONTROL_MAP_DIR, dir_name, "map.yaml")
    if os.path.exists(pgm_path):
        subprocess.Popen(["eog", pgm_path])  # 또는 선호하는 뷰어
```

---

## 9. 전체 맵핑 + 맵 조회 흐름

### 자동 모드 (explore:true)

```
1. 제어: start_mapping (explore:true) → 서버:4001
2. 서버: R_STARTED, operating_mode=MAPPING
3. [클라이언트 자율 탐색 중... 수동 조작 불필요]
4. [클라이언트 완료 감지 → 서버에 자동 알림]
5. [서버 백그라운드에서 맵 파일 pull]
6. 제어: map_list → 서버:4001
7. 서버: 맵 목록 + 메타데이터 응답
8. 제어: 목록 표시 → 운영자가 번호 선택
9. 제어: map_image_select (index=1) → 서버:4001
10. 서버: 해당 디렉토리 rsync push → 제어 컴퓨터
11. 제어: map.pgm 이미지 표시
```

### 수동 모드 (explore 없음)

```
1. 제어: start_mapping → R_STARTED, MAPPING
2. 제어: move_forward / turn_left 등 → 수동 탐색
3. 제어: save_map → R_MAP_LOCAL_SAVED (MAPPING 유지)
4. 제어: stop_mapping → R_DONE, MANUAL
5. [서버가 자동 rsync pull, 또는]
   제어: map_list → map_image_select
```

---

## 10. 네비게이션

### nav_goal (MANUAL 또는 AUTO 모드에서)

```json
{
  "command": {
    "action": "nav_goal",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": { "x": 1.5, "y": 0.8, "theta": 0.0 }
  }
}
```

성공: `code=R_STARTED, operating_mode=NAVIGATION`

### nav_cancel

```json
{
  "command": {
    "action": "nav_cancel",
    "target_scope": "single",
    "targets": ["tb1"]
  }
}
```

성공: `code=R_CANCELED, operating_mode=MANUAL`

---

## 11. 일시정지 / 재개

```json
{ "command": { "action": "pause_all",  "target_scope": "all",    "targets": ["all"] } }
{ "command": { "action": "resume_all", "target_scope": "all",    "targets": ["all"] } }
{ "command": { "action": "pause_robot",  "target_scope": "single", "targets": ["tb1"] } }
{ "command": { "action": "resume_robot", "target_scope": "single", "targets": ["tb1"] } }
```

---

## 12. 상태 조회

```json
{ "command": { "action": "status_request", "target_scope": "all", "targets": ["all"] } }
{ "command": { "action": "ping",           "target_scope": "all", "targets": ["all"] } }
```

ping 응답: `code=R_PONG`
status 응답: `code=R_STATUS`, results에 각 로봇 상태

---

## 13. 오류 처리 패턴

```python
response = send_command(req)
if not response.get("ok"):
    code = response.get("code", "E_UNKNOWN")
    message = response.get("message", "")
    if code == "E_MODE_BLOCKED":
        show_ui("현재 모드에서 사용 불가")
    elif code == "E_ROBOT_BUSY":
        show_ui("로봇이 다른 작업 중")
    elif code == "E_SYSTEM_EMERGENCY":
        show_ui("긴급 정지 상태 — clear_emergency 필요")
    elif code == "E_AGENT_DISCONNECTED":
        show_ui("클라이언트 연결 없음")
    elif code == "E_TIMEOUT":
        show_ui("응답 시간 초과")
    else:
        show_ui(f"오류: {code} — {message}")
```

---

## 14. 제어 UI 구현 체크리스트

- [ ] 요청 JSON: `v=6, schema=fleet_json_v0.6` 포함
- [ ] JSON 한 줄 직렬화 (`\n` 종료, 들여쓰기 없음)
- [ ] `msg_id` 고유값 생성 (타임스탬프 + 시퀀스 등)
- [ ] 응답의 `ref`가 요청 `msg_id`와 일치하는지 확인
- [ ] `ok=false` 응답에서 `code` 값으로 분기 처리
- [ ] `map_list` 응답: `status.maps[]` 배열에서 `display` 문자열 표시
- [ ] `map_image_select`: index 또는 dir_name 중 하나 필수
- [ ] 맵 수신 후 `control_map_receive_dir/<dir_name>/map.pgm` 파일 열기
- [ ] `start_mapping` 응답에서 `operating_mode=MAPPING` 확인 후 이동 버튼 활성화
- [ ] `stop_mapping` 응답에서 `operating_mode=MANUAL` 확인 후 상태 복귀 표시
- [ ] `emergency_stop` 후 이동/맵핑 버튼 비활성화 (`E_SYSTEM_EMERGENCY`)
- [ ] 헬스 응답의 `agents.tb1.connected` 로 연결 상태 표시

---

## 15. 결과 코드 빠른 참조

| 코드 | 의미 | 다음 동작 |
|------|------|---------|
| R_DONE | 완료 | 정상 |
| R_STARTED | 시작됨 (백그라운드) | 진행 중 표시 |
| R_STOPPED | 정지됨 | 정상 |
| R_PAUSED | 일시정지 | resume 버튼 활성화 |
| R_RESUMED | 재개됨 | 정상 |
| R_CANCELED | 취소됨 | 정상 |
| R_STATUS | 상태 조회 | results 파싱 |
| R_PONG | ping 응답 | 지연 시간 측정 |
| R_MAP_LOCAL_SAVED | 클라이언트 저장 완료 | stop_mapping 가능 표시 |
| R_FILE_SYNC_REPORTED | 맵 파일 전송 완료 | 맵 이미지 열기 |
| E_MODE_BLOCKED | 모드 불허 | 사용 불가 메시지 |
| E_ROBOT_BUSY | 로봇 바쁨 | 잠시 후 재시도 |
| E_SYSTEM_EMERGENCY | 긴급 정지 상태 | clear_emergency 버튼 |
| E_TIMEOUT | 타임아웃 | 재시도 |
| E_AGENT_DISCONNECTED | 클라이언트 없음 | 연결 확인 |
