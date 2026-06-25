# Fleet JSON v0.4 Policy Review Notes

작성일: 2026-06-19

이 파일은 5단계 진행 전에 `action_policy.json`을 `JSON_CONTRACT_V4.md`의 정책 요약값에 맞춰 보정한 이유와, 7단계 완료 후 다시 확인할 항목을 남기기 위한 메모입니다.

## 수정 이유

`fleet_server_main.py`가 5단계에서 `action_policy.json`을 실제 서버 판단 기준으로 사용하게 됩니다. 따라서 서버 로직을 붙이기 전에 정책표가 계약 문서와 맞아야 합니다.

기존 정책표는 형식 검증은 통과했지만, `JSON_CONTRACT_V4.md`의 "8. action_policy_table"에 적힌 priority, blocking_type, interrupt_policy, target_scope 일부와 달랐습니다.

## 보정한 주요 항목

```text
pause_all / pause_robot:
  HARD -> SOFT

cancel_job:
  SOFT -> HARD
  target_scope_allowed: single,multi -> single,multi,all

clear_emergency:
  priority 9 -> 7

resume_all / resume_robot:
  priority 12/13 -> 20
  status_only -> replace_same_job

stop_mapping:
  priority 18 -> 40

nav_cancel:
  priority 18 -> 6

start_mapping:
  HARD -> SOFT

mapping_status:
  priority 10 -> 40

save_map:
  priority 35 -> 50
  HARD -> SINGLE
  queue_if_busy -> reject_if_busy

rsync_map:
  priority 36 -> 55
  HARD -> SINGLE

map_status:
  priority 10 -> 60

map_list:
  priority 10 -> 60
  target_scope_allowed: single,multi,all -> all

nav_goal:
  priority 40 -> 70
  HARD -> SOFT

nav_status:
  priority 10 -> 70
```

## 의도적으로 남긴 항목

`clear_error`는 action enum에는 있지만 `JSON_CONTRACT_V4.md`의 정책 요약표에는 별도 줄이 없습니다. 현재는 오류 상태 해제용 보조 명령으로 유지했습니다.

7단계 완료 후 아래 중 하나로 결정합니다.

```text
1. clear_error를 계속 유지한다.
2. clear_emergency로 통합한다.
3. 실제 UI/서버에서 쓰지 않으면 action enum과 정책표에서 제거한다.
```

## 7단계 완료 후 재검토할 질문

```text
1. 계약 문서 기준으로 보정한 priority가 실제 데모 흐름에 불편을 만들었는가?
2. pause/cancel/resume 계열의 SOFT/HARD/replace_same_job 정책이 서버 구현과 자연스럽게 맞는가?
3. save_map/rsync_map의 SINGLE 정책이 Mock Agent 및 실제 Agent 연결 시 과하게 막히지는 않는가?
4. map_list scope=all 제한이 UI 담당자의 사용 방식과 맞는가?
5. nav_goal priority=70이 수동 이동 priority=30보다 낮은 우선순위로 해석되는 문제가 없는가?
6. clear_error를 유지할지, clear_emergency로 합칠지 결정했는가?
```

## 현재 결론

5단계 전에는 계약 문서를 기준으로 정책표를 맞추는 것이 안전합니다. 다만 7단계 테스트가 끝나면 실제 사용성과 충돌이 없는지 다시 확인합니다.

## 7단계 완료 후 재검토 결과

작성일: 2026-06-19

7단계까지 완료한 뒤 다시 확인한 결과, 5단계 전에 정책표를 계약 문서 기준으로 보정한 것은 필요했습니다.

이유:

```text
1. fleet_server_main.py가 실제로 action_policy.json을 읽고 v4 요청 처리 판단에 사용합니다.
2. 서버가 UI priority를 신뢰하지 않고 서버 정책값으로 server_priority/blocking_type/interrupt_policy를 채웁니다.
3. all_stop, robot_stop, move_forward, status_request, heartbeat/state_report, Mock Agent 3대 fan-out 테스트에서 정책표 보정으로 인한 오류는 발견되지 않았습니다.
4. 정책표가 JSON_CONTRACT_V4.md와 맞아야 제어 담당자에게 공유한 통신 규격과 서버 동작이 어긋나지 않습니다.
```

검증된 항목:

```text
policy_valid = (True, R_ACCEPTED, OK)
move_forward: priority=30, SOFT, reject_if_busy, scope=single
robot_stop: priority=3, HARD, interrupt_current, scope=single,multi
all_stop: priority=2, HARD, interrupt_current, scope=all
status_request: priority=10, NONE, status_only, scope=single,multi,all
Mock Agent 3대 all_stop fan-out: R_STOPPED 3개, group_result SUCCESS
Mock Agent 3대 heartbeat/state_report: CONNECTED 3개
```

현재까지 발견된 부작용:

```text
없음
```

다만 아래 항목은 실제 map/nav 기능 구현 전에 한 번 더 결정해야 합니다.

```text
1. clear_error는 현재 유지합니다. 아직 UI/실제 서버 흐름에서 쓰이지 않았으므로 제거 또는 clear_emergency 통합 여부는 보류합니다.
2. save_map/rsync_map의 SINGLE 정책은 실제 파일 동기화 구현 전까지는 과한지 판단하지 않습니다.
3. map_list scope=all 제한은 UI 담당자가 개별 로봇 map list를 원하면 바꿀 수 있습니다.
4. nav_goal priority=70은 계약서 기준으로 유지합니다. 현재 서버는 숫자가 낮을수록 높은 우선순위처럼 해석하므로, 실제 우선순위 비교 로직을 구현할 때 이 의미를 다시 확인해야 합니다.
```

현재 결론:

```text
이번 정책표 보정은 유지합니다.
7단계 테스트 기준으로 문제는 없습니다.
map/nav/file sync 실제 구현 단계에서만 추가 재검토합니다.
```
