# 이전 3개 프로젝트 비교 분석 — 코드 스타일 / 서버 스타일

작성일: 2026-08-10
대상: 사용자가 "메인"으로 꼽은 세 개의 서로 다른 이전 프로젝트

- `RobotStudio/project.mod` — ABB 타이어 자동화 셀 (RAPID 단일 파일)
- `0723_AMR_Project/Final_Ver07` — 자동차 자동화 공정 1차 (ABB×3 + AMR + PLC + Python 서버)
- `Ros2/turtlebot_server` — TurtleBot Fleet Server (Linux, Python, ROS2 연동)

세 프로젝트는 서로 의존관계 없는 독립 프로젝트입니다. 이 문서는 각 프로젝트의 실제 코드를
읽고 확인한 내용만 담았으며, 확인하지 못한 부분(전체 파일을 다 읽지는 못함)은 명시했습니다.

---

## 1. RobotStudio/project.mod

**검토 범위**: `project.mod` 전체 1개 파일(약 650줄), `RobotStudio/CLAUDE.md`(기존 인수인계 문서).

### 코드 스타일
- RAPID 단일 MODULE에 서버 루프·생산 사이클·에러 처리·좌표 데이터가 전부 한 파일에 있음.
- 영어 주석이 상당히 상세함 — 예: `p_tool2_down10`에 "not referenced anywhere currently"라고
  써서 죽은 변수임을 스스로 표시, `Reorient_CoolingSweep`의 25도/45도 각도를 "5/10/15/20/30도와
  MoveJ vs MoveL을 실기로 비교해서 결정"이라고 근거까지 남김. 코드 자체가 결정 기록 역할을 겸함.
- 생산 로직(`Run_Production_Cycle`)이 `di21~di26` 각각을 조건으로 하는 큰 `WHILE` 루프 하나에
  전부 들어있음 — 마스터 프롬프트가 경고한 "무한 while 안에 단순 다수의 if문" 패턴과 정확히
  일치. 상태 머신이 암묵적(di 신호 자체가 상태)이라, 지금 어느 단계인지 코드 흐름을 눈으로
  따라가야만 알 수 있음.

### 서버 스타일
- `PROC Main()`이 RAPID 안에서 직접 raw TCP 서버(`SocketBind`/`SocketListen`)를 열고, 클라이언트
  텍스트 명령(`"start"`/`"end"`)을 **정확히 일치(`=`)** 비교로 처리.
- `Count > 0`이면 재접속 시 "start" 없이 자동으로 이어서 생산 — 서버 재시작에도 진행 상태가
  살아남는 설계(단, 이 진행 상태가 오직 `Count` 하나뿐이라 표현력은 제한적).
- 에러 처리: `ERR_SOCK_TIMEOUT`→RETRY, `ERR_SOCK_CLOSED`→소켓 재생성 후 RETRY, 그 외 전부
  `TPWrite; Stop;` — **0723_AMR_Project의 3abb.mod/5abb.mod/4abb.mod와 완전히 동일한 패턴**.
  아마 이 project.mod가 원형이고 AMR 프로젝트가 이 구조를 그대로 이어받은 것으로 보임.

### 장점
- **비상정지(TRAP) 처리가 세 프로젝트 중 가장 완성도 높음.** `Trap_EStop`이 `StopMove` →
  양쪽 액추에이터 출력 OFF → 클라이언트에 "EMERGENCY STOP" 통지 → `Count`를 0으로 강제 리셋 →
  "클라이언트 재접속 AND 물리적 E-stop 해제" 두 조건이 다 될 때까지 대기 → `ExitCycle`로
  `Main()` 처음부터 재시작. 소프트웨어 정지와 물리적 비상정지를 실제로 연동한 유일한 사례.
- `Check_For_End_Command`가 0.5초 타임아웃 소켓 수신으로 "생산 계속하면서 END 명령도 계속
  확인"을 스레드 없이 구현 — RAPID에 스레드가 없다는 제약 안에서 나온 실용적인 해법.

### 문제점 (RobotStudio/CLAUDE.md에 이미 기록된 것 포함)
- `count_White`의 `CASE 2/3/4`가 비어있어 두 번째 이후 불량 타이어의 그리퍼가 안 열림(기존
  기록된 버그).
- 불량 발생 시에만 `processRunning := FALSE`로 전체 사이클 종료 — 정상 분기와 비대칭.
- `Grip_on`/`Grip_off`의 `WaitDI`에 타임아웃 없음 — 센서 무응답 시 무한 정지.
- **`received_string = "start"` 정확히 일치 비교** — 3abb.mod가 이미 "SocketReceive가 개행/여분
  문자를 덧붙일 수 있어 정확 일치가 조용히 실패한다"는 이유로 `StrPart` 접두어 비교로 바꾼 걸로
  볼 때, project.mod는 아직 그 교훈이 반영되기 전 버전일 가능성이 있음.
