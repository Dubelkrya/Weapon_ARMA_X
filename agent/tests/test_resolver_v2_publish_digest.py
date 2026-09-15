import json
import os
import sys
import tempfile
import unittest

SCRIPT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts"))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from publish_architecture_digest import publish  # noqa: E402


def dump(root, name, payload):
    path = os.path.join(root, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)
    return path


class ResolverV2PublishDigestTests(unittest.TestCase):
    def test_publish_shards_blueprints_and_keeps_only_derived_inputs(self):
        with tempfile.TemporaryDirectory() as input_root, tempfile.TemporaryDirectory() as parent:
            output_root = os.path.join(parent, "generated")
            dump(input_root, "package_manifest.json", {"schema_version": 1})
            dump(input_root, "architecture_summary.json", {"resource_count": 2})
            dump(input_root, "architecture_graph.json", {"resource_index": [], "reference_edges": [], "closure": {}})
            dump(
                input_root,
                "weapon_blueprints.json",
                [
                    {
                        "resource": "Prefabs/Weapons/Rifles/Test/Weapon.et",
                        "classification": {"kind": "weapon"},
                        "local_tree": {"name": "__root__"},
                    }
                ],
            )
            dump(input_root, "workbench_export_requests.json", [])
            dump(input_root, "resolver_warnings.json", [])
            dump(input_root, "script_class_links.json", {"declarations": []})

            publication = publish(input_root, output_root)

            self.assertEqual(publication["blueprint_count"], 1)
            self.assertEqual(publication["workbench_exact_request_count"], 0)
            self.assertTrue(os.path.isfile(os.path.join(output_root, "resource_graph.json")))
            self.assertTrue(os.path.isfile(os.path.join(output_root, "blueprint_index.json")))
            with open(os.path.join(output_root, "blueprint_index.json"), "r", encoding="utf-8") as handle:
                index = json.load(handle)
            self.assertEqual(index[0]["resource"], "Prefabs/Weapons/Rifles/Test/Weapon.et")
            self.assertTrue(os.path.isfile(os.path.join(output_root, index[0]["file"])))
            self.assertFalse(os.path.exists(os.path.join(output_root, "weapon_blueprints.json")))
            self.assertTrue(os.path.isfile(os.path.join(output_root, "publication_manifest.json")))

    def test_publish_refuses_to_replace_unmarked_directory(self):
        with tempfile.TemporaryDirectory() as input_root, tempfile.TemporaryDirectory() as output_root:
            dump(input_root, "package_manifest.json", {})
            dump(input_root, "architecture_summary.json", {})
            dump(input_root, "architecture_graph.json", {})
            dump(input_root, "weapon_blueprints.json", [])
            dump(input_root, "workbench_export_requests.json", [])
            dump(input_root, "resolver_warnings.json", [])
            with open(os.path.join(output_root, "manual.txt"), "w", encoding="utf-8") as handle:
                handle.write("keep")

            with self.assertRaisesRegex(RuntimeError, "unmarked architecture directory"):
                publish(input_root, output_root)


if __name__ == "__main__":
    unittest.main()
