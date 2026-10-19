# MP133_MINIMAL_GRAPH_DIAGNOSTIC_DESIGN

2026-10-08. Authorization: owner `go` for DESIGN-ONLY. **Result: SOURCE_BLOCKED**.

Starting HEAD: `8d3e896b96d3b14a269d678e76d946eb5d40c708`, branch `t4b/installed-mag-probe`. Only this report is produced; no functional candidate. Owner-untracked CORE_ARMST_READONLY_AUDIT.md preserved. No command, install, compile, UI or runtime execution. Rack FROZEN; G3B2 HOLD.

## Current evidence / corrections

Owner inspected this installed editor: Load / Attach / Detach, no Fetch. Character player_main evaluation visible; W not independently identified; Unknown 1 unclassified. Do not repeat Fetch instructions or presume two live subscriptions. Previously identified MP133_Astra2_player.asi injection remains historical evidence, not health at a future pulse frame.

Current live MP133_Astra2 AGR/AGF is shared between W and P, with distinct weapon/player ASIs. CMD_ASTRA_TransportProbe declared but no consumer. P/W role cannot be inferred from AGR filename or a generic callback. Current MasterControl (AGF 412) blends IdleReloadSTM and SightPose, with Always eval both. Existing states, transitions, clips and rack route must remain byte-identical in a future diagnostic delta.

## Source-supported building blocks

