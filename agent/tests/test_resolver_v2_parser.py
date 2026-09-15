import os
import sys
import tempfile
import textwrap
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from et_parser import find_child, parse_text  # noqa: E402
from resolver_v2 import ResourceRoot, find_recursive_r, scalar_r  # noqa: E402
from resolver_v2_configs import HydratedResourceStore  # noqa: E402


def write(root, rel, content):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path) or root, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(textwrap.dedent(content).lstrip())
    return path


class ResolverV2ParserTests(unittest.TestCase):
    def test_block_instance_id_survives_config_inheritance_syntax(self):
        _header, root = parse_text(
            '''
            BaseFireMode "{C0DE}" : "{F001}FireMode_Auto.conf" {
             RoundsPerMinute 650
            }
            '''
        )
        mode = root.children[0]

        self.assertEqual(mode.name, "BaseFireMode")
        self.assertIsNone(mode.type)
        self.assertEqual(mode.id, "{C0DE}")
        self.assertEqual(mode.ref["guid"], "F001")
        self.assertEqual(mode.ref["path"], "FireMode_Auto.conf")

    def test_typed_block_keeps_type_id_and_template_ref_separate(self):
        _header, root = parse_text(
            '''
            m_MagIndicator SomeIndicator "{CAFE}" : "{BEEF}Indicator.conf" {
             Value 1
            }
            '''
        )
        node = root.children[0]

        self.assertEqual(node.name, "m_MagIndicator")
        self.assertEqual(node.type, "SomeIndicator")
        self.assertEqual(node.id, "{CAFE}")
        self.assertEqual(node.ref["guid"], "BEEF")
        self.assertEqual(node.ref["path"], "Indicator.conf")

    def test_config_root_inheritance_does_not_create_fake_type_or_id(self):
        _header, root = parse_text(
            '''
            MagazineConfig:"{ABCD}BaseAmmo.conf" {
             MaxAmmo 30
            }
            '''
        )
        config = root.children[0]

        self.assertEqual(config.name, "MagazineConfig")
        self.assertIsNone(config.type)
        self.assertIsNone(config.id)
        self.assertEqual(config.ref["guid"], "ABCD")
        self.assertEqual(config.ref["path"], "BaseAmmo.conf")
        self.assertEqual(scalar_r(find_recursive_r(config, "MaxAmmo")[0]), 30)

    def test_hydrated_fire_mode_keeps_instance_id_and_local_override(self):
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
                      BaseFireMode "{C0DE}" : "{F001}FireMode_Auto.conf" {
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

            self.assertEqual(mode.id, "{C0DE}")
            self.assertEqual(mode.ref["path"], "FireMode_Auto.conf")
            self.assertEqual(
                scalar_r(find_child(mode, "RoundsPerMinute")),
                650,
            )
            ui_name = next(child for child in mode.children if child.name == "UIName")
            self.assertEqual(scalar_r(ui_name), "Auto")
            self.assertEqual(ui_name.defined_in, "FireMode_Auto.conf")


if __name__ == "__main__":
    unittest.main()
