# TurtleBot Fleet Server — 순서도(Flowchart) 제작 요청 프롬프트

> 이 문서를 다른 AI(ChatGPT, Claude 등)에 그대로 붙여넣으면
> 전체 시스템 순서도를 생성할 수 있습니다.
> 요청 방법 예시: "아래 명세를 바탕으로 Mermaid / PlantUML / draw.io XML 로 순서도를 만들어줘"

---

## 0. 목적

아래에 기술된 **TurtleBot Fleet 제어 시스템** 의 통신 흐름, 내부 처리 파이프라인, 상태 전이를
**상세한 순서도(Flowchart)** 로 표현해 주세요.

순서도는 다음 **7개** 를 별도로 그려주세요:

| 번호 | 제목 |
|------|------|
| ① | 전체 시스템 토폴로지 (노드 + 포트) |
| ② | 서버 수신 → 내부 처리 파이프라인 (모든 요청 공통) |
| ③ | 맵핑 전체 흐름 (start → 탐색 → 저장 → 서버 pull → 조회) |
| ④ | 이동 명령 처리 흐름 |
| ⑤ | 긴급 정지 흐름 |
| ⑥ | operating_mode 상태 전이도 |
| ⑦ | 맵 이미지 수신 흐름 (map_list → map_image_select → rsync push) |

---

## 1. 시스템 구성 — 3개 노드

```
[제어 UI]          [Fleet Server]        [Robot Command Client]      [TurtleBot3]
192.168.3.59  <→>  192.168.3.61  <→>    192.168.3.63               (ROS2, tb1)
Ubuntu PC          Ubuntu Server         Ubuntu PC (ros2_ws)         ROS_DOMAIN_ID=14
user: ubuntu       user: admin_kyj       user: ubuntu22
```

- **제어 UI (Control UI):** 운영자가 명령을 입력하는 노트북
- **Fleet Server (서버):** 모든 명령을 중계하고 상태를 관리하는 중앙 서버
- **Robot Command Client (클라이언트/게이트웨이):** ROS2 명령을 실행하는 게이트웨이 PC
- **TurtleBot3:** 실제 로봇. 클라이언트를 통해서만 제어됨

---

## 2. 포트 전체 목록

### 제어 UI ↔ Fleet Server (포트 4000-4003)

| 포트 | 채널명 | 방향 | 용도 |
|------|--------|------|------|
| **4000** | Control Health | 제어 → 서버 | 서버 생존 확인 (헬스체크) |
| **4001** | Control Command | 제어 → 서버 | 모든 로봇 명령 (이동/정지/맵핑/map_list/map_image_select 포함) |
| **4002** | Control Data | 제어 → 서버 | 카메라 이미지/로그 요청 전용 |
| **4003** | Client Event | **클라이언트 → 서버** | 맵핑 완료 알림 (방향 반대!) |

> ⚠️ 포트 4003은 다른 포트와 달리 **클라이언트가 서버에 먼저 연결**합니다.

### Fleet Server ↔ Robot Command Client (포트 5000-5002)

| 포트 | 채널명 | 방향 | 용도 |
|------|--------|------|------|
| **5000** | Client Health | 서버 → 클라이언트 | 클라이언트 생존 확인 (서버가 주기적으로 probe) |
| **5001** | Client Command | 서버 → 클라이언트 | TurtleBot 명령 전달 |
| **5002** | Client Data Control | 서버 → 클라이언트 | 파일 경로/목록 요청 (rsync_map 준비) |

> 제어 UI는 포트 5000-5002를 직접 사용하지 않습니다.

### SSH / rsync 채널

| 방향 | 용도 |
|------|------|
| 서버(192.168.3.61) → 클라이언트(192.168.3.63) | 맵 파일 rsync pull (SSH key: fleet_server_map_pull_ed25519) |
| 서버(192.168.3.61) → 제어 UI(192.168.3.59) | 맵 디렉토리 rsync push (SSH, user: ubuntu) |

---

## 3. 통신 프로토콜

```
TCP + UTF-8 + NDJSON
- JSON 1개 = 한 줄 (\n 종료)
- 연결 방식: 요청 1회 → 응답 1회 → 연결 종료
  (예외: 포트 4000/4001/4002는 persistent 연결, while True 루프로 다수 요청 처리)
- 포트 4003: 단방향 알림 1회 → ACK 1회 → 연결 종료
```

---

## 4. 메시지 타입 목록

### 제어 UI ↔ 서버

