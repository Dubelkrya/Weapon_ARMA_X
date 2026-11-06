# MP-133 V3 — Astra isolated animation/graph source prototype

2026-10-03–04. **SOURCE_PROTOTYPE_OWNER_IMPORT_REQUIRED / STATIC_CONTRACTS_PASS**.
Compilation, imported animation, visual and runtime results: **NOT_TESTED**.

Authority: [assignment](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5970762059)
and [correction](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5970795240).
The owner subsequently instructed: “не запускай игру, тебе только составить систему,
проверю я сам”. No further Workbench/game launch after that instruction.
This report does not replace the primary T3F report or integrate T4.

## Deliverable and isolation

- Branch `codex/mp133-astra-shell-graph`, initially based on fresh `origin/main`
  `99c1819`, separate worktree; knowledge main not edited.
- [New lab source](../labs/ARMST_MP133_AstraShellGraph/README.md), ID
  `ARMSTMP133AstraShellGraph`, project GUID `CC35799EC8FA55E1`.
- Working directory:
  `C:\Users\yshky\Documents\Codex\2026-09-29\new-chat\outputs\mp133-astra-worktree`.
  The new addon is its `labs/ARMST_MP133_AstraShellGraph` subdirectory. It is not
  installed over any existing addon. Use Add Existing on its gproj.
- Dependencies: base `58D0FB3206B6F859`, production Weapons `6A70E400C54051DC`;
  Weapons transitively requires UI `6922BE16974B3AED`. No Core, T2A, V2/P2 or T4.
- All source/meta identities of pre-existing resources were left alone. New
  resource GUIDs are reserved by new meta files. Inherited prefab component IDs
  remain the original override addresses; replacing those with random IDs would
  create siblings rather than address the inherited animator.
- Exact source/output paths, SHA-256, reserved GUIDs and clip timing are in the
  [manifest](astra-shell-graph/manifest.json). Import is pending: a meta file is
  **not** an ANM and does not prove resource resolution.

## Source findings and architecture choice

Production source resolved through `agent/scripts/addon_path.py`. Inspected workspace:
`Assets/Weapons_RUS/Mp_133/Workspace`. Current `IdleReloadSTM` excludes commands
7–9 and -2; 10 is not excluded but has no implemented command-10 branch. Native
branches remain bolt=1, insert=2/3, remove+insert=4/5, remove=6. Old notes describing
a command-7 insertion node are not the current graph authority.

The minimal option was selected: clone compatible MP-133 graph/ASI resources and
cut the existing paired `P/W_MP133_Reload_Inject.txa`. Separately authored hand,
shell and weapon clips could improve the motion but require visual rig/contact
validation; this source-only iteration cannot justify replacing the existing rig
or claiming those authored clips finished. No Ithaca assets or scripts imported.

`MasterControl.Child0` now routes to `AstraRouteSTM`; other native nodes are
retained. `Child1` sight overlay remains native. The new route uses explicit
diagnostic parameters, not native command 7, native R, a fire handler or global
`modded` code. Standing (`Stance==0`) is the only supported prototype pose.

```text
Native (IdleReloadSTM) --Request + eligibility--> ShellReloadSTM
  StartReload -> GrabShell -> InsertShell -> CheckContinue
                    ^                          |         |
                    +---- Repeat + eligible ----+         |
                                                         v
                                                     EndReload
                                                         |
                                   NativeRearm (IdleReloadSTM)
                                                         |
                                            Request=false -> Native
```

Entry also checks no Firing, no inspection and no new native reload command.
This does **not** prove that a native reload already in progress is absent:
the owner must start from Idle. Do not mix native reload and diagnostic entry.
`NativeRearm` prevents a held Request from starting a new session, while allowing
the animation to return regardless of whether Request was cleared early.
The nested terminal-time behavior is inferred from existing engine graph
patterns and awaits Workbench compilation/preview.

