# AMR 서버 자동 탐색 (UDP) — Server_admin_Web_ver02.py

`Server_admin_Web_ver02.py`는 `Server_admin_Web_AMR.py`(AMR 담당자가 전달한, AMR
명령 매핑이 완성된 버전)를 기준으로 만들었고, 여기에 **UDP 자동 탐색 응답
기능만** 추가했습니다. 기존 TCP 5000 로봇/AMR 서버, Flask 웹 HMI(8080), 자동
생산 오케스트레이션, SSE 로그 스트림은 전혀 건드리지 않았습니다.

## 왜 필요한가

Arduino(UNO R4 WiFi) 펌웨어(`AMR_Server_Bridge.ino`)는 지금 관리자 서버 주소를
`IPAddress ADMIN_SERVER_IP(192, 168, 0, 173)`로 **하드코딩**해서 접속합니다.
이 노트북의 IP가 바뀌면(DHCP 재할당, 다른 Wi-Fi 등) Arduino가 서버를 더 이상
찾지 못합니다.

그래서 서버가 UDP 5001번 포트에서 "누구 없나요?" 질문을 상시 대기하다가,
질문이 오면 "나 여기 있고 TCP는 5000번이야"라고 응답해주는 기능을 추가했습니다.

## 통신 규격

| 항목 | 값 |
|---|---|
| UDP 탐색 수신 포트 | 5001 (`0.0.0.0:5001`에 바인딩) |
| TCP 로봇/AMR 서버 포트 | 5000 (기존과 동일) |
| Arduino 요청 | `AMR_SERVER_DISCOVER_V1 device=amr` |
| 서버 응답 | `AMR_SERVER_V1 name=admin tcp_port=5000` |

응답 패킷에는 서버 IP를 문자열로 넣지 않습니다. Arduino는 UDP 응답이 도착한
패킷의 **발신 주소**를 그대로 서버 IP로 사용해야 합니다 (`WiFiUDP`에서
`Udp.remoteIP()`로 얻는 값). 이 방식이라야 이 노트북에 인터페이스가 여러
개(Wi-Fi/Tailscale/이더넷) 있어도 항상 Arduino가 실제로 패킷을 받은 경로의
주소로 응답받습니다.

## ⚠️ 중요 — 이것만으로는 "IP가 바뀌어도 자동 연결"이 완성되지 않습니다

지금 전달받은 `AMR_Server_Bridge.ino`에는 이 UDP 탐색을 실제로 사용하는
코드가 없습니다. `ADMIN_SERVER_IP`가 여전히 컴파일 타임에 고정된 값이고,
`connectAdminIfNeeded()`도 그 고정 주소로만 접속을 시도합니다.

**서버(이 파일)만 배포해서는 목적이 달성되지 않습니다.** Arduino 쪽에도
다음과 같은 대응 코드가 필요합니다 (별도 작업 필요, 이 파일 범위 밖):
1. `WiFiUDP`로 주기적으로(예: TCP 연결이 안 됐을 때) `AMR_SERVER_DISCOVER_V1 device=amr`를 브로드캐스트
2. `AMR_SERVER_V1 name=admin tcp_port=...` 응답을 받으면 `Udp.remoteIP()`를 서버 IP로 저장
3. 그 주소로 TCP 접속 (`ADMIN_SERVER_IP` 하드코딩 대신 이 값을 사용)
4. TCP 연결이 끊기면 다시 탐색부터 반복 (서버 IP가 바뀐 경우까지 커버)

## 실행

```bash
pip install flask   # 최초 1회
python Server_admin_Web_ver02.py
```

브라우저: `http://localhost:8080` (같은 네트워크의 다른 기기에서는
`http://<이 PC의 IP>:8080`)

## 시험 순서

1. **문법 확인**
   ```bash
   python -m py_compile Server_admin_Web_ver02.py
   ```

2. **서버 실행 후 콘솔에 다음이 뜨는지 확인**
   ```
   웹 HMI: http://localhost:8080  (로봇/AMR 접속용 TCP 포트: 5000, AMR 탐색 UDP 포트: 5001)
   ```

3. **TCP 5000이 살아있는지 확인** — 아무 터미널에서:
   ```bash
   python -c "import socket; socket.create_connection(('127.0.0.1',5000),timeout=3); print('OK')"
   ```

