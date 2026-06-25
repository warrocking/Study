# 제어용 컴퓨터 작업 지시 프롬프트: JSON v4 기반 이미지 전송/표시/닫기 보고

당신은 TurtleBot 3대 협업 제어 시스템의 제어용 컴퓨터 UI/HMI 담당자입니다.

이번 작업의 목표는 기존 JSON v4 통신 규칙을 유지하면서, 서버 노트북이 가진 이미지 파일을 제어용 컴퓨터로 전송하고, 제어 UI에서 이미지를 표시한 뒤, 사용자가 이미지 창을 닫으면 로컬 파일을 삭제하고 서버에 그 결과를 JSON으로 보고하는 것입니다.

중요한 전제:

```text
이미지 파일 자체를 JSON에 넣지 않습니다.
JSON은 요청/응답/보고/로그용입니다.
실제 이미지 파일 전송은 rsync over SSH를 사용합니다.
```

서버 담당자가 제공하는 최종 계약 문서는 다음입니다.

```text
JSON_CONTRACT_V4.md
특히 18.1 Image Transfer Over Rsync 절을 기준으로 구현하세요.
```

## 전체 흐름

```text
1. 제어 UI가 서버로 image_request JSON을 보냅니다.
2. 서버가 서버 로컬 이미지 파일을 확인합니다.
3. 서버가 rsync over SSH로 제어용 컴퓨터에 이미지를 보냅니다.
4. 서버가 operator_response JSON을 제어 UI에 돌려줍니다.
5. 제어 UI는 응답의 file_transfer.control_path 이미지를 표시합니다.
6. 사용자가 이미지 창을 닫습니다.
7. 제어 UI는 로컬 이미지 파일을 삭제합니다.
8. 제어 UI가 image_view_closed JSON을 서버에 보냅니다.
9. 서버는 닫기/삭제 보고를 로그로 남깁니다.
```

여기서 이미지 창을 닫는 행동은 기존 TCP 연결을 닫는 신호가 아닙니다. JSON 요청 연결과 rsync 연결은 각각 요청/응답 또는 파일 복사 완료 후 종료됩니다. 창 닫기 후에는 새 JSON 요청으로 서버에 닫기/삭제 결과를 보고해야 합니다.

## 제어용 컴퓨터에서 준비할 것

서버가 제어용 컴퓨터로 rsync 전송을 해야 하므로, 제어용 컴퓨터는 SSH 접속을 받을 수 있어야 합니다.

Ubuntu 기준 준비:

```bash
sudo apt update
sudo apt install -y openssh-server rsync
sudo systemctl enable --now ssh
sudo systemctl status ssh
```

이미지를 받을 폴더를 준비하세요.

```bash
mkdir -p ~/openCV/cache/images
```

서버 담당자에게 아래 정보를 알려주세요.

```text
control_host: 제어용 컴퓨터 IP
control_user: 제어용 컴퓨터 Ubuntu 계정명
control_dir: 제어용 컴퓨터 이미지 저장 폴더
```

서버 담당자는 이 값을 `control_info.json`에 저장해서 관리합니다. 제어 UI는 특별한 사유가 없으면 image_request JSON에 IP/계정/폴더를 반복해서 넣지 않아도 됩니다.

예시:

```text
control_host = 192.168.3.59
control_user = ubuntu
control_dir = /home/ubuntu/openCV/cache/images
```

서버 담당자가 서버 노트북에서 아래 테스트를 할 수 있어야 합니다.

```bash
ssh ubuntu@192.168.3.59
rsync --version
```

## 공통 전송 규칙

기존 서버 통신 방식은 그대로 유지합니다.

```text
TCP
UTF-8
NDJSON
JSON 객체 1개를 한 줄로 전송
마지막에 반드시 \n 포함
요청 1개를 보내고 응답 1개를 읽습니다.
```

제어 UI는 서버와의 JSON 통신을 직접 구현해도 됩니다. 단, 아래 JSON 구조는 반드시 지켜야 합니다.

## 새로 추가된 action

