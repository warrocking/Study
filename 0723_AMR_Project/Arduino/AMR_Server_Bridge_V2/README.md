# AMR Server Bridge V2

`AMR_Server_Bridge_V2.ino`는 받은 최신 통합 자료의 서버 명령 규격을 유지하면서 현재 실습실 네트워크와 안전 동작을 반영한 UNO R4 WiFi용 스케치입니다.

## 현재 설정

- Wi-Fi: `ROBOT_MA2_2G` (공개 네트워크)
- 중앙 서버: `192.168.0.168:5000`
- 서버 등록 이름: `amr`
- LD-90 직접 ARCL: `192.168.0.10:7171`
- ARCL 암호 기본값: `adept`
- 물체 센서: D2, LOW 감지
- 컨베이어 정방향/역방향: D10/D11

중앙 노트북의 Wi-Fi 주소가 바뀌면 스케치의 `ADMIN_SERVER_IP`도 바꿔야 합니다. Arduino 자체 주소는 DHCP여도 중앙 서버로 먼저 접속하기 때문에 고정할 필요가 없습니다.

## 받은 코드에서 보강된 내용

- 공개 Wi-Fi에 맞게 `WiFi.begin(WIFI_SSID)`를 자동 선택합니다.
- ARCL의 `End of commands`를 받아야 인증 완료로 판정합니다.
- `faultsGet`과 `queryMotors` 결과가 준비되기 전에는 운행 명령을 거부합니다.
- 경로 운행 180초, 컨베이어 5초, ARCL 로그인/진단 타임아웃이 있습니다.
- `WaitState` 완료, 경로 완료, 서버·Wi-Fi·ARCL 단절 시 컨베이어를 정지합니다.
- 서버가 운행 중 끊기면 LD-90에 `stop`을 보내는 fail-safe가 있습니다.
- D2가 운행 중 올바른 방향으로 바뀌면 이송 완료로 판정하여 컨베이어를 조기 정지합니다.
- 동적 `String` 누적 대신 길이가 제한된 문자 버퍼를 사용합니다.
- 최신 서버의 6단계 순서와 `RESET_SEQUENCE`, `arrived` 응답을 지원합니다.

## 업로드 전 AMR 담당자 확인 항목

1. MobilePlanner의 ARCL Server Setup 암호가 정말 `adept`인지 확인합니다. `1234`라면 `ARCL_PASSWORD` 한 줄만 수정합니다.
2. 지도에 `ROUTE_ST1`, `ROUTE_ST2`, `ROUTE_ST3`가 정확히 존재하는지 확인합니다.
3. 각 경로에 제품 이송용 `WaitState`가 하나 이상 있는지 확인합니다.
4. D10=FWD, D11=REV와 HIGH 활성 방식이 실제 절연 입력 회로와 맞는지 확인합니다.
5. D2가 물체 감지 시 LOW인지 확인합니다.

`REQUIRE_OBJECT_SENSOR_CONFIRMATION`은 현재 `false`입니다. D2 설치 위치와 극성을 실제로 검증한 뒤 `true`로 바꾸면 센서 확인 없이는 `arrived`를 보내지 않는 엄격 모드가 됩니다.

## 권장 시험 순서

1. 기존 서버를 종료하여 TCP 5000 포트 중복을 없앱니다.
2. 받은 최신 서버 중 `Server_admin_Web_AMR.py`를 실행합니다.
3. 이 스케치를 UNO R4 WiFi에 업로드하고 시리얼 모니터를 115200 baud로 엽니다.
4. 다음 문자열을 확인합니다.

```text
FIRMWARE 2026-08-06-amr-server-bridge-v2
WIFI_CONNECTED ip=...
ADMIN_CONNECTING 192.168.0.168:5000
ARCL_CONNECTING 192.168.0.10:7171
STATUS LD90_ARCL_ONLINE auth=VERIFIED
STATUS FAULT_SCAN_COMPLETE faults=0
STATUS MOTORS_READY confirmed=queryMotors
```

5. 먼저 Web HMI에서 `amr STATUS`를 전송합니다.
6. 비상정지 상태, 이동 경로, 사람·장애물, 컨베이어 배선을 확인합니다.
7. 자동 생산 전에 단일 시험으로 `amr RESET_SEQUENCE`, 이어서 `amr RUN ROUTE_ST1 FWD`를 전송합니다.
8. LD-90 경로 이동, WaitState에서 D10 출력, D2 상태 변화, 최종 `arrived route=ROUTE_ST1 step=1`을 확인합니다.

`ERR ARCL_AUTH_TIMEOUT`이면 ARCL 암호부터 확인해야 합니다. `ERR DIAGNOSTIC_TIMEOUT`이면 LD-90 ARCL 버전에서 `faultsGet` 응답이 어떻게 나오는지 시리얼 로그를 확보해야 합니다. `ERR MOTORS_NOT_CONFIRMED`이면 물리적 E-stop과 안전 상태를 확인한 뒤 `amr PREPARE`, `amr ARM`을 차례로 보냅니다.

서버의 자동 생산 코드는 현재 `ERR` 응답 및 장시간 무응답을 타임아웃으로 해제하지 못합니다. 첫 실기 시험은 반드시 위의 단일 경로 시험으로 성공을 확인한 뒤 진행해야 합니다.