4. **웹 HMI 접속 확인** — 브라우저로 `http://localhost:8080` 열어서 화면이 뜨는지 확인.

5. **UDP 탐색 응답 확인** — 다른 터미널에서 (Arduino 대신 흉내):
   ```bash
   python -c "
   import socket
   udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   udp.settimeout(3)
   udp.sendto(b'AMR_SERVER_DISCOVER_V1 device=amr', ('<이 PC의 IP>', 5001))
   data, addr = udp.recvfrom(200)
   print('응답:', data.decode(), '보낸 주소:', addr)
   "
   ```
   `AMR_SERVER_V1 name=admin tcp_port=5000`이 찍히면 정상입니다.

6. **기존 amr TCP 등록 확인** — 실제 Arduino(또는 흉내 스크립트)가 TCP
   5000에 접속해서 첫 줄로 `amr`을 보내면, 서버 로그(웹 HMI 로그 패널 또는
   콘솔)에 `amr 연결됨: ...`이 뜨는지 확인.

7. **서버를 나중에 켜도 되는지 확인** — Arduino(또는 흉내 스크립트)를 먼저
   켠 상태에서 서버를 나중에 실행해도, 서버가 뜬 뒤 탐색 요청에 정상
   응답하는지 확인 (단, 위의 ⚠️ 항목대로 Arduino 쪽이 탐색을 실제로
   재시도하는 코드가 있어야 전체 흐름이 완성됩니다).

## Windows 방화벽 (필요 시 직접 실행하세요 — 자동으로 바꾸지 않았습니다)

TCP 5000은 이미 기존 서버로 접속이 되고 있었다면 방화벽 규칙이 있을
가능성이 높습니다. **UDP 5001은 새로 추가된 포트라 별도 허용이 필요할 수
있습니다.**

관리자 권한 PowerShell에서:

```powershell
New-NetFirewallRule -DisplayName "AMR UDP Discovery 5001" -Direction Inbound -Protocol UDP -LocalPort 5001 -Action Allow
```

또는 `netsh` (관리자 권한 cmd):

```cmd
netsh advfirewall firewall add rule name="AMR UDP Discovery 5001" dir=in action=allow protocol=UDP localport=5001
```

둘 중 하나만 실행하면 됩니다. 규칙을 지우려면:

```powershell
Remove-NetFirewallRule -DisplayName "AMR UDP Discovery 5001"
```

## 로그 예시

정상 탐색 시 (같은 주소의 반복 요청은 60초 안에는 다시 로그로 남기지 않음):

```
14:23:01  AMR discovery request: 192.168.0.55
14:23:01  AMR discovery response: tcp_port=5000
```

## 검증 완료 항목 (2026-08-06 기준)

- [x] `py_compile` 문법 검사 통과
- [x] TCP 5000 리스닝 + `amr` 등록 확인
- [x] Web 8080 접속 확인 (`GET /` 200 OK)
- [x] UDP 5001 리스닝 + 정확한 탐색 요청에 정확한 응답 확인
- [x] 잘못된 메시지(`GARBAGE` 등) 무시 확인 — 응답 없음
- [x] 지나치게 큰 패킷(600B, 4000B) 무시 확인 — **테스트 중 실제 버그 발견 및 수정**
      (아래 참고)
- [x] 같은 주소의 반복 탐색 요청 → 응답은 매번 정상, 로그만 제한됨 확인

### 테스트 중 발견/수정한 버그

`recvfrom()` 버퍼보다 큰 UDP 패킷이 들어오면 Windows(Winsock)는 POSIX와
달리 자르지 않고 `OSError`(WSAEMSGSIZE)를 던집니다. 처음 구현에서는 이걸
`except OSError: break`로 잡아서 **탐색 루프 자체가 조용히 종료**되어
버렸습니다(그 이후로는 정상 요청에도 응답 안 함). 수신 버퍼를 여유 있게
늘리고, `OSError`가 나도 서버가 정상 운영 중이면 그 패킷만 무시하고 계속
수신하도록 고쳐서 해결했습니다 (barrage 테스트로 재현 및 재검증 완료).
