import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "agent" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from build_balance_pages import render_9x39  # noqa: E402


class BalanceReportRegressionTests(unittest.TestCase):
    def test_9x39_narrative_tracks_current_catalog(self):
        report = render_9x39()

        self.assertNotIn(
            "Current 9×39 magazine records have empty serialized `ammo_mapping` arrays",
            report,
        )
        self.assertNotIn(
            "Current 9×39 magazine records expose `#AR-AmmunitionID_545x39mm`",
            report,
        )
        self.assertNotIn(
            "Both current catalog projectiles resolve `PenetrationDepth = 3.7`",
            report,
        )
        # Current source truth for 9x39 SP6, tied to the specific ammo line so a
        # bare number elsewhere in the report cannot satisfy the assertion.
        self.assertRegex(
            report,
            r"`armst_Ammo_9x39_SP6_Ball\.et`: InitSpeed=290, Mass=0\.0156, "
            r"Damage=50, PenetrationDepth=6,",
        )
        self.assertIn(
            "RPM, velocity coefficient and dispersion remain per-entry evidence",
            report,
        )


if __name__ == "__main__":
    unittest.main()
