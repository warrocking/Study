# Log Format v0.5.1

최종 목표는 latest/events 분리입니다.

```text
data/log/*/latest   최신 상태 덮어쓰기
data/log/*/events   주요 이벤트 jsonl 누적
```

현재 v0.5.1 서버는 아래 로그를 우선 사용합니다.

```text
data/log/server/latest/operator_requests
data/log/server/latest/operator_responses
data/log/server/latest/client_health
data/log/server/latest/commands
data/log/server/latest/results
data/log/server/latest/file_transfers
data/log/server/latest/system
```

각 카테고리는 `latest_*.json`과 시간별 history JSON을 함께 남깁니다.