| 메시지 타입 | 방향 | 포트 |
|------------|------|------|
| `control_health_request` | 제어→서버 | 4000 |
| `control_health_response` | 서버→제어 | 4000 |
| `control_command_request` | 제어→서버 | 4001 |
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
| `mapping_complete_notification` | **클라이언트→서버** | **4003** |
| `mapping_complete_ack` | 서버→클라이언트 | 4003 |

---

## 5. 서버 내부 처리 파이프라인 (모든 명령 공통)

제어 UI로부터 `control_command_request` 수신 시 서버 내부 처리 순서:

```
수신 (포트 4001, TCP)
  │
  ▼
[1] 로그 저장: operator_requests/ 에 요청 JSON 기록
  │
  ▼
[2] 버전 감지: v=5 또는 v=6? → handle_control_request_v5()
              v=4?            → handle_operator_request_v4() 직접
  │
  ▼
[3] 채널 체크: mt가 해당 포트에서 허용되는 타입인가?
    포트 4001: operator_request 또는 control_command_request만 허용
  │
  ▼
[4] 공통 필드 검증 (validate_common_fields_v5):
    - v=5 또는 v=6인가?
    - schema가 fleet_json_v0.5 / fleet_json_v0.5.1 / fleet_json_v0.6 중 하나인가?
    - mt, msg_id, ts, source, dest 필드 존재하는가?
  │
  ▼
[5] v6→v4 형식 변환 (_adapt_control_command_request_v5_to_v4):
    - action/op 추출
    - params 추출
    - targets 배열 정규화 (tb1 → ["tb1"])
    - target_scope 결정 (single/multi/all)
    - command_id 생성 또는 그대로 사용
  │
  ▼
[6] 액션 검증 (is_known_action):
    - FLEET_ACTIONS 집합에 있는가?
    - 없으면 E_UNKNOWN_ACTION 즉시 반환
  │
  ▼
[7] 인증 검증 (validate_auth):
    - require_auth=false이면 건너뜀 (현재 비활성화)
  │
  ▼
[8] 정책 조회 (get_action_policy):
    - action_policy.json에서 해당 액션의 정책 로드
    - 없으면 E_UNKNOWN_ACTION
  │
  ▼
[9] target_scope 검증:
    - 정책의 target_scope_allowed에 포함되는가?
  │
  ▼
[10] 타겟 해석 (_resolve_targets_v4):
    - "tb1", "14" 모두 tb1으로 정규화
    - "all" → 활성화된 전체 로봇 목록
    - 모르는 이름 → E_TARGET_INVALID
  │
  ▼
[11] 모드 체크 (_check_policy_modes_v4):
    - global_state == EMERGENCY이면 일부 액션만 허용
    - 로봇의 현재 operating_mode가 정책 allowed_operating_modes에 있는가?
    - 없으면 E_MODE_BLOCKED
  │
  ▼
[12] 안전 체크 (_check_server_safety):
    - 이동 액션(MOVE_ACTIONS)이면 OpenCV 이벤트 파일 확인
    - 장애물 감지 이벤트가 있으면 E_SYSTEM_EMERGENCY
  │
  ▼
[13] 중복 command_id 체크 (seen_command_ids):
    - 이미 처리한 command_id → E_DUPLICATE_COMMAND
    - 처음이면 seen_command_ids에 추가
  │
  ▼
[14] 서버 직접 처리 액션 분기 (클라이언트 전달 없음):
    - ping → R_PONG
    - status_request / robot_state_request / mapping_status / map_status / nav_status → R_STATUS
    - map_list → _handle_map_list_v5() → 서버 maps 디렉토리 스캔 → R_STATUS
    - map_image_select → _handle_map_image_select_v5() → rsync push to 제어 UI
    - image_request → _handle_image_request_v4() → 이미지 파일 push
    - image_view_closed / file_cleanup_report → 파일 정리 처리
  │
  ▼ (클라이언트 전달이 필요한 액션)
[15] server_command 빌드 (_build_server_command_v4):
    - 액션별 params 변환:
      move_forward  → {lx: +abs, az: 0, dur, hz, stop}
      move_backward → {lx: -abs, az: 0, dur, hz, stop}
      turn_left     → {lx: 0, az: +abs, dur, hz, stop}
      turn_right    → {lx: 0, az: -abs, dur, hz, stop}
      custom_move   → {lx, az, dur, hz, stop} 그대로
      start_mapping → {explore: true(강제), mapping_engine: "cartographer", [map_name], [session_id]}  timeout: 30s
      stop_mapping  → {save: true, [map_name], [session_id], [format]}  timeout: 60s
      robot_stop    → {lx:0, az:0, dur:0, hz, stop:true, kill_explorer:true, reason}  timeout: 5s
      emergency_stop → robot_stop와 동일 + kill_explorer:true
      기타 액션    → params 그대로 전달
    - server_priority, blocking_type, interrupt_policy: action_policy.json에서 주입
    - ros: {domain_id:14, namespace:"/tb1", topic:"/tb1/cmd_vel"} 주입
    - robot_id: "14" (wire robot_id)
    - job_id 생성
  │
  ▼
[16] 클라이언트로 명령 전송 (_send_server_command_to_agent_v4):
    - 포트 5001에 TCP 연결
    - server_command JSON 1줄 전송
    - agent_result 수신 대기
    - 타임아웃 시 E_TIMEOUT
    - 연결 실패 시 E_AGENT_DISCONNECTED
  │
  ▼
[17] 결과 검증:
    - agent_result.ref == server_command.msg_id ?
    - agent_result.robot_id == "14" ?
    - agent_result.command.command_id 일치 ?
    - 불일치 시 E_STATE_MISMATCH
  │
  ▼
[18] 특수 후처리:
    - rsync_map 또는 stop_mapping이고 ok=true → _sync_map_from_client_v5()
      (포트 5002로 파일 경로 요청 → SSH rsync로 서버에 pull)
  │
  ▼
[19] 로봇 상태 업데이트: robot_states 딕셔너리에 최신 state 기억
  │
  ▼
[20] v4 응답 → v6 응답 변환 (_operator_response_v4_to_v5):
    - mt: "operator_response"
    - v=6, schema="fleet_json_v0.6"
    - results.tb1.operating_mode, robot_state, job_state 등 포함
  │
  ▼
[21] 로그 저장: operator_responses/ 에 응답 JSON 기록
  │
  ▼
[22] 제어 UI에 응답 전송 (같은 TCP 연결)
```

