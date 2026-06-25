# TurtleBot Fleet JSON v0.5.1 팀 공유 프롬프트

당신은 TurtleBot 협업 제어 시스템의 제어 UI 또는 Robot Command Client 담당자입니다.

서버 담당자는 Fleet Server v0.5.1 규칙을 준비했습니다. 이 문서는 제어 UI, Fleet Server, Robot Command Client가 같은 JSON 규칙으로 통신하기 위한 통합 전달용 프롬프트입니다.

## 1. 버전 기준

새 구현은 아래 값을 사용하세요.

```text
v = 5
schema = fleet_json_v0.5.1
protocol = TCP + UTF-8 + NDJSON
JSON 1개 = 한 줄
마지막은 반드시 \n
pretty JSON 여러 줄 전송 금지
```

서버는 과도기 호환을 위해 `fleet_json_v0.5` 입력도 받을 수 있습니다. 하지만 새로 작성하거나 수정하는 코드는 `fleet_json_v0.5.1`을 기준으로 하세요.

## 2. 전체 구조

```text
Control UI
  -> control_command_request / operator_request
Fleet Server
  -> server_command
Robot Command Client
  -> ROS2 / TurtleBot 실행
```

응답은 반대 방향입니다.

```text
Robot Command Client
  -> agent_result
Fleet Server
  -> operator_response
Control UI
```

Control UI는 TurtleBot에 직접 ROS2 명령을 보내지 않습니다. Robot Command Client는 Control UI와 직접 통신하지 않습니다.

## 3. 포트 규칙

### Control UI -> Fleet Server

```text
health: 4000
command: 4001
data_control: 4002
```

```text
4000: control_health_request -> control_health_response
4001: control_command_request 또는 operator_request -> operator_response
4002: control_data_request -> control_data_response
```

### Fleet Server -> Robot Command Client

```text
health: 5000
command: 5001
data_control: 5002
```

```text
5000: client_heartbeat_request -> client_heartbeat_response
5001: server_command -> agent_result
5002: client_data_prepare_request -> client_data_prepare_response
```

## 4. 현재 로봇 기준

```text
display alias: tb1
actual robot_id: 14
ROS_DOMAIN_ID: 14
namespace: /tb1
cmd_vel topic: /tb1/cmd_vel
```

Control UI는 target으로 `tb1` 또는 `14`를 사용할 수 있습니다. Fleet Server가 Robot Command Client로 보내는 `server_command.command.robot_id`는 실제 ID인 `"14"`입니다.

## 5. Control UI 명령 요청 형식

제어 UI는 command 포트 4001로 아래 구조를 보냅니다.

```json
{
  "v": 5,
  "mt": "control_command_request",
  "msg_id": "MSG_EXAMPLE_000001",
  "ts": "2026-06-24T12:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "command": {
    "command_id": "CMD_EXAMPLE_000001",
    "command_revision": 0,
    "action": "move_forward",
    "target_scope": "single",
    "targets": ["tb1"],
    "params": {},
    "timeout_sec": 5.0
  }
}
```

필수 매칭/표시용 필드:

```text
msg_id
command.command_id
command.action
command.targets
command.params
```

## 6. 이동 명령

지원 action/op:

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

전진 예시:

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

Fleet Server가 Robot Command Client로 전달할 때는 `server_command.command.op`가 동일한 이름으로 들어갑니다. `all_stop`은 서버가 각 로봇별 `robot_stop`으로 fanout할 수 있습니다.

## 7. 맵핑 시작

맵핑 시작 action/op는 `start_mapping`입니다.

