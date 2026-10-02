#!/usr/bin/env python3
"""Tests for the one-command lab clip connector (issue #27)."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import mp133_lab_connect_anims as c  # noqa: E402

W_OLD = c.W_OLD_REL
P_OLD = c.P_OLD_REL
W_NEW = c.W_ANM_REL
P_NEW = c.P_ANM_REL


class RepointRowsTests(unittest.TestCase):
    def test_repoints_both_rows(self):
        text = (
            'AnimSetInstanceSource_Line "Reload.Erc.Reload_InsertMag" {\n'
            f' Resource "{{45B1772B8AFEAE47}}{W_OLD}"\n'
            '}\n'
            'AnimSetInstanceSource_Line "Reload.Pne.Reload_InsertMag" {\n'
            f' Resource "{{45B1772B8AFEAE47}}{W_OLD}"\n'
            '}\n')
        out = c.repoint_inject_rows(text, "AABBCCDDEEFF0011", W_OLD, W_NEW)
        self.assertIn('{AABBCCDDEEFF0011}' + W_NEW, out)
        self.assertNotIn(W_OLD, out)

    def test_idempotent_after_connect(self):
        text = (
            'AnimSetInstanceSource_Line "Reload.Erc.Reload_InsertMag" {\n'
            f' Resource "{{AABBCCDDEEFF0011}}{W_NEW}"\n'
            '}\n'
            'AnimSetInstanceSource_Line "Reload.Pne.Reload_InsertMag" {\n'
            f' Resource "{{AABBCCDDEEFF0011}}{W_NEW}"\n'
            '}\n')
        self.assertEqual(c.repoint_inject_rows(text, "AABBCCDDEEFF0011", W_OLD, W_NEW), text)

    def test_missing_rows_raises(self):
        with self.assertRaises(SystemExit):
            c.repoint_inject_rows('no rows here', "AABBCCDDEEFF0011", W_OLD, W_NEW)


class HardenGraphTests(unittest.TestCase):
    def test_reroutes_mag_states(self):
        text = ('AnimSrcNodeState MagReload {\n Child "MagReloadSTM"\n}\n'
                'AnimSrcNodeState RemoveMag {\n Child "RemoveMagAnim"\n}\n'
                'AnimSrcNodeState ReloadActionBolt {\n Child "RackBoltAnim"\n}\n')
        out = c.harden_graph(text)
        self.assertNotIn('Child "MagReloadSTM"', out)
        self.assertNotIn('Child "RemoveMagAnim"', out)
        self.assertIn('Child "RackBoltAnim"', out)  # pump untouched
        self.assertEqual(out.count('Child "InsertMagAnim"'), 2)

    def test_idempotent(self):
        text = 'AnimSrcNodeState X {\n Child "InsertMagAnim"\n}\n'
        self.assertEqual(c.harden_graph(text), text)


class GuidTests(unittest.TestCase):
    def test_accepts_braced_and_plain(self):
        self.assertEqual(c._guid("{aabbccddeeff0011}"), "AABBCCDDEEFF0011")
        self.assertEqual(c._guid("AABBCCDDEEFF0011"), "AABBCCDDEEFF0011")

    def test_rejects_bad(self):
        with self.assertRaises(SystemExit):
            c._guid("not-a-guid")


if __name__ == "__main__":
    unittest.main(verbosity=2)