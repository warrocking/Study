# Server Code Role v0.5.1

```text
server_manager.py
    서버 실행 진입점

config_loader.py
    설정 JSON 로드와 디렉토리 생성

fleet_server_main.py
    현재 실제 TCP 서버 및 라우팅 엔진

fleet_protocol.py
    현재 JSON/NDJSON 유틸과 검증 함수
```

나머지 manager/router/supervisor 파일은 현재 FleetServer가 직접 수행하는 책임을 문서화하고, 이후 분리할 수 있도록 둔 경계 클래스입니다.

현재 실행 경로:

```text
server_manager.py
  -> FleetServer.run()
  -> control_health_request / operator_request / control_command_request / control_data_request 수신
  -> client_heartbeat_request 또는 server_command 전송
  -> client_heartbeat_response 또는 agent_result 수신
  -> operator_response/control_health_response 반환
```