---

## 6. 전체 맵핑 흐름 (자동 모드, explore:true)

```
[제어 UI]                    [Fleet Server]                  [Robot Command Client]
    │                              │                                   │
    │── start_mapping ──────────→  │                                   │
    │   (포트 4001, explore:true)  │                                   │
    │                              │── server_command ────────────────→│
    │                              │   op=start_mapping                │
    │                              │   params={explore:true,           │
    │                              │           mapping_engine:         │
    │                              │           "cartographer"}         │
    │                              │   (포트 5001)                     │
    │                              │                                   │── ROS2 cartographer 실행
    │                              │                                   │── slam_explorer 노드 실행
    │                              │←── agent_result ─────────────────│
    │                              │    ok=true, code=R_STARTED        │
    │                              │    operating_mode=MAPPING         │
    │                              │    robot_state=MAPPING            │
    │                              │    job_state=RUNNING              │
    │←── operator_response ───────│                                   │
    │    ok=true, R_STARTED        │                                   │
    │    operating_mode=MAPPING    │                                   │
    │                              │                                   │
    │  [자율 탐색 중... LiDAR 데이터 축적 중...]                        │
    │                              │                                   │
    │  [주기적 헬스체크]            │←── client_heartbeat ────────────→│
    │                              │    (포트 5000, 서버→클라이언트)   │
    │                              │    coverage_percent 업데이트       │
    │                              │                                   │
    │  [탐색 완료 조건 감지 — 클라이언트 자동 판단]                      │
    │                              │                                   │── SLAM 종료
    │                              │                                   │── 맵 저장
    │                              │                                   │   (pgm + yaml)
    │                              │                                   │── dir_name 생성
    │                              │                                   │   (YYYYMMDD_HHMMSS_tb1_autoSave_1)
    │                              │                                   │
    │                              │←── mapping_complete_notification ─│
    │                              │    (포트 4003, 클라이언트→서버)   │
    │                              │    map_dir_name                   │
    │                              │    client_map_dir (절대경로)       │
    │                              │──→ mapping_complete_ack ─────────│
    │                              │    ok=true, R_ACCEPTED            │
    │                              │                                   │
    │                              │ [백그라운드 스레드 시작]           │
    │                              │── SSH rsync pull ────────────────→│
    │                              │   ubuntu22@192.168.3.63:          │
    │                              │   /home/ubuntu22/ros2_ws/maps/    │
    │                              │   YYYYMMDD_HHMMSS_tb1_autoSave_1/ │
    │                              │   → 서버: data/maps/              │
    │                              │             (map.pgm, map.yaml)   │
    │                              │                                   │
    │── map_list ─────────────────→│                                   │
    │   (포트 4001)                 │                                   │
    │                              │ [data/maps/ 스캔]                  │
    │                              │ [dir_name 파싱 및 메타데이터 생성] │
    │←── R_STATUS ────────────────│                                   │
    │    status.maps[]             │                                   │
    │    [{index:1, dir_name:...,  │                                   │
    │      date, time, robot,      │                                   │
    │      save_method, display}]  │                                   │
    │                              │                                   │
    │── map_image_select ─────────→│                                   │
    │   (포트 4001, index=1)        │                                   │
    │                              │ [data/maps/dir_name/ 확인]        │
    │                              │── SSH rsync push ─────────────────────────────────→
    │                              │   rsync -az -e ssh               [제어 UI 노트북]
    │                              │   data/maps/dir_name/             192.168.3.59
    │                              │   → ubuntu@192.168.3.59:          ubuntu
    │                              │     /home/ubuntu/                 /home/ubuntu/
    │                              │     control_laptop/               control_laptop/
    │                              │     control_laptop_map/           control_laptop_map/
    │                              │                     dir_name/
    │                              │                     ├ map.pgm
    │                              │                     └ map.yaml
    │←── R_FILE_SYNC_REPORTED ────│
    │    ok=true                   │
    │                              │
    │ [map.pgm 파일 표시]           │
```