Continuation is `Repeat && Eligible && !Stop && !FireStop && !Firing` at
CheckContinue. Stop completes the current insertion and suppresses the next.
Stop/FireStop must stay true until End; no input-edge latch exists. A transient
Firing pulse can be missed between boundaries, so it is not a real fire-stop
implementation. Full/no-reserve is simulated by Eligible=false; empty/partial
weapons use the same motion. No automatic chamber/rack operation is added.

Interior boundaries have zero blend because paired cut endpoints are retained;
repeat uses 0.05 s, outer entry/exit 0.1 s. These are authored prototype settings,
not visually verified timings. Repeat seam, pose drift and hand contact need review.

## Paired clips and markers

| Phase | Original frames, both sides | New last frame | Events |
| --- | --- | --- | --- |
| StartReload | hold 0 | 6 | StartReload at 1 |
| GrabShell | 0–32 | 32 | GrabShell at 1 |
| InsertShell | 32–107 | 75 | InsertShell at 1; InsertCommit at 11 |
| CheckContinue | hold 107 | 6 | CheckContinue at 1 |
| EndReload | hold 107 | 6 | EndReload at 1; Stop at 2; ReturnReady at 5 |

All 30 fps; source `#numFrames` conventions retained (keys include last frame).
Commit is original frame 43 minus cut start 32 = local 11 on **both** tracks.
P profile `A_UpperbodyADD_AllUp`; W profile `A_Weapon_MagRelease_All` inherited
from the original import configuration. Profile compatibility for the cuts remains
an owner import check; its name is not an event. Sources are UTF-8 without BOM.

All original events are removed from **new shell clips**, including BlendIn/Out,
SpawnMagazine, AttachMagazine, MagRelease. Original native clips stay referenced
by native ASI rows and are not edited. The existing native R branch can still
swap magazines; it is not a diagnostic trigger.

TXA sampling preserves each channel's last declared value over the source's
explicit constant frame spans. Both originals cover frames continuously (no gaps).
The empty `RightArmVolume` channel is retained as empty, not filled with an
invented transform. No procedural rig animation or generated image is involved.
The source movement is reused, **not** a proven new per-shell animation. A separate
visible shell prop is not spawned; its appearance/contact remains unverified.

## Diagnostics, ownership and T4 boundary

The new prefab overrides inherited animator address `{60B4EA76EB15F6E0}` under
WeaponComponent `{CFBAA4B706BA66E8}` with `ARMST_AstraShellAnimationComponent`.
It assigns the own AGR, weapon ASI and paired player AnimInjection (`Weapon`
binding). This is authored configuration, **not proof** that the subclass is
instantiated or the original component disappears. Verify actual component tree
and `[ARMST-ASTRA-SHELL] component_constructed` in the owner's run.

The callback calls super once and logs only `ASTRA_Shell*` markers. Both suffixes
can be observed on the weapon receiver; `_P` does not mean a character callback.
No character listener/subscription/global override is installed. Missing P markers
there cannot establish missing character animation. No hidden delivery bridge.

Only `ASTRA_ShellInsertCommit_W` may produce `diagnostic_candidate_no_transfer`,
after ordered Start→Grab→Insert. A local cycle/stage latch rejects repeated commit
callbacks within that cycle. This is **not** server/network exactly-once proof,
and delayed cross-cycle events are not solved by this local latch. Aborted or
out-of-order sequences fail closed; recreate the component before the next test.
Stop marks EndReload irrespective of completion reason. ReturnReady is a clip
marker, **not proof of actual Idle**; inspect the graph state for Idle.

Snapshots read current physical magazine entity, ammo/max and chamber predicates.
`magTag` identifies reference changes within one component, not a persistent ID.
No `SetAmmoCount`, PumpShotgun setter, SpawnShell, transfer, RPC, listener to
OnProjectileShot, command override, or automatic R/fire action is added.

Custom variable propagation from an equipped weapon to the injected player
graph is unresolved. The installed BaseItemAnimationComponent API does not expose
the BaseAnimPhys variable setters as weapon methods. Therefore this prototype
does not invent an in-game setter. Paired Animation Editor graph controls are
the supported initial test route; live trigger integration remains a gate.

