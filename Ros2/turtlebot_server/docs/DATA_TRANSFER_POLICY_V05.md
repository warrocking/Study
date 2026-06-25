# Data Transfer Policy v0.5.1

데이터 전송의 실제 실행 주체는 서버입니다.

```text
Server -> Control UI: rsync push
Client -> Server: server rsync pull 또는 local_path copy
Server -> Client: server rsync push, 확장 예정
```

SSH 포트는 JSON 통신 포트와 다릅니다. 기본 SSH 포트는 22입니다.

## Control UI 맵 이미지 표시

제어 UI가 맵 이미지를 보고 싶으면 4002 data_control 포트로 `control_data_request`를 보냅니다.

```text
data_type=image
data_type=map
```

둘 다 서버의 이미지 요청 흐름으로 처리됩니다. 서버는 `control_info.json`의 SSH/경로 설정을 사용해 제어 컴퓨터의 이미지 캐시 디렉토리로 파일을 보냅니다.

## Client 맵 파일 서버 안착

클라이언트 맵 파일을 서버로 가져오는 흐름은 아래와 같습니다.

```text
1. Control UI -> Fleet Server: rsync_map
2. Fleet Server -> Robot Command Client 5001: server_command(op=rsync_map)
3. Robot Command Client -> Fleet Server: agent_result(ok=true)
4. Fleet Server -> Robot Command Client 5002: client_data_prepare_request
5. Robot Command Client -> Fleet Server: client_data_prepare_response
6. Fleet Server가 map/image/yaml 파일을 data/map/incoming 아래에 저장
7. Fleet Server가 data/images/latest/tb1_latest_map.png를 갱신
```

`client_data_prepare_response.files`에는 `local_path` 또는 `remote_path`가 필요합니다.

```text
local_path: 서버와 클라이언트가 같은 파일시스템을 볼 때 사용
remote_path: 실제 분리 장비에서 SSH/rsync로 가져올 때 사용
```

실기기 분리 환경에서는 `remote_path` + `client_info.json`의 SSH 설정을 사용하는 구성이 권장됩니다.