| Capability | Source inspected | Limitation |
|---|---|---|
| Event wrapper with Child, conditional generic event, InitOnly/MainPathOnly/Once | Official [Animation Editor Nodes](https://community.bistudio.com/wiki/Arma_Reforger:Animation_Editor:_Nodes); live MP133_Astra2.agf 697–708 serialized AnimSrcNodeEvent / AnimSrcEventGeneric | Existing example is Sound: never reuse its event identity or sound payload |
| Separate W/P entry node | Official [Weapon Components](https://community.bistudio.com/wiki/Arma_Reforger:Weapon_Components): Start Node on item component and AnimationAttachmentInfo; local Core prefabs serialize StartNode | Runtime preservation of injected command mapping after changed entry is untested |
| IsCommand / GetCommandI | Current live AGF 259/301 | Syntax precedent, not custom transport proof; use only custom diagnostic name |
| Boolean constant expression | Core Anims/Player/ak74.agf contains Condition "true" | Event heartbeat cadence/order still requires validation |
| W callback | Installed ArmaReforgerScriptAPIPublic/html/interfaceBaseItemAnimationComponent.html; live AstraV2 override at 208 | Callback identifies receiver, not automatically graph origin; current super processing must be considered |
| Character event subscription | Installed interfaceSCR__CharacterControllerComponent.html GetOnAnimationEvent; repo labs ARMST_T4B_CharacterMagEventObserver.c 34/39 | Available ScriptInvoker; existing listener filters Weapon_ and will NOT observe new diagnostic names |
| Callback frame stamp | Installed EnfusionScriptAPI/html/interfaceBaseWorld-members.html GetFrameNumber, line 128 | World frame at callback is not proven animation evaluation-frame ID; equal stamps alone do not establish capture completeness |
| Named emission | Installed BaseAnimationController BindCommand/CallCommand | Controller-local handle; source emission only, never hardcode 3 |

VarSet is rejected for this design: its values are subtree-scoped/restored, so it is not a proven externally readable persistent receipt latch. Shared diagnostic variables could also contaminate attribution through synchronization. No diagnostic animation clips, changes to ASI/AST, native reload events, pose blend branches or state-machine transitions are proposed.

## Exact proposed topology (documentation, not an implemented graph)

Select two explicitly configured entry roots in the SAME graph, each wrapping the unchanged MasterControl exactly once:

```text
W component StartNode = AstraDiagW
  AnimSrcNodeEvent AstraDiagW
    Child = MasterControl [unchanged existing subtree]
    Events = W_HEALTH, W_RECEIPT

P AnimInjection StartNode = AstraDiagP
  AnimSrcNodeEvent AstraDiagP
    Child = MasterControl [same unchanged subtree, separate P runtime evaluation]
    Events = P_HEALTH, P_RECEIPT
```

Do not change DefaultRunNode or player_main, binding name Weapon, AGR/ASI GUIDs, command flags, BindWithInjection, command binding lists, input or rack dispatcher. Future prefab delta would set ONLY the two StartNode fields. Do not copy the old labs prefab over live: current owner bytes are authoritative. This is graph-entry instrumentation, NOT a new transport architecture.

Each wrapper contains two distinct AnimSrcEventGeneric definitions. Proposed names below are new diagnostic identifiers, NOT claims that the engine already registers them:

| Proposed event Name | Condition | InitOnly | MainPathOnly | Once | Meaning |
|---|---|---:|---:|---:|---|
| ARMST_Diag_W_Health | true | 0 | 0 | 0 | W observer node evaluated and event made observable |
| ARMST_Diag_W_Receipt | IsCommand(CMD_ASTRA_TransportProbe) && GetCommandI(CMD_ASTRA_TransportProbe) == Q | 0 | 0 | 1 | W predicate evaluated true for reviewed payload Q |
| ARMST_Diag_P_Health | true | 0 | 0 | 0 | P observer node evaluated and event made observable |
| ARMST_Diag_P_Receipt | IsCommand(CMD_ASTRA_TransportProbe) && GetCommandI(CMD_ASTRA_TransportProbe) == Q | 0 | 0 | 1 | P predicate evaluated true for reviewed payload Q |

Q denotes one owner-reviewed integer literal substituted in BOTH predicates and a future single W call. It is not a new variable or dynamic UserInt expression. UserString would be a fixed diagnostic run label; UserInt a fixed payload literal Q for receipt, not an invented expression field. It proves matching the predicate, not independent payload transport instrumentation. No GUIDs/generated instance IDs are invented in this report; serialization identifiers belong to separately authorized staging.

HEALTH is intentionally independent of command presence. Once=0 avoids an init-only positive control falsely validating a later frame; receipt Once=1 suppresses a sustained true condition, not duplicate delivery globally. Blending/reinitialization could still duplicate events: collector must record and deduplicate evidence, never produce gameplay actions. No pulse is proposed from health events.

## Observation / attribution design

Future collector subscribes on the actual current owning character's GetOnAnimationEvent and observes the actual equipped W animation component's OnAnimationEvent. Prefer a narrowly scoped subscriber, not another global reload/controller override. Preserve other handlers and ordinary super calls; no ammo writers or command forwarding. Where to own subscription/lifecycle without broader changes is a candidate-review gap, not permission to add a component now.

Each row records receiver identity (character or equipped weapon), source-specific event name, callback world frame, run label, payload, and whether the expected role-root configuration is verified. Origin is assigned by UNIQUE emitting node/entry path, not by callback alone. P events forwarded into W must retain their P name and count as one P-origin observation, NOT a second W receipt. W events on the character invoker likewise remain W-origin. Reject unexpected role-root traversal, stale owner/weapon association, duplicate indistinguishable producers, or an event name found in any other resource.

Four distinct names are mandatory. Two copies of one shared marker, two listeners seeing the same marker, or suffix naming without role-exclusive entry roots do not prove independent consumers.

P health and P receipt originate from the SAME P Event node. This improves validity compared with an unrelated MasterControl screenshot, but callback world-frame equality does not prove they correspond to the same engine evaluation; ordering/buffering/drop semantics remain unestablished. Thus a P heartbeat before/after a pulse is insufficient for a decisive negative. The collector must establish a complete evaluation window and positive event retention/calibration before classifying P receipt NO. Without that, INCONCLUSIVE.

Expected future evidence labels (not implemented log/API):

```text
EMIT: actual W controller, named binding, Q, exactly one call
W_CONSUMER: ARMST_Diag_W_Receipt from verified W entry node
P_CONSUMER: ARMST_Diag_P_Receipt from verified P entry node
P_HEALTH: ARMST_Diag_P_Health on complete relevant P evaluation(s)
```

An empty P receipt log is never PASS/NO unless P health, capture calibration and coverage are independently valid. No additional command is emitted to silently calibrate this one-pulse test. A separately reviewed observer-only calibration may be necessary.

## Pose / gameplay risk analysis

Wrappers add no source pose, blend weight, state or transition and preserve the existing Child, but structural similarity does NOT prove evaluation equivalence. Entry changes can affect initialization, inherited context, event timing, caching, sleep/LOD and attachment command mapping. These require a later owner regression gate; no zero-impact runtime claim now.

Generic events signal game/engine code. New Name registration and unknown-event handling are not established for this installed build. Current W OnAnimationEvent calls AstraEnsureInstanceInit and super before filtering; it rejects names outside Weapon_/ASTRA_Shell afterwards, but that does not prove the preceding native processing is harmless. Never use Sound, Weapon_*, ASTRA_Shell* or native event identifiers. Do not suppress super as an unreviewed workaround. Character handlers outside the inspected listener/native code may also act on events.

Per-evaluation heartbeats can increase event traffic and log volume. A collector may keep bounded diagnostic state, but cannot drop receipt/health while claiming complete observation. Do not use polling/retries, timers to emit commands, or log caps that erase evidence. Events intended as diagnostics still need a proven no-gameplay dispatch contract.

## Blockers / acceptance verdict

1. Role-exclusive StartNode configuration is source-supported, but runtime traversal and command mapping preservation are unproven. No current graph role discriminator is substituted for this requirement.
2. Unknown custom generic event registration/dispatch and all native/default handlers prevent proving zero effect on gameplay from inspected source alone.
3. Character callback API exists, but delivery of these graph-generated injected-P events is not proven. Historical P clip markers are a precedent, not proof of this wrapper path.
4. Callback world-frame stamps do not establish animation-frame identity, complete health/receipt coverage or drop-free capture. No source-backed negative-result gate yet.

Result therefore **SOURCE_BLOCKED**, not DESIGN_READY_FOR_REVIEW. The exact topology and consumer conditions are now specified; the missing piece is their safe, independently attributable observation contract, not another graph sketch. No claim that W-to-P transport is impossible.

Future file set if gaps close and separate staging GO is granted: current laboratory MP133_Astra2.agf (two wrappers), current AstraRebuild test prefab (two entry strings), minimal scoped diagnostic collector/producer script(s) after exact lifecycle review. No AGR declaration change needed for the existing command. No ASI/AST/clip/input/Core/production edit. This list is NOT an implementation authorization.

## Guards / stopping point

Protected PRE/POST inventories match; extensions `.et,.conf,.meta,.c,.layer,.agr,.agf,.asi,.ast,.gproj,.anm,.txa`, sorted absolutePath|fileSHA256 rows joined by LF, UTF-8 aggregate SHA-256:

| Root | Count | PRE = POST |
|---|---:|---|
| ARMSTMP133T4B_InstalledMagProbe | 105 | D540BE18C0EA0A4754F34D27C260F1BAF9971DC9C1B76674D095C26BC3B48B76 |
| ARMST-PLATFORM---Core | 5521 | 2EDF4D1DCA02F0C662AE1CA567D8B9655C374BC817883B7625A7AF02D8860B4B |
| ARMST-PLATFORM---Weapons | 1584 | A7C611FE0417F5A5E1DA6E4209F01E3CF846295E9ADA57999713FF1B4CC2AECF |
| Armst_Work | 163 | 62AD288141B18B222E058011B29672E23996D7B651C8C4C79E7535BD24123E29 |

No unrelated test/dependency rerun or repair; no repository-green claim. Only documentation created. No candidate, installation, compile, runtime or emission. Rollback: none installed; future rollback must use separately captured CURRENT owner bytes, never old_pa or historical restoration. STOP for owner review of source gaps; no functional GO inferred.
