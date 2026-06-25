# TurtleBot Fleet Server v0.5.1

이 프로젝트는 서버 담당자 전용 Fleet Server 루트입니다.

기존 `/home/admin_kyj/openCV/server`에 섞여 있던 서버 코드, 설정, 문서, 테스트 도구를 분리하기 위해 만들었습니다.

## 현재 실행 방식

서버 담당자는 아래 명령만 실행합니다.

```bash
cd /home/admin_kyj/turtlebot_server/program/code
python3 server_manager.py
```

`server_manager.py`가 설정을 읽고, 디렉토리를 확인한 뒤 Fleet Server를 실행합니다.

## 현재 실제 연결 기준

```text
Control UI -> Fleet Server
server_ip: 192.168.3.61
health_port: 4000
command_port: 4001
data_control_port: 4002

Fleet Server -> Robot Command Client
client_ip: program/json/client_info.json의 robot_command_client.ip
health_port: 5000
command_port: 5001
data_control_port: 5002

active robot alias: tb1
actual robot_id: 14
protocol: TCP + UTF-8 + NDJSON
control -> server mt: control_health_request / operator_request / control_command_request / control_data_request
server -> client health mt: client_heartbeat_request
client -> server health mt: client_heartbeat_response
server -> client command mt: server_command
client -> server command mt: agent_result
schema: fleet_json_v0.5.1
```

IP가 바뀌면 아래 파일만 우선 수정합니다.

```text
program/json/server_config.json
program/json/control_info.json
program/json/client_info.json
```

## 디렉토리 역할

```text
docs/             사람이 읽는 문서
program/json/     서버 설정 JSON
program/code/     서버 운영 Python 코드
program/scripts/  실행/점검 스크립트
data/             실행 중 생성되는 로그/이미지/맵/전송 파일
tests/            외부 역할 mock
legacy_removed/   운영 코드에서 제외한 과거 파일
```

## 현재 단계

현재는 v0.5.1 통신 호환 구조입니다. 서버는 `fleet_json_v0.5.1`을 기본으로 사용하고, 과도기 호환을 위해 `fleet_json_v0.5` 입력도 받습니다.

```text
완료:
- openCV/server 밖의 새 서버 루트 생성
- server_manager.py 실행 진입점 생성
- control 4000 / client health 5000 / command 5001 / data_control 5002 설정 분리
- Control UI v5 요청 수신
- v5 control_health_request 응답
- v5 server_command 전송
- v5 agent_result 수신/검증/로그
- 운영 코드와 테스트/legacy 코드 분리
- v5.1 start_mapping auto_explore/save_map/rsync_map params 규칙 명시

다음 단계:
- 실제 클라이언트와 192.168.x.x:5000/5001/5002 연결 검증
- 클라이언트 ROS2/TurtleBot 실행 결과 agent_result 검증
- 데이터 전송/맵 파일 동기화 실기기 검증
```

## 로컬 mock 검증

클라이언트 담당자가 아직 준비되지 않았을 때는 아래 mock으로 서버 v5 흐름을 확인할 수 있습니다.

```bash
cd /home/admin_kyj/turtlebot_server
python3 tests/mock_external/mock_robot_command_client.py --bind-ip 127.0.0.1 --mode gateway --multi-port
```

서버 코드에서 테스트할 때만 `client_info`의 IP를 `127.0.0.1`로 대체하면 `client_heartbeat_request`, `server_command`, `agent_result` 왕복을 확인할 수 있습니다.

## 담당자 전달 문서

클라이언트 담당자에게는 아래 파일을 전달하면 됩니다.

```text
docs/FLEET_JSON_V051_PROMPT.md
docs/CLIENT_V05_HANDOFF_PROMPT.md
docs/CLIENT_INTERFACE_V05.md
docs/JSON_STRUCTURE_V05.md
```
