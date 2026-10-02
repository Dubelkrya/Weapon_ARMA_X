#!/usr/bin/env python3
"""Behavioral offline tests for the lab R entry-gate state model (issue #27).

These test the documented model in `mp133_lab_r_gate_model.py`; they are NOT
runtime validation of the EnforceScript (label: model-only).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from mp133_lab_r_gate_model import LabRGateModel  # noqa: E402

BASE = dict(lab=True, gate_enabled=True, request_active=True, pump=False,
            raised=True, tube=2, cap=3, reserve=30, insert_active=False)


def call(m, **kw):
    args = dict(BASE)
    args.update(kw)
    return m.on_handler_call(**args)


class EntryGateSequenceTests(unittest.TestCase):
    def test_press_begin_hold_abort_release_fresh_press(self):
        m = LabRGateModel()
        # press -> exactly one begin
        self.assertEqual(call(m), "begin")
        # held frames while active -> ignored
        self.assertEqual(call(m, insert_active=True), "ignore")
        self.assertEqual(call(m, insert_active=True), "ignore")
        # abort happened (insert no longer active) but the key is still held -> still latched
        self.assertEqual(call(m, insert_active=False), "ignore")
        # genuine release
        self.assertEqual(m.on_watch_tick(start=False, reload_type=0, is_reloading=False,
                                         pump=False, insert_active=False), "rearmed_release")
        # fresh press -> begin again
        self.assertEqual(call(m, insert_active=False), "begin")

    def test_no_repeated_begin_while_held(self):
        m = LabRGateModel()
        self.assertEqual(call(m), "begin")
        for _ in range(20):
            self.assertEqual(call(m, insert_active=False), "ignore")

    def test_ordinary_r_with_type1_is_not_blocked(self):
        # The prior log showed type 1 on the ordinary R path. Since pump is
        # identified by the Core action, a non-pump request must still begin.
        m = LabRGateModel()
        self.assertEqual(call(m, pump=False, request_active=True), "begin")

    def test_pump_is_not_an_insert(self):
        m = LabRGateModel()
        self.assertEqual(call(m, pump=True, request_active=True), "pump")
        # and it does not re-enter while held
        self.assertEqual(call(m, pump=True, request_active=True), "ignore")

    def test_lowered_weapon_blocks_then_latch_terminal(self):
        m = LabRGateModel()
        self.assertEqual(call(m, raised=False), "blocked")
        # still latched while held lowered -> no repeated attempts
        self.assertEqual(call(m, raised=False), "ignore")
        # release + new fresh press on a raised weapon -> begin
        m.on_watch_tick(start=False, reload_type=0, is_reloading=False, pump=False, insert_active=False)
        self.assertEqual(call(m, raised=True), "begin")

    def test_full_tube_blocks(self):
        m = LabRGateModel()
        self.assertEqual(call(m, tube=3, cap=3), "blocked")

    def test_no_reserve_blocks(self):
        m = LabRGateModel()
        self.assertEqual(call(m, reserve=0), "blocked")

    def test_foreign_weapon_passthrough(self):
        m = LabRGateModel()
        self.assertEqual(call(m, lab=False), "passthrough")

    def test_gate_disabled_passthrough(self):
        m = LabRGateModel()
        self.assertEqual(call(m, gate_enabled=False), "passthrough")

    def test_no_request_ignored(self):
        m = LabRGateModel()
        self.assertEqual(call(m, request_active=False), "ignore")


class ReleaseTests(unittest.TestCase):
    def test_not_released_while_reloading(self):
        m = LabRGateModel()
        call(m)
        self.assertEqual(m.on_watch_tick(start=False, reload_type=0, is_reloading=True,
                                         pump=False, insert_active=False), "none")
        self.assertTrue(m.latched)

    def test_not_released_while_pump(self):
        m = LabRGateModel()
        call(m, pump=True)
        self.assertEqual(m.on_watch_tick(start=False, reload_type=0, is_reloading=False,
                                         pump=True, insert_active=False), "none")

    def test_not_released_while_insert_active(self):
        m = LabRGateModel()
        call(m)
        self.assertEqual(m.on_watch_tick(start=True, reload_type=7, is_reloading=True,
                                         pump=False, insert_active=True), "none")

    def test_release_requires_zero_type_and_no_start(self):
        m = LabRGateModel()
        call(m)
        self.assertEqual(m.on_watch_tick(start=True, reload_type=7, is_reloading=False,
                                         pump=False, insert_active=False), "none")
        self.assertEqual(m.on_watch_tick(start=False, reload_type=5, is_reloading=False,
                                         pump=False, insert_active=False), "none")
        self.assertEqual(m.on_watch_tick(start=False, reload_type=0, is_reloading=False,
                                         pump=False, insert_active=False), "rearmed_release")

    def test_safety_timeout_recovers_from_stuck_latch(self):
        m = LabRGateModel()
        call(m)
        # Input never clears (start stays true) and nothing is active: after the
        # safety window the latch re-arms so the player is not permanently stuck.
        saw_timeout = False
        for _ in range(30):
            if m.on_watch_tick(start=True, reload_type=7, is_reloading=False,
                               pump=False, insert_active=False) == "rearmed_timeout":
                saw_timeout = True
        self.assertTrue(saw_timeout)
        self.assertFalse(m.latched)


if __name__ == "__main__":
    unittest.main(verbosity=2)