---

## 7. 맵핑 흐름 (수동 모드, explore 없음)

```
제어: start_mapping (explore 없음 또는 false)
  → 서버 → 클라이언트: op=start_mapping, params={explore:true, mapping_engine:"cartographer"}
    (서버가 explore:true 강제 주입)
  ← R_STARTED, operating_mode=MAPPING

제어: move_forward / turn_left / turn_right 등
  → 운영자가 직접 이동 명령 보내며 수동 탐색

제어: save_map (MAPPING 모드 중에만 가능)
  → 클라이언트: op=save_map
  ← R_MAP_LOCAL_SAVED (MAPPING 모드 유지)

제어: stop_mapping
  → 클라이언트: op=stop_mapping, params={save:true}  timeout: 60초
  ← R_DONE, operating_mode=MANUAL
  → 서버: _sync_map_from_client_v5() 자동 호출
           포트 5002로 파일 경로 요청
           SSH rsync로 서버에 pull

제어: map_list → map_image_select (위 자동 모드와 동일)
```

---

## 8. 이동 명령 처리 흐름

```
제어 UI: move_forward
  params: { lx: 0.05, dur: 2.0, hz: 10, stop: true }
         (lx 양수로 전송, 서버가 abs() 적용)

서버 내부 params 변환:
  command_params = {
    lx: +abs(lx),   ← 항상 양수
    az: 0.0,
    dur: 2.0,
    hz: 10,
    stop: true
  }

클라이언트 전달:
  server_command.command.op = "move_forward"
  server_command.command.params = {lx:0.05, az:0.0, dur:2.0, hz:10, stop:true}
  server_command.command.ros = {domain_id:14, namespace:"/tb1", topic:"/tb1/cmd_vel"}

클라이언트 실행:
  /tb1/cmd_vel 토픽으로 Twist 메시지 hz=10, dur=2.0초 동안 publish
  stop=true이면 완료 후 Twist(0,0) 전송

응답: ok=true, code=R_DONE, operating_mode=MANUAL, robot_state=IDLE

---

[ 이동 액션별 서버 params 변환 규칙 ]

move_forward  → lx = +abs(입력값),  az = 0.0
move_backward → lx = -abs(입력값),  az = 0.0
turn_left     → lx = 0.0,  az = +abs(입력값)
turn_right    → lx = 0.0,  az = -abs(입력값)
custom_move   → lx = 입력값 그대로, az = 입력값 그대로 (부호 변경 없음)

[ 파라미터 기본값 및 한계 ]
lx 기본: 0.05 m/s, 최대: 0.1 m/s
az 기본(직진): 0.0 rad/s
az 기본(회전): 0.5 rad/s, 최대: 1.0 rad/s
dur 기본: 2.0초, 최대: 5.0초
hz 기본: 10, 최대: 50
```

---

## 9. 긴급 정지 흐름

