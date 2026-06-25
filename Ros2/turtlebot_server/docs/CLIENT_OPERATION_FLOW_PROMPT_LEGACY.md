# TurtleBot Fleet Server v4 - Robot Agent Client 전체 규칙과 구동방식 프롬프트

당신은 TurtleBot 3대 협업 제어 시스템의 Robot Agent 클라이언트 담당자입니다.

이 문서는 JSON 필드 상세 규칙이 아니라, 전체 시스템이 어떤 구조로 구동되고 Robot Agent 클라이언트가 어떤 역할을 해야 하는지 설명하는 운영/구동 방식 프롬프트입니다. JSON 상세 필드는 별도 문서 `CLIENT_JSON_RULES_PROMPT.md`를 기준으로 하세요.

## 1. 전체 시스템 구조

시스템은 아래 3단 구조입니다.

```text
Control UI / HMI
  ↓ operator_request JSON
Fleet Server
  ↓ server_command JSON
Robot Agent Client
  ↓ ROS2 publish
TurtleBot3
```

응답 흐름은 반대입니다.

```text
TurtleBot3 실행 결과
  ↑ agent_result JSON
Robot Agent Client
  ↑ operator_response JSON으로 집계됨
Fleet Server
  ↑ UI 상태 갱신
Control UI / HMI
```

Control UI는 Robot Agent에 직접 명령하지 않습니다. Robot Agent도 Control UI와 직접 통신하지 않습니다.

```text
Control UI <-> Fleet Server <-> Robot Agent Client
```

## 2. 담당 역할 분리

### Control UI 담당

```text
사용자 버튼 입력 처리
operator_request JSON 생성
Fleet Server 192.168.3.61:4000으로 전송
operator_response를 보고 화면 상태 갱신
```

### Fleet Server 담당

```text
Control UI 요청 수신
JSON 검증
action policy 적용
target robot 결정
Robot Agent Client로 server_command 전송
agent_result 수신
최종 operator_response 생성
로그 저장
```

### Robot Agent Client 담당

```text
공통 TCP 포트 listen
Fleet Server의 server_command 수신
command.robot_id 확인
command.op와 command.params 해석
ROS2 /cmd_vel publish 또는 상태 작업 수행
agent_result JSON 응답
heartbeat_request 응답
state_report 제공
```

## 3. 네트워크 구동 방식

Fleet Server는 Control UI 쪽에서는 TCP 서버입니다.

```text
Control UI -> Fleet Server
192.168.3.61:4000
```

하지만 Robot Agent Client 쪽에서는 Fleet Server가 TCP 클라이언트처럼 접속합니다.

```text
Fleet Server -> Robot Agent Client
192.168.3.63:4000
```

따라서 Robot Agent Client는 아래 포트에서 먼저 대기하고 있어야 합니다.

```text
Robot Command Client: 0.0.0.0:4000 listen
```

서버는 TurtleBot별 IP를 관리하지 않습니다. 서버는 공통 Robot Command Client로 JSON을 보내고, 클라이언트가 `command.robot_id`를 읽어서 해당 TurtleBot에 명령을 내려야 합니다.

서버가 접속할 수 있도록 클라이언트 컴퓨터의 방화벽, IP, 포트가 열려 있어야 합니다.

## 4. 현재 서버 client_info 기준

현재 Fleet Server는 아래 Robot Command Client를 바라봅니다.

```text
client id: robot_command_client
ip: 192.168.3.63
port: 4000
```

서버가 JSON 안에 넣어 보내는 robot_id는 아래입니다.

```text
tb3_3
```

현재 1차 실제 연결 테스트에서는 TurtleBot 1대만 우선 연결하므로 `tb3_3`만 활성 로봇으로 사용합니다. `tb3_1`, `tb3_2`는 서버의 `client_info.json`에서 비활성화되어 있습니다.

클라이언트 컴퓨터의 실제 IP가 다르면 서버 담당자에게 알려주세요. 서버의 `client_info.json` 수정이 필요합니다.

## 5. TCP 연결 수명

명령 하나는 기본적으로 짧은 TCP 요청/응답입니다.

```text
1. Fleet Server가 Robot Agent Client 포트로 TCP 연결
2. server_command JSON 한 줄 전송
3. Robot Agent Client가 command.robot_id를 읽고 해당 TurtleBot 명령 실행
4. agent_result JSON 한 줄 응답
5. TCP 연결 종료
```

heartbeat도 짧은 요청/응답입니다.

```text
1. Fleet Server가 Robot Agent Client 포트로 TCP 연결
2. heartbeat_request JSON 한 줄 전송
3. Robot Agent Client가 heartbeat_response JSON 한 줄 응답
4. include_state_report=true이면 state_report JSON 한 줄 추가 응답
5. TCP 연결 종료
```

