import os
import sys
import tempfile
import textwrap
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from resolver_v2 import ResourceRoot, find_recursive_r, scalar_r  # noqa: E402
from resolver_v2_configs import HydratedResourceStore  # noqa: E402


def write(root, rel, content):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path) or root, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(textwrap.dedent(content).lstrip())
    return path


class ResolverV2IdentityTests(unittest.TestCase):
    def test_short_armst_parent_path_resolves_by_unique_suffix(self):
        with tempfile.TemporaryDirectory() as armst:
            write(
                armst,
                "Prefabs/Weapons/Rifles/AK74/base.et",
                '''
                GenericEntity {
                 Value 42
                }
                ''',
            )
            write(
                armst,
                "Prefabs/Weapons/Rifles/AK74/child.et",
                '''
                GenericEntity : "{AAAA}Rifles/AK74/base.et" {
                 ChildValue 7
                }
                ''',
            )

            store = HydratedResourceStore([ResourceRoot("armst", armst, 100)])
            store.scan()
            result = store.resolve_entity("Prefabs/Weapons/Rifles/AK74/child.et")

            self.assertEqual(result.status, "resolved")
            self.assertEqual(len(result.chain), 2)
            self.assertEqual(
                result.chain[1]["resource"],
                "Prefabs/Weapons/Rifles/AK74/base.et",
            )
            value = find_recursive_r(result.resolved, "Value")[0]
            self.assertEqual(scalar_r(value), 42)
            self.assertEqual(value.defined_in, "Prefabs/Weapons/Rifles/AK74/base.et")

    def test_vanilla_child_keeps_vanilla_parent_when_path_collides_with_armst(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            # ARMST shadows the same virtual path but intentionally lacks AmmoConfig.
            write(
                armst,
                "Prefabs/Weapons/Magazines/Ball.et",
                '''
                GenericEntity {
                 components {
                  MagazineComponent "{CA6}" {
                   MaxAmmo 2
                  }
                 }
                }
                ''',
            )
            write(
                vanilla,
                "Prefabs/Weapons/Magazines/Ball.et",
                '''
                GenericEntity {
                 components {
                  MagazineComponent "{CA6}" {
                   MaxAmmo 2
                   AmmoConfig "{C001}Configs/Weapons/Ammo/Ammo.conf"
                   AmmoMapping {
                    0 0
                   }
                  }
                 }
                }
                ''',
            )
            write(
                vanilla,
                "Prefabs/Weapons/Magazines/Last.et",
                '''
                GenericEntity : "{BEEF}Prefabs/Weapons/Magazines/Ball.et" {
                 components {
                  MagazineComponent "{CA6}" {
                   AmmoMapping {
                    0 0
                   }
                  }
                 }
                }
                ''',
            )
            write(
                vanilla,
                "Configs/Weapons/Ammo/Ammo.conf",
                '''
                MagazineConfig {
                 AmmoResourceArray {
                  "{A001}Prefabs/Weapons/Ammo/Ball.et"
                 }
                }
                ''',
            )
            write(
                vanilla,
                "Prefabs/Weapons/Ammo/Ball.et",
                '''
                Projectile {
                 components {
                  ShellMoveComponent "{S001}" {
                   InitSpeed 800
                  }
                 }
                }
                ''',
            )

            store = HydratedResourceStore(
                [
                    ResourceRoot("armst", armst, 100),
                    ResourceRoot("materialized_base", vanilla, 50),
                ]
            )
            store.scan()
            entity = store.resolve_entity("Prefabs/Weapons/Magazines/Last.et")
            self.assertEqual(entity.status, "resolved")
            self.assertEqual(entity.chain[1]["origin"], "materialized_base")

            result = store.resolve_magazine_ammo("Prefabs/Weapons/Magazines/Last.et")
            self.assertEqual(result["status"], "resolved")
            self.assertEqual(result["ammo_config"]["target_origin"], "materialized_base")
            self.assertEqual(result["counts"][0]["count"], 2)

    def test_same_origin_exact_collision_resolves_contextually(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            rel = "Prefabs/Weapons/Magazines/Same.et"
            write(armst, rel, "GenericEntity {\n}\n")
            write(vanilla, rel, "GenericEntity {\n}\n")

            store = HydratedResourceStore(
                [
                    ResourceRoot("armst", armst, 100),
                    ResourceRoot("materialized_base", vanilla, 50),
                ]
            )
            store.scan()

            armst_ref = store.resolve_ref("ABCD", rel, origin_hint="armst")
            vanilla_ref = store.resolve_ref("ABCD", rel, origin_hint="materialized_base")

            self.assertEqual(armst_ref["status"], "local")
            self.assertEqual(armst_ref["origin"], "armst")
            self.assertEqual(vanilla_ref["status"], "local")
            self.assertEqual(vanilla_ref["origin"], "materialized_base")

    def test_ambiguous_lookup_without_origin_is_not_silently_path_first(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            rel = "Prefabs/Weapons/Magazines/Same.et"
            write(armst, rel, "GenericEntity {\n}\n")
            write(vanilla, rel, "GenericEntity {\n}\n")

            store = HydratedResourceStore(
                [
                    ResourceRoot("armst", armst, 100),
                    ResourceRoot("materialized_base", vanilla, 50),
                ]
            )
            store.scan()
            resolved = store.resolve_ref("ABCD", rel)

            self.assertEqual(resolved["status"], "ambiguous")
            self.assertEqual(len(resolved["candidates"]), 2)


if __name__ == "__main__":
    unittest.main()
