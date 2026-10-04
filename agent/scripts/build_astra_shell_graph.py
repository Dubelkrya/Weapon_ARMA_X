"""Generate editable lab resources only; no Workbench or gameplay execution.
The diagnostic script is maintained separately in labs/. Existing different files abort.
"""
from pathlib import Path
import re, json, hashlib, uuid, sys, argparse

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'agent/scripts'))
from addon_path import resolve_addon_root
from astra_node_foundation import refine_graph
PRODUCTION=resolve_addon_root()
ADDONS=PRODUCTION.parent
P=PRODUCTION/'Assets/Weapons_RUS/Mp_133/Workspace'
parser=argparse.ArgumentParser(description='Generate isolated editable MP133 animation resources; never imports or runs Workbench.')
parser.add_argument('--output',type=Path,default=ROOT/'labs/ARMST_MP133_AstraShellGraph')
LAB=parser.parse_args().output.resolve()
if LAB==PRODUCTION or PRODUCTION in LAB.parents or ADDONS in LAB.parents:
    raise SystemExit('Output must be outside the live addons tree')
NS=uuid.UUID('be7dc412-bf4c-4b35-9668-cde982650b1a')
def guid(s): return uuid.uuid5(NS,s).hex[:16].upper()
BASE='Assets/MP133_AstraShellGraph'
def ref(name): return '{'+guid(name)+'}'+BASE+'/'+name
def write(rel,s):
    p=LAB/rel; p.parent.mkdir(parents=True,exist_ok=True)
    data=s.replace('\r\n','\n').encode('utf-8')
    if p.exists() and p.read_bytes()!=data:
        raise RuntimeError('Refusing to overwrite different existing content: '+str(p))
    p.write_bytes(data)
def meta(rel,cls,extra=''):
    ident=guid(rel.removeprefix(BASE+'/'))
    existing=LAB/(rel+'.meta')
    if existing.exists():
        if f'Name "{{{ident}}}{rel}"' not in existing.read_text():
            raise RuntimeError('Existing resource identity differs: '+str(existing))
        return # Preserve all importer-owned bytes, not just its GUID.
    write(rel+'.meta',f'MetaFileClass {{\n Name "{{{ident}}}{rel}"\n Configurations {{\n  {cls} PC {{\n{extra}  }}\n  {cls} XBOX_ONE : PC {{\n  }}\n  {cls} XBOX_SERIES : PC {{\n  }}\n  {cls} PS4 : PC {{\n  }}\n  {cls} PS5 : PC {{\n  }}\n  {cls} HEADLESS : PC {{\n  }}\n }}\n}}\n')
def block(text,start):
    begin=text.index('{',start); depth=0; quoted=False; escape=False
    for i in range(begin,len(text)):
        c=text[i]
        if escape: escape=False; continue
        if c=='\\' and quoted: escape=True; continue
        if c=='"': quoted=not quoted
        if quoted: continue
        if c=='{': depth+=1
        if c=='}':
            depth-=1
            if depth==0:return begin,i+1
    raise ValueError('unbalanced')

