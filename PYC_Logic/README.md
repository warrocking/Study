# PYC_Logic

PYC_basic 장비 학습용 프로젝트 구조입니다.

## 폴더 구조
- `notebooks/`: 실험/테스트용 Jupyter 노트북
- `src/`: 최종 정리된 실행 코드
- `src/examples/`: 기존 예제 백업/복사본
- `data/raw/`: 원본 측정 데이터
- `data/logs/`: 실행 로그/결과 파일
- `docs/`: 사용법/회로/운영 메모

## 권장 작업 흐름
1. 아이디어 실험: `notebooks/*.ipynb`에서 `Shift+Enter`
2. 동작 안정화: 필요한 부분만 `src/*.py`로 정리
3. 재사용 함수 분리: `src/` 내부에서 함수/모듈화
4. 결과 기록: 측정값은 `data/logs/`에 저장

## VSCode + Remote Jupyter
- 연결 방법은 `docs/VSCode_Jupyter_Setup.md` 참고
- 연결 후 `.ipynb` 파일에서 커널을 원격 서버로 선택

## Git 커밋 규칙 (간단)
- `feat:` 기능 추가
- `fix:` 버그 수정
- `docs:` 문서 수정
- `refactor:` 구조 개선 (동작 변화 없음)

예시:
- `feat: add distance based led control notebook`
- `fix: debounce switch read logic`
