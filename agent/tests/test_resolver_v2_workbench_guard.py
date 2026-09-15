import os
import unittest


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MATERIALIZER = os.path.join(
    REPO_ROOT,
    "Scripts",
    "WorkbenchGame",
    "ResourceManager",
    "WAX_BaseGameSourceMaterializerPlugin.c",
)


class ResolverV2WorkbenchGuardTests(unittest.TestCase):
    def _source(self):
        with open(MATERIALIZER, "r", encoding="utf-8") as handle:
            return handle.read()

    def test_materializer_is_selection_only_not_a_broad_scanner(self):
        source = self._source()
        self.assertIn('name: "WAX: Materialize Selected Vanilla Sources"', source)
        self.assertNotIn("SearchWorkbenchResources", source)
        self.assertNotIn("SearchWorkbenchFiles", source)
        self.assertNotIn("Materialize Vanilla Weapon Dataset", source)
        self.assertNotIn("Export Vanilla Weapon Source Snapshot", source)

    def test_materializer_has_no_dialog_or_resource_registration_side_effects(self):
        source = self._source()
        self.assertNotIn("PrintFormatDialog", source)
        self.assertNotIn("ScriptDialog", source)
        self.assertNotIn("RegisterResourceFile", source)

    def test_materializer_preserves_manifest_history_for_exact_retries(self):
        source = self._source()
        self.assertIn("FileMode.APPEND", source)
        self.assertIn("_wax_materialization.tsv", source)
        self.assertIn("destination_relative", source)
        self.assertIn("status", source)


if __name__ == "__main__":
    unittest.main()