```
[제어 UI]                    [Fleet Server]                  [클라이언트]
    │                              │                               │
    │── emergency_stop ───────────→│                               │
    │   target_scope: "all"        │                               │
    │   targets: ["all"]           │                               │
    │                              │ global_state = "EMERGENCY"    │
    │                              │ (메모리에 기록)               │
    │                              │                               │
    │                              │── server_command ────────────→│
    │                              │   op: robot_stop               │
    │                              │   params: {lx:0, az:0,        │
    │                              │           stop:true,           │
    │                              │           kill_explorer:true,  │
    │                              │           reason:"operator_stop"}
    │                              │                               │── cmd_vel Twist(0,0) 전송
    │                              │                               │── slam_explorer 종료
    │                              │←── agent_result ─────────────│
    │                              │    code=R_STOPPED             │
    │←── operator_response ───────│                               │
    │    code=R_STOPPED            │                               │
    │                              │                               │
    │ [이후 이동/맵핑/네비 명령]    │                               │
    │── move_forward ─────────────→│                               │
    │                              │ [11번 모드 체크]               │
    │                              │ global_state == EMERGENCY     │
    │←── E_SYSTEM_EMERGENCY ──────│ → 즉시 거부                   │
    │                              │                               │
    │── clear_emergency ──────────→│                               │
    │   (긴급 해제)                │                               │
    │                              │ global_state = "NORMAL"       │
    │←── R_STATUS ────────────────│                               │
    │                              │                               │
    │ [이제 명령 다시 가능]         │                               │
```

---

## 10. operating_mode 상태 전이도

```
상태 목록:
  STARTUP → MANUAL → MAPPING → MANUAL
                   → NAVIGATION → MANUAL
         → AUTO
         → PAUSED (←→ 이전 모드)
         → EMERGENCY → MANUAL (clear_emergency 후)
         → SERVICE
         → ERROR
         → SHUTDOWN

전이 조건:
  STARTUP  → MANUAL      : 부팅 완료
  MANUAL   → MAPPING     : start_mapping 성공 (R_STARTED)
  MANUAL   → NAVIGATION  : nav_goal 성공 (R_STARTED), 지도 있을 때
  MAPPING  → MANUAL      : stop_mapping 성공 (R_DONE)
  NAVIGATION → MANUAL    : nav_cancel (R_CANCELED) 또는 목표 도달 (R_DONE)
  ANY      → PAUSED      : pause_robot / pause_all
  PAUSED   → (이전 모드)  : resume_robot / resume_all
  ANY      → EMERGENCY   : emergency_stop
  EMERGENCY → MANUAL     : clear_emergency (조건: all_robot_stopped + operator_confirm + opencv_safety_clear)

모드별 허용 액션:
  MANUAL:      이동, start_mapping, nav_goal, 상태조회, 정지, 일시정지
  MAPPING:     이동, stop_mapping, save_map, rsync_map, 상태조회, 정지, 일시정지
  NAVIGATION:  nav_cancel, 상태조회, 정지, 일시정지
  PAUSED:      resume, stop_mapping(if was MAPPING), 상태조회, 정지
  EMERGENCY:   emergency_stop, all_stop, status_request, clear_emergency, reset_all_jobs
  ANY:         robot_stop, all_stop, emergency_stop, ping, map_list, map_image_select
```

---

## 11. 헬스체크 흐름

### 제어 UI → 서버 헬스체크 (포트 4000, 주기적)

```
제어 UI: control_health_request
  → 서버 포트 4000

서버 처리:
  1. 클라이언트(5000)에 client_heartbeat_request 전송
  2. 클라이언트 응답에서 robot_states 업데이트
  3. 종합 상태 반환

서버 응답: control_health_response
  ok: true
  code: R_HEALTH_OK (클라이언트 연결됨) 또는 R_HEALTH_WARN (클라이언트 미연결)
  server: { uptime_sec, global_state, public_ip, 포트 번호들 }
  client: { connection_state: CONNECTED/DISCONNECTED, ip, port, elapsed_ms }
  robots: {
    tb1: {
      operating_mode, robot_state, job_state, accept_state, ui_mode,
      mapping: { coverage_percent, map_start_ts, autosaved }
    }
  }

연결 상태 코드:
  R_HEALTH_OK   : 서버 + 클라이언트 모두 정상
  R_HEALTH_WARN : 서버는 살아있으나 클라이언트 연결 없음
```

---

## 12. 맵 이미지 수신 상세 흐름 (map_list → map_image_select)

