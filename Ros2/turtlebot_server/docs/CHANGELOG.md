# Changelog

## v0.6

- **Fleet JSON 와이어 포맷 v0.6 확정**: `"v": 6, "schema": "fleet_json_v0.6"` 아웃바운드 전환
  - 서버 상수: `FLEET_JSON_VERSION_V6 = 6`, `FLEET_JSON_SCHEMA_V6 = "fleet_json_v0.6"`
  - 서버 수락 범위: v=5 또는 v=6 인바운드 모두 수락 (`FLEET_JSON_SCHEMA_V5_COMPAT`)
  - 서버 발신: 모든 아웃바운드 메시지 v=6 전환 완료 (33개 참조 업데이트)
- **포트 4003 `client_event_port` 신규 추가**:
  - 방향: 클라이언트 → 서버 (서버가 listen, 클라이언트가 connect)
  - `server_config.server.client_event_port: 4003`
  - `run()` 메서드에 `("client_event", 4003)` 리스너 추가
  - `_handle_client_event_connection()` 핸들러 신규 구현
  - 헬스 응답에 `server.client_event_port` 필드 추가
- **`mapping_complete_notification` / `mapping_complete_ack` 신규**:
  - 클라이언트가 맵핑 완료 후 포트 4003으로 서버에 알림
  - 서버: ACK 응답 → 백그라운드 SSH rsync pull (`_auto_sync_map_from_client_v5`)
  - 필수 필드: `notification.map_dir_name`, `notification.client_map_dir`
- **맵 디렉토리 이름 규칙 v0.6 확정**:
  `YYYYMMDD_HHMMSS_turtlebotName_saveMethod_saveNumber`
  - saveMethod: `autoSave` / `stop` / `emergency`
  - saveNumber: 클라이언트 누적 카운터
  - `_parse_map_dir_name()`: 이름 파싱 + 검증
  - `_list_server_map_dirs()`: 백업 디렉토리 스캔 + 메타데이터 생성
- **`map_list` action 메타데이터 응답 강화**:
  - 응답 `status.maps[]`: index, dir_name, date, time, robot, save_method, save_number, files, display
  - `params.robot` 필터 지원
- **`map_image_select` action 신규**:
  - `params.index` 또는 `params.dir_name`으로 선택
  - 서버 → 제어 컴퓨터 SSH rsync push
  - `action_policy.json`에 priority 61 등록
- **config 추가/변경**:
  - `client_info.robot_command_client.paths.client_map_save_dir`
  - `control_info.control_ui.paths.control_map_receive_dir`
  - `server_config.file_transfer.allowed_source_dirs`에 maps 경로 추가
- **`FILE_TRANSFER_ACTIONS`**: `map_image_select` 추가
- **팀 문서 전면 갱신**:
  - `docs/JSON_CONTRACT_V06.md`: v0.6 전체 규약 (신규)
  - `docs/FLEET_JSON_V06_TEAM_PROMPT.md`: 팀 공유 프롬프트 (신규, FLEET_JSON_V051_PROMPT.md 대체)
  - `docs/CLIENT_V06_HANDOFF_PROMPT.md`: 클라이언트 개발자 가이드 (신규)
  - `docs/CONTROL_V06_INTERFACE.md`: 제어 UI 개발자 가이드 (신규)

## v0.5.2

- **맵핑 완료 자동화 흐름 추가** (클라이언트 주도)
  - 포트 4003 `client_event_port` 서버 listen 추가
  - 클라이언트 → 서버: `mapping_complete_notification` 처리 (`_handle_client_event_connection`)
  - 서버 응답: `mapping_complete_ack` 반환
  - 백그라운드 자동 SSH rsync: `_auto_sync_map_from_client_v5` (디렉토리 단위 pull)
- **맵 디렉토리 이름 규칙 확정**:
  `YYYYMMDD_HHMMSS_turtlebotName_saveMethod_saveNumber`
  - saveMethod: `autoSave` (자동) / `stop` (운영자 정지) / `emergency` (긴급정지)
  - saveNumber: 클라이언트가 자체 카운트한 누적 맵핑 번호
  - 예시: `20260624_164951_tb1_autoSave_1`
- **`map_list` action 고도화**: 서버 백업 디렉토리를 파싱해 목록+메타데이터 JSON 응답 (`_handle_map_list_v5`)
- **`map_image_select` action 신규**: index 또는 dir_name으로 선택 후 SSH rsync로 제어 컴퓨터 전송 (`_handle_map_image_select_v5`)
- **config 추가**:
  - `server_config.server.client_event_port: 4003`
  - `server_config.paths.server_map_backup_dir: data/maps`
  - `client_info.robot_command_client.paths.client_map_save_dir`
  - `control_info.control_ui.paths.control_map_receive_dir`
- **health response**: `server.client_event_port` 필드 추가 (클라이언트가 포트 자동 인지)
- **문서**: `JSON_CONTRACT_V051.md`, `CLIENT_V051_HANDOFF_PROMPT.md`, `CONTROL_INTERFACE_V051.md` 전체 반영

## v0.5.1

- Fleet JSON 규약 v0.5.1 정리 (와이어 포맷 v=5, schema=fleet_json_v0.5 유지, 하위 호환)
- 맵핑 전체 흐름 명세 확정: `start_mapping` → 이동 → `save_map` → `rsync_map` → `stop_mapping`
- `start_mapping` 성공 시 `operating_mode=MAPPING` 보고 필수로 명시
- 자동 탐색 규칙 확정: `explore: true`는 제어 UI가 명시적으로 params에 포함, 서버는 그대로 전달
- `R_STARTED` 사용 기준 명시: 백그라운드 작업 시작 시 (start_mapping, nav_goal 등)
- 네비게이션 명세 추가: `nav_goal` (x, y, theta), `nav_cancel`
- `operating_mode` 상태 전이 표 전체 정리, 모드별 허용 action 표 추가
- 전체 result code 목록 문서화 (R_* / E_*)
- 클라이언트 v0.5.1 작업 지시 프롬프트 (`CLIENT_V051_HANDOFF_PROMPT.md`)
- 제어 UI v0.5.1 인터페이스 가이드 (`CONTROL_INTERFACE_V051.md`)
- 전체 규약 단일 문서 (`JSON_CONTRACT_V051.md`)

## v0.5

- `/home/admin_kyj/turtlebot_server` 서버 전용 루트 생성
- `program/json`, `program/code`, `program/scripts`, `data`, `docs`, `tests`, `legacy_removed` 분리
- `server_manager.py` 실행 진입점 추가
- Control UI 포트 4000, Robot Command Client health 5000 / command 5001 / data_control 5002 기준 설정
- 활성 로봇을 `tb3_3`으로 설정
- v5 `control_health_request` 응답 지원
- v5 `operator_request` / `control_command_request`를 내부 명령으로 정규화해 v5 `server_command`를 Robot Command Client로 전달
- v5 `agent_result` 과도기 정규화 지원