Control UI 요청:

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
  }
}
```

params 규칙:

```text
mode = "mapping"
mapping_engine = "cartographer" 권장
auto_explore = true이면 SLAM 시작 후 자동 탐색 시작
explore = auto_explore의 별칭
map_name = 선택
session_id = 선택
```

Robot Command Client는 `start_mapping`을 받으면 Cartographer SLAM을 백그라운드로 시작하고 즉시 `agent_result`를 반환하세요. 실제 맵핑 완료까지 기다리지 마세요.

성공 응답 권장:

```text
ok = true
code = R_STARTED
operating_mode = MAPPING
robot_state = MAPPING
job_state = RUNNING
accept_state = ACCEPTING 또는 QUEUEABLE
ui_mode = BUSY_QUEUEABLE
```

## 8. 맵 저장

맵 저장 action/op는 `save_map`입니다.

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

Robot Command Client 성공 응답 권장:

```text
ok = true
code = R_MAP_LOCAL_SAVED
message = saved map path or map name
```

## 9. 맵 파일 서버 안착

맵 파일 전송 요청 action/op는 `rsync_map`입니다.

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

흐름:

```text
1. Control UI -> Fleet Server: rsync_map
2. Fleet Server -> Robot Command Client 5001: server_command(op=rsync_map)
3. Robot Command Client -> Fleet Server: agent_result(ok=true)
4. Fleet Server -> Robot Command Client 5002: client_data_prepare_request
5. Robot Command Client -> Fleet Server: client_data_prepare_response(files 포함)
6. Fleet Server가 파일을 서버 디렉토리에 저장
7. Fleet Server가 latest map image를 갱신
```

`client_data_prepare_response` 예시:

```json
{
  "v": 5,
  "mt": "client_data_prepare_response",
  "msg_id": "MSG_CLIENT_DATA_PREPARE_RESPONSE_TB1_000001",
  "ref": "MSG_CLIENT_DATA_PREPARE_TB1_000001",
  "ts": "2026-06-24T12:06:01+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "ok": true,
  "code": "R_MAP_READY",
  "message": "map files are ready",
  "transfer": {
    "method": "rsync_over_ssh"
  },
  "files": [
    {
      "kind": "map_image",
      "name": "tb1_classroom_map.png",
      "remote_path": "/home/ubuntu/turtlebot_client/data/maps/tb1_classroom_map.png"
    },
    {
      "kind": "map_yaml",
      "name": "tb1_classroom_map.yaml",
      "remote_path": "/home/ubuntu/turtlebot_client/data/maps/tb1_classroom_map.yaml"
    }
  ],
  "err": []
}
```

## 10. 제어 UI에서 맵 이미지 표시

제어 UI가 서버의 최신 맵 이미지를 보고 싶으면 data_control 포트 4002로 `control_data_request`를 보낼 수 있습니다.

```json
{
  "v": 5,
  "mt": "control_data_request",
  "msg_id": "MSG_MAP_IMAGE_REQUEST_TB1_000001",
  "ts": "2026-06-24T12:07:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "request": {
    "request_id": "REQ_MAP_IMAGE_TB1_000001",
    "data_type": "map",
    "target": "tb1",
    "timeout_sec": 10.0
  }
}
```

서버는 `data_type=map` 또는 `data_type=image`를 이미지 요청 흐름으로 처리합니다.

## 11. operator_response 처리

제어 UI는 서버 응답의 아래 필드를 우선 표시하세요.

```text
ok
code
message
command.action
results.tb1.ok
results.tb1.code
results.tb1.connection_state
results.tb1.operating_mode
results.tb1.robot_state
results.tb1.job_state
results.tb1.message
err
ui_hint
```

주의:

```text
control_health_response.ok=true는 서버 생존 의미입니다.
클라이언트 연결 상태는 client.connection_state를 봅니다.
로봇 상태는 robots.tb1 또는 operator_response.results.tb1을 봅니다.
서버가 임의 true로 처리하지 않고 클라이언트 heartbeat/agent_result 값을 반영합니다.
```

## 12. 클라이언트 구현 체크리스트

```text
1. 5000/5001/5002 포트를 listen한다.
2. client_heartbeat_request에 client_heartbeat_response를 반환한다.
3. server_command.op=move_* 계열을 /cmd_vel publish로 처리한다.
4. server_command.op=start_mapping을 Cartographer SLAM 백그라운드 실행으로 처리한다.
5. auto_explore 또는 explore가 true이면 자동 탐색도 시작한다.
6. server_command.op=save_map을 맵 저장으로 처리한다.
7. server_command.op=rsync_map에 성공 agent_result를 반환하고, 5002 data_control 요청에 파일 정보를 반환한다.
8. 모든 실패도 ok=false JSON으로 응답한다.
9. ref, robot_id, command_id, op 매칭 규칙을 지킨다.
10. heartbeat에서 현재 operating_mode/robot_state/job_state를 계속 보고한다.
```

## 13. 제어 UI 구현 체크리스트

```text
1. health는 4000으로 보낸다.
2. 이동/맵핑/저장/전송 명령은 4001로 보낸다.
3. 카메라 이미지/로그 요청은 4002로 보낸다.
   ※ v0.5.1에서는 data_type=map도 4002로 허용됨.
   ※ v0.6부터 map_list / map_image_select는 4001(command)로 이동 — v0.6 문서 참고.
4. start_mapping에서 자동 탐색이 필요하면 auto_explore=true를 명시한다.
5. save_map과 rsync_map은 start_mapping 성공 후 보낸다.
6. ok만 보지 말고 code/results/robots/client 상태를 함께 표시한다.
```

## 14. v0.5.1에서 새로 명확히 한 점

```text
schema=fleet_json_v0.5.1 사용
start_mapping.params.auto_explore 공식화
start_mapping.params.explore 별칭 허용
save_map params 공식화
rsync_map params 공식화
control_data_request data_type=map 허용
제어 3포트와 클라이언트 3포트 역할 명확화
```
