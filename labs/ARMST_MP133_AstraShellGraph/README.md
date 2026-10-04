# MP-133 Astra: V2 node foundation

Current report: [V2 foundation](../../reports/MP133_V3_ASTRA_NODE_FOUNDATION_V2.md).
Ten owner-imported ANMs are present locally; their event tracks and playback remain unverified. They and their modified metadata are preserved, not published.

Status: **SOURCE_PROTOTYPE / OWNER_IMPORT_AND_TEST_REQUIRED**.
No compiled ANM is included. Script compilation, graph compilation, visual motion,
event delivery and in-game behavior are **NOT_TESTED**. The owner requested that
the agent prepare the system only and not launch the game/Workbench again.

This new addon is separate from production Weapons, Core, T2A, V2/P2 and T4.
Project ID `ARMSTMP133AstraShellGraph`; GUID `CC35799EC8FA55E1`.
Dependencies: base game `58D0FB3206B6F859`, Weapons `6A70E400C54051DC`, and its
existing transitive UI dependency `6922BE16974B3AED`. Core is not required or allowed.

## Owner setup (no Play needed for initial checks)

1. In the Workbench launcher, **Add Existing** this folder's `addon.gproj`.
   Check that base game, Weapons and its UI dependency are available. Open this
   project, not T2A/production. Keep Core, frozen V2/P2 and T4 off.
2. Compile scripts. The isolated prefab is
   `Prefabs/Weapons/MP133_AstraShellGraph.et`. Its inherited animator override
   must resolve to `ARMST_AstraShellAnimationComponent`. Stop on any script error.
3. If the existing local imports resolve correctly, keep them: TXA sources are unchanged. Otherwise import the ten `Assets/MP133_AstraShellGraph/Clips/*.txa` into ANM **beside
   those TXA files**. Use the Animation Editor/Resource Manager TXA importer.
   P profiles: `A_UpperbodyADD_AllUp`; W profiles: `A_Weapon_MagRelease_All`.
   Source and output stems must match. The accompanying `.anm.meta` files reserve
   GUIDs already used by the ASIs. Check the imported GUIDs against those files.
   If the importer replaces a GUID, stop and send its resulting `.meta`; do not
   repoint to a production ANM or copy one over the output.
4. Open `Assets/MP133_AstraShellGraph/MP133_Astra.aw`. Inspect both ASIs:
   all five `AstraShell.Erc.*` rows must resolve. Inspect imported event tracks:
   only `ASTRA_Shell*`, no native magazine/bolt/fire-permission events.
   A header-only/empty ANM or a warning icon is a failed import, not a usable clip.
5. Preview with the paired character/weapon models. The weapon is attached to
   `RightHandProp` as in the original workspace. Use `MasterControl`, stance 0,
   inspection state 0, Firing false. Start from native Idle without an active
   native reload. **Diagnostic control is through graph parameters, not R.**

## Graph controls

| Parameter | Meaning/default |
| --- | --- |
| `ASTRA_ShellRequest` | false; set true to enter a shell session, false to re-arm the next session |
| `ASTRA_ShellRepeat` | false = one insertion; true = repeat at CheckContinue |
| `ASTRA_ShellEligible` | true; manual simulation of capacity/reserve eligibility, not an inventory query |
| `ASTRA_ShellStop` | false; hold true until exit to simulate a pending second-R stop |
| `ASTRA_FireStop` | false; hold true until exit to simulate a pending trigger stop |

One insertion: Repeat=false, Eligible=true, Stop/FireStop=false; Request=true.
Observe StartReload → GrabShell → InsertShell → CheckContinue → EndReload →
AstraWaitRelease, then Request=false → native Idle. Holding Request=true
must not start another session. Idle is confirmed by the graph state/pose, not
by the `ReturnReady` clip marker.

Repeat: Repeat=true before entry; observe at least three cycles. During Grab, set Stop=true and **keep it true**: exit without entering Insert.
During Insert, the current insertion finishes, then CheckContinue chooses EndReload. Repeat for FireStop and Eligible=false.
Requests are level parameters; a short pulse ending before CheckContinue is not
latched by this prototype. No script listens to physical R or fire input.

Full tube/no reserve: Eligible=false before entry must prevent entry. Setting
it false mid-cycle prevents the next cycle. Empty/partial gun uses the same
motion; no automatic pump/chamber operation is introduced.

The preview parameter UI is the supported initial trigger. This package does
**not** provide an in-game button or claim that weapon-only custom variables
automatically reach the injected character graph. Verify paired preview first;
live injected-variable propagation remains a separate owner test/integration gate.

## Diagnostics and limits

The script logs construction and ASTRA markers delivered to the **weapon**
callback. P/W suffixes identify authored tracks, not the callback's receiver.
Only `ASTRA_ShellInsertCommit_W` at InsertShell frame 11 is eligible for the
local `diagnostic_candidate_no_transfer` result. Repeated commit callbacks in
the same observed cycle are rejected. There are no subscriptions/global hooks,
ammo writes, inventory calls, RPC or T4 invocation.

`Stop` marks arrival in EndReload for any completion reason. `ReturnReady`
marks the last hold before return; neither proves actual input delivery or Idle.
`magTag` is a local entity-reference change counter, not a network entity ID.
Compare it and ammo/chamber snapshots only inside one component lifetime.

Clips reuse existing MP-133 insertion motion. Start/Check/End are short holds;
Grab/Insert are cuts of the original. These are **visual placeholders** until
the owner checks hand position, shell visibility, joint continuity and loop seam.
No separate shell prop is spawned. No claim of a finished new shell animation.

Do not use native R as the shell trigger: the unchanged native branch still
contains native whole-magazine reload behavior. No claims about multiplayer,
R/inspection integration, death/swap cancellation or exactly-once transactions.

## Return these results

- Import/compile errors, or confirmation that all ten clips resolve with events.
- Paired preview video: one cycle, three cycles, stop during Grab and Insert.
- Graph state at exit and behavior with Request held, then released/reasserted.
- If testing an equipped lab weapon: `component_constructed`, event log with
  marker counts/order, and whether both injected views follow the same phases.
- Magazine identity/count/chamber before and after (ordinary shots/racks excluded).

Rollback: close/disable **only this lab**. No production files require restoration.
Technical report: `reports/MP133_V3_ASTRA_ANIM_GRAPH_PROTOTYPE.md` in Weapon_ARMA_X.

V2 routing: entry is from native Idle only. A request held during another native state may enter when Idle returns. Release Request after End before testing native command 1. WaitRelease does not dispatch pump/inspection. The native-command guard is a graph predicate, not engine-side suppression; do not issue native reload commands as shell-session input. Explicit AstraShell/Erc GroupSelect resolves the five source rows. No open-action loading branch is included.
