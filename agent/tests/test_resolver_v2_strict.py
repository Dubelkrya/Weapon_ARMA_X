import os
import sys
import tempfile
import textwrap
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from resolver_v2 import ResourceRoot  # noqa: E402
from resolver_v2_strict import StrictHydratedResourceStore  # noqa: E402


def write(root, rel, content):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path) or root, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(textwrap.dedent(content).lstrip())
    return path


class ResolverV2StrictIdentityTests(unittest.TestCase):
    def build_store(self, armst, vanilla):
        store = StrictHydratedResourceStore(
            [
                ResourceRoot("armst", armst, 100),
                ResourceRoot("materialized_base", vanilla, 50),
            ]
        )
        store.scan()
        return store

    def test_armst_collision_requires_guid_evidence_instead_of_same_origin_guess(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            same = "Prefabs/Weapons/Rifles/Test/Same.et"
            write(armst, same, "GenericEntity {\n Value 100\n}\n")
            write(vanilla, same, "GenericEntity {\n Value 50\n}\n")
            write(
                vanilla,
                "Prefabs/Weapons/Rifles/Test/VanillaChild.et",
                f'''\
                GenericEntity : "{{B222}}{same}" {{
                }}
                ''',
            )
            write(
                armst,
                "Prefabs/Weapons/Rifles/Test/ArmstUsesVanilla.et",
                f'''\
                GenericEntity : "{{B222}}{same}" {{
                 ChildValue 1
                }}
                ''',
            )

            store = self.build_store(armst, vanilla)

            proven = store.resolve_ref("B222", same, origin_hint="armst")
            self.assertEqual(proven["status"], "local")
            self.assertEqual(proven["origin"], "materialized_base")

            unknown = store.resolve_ref("A111", same, origin_hint="armst")
            self.assertEqual(unknown["status"], "ambiguous")
            self.assertEqual(
                unknown["reason"],
                "path_collision_without_proven_guid_owner",
            )

            entity = store.resolve_entity(
                "Prefabs/Weapons/Rifles/Test/ArmstUsesVanilla.et"
            )
            self.assertEqual(entity.status, "resolved")
            self.assertEqual(entity.chain[1]["origin"], "materialized_base")

    def test_config_loop_identity_distinguishes_armst_and_vanilla_same_path(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            conf = "Configs/Weapons/Test/Mode.conf"
            write(
                armst,
                conf,
                f'''\
                BaseFireMode : "{{A111}}{conf}" {{
                 UIName "ARMST"
                }}
                ''',
            )
            write(
                vanilla,
                conf,
                f'''\
                BaseFireMode : "{{B222}}{conf}" {{
                 UIName "Vanilla"
                }}
                ''',
            )
            # A lower-origin reference proves B222 belongs to the vanilla copy.
            write(
                vanilla,
                "Configs/Weapons/Test/Anchor.conf",
                f'''\
                AnchorConfig {{
                 Mode SomeMode "{{CAFE}}" : "{{B222}}{conf}" {{
                 }}
                }}
                ''',
            )
            write(
                armst,
                "Prefabs/Weapons/Rifles/Test/Weapon.et",
                f'''\
                GenericEntity {{
                 components {{
                  WeaponComponent "{{1000}}" {{
                   components {{
                    MuzzleComponent "{{1001}}" {{
                     FireModes {{
                      BaseFireMode "{{1002}}" : "{{B222}}{conf}" {{
                       RoundsPerMinute 600
                      }}
                     }}
                    }}
                   }}
                  }}
                 }}
                }}
                ''',
            )

            store = self.build_store(armst, vanilla)
            entity = store.resolve_entity("Prefabs/Weapons/Rifles/Test/Weapon.et")
            self.assertEqual(entity.status, "resolved")

            modes = [
                node
                for node in entity.resolved.children[0].children
                if False
            ]
            # Inspect recursively without relying on semantic ordering helpers.
            stack = [entity.resolved]
            mode = None
            while stack:
                node = stack.pop()
                if node.name == "BaseFireMode":
                    mode = node
                    break
                stack.extend(reversed(node.children))
            self.assertIsNotNone(mode)
            ui = next(child for child in mode.children if child.name == "UIName")
            self.assertEqual(ui.value[0], "Vanilla")
            self.assertEqual(ui.origin, "materialized_base")
            self.assertEqual(
                [w for w in store.warnings if w.get("category") == "CONFIG_REF_LOOP"],
                [],
            )

    def test_magazine_ammo_projectile_origin_is_preserved_across_collisions(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            mag = "Prefabs/Weapons/Magazines/Test/Mag.et"
            cfg = "Configs/Weapons/Ammo/Test/Ammo.conf"
            projectile = "Prefabs/Weapons/Ammo/Test/Ball.et"

            write(
                armst,
                mag,
                '''
                GenericEntity {
                 components {
                  MagazineComponent "{3000}" {
                   MaxAmmo 1
                  }
                 }
                }
                ''',
            )
            write(
                vanilla,
                mag,
                f'''\
                GenericEntity {{
                 components {{
                  MagazineComponent "{{3000}}" {{
                   MaxAmmo 2
                   AmmoConfig "{{C333}}{cfg}"
                   AmmoMapping {{
                    0 0
                   }}
                  }}
                 }}
                }}
                ''',
            )
            write(
                armst,
                cfg,
                f'''\
                MagazineConfig {{
                 AmmoResourceArray {{
                  "{{A999}}{projectile}"
                 }}
                }}
                ''',
            )
            write(
                vanilla,
                cfg,
                f'''\
                MagazineConfig {{
                 AmmoResourceArray {{
                  "{{D444}}{projectile}"
                 }}
                }}
                ''',
            )
            write(
                armst,
                projectile,
                '''
                Projectile {
                 components {
                  ShellMoveComponent "{4000}" {
                   InitSpeed 999
                  }
                 }
                }
                ''',
            )
            write(
                vanilla,
                projectile,
                '''
                Projectile {
                 components {
                  ShellMoveComponent "{4000}" {
                   InitSpeed 700
                  }
                 }
                }
                ''',
            )
            # Lower-origin parent reference proves the vanilla magazine GUID.
            write(
                vanilla,
                "Prefabs/Weapons/Magazines/Test/Anchor.et",
                f'''\
                GenericEntity : "{{B222}}{mag}" {{
                }}
                ''',
            )

            store = self.build_store(armst, vanilla)
            mag_ref = store.resolve_ref("B222", mag, origin_hint="armst")
            self.assertEqual(mag_ref["origin"], "materialized_base")

            result = store.resolve_magazine_ammo(
                mag_ref["resource"],
                mag_ref["origin"],
            )
            self.assertEqual(result["status"], "resolved")
            self.assertEqual(result["max_ammo"]["value"], 2)
            self.assertEqual(result["ammo_config"]["target_origin"], "materialized_base")
            self.assertEqual(result["counts"][0]["projectile_origin"], "materialized_base")

            physics = store.projectile_physics(
                result["counts"][0]["projectile"],
                result["counts"][0]["projectile_origin"],
            )
            self.assertEqual(physics["origin"], "materialized_base")
            self.assertEqual(physics["physics"]["InitSpeed"]["value"], 700)


if __name__ == "__main__":
    unittest.main()
