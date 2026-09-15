import os
import sys
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from build_architecture_package import link_script_classes, serialized_class_names  # noqa: E402


class ResolverV2ArchitecturePackageTests(unittest.TestCase):
    def test_script_linker_follows_base_class_closure_and_reports_missing(self):
        blueprints = [
            {
                "local_tree": {
                    "name": "__root__",
                    "children": [
                        {
                            "name": "components",
                            "children": [
                                {
                                    "name": "WeaponComponent",
                                    "id": "{1000}",
                                    "children": [
                                        {
                                            "name": "ConfigField",
                                            "type": "KnownConfig",
                                            "id": "{1001}",
                                        },
                                        {
                                            "name": "UnknownComponent",
                                            "id": "{1002}",
                                        },
                                    ],
                                }
                            ],
                        }
                    ],
                },
                "effective_component_subtrees": [],
            }
        ]
        script_index = {
            "classes": [
                {"name": "WeaponComponent", "base": "BaseWeapon", "source_file": "w.c"},
                {"name": "BaseWeapon", "base": None, "source_file": "base.c"},
                {"name": "KnownConfig", "base": None, "source_file": "cfg.c"},
            ],
            "by_name": {
                "WeaponComponent": [0],
                "BaseWeapon": [1],
                "KnownConfig": [2],
            },
        }

        seeds = serialized_class_names(blueprints)
        self.assertIn("WeaponComponent", seeds)
        self.assertIn("KnownConfig", seeds)
        self.assertIn("UnknownComponent", seeds)

        linked = link_script_classes(blueprints, script_index)
        self.assertIn("BaseWeapon", linked["resolved_class_names"])
        self.assertIn("UnknownComponent", linked["missing_class_names"])
        self.assertEqual(
            {row["name"] for row in linked["declarations"]},
            {"WeaponComponent", "BaseWeapon", "KnownConfig"},
        )


if __name__ == "__main__":
    unittest.main()
