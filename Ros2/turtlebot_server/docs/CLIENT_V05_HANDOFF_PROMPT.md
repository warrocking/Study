# Robot Command Client v0.5.1 작업 지시 프롬프트

당신은 TurtleBot 협업 제어 시스템의 Robot Command Client 담당자입니다.

서버 담당자는 Fleet Server v0.5.1를 준비했습니다. 클라이언트는 서버가 보내는 JSON을 읽고, `command.robot_id`에 따라 실제 TurtleBot 또는 내부 ROS2 실행 코드로 명령을 전달한 뒤, 결과를 JSON으로 반환해야 합니다.

현재 1차 연결 대상 로봇은 아래 기준입니다.

```text
display alias: tb1
actual robot_id: 14
ROS namespace: /tb1
cmd_vel topic: /tb1/cmd_vel
ROS_DOMAIN_ID: 14
```

제어 UI 또는 서버 요청 target은 `tb1` 또는 `14` 둘 다 받을 수 있지만, Fleet Server가 Robot Command Client로 보내는 `server_command.command.robot_id`는 실제 ID인 `"14"`입니다.

## 1. 네트워크 기준

```text
Fleet Server -> Robot Command Client
protocol: TCP + UTF-8 + NDJSON
health listen port: 5000
command listen port: 5001
data_control listen port: 5002
JSON 1개 = 한 줄
모든 송수신 JSON은 마지막에 \n 포함
```

서버는 `client_info.json`의 `robot_command_client.ip`와 아래 포트로 접속합니다.

```text
client_heartbeat_request -> health_port 5000
server_command -> command_port 5001
data control JSON -> data_control_port 5002
```

클라이언트는 먼저 5000, 5001, 5002번 포트에서 listen 해야 합니다.

## 2. 클라이언트가 반드시 받아야 하는 메시지

```text
client_heartbeat_request
server_command
```

## 3. 클라이언트가 반드시 반환해야 하는 메시지

```text
client_heartbeat_response
agent_result
```

## 4. client_heartbeat_request 예시

서버가 클라이언트 연결 확인을 위해 `health_port=5000`으로 보냅니다.

```json
{
  "v": 5,
  "mt": "client_heartbeat_request",
  "msg_id": "MSG_CLIENT_HEARTBEAT_REQUEST_000001",
  "ts": "2026-06-23T16:00:00+09:00",
  "source": "fleet_server",
  "dest": "robot_command_client",
  "schema": "fleet_json_v0.5.1",
  "request": {
    "include_robot_states": true,
    "robots": ["14"]
  }
}
```

응답 예시:

```json
{
  "v": 5,
  "mt": "client_heartbeat_response",
  "msg_id": "MSG_CLIENT_HEARTBEAT_RESPONSE_000001",
  "ref": "MSG_CLIENT_HEARTBEAT_REQUEST_000001",
  "ts": "2026-06-23T16:00:00+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "ok": true,
  "code": "R_CLIENT_ALIVE",
  "message": "robot command client alive",
  "client": {
    "connection_state": "CONNECTED"
  },
  "robots": {
    "14": {
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

## 5. server_command 예시

서버가 제어 UI 요청을 받아 클라이언트의 `command_port=5001`로 보내는 명령입니다.

```json
{
  "v": 5,
  "mt": "server_command",
  "msg_id": "MSG_SERVER_COMMAND_TB1_000001",
  "ts": "2026-06-23T16:00:01+09:00",
  "source": "fleet_server",
  "dest": "robot_command_client",
  "schema": "fleet_json_v0.5.1",
  "command": {
    "command_id": "CMD_START_MAPPING_TB1_000001",
    "parent_command_id": null,
    "group_id": null,
    "job_id": "JOB_START_MAPPING_TB1_000001",
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
    "params": {
      "mode": "mapping",
      "mapping_engine": "cartographer",
      "auto_explore": true
    },
    "timeout_sec": 5.0
  }
}
```

## 6. agent_result 응답 규칙

`server_command`를 받으면 반드시 같은 TCP 연결에서 `agent_result` 한 줄 JSON을 반환하세요.

가장 중요한 매칭 규칙:

```text
agent_result.ref == server_command.msg_id
agent_result.robot_id == server_command.command.robot_id
agent_result.command.command_id == server_command.command.command_id
agent_result.command.op == server_command.command.op
```

성공 응답 예시:

```json
{
  "v": 5,
  "mt": "agent_result",
  "msg_id": "MSG_AGENT_RESULT_TB1_000001",
  "ref": "MSG_SERVER_COMMAND_TB1_000001",
  "ts": "2026-06-23T16:00:02+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "robot_id": "14",
  "command": {
    "command_id": "CMD_START_MAPPING_TB1_000001",
    "parent_command_id": null,
    "group_id": null,
    "job_id": "JOB_START_MAPPING_TB1_000001",
    "op": "start_mapping"
  },
  "ok": true,
  "code": "R_STARTED",
  "message": "tb1 start_mapping accepted",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MAPPING",
    "robot_state": "MAPPING",
    "job_state": "RUNNING",
    "accept_state": "ACCEPTING",
    "ui_mode": "BUSY_QUEUEABLE"
  },
  "perf": {
    "elapsed_ms": 10
  },
  "err": []
}
```

`start_mapping`은 Cartographer SLAM을 백그라운드로 시작한 뒤 즉시 `agent_result`를 반환하세요. `auto_explore=true` 또는 `explore=true`가 있으면 SLAM 시작 후 자동 탐색도 시작합니다. 실제 맵핑 완료까지 기다리지 마세요.

`save_map`은 현재 맵을 로컬 파일로 저장하고 `R_MAP_LOCAL_SAVED`를 반환하세요. `rsync_map`은 명령 성공 후 서버가 data_control 5002로 `client_data_prepare_request`를 보낼 수 있게 준비하세요.

실패 응답 예시:

```json
{
  "v": 5,
  "mt": "agent_result",
  "msg_id": "MSG_AGENT_RESULT_TB1_000002",
  "ref": "MSG_SERVER_COMMAND_TB1_000002",
  "ts": "2026-06-23T16:00:02+09:00",
  "source": "robot_command_client",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.5.1",
  "robot_id": "14",
  "command": {
    "command_id": "CMD_START_MAPPING_TB1_000002",
    "parent_command_id": null,
    "group_id": null,
    "job_id": "JOB_START_MAPPING_TB1_000002",
    "op": "start_mapping"
  },
  "ok": false,
  "code": "E_ROBOT_BUSY",
  "message": "tb1 is busy",
  "state": {
    "connection_state": "CONNECTED",
    "operating_mode": "MAPPING",
    "robot_state": "MAPPING",
    "job_state": "REJECTED",
    "accept_state": "BLOCKED",
    "ui_mode": "BUSY_BLOCKED"
  },
  "perf": {
    "elapsed_ms": 1
  },
  "err": [
    {
      "code": "E_ROBOT_BUSY",
      "msg": "tb1 is busy",
      "where": "robot_command_client",
      "detail": {
        "robot_id": "14"
      }
    }
  ]
}
```

## 7. 절대 지켜야 할 규칙

```text
pretty JSON 여러 줄 전송 금지
요청을 받고 무응답으로 연결 종료 금지
실패해도 ok=false agent_result 반환
code는 OK가 아니라 R_DONE, R_STOPPED, R_STATUS, R_CLIENT_ALIVE, E_ROBOT_BUSY 같은 정해진 코드 사용
ref, robot_id, command_id, op 매칭 규칙 준수
```

## 8. 1차 성공 기준

```text
1. 서버 health 요청에 client_heartbeat_response를 반환한다.
2. 서버 start_mapping 명령에 agent_result를 반환한다.
3. 서버 `data/log/server/latest/client_health/latest_client_heartbeat.json`에 CONNECTED가 남는다.
4. 서버 `data/log/server/latest/commands/latest_server_command.json`이 생성된다.
5. 서버 `data/log/server/latest/results/latest_agent_result.json`이 생성된다.
6. 서버 operator_response.results.tb1.code가 클라이언트 응답 code를 반영한다.
```
