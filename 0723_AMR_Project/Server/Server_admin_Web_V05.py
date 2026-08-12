#!/usr/bin/env python3
"""Server_admin_Web V05.

기존 Server_admin_Web.py의 TCP 중계, Web HMI, 자동 생산 로직은 그대로
사용하면서 4abb의 역할만 중앙 서버 쪽에서 올바르게 반영한다.

4abb 동작 정책:
  - 4abb RAPID는 Start를 한 번 받으면 PLC 도착 센서를 계속 감시한다.
  - 따라서 자동 생산을 시작할 때 4abb에 Start를 한 번만 보낸다.
  - 4abb에서는 Done을 기다리지 않는다.
  - 같은 중앙 서버 실행 중에는 자동 생산을 다시 시작해도 Start를 중복해서
    보내지 않는다.
  - 작업자가 Web HMI에서 4abb Start 또는 all Start를 먼저 보낸 경우에도
    이미 활성화한 것으로 기록한다.

4abb RAPID 및 4abb Python 중계기 코드는 수정하지 않는다.
"""

from __future__ import annotations

import threading

import Server_admin_Web as base


VERSION = "V05"
FOUR_ABB_NAME = "4abb"
START_COMMAND = "Start"

# AMR_Server_Bridge_V2와 합의한 최신 명령 규격. 원본
# Server_admin_Web.py의 예전 Goto... 매핑은 건드리지 않고 V05에만 적용한다.
AMR_COMMANDS_V05 = {
    "goto_3_pickup": "RUN ROUTE_ST1 FWD",
    "goto_4_drop_upper": "RUN ROUTE_ST2 REV",
    "goto_3_return": "RUN ROUTE_ST1 REV",
    "goto_5_pickup": "RUN ROUTE_ST3 FWD",
    "goto_4_drop_lower": "RUN ROUTE_ST2 REV",
    "goto_5_return": "RUN ROUTE_ST3 REV",
}
base.AMR_COMMANDS.update(AMR_COMMANDS_V05)


class AdminServerV05(base.AdminServer):
    """기존 Web 서버에 4abb 수신 대기 활성화 상태만 추가한다."""

    def __init__(self, event_queue: "base.Broadcaster") -> None:
        super().__init__(event_queue)
        self._four_abb_state_lock = threading.Lock()
        self._four_abb_start_sent = False

    def _mark_4abb_started(self) -> None:
        with self._four_abb_state_lock:
            self._four_abb_start_sent = True

    def _is_4abb_started(self) -> bool:
        with self._four_abb_state_lock:
            return self._four_abb_start_sent

    def send(self, name: str, command: str) -> tuple[bool, str]:
        """기존 전송 동작을 유지하고 성공한 4abb Start만 기록한다."""
        command_text = command.strip()
        name_text = name.strip()

        with self.relays_lock:
            four_abb_before = self.relays.get(FOUR_ABB_NAME)
            command_targets_4abb = (
                name_text.lower() == base.BROADCAST_NAME
                or name_text == FOUR_ABB_NAME
            )

        ok, error = super().send(name, command)

        if command_text.lower() == START_COMMAND.lower() and command_targets_4abb:
            # super().send()는 전송에 실패한 중계기를 relays에서 제거한다.
            # 전송 전후에 동일한 4abb 객체가 남아 있으면 4abb 전송은 성공했다.
            with self.relays_lock:
                four_abb_after = self.relays.get(FOUR_ABB_NAME)
            if four_abb_before is not None and four_abb_after is four_abb_before:
                self._mark_4abb_started()
                self.set_relay_status(
                    FOUR_ABB_NAME,
                    f"{base.now()}  PLC 센서 감시·적재 대기 활성화",
                    "ok",
                )

        return ok, error

    def _ensure_4abb_receiving(self) -> tuple[bool, str]:
        """자동 생산 전에 4abb의 무한 수신·적재 루프를 한 번만 시작한다."""
        with self.relays_lock:
            connected = FOUR_ABB_NAME in self.relays

        if not connected:
            return False, "4abb가 연결되어 있지 않아 자동 생산을 시작할 수 없습니다."

        if self._is_4abb_started():
            self.log(
                "4abb는 이미 PLC 센서 감시·적재 대기 상태입니다. Start를 다시 보내지 않습니다.",
                "orch",
            )
            return True, ""

        self.log("4abb에 Start 전송 - PLC 센서 감시·적재 무한 대기 활성화", "orch")
        ok, error = self.send(FOUR_ABB_NAME, START_COMMAND)
        if not ok:
            return False, error or "4abb Start 전송에 실패했습니다."

        self.log(
            "4abb 수신·적재 대기 시작 요청 완료 (4abb Done 응답은 기다리지 않음)",
            "orch",
        )
        return True, ""

    def _run_production(self, car_count: int) -> None:
        # 4abb는 3abb/5abb처럼 차량마다 Start하는 장비가 아니다. 자동 생산의
        # 첫 공정 전에 한 번만 Start하여 PLC 센서를 계속 감시하게 한다.
        ok, error = self._ensure_4abb_receiving()
        if not ok:
            self.log(f"자동 생산 시작 취소: {error}", "err")
            self.orchestrator_thread = None
            self.stop_requested.clear()
            self.set_orchestrator_state(False)
            return

        # 새 생산 묶음은 AMR의 6단계 순서를 첫 단계부터 시작한다.
        reset_ok, reset_error = self.send("amr", "RESET_SEQUENCE")
        if not reset_ok:
            self.log(
                f"AMR 순서 초기화 전송 실패: {reset_error or '전송 오류'}",
                "err",
            )

        # 이후 3abb/5abb Start, Done 대기, AMR 이송 순서는 기존 코드 그대로다.
        super()._run_production(car_count)

    def snapshot(self) -> dict:
        state = super().snapshot()
        state["four_abb_receiving_started"] = self._is_4abb_started()
        state["server_version"] = VERSION
        return state


# Server_admin_Web.py의 Flask 라우트는 base.server 전역을 참조한다.
# 기존 서버 객체를 V05 객체로 바꾸면 HTML/API 코드를 복사하지 않고도 모든
# 기존 기능을 그대로 사용하면서 V05 오케스트레이션이 적용된다.
server = AdminServerV05(base.broadcaster)
base.server = server
app = base.app

# 브라우저 제목에서 실행 버전을 식별할 수 있게 표시한다.
base.INDEX_HTML = base.INDEX_HTML.replace(
    "AMR 통합 관리자 - 웹 HMI", "AMR 통합 관리자 V05 - 웹 HMI"
)


def main() -> None:
    print("Server_admin_Web_V05: 4abb Start-once orchestration enabled")
    base.main()


if __name__ == "__main__":
    main()
