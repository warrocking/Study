# Directory Structure v0.5.1

서버 루트는 `/home/admin_kyj/turtlebot_server`입니다.

```text
docs/             설명 문서
program/json/     서버가 읽는 설정 JSON
program/code/     서버 운영 코드
program/scripts/  실행/점검 스크립트
data/             실행 결과물
tests/            테스트용 mock
legacy_removed/   운영 코드에서 제외한 과거 파일
```

`program/code`에는 서버 코드만 둡니다. Control UI 구현 코드와 Robot Command Client 실제 구현 코드는 운영 코드에 넣지 않습니다.

`data`에는 로그, 이미지, 맵, 전송 결과처럼 실행 중 바뀌는 파일만 둡니다.