- 에러 처리 catch-all `Stop` 패턴 — [[project_ver07_server_findings]]에서 지적한 것과 동일한
  구조적 문제.

---

## 2. 0723_AMR_Project/Final_Ver07

**검토 범위**: 오늘 밤 세션에서 `Server_admin_Web.py` 전체, `3abb_connector.py`/`5abb_connector.py`/
`4abb_connector.py` 전체, `3abb.mod`/`5abb.mod`/`4abb.mod` 핵심 부분을 읽음(가장 깊이 본 프로젝트).
상세 내용은 메모리 [[project_ver07_server_findings]] 참고 — 여기서는 스타일 관점만 요약.

### 코드 스타일
- Python 서버 쪽(`Server_admin_Web.py`)은 세 프로젝트 중 RAPID 밖으로 나온 유일한 사례 —
  Flask + threading + dataclass를 씀. 다만 약 1,300줄 단일 파일에 릴레이·오케스트레이션·웹·
  UDP 디스커버리가 전부 들어있는 단일 클래스(God Class) 구조.
- **코드 안에 "이전 버전 대비 뭐가 왜 바뀌었는지"를 굉장히 상세하게 기록하는 습관**이 세 파일
  모두에 일관되게 있음(예: "V05 대비 이 버전에서 바뀐 것: ..."). 사실상 코드 파일 자체가
  변경 이력서 역할을 함 — git log나 CHANGELOG가 따로 없는 대신 파일 헤더 주석이 그 역할을 대신함.
- 프로토콜은 여전히 raw 텍스트 문자열(`"ReadyForPickup unit=1"`) — 구조화된 스키마나 버전
  필드가 없음. RobotStudio/project.mod의 `"start"`/`"end"`보다는 진보(필드가 생김)했지만,
  아래 3번 프로젝트의 JSON 스키마 방식과 비교하면 여전히 파싱에 정규식(`_extract_number_field`)이
  필요한 수준.

### 서버 스타일
- 3개 커넥터(3abb/4abb/5abb)가 각각 자기 IP를 하드코딩(설정 파일 없음), ABB 세션과 관리자
  세션의 재접속을 독립적으로 처리하도록 설계된 점은 견고함.
- `_run_pickup_matcher`가 unit 불일치를 감지하고도 그대로 허가하는 fail-open, "정지 요청"이
  실제 장치에 아무 명령도 안 보내는 문제 등은 [[project_ver07_server_findings]]에 상세 기록.

### 장점
- 실제 사고(반납 도착이 픽업으로 오인, 배선 겸용 신호)를 겪고 고친 이력이 코드 주석에 생생하게
  남아있어 "왜 이렇게 짰는지"를 추적하기 매우 좋음.
- 릴레이 재접속을 ABB/관리자 세션 독립적으로 분리한 설계는 실전에서 검증된 패턴.

### 문제점
- [[project_ver07_server_findings]] 요약: fail-open 매칭, Stop이 실제로 안 멈춤, 매처에 세대
  개념 없음, 인증 없는 TCP 서버, IP 하드코딩 3중 복제, RAPID 쪽 catch-all Stop(project.mod와
  동일 패턴).
- **자동 테스트가 있다가 없어짐** — 폐기된 Final_Ver06에는 `Tests/test_signal_interlock.py`가
  있었는데, Final_Ver07에는 Tests 폴더 자체가 없음. 갈래가 바뀌면서 테스트 자산이 유실됨.
- 버전이 파일명/폴더명(Ver01~Ver07, V04~V19 등)으로 관리되어, 오늘 밤 확인한 것처럼 어느 게
  진짜 최신인지 파일을 열어봐야 알 수 있음.

---

## 3. Ros2/turtlebot_server

**검토 범위(1차)**: `README.md`, `fleet_protocol.py`(전체, ~1000줄), `emergency_supervisor.py`
(전체), `config_loader.py`(전체), `docs/CHANGELOG.md`(v0.5.2~v0.6 구간), `legacy_removed/README.md`.

**검토 범위(2차, 추가로 더 읽음)**: `fleet_server_main.py`(총 4,058줄 중 앞부분 1,343줄 +
안전 로직 부분 발췌 확인), `command_router.py`(전체), `opencv_manager.py`(전체), 그리고
`global_state`/`_check_server_safety`/`EmergencySupervisor` 참조 여부를 `program/code/` 전체에서
grep으로 교차 확인. `client_connection_manager.py`/`control_connection_manager.py`/
`data_log_manager.py`/`data_transfer_manager.py`/`server_manager.py`는 여전히 미검토.