```text
image_request
서버에 이미지 전송을 요청합니다.

image_view_closed
이미지를 표시했고, 사용자가 창을 닫았으며, 로컬 파일을 삭제했다는 것을 서버에 보고합니다.

file_cleanup_report
이미지 창 닫기와 파일 삭제 보고를 분리하고 싶을 때 사용합니다.
현재는 image_view_closed 안에 삭제 결과까지 넣는 방식을 우선 권장합니다.
```

## image_request 요청 JSON

제어 UI가 서버에 보내는 예시입니다.

```json
{
  "v": 4,
  "mt": "operator_request",
  "msg_id": "MSG_20260622_IMAGE_REQUEST_000001",
  "ts": "2026-06-22T10:00:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "auth": {
    "token": "team_demo_token"
  },
  "user": "operator_1",
  "command": {
    "command_id": "CMD_20260622_IMAGE_REQUEST_000001",
    "group_id": null,
    "job_id": null,
    "command_seq": null,
    "command_revision": 0,
    "action": "image_request",
    "target_scope": "single",
    "targets": ["tb3_1"],
    "params": {
      "server_path": "/home/admin_kyj/openCV/server/sync/to_control/images/tb3_1_latest_map.png",
      "image_type": "latest_map",
      "delete_after_view": true
    },
    "expects": {
      "response_type": "sync",
      "status_followup": false
    },
    "timeout_sec": 10.0
  },
  "ui_context": {
    "client": "control_ui",
    "screen": "image_view",
    "button": "image_request"
  }
}
```

필드 설명:

```text
action:
반드시 image_request

target_scope:
우선 single 사용

targets:
이미지를 요청할 로봇 ID
예: ["tb3_1"]

server_path:
서버 노트북에 있는 이미지 파일 절대경로
서버 담당자가 알려준 경로를 사용하세요.

transfer.method:
생략 가능. 서버는 `control_info.json`의 기본값을 사용합니다.

transfer.direction:
생략 가능. 서버는 `control_info.json`의 기본값을 사용합니다.

transfer.control_host:
생략 가능. 서버는 `control_info.json`의 control_ui.ip를 사용합니다.

transfer.control_user:
생략 가능. 서버는 `control_info.json`의 control_ui.user를 사용합니다.

transfer.control_dir:
생략 가능. 서버는 `control_info.json`의 control_ui.paths.image_cache_dir를 사용합니다.
```

## image_request 서버 응답에서 읽을 필드

서버 응답 예시:

```json
{
  "v": 4,
  "mt": "operator_response",
  "source": "fleet_server",
  "dest": "control_ui",
  "schema": "fleet_json_v0.4",
  "ok": true,
  "code": "R_FILE_SYNC_REPORTED",
  "message": "image transferred to control computer",
  "file_transfer": {
    "session_id": "SYNC_20260622_IMAGE_TB3_1_000001",
    "method": "rsync_over_ssh",
    "direction": "server_push",
    "source_path": "/home/admin_kyj/openCV/server/sync/to_control/images/tb3_1_latest_map.png",
    "control_host": "192.168.3.59",
    "control_user": "ubuntu",
    "control_path": "/home/ubuntu/openCV/cache/images/tb3_1_latest_map.png",
    "delete_after_view": true,
    "ok": true
  }
}
```

제어 UI는 최소한 아래 필드를 읽어야 합니다.

```text
ok
code
message
file_transfer.session_id
file_transfer.ok
file_transfer.control_path
file_transfer.delete_after_view
```

성공 조건:

```text
ok == true
code == "R_FILE_SYNC_REPORTED"
file_transfer.ok == true
file_transfer.control_path 파일이 제어용 컴퓨터에 존재함
```

성공하면 `file_transfer.control_path`에 있는 이미지를 제어 UI에서 표시하세요.

실패 조건:

```text
ok == false
code가 E_로 시작
```

이 경우 UI에는 서버 응답의 `message`를 표시하고, 이미지를 열지 마세요.

## 이미지 창 닫기 처리

사용자가 이미지 창을 닫으면 제어 UI는 아래 순서로 처리하세요.

