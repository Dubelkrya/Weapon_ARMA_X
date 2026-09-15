import os
import sys
import tempfile
import textwrap
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import scan_build_v2 as pipeline  # noqa: E402
from scan_build_v2_strict import build_store, install_strict_pipeline  # noqa: E402


def write(root, rel, content):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path) or root, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(textwrap.dedent(content).lstrip())
    return path


class ResolverV2StrictPipelineTests(unittest.TestCase):
    def test_weapon_ammo_pipeline_keeps_vanilla_origin_after_path_collision(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            mag = "Prefabs/Weapons/Magazines/Test/Mag.et"
            cfg = "Configs/Weapons/Ammo/Test/Ammo.conf"
            projectile = "Prefabs/Weapons/Ammo/Test/Ball.et"

            write(
                armst,
                "Prefabs/Weapons/Rifles/Test/Weapon.et",
                f'''\
                GenericEntity {{
                 components {{
                  WeaponComponent "{{1000}}" {{
                   components {{
                    MuzzleComponent "{{1001}}" {{
                     BulletInitSpeedCoef 0.5
                     MagazineTemplate "{{B222}}{mag}"
                    }}
                   }}
                  }}
                 }}
                }}
                ''',
            )
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
                vanilla,
                "Prefabs/Weapons/Magazines/Test/Anchor.et",
                f'''\
                GenericEntity : "{{B222}}{mag}" {{
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

            install_strict_pipeline()
            store = build_store(armst, [f"materialized_base={vanilla}"])
            docs = pipeline.build_documents(store)
            doc = docs["Prefabs/Weapons/Rifles/Test/Weapon.et"]

            ammo = doc["ammo_resolution"]
            self.assertEqual(ammo["status"], "resolved")
            self.assertEqual(ammo["magazine_target_origin"], "materialized_base")
            self.assertEqual(ammo["magazine"]["ammo_config"]["target_origin"], "materialized_base")
            self.assertEqual(
                ammo["magazine"]["counts"][0]["projectile_origin"],
                "materialized_base",
            )
            velocity = ammo["effective_muzzle_velocities"][0]
            self.assertEqual(velocity["origin"], "materialized_base")
            self.assertEqual(velocity["ammo_init_speed"], 700)
            self.assertEqual(velocity["effective_muzzle_velocity"], 350.0)


if __name__ == "__main__":
    unittest.main()
