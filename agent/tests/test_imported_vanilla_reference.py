import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "agent" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from imported_vanilla_reference import build_report  # noqa: E402


class ImportedVanillaReferenceTests(unittest.TestCase):
    def test_import_identity_uses_declared_original_path_not_live_guid(self):
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
 Name "{5208782369C978F0}Imported/VanillaSources/Prefabs/Weapons/Magazines/Magazine_545x39_RPK_45rnd_Base.et"
}
''',
                encoding="utf-8",
            )

            report = build_report(root)
            row = report["targets"][0]

            self.assertEqual(report["authority"], "STRUCTURED_REFERENCE_SOURCE")
            self.assertFalse(report["canonical_authority"])
            self.assertEqual(report["target_count"], 4)
            self.assertEqual(row["status"], "REFERENCE_RESOLVED")
            self.assertEqual(row["live_reference_guid"], "9569026177545A20")
            self.assertEqual(row["meta_import_guid"], "5208782369C978F0")
            self.assertNotEqual(row["live_reference_guid"], row["meta_import_guid"])
            self.assertEqual(
                row["meta_declared_original_resource"],
                "Prefabs/Weapons/Magazines/Magazine_545x39_RPK_45rnd_Base.et",
            )
            self.assertTrue(row["identity_match"])
            self.assertEqual(row["max_ammo"], 45)
            self.assertEqual(row["ammo_mapping_length"], 3)
            self.assertEqual(
                row["ammo_config"]["path"],
                "Configs/Weapons/Ammo/Ammo_545x39.conf",
            )

    def test_projectile_reference_extracts_explicit_damage_value(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ammo = root / "Ammo"
            ammo.mkdir()

            et = ammo / "Ammo_762x54r_Ball_57N323S.et"
            et.write_text(
                '''Projectile {
 components {
  ShellMoveComponent "{SHELL}" {
   ProjectileEffects {
    ProjectileDamage "{DAMAGE}" {
     DamageValue 130
    }
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
 Name "{CABAABDCADDAB3EE}Imported/VanillaSources/Prefabs/Weapons/Ammo/Ammo_762x54r_Ball_57N323S.et"
}
''',
                encoding="utf-8",
            )

            report = build_report(root)
            row = report["targets"][3]

            self.assertEqual(row["status"], "REFERENCE_RESOLVED")
            self.assertEqual(row["live_reference_guid"], "AC29AE3D5ECD6390")
            self.assertEqual(row["meta_import_guid"], "CABAABDCADDAB3EE")
            self.assertTrue(row["identity_match"])
            self.assertTrue(row["projectile_damage_found"])
            self.assertEqual(row["damage_value"], 130)


if __name__ == "__main__":
    unittest.main()
