"""Pure V1 -> V2 graph transform. Does not open editors or touch metadata."""
import re
import uuid
from validate_astra_shell_graph import block

NS = uuid.UUID('be7dc412-bf4c-4b35-9668-cde982650b1a')


def replace_body(text, anchor, change):
    start = text.index(anchor)
    body = block(text, start)
    pos = text.index(body, start)
    return text[:pos] + change(body) + text[pos+len(body):]


def edge(a, b, condition, duration='0.0'):
    ident = uuid.uuid5(NS, 'foundation2/'+a+'/'+b).hex[:16].upper()
    return (f'      AnimSrcNodeTransition "{{{ident}}}" {{\n'
            f'       FromState "{a}"\n       ToState "{b}"\n'
            f'       Duration "{duration}"\n       Condition "{condition}"\n'
            '       BlendFn "S"\n       PostEval 1\n      }\n')


ELIGIBLE = 'ASTRA_ShellEligible && !ASTRA_ShellStop && !ASTRA_FireStop && !Firing'
ENTRY = ('ASTRA_ShellRequest && '+ELIGIBLE+
         ' && WeaponInspectionState == 0 && Stance == 0 && !IsCommand(CMD_Weapon_Reload)')


def refine_graph(text):
    if 'AnimSrcNodeState AstraWaitRelease {' in text:
        raise ValueError('V2 already present; refusing a second transform')
    start = text.index('    AnimSrcNodeStateMachine AstraRouteSTM {')
    end = text.index('    AnimSrcNodeStateMachine ShellReloadSTM {', start)
    text = text[:start] + text[end:]
    text = text.replace('Child0 "AstraRouteSTM"', 'Child0 "IdleReloadSTM"')
    # Enter from the actual Idle state, never from the enclosing running native STM.
    def idle(body):
        states = '''
      AnimSrcNodeState AstraShell {
       EditorPos 9 0
       Child "AstraShellErcG"
       StartCondition "false"
       TimeStorage "Real Time"
       IsExit 1
      }
      AnimSrcNodeState AstraWaitRelease {
       EditorPos 9 3
       Child "Queue 1"
       StartCondition "false"
       IsExit 0
      }
'''
        body = body.replace('     states {', '     states {'+states, 1)
        transitions = edge('Idle','AstraShell',ENTRY,'0.1')
        transitions += edge('AstraShell','AstraWaitRelease','RemainingTimeLess(0.01)','0.1')
        transitions += edge('AstraWaitRelease','Idle','!ASTRA_ShellRequest')
        body = body.replace('     transitions {','     transitions {\n'+transitions,1)
        # Own request never deliberately selects a native full-magazine branch.
        # This graph predicate is NOT suppression of a game-side reload command.
        for match in list(re.finditer('AnimSrcNodeTransition ',body)):
            old = block(body,match.start())
            if 'FromState "Idle"' in old and 'ToState "Buffer3"' in old:
                new = old.replace('Condition "','Condition "(!ASTRA_ShellRequest || GetCommandI(CMD_Weapon_Reload) == 1) && ',1)
                body = body.replace(old,new,1)
                break
        else:
            raise ValueError('Native Idle reload edge absent')
        return body
    text = replace_body(text,'AnimSrcNodeStateMachine IdleReloadSTM {',idle)
    def shell(body):
        # Stop before entering Insert skips commit; once Insert begins it finishes.
        for source,target in [('StartReload','GrabShell'),('GrabShell','InsertShell')]:
            for match in list(re.finditer('AnimSrcNodeTransition ',body)):
                old = block(body,match.start())
                if f'FromState "{source}"' in old and f'ToState "{target}"' in old:
                    new = old.replace('Condition "RemainingTimeLess(0.01)"',
                                      'Condition "RemainingTimeLess(0.01) && '+ELIGIBLE+'"')
                    body = body.replace(old,new,1)
                    break
            else:
                raise ValueError('Missing phase edge '+source)
        aborts = ''.join(edge(s,'EndReload','RemainingTimeLess(0.01) && !('+ELIGIBLE+')','0.1')
                         for s in ['StartReload','GrabShell'])
        body = body.replace('     transitions {','     transitions {\n'+aborts,1)
        for i,phase in enumerate(['StartReload','GrabShell','InsertShell','CheckContinue','EndReload']):
            body=body.replace('AnimSrcNodeState '+phase+' {',
                              'AnimSrcNodeState '+phase+' {\n       EditorPos '+str(i*4)+' 0')
        return body
    text=replace_body(text,'AnimSrcNodeStateMachine ShellReloadSTM {',shell)
    group='''    AnimSrcNodeGroupSelect AstraShellErcG {
     EditorPos 12 -4
     Child "ShellReloadSTM"
     Group "AstraShell"
     Column "Erc"
    }
'''
    text=text.replace('    AnimSrcNodeStateMachine ShellReloadSTM {',group+
                      '    AnimSrcNodeStateMachine ShellReloadSTM {\n     EditorPos 16 -4',1)
    for i,phase in enumerate(['StartReload','GrabShell','InsertShell','CheckContinue','EndReload']):
        text=text.replace('AnimSrcNodeSource Astra'+phase+' {',
                          'AnimSrcNodeSource Astra'+phase+' {\n     EditorPos '+str(16+i*4)+' -8')
        text=text.replace('Source "AstraShell.Erc.'+phase+'"','Source "AstraShell.'+phase+'"')
    return text
