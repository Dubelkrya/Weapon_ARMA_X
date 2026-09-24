import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "agent" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from et_parser import parse_file, parse_text  # noqa: E402
from scan_build import array_values  # noqa: E402
from check_data_quality import (  # noqa: E402
    weapon_magazine_is_cataloged,
    weapon_magazine_is_external,
)


class ParserRegressionTests(unittest.TestCase):
    def test_inherited_block_keeps_instance_id_and_resource_ref(self):
        _, root = parse_text(
            '''BaseFireMode "{C0DE}" : "{F001}FireMode_Auto.conf" {
 RoundsPerMinute 650
}
''',
            source_name="test.conf",
            is_et=False,
        )
        node = root.children[0]
        self.assertEqual(node.name, "BaseFireMode")
        self.assertEqual(node.id, "{C0DE}")
        self.assertIsNone(node.type)
        self.assertEqual(node.ref["guid"], "F001")
        self.assertEqual(node.ref["path"], "FireMode_Auto.conf")

    def test_config_owner_resource_name_is_not_instance_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "Configs" / "Weapons" / "Ammo" / "Test.conf"
            path.parent.mkdir(parents=True)
            path.write_text(
                '''MagazineConfig "{ABCD}Configs/Weapons/Ammo/Test.conf" {
 AmmoResourceArray {
  "{1111}Prefabs/Weapons/Ammo/Test.et"
 }
}
''',
                encoding="utf-8",
            )
            resource = parse_file(path, root)
            self.assertEqual(resource.resource_ref["guid"], "ABCD")
            self.assertEqual(
                resource.resource_ref["path"],
                "Configs/Weapons/Ammo/Test.conf",
            )
            config_root = root_node = resource.root.children[0]
            self.assertIsNone(config_root.id)
            self.assertIsNone(config_root.ref)

    def test_array_values_reads_serialized_element_children(self):
        _, root = parse_text(
            '''AmmoMapping {
 0
 1
 0
 1
}
''',
            source_name="mapping.conf",
            is_et=False,
        )
        self.assertEqual(array_values(root.children[0]), [0, 1, 0, 1])


class DataQualityRegressionTests(unittest.TestCase):
    def test_relocated_magazine_guid_is_cataloged(self):
        doc = {
            "data": {
                "magazine": {
                    "magazine_template": {
                        "guid": "B7EC6D4222AE12BE",
                        "path": "Prefabs/Weapons/Magazines/9x39/old.et",
                    }
                }
            },
            "references": [
                {
                    "guid": "B7EC6D4222AE12BE",
                    "path": "Prefabs/Weapons/Magazines/9x39/old.et",
                    "resolved": "local",
                    "target": "Prefabs/Weapons/Magazines/Russian/9x39/new.et",
                }
            ],
        }
        resources = {
            "Prefabs/Weapons/Magazines/Russian/9x39/new.et": Path("new.json")
        }
        guids = {"B7EC6D4222AE12BE": Path("new.json")}
        self.assertTrue(weapon_magazine_is_cataloged(doc, resources, guids))


    def test_external_magazine_dependency_is_not_local_catalog_loss(self):
        doc = {
            "data": {
                "magazine": {
                    "magazine_template": {
                        "guid": "A827B610B7CD4158",
                        "path": "Prefabs/Weapons/Magazines/Vz58/Magazine.et",
                    }
                }
            },
            "references": [
                {
                    "guid": "A827B610B7CD4158",
                    "path": "Prefabs/Weapons/Magazines/Vz58/Magazine.et",
                    "resolved": "external",
                    "target": None,
                }
            ],
        }
        self.assertTrue(weapon_magazine_is_external(doc))


if __name__ == "__main__":
    unittest.main()
