"""Offline contracts for Astra's editable prototype. NOT an Enfusion compiler."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import re

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / 'labs/ARMST_MP133_AstraShellGraph'


def block(text, start):
    first = None
    depth = 0
    quoted = escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if escaped:
            escaped = False
            continue
        if quoted and ch == '\\':
            escaped = True
            continue
        if ch == '"':
            quoted = not quoted
        if not quoted:
            if ch == '{' and first is None:
                first = i
            depth += (ch == '{') - (ch == '}')
            if first is not None and depth == 0:
                return text[first+1:i]
    raise AssertionError('Unbalanced resource')


def verify(root):
    assets = root / 'Assets/MP133_AstraShellGraph'
    graph = (assets / 'MP133_Astra.agf').read_text()
    agr = (assets / 'MP133_Astra.agr').read_text()
    checks = []
    def check(condition, name):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    phases = ['StartReload', 'GrabShell', 'InsertShell', 'CheckContinue', 'EndReload']
    check('Child0 "IdleReloadSTM"' in graph and 'AstraRouteSTM' not in graph, 'Actual native Idle owns shell entry')
    check('DefaultRunNode "MasterControl"' in agr, 'Native entry retained')
    shell = block(graph, graph.index('AnimSrcNodeStateMachine ShellReloadSTM'))
    states = re.findall(r'AnimSrcNodeState (\w+)\s*{', shell)
    check(states == phases, 'Five shell phases in defined order')
    transitions = []
    for match in re.finditer('AnimSrcNodeTransition ', shell):
        body = block(shell, match.start())
        transitions.append(tuple(re.search(key+r' "([^"]+)"', body)[1]
                                 for key in ['FromState', 'ToState', 'Condition']))
    check({(a,b) for a,b,_ in transitions} == {
        ('StartReload','GrabShell'), ('GrabShell','InsertShell'),
        ('InsertShell','CheckContinue'), ('CheckContinue','GrabShell'),
        ('CheckContinue','EndReload'), ('StartReload','EndReload'),
        ('GrabShell','EndReload')}, 'Closed shell transition topology')
    for phase in phases:
        body = block(shell, shell.index('AnimSrcNodeState '+phase+' {'))
        check(f'IsExit {int(phase == "EndReload")}' in body, phase+' terminal flag')
    # Exhaustive truth table for the two actual serialized continuation predicates.
    predicates = {b:c for a,b,c in transitions if a == 'CheckContinue'}
    names = ['ASTRA_ShellRepeat','ASTRA_ShellEligible','ASTRA_ShellStop','ASTRA_FireStop','Firing']
    def evaluate(expr, values):
        expr = expr.replace('RemainingTimeLess(0.01)', 'True')
        expr = expr.replace('&&',' and ').replace('||',' or ').replace('!',' not ')
        return bool(eval(expr.strip(), {'__builtins__':{}}, values))
    for bits in itertools.product([False,True],repeat=len(names)):
        values = dict(zip(names,bits))
        loop = evaluate(predicates['GrabShell'], values)
        end = evaluate(predicates['EndReload'], values)
        check(loop != end, 'Continuation unique '+str(bits))
        check(loop == (bits[0] and bits[1] and not any(bits[2:])), 'Stop eligibility '+str(bits))
    route = block(graph, graph.index('AnimSrcNodeStateMachine IdleReloadSTM'))
    check('ToState "AstraWaitRelease"' in route and 'Condition "!ASTRA_ShellRequest"' in route,
          'Request release re-arms entry; exit is not held hostage by request')
    group=block(graph,graph.index('AnimSrcNodeGroupSelect AstraShellErcG'))
    check('Group "AstraShell"' in group and 'Column "Erc"' in group and
          'Child "ShellReloadSTM"' in group and 'Child "AstraShellErcG"' in route,
          'Explicit standing group context on shell path')
    check(all('Source "AstraShell.'+p+'"' in graph for p in phases), 'Sources use selected group column')
    check('Events {' not in shell and 'AnimSrcNodeEvent ' not in shell, 'No shell graph or transition events')

    resources = {}
    for meta in root.rglob('*.meta'):
        text = meta.read_text()
        gid,path = re.search(r'Name "\{([0-9A-F]{16})\}([^"]+)"',text).groups()
        check(gid not in resources, 'Unique resource GUID '+gid)
        check(path == meta.relative_to(root).as_posix()[:-5], 'Meta path '+path)
        resources[gid] = path
    expected_events = {}
    for phase in phases:
        paired = []
        for side in ['P','W']:
            stem = f'Clips/{side}_Astra_{phase}'
            text = (assets/(stem+'.txa')).read_text()
            events = [(int(f),n) for f,n in re.findall(r'#event (\d+) "([^"]+)"',text)]
            duration = int(re.search(r'#numFrames (\d+)',text)[1])
            check(all(0 <= f <= duration and n.startswith('ASTRA_Shell') for f,n in events),
                  'Only diagnostic events '+stem)
            check(sum(n == 'ASTRA_ShellInsertCommit_'+side for _,n in events) == int(phase=='InsertShell'),
                  'Exactly one commit track marker '+stem)
            check(all(int(f) <= duration for f in re.findall(r'\$frame (\d+)',text)), 'Frames bounded '+stem)
            check('#fps 30' in text and not (assets/(stem+'.txa')).read_bytes().startswith(b'\xef\xbb\xbf'), '30fps without BOM '+stem)
            paired.append((duration,[(f,n[:-2]) for f,n in events]))
            expected_events[stem] = events
            asi = (assets/f'MP133_Astra_{"player" if side=="P" else "weapon"}.asi').read_text()
            row = block(asi,asi.index('"AstraShell.Erc.'+phase+'"'))
            gid,path = re.search(r'Resource "\{([^}]+)\}([^"]+)"',row).groups()
            check(resources.get(gid) == path == 'Assets/MP133_AstraShellGraph/'+stem+'.anm', 'ASI paired clip '+stem)
        check(paired[0] == paired[1], 'Paired phase duration and marker times '+phase)
    script = next(root.rglob('*.c')).read_text()
    check(not re.search(r'\b(modded|SetAmmoCount|PumpShotgunSetAmmoCount|SpawnShell|OnCharacterCommand|OnProjectileShot)\b',script),
          'No global hook, command override or ammo setter')
    check(script.count('super.OnAnimationEvent(') == 1, 'Exactly one super event call in source')
    check('m_iStage == 3 && !m_bCandidate' in script, 'Local duplicate candidate latch')
    check('ASTRA_ShellInsertCommit_W' in script and 'ASTRA_ShellInsertCommit_P' not in script,
          'Only weapon-authored marker selects a candidate')
    return {'status':'STATIC_CONTRACTS_PASS', 'checks':len(checks),
            'anm_imported':len(list(assets.rglob('*.anm'))),
            'compile':'NOT_TESTED', 'runtime':'NOT_TESTED', 'visual':'NOT_TESTED',
            'events':expected_events}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lab',type=Path,default=DEFAULT)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    result = verify(args.lab)
    out = json.dumps(result,indent=2)
    if args.output:
        args.output.write_text(out+'\n',encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
