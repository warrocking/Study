# RAPID / VSCode 세팅 로그

## 이 문서를 읽는 AI/사람에게

이 문서는 "설명서"가 아니라 **로그**입니다. 시간순으로 아래에 쌓입니다.
같은 목적(예: "RAPID 자동완성 켜기")을 위해 여러 설정을 시도한 기록이 섞여 있을 수 있습니다.

**규칙: 각 항목마다 반드시 상태 표시가 붙습니다.**

- `✅ 현재 사용 중` — 지금 실제로 적용돼 있는 설정. 새 컴퓨터/새 사용자는 이것만 가져다 쓰면 됩니다.
- `❌ 폐기됨` — 과거에 시도했지만 이유가 있어 버린 설정. **겉보기에 비슷하거나 더 간단해 보여도
  절대 이걸 대신 적용하지 마세요.** 폐기 이유가 같이 적혀 있으니 반드시 읽을 것.
- `🔎 미확인/추정` — 왜 이렇게 돼 있는지 기록이 없어서 추측만 있는 상태. 바꾸기 전에 먼저
  실기(RobotStudio + 실제 로봇/시뮬레이터)로 검증할 것.

새 컴퓨터에서 세팅할 때: 이 문서를 위에서 아래로 다 읽고, **각 설정 항목의 가장 최근 `✅` 항목만**
적용하세요. 그 위에 있는 `❌` 항목은 "이미 해봤는데 안 됐던 것" 목록이니 다시 시도하지 마세요.

---

## 2026-07-24 — RAPID 자동완성이 안 뜨는 문제 조사 및 정리

### 배경

사용자가 `MODULE (이름)` 다음 줄에서 `END`를 치면 `ENDMODULE`이 자동완성으로 떠야 하는데
전혀 안 뜬다고 보고. 확장 프로그램은 이미 설치돼 있었음.

### 발견 1 — 설정이 워크스페이스 루트에서만 적용됨

**✅ 현재 사용 중**: `abb-rapid-pack.*` 및 `"[rapid]"` 에디터 설정(quickSuggestions,
tabCompletion 등)을 다음 3곳 모두의 `.vscode/settings.json`에 동일하게 복사해 둠:

- `Study/.vscode/settings.json` (저장소 루트)
- `Study/RobotStudio/.vscode/settings.json` (기존)
- `Study/0723_AMR_Project/.vscode/settings.json` (신규)

**이유**: VSCode는 "현재 열려 있는 워크스페이스 루트 폴더"의 `.vscode`만 읽는다. 하위 폴더의
`.vscode/settings.json`은 그 하위 폴더 자체를 워크스페이스 루트로 열지 않는 이상 무시된다.
이 저장소는 여러 하위 프로젝트를 한 폴더(`C:\dev\Study`)로 묶어서 열 때가 많으므로,
RAPID 관련 `.mod` 파일이 어디 있든(`RobotStudio/`, `0723_AMR_Project/`, 앞으로 생길 새 폴더 등)
자동완성이 되게 하려면 **`.mod` 파일이 존재할 수 있는 모든 폴더에 같은 설정을 복사해둬야 한다.**
(VSCode가 상위 설정을 하위로 상속하는 기능은 없음 — 다중 루트 워크스페이스로 명시적으로
묶지 않는 한 각 폴더가 독립적임.)

**🔎 미확인/추정**: 더 근본적인 해법은 `Study.code-workspace`를 멀티루트 워크스페이스로 만들어
`RobotStudio`, `0723_AMR_Project` 등을 명시적 폴더로 추가하고 워크스페이스 레벨 `settings`에
한 번만 적는 것. 현재 `Study.code-workspace`는 `CPP`, `Python`만 포함하고 있어 이 프로젝트와
무관해 손대지 않음. 이후 세션에서 "코드 중복 없애고 싶다"는 요청이 오면 이 방식을 검토할 것.

### 발견 2 — 확장 프로그램 두 개가 같은 언어 ID(`rapid`)를 동시에 등록하고 있었음

**❌ 폐기됨**: `verbotics.abb-rapid` (v0.1.1, 2018년 "Initial release" 이후 사실상 업데이트 없는
구형 확장) — grammar만 제공(102줄짜리 얕은 tmLanguage), 스니펫/포맷터/진단 없음.
`.mod`/`.prg`/`.sys` 확장자에 대해 언어 ID `rapid`를 등록.

**이유(폐기 사유)**: `Maxzurek.abb-rapid-pack`도 **동일하게 언어 ID `rapid`를 직접 등록**하고
같은 확장자(`.mod` 등)를 점유한다. 확장 두 개가 같은 언어 ID의 "기본 언어 정의"
(`language-configuration.json` — 들여쓰기 규칙, 자동 괄호닫기 등)를 동시에 등록하면 VSCode가
어느 쪽 설정을 실제로 적용할지 문서화된 우선순위가 없어 세션마다 달라질 수 있음. 사용자가 겪은
"자동완성이 어떨 땐 되는 것 같고 어떨 땐 안 되는 느낌"의 잠재 원인 중 하나로 판단.
`abb-rapid-pack`이 grammar/스니펫/포맷터/진단/네비게이션까지 완전 상위호환이라 `verbotics`를
따로 쓸 이유가 없음.

