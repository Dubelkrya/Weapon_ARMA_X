"""Static integration contracts. Does not load Enfusion or require local ANM binaries."""
from pathlib import Path
import re
import unittest
ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT/'labs/ARMSTMP133T4B_InstalledMagProbe'
ASSETS = LAB/'Assets/MP133_AstraShellGraph'
PREFAB = LAB/'Prefabs/Test/ARMST_T4B_AstraV2_Bridge_TestWeapon.et'
SCRIPT = LAB/'Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c'

def tokens(s):
    return re.findall(r'"[^"\n]*"|[{}]|[^\s{}]+', s)

def balanced(s):
    level=0
    for t in tokens(s):
        if t=='{':level+=1
        elif t=='}':level-=1
        if level<0:return False
    return level==0

class AstraT4BIntegrationTests(unittest.TestCase):
    def test_single_nested_animator(self):
        s=PREFAB.read_text()
        self.assertTrue(balanced(s))
        self.assertEqual(s.count('"{60B4EA76EB15F6E0}"'),1)
        self.assertIn('ARMST_T4B_AstraV2_WeaponAnimationComponent "{60B4EA76EB15F6E0}"',s)
        self.assertLess(s.index('WeaponComponent "{CFBAA4B706BA66E8}"'),s.index('ARMST_T4B_AstraV2_WeaponAnimationComponent'))
        self.assertTrue(s.startswith('GenericEntity : "{63FF6FDCA4E7E735}'))
    def test_bindings_and_independent_action(self):
        s=PREFAB.read_text()
        self.assertEqual(s.count('{9A5A46E2D8F8586F}'),2)
        for value in ['AE8E3367177C57BD','2629533DCE9A5811','CD8091A2B3C4D5E6','BindingName "Weapon"','BindWithInjection 1','m_iT4BStartAmmo 2','m_iG3B2RequiredTargetMax 3','m_bG3B2WriteEnabled 1','m_bG3B2InventoryWide 1']:self.assertIn(value,s)
        self.assertEqual(s.count('ARMST_T4B_G3B2_TransferAction'),1)
        self.assertNotIn('Lab_MP133',s)
    def test_callback_chain_has_no_transfer_or_input(self):
        s=SCRIPT.read_text()
        self.assertIn(': ARMST_T4B_WeaponAnimationComponent\n',s)
        self.assertEqual(s.count('super.OnAnimationEvent('),1)
        for forbidden in ['SetAmmoCount(', 'PerformAction(', 'override void OnCharacterCommand', 'modded class', 'AddActionListener']:self.assertNotIn(forbidden,s)
        self.assertIn('m_iStage == 3 && !m_bCandidate',s)
        self.assertIn('ended_before_insert_no_candidate',s)
    def test_paired_rows_match_authored_clips(self):
        for side,prefix in [('player','P'),('weapon','W')]:
            s=(ASSETS/f'MP133_Astra_{side}.asi').read_text()
            rows=re.findall(r'"AstraShell.Erc.([^"]+)"\s*\{\s*Resource "\{([^}]+)\}([^"]+)"',s)
            self.assertEqual(len(rows),5)
            for phase,gid,path in rows:
                self.assertEqual(path,f'Assets/MP133_AstraShellGraph/Clips/{prefix}_Astra_{phase}.anm')
                self.assertTrue((LAB/path).with_suffix('.txa').exists())
    def test_graph_keeps_native_and_release_gate(self):
        s=(ASSETS/'MP133_Astra.agf').read_text()
        for value in ['AstraShellErcG','ShellReloadSTM','AstraWaitRelease','!ASTRA_ShellRequest','GetCommandI(CMD_Weapon_Reload) == 1']:self.assertIn(value,s)
        self.assertTrue(balanced(s))
    def test_no_fabricated_registration_or_binaries_in_snapshot(self):
        self.assertFalse(Path(str(PREFAB)+'.meta').exists())
        self.assertEqual(len(list(ASSETS.rglob('*.anm'))),0)
        self.assertEqual(len(list(ASSETS.rglob('*.anm.meta'))),0)
        self.assertEqual(len(list(ASSETS.rglob('*.txa'))),10)

if __name__=='__main__':unittest.main()
