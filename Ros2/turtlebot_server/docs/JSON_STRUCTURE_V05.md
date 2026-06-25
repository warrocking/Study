# JSON Structure v0.5.1

현재 기준은 Fleet JSON v0.5.1입니다.

새 메시지는 `v=5`, `schema=fleet_json_v0.5.1`을 사용합니다. 서버는 과도기 호환을 위해 `fleet_json_v0.5` 입력도 받을 수 있습니다.

## 필수 흐름

```text
control_health_request -> control_health_response
operator_request 또는 control_command_request -> operator_response
control_data_request -> control_data_response
client_heartbeat_request -> client_heartbeat_response
server_command -> agent_result
client_data_prepare_request -> client_data_prepare_response
```

서버는 제어의 `operator_request` 또는 `control_command_request`를 내부 요청으로 정규화한 뒤, Robot Command Client에는 `server_command`를 보냅니다.

## 포트

```text
Control UI -> Fleet Server health: 4000
Control UI -> Fleet Server command: 4001
Control UI -> Fleet Server data_control: 4002

Fleet Server -> Robot Command Client health: 5000
Fleet Server -> Robot Command Client command: 5001
Fleet Server -> Robot Command Client data_control: 5002
```

## 주요 action/op

```text
move_forward
move_backward
turn_left
turn_right
custom_move
robot_stop
all_stop
emergency_stop

start_mapping
stop_mapping
mapping_status
save_map
rsync_map
map_status
map_list

image_request
image_view_closed
file_cleanup_report
```

## 실기기 params 규칙

```text
move_forward/move_backward:
  lx, dur, hz, stop

turn_left/turn_right:
  az, dur, hz, stop

custom_move:
  lx, az, dur, hz, stop

start_mapping:
  mode = "mapping"
  mapping_engine = "cartographer" 권장
  auto_explore = true이면 SLAM 후 자동 탐색 시작
  explore = auto_explore 별칭
  map_name = 선택
  session_id = 선택

save_map:
  map_name
  session_id
  format = png_yaml 또는 pgm_yaml 등

rsync_map:
  map_name
  session_id
  preferred_files = 선택
```

서버는 `params` 객체를 클라이언트의 `server_command.command.params`로 전달합니다. 따라서 제어 UI가 `auto_explore`를 명시하면 클라이언트가 그대로 읽을 수 있습니다.

## 상태 보고 규칙

맵핑 시작 성공 후 클라이언트는 `agent_result`와 이후 heartbeat에서 아래 상태를 보고해야 합니다.

```text
connection_state=CONNECTED
operating_mode=MAPPING
robot_state=MAPPING
job_state=RUNNING
accept_state=ACCEPTING 또는 QUEUEABLE
ui_mode=BUSY_QUEUEABLE
```

서버가 제어 UI에 보여주는 로봇 상태는 클라이언트 heartbeat 또는 agent_result에서 받은 값을 기억한 것입니다. 단, `mapping_status` 같은 상태 조회는 현재 서버 캐시 기반이므로 클라이언트가 heartbeat를 꾸준히 갱신해야 합니다.