### 코드 스타일
- **세 프로젝트 중 가장 현대적인 Python 스타일**: `from __future__ import annotations`, 타입
  힌트(`Dict[str, Any]`, `Iterable[str] | None`), 명확한 예외 클래스(`ProtocolError`,
  `ConfigError`), 기능별로 파일이 잘게 분리됨(`fleet_protocol.py`/`emergency_supervisor.py`/
  `config_loader.py`/`data_transfer_manager.py`/`opencv_manager.py` 등 11개 모듈).
- **메시지 타입·액션·결과 코드가 전부 명시적 집합(set)으로 선언**되어 있음
  (`FLEET_MESSAGE_TYPES_V5`, `FLEET_ACTIONS`, `RESULT_CODES_OK`/`RESULT_CODES_ERROR`) — 이건
  오늘 밤 학습 자료에서 다룬 "COMMAND/EVENT/STATUS/ACK/ERROR를 명확히 구분하라"는 원칙을 이미
  실제 코드로 구현해 놓은 사례.
- 프로토콜이 JSON Lines이고, 버전 필드(`v`)와 스키마 문자열(`schema`)이 메시지마다 들어있으며,
  구버전 호환(`FLEET_JSON_SCHEMA_V5_COMPAT`)까지 명시적으로 관리됨.

### 서버 스타일
- **포트를 역할별로 분리**: health(4000)/command(4001)/data(4002)/event(4003) — 하나의 소켓이
  모든 걸 다 하는 게 아니라 관심사별로 나뉨. 오늘 밤 3부에서 논의한 "SCADA/MES 계층 분리"
  아이디어를 이미 물리적 포트 분리로 실현한 사례.
- **설정이 전부 JSON 파일로 외부화**(`server_config.json`/`client_info.json`/`control_info.json`/
  `emergency_info.json`)되어 있고, `config_loader.py`가 시작 시점에 필수 키·포트 범위까지
  검증(`validate_ports`) — 0723_AMR_Project 커넥터들의 "IP 하드코딩" 문제가 여기선 원천적으로
  없음.
- **비상정지 정책이 별도 클래스(`EmergencySupervisor`)로 분리**되어 있고, "EMERGENCY 상태에서
  허용되는 액션 집합"을 명시적으로 관리 — 마스터 프롬프트가 요구한 "정상정지/공정중단/비상정지
  구분"에 필요한 뼈대가 이미 있음(다만 이 클래스가 실제 커맨드 처리 경로 전체에 빠짐없이
  연결돼 있는지는 이번에 확인하지 못함).
- **테스트용 Mock 클라이언트가 실제로 존재**(`tests/mock_external/mock_robot_command_client.py`)
  — 마스터 프롬프트가 요구했던 "가상 중계기로 실물 없이 검증"이 이 프로젝트에서는 실제로
  구현돼 있음. 0723_AMR_Project에서는 이게 (Final_Ver06에만 잠깐 있다가) 유실됐던 것과 대비됨.

### 장점
- 버전 관리가 세 프로젝트 중 가장 체계적. `docs/CHANGELOG.md`가 v0.5.2, v0.6마다 무엇을
  왜 바꿨는지 기능 단위로 기록되어 있고, `docs/JSON_CONTRACT_V05/V051/V06.md`처럼 프로토콜
  버전마다 별도 계약 문서가 있음.
- `legacy_removed/README.md`에 "완전 삭제는 사용자 확인 후 진행"이라는 명시적 거버넌스 규칙이
  있음 — 오늘 밤 세션에서 계속 강조된 "함부로 삭제하지 말고 옮겨두라"는 원칙을 프로젝트
  자체가 이미 실천하고 있는 사례.

### 문제점 (2차 검토에서 실제로 확인됨)

- **`fleet_server_main.py`가 4,058줄짜리 단일 파일입니다.** `FleetServer` 클래스 하나에 설정
  검증, v4/v5/v6 프로토콜 처리, 타겟 해석, 안전 검사, 맵 동기화, 이미지 전송까지 다 들어있음 —
  세 프로젝트 중 가장 정교한 설계 아이디어를 가진 프로젝트인데, 정작 실행 파일은 가장 심한
  God Class입니다(0723_AMR_Project의 `Server_admin_Web.py` 1,300줄보다 3배 이상 큼).

