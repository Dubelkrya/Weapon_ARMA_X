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

    def test_vanilla_reference_does_not_prove_guid_to_armst_only_candidate(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            target = "Prefabs/Weapons/Test/SharedTarget.et"
            source = "Prefabs/Weapons/Test/VanillaSource.et"
            write(armst, target, 'GenericEntity {\n ID "ARMST_COPY"\n}\n')
            write(
                vanilla,
                source,
                f'''\
                GenericEntity : "{{BEEF}}{target}" {{
                }}
                ''',
            )

            store = build_store(armst, [f"materialized_base={vanilla}"])

            # Incomplete materialization is not evidence that vanilla's BEEF
            # GUID belongs to the ARMST overlay copy.
            self.assertEqual(store._guid_records("BEEF"), [])
            ref = store.resolve_ref("BEEF", target, origin_hint="materialized_base")
            self.assertEqual(ref["status"], "external")
            self.assertEqual(ref["reason"], "upward_dependency_blocked")
            self.assertEqual(ref["candidates"][0]["origin"], "armst")

            entity = store.resolve_entity(source, "materialized_base")
            self.assertEqual(entity.status, "partial")
            self.assertEqual(entity.missing_parent["status"], "external_parent")
            self.assertEqual(entity.missing_parent["reason"], "upward_dependency_blocked")

    def test_armst_reference_can_resolve_downward_to_unique_vanilla_candidate(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            target = "Prefabs/Weapons/Test/VanillaBase.et"
            source = "Prefabs/Weapons/Test/ArmstChild.et"
            write(vanilla, target, 'GenericEntity {\n ID "VANILLA_BASE"\n}\n')
            write(
                armst,
                source,
                f'''\
                GenericEntity : "{{CAFE}}{target}" {{
                }}
                ''',
            )

            store = build_store(armst, [f"materialized_base={vanilla}"])
            ref = store.resolve_ref("CAFE", target, origin_hint="armst")
            self.assertEqual(ref["status"], "local")
            self.assertEqual(ref["origin"], "materialized_base")

            entity = store.resolve_entity(source, "armst")
            self.assertEqual(entity.status, "resolved")
            self.assertEqual(entity.chain[1]["origin"], "materialized_base")


if __name__ == "__main__":
    unittest.main()
