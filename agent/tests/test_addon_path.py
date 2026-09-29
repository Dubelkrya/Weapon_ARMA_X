#!/usr/bin/env python3
"""Regression tests for addon_path resolution policy.

The resolver decides which addon every scanner in this repository reads. The
failure that matters is silent: resolving a *different* addon than the one the
operator asked for and writing the result into catalog/ and reports/. These
tests pin the policy.

    python agent/tests/test_addon_path.py
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import addon_path  # noqa: E402


def make_addon(root: Path, gproj_id: str = "ARMSTPLATFORMWeapons") -> Path:
    """Create a minimal directory that satisfies the structural checks."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "addon.gproj").write_text(
        f'GameProject {{\n ID "{gproj_id}"\n GUID "0000000000000000"\n}}\n',
        encoding="utf-8",
    )
    (root / "Prefabs").mkdir(exist_ok=True)
    return root


class ValidateAddonRootTests(unittest.TestCase):
    def setUp(self):
        self._saved = {k: os.environ.get(k) for k in
                       (addon_path.ENV_PRIMARY, addon_path.ENV_LEGACY,
                        addon_path.ENV_ALLOW_ANY)}
        for k in self._saved:
            os.environ.pop(k, None)
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)

    def tearDown(self):
        for k, v in self._saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()

    # --- accepted ---

    def test_accepts_well_formed_weapons_addon(self):
        root = make_addon(self.base / "ARMST-PLATFORM---Weapons")
        self.assertEqual(addon_path.validate_addon_root(root), [])

    def test_missing_directory_is_rejected(self):
        self.assertTrue(addon_path.validate_addon_root(self.base / "nope"))

    def test_directory_without_gproj_is_rejected(self):
        root = self.base / "bare"
        root.mkdir()
        problems = addon_path.validate_addon_root(root)
        self.assertTrue(any("addon.gproj" in p for p in problems))

    def test_directory_without_prefabs_is_rejected(self):
        root = self.base / "no_prefabs"
        root.mkdir()
        (root / "addon.gproj").write_text(
            'GameProject {\n ID "ARMSTPLATFORMWeapons"\n}\n', encoding="utf-8")
        problems = addon_path.validate_addon_root(root)
        self.assertTrue(any("Prefabs" in p for p in problems))

    def test_file_instead_of_directory_is_rejected(self):
        f = self.base / "afile.txt"
        f.write_text("x", encoding="utf-8")
        problems = addon_path.validate_addon_root(f)
        self.assertTrue(any("not a directory" in p for p in problems))

    def test_empty_string_is_rejected(self):
        self.assertTrue(addon_path.validate_addon_root(""))

    # --- identity, not just structure ---

    def test_sibling_addon_with_same_structure_is_rejected(self):
        """Structure alone does not identify the addon; several siblings pass it."""
        root = make_addon(self.base / "Arm_Structura",
                          gproj_id="ARMSTPLATFORMStructura")
        problems = addon_path.validate_addon_root(root)
        self.assertTrue(any("is not the ARMST weapons addon" in p
                            for p in problems), problems)

    def test_allow_any_addon_overrides_identity_gate(self):
        root = make_addon(self.base / "Arm_Structura",
                          gproj_id="ARMSTPLATFORMStructura")
        os.environ[addon_path.ENV_ALLOW_ANY] = "1"
        self.assertEqual(addon_path.validate_addon_root(root), [])

    def test_allow_any_addon_does_not_override_structure(self):
        root = self.base / "Arm_Structura"
        root.mkdir()
        os.environ[addon_path.ENV_ALLOW_ANY] = "1"
        self.assertTrue(addon_path.validate_addon_root(root))

    def test_forbidden_tools_path_is_rejected_even_if_it_looked_like_an_addon(self):
        name = "Weapon_ARMA_X"
        root = make_addon(self.base / name, gproj_id="ARMSTPLATFORMWeapons")
        problems = addon_path.validate_addon_root(root)
        self.assertTrue(any("tools/sandbox" in p for p in problems), problems)

    # --- resolution policy ---

    def test_valid_explicit_env_wins_over_default(self):
        root = make_addon(self.base / "ARMST-PLATFORM---Weapons")
        os.environ[addon_path.ENV_PRIMARY] = str(root)
        self.assertEqual(addon_path.resolve_addon_root(), root.resolve())

    def test_invalid_explicit_env_is_fatal_and_does_not_fall_back(self):
        """The core policy: never silently scan a different addon."""
        os.environ[addon_path.ENV_PRIMARY] = str(self.base / "does_not_exist")
        with self.assertRaises(addon_path.AddonPathError) as ctx:
            addon_path.resolve_addon_root()
        self.assertIn("refusing to fall back", str(ctx.exception))

    def test_invalid_legacy_env_is_also_fatal(self):
        os.environ[addon_path.ENV_LEGACY] = str(self.base / "does_not_exist")
        with self.assertRaises(addon_path.AddonPathError):
            addon_path.resolve_addon_root()

    def test_primary_takes_precedence_over_legacy(self):
        good = make_addon(self.base / "ARMST-PLATFORM---Weapons")
        bad = self.base / "other"
        bad.mkdir()
        os.environ[addon_path.ENV_PRIMARY] = str(good)
        os.environ[addon_path.ENV_LEGACY] = str(bad)
        self.assertEqual(addon_path.resolve_addon_root(), good.resolve())

    def test_non_strict_returns_none_instead_of_raising(self):
        os.environ[addon_path.ENV_PRIMARY] = str(self.base / "does_not_exist")
        self.assertIsNone(addon_path.resolve_addon_root(strict=False))

    def test_error_message_names_the_env_var(self):
        os.environ[addon_path.ENV_PRIMARY] = str(self.base / "does_not_exist")
        with self.assertRaises(addon_path.AddonPathError) as ctx:
            addon_path.resolve_addon_root()
        self.assertIn(addon_path.ENV_PRIMARY, str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
