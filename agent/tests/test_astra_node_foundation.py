"""Read serialized transition predicates; no claim of Enfusion scheduling equivalence."""
import itertools
from pathlib import Path
import re
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from validate_astra_shell_graph import block, verify, DEFAULT

GRAPH=(DEFAULT/'Assets/MP133_AstraShellGraph/MP133_Astra.agf').read_text()


def edges(stm):
    body=block(GRAPH,GRAPH.index('AnimSrcNodeStateMachine '+stm+' {'))
    result=[]
    for m in re.finditer('AnimSrcNodeTransition ',body):
        b=block(body,m.start())
        result.append(tuple(re.search(k+r' "([^"]+)"',b)[1] for k in ['FromState','ToState','Condition']))
    return result


def context(**overrides):
    c=dict(ASTRA_ShellRequest=True,ASTRA_ShellRepeat=False,ASTRA_ShellEligible=True,
           ASTRA_ShellStop=False,ASTRA_FireStop=False,Firing=False,WeaponInspectionState=0,Stance=0)
    c.update(overrides)
    return c


def destinations(stm,state,c,command=None,expired=True):
    found=[]
    for a,b,expr in edges(stm):
        if a!=state:continue
        expr=expr.replace('RemainingTimeLess(0.01)',str(expired))
        expr=expr.replace('IsCommand(CMD_Weapon_Reload)',str(command is not None))
        expr=expr.replace('GetCommandI(CMD_Weapon_Reload)',str(command or 0))
        expr=re.sub(r'!(?!=)',' not ',expr.replace('&&',' and ').replace('||',' or '))
        # Only the three relevant entry/re-arm destinations are part of this predicate test.
        if b not in ['AstraShell','AstraWaitRelease','Idle','Buffer3'] and stm=='IdleReloadSTM':continue
        if eval(expr.strip(),{'__builtins__':{},'inRange':lambda v,a,b:a<=v<=b},c):found.append(b)
    return found


class AstraGraphContract(unittest.TestCase):
    def test_whole_source_contract(self):
        self.assertEqual(verify(DEFAULT)['status'],'STATIC_CONTRACTS_PASS')

    def test_entry_only_from_actual_idle(self):
        incoming=[a for a,b,_ in edges('IdleReloadSTM') if b=='AstraShell']
        self.assertEqual(incoming,['Idle'])
        self.assertEqual(destinations('IdleReloadSTM','Idle',context()),['AstraShell'])

    def test_native_commands_never_start_shell(self):
        for cmd in range(-2,11):
            with self.subTest(cmd=cmd):
                targets=destinations('IdleReloadSTM','Idle',context(),cmd)
                self.assertNotIn('AstraShell',targets)
                if cmd in [2,3,4,5,6]:self.assertNotIn('Buffer3',targets)
        self.assertIn('Buffer3',destinations('IdleReloadSTM','Idle',context(),1))

    def test_native_command_routes_retained_without_request(self):
        for cmd in [1,2,3,4,5,6,10]:
            self.assertIn('Buffer3',destinations('IdleReloadSTM','Idle',context(ASTRA_ShellRequest=False),cmd))

    def test_entry_rejects_unsafe_context(self):
        for change in [dict(ASTRA_ShellEligible=False),dict(ASTRA_ShellStop=True),
                       dict(ASTRA_FireStop=True),dict(Firing=True),dict(Stance=2),dict(WeaponInspectionState=1)]:
            self.assertNotIn('AstraShell',destinations('IdleReloadSTM','Idle',context(**change)))

    def test_predicates_are_exclusive_and_wait_for_boundary(self):
        names=['ASTRA_ShellRepeat','ASTRA_ShellEligible','ASTRA_ShellStop','ASTRA_FireStop','Firing']
        for values in itertools.product([False,True],repeat=5):
            c=context(**dict(zip(names,values)))
            for state in ['StartReload','GrabShell','InsertShell','CheckContinue']:
                self.assertEqual(len(destinations('ShellReloadSTM',state,c)),1)
                self.assertEqual(destinations('ShellReloadSTM',state,c,expired=False),[])

    def test_stop_before_insert_never_visits_commit_clip(self):
        for stop in ['ASTRA_ShellStop','ASTRA_FireStop']:
            for phase in ['StartReload','GrabShell']:
                self.assertEqual(destinations('ShellReloadSTM',phase,context(**{stop:True})),['EndReload'])

    def test_stop_after_insert_entry_finishes_once_and_exits(self):
        c=context(ASTRA_ShellRepeat=True,ASTRA_ShellStop=True)
        self.assertEqual(destinations('ShellReloadSTM','InsertShell',c),['CheckContinue'])
        self.assertEqual(destinations('ShellReloadSTM','CheckContinue',c),['EndReload'])

    def test_three_cycles_then_held_request_release(self):
        c=context(ASTRA_ShellRepeat=True);phase='StartReload';visits=0
        for _ in range(20):
            if phase=='InsertShell':visits+=1
            if phase=='CheckContinue' and visits==3:c['ASTRA_ShellStop']=True
            if phase=='EndReload':break
            phase=destinations('ShellReloadSTM',phase,c)[0]
        self.assertEqual((visits,phase),(3,'EndReload'))
        self.assertEqual(destinations('IdleReloadSTM','AstraShell',c),['AstraWaitRelease'])
        self.assertEqual(destinations('IdleReloadSTM','AstraWaitRelease',c),[])
        c['ASTRA_ShellRequest']=False
        self.assertEqual(destinations('IdleReloadSTM','AstraWaitRelease',c),['Idle'])


if __name__=='__main__':unittest.main()