```text
1. 이미지 창을 닫습니다.
2. file_transfer.delete_after_view == true이면 로컬 이미지 파일을 삭제합니다.
3. 삭제 성공 여부를 local_file_deleted에 기록합니다.
4. image_view_closed JSON을 서버에 보냅니다.
```

## image_view_closed 보고 JSON

```json
{
  "v": 4,
  "mt": "operator_request",
  "msg_id": "MSG_20260622_IMAGE_CLOSED_000001",
  "ts": "2026-06-22T10:01:00+09:00",
  "source": "control_ui",
  "dest": "fleet_server",
  "schema": "fleet_json_v0.4",
  "auth": {
    "token": "team_demo_token"
  },
  "user": "operator_1",
  "command": {
    "command_id": "CMD_20260622_IMAGE_CLOSED_000001",
    "group_id": null,
    "job_id": null,
    "command_seq": null,
    "command_revision": 0,
    "action": "image_view_closed",
    "target_scope": "single",
    "targets": ["tb3_1"],
    "params": {
      "session_id": "SYNC_20260622_IMAGE_TB3_1_000001",
      "displayed": true,
      "closed_by": "user",
      "local_file_deleted": true,
      "local_path": "/home/ubuntu/openCV/cache/images/tb3_1_latest_map.png"
    },
    "expects": {
      "response_type": "sync",
      "status_followup": false
    },
    "timeout_sec": 3.0
  },
  "ui_context": {
    "client": "control_ui",
    "screen": "image_view",
    "button": "image_view_closed"
  }
}
```

여기서 `session_id`는 반드시 image_request 서버 응답의 `file_transfer.session_id` 값을 그대로 사용하세요.

## 서버가 남기는 로그

서버 담당자는 아래 로그를 확인합니다.

```text
logs/server/operator_requests/latest_operator_request.json
logs/server/operator_responses/latest_operator_response.json
logs/server/file_transfers/latest_image_request.json
logs/server/file_transfers/latest_image_view_closed.json
logs/server/file_transfers/latest_file_cleanup_report.json
```

## 제어 담당자가 서버 담당자에게 전달할 확인 자료

코드 전체를 전달할 필요는 없습니다. 대신 아래를 전달해주세요.

```text
1. 실제로 보낸 image_request JSON 원문
2. 서버에서 받은 operator_response JSON 원문
3. 이미지가 제어용 컴퓨터의 어느 경로에 저장됐는지
4. 이미지 창을 닫은 뒤 로컬 파일을 삭제했는지
5. 실제로 보낸 image_view_closed JSON 원문
6. 제어용 컴퓨터 IP, 계정명, 이미지 저장 폴더
```

## 1차 성공 기준

```text
1. 기존 status_request가 성공한다.
2. image_request를 보내면 서버 응답 code가 R_FILE_SYNC_REPORTED이다.
3. 제어용 컴퓨터의 control_path에 이미지 파일이 생긴다.
4. 제어 UI가 해당 이미지를 표시한다.
5. 사용자가 이미지 창을 닫으면 제어 UI가 로컬 이미지 파일을 삭제한다.
6. image_view_closed를 서버로 보낸다.
7. 서버에 latest_image_view_closed.json 로그가 생긴다.
```

## 주의사항

```text
이미지를 JSON에 base64로 넣지 마세요.
서버 경로를 임의로 추측하지 말고 서버 담당자가 제공한 server_path를 사용하세요.
rsync는 제어 UI가 직접 실행하지 않습니다. 현재 규칙에서는 서버가 제어 컴퓨터로 server_push합니다.
제어 컴퓨터에는 SSH 서버가 켜져 있어야 합니다.
이미지 창 닫기와 JSON TCP 연결 종료를 같은 의미로 처리하지 마세요.
서버 응답 ok=false이면 이미지를 열지 마세요.
로컬 파일 삭제 실패 시 local_file_deleted=false로 보고하세요.
```

최종 목표는 제어 UI가 JSON으로 이미지 전송을 요청하고, 서버가 rsync over SSH로 이미지를 제어용 컴퓨터에 전달하며, 제어 UI가 이미지를 표시한 뒤 창 닫기와 로컬 삭제 결과를 다시 JSON으로 서버에 보고하는 것입니다.
