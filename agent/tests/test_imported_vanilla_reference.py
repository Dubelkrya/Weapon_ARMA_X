import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "agent" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from imported_vanilla_reference import build_report  # noqa: E402


class ImportedVanillaReferenceTests(unittest.TestCase):
    def test_fixed_reference_target_is_extracted_without_filename_inference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mags = root / "Magazines"
            mags.mkdir()

            et = mags / "Magazine_545x39_RPK_45rnd_Base.et"
            et.write_text(
                '''GenericEntity {
 components {
  MagazineComponent "{AAAA}" {
   MagazineWell BaseMagazineWell MagazineWellAK545
   MaxAmmo 45
   AmmoConfig "{BBBB}Configs/Weapons/Ammo/Ammo_545x39.conf"
   AmmoMapping {
    0
    0
    1
   }
  }
 }
}
''',
                encoding="utf-8",
            )
            meta = Path(str(et) + ".meta")
            meta.write_text(
                '''MetaFileClass {
 Name "{9569026177545A20}Imported/VanillaSources/Prefabs/Weapons/Magazines/Magazine_545x39_RPK_45rnd_Base.et"
}
''',
                encoding="utf-8",
            )

            # Other fixed targets are intentionally absent in this focused test.
            report = build_report(root)
            row = report["targets"][0]

            self.assertEqual(report["authority"], "STRUCTURED_REFERENCE_SOURCE")
            self.assertFalse(report["canonical_authority"])
            self.assertEqual(row["status"], "REFERENCE_RESOLVED")
            self.assertEqual(row["meta_guid"], "9569026177545A20")
            self.assertTrue(row["meta_imported_vanilla"])
            self.assertEqual(row["max_ammo"], 45)
            self.assertEqual(row["ammo_mapping_length"], 3)
            self.assertEqual(
                row["ammo_config"]["path"],
                "Configs/Weapons/Ammo/Ammo_545x39.conf",
            )
            self.assertEqual(row["canonical_resource"],
                             "Prefabs/Weapons/Magazines/Magazine_545x39_RPK_45rnd_Base.et")


if __name__ == "__main__":
    unittest.main()