```
[제어 UI]                    [Fleet Server]
    │                              │
    │── map_list ─────────────────→│
    │   (포트 4001)                 │
    │   params: { robot: "tb1" }   │ [서버: data/maps/ 디렉토리 스캔]
    │                              │ [dir_name 파싱: YYYYMMDD_HHMMSS_robot_method_N]
    │                              │ [메타데이터 추출: date, time, robot, save_method]
    │                              │ [index 1-N 부여]
    │←── R_STATUS ────────────────│
    │    status: {                 │
    │      maps: [                 │
    │        { index: 1,           │
    │          dir_name: "20260624_202331_tb1_stop_1",
    │          date: "2026-06-24", │
    │          time: "20:23:31",   │
    │          robot: "tb1",       │
    │          save_method: "stop",│
    │          save_number: 1,     │
    │          files: ["map.pgm", "map.yaml"],
    │          display: "2026-06-24 20:23:31 | tb1 | stop | #1"
    │        }                     │
    │      ],                      │
    │      map_total: 1            │
    │    }                         │
    │                              │
    │ [운영자: 번호 1 선택]         │
    │                              │
    │── map_image_select ─────────→│
    │   (포트 4001)                 │
    │   params: { index: 1 }       │
    │   (또는 dir_name 직접 지정)   │
    │                              │ [서버: data/maps/20260624_202331_tb1_stop_1/ 확인]
    │                              │ [rsync push 실행]
    │                              │   rsync -az
    │                              │   -e "ssh -o BatchMode=yes
    │                              │        -o ConnectTimeout=5
    │                              │        -o StrictHostKeyChecking=accept-new"
    │                              │   data/maps/20260624_202331_tb1_stop_1/
    │                              │   ubuntu@192.168.3.59:
    │                              │   /home/ubuntu/control_laptop/control_laptop_map/
    │                              │   20260624_202331_tb1_stop_1/
    │←── R_FILE_SYNC_REPORTED ────│
    │    ok: true                  │
    │                              │
    │ [제어 UI: 파일 확인]          │
    │   ~/control_laptop/          │
    │   control_laptop_map/        │
    │   20260624_202331_tb1_stop_1/│
    │   ├─ map.pgm                 │
    │   └─ map.yaml                │
```

---

## 13. 맵 파일 저장 경로 전체

```
[Robot Command Client, 192.168.3.63]
  /home/ubuntu22/ros2_ws/maps/
    └─ YYYYMMDD_HHMMSS_tb1_autoSave_1/
       ├─ map.pgm
       └─ map.yaml

         ↓ SSH rsync pull (서버가 클라이언트에서 당김)
         SSH key: /home/admin_kyj/.ssh/fleet_server_map_pull_ed25519

[Fleet Server, 192.168.3.61]
  /home/admin_kyj/turtlebot_server/data/maps/
    └─ YYYYMMDD_HHMMSS_tb1_autoSave_1/
       ├─ map.pgm
       └─ map.yaml

         ↓ SSH rsync push (서버가 제어 UI에 밀어넣음)
         user: ubuntu, key: 기본 SSH 키

[Control UI, 192.168.3.59]
  /home/ubuntu/control_laptop/control_laptop_map/
    └─ YYYYMMDD_HHMMSS_tb1_autoSave_1/
       ├─ map.pgm
       └─ map.yaml
```

---

## 14. 서버 커넥션 구조 (소켓 모델)

```
Fleet Server 메인 루프:
  - 포트 4000, 4001, 4002, 4003 동시 listen
  - 새 연결 수신 시 스레드 생성 (threading.Thread)

포트 4000/4001/4002:
  - _handle_control_connection() (스레드)
  - while True 루프: 연결 유지하며 다수 요청 처리
  - 연결 끊어지면 루프 종료

포트 4003:
  - _handle_client_event_connection() (스레드)
  - mapping_complete_notification 1회 수신
  - mapping_complete_ack 전송
  - 연결 종료 후 백그라운드 스레드로 _auto_sync_map_from_client_v5() 실행

서버→클라이언트 (5001):
  - 명령마다 새 TCP 연결
  - 1회 전송 → 1회 수신 → 연결 종료

서버→클라이언트 (5000, 헬스):
  - _probe_robot_command_client_v5()
  - 헬스체크마다 새 TCP 연결

서버→클라이언트 (5002, 데이터):
  - _send_client_data_prepare_request_v5()
  - rsync_map 시 파일 경로 협상에 사용
```

---

## 15. 로봇 ID 매핑

```
제어 UI에서 사용하는 이름 : "tb1"
서버 내부 키 (robot_key)   : "tb1"
서버→클라이언트 wire ID    : "14"
ROS_DOMAIN_ID              : 14
ROS namespace              : /tb1
cmd_vel topic              : /tb1/cmd_vel

제어 UI는 targets에 "tb1" 또는 "14" 모두 사용 가능.
서버가 클라이언트로 보내는 server_command.command.robot_id는 항상 "14".
```

---

## 16. 결과 코드 분류

