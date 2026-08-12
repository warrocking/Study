# Mock ABB Controller — 학습용 코드 프로젝트

실제 ABB 로봇 없이도, 0723_AMR_Project/Final_Ver07의 실제 프로토콜
(`ReadyForPickup` / `AmrArrived` / `ConveyDone` / `EVENT PICKUP_ARRIVED`)을
단순화해서 손으로 만져볼 수 있게 만든 학습용 코드입니다.

**이 코드는 실제 프로젝트 코드가 아니라 학습 자료입니다.** 실제 서버/RAPID
코드는 여전히 `0723_AMR_Project/Final_Ver07/`이 기준입니다.

## 구성

```
mock_abb_controller/
├── protocol.py      # TCP 메시지 프레이밍 + COMMAND/EVENT/STATUS 파싱 (학습 자료 3부 3.4절)
├── orchestrator.py  # "출고 허가" 판단 로직 — 1차 프로젝트 핵심 사고를 막는 코드 (3부 3.2절)
└── mock_station.py  # 3abb/5abb 흉내를 내는 독립 실행형 TCP 서버
tests/
├── test_protocol.py     # 메시지 프레이밍 회귀 테스트
└── test_orchestrator.py # 출고 허가 로직 회귀 테스트 (1차 프로젝트 사고 재현 시나리오 포함)
```

## 설치

```powershell
pip install pytest
```

## 테스트 실행 (검증됨 — 13개 전부 통과)

```powershell
cd Next_Automotive_Automation\study\code
python -m pytest -v
```

## Mock Station 직접 실행해보기

터미널 1 (가짜 3abb 실행):

```powershell
python mock_abb_controller\mock_station.py --station 3abb --port 6001 --units 2
```

터미널 2 (직접 만든 서버 대신 손으로 대화해보기 — PowerShell의 경우 아래처럼
간단한 파이썬 클라이언트를 새로 짜거나, `nc`/`ncat`이 있다면 그것으로 접속):

```powershell
python -c "
import socket
s = socket.create_connection(('localhost', 6001))
s.sendall(b'Start\n')
buf = b''
while True:
    buf += s.recv(4096)
    while b'\n' in buf:
        line, buf = buf.split(b'\n', 1)
        print('RECV:', line.decode())
        if line.startswith(b'ReadyForPickup'):
            unit = line.decode().split('=')[1]
            s.sendall(f'AmrArrived unit={unit}\n'.encode())
"
```

`mock_station.py`가 `ReadyForPickup unit=1` → `AmrArrived unit=1` →
`ConveyDone unit=1` → … → `Done` 순서를 실제로 주고받는 걸 눈으로 확인할 수
있습니다. 이게 바로 `docx/02_실습_워크북.docx`의 실습 1과 이어집니다.

## 왜 이 코드가 존재하는가

마스터 프롬프트 7절이 요구한 "ABB가 없어도 Ready/Done 신호를 발생시킬 수
있는 가상 중계기"의 최소 구현입니다. 실제 로봇을 붙이기 전에, 서버 쪽
오케스트레이션 로직을 이 Mock으로 먼저 검증할 수 있습니다.
