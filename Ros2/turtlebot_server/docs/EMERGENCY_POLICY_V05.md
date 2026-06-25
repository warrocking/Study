# Emergency Policy v0.5.1

긴급상황 원칙:

```text
emergency_stop은 최우선
all_stop은 robot_stop fan-out
clear_emergency와 reset_all_jobs는 별개
emergency 해제 후 기존 작업 자동 재시작 금지
```

정책 설정은 `program/json/emergency_info.json`에 둡니다.
