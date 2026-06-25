# 제어용 노트북 UI/HMI v4 기본 작업 지시 프롬프트

당신은 TurtleBot 3대 협업 제어 시스템의 제어용 노트북 UI/HMI 담당자입니다.

이 문서는 기본 제어 버튼과 서버 상태 표시를 위한 최신 v4 기준 프롬프트입니다. 이미지 전송/이미지 창 닫기 보고는 `CONTROL_UI_FILE_TRANSFER_PROMPT.md`를 별도로 따르세요.

## 1. 목표

UI 버튼을 누르면 제어 UI가 Fleet Server로 v4 `operator_request` JSON을 보내고, 서버가 `operator_response` JSON을 반환하면 UI가 그 결과에 따라 로봇 상태/성공/실패/오류 메시지를 갱신합니다.

```text
Control UI
-> operator_request
-> Fleet Server
-> server_command
-> Robot Agent Client
-> agent_result
-> Fleet Server
-> operator_response
-> Control UI
```

UI는 TurtleBot을 직접 제어하지 않습니다. ROS2 `/cmd_vel` publish는 Robot Agent Client가 담당합니다.

## 2. 서버 정보

```text
server_ip = 192.168.3.61
server_port = 4000
protocol = TCP + UTF-8 + NDJSON
schema = fleet_json_v0.4
```

JSON은 반드시 한 줄 compact JSON으로 보내고 마지막에 `\n`을 붙여야 합니다.

## 3. 제공 파일

서버 담당자가 제공할 수 있는 기본 파일은 다음입니다.

```text
control_laptop_client.py
control_client_config.json
JSON_CONTRACT_V4.md
CONTROL_UI_FILE_TRANSFER_PROMPT.md
```

UI/UX 디자인은 자유롭게 구현해도 됩니다. 다만 서버와의 JSON 계약은 임의로 바꾸지 마세요.

## 4. control_client_config.json

```json
{
  "server_ip": "192.168.3.61",
  "server_port": 4000,
  "timeout": 40.0,
  "auth_token": "team_demo_token",
  "user": "operator_1",
  "default_target": "tb3_3"
}
```

이미지 전송을 함께 테스트할 경우 `timeout`은 40초 이상을 권장합니다.

## 5. 통신 테스트

UI를 만들기 전에 터미널에서 먼저 테스트하세요.

```bash
python3 control_laptop_client.py
```

메뉴에서 `status_request`를 실행했을 때 서버 응답에 아래 값이 있으면 제어 UI와 Fleet Server 통신은 성공입니다.

```json
{
  "ok": true,
  "code": "R_STATUS"
}
```

서버 로그에는 아래 파일이 새로 생겨야 합니다.

```text
logs/server/operator_requests/latest_operator_request.json
logs/server/operator_responses/latest_operator_response.json
```

## 6. UI에서 사용할 기본 코드 예시

```python
from control_laptop_client import ControlServerClient

client = ControlServerClient("192.168.3.61", 4000, timeout=40.0)

selected_robot = "tb3_3"

def on_forward_button():
    response = client.move_forward(selected_robot)
    update_ui_from_response(response)

def on_backward_button():
    response = client.move_backward(selected_robot)
    update_ui_from_response(response)

def on_turn_left_button():
    response = client.turn_left(selected_robot)
    update_ui_from_response(response)

def on_turn_right_button():
    response = client.turn_right(selected_robot)
    update_ui_from_response(response)

def on_stop_button():
    response = client.stop(selected_robot)
    update_ui_from_response(response)

def on_all_stop_button():
    response = client.all_stop()
    update_ui_from_response(response)

def on_status_button():
    response = client.status_request()
    update_ui_from_response(response)
```

`client.stop()`은 UI 편의용 이름이며, 전송 전 v4 표준 action인 `robot_stop`으로 정규화됩니다.

## 7. 필수 UI 기능

UI에는 로봇 선택 기능이 있어야 합니다.

```text
tb3_1
tb3_2
tb3_3
```

현재 1차 실제 연결 테스트에서는 `tb3_3`만 활성 로봇으로 사용합니다. UI 기본 선택값은 `tb3_3`으로 두고, 서버 담당자가 다른 로봇을 활성화하기 전까지 실제 이동/정지 테스트는 `tb3_3` 대상으로 진행하세요.

버튼은 최소한 아래 항목을 구현하세요.

```text
전진
후진
좌회전
우회전
정지
ALL STOP
상태 확인
```

ALL STOP 버튼은 항상 잘 보이는 위치에 배치하세요.

## 8. 서버 응답에서 표시할 필드

UI는 `operator_response`의 아래 필드를 우선 표시하세요.

```text
ok
code
message
command.action
command.normalized_action
command.resolved_targets
results
err
ui_hint.summary
ui_hint.severity
```

성공 응답의 대표 코드는 다음입니다.

```text
R_STATUS
R_DONE
R_STOPPED
R_FILE_SYNC_REPORTED
```

오류 응답은 `ok=false`이거나 `code`가 `E_`로 시작합니다.

## 9. Robot Agent 연결 상태 해석

Fleet Server와 제어 UI 통신이 성공해도 Robot Agent Client가 꺼져 있으면 로봇 명령은 실패할 수 있습니다.

대표 오류:

```text
E_AGENT_DISCONNECTED
E_TIMEOUT
E_BAD_REQUEST
E_STATE_MISMATCH
```

이 경우 UI는 아래처럼 구분해서 표시하세요.

```text
서버 연결 성공 / Robot Agent 연결 실패
```

## 10. 성공 기준

1차 UI-서버 연동 성공 기준:

```text
1. status_request 실행 시 R_STATUS가 나온다.
2. 서버 터미널에 CONTROL CONNECT / CONTROL CLOSE가 찍힌다.
3. logs/server/operator_requests/에 요청 로그가 생성된다.
4. logs/server/operator_responses/에 응답 로그가 생성된다.
5. UI가 response.ok, response.code, response.message를 보고 화면 상태를 갱신한다.
```

Robot Agent까지 켜진 상태의 추가 성공 기준:

```text
1. move_forward 또는 robot_stop 실행 시 서버가 server_command 로그를 남긴다.
2. Robot Agent가 agent_result를 반환한다.
3. logs/server/commands/latest_server_command.json이 생성된다.
4. logs/server/results/latest_agent_result.json이 생성된다.
5. operator_response.results.tb3_x.ok 값이 UI에 반영된다.
```

## 11. 이미지 전송 기능

이미지 전송은 별도 문서 기준으로 구현하세요.

```text
CONTROL_UI_FILE_TRANSFER_PROMPT.md
```

이미지 파일은 JSON에 넣지 않습니다. JSON은 요청/응답/닫기 보고에만 쓰고, 실제 파일은 서버가 rsync over SSH로 제어 컴퓨터에 전송합니다.

## 12. 주의사항

```text
UI에서 ROS2 /cmd_vel을 직접 publish하지 마세요.
UI에서 TurtleBot을 직접 제어하지 마세요.
UI는 반드시 Fleet Server에 operator_request를 보내야 합니다.
서버 응답을 임의로 성공 처리하지 마세요.
ok=false이면 실패 상태로 표시하세요.
code가 E_로 시작하면 오류로 표시하세요.
pretty JSON 여러 줄을 그대로 TCP로 보내지 마세요.
마지막 개행 \n 없이 보내지 마세요.
```

최종 목표는 버튼 클릭 -> 서버 JSON 로그 -> Robot Agent 결과 -> UI 상태 갱신의 흐름을 안정적으로 유지하는 것입니다.
