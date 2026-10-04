"""Source-only contracts for the repaired authoring workspace; no engine execution."""
from pathlib import Path
import re, unittest
ROOT=Path(__file__).resolve().parents[2]
ASSETS=ROOT/'labs/ARMSTMP133T4B_InstalledMagProbe/Assets/MP133_AstraShellGraph_test'

def body(text, anchor):
    start=text.index(anchor);level=0;quoted=False
    for i in range(start,len(text)):
        if text[i]=='"':quoted=not quoted
        if quoted:continue
        if text[i]=='{':level+=1
        elif text[i]=='}':
            level-=1
            if level==0:return text[start:i+1]
    raise AssertionError('unclosed block')

class AstraRebuildContracts(unittest.TestCase):
    def setUp(self):self.graph=(ASSETS/'MP133_Astra.agf').read_text()
    def test_native_entry_only_rack(self):
        edge=body(self.graph,'AnimSrcNodeTransition "{398BA5133896591E}"')
        self.assertIn('GetCommandI(CMD_Weapon_Reload) == 1',edge)
        self.assertIn('GetCommandF(CMD_Weapon_Reload) == 0.0',edge)
        route=body(self.graph,'AnimSrcNodeStateMachine ReloadRouteSTM')
        self.assertNotIn('AnimSrcNodeState Shell',route)
        self.assertNotIn('AstraShell',route)
    def test_no_legacy_mag_sources_anywhere_in_new_resources(self):
        for filename in ['MP133_Astra.agf','MP133_Astra.ast','MP133_Astra_player.asi','MP133_Astra_weapon.asi']:
            s=(ASSETS/filename).read_text()
            for bad in ['Reload_InsertMag','Reload_RemoveMag','Weapon_SpawnMagazine','Weapon_AttachMagazine','Weapon_DetachMagazine','Weapon_DespawnMagazine','Weapon_MagRelease']:
                self.assertNotIn(bad,s,(filename,bad))
    def test_no_unbound_debug_controls(self):
        self.assertNotIn('ASTRA_',self.graph)
        self.assertNotIn('ASTRA_', (ASSETS/'MP133_Astra.agr').read_text())
    def test_rack_both_stances_have_group_context(self):
        for stance in ['Erc','Pne']:
            node=body(self.graph,'AnimSrcNodeGroupSelect Rack'+stance+'G')
            self.assertIn('Group "Reload"',node)
            self.assertIn('Column "'+stance+'"',node)
            self.assertIn('Child "RackBoltAnim"',node)
    def test_exact_five_paired_sources_and_template(self):
        phases=['StartReload','GrabShell','InsertShell','CheckContinue','EndReload']
        ast=(ASSETS/'MP133_Astra.ast').read_text()
        group=body(ast,'AnimSetTemplateSource_AnimationGroup "{6A8947ABB9A94F69}"')
        for phase in phases:self.assertIn('"'+phase+'"',group)
        for side,prefix in [('player','P'),('weapon','W')]:
            s=(ASSETS/f'MP133_Astra_{side}.asi').read_text()
            for phase in phases:
                row=body(s,'AnimSetInstanceSource_Line "Reload.Erc.'+phase+'"')
                self.assertIn('/Clips/'+prefix+'_Astra_'+phase+'.anm',row)
            self.assertEqual(s.count('AnimSetInstanceSource_Line "Reload.Erc.'),len(phases))
            self.assertNotIn('AnimSetInstanceSource_Line "AstraShell.',s)
        node=body(self.graph,'AnimSrcNodeGroupSelect AstraShellErcG')
        self.assertIn('Group "Reload"',node)
        self.assertIn('Column "Erc"',node)
        for phase in phases:
            self.assertIn('Source "Reload.'+phase+'"',self.graph)
    def test_finite_cycle_no_speculative_repeat(self):
        shell=body(self.graph,'AnimSrcNodeStateMachine ShellReloadSTM')
        transitions=re.findall(r'FromState "([^"]+)"\s+ToState "([^"]+)"',shell)
        self.assertEqual(set(transitions),{('StartReload','GrabShell'),('StartReload','EndReload'),('GrabShell','InsertShell'),('GrabShell','EndReload'),('InsertShell','CheckContinue'),('CheckContinue','EndReload')})
        for phase in ['StartReload','GrabShell']:
            self.assertIn('TriggerPulled',shell)
        self.assertEqual(shell.count('PostEval 1'),6)
    def test_all_named_child_nodes_resolve(self):
        names=[]
        for m in re.finditer(r'^    AnimSrcNode\w+ ("[^"]+"|\w+) \{',self.graph,re.M):names.append(m[1].strip('"'))
        self.assertEqual(len(names),len(set(names)))
        for child in re.findall(r'\bChild(?:0|1)? "([^"]+)"',self.graph):self.assertIn(child,names)
    def test_no_new_action_or_ammo_in_fixture(self):
        p=ASSETS.parents[1]/'Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et'
        s=p.read_text()
        self.assertNotIn('additionalActions',s)
        self.assertEqual(s.count('"{60B4EA76EB15F6E0}"'),1)

if __name__=='__main__':unittest.main()