def protect():
    paths=set()
    for sub in ['ARMSTMP133T2A_Diag','ARMST_MP133_AnimationLab']:
        paths.update(p for p in (ADDONS/sub).rglob('*') if p.is_file() and '.git' not in p.parts)
    paths.update(P.rglob('*'))
    for sub in ['ARMST-PLATFORM---Weapons','ARMST-PLATFORM---Core']:
        for folder in ['Scripts','Prefabs']:
            paths.update((ADDONS/sub/folder).rglob('*'))
        paths.add(ADDONS/sub/'addon.gproj')
    records={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths) if p.is_file()}
    (ROOT/'artifacts/astra_protected_before.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    return len(records)

if not (ROOT/'artifacts/astra_protected_before.json').exists():
    print('Protected files',protect())
LAB.mkdir(parents=True,exist_ok=True)
write('addon.gproj',f'GameProject {{\n ID "ARMSTMP133AstraShellGraph"\n GUID "{guid("project")}"\n TITLE "ARMST MP133 Astra Shell Graph LAB"\n Dependencies {{\n  "58D0FB3206B6F859" "6A70E400C54051DC"\n }}\n}}\n')

# New resources; native graph nodes remain intact except the routing child of MasterControl.
src_agf=(P/'MP133.agf').read_text()
agf=re.sub(r'\{([0-9A-F]{16})\}',lambda m:'{'+guid('node/'+m[1])+'}',src_agf)
assert agf.count('Child0 "IdleReloadSTM"')==1
agf=agf.replace('Child0 "IdleReloadSTM"','Child0 "AstraRouteSTM"')

def state(name,child,exit=False,initial=False):
    return f'      AnimSrcNodeState {name} {{\n       Child "{child}"\n       StartCondition "{str(initial).lower()}"\n       TimeStorage "Real Time"\n       IsExit {int(exit)}\n      }}\n'
def transition(a,b,condition,duration='0.0'):
    return f'      AnimSrcNodeTransition "{{{guid(a+"/"+b+"/"+condition)}}}" {{\n       FromState "{a}"\n       ToState "{b}"\n       Duration "{duration}"\n       Condition "{condition}"\n       BlendFn "S"\n       PostEval 1\n      }}\n'
def stm(name,states,trans):
    return f'    AnimSrcNodeStateMachine {name} {{\n     states {{\n{states}     }}\n     transitions {{\n{trans}     }}\n    }}\n'
eligible='ASTRA_ShellEligible && !ASTRA_ShellStop && !ASTRA_FireStop && !Firing'
route=stm('AstraRouteSTM',state('Native','IdleReloadSTM',initial=True)+state('Shell','ShellReloadSTM',exit=True)+state('NativeRearm','IdleReloadSTM'),
    transition('Native','Shell',f'ASTRA_ShellRequest && {eligible} && WeaponInspectionState == 0 && Stance == 0 && !IsCommand(CMD_Weapon_Reload)','0.1')+
    transition('Shell','NativeRearm','RemainingTimeLess(0.01)','0.1')+
    transition('NativeRearm','Native','!ASTRA_ShellRequest'))
phases={'StartReload':(0,0,6),'GrabShell':(0,32,None),'InsertShell':(32,107,None),'CheckContinue':(107,107,6),'EndReload':(107,107,6)}
states=''.join(state(n,'Astra'+n,exit=n=='EndReload',initial=n=='StartReload') for n in phases)
trans=transition('StartReload','GrabShell','RemainingTimeLess(0.01)')
trans+=transition('GrabShell','InsertShell','RemainingTimeLess(0.01)')
trans+=transition('InsertShell','CheckContinue','RemainingTimeLess(0.01)')
trans+=transition('CheckContinue','GrabShell',f'RemainingTimeLess(0.01) && ASTRA_ShellRepeat && {eligible}','0.05')
trans+=transition('CheckContinue','EndReload',f'RemainingTimeLess(0.01) && !(ASTRA_ShellRepeat && {eligible})')
nodes=route+stm('ShellReloadSTM',states,trans)
for n in phases:
    nodes+=f'    AnimSrcNodeSource Astra{n} {{\n     Source "AstraShell.Erc.{n}"\n     Looptype "No Loop"\n    }}\n'
agf=agf.replace('   Nodes {','   Nodes {\n'+nodes,1)
write(BASE+'/MP133_Astra.agf',refine_graph(agf));meta(BASE+'/MP133_Astra.agf','AnimGraphFileResourceClass')

agr=(P/'MP133.agr').read_text()
agr=re.sub(r'AnimSetTemplate "[^"]+"',f'AnimSetTemplate "{ref("MP133_Astra.ast")}"',agr,count=1)
agr=re.sub(r'"\{1E547F9548AB5BD7\}[^"]+"',f'"{ref("MP133_Astra.agf")}"',agr)
variables=''.join(f'   AnimSrcGCTVarBool {v} {{\n    DefaultValue {default}\n   }}\n' for v,default in [('ASTRA_ShellRequest',0),('ASTRA_ShellRepeat',0),('ASTRA_ShellStop',0),('ASTRA_FireStop',0),('ASTRA_ShellEligible',1)])
agr=agr.replace('  Variables {','  Variables {\n'+variables,1)
agr=re.sub(r'\{6906[0-9A-F]{12}\}',lambda m:'{'+guid('agr/'+m[0])+'}',agr)
write(BASE+'/MP133_Astra.agr',agr);meta(BASE+'/MP133_Astra.agr','AnimGraphResourceClass')
ast=(P/'MP133.ast').read_text();ast=ast.replace(' Groups {',' Groups {\n  AnimSetTemplateSource_AnimationGroup "{'+guid('shell-group')+'}" {\n   Name "AstraShell"\n   Animations {\n'+''.join(f'    "{n}"\n' for n in phases)+'   }\n   Columns {\n    "Erc"\n   }\n  }',1)
ast=re.sub(r'\{6906[0-9A-F]{12}\}',lambda m:'{'+guid('ast/'+m[0])+'}',ast)
write(BASE+'/MP133_Astra.ast',ast);meta(BASE+'/MP133_Astra.ast','AnimSetTemplateResourceClass')

def event(frame,name):
    return f'  #event {frame} "{name}" "AnimSrcEventGeneric {{  Name \\"{name}\\"  MainPathOnly 0  Frame {frame}  FrameCount 0  UserString \\"\\"  UserInt -1 }}" -1 0 "" 0\n'
def cut_txa(source,start,end,hold,events):
    # TXA frame values are sparse channel updates; reconstruct step sample at every original
    # integer keyframe before slicing. Source inspection verifies dense animated channels.
    out=source
    matches=list(re.finditer(r'\$keys ([tqs ]+)\{',source))
    for m in reversed(matches):
        left,right=block(source,m.start()); body=source[left+1:right-1]
        keys=[]
        for fm in re.finditer(r'\$frame (\d+)(?: (\d+))?\s*\{',body):
            fl,fr=block(body,fm.start())
            values={ch:val.strip() for ch,val in re.findall(r'#([tqs])\s+([^\r\n]+)',body[fl+1:fr-1])}
            keys.append((int(fm[1]),values))
        assert keys and keys[0][0]==0
        duration=hold if hold is not None else end-start
        cur={};idx=0; lines=[]
        for f in range(duration+1):
            original=start if hold is not None else start+f
            while idx<len(keys) and keys[idx][0]<=original:
                cur.update(keys[idx][1]);idx+=1
            # Empty channel blocks occur in the original (RightArmVolume).
            # Preserve their absence; never synthesize a bind transform.
            lines.append('    $frame '+str(f)+' {\n'+''.join(f'     #{ch} {cur[ch]}\n' for ch in m[1].split() if ch in cur)+'    }\n')
        out=out[:left+1]+'\n'+''.join(lines)+'   '+out[right-1:]
    num=hold if hold is not None else end-start
    out=re.sub(r'#numFrames \d+',f'#numFrames {num}',out,count=1)
    el,er=block(out,out.index('$events'))
    out=out[:el+1]+'\n'+''.join(event(f,n) for f,n in events)+' '+out[er-1:]
    return out

clip_manifest=[]
for side,profile in [('P','A_UpperbodyADD_AllUp'),('W','A_Weapon_MagRelease_All')]:
    original=P/'Reload'/f'{side}_MP133_Reload_Inject.txa';source=original.read_text()
    for phase,(start,end,hold) in phases.items():
        dur=hold if hold is not None else end-start
        ev=[(1,f'ASTRA_Shell_{phase}_{side}')]
        if phase=='InsertShell': ev.append((43-start,f'ASTRA_ShellInsertCommit_{side}'))
        if phase=='EndReload':
            ev.append((2,f'ASTRA_Shell_Stop_{side}'))
            ev.append((dur-1,f'ASTRA_Shell_ReturnReady_{side}'))
        name=f'Clips/{side}_Astra_{phase}'
        write(BASE+'/'+name+'.txa',cut_txa(source,start,end,hold,ev))
        meta(BASE+'/'+name+'.anm','TXAResourceClass',f'   SourcePath "{name.split("/")[-1]}.txa"\n   SourceProfile "{profile}"\n')
        clip_manifest.append(dict(side=side,phase=phase,original=str(original),source_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),original_range=[start,end],last_frame=dur,fps=30,events=ev,anm_guid=guid(name+'.anm'),anm_status='IMPORT_REQUIRED'))
    asi=(P/f'MP133_{"player" if side=="P" else "weapon"}.asi').read_text()
    asi=re.sub(r'Template "[^"]+"',f'Template "{ref("MP133_Astra.ast")}"',asi,count=1)
    entries=''.join(f'  AnimSetInstanceSource_Line "AstraShell.Erc.{phase}" {{\n   Resource "{ref(f"Clips/{side}_Astra_{phase}.anm")}"\n  }}\n' for phase in phases)
    asi=asi.replace(' Lines {',' Lines {\n'+entries,1)
    asi=re.sub(r'\{6906[0-9A-F]{12}\}',lambda m:'{'+guid('asi/'+m[0])+'}',asi)
    suffix='player' if side=='P' else 'weapon'
    write(BASE+f'/MP133_Astra_{suffix}.asi',asi);meta(BASE+f'/MP133_Astra_{suffix}.asi','AnimSetInstanceResourceClass')

