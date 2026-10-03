#!/usr/bin/env python3
"""Deterministic static validation for the ARMST_MP133_AnimationLab addon.

Pins the lab addon's structural invariants (file set, GUID resolution, prefab
wiring, insert-loop graph transition, .asi<->.ast row mapping). These are
repository-level static checks; they do NOT prove Workbench/runtime behavior.

    python agent/tests/test_mp133_lab_validation.py
"""

import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import validate_mp133_lab as v  # noqa: E402


class MP133LabValidationTests(unittest.TestCase):
    def setUp(self):
        lab = v.resolve_lab_root(strict=False)
        orig = v.resolve_original_root(strict=False)
        decision = v.local_dependency_decision(
            lab, orig, os.environ.get(v.ENV_LAB), os.environ.get(v.ENV_ORIG))
        if decision == "fail":
            self.fail(
                "explicitly configured local addon path is invalid; fix "
                f"${v.ENV_LAB} / ${v.ENV_ORIG} or unset it to skip"
            )
        if decision == "skip":
            self.skipTest(
                "LOCAL_ONLY: local Weapons addon / frozen lab not available and "
                "not explicitly configured; set MP133_LAB_ADDON_PATH and "
                "MP133_ORIGINAL_ADDON_PATH to run these integration tests"
            )
        self.lab = lab
        self.orig = orig

    def assert_clean(self, problems, ctx):
        self.assertEqual(problems, [], f"{ctx}: {problems}")

    def test_file_set(self):
        self.assert_clean(v.check_file_set(self.lab), "file set")

    def test_no_world_or_layer(self):
        self.assert_clean(v.check_no_world(self.lab), "no world/layer")

    def test_text_hygiene(self):
        self.assert_clean(v.check_text_hygiene(self.lab), "hygiene")

    def test_guid_references_resolve(self):
        union = v.original_guid_union(self.orig)
        self.assert_clean(v.check_guid_references(self.lab, union), "guid refs")

    def test_prefab_wiring(self):
        self.assert_clean(v.check_prefab_wiring(self.lab), "prefab wiring")

    def test_capacity_is_3(self):
        self.assert_clean(v.check_capacity3(self.lab), "capacity 3")

    def test_lab_magazine(self):
        self.assert_clean(v.check_lab_magazine(self.lab), "lab magazine")

    def test_v23_safety(self):
        self.assert_clean(v.check_v23_safety(self.lab), "v2.3 safety")

    def test_r_hook(self):
        self.assert_clean(v.check_r_hook(self.lab), "r hook")

    def test_v24_entry_gate(self):
        self.assert_clean(v.check_v24_entry_gate(self.lab), "v2.4 entry gate")

    def test_v27_trace(self):
        self.assert_clean(v.check_v27_trace(self.lab), "v2.7 C2 trace + gates off")

    def test_graph_insert_loop(self):
        self.assert_clean(v.check_graph_loop(self.lab), "graph loop")

    def test_asi_rows_match_ast(self):
        self.assert_clean(v.check_asi_rows(self.lab), "asi rows")

    def test_full_suite_clean(self):
        self.assert_clean(v.run_all(self.lab, self.orig), "full suite")


if __name__ == "__main__":
    unittest.main(verbosity=2)