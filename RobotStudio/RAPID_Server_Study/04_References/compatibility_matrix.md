# 버전·연동 호환성 기준

| 영역 | 이 자료의 기준 | 실무 확인 사항 |
|---|---|---|
| RAPID | RobotWare 8 매뉴얼 중심 | RW6/7에서 명령 인자, 옵션, 오류 번호가 같은지 대상 매뉴얼 확인 |
| Controller | OmniCore / RW8 중심 | IRC5/RW6, OmniCore/RW7·8의 옵션과 시스템 설정 차이 확인 |
| RobotStudio | 2026.2 문서 기준 | 설치된 RobotStudio와 Virtual Controller RobotWare 버전 조합 확인 |
| RWS 1.x | RW6 계열 예제와 참고 문서 | Digest/session, `?json=1`, 리소스 경로를 버전 문서로 확인 |
| RWS 2.0 | RW7/8 계열 OpenAPI | HTTPS, versioned media type, HAL 응답과 UAS 권한 확인 |
| Socket Messaging | TCP byte stream | 컨트롤러 옵션, 허용 포트, RAPID Socket instruction 서명 확인 |
| EGM | 별도 주제 | RobotWare 옵션, UDP/protobuf 계약, 제어 주기와 안전 설계 필요 |
| Python | Python 3.12 | `uv.lock`으로 의존성 재현, 운영 OS와 인증서 저장소 확인 |
| Tailscale | subnet router + grants | route 승인, SNAT/return path, 방화벽, 태그 소유권, MagicDNS 확인 |

## 적용 원칙

1. 인터넷 코드 조각보다 설치된 RobotWare 버전의 ABB 공식 문서를 우선합니다.
2. 클라이언트 설정에 RWS 세대를 명시하고 응답 parser를 fixture로 테스트합니다.
3. 읽기 API로 버전·모드·task 상태를 확인한 뒤 제한된 쓰기로 승격합니다.
4. RobotStudio simulation 결과를 실제 로봇의 TCP, load, workobject, calibration과 동일하다고 가정하지 않습니다.
