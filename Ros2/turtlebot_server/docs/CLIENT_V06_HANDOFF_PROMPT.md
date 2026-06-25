# Robot Command Client v0.6 작업 지시 프롬프트

> **대상:** Robot Command Client 개발자
> **서버 IP:** 192.168.3.61 / 클라이언트 IP: 192.168.3.63
>
> 이 문서는 Fleet JSON v0.6 규약에 맞춰 클라이언트가 구현/수정해야 할 사항을 정리합니다.
> 전체 규약은 `docs/JSON_CONTRACT_V06.md` 참고.

---

## 1. v0.6 클라이언트 추가 구현 목록

| # | 항목 | 우선순위 |
|---|------|---------|
| 1 | 포트 4003으로 mapping_complete_notification 전송 | **필수** |
| 2 | 맵 디렉토리 이름 규칙 준수 (YYYYMMDD_HHMMSS_robot_method_N) | **필수** |
| 3 | 발신 JSON v=6, schema=fleet_json_v0.6 전환 | 권장 |
| 4 | start_mapping 성공 시 operating_mode=MAPPING 보고 | 기존 필수 |
| 5 | save_map / rsync_map / stop_mapping op 처리 | 기존 필수 |

---

## 2. 포트 구성

| 포트 | 역할 | 방향 |
|------|------|------|
| 5000 | Client Health | 서버가 connect → 클라이언트가 listen |
| 5001 | Client Command | 서버가 connect → 클라이언트가 listen |
| 5002 | Client Data | 서버가 connect → 클라이언트가 listen |
| **4003** | **Client Event** | **클라이언트가 서버(192.168.3.61)에 connect** |

---

## 3. 수신 명령 처리 (포트 5001)

서버로부터 `server_command.command.op`로 명령을 받습니다.

### 3-1. start_mapping

```json
{
  "mt": "server_command",
  "command": {
    "op": "start_mapping",
    "robot_id": "14",
    "ros": { "domain_id": 14, "namespace": "/tb1" },
    "params": { "mode": "mapping", "explore": true },
    "timeout_sec": 40.0
  }
}
```

처리:
1. ROS2 SLAM 노드 실행 (예: cartographer)
2. `explore:true`이면 자율 탐색 노드도 함께 실행
3. 성공 시 즉시 `agent_result` 반환

성공 응답:
```json
{
  "ok": true, "code": "R_STARTED",
  "state": {
    "operating_mode": "MAPPING",
    "robot_state": "MAPPING",
    "job_state": "RUNNING"
  }
}
```

> `operating_mode=MAPPING` 필수. 빠뜨리면 서버가 상태 추적 실패.

### 3-2. save_map

```json
{ "command": { "op": "save_map", "params": { "map_name": "lab_map_01" } } }
```

처리:
1. ROS2 map_saver 실행 (`ros2 run nav2_map_server map_saver_cli`)
2. 맵 디렉토리 생성 (이름 규칙은 섹션 4 참고)
3. map.pgm + map.yaml 디렉토리 안에 저장

성공 응답:
```json
{
  "ok": true, "code": "R_MAP_LOCAL_SAVED",
  "state": { "operating_mode": "MAPPING" }
}
```

> **MAPPING 모드 유지** — save_map 이후에도 SLAM은 계속 실행 중.

### 3-3. rsync_map (수동 방식, 서버가 pull 요청하는 경우)

서버가 rsync pull로 파일을 가져갑니다. 클라이언트는 SSH 서버 데몬(sshd)만 실행 중이면 됩니다.

성공 응답:
```json
{
  "ok": true, "code": "R_FILE_SYNC_REPORTED",
  "state": { "operating_mode": "MAPPING" }
}
```

### 3-4. stop_mapping

```json
{ "command": { "op": "stop_mapping" } }
```

처리:
1. SLAM 노드 종료
2. 자율 탐색 노드 종료 (실행 중이었다면)

성공 응답:
```json
{
  "ok": true, "code": "R_DONE",
  "state": {
    "operating_mode": "MANUAL",
    "robot_state": "IDLE",
    "job_state": "DONE"
  }
}
```

---

## 4. 맵 디렉토리 이름 규칙

```
YYYYMMDD_HHMMSS_turtlebotName_saveMethod_saveNumber
```

| 필드 | 설명 | 예시 |
|------|------|------|
| YYYYMMDD_HHMMSS | 맵핑 **시작** 시각 | 20260624_164951 |
| turtlebotName | 로봇 별칭 | tb1 |
| saveMethod | 저장 방식 | autoSave / stop / emergency |
| saveNumber | 이 클라이언트의 누적 맵 저장 횟수 | 1, 2, 3, ... |

예: `20260624_164951_tb1_autoSave_1`

