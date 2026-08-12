# 안전·보안 경계

## RAPID에 남겨야 할 책임

- 승인된 목표점과 속도 범위
- tool/workobject와 robot configuration 검증
- 센서·PLC·가드 인터록
- 모션 실행, 정지, 오류 처리와 안전한 복귀
- 알 수 없는 명령의 기본 거부

## Python 서버가 맡기 좋은 책임

- 작업 ID, 레시피와 업무 데이터 검증
- 사용자 API, 기록, 관측과 알람
- RWS/Socket 프로토콜 어댑터
- 중복 명령 억제와 timeout 정책
- 장치 상태를 사용자에게 표현

## Tailscale이 제공하는 것과 제공하지 않는 것

제공: tailnet 장치 신원, 암호화된 private connectivity, subnet route, grants 기반 접근 제어.

제공하지 않음: 로봇 안전 정지, 기능 안전, 결정론적 실시간 통신, 애플리케이션 명령 권한, RAPID 인터록.

## 실제 컨트롤러 쓰기 전 승인 게이트

1. 자동 테스트와 Mock 성공
2. RobotStudio Virtual Controller에서 동일 명령 성공
3. 읽기 전용 RWS로 버전·모드·task 상태 확인
4. 최소 권한 계정, TLS 검증, grants/방화벽 확인
5. 현장 책임자의 모션·I/O·복구 절차 승인
6. 수동 모드·저속·단계 실행으로 목표점과 중간 경로 확인
7. command allowlist와 명령별 precondition 활성화
8. 백업과 rollback 연습 완료

## 금지 기본값

- 실제 RWS write 자동 활성화
- 인증서 검증 영구 비활성화
- 모든 tailnet 사용자에게 모든 포트 허용
- 무제한 frame, 무기한 read, 무한 재시도
- command ID 없이 동작 명령 재전송
- Python 서버를 안전 PLC 또는 실시간 모션 제어기로 취급
