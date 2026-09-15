import os
import sys
import tempfile
import textwrap
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from scan_build_v2_strict import build_store  # noqa: E402


def write(root, rel, content):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path) or root, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(textwrap.dedent(content).lstrip())
    return path


class ResolverV2OriginPinningTests(unittest.TestCase):
    def test_explicit_missing_vanilla_origin_does_not_fallback_to_armst(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            rel = "Prefabs/Weapons/Test/OnlyArmst.et"
            write(
                armst,
                rel,
                '''
                GenericEntity {
                 ID "ARMST_ONLY"
                }
                ''',
            )

            store = build_store(armst, [f"materialized_base={vanilla}"])

            self.assertIsNotNone(store._record_for(rel))
            self.assertEqual(store._record_for(rel).origin, "armst")
            self.assertIsNone(store._record_for(rel, "materialized_base"))

            result = store.resolve_entity(rel, "materialized_base")
            self.assertEqual(result.status, "missing")

    def test_explicit_armst_origin_does_not_fallback_to_vanilla(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            rel = "Prefabs/Weapons/Test/OnlyVanilla.et"
            write(
                vanilla,
                rel,
                '''
                GenericEntity {
                 ID "VANILLA_ONLY"
                }
                ''',
            )

            store = build_store(armst, [f"materialized_base={vanilla}"])

            self.assertIsNotNone(store._record_for(rel))
            self.assertEqual(store._record_for(rel).origin, "materialized_base")
            self.assertIsNone(store._record_for(rel, "armst"))

            result = store.resolve_entity(rel, "armst")
            self.assertEqual(result.status, "missing")


if __name__ == "__main__":
    unittest.main()
