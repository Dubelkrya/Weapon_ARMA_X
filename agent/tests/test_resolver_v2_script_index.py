import json
import os
import sys
import tempfile
import textwrap
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from script_class_index import build_script_index, parse_script_classes  # noqa: E402


class ResolverV2ScriptIndexTests(unittest.TestCase):
    def test_class_parser_keeps_base_fields_methods_and_modded_declarations(self):
        text = textwrap.dedent(
            '''
            [BaseContainerProps()]
            class MuzzleComponent : BaseComponent
            {
                [Attribute("1")]
                protected int m_iRounds = 1;

                void Fire(int count)
                {
                    if (count > 0)
                    {
                        count--;
                    }
                }
            }

            modded class MuzzleComponent
            {
                override void Fire(int count)
                {
                }
            }
            '''
        )
        rows = parse_script_classes(text, "scripts/Game/Weapons/MuzzleComponent.c")
        self.assertEqual(len(rows), 2)

        base = rows[0]
        self.assertEqual(base["name"], "MuzzleComponent")
        self.assertEqual(base["base"], "BaseComponent")
        self.assertFalse(base["modded"])
        self.assertEqual([field["name"] for field in base["fields"]], ["m_iRounds"])
        self.assertIn("Fire", [method["name"] for method in base["methods"]])

        modded = rows[1]
        self.assertTrue(modded["modded"])
        self.assertIsNone(modded["base"])
        self.assertIn("Fire", [method["name"] for method in modded["methods"]])

    def test_directory_index_preserves_official_source_marker(self):
        with tempfile.TemporaryDirectory() as root:
            scripts = os.path.join(root, "scripts", "Game", "Weapons")
            os.makedirs(scripts, exist_ok=True)
            with open(os.path.join(scripts, "Weapon.c"), "w", encoding="utf-8") as handle:
                handle.write(
                    "class WeaponComponent : BaseComponent\n"
                    "{\n"
                    "    protected float m_fValue;\n"
                    "    void Fire() { }\n"
                    "}\n"
                )
            marker = {
                "source": "official_bohemia_script_diff",
                "game_version": "1.8.0.13",
                "commit": "3d77cc212d5cda9922daf5f45635c7300d2d4cce",
            }
            with open(os.path.join(root, "_wax_source.json"), "w", encoding="utf-8") as handle:
                json.dump(marker, handle)

            payload = build_script_index(root)
            self.assertEqual(payload["summary"]["script_file_count"], 1)
            self.assertEqual(payload["summary"]["distinct_class_count"], 1)
            self.assertEqual(payload["summary"]["source"], marker)
            self.assertEqual(payload["inheritance"][0]["base"], "BaseComponent")


if __name__ == "__main__":
    unittest.main()
