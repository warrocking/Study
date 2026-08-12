# AMR Server Bridge V4

`AMR_Server_Bridge_V4.ino`는 Arduino UNO R4 WiFi를 중앙 서버와 LD-90 사이의 중계기로 사용하는 최신 통합본입니다. 현재 중앙 서버인 `Server_admin_Web_ver02.py`의 통신 형식에 맞췄습니다.

## 이번 버전의 핵심

- Arduino는 `ROBOT_MA2_2G`에 DHCP로 연결합니다.
- 노트북의 `192.168.0.xxx` 주소를 코드에 고정하지 않습니다.
- Arduino가 UDP 5001로 서버를 찾고, 서버가 응답한 실제 IP의 TCP 5000에 연결합니다.
- 중앙 서버에는 첫 줄로 `amr`을 보내 장치 이름을 등록합니다.
- 서버의 6개 `RUN ROUTE_STx FWD/REV` 명령과 `RESET_SEQUENCE`를 그대로 처리합니다.
- 각 운행이 정상 종료되면 중앙 서버에 `arrived ...`를 보내 다음 공정으로 진행시킵니다.
- 서버 또는 Wi-Fi 연결이 끊기면 컨베이어를 즉시 정지하고, 운행 중이면 LD-90에 `stop`을 전송합니다.
- ARCL 인증 완료, Fault 조회 완료, 모터 활성 확인 전에는 운행을 거부합니다.
- ARCL `WaitState`에서만 컨베이어를 구동하고, WaitState 종료·5초 제한·센서 변화 중 먼저 발생한 조건에서 정지합니다.
- 완료 응답을 보내는 순간 서버 연결이 끊긴 경우, 재접속 후 보류된 `arrived`를 한 번 재전송합니다.

## 현재 설정값

| 항목 | 설정 |
|---|---|
| Arduino 보드 | UNO R4 WiFi |
| Wi-Fi | `ROBOT_MA2_2G` (현재 개방형, 비밀번호 없음) |
| 중앙 서버 탐색 | UDP 5001 |
| 중앙 서버 연결 | 발견된 IP의 TCP 5000 |
| 서버 등록 이름 | `amr` |
| LD-90 | `192.168.0.10:7171` |
| ARCL 비밀번호 | `adept` |
| 물체 센서 | D2, LOW=감지 |
| 컨베이어 정방향 | D10 HIGH / D11 LOW |
| 컨베이어 역방향 | D10 LOW / D11 HIGH |
| 컨베이어 정지 | D10 LOW / D11 LOW |

`ROBOT_MA2_2G`에 실제 비밀번호가 생기면 `WIFI_PASSWORD`만 수정하면 됩니다. LD-90 주소나 ARCL 비밀번호가 현장 설정과 다를 때에도 코드 상단의 설정값을 실제 값으로 바꿔야 합니다.

## 서버와 명령 순서

중앙 서버가 자동생산을 시작하면 먼저 `RESET_SEQUENCE`를 보냅니다. 이후 아래 순서만 허용됩니다.

1. `RUN ROUTE_ST1 FWD`
2. `RUN ROUTE_ST2 REV`
3. `RUN ROUTE_ST1 REV`
4. `RUN ROUTE_ST3 FWD`
5. `RUN ROUTE_ST2 REV`
6. `RUN ROUTE_ST3 REV`

순서나 방향이 다르면 Arduino는 AMR을 움직이지 않고 `ERR SEQUENCE_MISMATCH ...`를 응답합니다.

## 적용 및 연결 확인

1. AMR 전원을 끄거나 안전한 정비 상태로 두고 D2/D10/D11 배선과 전압·절연을 AMR 담당자가 확인합니다.
2. Arduino IDE에서 UNO R4 WiFi 보드를 선택하고 `AMR_Server_Bridge_V4.ino`를 업로드합니다.
3. 중앙 노트북을 `ROBOT_MA2_2G`에 연결합니다.
4. 중앙 노트북에서 `Server_admin_Web_ver02.py`를 실행합니다.
5. Arduino를 켜고 시리얼 모니터를 115200 baud로 엽니다.
6. 아래 흐름이 나타나는지 확인합니다.

```text
WIFI_CONNECTED ip=192.168.0.xxx
DISCOVERY_READY local_port=5002
DISCOVERY_TX target=192.168.0.255:5001
DISCOVERY_OK admin=192.168.0.xxx:5000
ADMIN_CONNECTING 192.168.0.xxx:5000
```

7. Web HMI에서 `amr` 표시가 연결 상태로 바뀌는지 확인합니다.
8. 사람과 장애물을 치운 뒤 저속·수동 감시 상태에서 `amr STATUS`, `PREPARE`, 첫 경로 순으로 시험합니다. 자동생산 전체 시험은 단일 경로와 컨베이어 방향을 모두 확인한 뒤 진행합니다.

## 반드시 현장에서 확인할 항목

- MobilePlanner에 `ROUTE_ST1`, `ROUTE_ST2`, `ROUTE_ST3`가 정확히 존재해야 합니다.
- 각 경로에는 물품 인계용 `WaitState`가 있어야 합니다. 없으면 안전상 `arrived`를 보내지 않습니다.
- `FWD`와 `REV`가 실제 컨베이어 방향과 일치하는지 확인해야 합니다.
- D10/D11은 모터 전원선이 아니라 절연된 PLC/릴레이/드라이버의 제어 입력에만 연결해야 합니다.
- D2 센서의 실제 극성과 검출 위치를 확인해야 합니다. 현재는 센서 변화가 있으면 조기 정지에 사용하지만, 검증 전 운행 완료의 필수 조건으로는 두지 않았습니다. 검증이 끝나면 `REQUIRE_OBJECT_SENSOR_CONFIRMATION`을 `true`로 바꿀 수 있습니다.
- 물리 E-stop과 LD-90 자체 안전 장치가 최우선이며 Arduino 코드가 이를 대신하지 않습니다.

## 서버 쪽에 남아 있는 사항

이 스케치는 현재 서버를 수정하지 않습니다. `Server_admin_Web_ver02.py`는 AMR에서 오류가 오더라도 자동생산 대기 이벤트를 즉시 풀지 않고 `arrived`를 계속 기다리는 구조이므로, AMR 오류 시 Web HMI에서 정지 요청을 하고 원인을 해결해야 합니다. 또한 4abb 시작 시점은 서버 로직에서 별도로 관리해야 하며 Arduino가 4abb를 직접 시작시키지는 않습니다.

서버 자동 탐색이 되지 않으면 Windows 방화벽에서 Python의 사설 네트워크 통신과 UDP 5001/TCP 5000을 허용했는지, 노트북과 Arduino가 같은 `ROBOT_MA2_2G` 대역인지 확인합니다.
