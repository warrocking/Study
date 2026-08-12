# AMR Arduino bridge sketches

> 현재 기본 활성 코드는 `Server_Amr.ino`입니다. 같은 폴더의
> `AMR_IO_Bridge.ino` 첫 부분에서 `AMR_IO_BRIDGE_USE_SERVER_AMR`가 `1`로
> 설정되어 두 파일이 충돌하지 않도록 기존 Digital I/O 구현은 컴파일에서
> 제외됩니다. 아래의 기존 Digital I/O 설명은 이 값을 `0`으로 바꿨을 때만
> 적용됩니다.

## 현재 활성 코드: Server_Amr.ino

`Server_Amr.ino`는 `ROBOT_MA2_2G`에서 중앙 서버 노트북의
`192.168.0.168:5000`으로 무한 재접속하며 이름 `amr`로 등록합니다. LD-90은
MobilePlanner의 Outgoing ARCL 설정을 통해 Arduino의 고정 IP와 TCP 5353으로
접속해야 합니다.

관리자 서버에서 `all Start`를 보내면 Arduino는 수신한 `Start`를
`patrolOnce 경로1`으로 변환합니다. 개별 시험은 다음과 같습니다.

```text
amr STATUS
amr GET_ROUTES
amr GET_MACROS
amr Start
amr STOP
amr CONVEYOR_TEST
```

`CONVEYOR_TEST`는 D7을 1초만 켜며, 매크로 연동 컨베이어 출력도 7초 후 강제로
꺼집니다. Wi-Fi, 관리자 서버 또는 LD-90 연결이 끊겨도 D7은 즉시 꺼집니다.

## 이전 코드: AMR1 TCP–Digital I/O Bridge

`AMR_IO_Bridge.ino`는 Arduino UNO R4 WiFi를 `TestServer_admin.py`와 Omron LD-90 사이의 중계기로 사용하기 위한 독립 스케치입니다.

## 통신 구조

```text
TestServer_admin.py (192.168.3.91:5000)
              ▲
              │ Wi-Fi TCP, 줄바꿈 문자열
              │ 첫 줄: AMR1
              ▼
      Arduino UNO R4 WiFi
              │
              │ 절연 릴레이/옵토커플러/산업용 I/O 인터페이스
              ▼
        LD-90 DIGITAL I/O
```

Arduino는 `TestServer_admin.py`에 TCP 클라이언트로 접속한 직후 `AMR1\n`을 전송합니다. 따라서 관리자 서버에서는 다른 ABB 중계기와 동일하게 이름으로 명령을 보낼 수 있습니다.

## 관리자 명령

`TestServer_admin.py` 터미널에서 다음과 같이 입력합니다.

```text
AMR1 STATUS
AMR1 ROUTE1
AMR1 ROUTE2
AMR1 ROUTE3
AMR1 STOP
```

지원 명령은 다음과 같습니다.

| 명령 | 동작 |
|---|---|
| `ROUTE1`, `MOVE_ST1` | D2에 Route 1 펄스 출력 |
| `ROUTE2`, `MOVE_ST2` | D3에 Route 2 펄스 출력 |
| `ROUTE3`, `MOVE_ST3` | D4에 Route 3 펄스 출력 |
| `STOP`, `END` | D5에 일반 정지 요청 펄스 출력 |
| `STATUS` | 네트워크, 출력 펄스 및 피드백 상태 보고 |
| `PING` | 연결 확인용 `PONG` 보고 |
| `ALL_OFF` | 모든 명령 출력을 즉시 비활성화 |
| `HELP` | 지원 명령 보고 |

일반적인 `START` 명령은 의도적으로 지원하지 않습니다. ABB 전체 시작에 쓰는
`all Start`가 AMR까지 예기치 않게 움직이는 것을 막기 위한 조치입니다. AMR 이동은
항상 `AMR1 ROUTE1`처럼 대상과 경로를 명시해 보내십시오.

명령은 대소문자를 구분하지 않으며 한 줄에 하나씩 처리됩니다. 출력 펄스 기본 길이는 300ms입니다.

## 기본 핀 배치

