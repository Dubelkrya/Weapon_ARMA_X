import os
import sys
import tempfile
import textwrap
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from scan_build_v2 import build_documents, build_store  # noqa: E402


def write(root, rel, content):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path) or root, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(textwrap.dedent(content).lstrip())
    return path


class ResolverV2PipelineTests(unittest.TestCase):
    def test_armst_to_vanilla_to_ammo_pipeline(self):
        with tempfile.TemporaryDirectory() as armst, tempfile.TemporaryDirectory() as vanilla:
            write(
                vanilla,
                "Prefabs/Weapons/Core/Configs/FireModes/FireMode_Auto.conf",
                '''
                BaseFireMode {
                 MaxBurst -1
                 UIName "Auto"
                }
                ''',
            )
            write(
                vanilla,
                "Prefabs/Weapons/Rifles/Test/Rifle_Base.et",
                '''
                GenericEntity {
                 components {
                  SCR_WeaponAttachmentsStorageComponent "{1000}" {
                   Attributes SCR_ItemAttributeCollection "{1001}" {
                    ItemPhysAttributes ItemPhysicalAttributes "{1002}" {
                     Weight 3
                     ItemVolume 1500
                    }
                   }
                  }
                  WeaponComponent "{2000}" {
                   components {
                    MuzzleComponent "{2001}" {
                     FireModes {
                      BaseFireMode "{AUTO}" : "{F001}Prefabs/Weapons/Core/Configs/FireModes/FireMode_Auto.conf" {
                       RoundsPerMinute 600
                      }
                     }
                     BulletInitSpeedCoef 0.9
                     DispersionDiameter 0.4
                     DispersionRange 200
                     MagazineWell MagazineWellTest "{2002}" {
                     }
                     MagazineTemplate "{M001}Prefabs/Weapons/Magazines/Mag_Test.et"
                    }
                   }
                  }
                 }
                }
                ''',
            )
            write(
                vanilla,
                "Prefabs/Weapons/Magazines/Mag_Test.et",
                '''
                GenericEntity {
                 components {
                  MagazineComponent "{3000}" {
                   MagazineWell MagazineWellTest "{3001}" {
                   }
                   MaxAmmo 3
                   AmmoConfig "{C001}Configs/Weapons/Ammo/Ammo_Test.conf"
                   AmmoMapping {
                    0 1 1
                   }
                  }
                 }
                }
                ''',
            )
            write(
                vanilla,
                "Configs/Weapons/Ammo/Ammo_Test.conf",
                '''
                MagazineConfig {
                 AmmoResourceArray {
                  "{A001}Prefabs/Weapons/Ammo/Ammo_Test_Ball.et"
                  "{A002}Prefabs/Weapons/Ammo/Ammo_Test_Tracer.et"
                 }
                }
                ''',
            )
            write(
                vanilla,
                "Prefabs/Weapons/Ammo/Ammo_Test_Ball.et",
                '''
                Projectile {
                 components {
                  ShellMoveComponent "{4000}" {
                   InitSpeed 800
                   Mass 0.01
                   AirDrag 0.00001
                  }
                 }
                }
                ''',
            )
            write(
                vanilla,
                "Prefabs/Weapons/Ammo/Ammo_Test_Tracer.et",
                '''
                Projectile {
                 components {
                  ShellMoveComponent "{4000}" {
                   InitSpeed 810
                   Mass 0.01
                   AirDrag 0.00001
                  }
                 }
                }
                ''',
            )
            write(
                armst,
                "Prefabs/Weapons/Rifles/Test/Armst_Test.et",
                '''
                GenericEntity : "{B001}Prefabs/Weapons/Rifles/Test/Rifle_Base.et" {
                 components {
                  WeaponComponent "{2000}" {
                   components {
                    MuzzleComponent "{2001}" {
                     DispersionRange 150
                    }
                   }
                  }
                 }
                }
                ''',
            )

            store = build_store(armst, [f"vanilla={vanilla}"])
            docs = build_documents(store)
            self.assertEqual(list(docs), ["Prefabs/Weapons/Rifles/Test/Armst_Test.et"])
            doc = docs["Prefabs/Weapons/Rifles/Test/Armst_Test.et"]

            self.assertEqual(doc["resolution"]["status"], "resolved")
            self.assertEqual(doc["classification"]["kind"], "weapon")

            weight = doc["resolved"]["physical"]["Weight"]
            self.assertEqual(weight["value"], 3)
            self.assertTrue(weight["inherited"])
            self.assertEqual(weight["defined_in"], "Prefabs/Weapons/Rifles/Test/Rifle_Base.et")

            dispersion = doc["resolved"]["ballistics"]["dispersion_range"]
            self.assertEqual(dispersion["value"], 150)
            self.assertFalse(dispersion["inherited"])

            mode = doc["resolved"]["fire_modes"][0]
            self.assertEqual(mode["ui_name"]["value"], "Auto")
            self.assertEqual(mode["max_burst"]["value"], -1)
            self.assertEqual(mode["rounds_per_minute"]["value"], 600)

            ammo = doc["ammo_resolution"]["magazine"]
            self.assertEqual(ammo["mapping"], [0, 1, 1])
            self.assertEqual(
                [(row["ammo_index"], row["count"]) for row in ammo["counts"]],
                [(0, 1), (1, 2)],
            )

            velocities = {
                row["projectile"]: row["effective_muzzle_velocity"]
                for row in doc["derived"]["effective_muzzle_velocities"]
            }
            self.assertEqual(velocities["Prefabs/Weapons/Ammo/Ammo_Test_Ball.et"], 720.0)
            self.assertEqual(velocities["Prefabs/Weapons/Ammo/Ammo_Test_Tracer.et"], 729.0)
            self.assertAlmostEqual(doc["derived"]["approx_moa"], 9.167, places=3)

            # Local child view must not pretend inherited physical fields were authored locally.
            self.assertNotIn("Weight", doc["local"].get("physical", {}))


if __name__ == "__main__":
    unittest.main()
