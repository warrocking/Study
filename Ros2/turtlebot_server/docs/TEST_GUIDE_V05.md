# Test Guide v0.5.1

컴파일 확인:

```bash
cd /home/admin_kyj/turtlebot_server
bash program/scripts/compile_check.sh
```

서버 실행:

```bash
cd /home/admin_kyj/turtlebot_server/program/code
python3 server_manager.py
```

포트 확인:

```bash
bash program/scripts/check_control_health_port.sh
bash program/scripts/check_client_health_port.sh
bash program/scripts/check_client_command_port.sh
bash program/scripts/check_client_data_port.sh
```

클라이언트 담당자가 준비되지 않았을 때 로컬 mock:

```bash
cd /home/admin_kyj/turtlebot_server
python3 tests/mock_external/mock_robot_command_client.py --bind-ip 127.0.0.1 --mode gateway --multi-port
```

서버 v5.1 흐름 성공 기준:

```text
client_health/latest_client_heartbeat.json 생성
commands/latest_server_command.json 생성
results/latest_agent_result.json 생성
operator_responses/latest_operator_response.json 생성
```
