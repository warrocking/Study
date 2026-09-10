# AMR을 활용한 자동차 상·하부체 생산·이송 공정

ABB 로봇 3대(3abb/4abb/5abb), Omron LD-90 AMR(Arduino UNO R4 WiFi 브릿지),
중앙 Python 관리 서버, PLC를 TCP 소켓으로 연동한 자동차 조립 자동화 프로젝트입니다.

로봇이 자체 TCP 서버를 열고, 로봇 옆 노트북의 Python 중계기가 로봇과 중앙 서버 사이를
릴레이합니다. 중앙 서버는 로봇의 `ReadyForPickup` 과 AMR의 도착 이벤트를 매칭해
`AmrArrived` 를 내려주는 방식으로 출고를 게이팅합니다.

## 폴더 구성

| 경로                                | 설명                               |
| --------------------------------- | -------------------------------- |
| `Final_Ver07/`                    | 최종 버전 (Server / Rapid / Arduino) |
| `Final_Ver01/` \~ `Final_Ver06/`  | 개발 과정 버전 이력                      |
| `NEXT_PROJECT_KICKOFF_PROMPT.md`  | 프로젝트에서 겪은 문제와 해결 과정 정리           |
| `Startup_Order_Resilience_Study/` | 기동 순서·복원력 검토 자료                  |
