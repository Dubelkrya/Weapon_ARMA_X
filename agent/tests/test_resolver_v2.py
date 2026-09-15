import os
import sys
import tempfile
import textwrap
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from resolver_v2 import (  # noqa: E402
    ResourceRoot,
    ResourceStore,
    find_recursive_r,
    scalar_r,
    validate_aibt,
)


def write(root, rel, content):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path) or root, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(textwrap.dedent(content).lstrip())
    return path


class ResolverV2Tests(unittest.TestCase):
    def test_inheritance_uses_name_occurrence_and_instance_id(self):
        with tempfile.TemporaryDirectory() as root:
            write(
                root,
                "base.et",
                '''
                GenericEntity {
                 components {
                  WeaponComponent "{AAAA}" {
                   components {
                    MuzzleComponent "{BBBB}" {
                     BulletInitSpeedCoef 1
                     DispersionRange 300
                    }
                   }
                  }
                 }
                }
                ''',
            )
            write(
                root,
                "child.et",
                '''
                GenericEntity : "{ABCD}base.et" {
                 ID "CHILD"
                 components {
                  WeaponComponent "{AAAA}" {
                   components {
                    MuzzleComponent "{BBBB}" {
                     NewUnrelatedField 99
                     DispersionRange 200
                    }
                   }
                  }
                 }
                }
                ''',
            )
            write(
                root,
                "base.et.meta",
                '''
                MetaFileClass {
                 Name "{DEAD}base.et"
                }
                ''',
            )

            store = ResourceStore([ResourceRoot("test", root, 10)])
            store.scan()
            result = store.resolve_entity("child.et")

            self.assertEqual(result.status, "resolved")
            coef = find_recursive_r(result.resolved, "BulletInitSpeedCoef")[0]
            dispersion = find_recursive_r(result.resolved, "DispersionRange")[0]
            self.assertEqual(scalar_r(coef), 1)
            self.assertEqual(coef.defined_in, "base.et")
            self.assertEqual(scalar_r(dispersion), 200)
            self.assertEqual(dispersion.defined_in, "child.et")

            # Live Resource GUID is learned from the child parent reference.
            # .meta Name stays metadata and must not replace it.
            self.assertEqual(result.chain[1]["live_guid"], "ABCD")
            self.assertEqual(result.chain[1]["meta_name_guid"], "DEAD")

    def test_ammo_mapping_resolves_exact_rounds(self):
        with tempfile.TemporaryDirectory() as root:
            write(
                root,
                "ammo0.et",
                '''
                Projectile {
                 components {
                  ShellMoveComponent "{1000}" {
                   InitSpeed 800
                  }
                 }
                }
                ''',
            )
            write(
                root,
                "ammo1.et",
                '''
                Projectile {
                 components {
                  ShellMoveComponent "{1000}" {
                   InitSpeed 810
                  }
                 }
                }
                ''',
            )
            write(
                root,
                "ammo.conf",
                '''
                MagazineConfig {
                 AmmoResourceArray {
                  "{A0}ammo0.et"
                  "{A1}ammo1.et"
                 }
                }
                ''',
            )
            write(
                root,
                "mag.et",
                '''
                GenericEntity {
                 components {
                  MagazineComponent "{2000}" {
                   MaxAmmo 3
                   AmmoConfig "{C0}ammo.conf"
                   AmmoMapping {
                    0 1 1
                   }
                  }
                 }
                }
                ''',
            )

            store = ResourceStore([ResourceRoot("test", root, 10)])
            store.scan()
            result = store.resolve_magazine_ammo("mag.et")

            self.assertEqual(result["status"], "resolved")
            self.assertEqual(result["mapping"], [0, 1, 1])
            self.assertEqual(
                [(row["ammo_index"], row["count"]) for row in result["counts"]],
                [(0, 1), (1, 2)],
            )
            self.assertEqual(result["rounds"][0]["projectile"], "ammo0.et")
            self.assertEqual(result["rounds"][2]["projectile"], "ammo1.et")

    def test_aibt_caliber_mismatch_is_ai_warning_not_physics_override(self):
        physics = {
            "InitSpeed": {"value": 290},
            "Mass": {"value": 0.01959},
            "AirDrag": {"value": 9.4e-6},
        }
        result = validate_aibt(
            "Prefabs/Weapons/Ammo/Ammo_9x39_SP5_Ball.et",
            {"path": "Configs/Weapons/Ammo/BallisticTables/AIBT_762x54r_Ball_7N1.conf"},
            physics,
        )
        self.assertEqual(result["status"], "suspicious_caliber_mismatch")
        self.assertEqual(result["projectile_caliber_token"], "9x39")
        self.assertEqual(result["table_caliber_token"], "762x54r")
        self.assertIn("AI-aiming", result["note"])


if __name__ == "__main__":
    unittest.main()
