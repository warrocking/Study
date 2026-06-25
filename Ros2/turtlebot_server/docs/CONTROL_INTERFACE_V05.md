# Control Interface v0.5.1

현재 제어 UI와 Fleet Server 사이의 기준 규칙입니다.

새 구현은 `v=5`, `schema=fleet_json_v0.5.1`을 사용합니다. 서버는 과도기 호환을 위해 `fleet_json_v0.5` 입력도 받을 수 있습니다.

## 포트

```text
Control UI -> Fleet Server health: 192.168.3.61:4000
Control UI -> Fleet Server command: 192.168.3.61:4001
Control UI -> Fleet Server data_control: 192.168.3.61:4002
```

```text
4000 health       control_health_request -> control_health_response
4001 command      operator_request 또는 control_command_request -> operator_response
4002 data_control control_data_request -> control_data_response
```

명령 요청은 서버 내부에서 기존 처리 흐름으로 정규화된 뒤, Robot Command Client에 `server_command`로 전달되고 최종 `operator_response`가 제어 UI로 돌아옵니다.

## 맵핑 시작

맵핑 버튼은 command 포트 4001로 보냅니다.

```json
{
  "v": 5,
  "mt": "control_command_request",
  "msg_id": "MSG_START_MAPPING_TB1_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "command": {
    "command_id": "CMD_START_MAPPING_TB1_000001",
    "command_revision": 0,
    "action": "start_mapping",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": {
      "mode": "mapping",
      "mapping_engine": "cartographer",
      "auto_explore": true
    },
    "expects": {
      "response_type": "async",
      "status_followup": true
    },
    "timeout_sec": 40.0
  },
  "ui_context": {
    "screen": "main_control",
    "button": "mapping"
  }
}
```

`auto_explore=true` 또는 `explore=true`이면 클라이언트는 SLAM 시작 후 자동 탐색도 시작합니다. 자동 탐색 없이 SLAM만 켜려면 둘 다 생략하거나 false로 보냅니다.

## 이동 명령

이동 명령도 command 포트 4001로 보냅니다.

```json
{
  "v": 5,
  "mt": "control_command_request",
  "msg_id": "MSG_MOVE_FORWARD_TB1_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "command": {
    "command_id": "CMD_MOVE_FORWARD_TB1_000001",
    "command_revision": 0,
    "action": "move_forward",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": {
      "lx": 0.05,
      "dur": 2.0,
      "hz": 10,
      "stop": true
    },
    "timeout_sec": 5.0
  }
}
```

지원 이동 action:

```text
move_forward
move_backward
turn_left
turn_right
custom_move
robot_stop
all_stop
emergency_stop
```

## 맵 저장/전송

권장 흐름:

```text
1. start_mapping
2. 클라이언트가 operating_mode=MAPPING, robot_state=MAPPING 보고
3. save_map
4. rsync_map
5. control_data_request(data_type=image) 또는 image_request로 최신 맵 이미지 표시
```

`save_map` 예시:

```json
{
  "v": 5,
  "mt": "control_command_request",
  "msg_id": "MSG_SAVE_MAP_TB1_000001",
  "ts": "2026-06-24T12:05:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "command": {
    "command_id": "CMD_SAVE_MAP_TB1_000001",
    "command_revision": 0,
    "action": "save_map",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": {
      "map_name": "tb1_classroom_map",
      "session_id": "MAP_SESSION_TB1_001",
      "format": "png_yaml"
    },
    "timeout_sec": 20.0
  }
}
```

`rsync_map` 예시:

```json
{
  "v": 5,
  "mt": "control_command_request",
  "msg_id": "MSG_RSYNC_MAP_TB1_000001",
  "ts": "2026-06-24T12:06:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "command": {
    "command_id": "CMD_RSYNC_MAP_TB1_000001",
    "command_revision": 0,
    "action": "rsync_map",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": {
      "map_name": "tb1_classroom_map",
      "session_id": "MAP_SESSION_TB1_001"
    },
    "timeout_sec": 30.0
  }
}
```

## 응답 표시 기준

UI는 `operator_response.ok`, `operator_response.code`, `operator_response.results.tb1`을 기준으로 상태를 표시합니다.

`control_health_response.ok=true`는 서버 생존 의미입니다. 클라이언트와 로봇 연결 상태는 반드시 `client.connection_state`와 `robots.tb1.connection_state`를 따로 확인하세요.
