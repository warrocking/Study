# -*- coding: utf-8 -*-
"""
1차 프로젝트의 핵심 사고("AMR 없이 두 번째 제품이 출고된 문제")를 재현하고,
PickupMatcher가 이를 실제로 막는지 검증하는 회귀 테스트.

각 테스트는 학습 자료 3부 "필수 검증해야 할 회귀 테스트" 목록의 번호와 대응됩니다.
"""
from mock_abb_controller.orchestrator import PickupMatcher, ReadyForPickup, ArrivalEvent


def test_return_arrival_never_grants_pickup():
    """회귀 테스트 1~5번 핵심: 반납(RETURN) 도착이 다음 픽업으로 오인되면 안 된다.

    시나리오 재현:
      1. unit=1 픽업 허가 및 완료
      2. unit=2가 매우 빨리 준비되어 ReadyForPickup unit=2 등록
      3. AMR이 '빈 플레이트 반납'을 위해 3abb에 도착 (purpose="return")
      4. 이 시점에 절대로 unit=2가 출고되면 안 된다
      5. AMR이 실제로 unit=2를 픽업하러 다시 도착한 뒤에만 허가
    """
    m = PickupMatcher()
    m.start_new_run("RUN-1")

    # 1) unit=1 정상 픽업
    m.on_ready_for_pickup(ReadyForPickup("3abb", 1, "RUN-1"))
    granted = m.on_arrival(ArrivalEvent("3abb", 1, "RUN-1", purpose="pickup"))
    assert granted == ("3abb", 1)

    # 2) unit=2가 빨리 준비됨
    m.on_ready_for_pickup(ReadyForPickup("3abb", 2, "RUN-1"))

    # 3) AMR이 반납 목적으로 도착 (예전 버그의 원인이었던 상황)
    granted = m.on_arrival(ArrivalEvent("3abb", 2, "RUN-1", purpose="return"))
    assert granted is None, "RETURN_ARRIVED가 출고 허가를 내면 절대 안 된다"

    # 4) 실제 픽업 도착 이후에만 허가
    granted = m.on_arrival(ArrivalEvent("3abb", 2, "RUN-1", purpose="pickup"))
    assert granted == ("3abb", 2)


def test_wrong_unit_is_rejected():
    """회귀 테스트 7번: 잘못된 unit 번호 거부."""
    m = PickupMatcher()
    m.start_new_run("RUN-1")
    m.on_ready_for_pickup(ReadyForPickup("3abb", 1, "RUN-1"))

    granted = m.on_arrival(ArrivalEvent("3abb", 99, "RUN-1", purpose="pickup"))
    assert granted is None


def test_stale_run_id_is_rejected():
    """회귀 테스트 9번: 이전 run_id 메시지 거부 (경로 실패 후 늦게 도착한 신호 등)."""
    m = PickupMatcher()
    m.start_new_run("RUN-1")
    m.on_ready_for_pickup(ReadyForPickup("3abb", 1, "RUN-1"))

    # 서버가 재시작되거나 새 Start가 눌려 RUN-2로 세대교체됨
    m.start_new_run("RUN-2")

    # RUN-1 시절의 늦은 도착 메시지가 지금 들어옴
    granted = m.on_arrival(ArrivalEvent("3abb", 1, "RUN-1", purpose="pickup"))
    assert granted is None, "이전 세대(run_id)의 메시지로 출고를 허가하면 안 된다"


def test_duplicate_arrival_grants_only_once():
    """회귀 테스트 10번: 중복 도착 이벤트가 출고를 두 번 발생시키지 않아야 함
    (예: ACK 유실로 AMR이 같은 이벤트를 재전송한 경우)."""
    m = PickupMatcher()
    m.start_new_run("RUN-1")
    m.on_ready_for_pickup(ReadyForPickup("3abb", 1, "RUN-1"))

    first = m.on_arrival(ArrivalEvent("3abb", 1, "RUN-1", purpose="pickup"))
    second = m.on_arrival(ArrivalEvent("3abb", 1, "RUN-1", purpose="pickup"))  # 재전송

    assert first == ("3abb", 1)
    assert second is None, "이미 허가한 이벤트가 다시 허가를 내면 안 된다"


def test_two_full_cycles_grant_exactly_four_times():
    """회귀 테스트: 2회 전체 순서에서 3abb/5abb 픽업이 정확히 필요한 횟수만 허가되는지."""
    m = PickupMatcher()
    m.start_new_run("RUN-1")
    grants = []

    for station in ("3abb", "5abb"):
        for unit in (1, 2):
            m.on_ready_for_pickup(ReadyForPickup(station, unit, "RUN-1"))
            # 반납 이벤트가 중간에 끼어들어도 영향 없어야 함
            m.on_arrival(ArrivalEvent(station, unit, "RUN-1", purpose="return"))
            g = m.on_arrival(ArrivalEvent(station, unit, "RUN-1", purpose="pickup"))
            if g:
                grants.append(g)

    assert grants == [("3abb", 1), ("3abb", 2), ("5abb", 1), ("5abb", 2)]