Future T4 contract (not implemented): authoritative owner accepts a request with
session/cycle token, weapon and installed-magazine identity, verifies the same
live entities, capacity and compatible legitimate donor, and returns exactly one
`INSERT_COMMITTED` or `REJECTED`. One successful commit means destination +1,
donor -1, unchanged installed-mag identity and unchanged chamber. Deduplication
must live with that authoritative operation, not on both P/W callbacks. Only its
result may authorize the next insertion; graph markers alone never change ammo.

## Evidence and checks

Installed executable file version: **1.8.0.13**. API evidence under
`C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs`:

- `ArmaReforgerScriptAPIPublic/html/interfaceBaseItemAnimationComponent.html:140`:
  five-argument OnAnimationEvent (inherited by WeaponAnimationComponent);
  `interfaceWeaponAnimationComponent.html:130–141` shows owner, sync and callback.
- `interfaceGameAnimationUtils.html:116`: static `GetEventString(AnimationEventID)`.
- `interfaceBaseWeaponComponent.html:137–139`: `IsChamberingNecessary`,
  `IsChamberingPossible`, `GetCurrentMagazine`. No invented `IsChamberingNeeded`.
- `EnfusionScriptAPI/html/interfacestring.html:151`: StartsWith;
  `interfacebool.html:111`: ToString. Formatting split into short expressions.

Results:

- `python agent/scripts/validate_astra_shell_graph.py`: 168 static contract checks
  passed (resource/meta paths and unique IDs, closed transitions, 32-case repeat/
  stop truth table, paired times, one commit per side, isolated diagnostic script).
- Repository integrity checker passed; existing unittest suite: **82 tests passed**.
  These are Python/source checks, not an Enforce/graph compiler or visual tests.
- **0 imported ANM**. New clips are editable TXA plus reserved meta only.
- Workbench launch was attempted twice before the owner's no-launch instruction.
  Both attempts ended at startup with `Game addon '58D0FB3206B6F859' not found` /
  `Cannot initialize game project settings!`. Separate profile had incomplete
  addon search paths; repeated `-addonsDir` only retained its last value. No game
  session/Play, project compile, clip import or visual preview took place.
  No further launches are allowed by the latest instruction.

Preservation: initial hash set **4665** existing files. T2A **24/24**, frozen V2
**30/30**, consumed MP-133 workspace **66/66**, Core sampled Scripts/Prefabs/gproj
**4188/4188** unchanged. Separate P2 backup directories were not included in that
baseline, and were not edited. Do not expand this claim to every Core/Weapons file.

There were **35 changed/deleted other Weapons paths** during the task, while
Weapons advanced to `9ebf323` (optics work). They were not written/reset/staged by
this task and are preserved. Full global hash equality is therefore **NOT claimed**.
The changed-path evidence is in the manifest. Our authored writes are confined
to this branch's new lab, tools and report/pointers; no production writes by the
agent. Existing dirty Weapons world/RDB and Core weather/RDB/untracked gear remain.

## Owner acceptance and rollback

Follow [lab README](../labs/ARMST_MP133_AstraShellGraph/README.md): load own gproj,
compile, import ten TXA, verify reserved GUIDs/event tracks, open own AW.
First preview one cycle, then three repeats, Stop during Grab/Insert, FireStop,
Eligible=false before entry and mid-cycle, Request held through exit/rearmed.
Confirm both P/W poses and actual exit state; do not count ReturnReady as Idle.
Then, only on the owner's initiative, equipped-prefab diagnostics can test
instantiation, injected-variable propagation, event delivery and unchanged
physical magazine/ammo/chamber. All acceptance runtime gates remain open.

Do not fix missing dependency classes by connecting Core or editing production.
Stop on an own-resource/compiler error, wrong paired clip, double candidate,
unwanted magazine change or native rack regression. Send exact error/log/video.

Rollback: close/disable only `ARMSTMP133AstraShellGraph`. No production restore,
T2A rollback, new remote, merge or T4 action required. Generator refuses to write
different existing files or into the live addons tree; no delete/cleanup routine.