```
성공 코드 (R_):
  R_DONE              : 명령 정상 완료 (이동, save_map, stop_mapping 등)
  R_STARTED           : 백그라운드 작업 시작 (start_mapping, nav_goal)
  R_STOPPED           : 정지 완료 (robot_stop)
  R_PAUSED            : 일시정지 완료
  R_RESUMED           : 재개 완료
  R_CANCELED          : 취소 완료 (nav_cancel)
  R_STATUS            : 상태 조회 완료
  R_PONG              : ping 응답
  R_ACCEPTED          : 알림 수락 (mapping_complete_ack)
  R_MAP_LOCAL_SAVED   : 클라이언트 로컬 저장 완료 (save_map)
  R_FILE_SYNC_REPORTED: 파일 동기화 완료 (rsync_map, map_image_select)
  R_HEALTH_OK         : 헬스체크 정상
  R_HEALTH_WARN       : 헬스체크 경고 (클라이언트 미연결)

오류 코드 (E_):
  E_UNKNOWN_ACTION    : FLEET_ACTIONS에 없는 액션
  E_MODE_BLOCKED      : 현재 operating_mode에서 불허
  E_SYSTEM_EMERGENCY  : global_state=EMERGENCY 상태
  E_ROBOT_BUSY        : 로봇이 다른 명령 처리 중
  E_DUPLICATE_COMMAND : 같은 command_id 재사용
  E_TIMEOUT           : 클라이언트 응답 시간 초과
  E_AGENT_DISCONNECTED: 클라이언트 TCP 연결 없음
  E_TARGET_INVALID    : 없는 robot_id 또는 비활성 로봇
  E_STATE_MISMATCH    : agent_result의 ref/robot_id/command_id/op 불일치
  E_FILE_SYNC_FAILED  : rsync 실패 (경로 없음, SSH 인증 실패, 타임아웃 등)
  E_BAD_REQUEST       : JSON 구조 오류 (필드 누락, 타입 오류)
  E_BAD_JSON          : JSON 파싱 실패
  E_SERVER_CONNECT    : 클라이언트 연결 자체 실패 (OSError)
```

---

## 17. JSON 버전 호환성

```
서버 수신 (인바운드): v=5 또는 v=6 모두 수락
서버 발신 (아웃바운드): 항상 v=6, schema="fleet_json_v0.6"

수락 schema 집합 (FLEET_JSON_SCHEMA_V5_COMPAT):
  "fleet_json_v0.5"
  "fleet_json_v0.5.1"
  "fleet_json_v0.6"

v=6 전용 기능:
  - 포트 4003 (mapping_complete_notification)
  - map_list 메타데이터 상세 응답
  - map_image_select 신규 액션
  - 맵 디렉토리 이름 규칙 (YYYYMMDD_HHMMSS_robot_method_N)
```

---

## 18. 설정 파일 요약

```
server_config.json:
  server.public_ip: 192.168.3.61
  server.control_port: 4000
  server.control_command_port: 4001
  server.control_data_port: 4002
  server.client_event_port: 4003
  server.socket_timeout: 6.0
  defaults.lx: 0.05, az: 0.0, turn_az: 0.5, dur: 2.0, hz: 10, timeout: 5.0
  limits.lx_abs_max: 0.1, az_abs_max: 1.0, dur_max: 5.0, hz_max: 50
  safety.allow_multi_robot_move: false
  file_transfer.rsync_timeout: 30.0
  paths.server_map_backup_dir: /home/admin_kyj/turtlebot_server/data/maps

client_info.json:
  robot_command_client.ip: 192.168.3.63
  robot_command_client.health_port: 5000
  robot_command_client.command_port: 5001
  robot_command_client.data_control_port: 5002
  robot_command_client.ssh.identity_file: ~/.ssh/fleet_server_map_pull_ed25519
  robots.tb1.robot_id: "14"
  robots.tb1.ros_domain_id: 14
  robots.tb1.namespace: /tb1
  robots.tb1.topic: /tb1/cmd_vel

control_info.json:
  control_ui.ip: 192.168.3.59
  control_ui.user: ubuntu
  control_ui.ssh.port: 22
  control_ui.paths.control_map_receive_dir: /home/ubuntu/control_laptop/control_laptop_map
  image_transfer.method: rsync_over_ssh
  image_transfer.direction: server_push

action_policy.json (주요 항목):
  start_mapping: priority=40, SOFT, reject_if_busy, 허용모드=[MANUAL,AUTO,SERVICE]
  stop_mapping:  priority=40, HARD, interrupt_current, 허용모드=[MAPPING,PAUSED]
  robot_stop:    priority=3,  HARD, interrupt_current, 허용모드=[ANY]
  all_stop:      priority=2,  HARD, interrupt_current, 허용모드=[ANY], target=all
  emergency_stop:priority=1,  HARD, interrupt_current, 허용모드=[ANY]
  move_*:        priority=10, SOFT, reject_if_busy,    허용모드=[MANUAL,MAPPING]
  map_list:      priority=90, SOFT, reject_if_busy,    허용모드=[ANY]
  map_image_select:priority=90,SOFT,reject_if_busy,   허용모드=[ANY]
  rsync_map:     priority=55, SINGLE, queue_if_busy,  허용모드=[MAPPING,SERVICE]
  save_map:      priority=50, SINGLE, reject_if_busy, 허용모드=[MAPPING,SERVICE]
  nav_goal:      priority=30, SOFT, reject_if_busy,   허용모드=[AUTO,MANUAL]
```