- **`command_router.py`와 `emergency_supervisor.py`는 실제로 안 쓰이는 죽은 모듈입니다.**
  `command_router.py`는 자기 docstring에 스스로 "FleetServer currently owns the executable
  routing path. This class is kept as the future extraction point"라고 명시 — 즉 앞으로 옮길
  자리를 미리 잡아둔 빈 틀입니다. `emergency_supervisor.py`(`EmergencySupervisor.command_allowed`)는
  `program/code/` 전체를 grep해봐도 `fleet_server_main.py`에서 단 한 번도 import되거나
  호출되지 않습니다 — **같은 로직(EMERGENCY 상태에서 허용되는 액션 집합)이 `fleet_server_main.py`
  1345행에 따로, 거의 동일한 목록으로 다시 인라인 작성**되어 있습니다(`EmergencySupervisor`는
  `job_status_request`를 허용 목록에 포함하는데 인라인 버전은 빠져있는 등 미세한 차이까지
  있어서, 두 버전이 서서히 갈라지고 있는 상태). 모듈로 분리해놓고 실제로는 안 쓰고 복붙한
  전형적인 사례.

- **비상 상태(`global_state == "EMERGENCY"`) 자체가 실제로 켜지는 코드 경로를 못 찾았습니다.**
  `self.global_state`는 `__init__`에서 `"NORMAL"`로 초기화된 뒤, 상태를 보고하거나
  `1345행의 if self.global_state == "EMERGENCY"` 조건에서 읽히기만 할 뿐, `program/code/`
  어디에서도 `"EMERGENCY"`로 재할당되는 곳이 없습니다(grep으로 확인). 즉 이 EMERGENCY 차단
  로직은 지금 상태로는 **도달 불가능한 코드일 가능성**이 있습니다 — clear_emergency
  액션도 있는 걸 보면 원래는 뭔가가 EMERGENCY로 전환해야 하는데, 그 트리거가 이 서버 코드
  안에는 없습니다(다른 파일이나 별도 프로세스에 있을 수도 있어 완전히 단정할 수는 없음).

- **실제로 살아서 동작하는 안전 장치는 따로 있습니다.** `_check_server_safety()`(2108행)가
  `opencv_manager.py`가 읽는 JSON 이벤트 파일(`lv: NORMAL/PAUSE/EMERGENCY`, 카메라 기반
  사람/장애물 감지로 추정)을 매 `MOVE_ACTIONS` 요청마다 새로 읽어서, PAUSE/EMERGENCY면
  이동 명령을 차단합니다. **이건 실제로 매 요청마다 파일을 다시 읽어서 확인하는, 살아있는
  메커니즘**입니다. 문제는 이게 이동 명령에만 적용되고, 위의 "죽은" `global_state` 기반
  차단과는 완전히 별개의 병렬 시스템이라는 점 — **"비상 상태"를 나타내는 개념이 두 개
  (opencv 이벤트 파일의 `lv`, 서버의 `global_state`) 존재하는데 서로 연결되어 있지 않습니다.**
  나중에 유지보수하는 사람이 어느 쪽이 진짜인지 헷갈리기 쉬운 구조.

- **인증이 기본적으로 꺼져 있습니다.** `require_auth = bool(self.config.get("auth", {}).get
  ("require_auth", False))` — 기본값 `False`. 설정하더라도 토큰 기본값이 코드에 그대로 박힌
  `"team_demo_token"`. 0723_AMR_Project의 "인증 전혀 없음"보다는 한 단계 나은 구조(토큰 검증
  자체는 구현돼 있음)지만, 기본 설정으로 배포하면 사실상 인증이 없는 것과 같습니다.

### 확인된 장점 (2차 검토에서 추가로 확인)
- `allowed_control_ips` 화이트리스트로 제어 클라이언트 IP를 제한하는 기능이 실제로 구현돼
  있음 — 0723_AMR_Project에는 아예 없는 기능.
- `seen_command_ids` 집합으로 **명령 중복 실행 방지(idempotency)가 실제로 동작**함 — 마스터
  프롬프트가 요구했던 "중복 이벤트가 두 번 실행되지 않게" 원칙이 실제 코드로 구현된 사례.
- v4→v5→v6 프로토콜을 어댑터 레이어(`_adapt_control_command_request_v5_to_v4` 등)로 흡수해서
  구버전 클라이언트도 계속 받아주는 하위 호환 처리 — 다만 이로 인해 사실상 같은 요청을 처리하는
  경로가 3벌(레거시 v1, v4, v5/v6→v4 변환)로 늘어나 있어, 파일 크기가 커진 원인 중 하나로 보임.

