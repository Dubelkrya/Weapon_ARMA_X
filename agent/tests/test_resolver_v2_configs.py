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


if __name__ == "__main__":
    unittest.main()