**조치**: `C:\Users\user\.vscode\extensions\verbotics.abb-rapid-0.1.1` 폴더명을
`verbotics.abb-rapid-0.1.1.disabled`로 변경해 VSCode가 인식하지 못하게 함(비활성화).
완전 삭제는 아니므로, 문제가 생기면 폴더명에서 `.disabled`를 떼어내면 원상복구됨.
**이건 이 컴퓨터(로컬 VSCode 설치)에만 적용된 조치라 git으로 다른 컴퓨터에 전파되지 않는다.**
새 컴퓨터에서 세팅할 때는 아래 "새 컴퓨터 세팅 체크리스트" 참고.

**✅ 현재 사용 중**: `Maxzurek.abb-rapid-pack` 단독 사용. `RobotStudio/.vscode/extensions.json`,
`Study/.vscode/extensions.json`, `0723_AMR_Project/.vscode/extensions.json`에
`recommendations: ["Maxzurek.abb-rapid-pack"]` / `unwantedRecommendations: ["verbotics.abb-rapid"]`
로 명시해 둠 — 새 컴퓨터에서 폴더를 열면 VSCode가 알아서 올바른 확장만 추천함.

### 발견 3 — "END 치면 ENDMODULE 자동완성"의 실제 동작 방식

**🔎 미확인/추정 → 확인 완료로 격상**: `abb-rapid-pack`의 스니펫(`snippets/rapid.json`)을 직접
열어서 확인함. 동작 방식은 사용자가 기대한 것과 약간 다름:

- ❌ 아닌 것: `MODULE Foo` 입력 → 다음 줄에 `END`를 치면 `ENDMODULE`이 제안되는 방식이 **아님**.
- ✅ 실제 방식: `MODULE Foo` 줄을 입력하고 **다음 줄에서 `module`이라는 단어(스니펫 prefix)를
  치고 Tab**을 누르면, 아래 템플릿이 통째로 삽입됨:
  ```
  MODULE ${1:ModuleName}
      $0
  ENDMODULE
  ```
  즉 `ENDMODULE`은 스니펫이 펼쳐지는 순간 바로 따라 나오는 것이지, 나중에 `END`를 타이핑해서
  얻는 게 아님. `if`/`ifelse`/`for`/`while`/`proc`/`func`/`trap`/`test`/`errorhandler` 등도
  전부 같은 방식(prefix + Tab → 블록 전체 + 닫는 키워드 자동 삽입).
- 사용자에게 이 워크스페이스 안내 시, "END를 치면 뜬다"가 아니라 **"블록 시작 키워드를 소문자
  prefix로 치고 Tab을 누르면 END 키워드까지 한 번에 삽입된다"**로 안내할 것.

### 발견 4 — 포맷터(`enableRapidFormatter`)가 꺼져 있는 이유

**🔎 미확인/추정 (그대로 유지)**: `RobotStudio/.vscode/settings.json`에는 원래부터
`"abb-rapid-pack.enableRapidFormatter": false`와 `"editor.formatOnSave": false`가 설정돼 있었음
(이 값을 언제, 왜 껐는지에 대한 기록은 이 저장소 히스토리에 없음 — 해당 파일은
커밋 `2f1b958`에서 이미 이 값으로 처음 추가됨).
확장 자체의 기본값(`configurationDefaults`)은 `editor.formatOnSave: true` +
`editor.defaultFormatter: Maxzurek.abb-rapid-pack`이라, **누군가 의도적으로 기본값을 뒤집어서
꺼둔 것**은 확실함. `RobotStudio/CLAUDE.md`에 있는 "RobotStudio가 저장할 때 한글 주석을
깨뜨리거나 지워버리는 문제"와 연관 있을 가능성이 있다고 추정되나 확인된 사실은 아님.
**이 값은 바꾸지 않았음.** 포맷터를 켜고 싶다면 먼저 이 로그에 "왜 켜는지, 테스트 결과가
어땠는지"를 새 항목으로 남긴 뒤 바꿀 것 — 아무 설명 없이 `true`로 바꾸지 말 것.

---

## 새 컴퓨터 세팅 체크리스트 (이 로그의 `✅` 항목 요약)

1. VSCode 확장 `Maxzurek.abb-rapid-pack` 설치. `verbotics.abb-rapid`가 같이 설치돼 있다면
   비활성화(Extensions 패널에서 우클릭 → Disable, 또는 확장 폴더명 뒤에 `.disabled` 붙이기).
2. `Study` 저장소를 열 때 사용하는 폴더(루트든 하위 프로젝트 폴더든)의 `.vscode/settings.json`에
   `abb-rapid-pack.*` + `"[rapid]"` 블록이 있는지 확인 — 이미 `Study/`, `RobotStudio/`,
   `0723_AMR_Project/`에는 들어가 있음. 새 RAPID 프로젝트 폴더를 만들면 이 세 파일 중 하나를
   그대로 복사해 넣을 것.
3. `.mod` 파일을 열고 우측 하단 언어 모드가 "RAPID"인지 확인.
4. 스니펫은 `module`, `if`, `ifelse`, `for`, `while`, `proc`, `func`, `trap`, `test`,
   `errorhandler` 등 prefix + Tab으로 사용 (발견 3 참고).