---

## 19. 맵핑 완료 자동 동기화 흐름 (포트 4003)

```
조건: 클라이언트가 SLAM 완료 후 자동으로 서버에 알림

1. 클라이언트 → 서버 포트 4003 TCP 연결
2. mapping_complete_notification 전송:
   {
     "mt": "mapping_complete_notification",
     "notification": {
       "robot_alias": "tb1",
       "map_dir_name": "YYYYMMDD_HHMMSS_tb1_autoSave_1",   ← 필수
       "client_map_dir": "/home/ubuntu22/ros2_ws/maps/...", ← 필수
       "save_method": "autoSave",
       "map_start_ts": "...",
       "files": ["map.pgm", "map.yaml"]
     }
   }

3. 서버 → 클라이언트 ACK:
   { "mt": "mapping_complete_ack", "ok": true, "code": "R_ACCEPTED" }

4. 연결 종료

5. 서버 백그라운드 스레드 (_auto_sync_map_from_client_v5):
   - 이미 서버에 해당 dir_name이 있으면 skip (R_FILE_SYNC_REPORTED)
   - 없으면 SSH rsync pull:
     rsync -az ubuntu22@192.168.3.63:{client_map_dir}/ {server_map_dir}/{map_dir_name}/
   - 성공: data/maps/YYYYMMDD_HHMMSS_tb1_autoSave_1/ 에 map.pgm, map.yaml 저장
   - 실패: 로그에 E_FILE_SYNC_FAILED 기록
```

---

## 20. 로그 디렉토리 구조

```
/home/admin_kyj/turtlebot_server/data/log/server/
  latest/                           ← 현재 세션 (재시작 전까지 유지)
    system/
      startup_check_*.json          ← 서버 시작 시 설정 스냅샷
      shutdown_check_*.json         ← 서버 종료 시 기록
    operator_requests/
      operator_request_*.json       ← 제어 UI로부터 수신한 모든 요청
      latest_operator_request.json  ← 최신 요청 (항상 덮어쓰기)
    operator_responses/
      operator_response_*.json      ← 제어 UI에 보낸 모든 응답
      latest_operator_response.json ← 최신 응답
    commands/
      server_command_*.json         ← 클라이언트에 보낸 모든 명령
      latest_server_command.json    ← 최신 명령
    results/
      agent_result_*.json           ← 클라이언트로부터 받은 모든 결과
      latest_agent_result.json      ← 최신 결과
    client_health/
      latest_client_heartbeat.json  ← 최신 클라이언트 헬스 상태
    client_data/
      mapping_complete_notification_*.json
      auto_map_sync_*.json
      client_map_sync_*.json
    file_transfers/
      map_image_select_*.json
  events/
    session_YYYYMMDD_HHMMSS/       ← 이전 세션 아카이브
      (latest와 동일한 구조)
```

---

## 21. 순서도 제작 시 주의사항

1. **포트 4003은 방향이 반대**: 클라이언트가 서버에 연결. 다른 포트와 화살표 방향 다름.
2. **map_list / map_image_select는 포트 4001**: 4002가 아님. 클라이언트에 전달되지 않고 서버가 직접 처리.
3. **start_mapping 후 explore:true 강제 주입**: 제어 UI가 explore를 안 보내도 서버가 항상 true로 설정.
4. **stop_mapping 후 rsync 자동 실행**: 클라이언트가 R_DONE 반환 시 서버가 자동으로 맵 pull.
5. **mapping_complete_notification은 선택적 경로**: 자동 탐색 완료 시 클라이언트가 먼저 알림 → 서버 pull. 수동 모드는 stop_mapping 후 서버 pull.
6. **서버는 명령을 반복 전송하지 않음**: 제어 UI 요청 1회 → 클라이언트 전달 1회. 재연결 시 재전송 없음.
7. **seen_command_ids**: 서버 재시작 시 초기화. 동일 command_id 재사용 시 E_DUPLICATE_COMMAND.
8. **timeout 주의**: adapter가 UI 미지정 시 5.0초 기본 주입 → start_mapping(30s), stop_mapping(60s) 분기의 기본값 무력화되는 버그 있음 (수정 예정).
