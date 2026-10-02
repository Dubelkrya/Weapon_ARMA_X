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
        self.lab = v.resolve_lab_root()
        self.orig = v.resolve_original_root()

    def assert_clean(self, problems, ctx):
        self.assertEqual(problems, [], f"{ctx}: {problems}")

    def test_file_set(self):
        self.assert_clean(v.check_file_set(self.lab), "file set")

    def test_text_hygiene(self):
        self.assert_clean(v.check_text_hygiene(self.lab), "hygiene")

    def test_guid_references_resolve(self):
        union = v.original_guid_union(self.orig)
        self.assert_clean(v.check_guid_references(self.lab, union), "guid refs")

    def test_prefab_wiring(self):
        self.assert_clean(v.check_prefab_wiring(self.lab), "prefab wiring")

    def test_graph_insert_loop(self):
        self.assert_clean(v.check_graph_loop(self.lab), "graph loop")

    def test_asi_rows_match_ast(self):
        self.assert_clean(v.check_asi_rows(self.lab), "asi rows")

    def test_full_suite_clean(self):
        self.assert_clean(v.run_all(self.lab, self.orig), "full suite")


if __name__ == "__main__":
    unittest.main(verbosity=2)