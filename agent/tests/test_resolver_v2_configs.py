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
            write(
                root,
                "FireMode_Auto.conf",
                '''
                BaseFireMode {
                 MaxBurst -1
                 UIName "Auto"
                }
                ''',
            )
            write(
                root,
                "weapon.et",
                '''
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
                ''',
            )

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
            write(
                root,
                "FireMode_Auto.conf",
                '''
                BaseFireMode : "{D0}FireMode_Auto.conf" {
                 MaxBurst -1
                 UIName "Auto"
                }
                ''',
            )
            write(
                root,
                "weapon.et",
                '''
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
                ''',
            )

            store = HydratedResourceStore([ResourceRoot("test", root, 10)])
            store.scan()
            result = store.resolve_entity("weapon.et")
            mode = find_recursive_r(result.resolved, "BaseFireMode")[0]

            self.assertEqual(
                [w for w in store.warnings if w.get("category") == "CONFIG_REF_LOOP"],
                [],
            )
            self.assertEqual(
                scalar_r(next(c for c in mode.children if c.name == "MaxBurst")), -1
            )
            self.assertEqual(
                scalar_r(next(c for c in mode.children if c.name == "RoundsPerMinute")),
                700,
            )

    def test_real_config_cycle_is_reported_once_across_reuse(self):
        with tempfile.TemporaryDirectory() as root:
            write(
                root,
                "A.conf",
                '''
                BaseFireMode : "{B0}B.conf" {
                 AValue 1
                }
                ''',
            )
            write(
                root,
                "B.conf",
                '''
                BaseFireMode : "{A0}A.conf" {
                 BValue 2
                }
                ''',
            )
            for name in ("weapon1.et", "weapon2.et"):
                write(
                    root,
                    name,
                    '''
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
                    ''',
                )

            store = HydratedResourceStore([ResourceRoot("test", root, 10)])
            store.scan()
            store.resolve_entity("weapon1.et")
            store.resolve_entity("weapon2.et")

            loops = [w for w in store.warnings if w.get("category") == "CONFIG_REF_LOOP"]
            self.assertEqual(len(loops), 1)
            self.assertEqual(loops[0]["stack"], ["A.conf", "B.conf", "A.conf"])


if __name__ == "__main__":
    unittest.main()
