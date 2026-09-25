import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "agent" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import scan_build  # noqa: E402
from base_game_snapshot import build_snapshot_index  # noqa: E402
from et_parser import find_child, parse_file  # noqa: E402


class BaseGameSnapshotResolverTests(unittest.TestCase):
    def test_external_parent_resolves_by_original_path_not_import_guid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot_root = root / "snapshot"
            mod_root = root / "mod"
            snapshot_mag = snapshot_root / "catalog" / "magazines"
            snapshot_mag.mkdir(parents=True)
            mod_root.mkdir()

            parent = snapshot_mag / "Magazine_545x39_RPK_45rnd_Base.et"
            parent.write_text(
                '''GenericEntity {
 components {
  MagazineComponent "{MAG}" {
   MagazineWell BaseMagazineWell MagazineWellAK545
   MaxAmmo 45
   AmmoMapping {
    0
    0
    0
   }
  }
 }
}
''',
                encoding="utf-8",
            )
            Path(str(parent) + ".meta").write_text(
                '''MetaFileClass {
 Name "{5208782369C978F0}Imported/VanillaSources/Prefabs/Weapons/Magazines/Magazine_545x39_RPK_45rnd_Base.et"
}
''',
                encoding="utf-8",
            )

            child = mod_root / "Child_RPK.et"
            child.write_text(
                '''GenericEntity : "{9569026177545A20}Prefabs/Weapons/Magazines/Magazine_545x39_RPK_45rnd_Base.et" {
 components {
  InventoryMagazineComponent "{INV}" {
  }
 }
}
''',
                encoding="utf-8",
            )

            snapshot = build_snapshot_index(str(snapshot_root))
            self.assertEqual(snapshot["resource_count"], 1)
            record = next(iter(snapshot["metadata"].values()))
            self.assertEqual(record["import_guid"], "5208782369C978F0")

            child_resource = parse_file(str(child), str(mod_root))
            resources = {"Child_RPK.et": child_resource}
            all_files = {"Child_RPK.et": str(child)}

            chain, external = scan_build.build_chain(
                child_resource,
                resources,
                all_files,
                {},
                snapshot,
            )
            self.assertEqual(external, [])
            self.assertEqual(
                [item["status"] for item in chain],
                ["local", "base_game_snapshot"],
            )
            self.assertEqual(
                chain[1]["resource"],
                "Prefabs/Weapons/Magazines/Magazine_545x39_RPK_45rnd_Base.et",
            )

            merge_resources = dict(resources)
            merge_resources.update(snapshot["resources"])
            resolved = scan_build.chain_merge(
                [item["rel"] for item in chain],
                merge_resources,
            )
            magazine = scan_build.functional_magazine_component(resolved)
            self.assertIsNotNone(magazine)
            max_ammo = find_child(magazine, "MaxAmmo")
            self.assertEqual(max_ammo.value[0], 45)
            self.assertTrue(max_ammo.src.startswith("base_game_snapshot:"))

    def test_generated_cleanup_preserves_reference_and_curated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old = (
                scan_build.CATALOG_DIR,
                scan_build.INDEX_DIR,
                scan_build.REPORT_DIR,
                scan_build.SCHEMA_DIR,
                scan_build.AGENT_DIR,
                scan_build.SCRIPT_DIR,
            )
            try:
                scan_build.CATALOG_DIR = str(root / "catalog")
                scan_build.INDEX_DIR = str(root / "indexes")
                scan_build.REPORT_DIR = str(root / "reports")
                scan_build.SCHEMA_DIR = str(root / "schema")
                scan_build.AGENT_DIR = str(root / "agent")
                scan_build.SCRIPT_DIR = str(root / "agent" / "scripts")

                mag_dir = root / "catalog" / "magazines"
                mag_dir.mkdir(parents=True)
                generated_catalog = mag_dir / "generated.json"
                generated_catalog.write_text("{}", encoding="utf-8")
                physical = mag_dir / "Magazine_Base.et"
                physical.write_text("GenericEntity {\n}\n", encoding="utf-8")
                physical_meta = Path(str(physical) + ".meta")
                physical_meta.write_text("MetaFileClass {\n}\n", encoding="utf-8")

                (root / "indexes").mkdir()
                generated_index = root / "indexes" / "references.json"
                generated_index.write_text("{}", encoding="utf-8")
                supplied = root / "indexes" / "magazine_reference"
                supplied.mkdir()
                supplied_file = supplied / "reference.json"
                supplied_file.write_text("{}", encoding="utf-8")

                (root / "reports" / "samples").mkdir(parents=True)
                generated_report = root / "reports" / "scan_summary.md"
                generated_report.write_text("generated", encoding="utf-8")
                curated = root / "reports" / "PREFAB_AUTHORING_GUIDE.md"
                curated.write_text("curated", encoding="utf-8")
                sample = root / "reports" / "samples" / "Sample.et"
                sample.write_text("GenericEntity {\n}\n", encoding="utf-8")

                (root / "schema").mkdir()
                generated_schema = root / "schema" / "entity.schema.json"
                generated_schema.write_text("{}", encoding="utf-8")
                extra_schema = root / "schema" / "compatibility.schema.json"
                extra_schema.write_text("{}", encoding="utf-8")

                (root / "agent" / "scripts" / "working_tables").mkdir(parents=True)
                scan_state = root / "agent" / "scan_state.json"
                scan_state.write_text("{}", encoding="utf-8")
                working = root / "agent" / "scripts" / "working_tables" / "entities.json"
                working.write_text("[]", encoding="utf-8")

                scan_build.clean_generated_outputs()

                for removed in (
                    generated_catalog,
                    generated_index,
                    generated_report,
                    generated_schema,
                    scan_state,
                    working,
                ):
                    self.assertFalse(removed.exists(), str(removed))

                for preserved in (
                    physical,
                    physical_meta,
                    supplied_file,
                    curated,
                    sample,
                    extra_schema,
                ):
                    self.assertTrue(preserved.exists(), str(preserved))
            finally:
                (
                    scan_build.CATALOG_DIR,
                    scan_build.INDEX_DIR,
                    scan_build.REPORT_DIR,
                    scan_build.SCHEMA_DIR,
                    scan_build.AGENT_DIR,
                    scan_build.SCRIPT_DIR,
                ) = old


if __name__ == "__main__":
    unittest.main()
