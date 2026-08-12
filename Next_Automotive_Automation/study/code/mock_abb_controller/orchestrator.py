# -*- coding: utf-8 -*-
"""
학습용 최소 오케스트레이터 — "출고 허가" 판단 로직만 떼어낸 교육용 구현.

이 파일 하나가 이번 프로젝트 전체에서 가장 중요한 교훈을 코드로 보여줍니다:

    1차 프로젝트에서 실제로 벌어졌던 사고 —
    "AMR이 빈 플레이트를 반납하러 온 것뿐인데, 마침 두 번째 제품도 준비돼 있어서
     그게 그대로 출고돼 버린 문제" (0723_AMR_Project/NEXT_PROJECT_KICKOFF_PROMPT.md 3.4절,
     Final_Ver06/README.md) — 를 재현/방지하는 로직.

ISA-88의 "Phase는 다음 순서를 스스로 정하지 않고, 레시피 실행 계층이 정한다"는
원칙(학습 자료 3부 3.2절)을 그대로 옮긴 것이 이 PickupMatcher 클래스입니다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReadyForPickup:
    station: str
    unit: int
    run_id: str


@dataclass
class ArrivalEvent:
    """AMR이 보내는 도착 이벤트. purpose가 'pickup'이 아니면 절대 허가에 안 씀."""

    station: str
    unit: int
    run_id: str
    purpose: str  # "pickup" | "return" | "transfer" — 반드시 목적을 구분해서 받는다


class PickupMatcher:
    """station별로 ReadyForPickup과 PICKUP_ARRIVED를 매칭해서 출고 허가를 낸다.

    설계 원칙 (모두 학습 자료 3부/4부와 대응):
      - purpose != "pickup" 인 도착은 절대 큐에 넣지 않는다 (RETURN_ARRIVED 오인 방지)
      - station과 unit이 정확히 같아야만 매칭한다 (잘못된 unit 거부)
      - run_id가 다르면 매칭하지 않는다 (이전 실행의 늦은 메시지 방지)
      - 같은 (station, unit, run_id) 조합에 대해 이미 허가를 냈으면 다시 내지 않는다
        (중복 이벤트가 출고를 두 번 일으키지 않게)
      - 정보가 하나라도 없거나 불일치하면 "허가하지 않는" 쪽으로 처리한다 (fail-closed)
    """

    def __init__(self):
        self._pending_ready: dict[tuple[str, str], ReadyForPickup] = {}
        self._granted: set[tuple[str, int, str]] = set()
        self._current_run_id: Optional[str] = None
        self.decision_log: list[str] = []

    def start_new_run(self, run_id: str) -> None:
        """새 Start 명령마다 호출. 이전 실행에서 남아있던 대기 상태를 전부 버린다."""
        self._current_run_id = run_id
        stale = list(self._pending_ready.keys())
        self._pending_ready.clear()
        if stale:
            self.decision_log.append(
                f"[세대교체] run_id={run_id} 시작 — 이전 대기 {len(stale)}건 폐기"
            )

    def on_ready_for_pickup(self, ev: ReadyForPickup) -> None:
        key = (ev.station, ev.run_id)
        self._pending_ready[key] = ev
        self.decision_log.append(
            f"[대기] {ev.station} unit={ev.unit} run={ev.run_id} 픽업 대기 등록"
        )

    def on_arrival(self, ev: ArrivalEvent) -> Optional[tuple[str, int]]:
        """도착 이벤트를 받아서, 허가가 나면 (station, unit)을 반환하고 아니면 None."""
        if ev.purpose != "pickup":
            # RETURN_ARRIVED, TRANSFER_ARRIVED는 여기서 끝 — 절대 허가로 이어지지 않는다.
            self.decision_log.append(
                f"[무시] {ev.station} unit={ev.unit} purpose={ev.purpose} — 출고 허가 대상 아님"
            )
            return None

        if ev.run_id != self._current_run_id:
            self.decision_log.append(
                f"[거부] {ev.station} unit={ev.unit} run={ev.run_id} — "
                f"현재 실행(run={self._current_run_id})과 다른 세대의 메시지"
            )
            return None

        key = (ev.station, ev.run_id)
        ready = self._pending_ready.get(key)
        if ready is None:
            self.decision_log.append(
                f"[거부] {ev.station} unit={ev.unit} — 매칭되는 ReadyForPickup이 없음"
            )
            return None

        if ready.unit != ev.unit:
            self.decision_log.append(
                f"[거부] {ev.station} — ReadyForPickup unit={ready.unit} vs "
                f"도착 unit={ev.unit} 불일치, 다른 차량이므로 허가 안 함"
            )
            return None

        grant_key = (ev.station, ev.unit, ev.run_id)
        if grant_key in self._granted:
            self.decision_log.append(
                f"[중복] {ev.station} unit={ev.unit} — 이미 허가한 이벤트, ACK만 재전송하고 재허가는 안 함"
            )
            return None

        self._granted.add(grant_key)
        del self._pending_ready[key]
        self.decision_log.append(
            f"[허가] {ev.station} unit={ev.unit} run={ev.run_id} — AmrArrived 전달 (근거: {ev})"
        )
        return (ev.station, ev.unit)
