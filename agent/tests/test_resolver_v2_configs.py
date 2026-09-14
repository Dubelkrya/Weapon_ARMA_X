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


class ResolverV2ConfigTests(unittest.TestCase):
    def test_fire_mode_conf_merges_before_local_overrides(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "FireMode_Auto.conf", '''
                BaseFireMode {
                 MaxBurst -1
                 UIName "Auto"
                }
            ''')
            write(root, "weapon.et", '''
                GenericEntity {
                 components {
                  WeaponComponent "{AAAA}" {
                   components {
                    MuzzleComponent "{BBBB}" {
                     FireModes {
                      BaseFireMode "{CCCC}" : "{D0}FireMode_Auto.conf" {
                       RoundsPerMinute 650
                      }
                     }
                    }
                   }
                  }
                 }
                }
            ''')
            store = HydratedResourceStore([ResourceRoot("test", root, 10)])
            store.scan()
            result = store.resolve_entity("weapon.et")
            mode = find_recursive_r(result.resolved, "BaseFireMode")[0]
            max_burst = next(c for c in mode.children if c.name == "MaxBurst")
            rpm = next(c for c in mode.children if c.name == "RoundsPerMinute")
            ui_name = next(c for c in mode.children if c.name == "UIName")
            self.assertEqual(scalar_r(max_burst), -1)
            self.assertEqual(max_burst.defined_in, "FireMode_Auto.conf")
            self.assertEqual(scalar_r(rpm), 650)
            self.assertEqual(rpm.defined_in, "weapon.et")
            self.assertEqual(scalar_r(ui_name), "Auto")

    def test_materialized_config_self_reference_is_not_a_loop(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "FireMode_Auto.conf", '''
                BaseFireMode : "{D0}FireMode_Auto.conf" {
                 MaxBurst -1
                 UIName "Auto"
                }
            ''')
            write(root, "weapon.et", '''
                GenericEntity {
                 components {
                  MuzzleComponent "{BBBB}" {
                   FireModes {
                    BaseFireMode "{CCCC}" : "{D0}FireMode_Auto.conf" {
                     RoundsPerMinute 700
                    }
                   }
                  }
                 }
                }
            ''')
            store = HydratedResourceStore([ResourceRoot("test", root, 10)])
            store.scan()
            result = store.resolve_entity("weapon.et")
            mode = find_recursive_r(result.resolved, "BaseFireMode")[0]
            self.assertEqual(
                [w for w in store.warnings if w.get("category") == "CONFIG_REF_LOOP"], []
            )
            self.assertEqual(scalar_r(next(c for c in mode.children if c.name == "MaxBurst")), -1)
            self.assertEqual(
                scalar_r(next(c for c in mode.children if c.name == "RoundsPerMinute")), 700
            )

    def test_real_config_cycle_is_reported_once_across_reuse(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "A.conf", '''
                BaseFireMode : "{B0}B.conf" {
                 AValue 1
                }
            ''')
            write(root, "B.conf", '''
                BaseFireMode : "{A0}A.conf" {
                 BValue 2
                }
            ''')
            for name in ("weapon1.et", "weapon2.et"):
                write(root, name, '''
                    GenericEntity {
                     components {
                      MuzzleComponent "{BBBB}" {
                       FireModes {
                        BaseFireMode "{CCCC}" : "{A0}A.conf" {
                         RoundsPerMinute 600
                        }
                       }
                      }
                     }
                    }
                ''')
            store = HydratedResourceStore([ResourceRoot("test", root, 10)])
            store.scan()
            store.resolve_entity("weapon1.et")
            store.resolve_entity("weapon2.et")
            loops = [w for w in store.warnings if w.get("category") == "CONFIG_REF_LOOP"]
            self.assertEqual(len(loops), 1)
            self.assertEqual(loops[0]["stack"], ["A.conf", "B.conf", "A.conf"])

    def test_magazine_resolver_selects_component_with_functional_ammo_fields(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "Ammo.conf", '''
                MagazineConfig {
                 AmmoResourceArray {
                  "{A001}Ammo.et"
                 }
                }
            ''')
            write(root, "Ammo.et", '''
                Projectile {
                }
            ''')
            write(root, "Magazine.et", '''
                GenericEntity {
                 components {
                  MagazineComponent "{1111}" {
                   MaxAmmo 1
                  }
                  MagazineComponent "{2222}" {
                   MaxAmmo 2
                   AmmoConfig "{C001}Ammo.conf"
                   AmmoMapping {
                    0 0
                   }
                  }
                 }
                }
            ''')
            store = HydratedResourceStore([ResourceRoot("test", root, 10)])
            store.scan()
            result = store.resolve_magazine_ammo("Magazine.et")
            self.assertEqual(result["status"], "resolved")
            self.assertEqual(result["magazine_component"]["id"], "{2222}")
            self.assertEqual(result["magazine_component"]["candidate_count"], 2)
            self.assertEqual(result["max_ammo"]["value"], 2)
            self.assertEqual(result["mapping"], [0, 0])
            self.assertEqual(result["counts"][0]["count"], 2)

    def test_sparse_child_weapon_component_does_not_hide_inherited_muzzle(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "Base.et", '''
                GenericEntity {
                 components {
                  WeaponComponent "{1000}" {
                   components {
                    MuzzleComponent "{1001}" {
                     MagazineWell MagazineWellTest "{1002}" {
                     }
                     MagazineTemplate "{D001}Magazine.et"
                     FireModes {
                     }
                    }
                   }
                  }
                 }
                }
            ''')
            write(root, "Child.et", '''
                GenericEntity : "{B001}Base.et" {
                 components {
                  WeaponComponent "{9000}" {
                   UIInfo {
                    Name "Child UI only"
                   }
                  }
                 }
                }
            ''')
            store = HydratedResourceStore([ResourceRoot("test", root, 10)])
            store.scan()
            result = store.resolve_entity("Child.et")
            weapon = find_recursive_r(result.resolved, "WeaponComponent")[0]
            components = next(c for c in weapon.children if c.name == "components")
            muzzle = next(c for c in components.children if c.name == "MuzzleComponent")
            template = next(c for c in muzzle.children if c.name == "MagazineTemplate")
            self.assertEqual(weapon.id, "{1000}")
            self.assertEqual(template.ref["path"], "Magazine.et")
            self.assertEqual(template.defined_in, "Base.et")

    def test_inherited_ammo_config_array_is_hydrated(self):
        with tempfile.TemporaryDirectory() as root:
            write(root, "BaseAmmo.conf", '''
                MagazineConfig {
                 AmmoResourceArray {
                  "{A001}Ammo.et"
                 }
                }
            ''')
            write(root, "ChildAmmo.conf", '''
                MagazineConfig : "{B001}BaseAmmo.conf" {
                }
            ''')
            write(root, "Ammo.et", '''
                Projectile {
                }
            ''')
            write(root, "Magazine.et", '''
                GenericEntity {
                 components {
                  MagazineComponent "{2222}" {
                   MaxAmmo 1
                   AmmoConfig "{C001}ChildAmmo.conf"
                   AmmoMapping {
                    0
                   }
                  }
                 }
                }
            ''')
            store = HydratedResourceStore([ResourceRoot("test", root, 10)])
            store.scan()
            result = store.resolve_magazine_ammo("Magazine.et")
            self.assertEqual(result["status"], "resolved")
            self.assertEqual(result["counts"], [{"ammo_index": 0, "count": 1, "projectile": "Ammo.et"}])
            self.assertEqual(result["projectiles"][0]["target"], "Ammo.et")


if __name__ == "__main__":
    unittest.main()