### Arduino 출력 → LD-90 입력

| Arduino | 의미 |
|---|---|
| D2 | Route 1 요청 |
| D3 | Route 2 요청 |
| D4 | Route 3 요청 |
| D5 | 일반 Stop 요청 |

### LD-90 출력 → Arduino 입력

| Arduino | 의미 |
|---|---|
| D6 | READY |
| D7 | BUSY |
| D8 | DONE |
| D9 | FAULT |

피드백 입력은 기본적으로 `INPUT_PULLUP`, active-low로 설정되어 있습니다. 인터페이스 출력이 접점을 닫거나 오픈컬렉터로 GND에 연결될 때 활성화되는 구성입니다.

실제 AMR 배선이 다르면 스케치 상단의 핀 번호와 다음 값을 반드시 수정해야 합니다.

```cpp
COMMAND_ACTIVE_LEVEL
FEEDBACK_PIN_MODE
FEEDBACK_ACTIVE_LEVEL
COMMAND_PULSE_MS
```

## 네트워크 설정

스케치에는 현재 총괄 서버 노트북 `DESKTOP-12MCCAQ`의 `ROBOT3_2G` Wi-Fi 주소인 `192.168.3.91`이 들어 있습니다.

```cpp
IPAddress ADMIN_SERVER_IP(192, 168, 3, 91);
```

이 주소가 DHCP로 변경되면 스케치도 수정해야 하므로 서버 노트북에 DHCP 예약 또는 고정 IP를 설정하는 것이 좋습니다.

ABB 옆 노트북은 Tailscale 프로그램을 실행할 수 있으므로 `100.109.178.123`으로 접속할 수 있지만, UNO R4 WiFi는 기본 상태에서 Tailscale 네트워크에 직접 참여하지 않습니다. Arduino와 서버 노트북이 `ROBOT3_2G`에 같이 연결되어 있다면 서버 노트북의 `192.168.3.91` 주소를 사용해야 합니다.

## 서버에 보고되는 메시지 예시

```text
ONLINE device=AMR1 ip=192.168.3.120 firmware=IO_BRIDGE_V1
ACK ROUTE1 PULSE_STARTED duration_ms=300
EVENT ROUTE1 PULSE_FINISHED
EVENT IO_CHANGED signal=READY active=1 READY=1 BUSY=0 DONE=0 FAULT=0
STATUS WIFI=CONNECTED SERVER=CONNECTED PULSE=NONE READY=1 BUSY=0 DONE=0 FAULT=0 ...
```

`ACK ... PULSE_STARTED`는 Arduino 출력이 발생했다는 의미일 뿐, LD-90이 실제로 이동을 완료했다는 뜻은 아닙니다. 실제 완료 판단은 `READY`, `DONE`, `FAULT` 등 AMR 피드백 입력으로 해야 합니다.

## 업로드 전 필수 확인

1. Arduino IDE에서 보드를 `Arduino UNO R4 WiFi`로 선택합니다.
2. LD-90의 네 개 명령 입력이 MobilePlanner에서 올바른 Route/Macro에 연결됐는지 확인합니다.
3. 완성된 AMR 배선과 D2~D9의 대응 관계를 확인합니다.
4. LD-90 입력 Bank의 NPN/PNP 및 Common 결선을 확인합니다.
5. Arduino와 LD-90 사이에 적합한 절연 인터페이스가 있는지 확인합니다.
6. 실제 AMR을 움직이기 전에 릴레이 또는 인터페이스 출력만 측정해 각 명령이 정확히 한 번, 300ms 동안 발생하는지 확인합니다.

## 안전 주의

- Arduino GPIO를 LD-90 DIGITAL IO에 직접 연결하지 마십시오.
- D5의 `STOP`은 공정용 일반 정지 요청일 뿐 안전 기능이나 E-Stop이 아닙니다.
- 실제 운행 테스트는 LD-90의 물리적 E-Stop에 즉시 접근할 수 있는 상태에서 수행해야 합니다.
- 출력은 전원 투입, 서버 단절 및 Wi-Fi 단절 시 비활성 상태로 돌아가도록 설계되어 있습니다.