```python
import os, time, datetime

class MapDirNamer:
    def __init__(self, robot_alias: str, base_dir: str):
        self.robot_alias = robot_alias
        self.base_dir = base_dir
        self._count = 0

    def start_mapping(self):
        self._mapping_start_ts = datetime.datetime.now()

    def make_dir_name(self, save_method: str) -> str:
        self._count += 1
        ts = self._mapping_start_ts.strftime("%Y%m%d_%H%M%S")
        return f"{ts}_{self.robot_alias}_{save_method}_{self._count}"

    def create_dir(self, save_method: str) -> str:
        dir_name = self.make_dir_name(save_method)
        path = os.path.join(self.base_dir, dir_name)
        os.makedirs(path, exist_ok=True)
        return path, dir_name
```

---

## 5. 맵핑 완료 알림 (포트 4003) — v0.6 핵심 신규

SLAM + 맵 저장 완료 후 서버 포트 4003에 TCP 연결 → JSON 전송 → ACK 수신 → 연결 종료.

```python
import socket, json, datetime, time

SERVER_IP = "192.168.3.61"
CLIENT_EVENT_PORT = 4003

def send_mapping_complete_notification(
    robot_alias: str,
    robot_id: str,
    map_dir_name: str,
    save_method: str,
    map_start_ts: datetime.datetime,
    client_map_dir: str,
    files: list[str],
) -> bool:
    msg = {
        "v": 6,
        "mt": "mapping_complete_notification",
        "msg_id": f"MSG_MAPPING_COMPLETE_{robot_alias.upper()}_{int(time.time())}",
        "ts": datetime.datetime.now().astimezone().isoformat(),
        "source": "robot_command_client",
        "dest": "fleet_server",
        "schema": "fleet_json_v0.6",
        "notification": {
            "robot_alias": robot_alias,
            "robot_id": robot_id,
            "map_dir_name": map_dir_name,
            "save_method": save_method,
            "map_start_ts": map_start_ts.astimezone().isoformat(),
            "client_map_dir": client_map_dir,
            "files": files,
        },
    }
    payload = json.dumps(msg, ensure_ascii=False) + "\n"

    try:
        with socket.create_connection((SERVER_IP, CLIENT_EVENT_PORT), timeout=10) as sock:
            sock.sendall(payload.encode("utf-8"))
            raw = b""
            while not raw.endswith(b"\n"):
                chunk = sock.recv(4096)
                if not chunk:
                    break
                raw += chunk
            ack = json.loads(raw.strip())
            return ack.get("ok", False)
    except Exception as e:
        print(f"[WARN] mapping_complete_notification 전송 실패: {e}")
        return False
```

### 사용 예

```python
namer = MapDirNamer(robot_alias="tb1", base_dir="/home/ubuntu/turtlebot_client/data/maps")
namer.start_mapping()   # start_mapping op 수신 시 호출

# ... SLAM 실행, 완료 감지 ...

map_dir_path, map_dir_name = namer.create_dir(save_method="autoSave")
# map_saver_cli 실행 → map.pgm, map.yaml 저장

ok = send_mapping_complete_notification(
    robot_alias="tb1",
    robot_id="14",
    map_dir_name=map_dir_name,
    save_method="autoSave",
    map_start_ts=namer._mapping_start_ts,
    client_map_dir=map_dir_path,
    files=["map.pgm", "map.yaml"],
)
```

---

## 6. agent_result 공통 규칙

```python
def build_agent_result(server_cmd: dict, ok: bool, code: str, message: str, state: dict) -> str:
    cmd = server_cmd["command"]
    result = {
        "v": 6,
        "mt": "agent_result",
        "msg_id": f"MSG_AGENT_RESULT_{int(time.time())}",
        "ref": server_cmd["msg_id"],          # 반드시 서버 msg_id로 설정
        "ts": datetime.datetime.now().astimezone().isoformat(),
        "source": "robot_command_client",
        "dest": "fleet_server",
        "schema": "fleet_json_v0.6",
        "robot_id": cmd["robot_id"],           # 반드시 "14" (서버가 보낸 그대로)
        "command": {
            "command_id": cmd["command_id"],   # 반드시 매칭
            "job_id": cmd.get("job_id", ""),
            "op": cmd["op"],                   # 반드시 매칭
        },
        "ok": ok,
        "code": code,
        "message": message,
        "state": state,
        "err": [],
    }
    return json.dumps(result, ensure_ascii=False) + "\n"
```

**매칭 필수 4항목:**
```
agent_result.ref                == server_command.msg_id
agent_result.robot_id           == server_command.command.robot_id
agent_result.command.command_id == server_command.command.command_id
agent_result.command.op         == server_command.command.op
```

---

## 7. config 파일 설정 (client_info.json)

`program/json/client_info.json`의 `robot_command_client.paths` 에 다음 추가:

```json
{
  "robot_command_client": {
    "paths": {
      "client_map_save_dir": "/home/ubuntu/turtlebot_client/data/maps"
    },
    "ssh": {
      "enabled": true,
      "user": "ubuntu",
      "host": "192.168.3.63",
      "port": 22,
      "identity_file": "/home/admin_kyj/.ssh/id_rsa"
    }
  }
}
```

> **`ssh.enabled: true` 필수.** 현재 false이면 서버의 rsync pull 실패.

---

## 8. 구현 체크리스트

### 8-1. 필수 (v0.5.x 대비 추가)

- [ ] `start_mapping` op 처리 — SLAM 노드 실행
- [ ] `start_mapping` 응답에 `operating_mode=MAPPING` 포함
- [ ] `explore:true` 파라미터 수신 시 자율 탐색 노드도 함께 실행
- [ ] `save_map` op 처리 — map_saver_cli 실행
- [ ] 맵 저장 디렉토리 이름 규칙 준수 (`YYYYMMDD_HHMMSS_robot_method_N`)
- [ ] 맵핑 시작 시각(`map_start_ts`) 로컬 보관 (디렉토리 이름 HHMMSS 사용)
- [ ] `saveNumber` 누적 카운터 관리
- [ ] 맵 저장 완료 후 포트 4003으로 `mapping_complete_notification` 전송
- [ ] ACK 수신 확인 후 연결 종료
- [ ] `stop_mapping` op 처리 — SLAM/탐색 노드 종료
- [ ] SSH key 인증 설정 (서버 rsync pull용)
- [ ] `client_info.json` `ssh.enabled: true` 설정

### 8-2. 기존 유지

- [ ] `move_forward` / `move_backward` / `turn_left` / `turn_right` / `custom_move` — cmd_vel pub
- [ ] `robot_stop` — 정지 명령
- [ ] `emergency_stop` — 전체 정지
- [ ] `agent_result` ref / robot_id / command_id / op 4항목 매칭
- [ ] `client_heartbeat_response` 정상 반환

---

## 9. 맵핑 완료 감지 기준

`explore:true` 자율 탐색 모드에서 맵핑 완료를 판단하는 방법:

```
A. 탐색 범위 커버리지 임계값 도달 (추천)
   - /map 토픽 unknown cell 비율이 일정 % 이하
B. 탐색 경로 수렴 감지
   - 새로운 frontier가 더 이상 없음
C. 타임아웃 기반
   - start_mapping 후 N분 경과 → 저장 후 완료
D. 운영자 수동 정지
   - stop_mapping 명령 수신 → save → complete
```

구현은 자유롭게 선택. 단, 완료 판단 후 반드시:
1. `save_map` 실행 (map.pgm + map.yaml 생성)
2. `mapping_complete_notification` 전송 (포트 4003)
3. SLAM 노드 종료
4. `operating_mode=MANUAL` 상태로 전환

---

## 10. SSH 키 설정 (서버 rsync pull용)

서버(`admin_kyj@192.168.3.61`)가 클라이언트(`ubuntu@192.168.3.63`)의 파일을 rsync로 pull합니다.

```bash
# 서버에서 실행 (192.168.3.61)
ssh-keygen -t rsa -f ~/.ssh/id_rsa  # 이미 있으면 skip

# 클라이언트에 공개키 등록 (서버에서 실행)
ssh-copy-id ubuntu@192.168.3.63
# 또는 수동으로:
# cat ~/.ssh/id_rsa.pub | ssh ubuntu@192.168.3.63 "cat >> ~/.ssh/authorized_keys"

# 연결 테스트 (서버에서)
ssh ubuntu@192.168.3.63 "echo OK"
rsync -az ubuntu@192.168.3.63:/home/ubuntu/turtlebot_client/data/maps/ /tmp/test_maps/
```

---

## 11. 맵 저장 디렉토리 생성 스크립트 예시

```python
import os, datetime

class MappingSessionManager:
    def __init__(self, robot_alias: str, base_dir: str):
        self.robot_alias = robot_alias
        self.base_dir = base_dir
        self._start_ts: datetime.datetime | None = None
        self._save_count = self._load_save_count()

    def _load_save_count(self) -> int:
        if not os.path.exists(self.base_dir):
            return 0
        return len([
            d for d in os.listdir(self.base_dir)
            if os.path.isdir(os.path.join(self.base_dir, d))
               and f"_{self.robot_alias}_" in d
        ])

    def on_start_mapping(self):
        self._start_ts = datetime.datetime.now()

    def on_save_map(self, save_method: str = "autoSave") -> tuple[str, str]:
        assert self._start_ts, "start_mapping must be called first"
        self._save_count += 1
        ts_str = self._start_ts.strftime("%Y%m%d_%H%M%S")
        dir_name = f"{ts_str}_{self.robot_alias}_{save_method}_{self._save_count}"
        dir_path = os.path.join(self.base_dir, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        return dir_path, dir_name

    @property
    def mapping_start_ts(self) -> datetime.datetime:
        return self._start_ts
```