### 확인 필요 (아직 못 읽음)
- `client_connection_manager.py`/`control_connection_manager.py`/`data_log_manager.py`/
  `data_transfer_manager.py`/`server_manager.py` 본문
- SSH rsync 기반 맵 동기화(`_auto_sync_map_from_client_v5`)의 실패 처리
- Linux 환경(`/home/admin_kyj/...` 경로) 기반이라, 이 패턴들을 그대로 Windows + Tailscale
  환경의 AMR 프로젝트에 이식하려면 경로/서비스 실행 방식 등은 조정이 필요합니다.

---

## 종합 — 세 프로젝트를 나란히 놓고 보면

| 항목 | RobotStudio | 0723_AMR_Project | turtlebot_server |
|---|---|---|---|
| 프로토콜 | 텍스트 1단어(`start`/`end`) | 텍스트+필드(`unit=`) | JSON Lines + 버전 필드 |
| 설정 관리 | 코드에 하드코딩 | 코드에 하드코딩(3중 복제) | JSON 파일 + 시작 시 검증 |
| 비상정지 | TRAP으로 실제 연동 | 별도 비상정지 로직 미확인 | 별도 정책 클래스로 분리 |
| 에러 처리 | catch-all Stop | catch-all Stop(동일 패턴) | 살아있는 안전장치(opencv) + 죽은 안전장치(global_state) 병존 |
| 버전 관리 | 단일 파일, 이력 없음 | 폴더/파일명 버전, 갈래 분기 발생 | CHANGELOG + 계약 문서(체계적) |
| 테스트 | 없음 | 있다가 유실됨(Ver06→Ver07) | Mock 클라이언트 존재 |
| 실행 파일 크기 | 650줄 단일 파일 | 1,300줄 단일 클래스 | **4,058줄 단일 클래스(가장 큼)** |
| 모듈 분리 | 해당 없음 | 해당 없음 | 파일은 분리돼 있지만 일부(command_router, emergency_supervisor)는 실제로 안 쓰이는 껍데기 |

같은 사람(팀)이 만든 세 프로젝트인데 **성숙도 차이가 뚜렷하지만, 더 깊이 볼수록 turtlebot_server도
"설계는 좋은데 실제 실행 경로와 어긋난 부분이 있다"는 게 드러났습니다.** RobotStudio와
0723_AMR_Project는 같은 원형(catch-all Stop, 하드코딩 설정, raw 텍스트 프로토콜)을 공유하는
소품종 구조이고, turtlebot_server는 스키마 버전 관리·설정 외부화·포트 분리·Mock 테스트 등
좋은 아이디어를 훨씬 많이 시도했지만, 그중 일부(비상정지 정책 분리, 라우터 분리)는 **모듈만
만들어놓고 실제로는 연결 안 한 상태**로 남아있습니다. 세 프로젝트를 관통하는 공통 교훈은
하나입니다 — **"좋은 설계를 문서/모듈로 만들어두는 것"과 "그게 실제로 실행 경로에 연결되어
있는지"는 완전히 다른 문제**라는 것. 오늘 밤 0723_AMR_Project에서 찾은 것(Stop 버튼이 실제
장치에 아무 명령도 안 보냄)과 turtlebot_server에서 찾은 것(EmergencySupervisor가 안 쓰임,
global_state=EMERGENCY로 가는 경로가 없음)은 같은 종류의 함정입니다.

**2차 프로젝트(Next_Automotive_Automation) 설계에 주는 실질적 시사점**:
- turtlebot_server의 `fleet_protocol.py` 패턴(메시지 타입/액션/결과 코드를 명시적 집합으로
  선언, 버전 필드 포함 JSON 메시지, config_loader의 시작 시 검증)은 그대로 참고할 가치가
  있는 실제 코드 사례입니다.
- 다만 그대로 베끼면 안 되는 것도 있습니다: 모듈을 분리했으면 **반드시 그 모듈이 실제로
  import되고 호출되는지 자동 테스트나 코드 검색으로 주기적으로 확인**해야 합니다(안 그러면
  `command_router.py`/`emergency_supervisor.py`처럼 "있는데 안 쓰이는" 모듈이 생김).
- "비상 상태"를 나타내는 개념(플래그/이벤트)은 **한 곳에서만 정의하고, 그걸 켜는 경로와
  그걸 확인하는 경로가 반드시 코드 레벨에서 연결**되어 있어야 합니다 — 두 프로젝트 모두에서
  "정지/비상 상태 개념은 있는데 실제 실행 경로와 끊겨 있는" 패턴이 반복됐습니다.
