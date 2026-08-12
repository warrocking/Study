# Server_admin_Web V05

## 변경 목적

4abb는 `Start`를 한 번 받으면 PLC의 출고 컨베이어 끝 센서를 계속 감시합니다. 물체가 감지되면 컨베이어를 역기동하여 제품을 들여오고 적재합니다. 이 무한 대기는 정상 동작입니다.

V05는 4abb의 RAPID나 중계기 코드를 변경하지 않습니다. 중앙 Web 서버의 자동 생산 시작 절차에만 다음 동작을 추가합니다.

1. 자동 생산 시작 시 4abb 연결 여부를 확인합니다.
2. 4abb에 `Start`를 한 번 보냅니다.
3. 4abb의 `Done`은 기다리지 않습니다.
4. 같은 서버 실행 중 다음 자동 생산을 시작해도 4abb에 `Start`를 중복 전송하지 않습니다.
5. 기존 3abb·5abb 시작 및 완료 대기와 AMR 이송 순서는 유지합니다.
6. 새 아두이노와 맞도록 AMR 명령은 `RUN ROUTE_ST...` 형식을 사용하고, 자동 생산 시작 시 `RESET_SEQUENCE`를 전송합니다.

## 실행

기존 `Server_admin_Web.py`와 동시에 실행하면 TCP 5000 및 Web 8080 포트가 충돌합니다. 기존 서버를 종료하고 다음 하나만 실행합니다.

```powershell
cd C:\dev\Study\0723_AMR_Project\Server
python Server_admin_Web_V05.py
```

브라우저 주소:

```text
http://localhost:8080
```

## 예상 로그

첫 번째 자동 생산 시작:

```text
4abb에 Start 전송 - PLC 센서 감시·적재 무한 대기 활성화
4abb -> Start
4abb 수신·적재 대기 시작 요청 완료 (4abb Done 응답은 기다리지 않음)
amr -> RESET_SEQUENCE
자동 생산 시작 - 목표 ...대
```

같은 서버 실행 중 두 번째 자동 생산 시작:

```text
4abb는 이미 PLC 센서 감시·적재 대기 상태입니다. Start를 다시 보내지 않습니다.
```

4abb가 연결되지 않았다면 자동 생산을 시작하지 않고 오류 로그를 표시합니다. 수동 명령의 `4abb Start`와 `all Start`도 성공적으로 전송되면 4abb가 활성화된 것으로 기록됩니다.

## 주의

V05는 기존 `Server_admin_Web.py`를 가져와 필요한 부분만 확장하는 파일이므로 두 파일이 같은 폴더에 있어야 합니다. 4abb RAPID가 재시작되어 다시 `Start`가 필요할 때는 Web HMI에서 `4abb Start`를 수동으로 전송하면 됩니다.
