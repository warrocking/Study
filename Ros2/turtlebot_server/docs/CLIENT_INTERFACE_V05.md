# Client Interface v0.5.1

현재 Fleet Server와 Robot Command Client 사이의 기준 규칙입니다.

새 구현은 `v=5`, `schema=fleet_json_v0.5.1`을 사용합니다. 서버는 과도기 호환을 위해 `fleet_json_v0.5` 입력도 받을 수 있습니다.

## 포트

```text
Fleet Server -> Robot Command Client health: client_info.json의 robot_command_client.ip:5000
Fleet Server -> Robot Command Client command: client_info.json의 robot_command_client.ip:5001
Fleet Server -> Robot Command Client data_control: client_info.json의 robot_command_client.ip:5002
```

```text
5000 health       client_heartbeat_request -> client_heartbeat_response
5001 command      server_command -> agent_result
5002 data_control client_data_prepare_request -> client_data_prepare_response
```

## 공통 매칭 규칙

```text
agent_result.ref == server_command.msg_id
agent_result.robot_id == server_command.command.robot_id
agent_result.command.command_id == server_command.command.command_id
agent_result.command.op == server_command.command.op
```

성공 code는 `OK`가 아니라 `R_STARTED`, `R_DONE`, `R_STOPPED`, `R_STATUS`, `R_CLIENT_ALIVE` 같은 서버 규칙 값을 사용합니다.

## 이동 op

```text
move_forward
move_backward
turn_left
turn_right
custom_move
robot_stop
emergency_stop
```

이동 계열은 `command.params.lx`, `az`, `dur`, `hz`, `stop`을 기준으로 `/tb1/cmd_vel`에 publish합니다.

## start_mapping

`command.op=start_mapping`이면 Cartographer SLAM을 백그라운드로 시작하고, 같은 TCP 연결에서 즉시 `agent_result`를 반환합니다. 실제 맵핑 완료까지 기다리면 제어 UI가 멈출 수 있습니다.

대표 params:

```json
{
  "mode": "mapping",
  "mapping_engine": "cartographer",
  "auto_explore": true
}
```

`auto_explore=true` 또는 `explore=true`이면 SLAM 시작 후 자동 탐색도 시작합니다.

성공 응답 권장:

```text
ok=true
code=R_STARTED
operating_mode=MAPPING
robot_state=MAPPING
job_state=RUNNING
accept_state=ACCEPTING
ui_mode=BUSY_QUEUEABLE
```

## save_map

`command.op=save_map`이면 클라이언트는 현재 맵을 로컬 파일로 저장합니다.

성공 응답 권장:

```text
ok=true
code=R_MAP_LOCAL_SAVED
operating_mode=MAPPING 또는 SERVICE
robot_state=SAVING_MAP 또는 MAPPING
job_state=DONE
```

가능하면 저장된 파일 경로를 `message`, `perf`, 또는 `err.detail`에 남깁니다.

## rsync_map과 data_control

`command.op=rsync_map` 성공 후 서버는 5002 포트로 `client_data_prepare_request`를 보냅니다.

클라이언트는 `client_data_prepare_response`에 맵 이미지, yaml, metadata 파일 정보를 넣어 반환합니다.

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

실제 분리 장비에서는 `remote_path`와 SSH/rsync 설정을 쓰는 구성이 권장됩니다.
