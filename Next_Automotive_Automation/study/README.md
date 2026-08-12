# 자동차 자동화 공정 — 서버/RAPID/네트워킹 학습 패키지

2026-08-09~10 밤 동안 만든 학습 자료 모음입니다. 결정된 설계 문서가 아니라
**공부 자료**이며, 실제 설계 문서(SYSTEM_REQUIREMENTS.md 등)는 팀 상황이
확정된 뒤 별도로 작성합니다.

## 무엇부터 볼까

1. **`../docs/Server_Architecture_Study.docx`** (어제 먼저 만든 것) — 서버
   아키텍처 심화: ISA-95/ISA-88, 이벤트 소싱, 오픈소스·논문 사례.
2. **`pptx/01_RAPID_기초.pptx`** → **`pptx/04_Python_서버_통합설계.pptx`**
   — 순서대로 보면 RAPID 문법부터 우리 서버 설계까지 이어집니다. (총 65장)
3. **`docx/01_RAPID_서버_종합교재.docx`** — PPT 내용을 풀어쓴 상세 텍스트북.
4. **`docx/02_실습_워크북.docx`** — `code/`의 Mock Controller로 직접
   손을 움직이는 실습 6개 + 해답. **모든 해답은 실제로 코드를 실행해서
   검증했습니다.**
5. **`docx/03_명령어_참고서.docx`** — 실습 중 옆에 펴놓고 찾아보는 요약표
   + 트러블슈팅 체크리스트 + 전체 출처(검증 상태 포함).
6. **`code/`** — 실제로 실행·테스트까지 완료한 Mock ABB Controller
   (`python -m pytest -v` → 13개 전부 통과).

## 이 자료의 특징과 한계

- **ABB 공식 API(RWS, EGM) 관련 내용은 실제 웹 검색으로 검증**했고, 확인
  못 한 항목은 "❌ 확인 안 됨"으로 명확히 표시했습니다. 실습 전 실제
  컨트롤러/최신 공식 문서로 재확인하세요.
- **RobotStudio Virtual Controller를 이용한 로컬 검증은 하지 않았습니다**
  (이 환경에는 RobotStudio를 실행할 도구가 없습니다). RAPID 코드 예시는
  문법 참고용이며, 실제 컨트롤러에 넣기 전 RobotStudio에서 구문 검사가
  필요합니다.
- **Mock Controller 코드는 실제로 실행하고 pytest로 검증**했습니다 —
  이 부분은 "설명"이 아니라 "동작 확인된 코드"입니다.

## 폴더 구조

```
study/
├── README.md          (이 파일)
├── pptx/               PPT 4개, 총 65슬라이드
├── docx/               Word 3개
└── code/                Mock ABB Controller + pytest (13개 테스트 통과)
```
