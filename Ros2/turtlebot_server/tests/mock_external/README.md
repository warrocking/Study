# Mock External Tools

이 폴더는 운영 서버 코드가 아닙니다.

Control UI 또는 Robot Command Client 역할을 임시로 흉내 내는 테스트 도구만 둡니다.

## Robot Command Client mock

서버 v0.5 연결 확인용 mock입니다.

```bash
cd /home/admin_kyj/turtlebot_server
python3 tests/mock_external/mock_robot_command_client.py --bind-ip 127.0.0.1 --mode gateway --multi-port
```

지원 메시지:

```text
client_heartbeat_request -> client_heartbeat_response
server_command -> agent_result
```

실제 TurtleBot/ROS2 제어는 하지 않습니다. JSON 연결, 필드 매칭, 로그 생성 확인용입니다.