중요:

```text
연결을 오래 유지하는 방식이 아닙니다.
명령마다 연결되고 응답 후 종료되는 구조로 구현하세요.
```

## 6. 구동 순서

권장 구동 순서는 아래와 같습니다.

```text
1. Robot Agent Client 컴퓨터 네트워크 확인
2. tb3_1/tb3_2/tb3_3 Agent 포트 listen 시작
3. ROS2 환경 설정 확인
4. Fleet Server 실행
5. Control UI 실행
6. status_request로 서버 상태 확인
7. heartbeat 또는 move/stop 테스트
8. 실제 TurtleBot 제어 테스트
```

Robot Agent Client가 먼저 떠 있지 않으면 서버는 해당 로봇을 `DISCONNECTED` 또는 `E_AGENT_DISCONNECTED`로 판단합니다.

## 7. Robot Agent Client 실행 형태

구현 방식은 자유입니다.

가능한 형태:

```text
1. 하나의 Python 프로세스에서 4000 포트를 listen
2. 받은 JSON의 command.robot_id로 tb3_1/tb3_2/tb3_3 분기
3. 내부 코드나 별도 설정에서 TurtleBot별 실제 접속/ROS2 정보를 관리
```

단, 어떤 방식을 쓰더라도 서버에서 보는 포트는 맞아야 합니다.

```text
robot_command_client -> 4000
```

## 8. ROS2 동작 방식

Robot Agent Client는 서버가 보낸 `server_command.command.ros`와 `params`를 기준으로 ROS2 명령을 수행합니다.

서버가 보내는 ROS 정보:

```text
command.ros.domain_id
command.ros.namespace
command.ros.topic
```

서버가 보내는 이동 파라미터:

```text
params.lx
params.az
params.dur
params.hz
params.stop
```

기본 해석:

```text
lx: linear.x
az: angular.z
dur: publish 유지 시간
hz: 초당 publish 횟수
stop: 완료 후 0 속도 publish 여부
```

권장 동작:

```text
1. params.lx, params.az로 Twist 생성
2. dur 동안 hz 주기로 /cmd_vel publish
3. params.stop=true이면 마지막에 Twist 0을 1회 이상 publish
4. 결과를 agent_result로 응답
```

서버가 보낸 `params`를 우선 사용하고, 클라이언트가 임의로 속도나 시간을 키우지 마세요.

## 9. 주요 op 처리 방향

### move_forward / move_backward / turn_left / turn_right / custom_move

```text
params 기반으로 /cmd_vel publish
성공 시 R_DONE
실패 시 E_ROS_PUBLISH_FAILED 또는 E_TIMEOUT
```

### robot_stop / emergency_stop

```text
즉시 Twist 0 publish
성공 시 R_STOPPED
실패 시 E_ROS_PUBLISH_FAILED
```

### status_request / robot_state_request / job_status_request / ping

```text
로봇 상태를 agent_result로 응답
ping은 R_PONG 권장
상태 조회는 R_STATUS 권장
```

### start_mapping / stop_mapping / save_map / rsync_map / nav_goal

```text
1차 연동에서는 실제 구현이 어렵다면 ok=false로 명확히 응답
구현한 경우에는 실제 시작/완료/실패 상태를 code와 state에 반영
무응답으로 두지 않기
```

## 10. 상태 관리 원칙

Robot Agent Client는 내부적으로 최소한 아래 상태를 관리하는 것을 권장합니다.

```text
connection_state
operating_mode
robot_state
job_state
accept_state
ui_mode
last_command_id
last_op
last_error
```

상태는 `agent_result.state`, `heartbeat_response.state`, `state_report.state`에 반영합니다.

예:

```text
명령 대기 중:
robot_state=IDLE
job_state=NONE
ui_mode=READY

이동 실행 중:
robot_state=MOVING
job_state=RUNNING
ui_mode=BUSY

명령 완료:
robot_state=IDLE
job_state=DONE
ui_mode=READY

오류:
robot_state=ERROR
job_state=FAILED
ui_mode=ERROR
```

## 11. 실패 처리 원칙

Robot Agent Client는 실패 상황에서도 반드시 JSON 응답을 보내야 합니다.

금지:

```text
요청을 받고 아무 응답 없이 연결 종료
예외 발생 후 프로세스 종료
잘못된 JSON을 응답
pretty JSON 여러 줄 응답
ref, command_id, op를 누락
```

권장:

```text
ok=false
적절한 E_ 코드
message에 사람이 읽을 수 있는 설명
err 배열에 detail 포함
state에 ERROR 또는 REJECTED 반영
```

