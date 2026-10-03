#!/usr/bin/env python3
"""Offline regression tests for the CI dependency gate (issue #29).

These tests are repository-contained and do not need the live Weapons addon or
the frozen V2 lab:

  * implicit absence of the local addons must SKIP;
  * an **explicitly configured** but invalid path must FAIL (not skip);
  * valid local roots must RUN;
  * a direct scanner CLI invocation without a valid addon must exit non-zero and
    write no generated catalog.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "agent" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import validate_mp133_lab as v  # noqa: E402


def make_addon(base: Path, name: str) -> Path:
    root = base / name
    root.mkdir(parents=True)
    (root / "addon.gproj").write_text(
        'GameProject {\n\tID "ARMSTPLATFORMWeapons"\n}\n', encoding="utf-8")
    (root / "Prefabs").mkdir()
    return root


class DependencyDecisionTests(unittest.TestCase):
    def test_implicit_absence_skips(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "no-addons"
            lab = v.resolve_lab_root(strict=False, env="", default=missing)
            orig = v.resolve_original_root(strict=False, env="", default=missing)
            self.assertIsNone(lab)
            self.assertIsNone(orig)
            self.assertEqual(v.local_dependency_decision(lab, orig, "", ""), "skip")

    def test_explicit_invalid_lab_path_fails(self):
        self.assertEqual(
            v.local_dependency_decision(None, Path("orig"), "/bad/lab", None),
            "fail",
        )

    def test_explicit_invalid_original_path_fails(self):
        self.assertEqual(
            v.local_dependency_decision(Path("lab"), None, None, "/bad/orig"),
            "fail",
        )

    def test_partial_implicit_absence_skips_not_fails(self):
        self.assertEqual(
            v.local_dependency_decision(Path("lab"), None, None, None), "skip")

    def test_valid_local_roots_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            lab = make_addon(base, "lab")
            orig = make_addon(base, "orig")
            rl = v.resolve_lab_root(strict=False, env=str(lab))
            ro = v.resolve_original_root(strict=False, env=str(orig))
            self.assertEqual(rl, lab)
            self.assertEqual(ro, orig)
            self.assertEqual(
                v.local_dependency_decision(rl, ro, str(lab), str(orig)), "run")

    def test_strict_resolver_raises_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(v.LabValidationError):
                v.resolve_lab_root(strict=True, env="", default=Path(tmp) / "none")
            with self.assertRaises(v.LabValidationError):
                v.resolve_original_root(strict=True, env="", default=Path(tmp) / "none")


class ScannerCliTests(unittest.TestCase):
    def test_scanner_exits_nonzero_and_writes_no_catalog_without_addon(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            env = dict(os.environ)
            env["ARMST_WEAPONS_ADDON_PATH"] = str(repo / "nonexistent-addon")
            env.pop("MOD_ROOT", None)
            env["REPO_ROOT"] = str(repo)
            env["BASE_GAME_SNAPSHOT_ROOT"] = str(repo / "catalog")
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "scan_build.py")],
                env=env, capture_output=True, text=True, cwd=str(ROOT),
            )
            self.assertNotEqual(proc.returncode, 0, proc.stderr)
            for sub in ("catalog", "indexes", "reports", "schema"):
                p = repo / sub
                generated = list(p.rglob("*.json")) if p.exists() else []
                self.assertEqual(generated, [], f"wrote generated files under {sub}")
            self.assertFalse((repo / "agent" / "scan_state.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