aw=(P/'MP133.aw').read_text()
for old,new in [('23A8072FE1CDE614','MP133_Astra.ast'),('CE3F8A5CEF0667C1','MP133_Astra_weapon.asi'),('35611B6D7707032D','MP133_Astra_player.asi'),('315A612FD60832E7','MP133_Astra.agr')]:
    aw=re.sub(r'\{'+old+r'\}[^"\r\n]+',ref(new),aw)
aw=re.sub(r'\{6906[0-9A-F]{12}\}',lambda m:'{'+guid('aw/'+m[0])+'}',aw)
write(BASE+'/MP133_Astra.aw',aw);meta(BASE+'/MP133_Astra.aw','AnimWorkspaceResourceClass')
prefab=f'''GenericEntity : "{{63FF6FDCA4E7E735}}Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et" {{
 ID "{guid('entity')}"
 components {{
  SCR_WeaponAttachmentsStorageComponent "{{51F080D5CE45A1A2}}" {{
   Attributes SCR_ItemAttributeCollection "{{51F080D5C64F12C5}}" {{
    ItemDisplayName WeaponUIInfo "{{5222CB07CFF6712A}}" {{
     Name "MP-133 [ASTRA ANIMATION ONLY]"
    }}
   }}
  }}
  WeaponComponent "{{CFBAA4B706BA66E8}}" {{
   components {{
    ARMST_AstraShellAnimationComponent "{{60B4EA76EB15F6E0}}" {{
     AnimGraph "{ref('MP133_Astra.agr')}"
     AnimInstance "{ref('MP133_Astra_weapon.asi')}"
     AnimInjection AnimationAttachmentInfo "{{532F3A9CB912F2BA}}" {{
      AnimGraph "{ref('MP133_Astra.agr')}"
      AnimInstance "{ref('MP133_Astra_player.asi')}"
      BindingName "Weapon"
     }}
     BindWithInjection 1
    }}
   }}
  }}
 }}
}}
'''
write('Prefabs/Weapons/MP133_AstraShellGraph.et',prefab);meta('Prefabs/Weapons/MP133_AstraShellGraph.et','EntityPrefabResourceClass')
(ROOT/'artifacts/astra_clip_manifest.json').write_text(json.dumps(clip_manifest,indent=2),encoding='utf-8')
print('New lab',LAB,'project',guid('project'),'files',len(list(LAB.rglob('*'))))