Fleet Server는 응답을 받지 못하면 `E_TIMEOUT` 또는 `E_AGENT_DISCONNECTED`로 처리합니다.

## 12. 서버 로그 기준 성공 확인

서버 담당자는 아래 로그를 확인합니다.

```text
logs/server/commands/
logs/server/results/
logs/server/operator_responses/
logs/server/heartbeats/
logs/server/state_reports/
```

정상 명령 흐름이면:

```text
logs/server/commands/latest_server_command.json 생성
logs/server/results/latest_agent_result.json 생성
operator_response의 results.tb3_x.ok=true
```

heartbeat 정상 흐름이면:

```text
logs/server/heartbeats/latest_heartbeat_request.json 생성
logs/server/heartbeats/latest_heartbeat_response.json 생성
include_state_report=true일 때 logs/server/state_reports/ 생성
```

## 13. 테스트 단계

### 1차: 포트 연결 확인

서버 노트북에서 클라이언트 포트에 연결 가능한지 확인합니다.

```bash
nc -vz 192.168.3.63 4000
```

성공 기준:

```text
succeeded 또는 open
```

### 2차: mock 또는 실제 Agent 응답 확인

서버가 `server_command`를 보냈을 때 클라이언트가 `agent_result`를 반환해야 합니다.

성공 기준:

```text
server_command 로그 생성
agent_result 로그 생성
operator_response ok=true
```

### 3차: ROS2 publish 확인

Robot Agent Client 쪽에서 실제 topic publish가 되는지 확인합니다.

예:

```bash
ros2 topic echo /tb3_1/cmd_vel
```

또는 실제 TurtleBot 움직임/정지 반응으로 확인합니다.

### 4차: stop 안전 확인

`robot_stop` 또는 `emergency_stop` 수신 시 0 속도 publish가 즉시 되는지 확인합니다.

성공 기준:

```text
Twist linear.x=0.0
Twist angular.z=0.0
agent_result code=R_STOPPED
```

## 14. mock_robot_agent 참고

서버 디렉토리에는 통신 테스트용 mock agent가 있습니다.

```text
mock_robot_agent.py
```

이 파일은 실제 ROS2 제어 대신 JSON 통신 구조를 검증하기 위한 참고 구현입니다.

클라이언트 담당자는 mock을 그대로 최종 코드로 쓰라는 뜻이 아니라, 아래 흐름을 참고하면 됩니다.

```text
TCP listen
JSON 한 줄 수신
mt 분기
server_command면 agent_result 응답
heartbeat_request면 heartbeat_response/state_report 응답
```

## 15. 이미지 전송과 Robot Agent의 관계

현재 이미지 전송은 Control UI와 Fleet Server 사이의 기능입니다.

```text
Control UI -> image_request -> Fleet Server
Fleet Server -> rsync over SSH -> Control UI
```

Robot Agent Client는 기본적으로 이미지 창 표시 기능을 담당하지 않습니다.

단, 나중에 실제 TurtleBot에서 맵 저장, 지도 파일 생성, 파일 동기화가 필요해지면 아래 op가 연관될 수 있습니다.

```text
save_map
rsync_map
file_sync_report
```

이 부분은 1차 연결 이후 서버 담당자와 별도로 합의해서 확장하세요.

## 16. 전체 성공 기준

Robot Agent Client 1차 성공 기준:

```text
1. Robot Command Client 포트 4000이 열려 있다.
2. Fleet Server가 server_command를 보낼 수 있다.
3. Robot Agent Client가 agent_result를 반환한다.
4. Fleet Server 로그에 commands와 results가 생성된다.
5. Control UI가 operator_response에서 ok/code/results를 확인할 수 있다.
6. robot_stop 또는 emergency_stop이 0 속도 publish로 처리된다.
7. 연결 실패, 실행 실패, 검증 실패도 ok=false JSON으로 응답한다.
```

최종 성공 기준:

```text
Control UI 버튼 클릭
-> Fleet Server operator_request 수신
-> Robot Agent Client server_command 수신
-> ROS2 /cmd_vel publish
-> agent_result 응답
-> Fleet Server operator_response 생성
-> Control UI 상태 갱신
```

## 17. 작업 중 합의가 필요한 항목

아래 항목은 임의로 바꾸지 말고 서버 담당자와 합의하세요.

```text
Robot Command Client IP
Robot Command Client port
robot_id 이름
ROS_DOMAIN_ID
/cmd_vel topic
op 이름
result code 이름
state enum 값
map/save/nav 관련 확장 방식
```

특히 서버의 `client_info.json`과 클라이언트 실행 설정은 반드시 서로 맞아야 합니다.
