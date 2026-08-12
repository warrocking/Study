import importlib.util
import sys
import threading
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = ROOT / "Server" / "Server_admin_Web.py"


def load_server_module():
    spec = importlib.util.spec_from_file_location("final_ver06_server", SERVER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SignalInterlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_server_module()

    def setUp(self):
        self.server = self.module.AdminServer(self.module.Broadcaster())
        self.sent = []

        def fake_send(name, command):
            self.sent.append((name, command))
            return True, ""

        self.server.send = fake_send
        self.server.running.set()
        self.matchers = [
            threading.Thread(
                target=self.server._run_pickup_matcher, args=(station,), daemon=True
            )
            for station in ("3abb", "5abb")
        ]
        for matcher in self.matchers:
            matcher.start()
        self.server._handle_message(
            "amr",
            "EVENT START_ACCEPTED run=41 mode=AUTO_2_CYCLES cycles=2 steps=12",
        )

    def tearDown(self):
        self.server.running.clear()
        for matcher in self.matchers:
            matcher.join(timeout=2)

    def wait_until(self, predicate, timeout=2.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return True
            time.sleep(0.01)
        return False

    def test_return_arrival_never_releases_second_unit(self):
        # 사용자가 보고한 경합: 1번 플레이트 반납이 먼저 도착하고, 그 직후
        # 3ABB 두 번째 제품이 Ready가 되어도 출고 허가가 나가면 안 된다.
        self.server._handle_message(
            "amr",
            "EVENT RETURN_ARRIVED station=3abb unit=1 cycle=1 step=3 run=41 route=ROUTE_ST1",
        )
        self.server._handle_message("3abb", "ABB: ReadyForPickup unit=2")
        time.sleep(0.15)
        self.assertNotIn(("3abb", "AmrArrived unit=2"), self.sent)

        # 구버전의 FWD/REV STATUS도 Ver06에서는 허가 소스로 쓰지 않는다.
        self.server._handle_message(
            "amr",
            "STATUS CONVEYOR_START direction=REV mode=RETURN_UNLOAD_6S station=3abb cycle=1 step=3",
        )
        self.server._handle_message(
            "amr",
            "STATUS CONVEYOR_START direction=FWD mode=UNTIL_D2 station=3abb cycle=1 step=1",
        )
        time.sleep(0.15)
        self.assertNotIn(("3abb", "AmrArrived unit=2"), self.sent)

    def test_second_body_ready_while_amr_is_away_waits_for_second_pickup_visit(self):
        """Reproduce the real 3ABB timing that previously caused an early discharge.

        Unit 2 may be ready immediately after unit 1 leaves 3ABB.  Neither the
        4ABB transfer visit nor the empty-plate return visit to 3ABB is allowed
        to authorize unit 2.  Only cycle 2 / step 1 PICKUP_ARRIVED may do so.
        """
        self.server._handle_message("3abb", "ABB: ReadyForPickup unit=1")
        self.server._handle_message(
            "amr",
            "EVENT PICKUP_ARRIVED station=3abb unit=1 cycle=1 step=1 run=41 route=START",
        )
        self.assertTrue(
            self.wait_until(lambda: ("3abb", "AmrArrived unit=1") in self.sent),
            self.sent,
        )
        self.server._handle_message("3abb", "ABB: ConveyDone unit=1")

        # The second upper body finishes while the AMR is travelling to 4ABB.
        self.server._handle_message("3abb", "ABB: ReadyForPickup unit=2")
        self.server._handle_message(
            "amr",
            "EVENT TRANSFER_ARRIVED station=4abb unit=1 cycle=1 step=2 run=41 route=ROUTE_ST2 action=UNLOAD_THEN_RELOAD",
        )
        self.server._handle_message(
            "amr",
            "EVENT RETURN_ARRIVED station=3abb unit=1 cycle=1 step=3 run=41 route=ROUTE_ST1",
        )
        self.server._handle_message(
            "amr",
            "STATUS CONVEYOR_START direction=REV mode=RETURN_UNLOAD_6S station=3abb cycle=1 step=3",
        )
        time.sleep(0.15)
        self.assertNotIn(("3abb", "AmrArrived unit=2"), self.sent)

        # After the 5ABB leg, the AMR genuinely returns for upper body unit 2.
        self.server._handle_message(
            "amr",
            "EVENT PICKUP_ARRIVED station=3abb unit=2 cycle=2 step=1 run=41 route=ROUTE_ST1",
        )
        self.assertTrue(
            self.wait_until(lambda: ("3abb", "AmrArrived unit=2") in self.sent),
            self.sent,
        )
        self.server._handle_message("3abb", "ABB: ConveyDone unit=2")

    def test_wrong_unit_pickup_is_rejected_until_exact_unit_arrives(self):
        self.server._handle_message("3abb", "ABB: ReadyForPickup unit=2")
        self.server._handle_message(
            "amr",
            "EVENT PICKUP_ARRIVED station=3abb unit=1 cycle=1 step=1 run=41 route=START",
        )
        time.sleep(0.15)
        self.assertNotIn(("3abb", "AmrArrived unit=2"), self.sent)

        self.server._handle_message(
            "amr",
            "EVENT PICKUP_ARRIVED station=3abb unit=2 cycle=2 step=1 run=41 route=ROUTE_ST1",
        )
        self.assertTrue(
            self.wait_until(lambda: ("3abb", "AmrArrived unit=2") in self.sent),
            self.sent,
        )
        self.server._handle_message("3abb", "ABB: ConveyDone unit=2")

    def test_old_run_pickup_is_rejected(self):
        self.server._handle_message("3abb", "ABB: ReadyForPickup unit=1")
        self.server._handle_message(
            "amr",
            "EVENT PICKUP_ARRIVED station=3abb unit=1 cycle=1 step=1 run=40 route=START",
        )
        time.sleep(0.15)
        self.assertNotIn(("3abb", "AmrArrived unit=1"), self.sent)

    def test_route_failure_invalidates_pending_permission(self):
        self.server._handle_message("3abb", "ABB: ReadyForPickup unit=1")
        self.server._handle_message(
            "amr", "ERR ROUTE_FAILED route=START detail=Interrupted"
        )
        self.server._handle_message(
            "amr",
            "EVENT PICKUP_ARRIVED station=3abb unit=1 cycle=1 step=1 run=41 route=START",
        )
        time.sleep(0.15)
        self.assertNotIn(("3abb", "AmrArrived unit=1"), self.sent)

    def test_automatic_start_fails_closed_when_relays_are_missing(self):
        ok, error = self.server.start_production()
        self.assertFalse(ok)
        self.assertIn("필수 연결", error)

    def test_done_requires_both_valid_convey_units(self):
        self.server._handle_message("3abb", "ABB: Done")
        self.assertFalse(self.server.done_events["3abb"].is_set())
        with self.server.pickup_state_lock:
            self.server.completed_pickup_units["3abb"].update((1, 2))
        self.server._handle_message("3abb", "ABB: Done")
        self.assertTrue(self.server.done_events["3abb"].is_set())

    def test_done_coalesced_after_convey_done_is_not_lost(self):
        # 실제 커넥터에서는 ConveyDone과 Done이 한 recv에 연달아 들어올 수 있다.
        # 서버 수신 스레드가 Done을 먼저 처리 완료하고 matcher가 ConveyDone을
        # 나중에 검증하더라도 최종 Done 이벤트가 살아나야 한다.
        with self.server.pickup_state_lock:
            self.server.completed_pickup_units["3abb"].add(1)
        self.server._handle_message("3abb", "ABB: ReadyForPickup unit=2")
        self.server._handle_message(
            "amr",
            "EVENT PICKUP_ARRIVED station=3abb unit=2 cycle=2 step=1 run=41 route=ROUTE_ST1",
        )
        self.assertTrue(
            self.wait_until(lambda: ("3abb", "AmrArrived unit=2") in self.sent),
            self.sent,
        )
        self.server._handle_message("3abb", "ABB: ConveyDone unit=2")
        self.server._handle_message("3abb", "ABB: Done")
        self.assertTrue(
            self.wait_until(lambda: self.server.done_events["3abb"].is_set()),
            "Done was lost behind ConveyDone validation",
        )

    def test_duplicate_pickup_is_acked_but_authorized_once(self):
        event = (
            "EVENT PICKUP_ARRIVED station=3abb unit=1 cycle=1 "
            "step=1 run=41 route=START"
        )
        self.server._handle_message("3abb", "ABB: ReadyForPickup unit=1")
        self.server._handle_message("amr", event)
        self.server._handle_message("amr", event)
        self.assertTrue(
            self.wait_until(lambda: ("3abb", "AmrArrived unit=1") in self.sent),
            self.sent,
        )
        self.assertEqual(self.sent.count(("3abb", "AmrArrived unit=1")), 1)
        self.assertEqual(
            self.sent.count(("amr", "ARRIVAL_ACK station=3abb unit=1 run=41")), 2
        )
        self.server._handle_message("3abb", "ABB: ConveyDone unit=1")

    def test_full_two_unit_route_authorizes_only_four_pickups(self):
        def pickup(station, unit, step, route):
            self.server._handle_message(
                "amr",
                f"EVENT PICKUP_ARRIVED station={station} unit={unit} cycle={unit} "
                f"step={step} run=41 route={route}",
            )
            self.server._handle_message(station, f"ABB: ReadyForPickup unit={unit}")
            self.assertTrue(
                self.wait_until(lambda: (station, f"AmrArrived unit={unit}") in self.sent),
                self.sent,
            )
            self.server._handle_message(station, f"ABB: ConveyDone unit={unit}")

        pickup("3abb", 1, 1, "START")
        self.server._handle_message(
            "amr",
            "EVENT RETURN_ARRIVED station=3abb unit=1 cycle=1 step=3 run=41 route=ROUTE_ST1",
        )
        pickup("5abb", 1, 4, "ROUTE_ST3")
        self.server._handle_message(
            "amr",
            "EVENT RETURN_ARRIVED station=5abb unit=1 cycle=1 step=6 run=41 route=ROUTE_ST3",
        )
        pickup("3abb", 2, 1, "ROUTE_ST1")
        self.server._handle_message(
            "amr",
            "EVENT RETURN_ARRIVED station=3abb unit=2 cycle=2 step=3 run=41 route=ROUTE_ST1",
        )
        pickup("5abb", 2, 4, "ROUTE_ST3")
        self.server._handle_message(
            "amr",
            "EVENT RETURN_ARRIVED station=5abb unit=2 cycle=2 step=6 run=41 route=ROUTE_ST3",
        )

        permissions = [item for item in self.sent if item[0] in ("3abb", "5abb")]
        self.assertEqual(
            permissions,
            [
                ("3abb", "AmrArrived unit=1"),
                ("5abb", "AmrArrived unit=1"),
                ("3abb", "AmrArrived unit=2"),
                ("5abb", "AmrArrived unit=2"),
            ],
        )

    def test_static_3abb_do05_order_and_protocol(self):
        rapid = (ROOT / "Rapid" / "3abb.mod").read_text(encoding="utf-8")
        loop_start = rapid.index('SocketSend srv_client_socket \\Str:="ReadyForPickup unit="')
        wait_pos = rapid.index("WaitForAmrArrived n_upperBodyCount;", loop_start)
        pulse_pos = rapid.index("do05_Body_Docking_Done;", wait_pos)
        convey_pos = rapid.index('SocketSend srv_client_socket \\Str:="ConveyDone unit="', pulse_pos)
        self.assertLess(loop_start, wait_pos)
        self.assertLess(wait_pos, pulse_pos)
        self.assertLess(pulse_pos, convey_pos)

        car_delivery = rapid[rapid.index("PROC Car_Delivery()") : rapid.index("ENDPROC", rapid.index("PROC Car_Delivery()"))]
        self.assertNotIn("PulseDO", car_delivery)

        arduino = (ROOT / "Arduino" / "AMR" / "AMR.ino").read_text(encoding="utf-8")
        self.assertIn("EVENT PICKUP_ARRIVED", arduino)
        self.assertIn("EVENT RETURN_ARRIVED", arduino)
        self.assertNotIn('"EVENT DOCK_ARRIVED', arduino)


if __name__ == "__main__":
    unittest.main()
