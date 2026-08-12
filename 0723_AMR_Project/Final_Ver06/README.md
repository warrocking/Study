# Final_Ver06 통합본

## 결론

Final_Ver05는 3ABB의 두 번째 상부체를 AMR 없이 출고할 수 있는 경로가 남아
있었습니다. Final_Ver06은 다음 세 조건이 모두 맞아야만 3ABB/5ABB 출고 DO를
발생시키는 fail-closed 구조입니다.

1. ABB가 `ReadyForPickup unit=N`을 보냈다.
2. AMR이 `EVENT PICKUP_ARRIVED ... unit=N cycle=N ...`을 보냈다.
3. AMR 이벤트의 `run`, `station`, `step`이 현재 실행과 정확히 일치한다.

빈 플레이트 반납은 `EVENT RETURN_ARRIVED`라는 별도 이벤트이며 출고 허가 큐에
들어가지 않습니다.

## Final_Ver05에서 확인된 문제

- 3ABB `Car_Delivery()`가 `ReadyForPickup`과 `WaitForAmrArrived`보다 먼저
  `do05_Body_Docking_Done`을 출력했습니다. PLC가 이 신호를 기억한 상태에서
  반납 플레이트 센서가 들어오면 AMR이 떠난 뒤에도 출고가 시작될 수 있었습니다.
- 서버는 `ReadyForPickup unit=N`과 AMR `cycle=N`이 다르거나 필드가 없어도
  경고만 하고 `AmrArrived`를 그대로 보냈습니다.
- 3ABB/5ABB는 `AmrArrived` 문자열 앞부분만 검사하여 잘못된 unit도 수락했습니다.
- AMR의 도착 이벤트 이름이 픽업/반납 공통이었고, 서버는 진단용
  `STATUS CONVEYOR_START`를 출고 허가 근거로 사용했습니다.
- `ConveyDone`에 unit 번호가 없어 이전 실행 메시지와 현재 실행 메시지를
  구분할 수 없었습니다.
- 픽업 매칭 스레드가 `ConveyDone`을 무기한 기다려 다음 실행의 신호와 섞일 수
  있었습니다.
- 자동 생산 시작 시 필수 중계기 연결과 각 명령 전송 결과를 충분히 확인하지
  않았습니다.

## Final_Ver06 변경 내용

### Arduino/AMR/AMR.ino (V26)

- `PICKUP_ARRIVED`: 3ABB/5ABB에서 제품을 받으러 온 경우만 전송
- `RETURN_ARRIVED`: 3ABB/5ABB에 빈 플레이트를 반납하는 경우만 전송
- `TRANSFER_ARRIVED`: 4ABB 이송 방문
- 모든 픽업 이벤트에 `station`, `unit`, `cycle`, `step`, `run` 포함
- 서버의 정확한 `ARRIVAL_ACK`을 받을 때까지 2초마다 픽업 이벤트 재전송
- `STATUS CONVEYOR_START`는 진단 로그로만 유지

### Rapid/3abb.mod

- `Car_Delivery()` 내부의 조기 `do05` 제거
- 정확한 `AmrArrived unit=N`을 받은 다음에만 `do05` 0.2초 출력
- 다른 unit의 도착 메시지는 거부
- `ConveyDone unit=N` 전송

정상 순서:

```text
제품을 출고 위치에 놓음
→ ReadyForPickup unit=N
→ WaitForAmrArrived(N)
→ AmrArrived unit=N 수신
→ do05_Body_Docking_Done 0.2초
→ ConveyDone unit=N
```

### Rapid/5abb.mod

- 정확한 `AmrArrived unit=N`만 수락
- `ConveyDone unit=N` 전송
- 기존처럼 `do16_Dilivery_Start`는 AMR 확인 뒤에 출력

### Server/Server_admin_Web.py

