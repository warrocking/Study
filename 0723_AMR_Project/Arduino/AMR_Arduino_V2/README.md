# AMR_Arduino_V2

`Server_admin_V2.py` 또는 자동 생산 기능이 추가된 `Server_admin_V3.py`와 Omron LD-90 사이에서 동작하는 Arduino UNO R4 WiFi용 통합 스케치입니다.

## 고정 네트워크 값

- Wi-Fi: `ROBOT_MA2_2G` (현재 비밀번호 없음)
- 중앙 서버: `192.168.0.168:5000`
- Arduino: `192.168.0.182`
- LD-90 ARCL: `192.168.0.10:7171`
- ARCL 비밀번호: `1234`
- 중앙 서버 등록 이름: `amr`

중앙 서버에는 UDP 검색 기능이 없으므로 이 버전은 서버 LAN IP로 직접 접속합니다. 공유기에서 중앙 서버 `.168`, Arduino `.182`, LD-90 `.10` 주소가 다른 장비에 배정되지 않게 고정하거나 DHCP 예약해야 합니다.

## 하드웨어

- 보드: Arduino UNO R4 WiFi
- HUSKYLENS: I2C 모드, 학습된 물체 ID `1`
- D10: 컨베이어 정방향 제어 입력
- D11: 컨베이어 역방향 제어 입력
- 출력 논리: Active HIGH

D10/D11은 모터에 직접 연결하면 안 됩니다. 절연 릴레이 또는 모터 드라이버 제어 입력에 연결하고, 정·역전 회로에는 하드웨어 상호 인터록과 비상정지 회로가 필요합니다.

## LD-90 설정

MobilePlanner의 `Robot Interface > ARCL Server Setup`에서 다음을 확인합니다.

- LD-90 주소: `192.168.0.10`
- 포트: `7171`
- 비밀번호: `1234`
- `ROUTE_ST1`, `ROUTE_ST2`, `ROUTE_ST3` 존재
- `MACRO_ST1`, `MACRO_ST2`, `MACRO_ST3` 존재
- 각 생산 Macro에는 컨베이어 작업 지점에서 ARCL `WaitState`가 발생하는 Wait 작업이 하나 이상 존재

이 버전은 Outgoing ARCL 5353 방식이 아니라 Arduino가 LD-90 ARCL 서버 7171에 직접 접속하는 방식입니다.

## 서버 명령

`Server_admin_V2.py`에서 `이름 명령` 형식으로 입력합니다.

| 입력 | 동작 |
|---|---|
| `amr Prepare` | 모터, 상태, Route, Macro, Fault 진단 |
| `amr Arm` | LD-90 모터 활성화 요청 및 상태 확인 |
| `amr Start` | `ROUTE_ST1` 한 번 실행 |
| `all Start` | ABB들과 함께 AMR의 `ROUTE_ST1` 실행 |
| `amr Route1`~`Route3` | 해당 Route 한 번 실행 |
| `amr Macro1`~`Macro3` | 해당 Macro 실행 |
| `amr Cycle` | 6단계 전체 생산 Cycle 실행 |
| `amr Stop` | 컨베이어 정지 및 LD-90 `stop` 전송 |
| `amr Status` | Arduino와 LD-90 상태 확인 |
| `amr Reset_Sequence` | 수동 Macro 컨베이어 순서를 1단계로 초기화 |
| `amr Conveyor_Forward` | 정지 상태에서 정방향 5초 시험 |
| `amr Conveyor_Reverse` | 정지 상태에서 역방향 5초 시험 |
| `amr Conveyor_Off` | 컨베이어 즉시 정지 |

`Start`는 연결 및 기본 이동 확인용 `ROUTE_ST1`입니다. 전체 생산 순서는 `Cycle` 명령으로 따로 실행합니다.

`Server_admin_V3.py`의 `produce <대수>`가 보내는 다음 명령도 그대로 인식합니다.

| V3 자동 명령 | 실행 Macro | 완료 응답 |
|---|---|---|
| `GotoUpperPickup` | `MACRO_ST1` | `ARRIVED ... UPPER_PICKUP_AT_3ABB` |
| `GotoDropoffUpper` | `MACRO_ST2` | `ARRIVED ... UPPER_DROPOFF_AT_4ABB` |
| `GotoUpperReturn` | `MACRO_ST1` | `ARRIVED ... UPPER_RETURN_AT_3ABB` |
| `GotoLowerPickup` | `MACRO_ST3` | `ARRIVED ... LOWER_PICKUP_AT_5ABB` |
| `GotoDropoffLower` | `MACRO_ST2` | `ARRIVED ... LOWER_DROPOFF_AT_4ABB` |
| `GotoLowerReturn` | `MACRO_ST3` | `ARRIVED ... LOWER_RETURN_AT_5ABB` |

V3는 각 단계마다 `arrived` 문자열이 포함된 응답을 기다립니다. 이 스케치는 Macro와 컨베이어 작업이 정상 완료된 뒤에만 `ARRIVED`를 전송합니다. 실패 시에는 `ERR`만 전송하므로 V3의 자동 생산은 다음 단계로 넘어가지 않습니다.

## 전체 Cycle

1. `MACRO_ST1` — 정방향
2. `MACRO_ST2` — 역방향
3. `MACRO_ST1` — 역방향
4. `MACRO_ST3` — 정방향
5. `MACRO_ST2` — 역방향
6. `MACRO_ST3` — 역방향

자동 컨베이어는 다음 조건이 모두 충족되어야 시작합니다.

1. 해당 Macro가 실행 중입니다.
2. LD-90에서 `WaitState: Waiting ...`이 수신됩니다.
3. 현재 Macro와 Cycle 단계가 일치합니다.
4. HUSKYLENS에서 ID 1이 2회 연속 감지됩니다.

컨베이어는 최대 5초간 동작합니다. Wait 종료 전 제품을 확인하지 못하거나 카메라가 끊기면 Cycle을 중단하고 서버에 `ERR`를 보냅니다.

## 권장 첫 시험 순서

1. LD-90 비상정지, 주행 경로, 컨베이어 주변을 사람이 확인합니다.
2. `Server_admin_V2.py` 또는 `Server_admin_V3.py`를 실행합니다.
3. Arduino에 `AMR_Arduino_V2.ino`를 업로드하고 전원을 켭니다.
4. 서버에서 `amr` 접속과 `ONLINE LD90 ... ARCL=AUTHENTICATED`를 확인합니다.
5. `amr Prepare`를 입력하고 `FAULT_SCAN_COMPLETE faults=0`을 확인합니다.
6. `amr Arm`을 입력하고 `EVENT MOTORS_READY`를 확인합니다.
7. 사람과 장애물이 없는 상태에서 `amr Start`로 `ROUTE_ST1`만 시험합니다.
8. 컨베이어를 분리하거나 안전하게 띄운 상태에서 정·역방향 수동 시험을 합니다.
9. HUSKYLENS ID 1과 각 Macro의 Wait를 확인한 뒤 `amr Cycle`을 시험합니다.

V3 자동 생산은 위의 개별 시험을 모두 통과한 다음 `produce 1`로 한 대만 먼저 시험합니다. `produce`는 자동으로 `Arm`하지 않으므로 실행 전에 반드시 `amr Prepare`, `amr Arm`, `EVENT MOTORS_READY` 확인이 필요합니다.

Arduino IDE에서는 이 폴더의 `AMR_Arduino_V2.ino`를 열어 컴파일해야 합니다. 기존 `DistanceSetting_WiFi` 폴더에 복사하면 그 폴더의 여러 `setup()`/`loop()`와 충돌합니다.
