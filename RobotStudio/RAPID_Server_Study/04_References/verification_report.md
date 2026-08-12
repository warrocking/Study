# 산출물 검증 보고서

검증일: 2026-08-10

## Python/RAPID 코드

- `uv run pytest -q`: 13 passed
- `uv run ruff check .`: All checks passed
- 비실패 경고 1개: 설치된 FastAPI test client가 Starlette의 향후 `httpx2` 전환을 안내하는 deprecation warning
- loopback 테스트가 실제 asyncio listener를 열어 CRLF frame의 split/merge와 응답 수명주기를 확인
- 실제 ABB 하드웨어 쓰기 테스트는 안전상 실행하지 않았고 기본 설정도 비활성화

## PowerPoint

| 파일 | 슬라이드 | Speaker notes | 렌더링 | Overflow 검사 |
|---|---:|---:|---|---|
| 01_RAPID_RobotStudio_기초.pptx | 29 | 29 | 통과 | 통과 |
| 02_RAPID_모션_좌표계_IO_오류.pptx | 34 | 34 | 통과 | 통과 |
| 03_TCP_HTTP_Tailscale_네트워크.pptx | 33 | 33 | 통과 | 통과 |
| 04_Python_Server_RAPID_통합.pptx | 41 | 41 | 통과 | 통과 |

총 137장을 1280×720 PNG로 렌더링하여 전체 montage와 코드·모션·통신 슬라이드를 원본 크기로 육안 확인했습니다.

## Word

| 파일 | 예상 페이지 | 구조 감사 | 접근성 감사 |
|---|---:|---|---|
| 01_ABB_RAPID_Python_Server_종합교재.docx | 75 | 통과 | high/medium/low 0 |
| 02_RAPID_Server_단계별_실습워크북.docx | 39 | 통과 | high/medium/low 0 |
| 03_RAPID_Server_명령어_문제해결_빠른참조.docx | 27 | 통과 | high/medium/low 0 |

구조 감사 항목: ZIP integrity, Letter page size, 1-inch margins, required styles, real numbering definitions, placeholder scan, fixed table geometry, repeated table header rows.

환경에 LibreOffice가 설치되어 있지 않았고 Microsoft Word COM PDF export도 `RPC_E_CALL_REJECTED`로 실패하여 DOCX의 canonical page-image render는 실행하지 못했습니다. 이 제한은 최종 전달 시 명시합니다.

## 파일 해시

최종 정리 후 `checksums.sha256`에 기록합니다.