- V26의 `PICKUP_ARRIVED`만 출고 허가 후보로 사용
- `RETURN_ARRIVED`는 로그만 남기고 출고 허가에 사용하지 않음
- `station/unit/cycle/step/run` 완전 일치 검사
- 누락이나 불일치 시 `AmrArrived`를 보내지 않는 fail-closed 처리
- 중복 픽업 이벤트는 ACK만 재전송하고 한 번만 매칭
- 실행 세대(generation)를 추가하여 이전 실행 메시지 폐기
- `ConveyDone unit=N` 검증
- unit 1과 2의 유효한 ConveyDone이 모두 있어야 ABB의 최종 `Done` 수락
- 자동 생산 시작 전에 3abb/4abb/5abb/amr 연결 확인
- ABB 명령 전송 실패 시 자동 생산 시작 중단

### 중계기와 4ABB

3ABB/4ABB/5ABB 중계기 및 4ABB RAPID의 공정 동작은 Final_Ver05에서 변경하지
않았습니다. 이번 문제의 수정 범위는 도착 종류, unit 매칭 및 출고 허가입니다.

## 반드시 한 세트로 적용할 파일

- `Arduino/AMR/AMR.ino`
- `Rapid/3abb.mod`
- `Rapid/5abb.mod`
- `Server/Server_admin_Web.py`
- 각 현장 노트북의 해당 `Server/*_connector.py`

Ver05 서버나 V25 아두이노를 일부 섞으면 V26 명시적 이벤트가 없어 출고 허가가
나오지 않습니다. 이는 잘못 출고하는 것보다 멈추는 쪽을 택한 의도적인 동작입니다.

## 문제 재현 시나리오의 기대 결과

```text
AMR: RETURN_ARRIVED station=3abb unit=1 ...
PLC: 반납 플레이트 감지
3ABB: 두 번째 제품 준비 후 ReadyForPickup unit=2
서버: unit=2 픽업 도착을 기다림
결과: do05 출력 없음, 출고 컨베이어 정지 유지

이후 실제 두 번째 픽업:
AMR: PICKUP_ARRIVED station=3abb unit=2 cycle=2 step=1 run=...
서버: AmrArrived unit=2
3ABB: do05 0.2초
결과: 그때만 출고 컨베이어 작동
```

## 검증 결과

- Python 전체 파일 `py_compile/compileall` 통과
- UNO R4 WiFi용 Arduino 컴파일 통과
- 자동 테스트에서 다음 항목 통과
  - 반납 도착으로 두 번째 제품을 출고하지 않음
  - 잘못된 unit 및 이전 run 거부
  - 중복 픽업은 한 번만 허가
  - 2회 전체 순서에서 3ABB/5ABB 픽업 4회만 허가
  - 3ABB `do05`가 AMR 대기 뒤에 위치함을 정적 확인

테스트 실행:

```powershell
python -m unittest discover -s C:\dev\Study\0723_AMR_Project\Final_Ver06\Tests -v
```

## 현장 적용 전 주의

- PLC에서 `do05_Body_Docking_Done`이 실제로 3ABB 출고 시작 입력(X1005로
  추정)에 매핑되는지 확인해야 합니다.
- 첫 시험은 제품 없이 또는 컨베이어 동력 분리 상태에서 신호 모니터링부터
  수행하세요.
- 웹의 `정지 요청`은 비상정지 회로가 아닙니다. 사람이나 장비 위험 시에는
  반드시 실제 비상정지와 장비 안전회로를 사용하세요.
- RAPID는 RobotStudio/실제 컨트롤러 컴파일을 이 환경에서 수행할 수 없으므로,
  적용 전에 RobotStudio의 구문 검사와 I/O 매핑 확인이 필요합니다.
- 3ABB 코드에는 PLC 완료 신호가 일정 시간 안에 없으면 완료로 간주하는 기존
  타임아웃이 남아 있습니다. 이번 출고 경합 수정과는 별도이지만 실제 설비용으로
  쓸 경우 담당자와 안전성을 다시 검토해야 합니다.
