#!/usr/bin/env python3
"""Tests for the reviewed one-command lab clip connector (issue #27)."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import mp133_lab_connect_anims as c  # noqa: E402

W_OLD, P_OLD = c.W_OLD_REL, c.P_OLD_REL
W_NEW, P_NEW = c.W_ANM_REL, c.P_ANM_REL
WG, PG = "AABBCCDDEEFF0011", "1122334455667788"

AGF_FIXTURE = """AnimSrcGraphFile {
 Sheets {
  AnimSrcGraphSheet Master {
   Nodes {
    AnimSrcNodeStateMachine WeaponReloadSTM {
     states {
      AnimSrcNodeState MagReload {
       Child "MagReloadSTM"
      }
      AnimSrcNodeState MagNoBulletReload {
       Child "MagReloadSTM"
      }
      AnimSrcNodeState RemoveMag {
       Child "RemoveMagAnim"
      }
      AnimSrcNodeState ReloadActionBolt {
       Child "RackBoltAnim"
      }
     }
     transitions {
      AnimSrcNodeTransition "{ABC0000000000001}" {
       FromState "MagNoBulletReload"
       ToState "ReloadActionBolt"
       Condition "RemainingTimeLess(0.1)"
      }
     }
    }
    AnimSrcNodeStateMachine MagReloadSTM {
     states {
      AnimSrcNodeState RemoveMag {
       Child "RemoveMagAnim"
      }
     }
    }
    AnimSrcNodeSource RemoveMagAnim {
     Source "Reload.Reload_RemoveMag"
    }
   }
  }
 }
}
"""


def asi_fixture(old_guid, old_rel):
    return (
        'AnimSetInstanceSource {\n'
        ' Template "{138604905EC95210}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.ast"\n'
        ' Lines {\n'
        '  AnimSetInstanceSource_Line "Reload.Erc.Reload_InsertMag" {\n'
        f'   Resource "{{{old_guid}}}{old_rel}"\n'
        '  }\n'
        '  AnimSetInstanceSource_Line "Reload.Pne.Reload_InsertMag" {\n'
        f'   Resource "{{{old_guid}}}{old_rel}"\n'
        '  }\n'
        ' }\n'
        '}\n')


def make_lab(base: Path) -> Path:
    lab = base / "ARMST_MP133_AnimationLab"
    ws = lab / "Assets/Weapons_RUS/Mp_133/Workspace"
    (ws / "LabClips").mkdir(parents=True, exist_ok=True)
    (lab / "addon.gproj").write_text('GameProject {\n ID "ARMSTMP133AnimationLab"\n}\n', encoding="utf-8")
    (ws / "MP133_Lab_weapon.asi").write_text(asi_fixture(c.W_OLD_GUID, W_OLD), encoding="utf-8")
    (ws / "MP133_Lab_player.asi").write_text(asi_fixture(c.P_OLD_GUID, P_OLD), encoding="utf-8")
    (ws / "MP133_Lab.agf").write_text(AGF_FIXTURE, encoding="utf-8")
    for guid, rel in ((WG, W_NEW), (PG, P_NEW)):
        anm = lab / rel
        anm.parent.mkdir(parents=True, exist_ok=True)
        anm.write_bytes(b"anm")
        (lab / (rel + ".meta")).write_text(
            'MetaFileClass {\n Name "{' + guid + '}' + rel + '"\n}\n', encoding="utf-8")
    return lab


class PreflightTests(unittest.TestCase):
    def test_verify_anm_ok(self):
        with tempfile.TemporaryDirectory() as d:
            lab = make_lab(Path(d))
            self.assertEqual(c.verify_anm(lab, W_NEW, WG), [])

    def test_verify_anm_missing(self):
        with tempfile.TemporaryDirectory() as d:
            lab = make_lab(Path(d))
            (lab / W_NEW).unlink()
            self.assertTrue(c.verify_anm(lab, W_NEW, WG))

    def test_verify_anm_wrong_guid(self):
        with tempfile.TemporaryDirectory() as d:
            lab = make_lab(Path(d))
            self.assertTrue(c.verify_anm(lab, W_NEW, "0000000000000000"))


class AsiPlanTests(unittest.TestCase):
    def test_repoints_both_rows(self):
        r = c.plan_asi(asi_fixture(c.W_OLD_GUID, W_OLD), WG, c.W_OLD_GUID, W_OLD, W_NEW)
        self.assertTrue(r["ok"], r["problems"])
        self.assertEqual(r["changed_rows"], list(c.EXPECTED_ROWS))
        self.assertIn("{" + WG + "}" + W_NEW, r["new_text"])
        self.assertNotIn(W_OLD, r["new_text"])

    def test_partial_rows_fail(self):
        text = asi_fixture(c.W_OLD_GUID, W_OLD).replace(
            'Reload.Pne.Reload_InsertMag', 'Reload.Pne.Reload_InsertMagX')
        r = c.plan_asi(text, WG, c.W_OLD_GUID, W_OLD, W_NEW)
        self.assertFalse(r["ok"])

    def test_wrong_resource_fails(self):
        text = asi_fixture(c.W_OLD_GUID, W_OLD).replace(W_OLD, "X.anm")
        r = c.plan_asi(text, WG, c.W_OLD_GUID, W_OLD, W_NEW)
        self.assertFalse(r["ok"])

    def test_idempotent(self):
        first = c.plan_asi(asi_fixture(c.W_OLD_GUID, W_OLD), WG, c.W_OLD_GUID, W_OLD, W_NEW)
        second = c.plan_asi(first["new_text"], WG, c.W_OLD_GUID, W_OLD, W_NEW)
        self.assertTrue(second["ok"])
        self.assertEqual(second["changed_rows"], [])


class GraphPlanTests(unittest.TestCase):
    def test_scoped_redirect(self):
        r = c.plan_graph_hardening(AGF_FIXTURE)
        self.assertTrue(r["ok"], r["problems"])
        self.assertEqual(sorted(r["states"]), ["MagNoBulletReload", "MagReload", "RemoveMag"])
        # nested MagReloadSTM internal RemoveMagAnim child must survive
        self.assertEqual(r["new_text"].count('Child "RemoveMagAnim"'), 1)
        self.assertEqual(r["new_text"].count('Child "RackBoltAnim"'), 1)
        self.assertIn('ToState "ReloadActionBolt"', r["new_text"])

    def test_idempotent(self):
        once = c.plan_graph_hardening(AGF_FIXTURE)["new_text"]
        twice = c.plan_graph_hardening(once)
        self.assertTrue(twice["ok"])
        self.assertEqual(twice["states"], [])

    def test_unexpected_structure_rejected(self):
        broken = AGF_FIXTURE.replace('Child "MagReloadSTM"\n      }\n      AnimSrcNodeState MagNoBulletReload {\n       Child "MagReloadSTM"', 'Child "InsertMagAnim"\n      }\n      AnimSrcNodeState MagNoBulletReload {\n       Child "InsertMagAnim"')
        r = c.plan_graph_hardening(broken)
        self.assertFalse(r["ok"])

    def test_broken_transition_endpoint_rejected(self):
        broken = AGF_FIXTURE.replace('ToState "ReloadActionBolt"', 'ToState "DoesNotExist"')
        r = c.plan_graph_hardening(broken)
        self.assertFalse(r["ok"])
        self.assertTrue(any("unknown state" in p for p in r["problems"]))


class RunTests(unittest.TestCase):
    def test_run_without_harden_changes_only_asi(self):
        with tempfile.TemporaryDirectory() as d:
            lab = make_lab(Path(d))
            agf_before = (lab / "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agf").read_text(encoding="utf-8")
            rc = c.run(lab, WG, PG, harden=False, dry_run=False)
            self.assertEqual(rc, 0)
            self.assertEqual((lab / "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agf").read_text(encoding="utf-8"), agf_before)
            asi = (lab / "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_weapon.asi").read_text(encoding="utf-8")
            self.assertIn("{" + WG + "}" + W_NEW, asi)

    def test_run_with_harden_changes_graph(self):
        with tempfile.TemporaryDirectory() as d:
            lab = make_lab(Path(d))
            rc = c.run(lab, WG, PG, harden=True, dry_run=False)
            self.assertEqual(rc, 0)
            agf = (lab / "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agf").read_text(encoding="utf-8")
            self.assertNotIn('Child "MagReloadSTM"', agf)
            self.assertEqual(agf.count('Child "RemoveMagAnim"'), 1)  # nested, outside STM

    def test_failed_preflight_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            lab = make_lab(Path(d))
            (lab / W_NEW).unlink()  # make preflight fail
            before = (lab / "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_weapon.asi").read_text(encoding="utf-8")
            rc = c.run(lab, WG, PG, harden=True, dry_run=False)
            self.assertEqual(rc, 1)
            after = (lab / "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_weapon.asi").read_text(encoding="utf-8")
            self.assertEqual(before, after)

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            lab = make_lab(Path(d))
            before = (lab / "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_weapon.asi").read_text(encoding="utf-8")
            rc = c.run(lab, WG, PG, harden=True, dry_run=True)
            self.assertEqual(rc, 0)
            after = (lab / "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_weapon.asi").read_text(encoding="utf-8")
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main(verbosity=2)