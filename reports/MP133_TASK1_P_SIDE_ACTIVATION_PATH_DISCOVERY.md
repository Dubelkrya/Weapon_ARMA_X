# MP-133 Task #1 — Phase 1D: P-side activation path discovery

Status: **T4B_P_SIDE_ACTIVATION_PATH_DISCOVERY_COMPLETE**
Date: 2026-10-07
Task: Issue #34 comment `6042238284` (Phase 1D).
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `15b7c2b440854fdfa7e741419b54354a8be0aa7d`.
Mode: **SOURCE / STATIC / READ-ONLY.** No functional file changed; no graph/prefab/config/meta/GUID/G3B2/live/lab change; no install; no runtime.

Evidence classes: **RUNTIME** (owner logs), **LOCAL_SOURCE** (repo files), **INSTALLED_ENGINE_SDK** (`EnfusionScriptAPI`), **INSTALLED_GAME_SDK** (`ArmaReforgerScriptAPIPublic`), **PUBLIC_WORKING_MOD / HISTORICAL_EXCERPT**, **INFERENCE**, **UNRESOLVED**.

---

## 0. Context — why P matters now

Owner runtime (comment `6042146419`) proved:

```text
W_LOCAL_REQUEST_PATH = PROVEN_W_ONLY
P_PROPAGATION_FROM_W_LOCAL = DISPROVEN_RUNTIME
[ARMST-T4B-WPROP] phase=request ... phase=family-W ... phase=return-ready sawP=false sawW=true
```

W-local `ASTRA_ShellRequest` starts the **W** graph but does **not** start the **P** injection. Phase 1D answers how the current `P_Astra_*` injection could be started from custom R without the vanilla reload pipeline and without native reload commands.

---

## A. Exact current ownership chain (with unknowns marked)

Current T4B prefab wiring (`labs/.../Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et`, loaded from HEAD; live identical):

```text
GenericEntity : armst_Shotgun_mp_133.et
  WeaponComponent {CFBAA4B706BA66E8}
    ARMST_T4B_AstraV2_WeaponAnimationComponent {60B4EA76EB15F6E0}   // : WeaponAnimationComponent
      AnimGraph    {AF2491EDB3449EED} Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr
      AnimInstance {5F61684997C53048} Assets/MP133_AstraShellGraph_test/MP133_Astra2_weapon.asi   // W instance
      AnimInjection AnimationAttachmentInfo {532F3A9CB912F2BA}
        AnimGraph    {AF2491EDB3449EED} MP133_Astra2.agr
        AnimInstance {A43FF9780FC454A4} MP133_Astra2_player.asi                                   // P instance
        BindingName  "Weapon"
      BindWithInjection 1
```

Resulting object/component chain:

```text
SCR_ChimeraCharacter (game)                                        [game class]
  -> CharacterAnimationComponent / SCR_CharacterAnimationComponent [BaseAnimPhysComponent family]
       -> character ROOT graph (player_main.agr)
          -> ASTRA_ShellRequest: ABSENT   (owner evidence 5983965875) => root bind invalid
  -> <engine CharacterEntity>.GetAnimGraphComponent()  ->  CharacterAnimGraphComponent   [ENGINE class]
       -> attachment binding "Weapon"  (AnimInjection target)  ->  injected P graph instance
             (AGR MP133_Astra2.agr + MP133_Astra2_player.asi)
             -> ASTRA_ShellRequest  (per-instance variable)

W side: ARMST_T4B_AstraV2_WeaponAnimationComponent
  : WeaponAnimationComponent : BaseItemAnimationComponent : AnimationControllerComponent
    : BaseAnimationControllerComponent                                [ENGINE base]
       -> W graph instance (MP133_Astra2_weapon.asi)
          -> ASTRA_ShellRequest  (separate per-instance variable)
```

Unknowns (explicit):
- The **runtime owner** of the injected P instance is **UNRESOLVED** from installed docs. The strongest candidate is the engine `CharacterAnimGraphComponent` (it is a `BaseAnimationControllerComponent`, it declares `SetAttachment`/`RemoveAttachment`, and `CharacterEntity.GetAnimGraphComponent()` returns it). No inspected game callsite/pfeb proves it exists on the current character entity.
- Whether a game `ChimeraCharacter` can reach `CharacterEntity.GetAnimGraphComponent()` is **UNRESOLVED**: the engine hierarchy shows `Managed → IEntity → GenericEntity → PawnEntity → CharacterEntity`, while the game class is `BaseGameEntity → GameEntity → ChimeraCharacter → SCR_ChimeraCharacter`; the two doc packages do not state the cross-package link. `CharacterAnimGraphComponent` does **not** exist in the game API package (verified: file absent; `functions_g.html` has no `GetAnimGraphComponent`).

---

## B. Source-backed API inventory

### B1. `BaseAnimationControllerComponent` (engine) — the controller API
Source: `EnfusionScriptAPI/html/interfaceBaseAnimationControllerComponent.html` (exact signatures, verbatim):

```
proto external int  BindCommand(string commandName)          // binds anim command -> ID
proto external void CallCommand(int cmdID, int intParam, float floatParam)
proto external void CallCommand4I(int cmdID, int, int, int, int, float)
proto external int  BindBoolVariable(string varName)
proto external void SetBoolVariable(int varId, bool value)
proto external bool GetBoolVariable(int varId)
proto external int  BindEvent(string eventName)
proto external int  BindTag(string tagName)
proto external int  BindAttachment(string attachmentName)
proto external int  BindAttCommand(int attachmentName, string commandName)
proto external void CallAttCommand(int attachmentName, int cmdID, int intParam, float floatParam)
proto external void CallAttCommand4I(int attachmentName, int cmdID, int, int, int, int, float)
proto external int  BindAttBoolVariable(int attachmentName, string varName)
proto external void SetAttBoolVariable(int attachmentName, int varId, float value)   // NOTE: float, not bool
proto external bool GetAttBoolVariable(int attachmentName, int varId)
proto external void RebindEntity(IEntity owner)
```

Inherited by: `AnimationControllerComponent` → `BaseItemAnimationComponent` → `WeaponAnimationComponent` (the **W** component — confirmed at runtime: WPROP used `BindBoolVariable`/`SetBoolVariable`/`GetBoolVariable` successfully), and by engine `CharacterAnimGraphComponent` (candidate **P** controller).

### B2. `CharacterAnimGraphComponent` (engine) — candidate P owner
Source: `EnfusionScriptAPI/html/interfaceCharacterAnimGraphComponent.html` / `-members.html`. Inherits `BaseAnimationControllerComponent`, so it has **all** of B1, plus:
```
proto external bool SetAttachment(string bindingName, ResourceName resNameAttachedGraph,
                                  ResourceName resNameAttachedInst, int attachedNodeIndex, bool attachAsManaged)
proto external void RemoveAttachment(string bindingName)
proto external int  BindIKTarget(string)/BindPrediction(string)
proto external void SetAnimSetInstance(ResourceName, float)
... (root motion, IK, post-graph) ...
```
Accessor: `EnfusionScriptAPI/html/interfaceCharacterEntity.html`:
```
proto external CharacterAnimGraphComponent CharacterEntity.GetAnimGraphComponent()
```

### B3. `BaseAnimPhysComponent` family (the game character animation) — the *other* API
Source: `ArmaReforgerScriptAPIPublic/html/interfaceBaseAnimPhysComponent-members.html`, `interfaceCharacterAnimationComponent-members.html`, `interfaceSCR__CharacterAnimationComponent-members.html`:
```
BindVariableBool/Int/Float(string) -> TAnimGraphVariable
SetVariableBool/Int/Float(TAnimGraphVariable, ...)
BindCommand(string) -> TAnimGraphCommand ; CallCommand(TAnimGraphCommand,int,float) ; CallCommand4I(...)
SetCurrentCommand(AnimPhysCommandScripted) ; BindEvent(string) ; BindTag(string)
CharacterAnimationComponent.SetSharedVariableBool/Float/Int(TAnimGraphVariable, ..., bool varHasOtherUsers)
```
`ChimeraCharacter.GetAnimationComponent()` → `CharacterAnimationComponent` (game). It exposes **no** `BindAttachment`/`BindAttBoolVariable`/`CallAttCommand` (verified: absent from the member lists). `ChimeraCharacter` itself exposes **no** `GetAnimGraphComponent`.

### B4. `SyncWithCharacter` (weapon side)
`WeaponAnimationComponent.SyncWithCharacter(ChimeraCharacter, bool, string)` "subscribes to its animation variable changes and animation command calls" — i.e. receives character→weapon changes via `OnCharacterBoolVariable`/`OnCharacterCommand`. It is a **character→weapon** subscription; nothing in the inspected signature provides **weapon→character (P)** propagation.

---

## C. Chungus / BC-Ithaca re-read — ACTIVATION vs SYNC

Local raw sources available: the BC-Ithaca graph set only (`Armst_Work/bc_ithaca_m37.agr|.agf|.ast|_weapon.asi|_player.asi`). The BC component scripts are **not** present locally; component behaviour is taken from historical excerpts (`MP133_G4A_RELOAD_SWAP_ROUTE_AUDIT.md` §3; `MP133_V3_T0_T1_T2_DESIGN.md`) → HISTORICAL_EXCERPT.

BC-Ithaca AGR (`bc_ithaca_m37.agr`) declares per-instance variables and commands:
```
AnimSrcGCTVarBool PumpShotgunStopReloading
AnimSrcGCTVarBool PumpShotgunCloseActionFlag
AnimSrcGCTCmd CMD_Weapon_Reload
AnimSrcGCTCmd CMD_Weapon_Action_Interrupt
AnimSrcGCTCmd CMD_BC_Weapon_Rack_Bolt          // custom command
```
BC-Ithaca AGF (`bc_ithaca_m37.agf`) has `StartReloadTimer` (a graph event) and `PumpShotgunAdjustAmmoCount`.

ACTIVATION mechanism (per excerpts): the per-shell workflow is entered through the **vanilla reload pipeline**; only **after** the running reload emits `StartReloadTimer` does `BC_PumpShotgunComponent.InitReloadSequence()` call `InitPlayerAnimVariables()`. `TryRackBolt` runs off the **trigger-pull edge** (`WeaponIsPullingTrigger`), not R, and calls `weaponAnim.CallCommand(...)`, `charAnim.CallCommand(...)` **and** `controller.ReloadWeapon()`.

SYNC-AFTER-ACTIVATION (not a starter): `InitPlayerAnimVariables()` binding/writing character-side variables (`CharacterAnimationComponent`) and weapon-side variables (`WeaponAnimationComponent`) **once the reload context already exists**.

MANDATORY DISTINCTION:
```
ACTIVATION                       = vanilla reload entering the character reload context (native); NOT custom-R reachable
SYNC AFTER ACTIVATION            = InitPlayerAnimVariables() variable writes; safe/portable only downstream
CUSTOM COMMAND (CMD_BC_..._Rack) = CallCommand emitted to BOTH components; its P/W reach is not proven to start P on its own
```
Forbidden backend (do not reuse): `ReloadWeapon()`, direct magazine count edits, dummy +1/fixup, magazine spawn/attach/detach.

⇒ Chungus does **not** provide a custom pre-reload P activation; re-confirms D5. Its usable pattern is a **custom command declared in the AGR and emitted via `CallCommand`**, but BC still relies on native reload for actual activation.

---

## D. Custom command/event route reaching both P and W

Source-backed pieces:
- A custom command can be declared in the current AGR ControlTemplate (e.g. a new `AnimSrcGCTCmd`). **That is a graph/AGR edit** (forbidden in this phase).
- Emission APIs exist on both controller families: `BaseAnimationControllerComponent.BindCommand`/`CallCommand` (W component, and `CharacterAnimGraphComponent`) and `BaseAnimPhysComponent.BindCommand`/`CallCommand` (character `CharacterAnimationComponent`).
- Attachment-scoped emission exists: `BindAttCommand(attachmentName, commandName)` + `CallAttCommand(attachmentName, cmdID, intParam, floatParam)`.
- `BindEvent(string)` exists on both; no `CallEvent` is documented on either.

Assessment:
- A **single** emission reaching **both** the W instance and the P instance is **not proven**. BC explicitly calls `weaponAnim.CallCommand(...)` **and** `charAnim.CallCommand(...)` — evidence that they are two sinks, not one fan-out.
- `CallAttCommand` on the character's `CharacterAnimGraphComponent` with the `"Weapon"` attachment is the closest to a "reach the injection" command route, but depends on the same unresolved attachment ownership as E.
- `BindEvent` has no documented caller (`CallEvent` absent) → not viable as an emitter.

STATUS: **PLAUSIBLE_SOURCE_BACKED** (APIs exist), but requires a graph edit to declare a custom command and does not prove single-emission dual delivery.

---

## E. Injection-aware attachment-variable route

Proposed (source-backed API, owner UNRESOLVED):
```text
characterEntity (CharacterEntity/ChimeraCharacter?)
  -> GetAnimGraphComponent() : CharacterAnimGraphComponent        [accessor UNRESOLVED from game script]
  int att   = animGraph.BindAttachment("Weapon");                  // the injected P graph attachment
  int varId = animGraph.BindAttBoolVariable(att, "ASTRA_ShellRequest");
  animGraph.SetAttBoolVariable(att, varId, 1.0);                   // float value
  bool rb   = animGraph.GetAttBoolVariable(att, varId);
  // or command variant:
  int cmd   = animGraph.BindAttCommand(att, "<custom command>");
  animGraph.CallAttCommand(att, cmd, intParam, 0.0);
```
Why it may work: the P injection is configured with `BindingName "Weapon"`; `CharacterAnimGraphComponent` is a `BaseAnimationControllerComponent` and thus has attachment-scoped bind/set/call; this targets the injected graph **instance** rather than the character root.
Why it is not proven: (1) game-script accessibility of `CharacterEntity.GetAnimGraphComponent()`/`CharacterAnimGraphComponent` is unverified; (2) no inspected callsite/example binds the `"Weapon"` attachment to a variable declared in the injected weapon AGR; (3) lifetime/rebind on equip/unequip is undocumented in the inspected sources.

STATUS: **PLAUSIBLE_SOURCE_BACKED** (best candidate), REQUIRES_GRAPH_CHANGE = NO (if it works), RISK = engine-only API + ownership assumptions.

---

## F. Minimal follower/sync architecture (only if A–E fail; analysis only)

If neither D nor E can start P: make the P instance **follow** a source-backed signal without native reload:
- Add a small **P-side follower state** to the Astra graph driven by a variable that both instances can observe (e.g. a shared/graph-control variable set on the character side), or
- Have the W graph's commit/phase markers (`*_W`) be mirrored into a character-visible signal and let the P graph react.

Constraints: no native reload; no cmd2..6; no gameplay writes; W commit remains the sole future gameplay authority; P visual only; protected rack branch unchanged. This is a **graph edit** and is out of scope for Phase 1D.

STATUS: **PLAUSIBLE_SOURCE_BACKED** (design), REQUIRES_GRAPH_CHANGE = YES.

---

## Critical static questions

1. **Are W and P `ASTRA_ShellRequest` separate graph-instance variables?** YES — same AGR, two instances (`_weapon.asi` W, `_player.asi` P injected); the WPROP runtime proved the W write started only W (`sawP=false`).
2. **Why did W-local setter fail to start P?** W-local `SetBoolVariable` writes only the W instance's variable; there is no automatic W→P propagation in the inspected APIs (the only link is `SyncWithCharacter`, which is character→weapon).
3. **Can character-root `CharacterAnimationComponent` see `ASTRA_ShellRequest` before P is active?** NO / UNRESOLVED — the character root graph (`player_main.agr`) does not declare it (owner evidence 5983965875); a root bind would be invalid.
4. **Is there an exact API for addressing the injection itself?** `CharacterAnimGraphComponent.BindAttachment`/`BindAttBoolVariable`/`SetAttBoolVariable`/`BindAttCommand`/`CallAttCommand` (+ `SetAttachment`). Accessor/ownership UNRESOLVED.
5. **Is there a non-reload custom command/event that reaches both graphs?** Not proven; custom commands exist but BC emits to both sinks separately; `BindEvent` has no caller.
6. **Does current P ASI expose a resolvable binding/attachment name?** YES — `BindingName "Weapon"` (prefab `AnimInjection`). Resolving it programmatically depends on the owner (#4).
7. **Does the current prefab give a direct handle to the P injection?** NO — the prefab only declares `AnimInjection`; no script handle/reference is created.
8. **Is a graph edit strictly necessary?** UNRESOLVED — no if E works; yes for the D command (declare command) and F follower.
9. **Single smallest safe next experiment?** Bounded animation-only probe of E (see below).

---

## Required candidate ranking

```
1. source-backed custom graph command/event delivered to both W + P
   STATUS = PLAUSIBLE_SOURCE_BACKED
   STATIC_EVIDENCE = BindCommand/CallCommand on BaseAnimationControllerComponent + BaseAnimPhysComponent; BindAttCommand/CallAttCommand; AGR cmd namespace; BC precedent (two calls)
   REQUIRES_GRAPH_CHANGE = YES (declare a custom command)
   REQUIRES_SCRIPT_CHANGE = YES
   REQUIRES_NATIVE_RELOAD = NO
   RISK = no proof a single emission reaches both; needs graph edit
   NEXT_MINIMAL_PROBE = after owner approval: emit a custom command on the character controller and observe W and P marker families

2. exact injection-aware P-variable write
   STATUS = PLAUSIBLE_SOURCE_BACKED  (best single candidate)
   STATIC_EVIDENCE = CharacterAnimGraphComponent : BaseAnimationControllerComponent; BindingName "Weapon"; BindAttBoolVariable/SetAttBoolVariable/GetAttBoolVariable signatures
   REQUIRES_GRAPH_CHANGE = NO (if it works)
   REQUIRES_SCRIPT_CHANGE = YES
   REQUIRES_NATIVE_RELOAD = NO
   RISK = engine-only accessor/ownership of the "Weapon" attachment unproven; lifetime/rebind undocumented
   NEXT_MINIMAL_PROBE = bounded animation-only probe E (below)

3. minimal P follower/sync graph design
   STATUS = PLAUSIBLE_SOURCE_BACKED
   STATIC_EVIDENCE = current AGR/AGF structure; instance separation proven at runtime
   REQUIRES_GRAPH_CHANGE = YES
   REQUIRES_SCRIPT_CHANGE = possibly
   REQUIRES_NATIVE_RELOAD = NO
   RISK = graph redesign; must keep W authority and rack frozen
   NEXT_MINIMAL_PROBE = design only, not this phase
```

---

## Rejected routes

- **Character-root variable set** (`CharacterAnimationComponent.BindVariableBool("ASTRA_ShellRequest")`): root graph lacks the variable → invalid bind. REJECTED.
- **`ReloadWeapon()` / native reload to activate P**: forbidden by task; and it re-enters the whole-mag pipeline. REJECTED.
- **`SetReloadWeapon` from the shell branch**: forbidden; and it is a native reload-command lever. REJECTED.
- **Manual ammo/chamber/mag writes, dummy +1, magazine spawn/attach**: forbidden. REJECTED.
- **`SyncWithCharacter` as a P starter**: signature only subscribes to character→weapon changes; it is not a weapon→character setter. REJECTED.

---

## Smallest safe next experiment (design only — NOT in this phase)

A bounded, animation-only probe of candidate **E**, fail-closed, no gameplay writes:
1. On the same custom-R non-rack branch, obtain the character's `CharacterAnimGraphComponent` (try `CharacterEntity.GetAnimGraphComponent()`, else `FindComponent(CharacterAnimGraphComponent)`); reject if unavailable.
2. `att = BindAttachment("Weapon")`; reject if invalid.
3. `v = BindAttBoolVariable(att, "ASTRA_ShellRequest")`; write `1.0`, read back; log `[ARMST-T4B-PACT]`.
4. Observe P marker family (`*_P`) on the existing receiver; reset deterministically on `ASTRA_Shell_ReturnReady_W` (or the P ReturnReady).
5. No ammo/chamber/mag/native reload/cmd1..6; W branch untouched.

This falsifiably separates "P addressable via injection attachment" from "P requires a graph follower".

---

## Final classification

```
P_TRIGGER_PATH_MULTIPLE_CANDIDATES
```

Two source-backed, non-native, non-graph-follower mechanisms remain viable (injection-aware attachment variable/command write; custom command emission to the character/attachment controller), with a graph-follower as the third. None is source-proven end-to-end; a bounded probe (above) is required to choose.

---

## Required final fields

```
FINAL_STATUS = P_TRIGGER_PATH_MULTIPLE_CANDIDATES
HEAD = 15b7c2b440854fdfa7e741419b54354a8be0aa7d
REPORT = reports/MP133_TASK1_P_SIDE_ACTIVATION_PATH_DISCOVERY.md
PLAN_UPDATED = YES (Phase 1D record + continuation)
TRACKED_FILES_CHANGED = 2 (this report + plan)
FUNCTIONAL_FILES_CHANGED = NO
GRAPH_CHANGED = NO
PREFAB_CHANGED = NO
CONFIG_CHANGED = NO
META_CHANGED = NO
GUID_CHANGED = NO
G3B2_CHANGED = NO
LIVE_CHANGED = NO
WORKBENCH_LAUNCHED = NO
REFORGER_LAUNCHED = NO
RUNTIME_TEST = NO

CURRENT_P_OWNER = UNRESOLVED; strongest candidate = engine CharacterAnimGraphComponent attachment "Weapon" hosting the injected P graph (game-side accessor unproven)
CURRENT_P_ACTIVATION_MECHANISM = currently only the vanilla reload pipeline enters the character reload context and thus runs P; no script P activation route is proven
WHY_WPROP_DID_NOT_REACH_P = W and P are separate graph instances with independent per-instance variables; W-local setter writes only W; no automatic W->P propagation
BEST_CANDIDATE = injection-aware attachment variable write: CharacterAnimGraphComponent.BindAttachment("Weapon") + BindAttBoolVariable(att,"ASTRA_ShellRequest") + SetAttBoolVariable(att,varId,1.0)
BEST_CANDIDATE_EVIDENCE = engine BaseAnimationControllerComponent attachment APIs; prefab AnimInjection BindingName "Weapon"; WPROP proving instance separation
GRAPH_CHANGE_REQUIRED = UNRESOLVED (NO if the attachment route works; YES for a follower or a custom-command declaration)
NEXT_MINIMAL_PROBE = bounded animation-only PACT probe: obtain CharacterAnimGraphComponent, bind attachment "Weapon" + variable ASTRA_ShellRequest, write/readback, observe P marker family, deterministic reset - no gameplay writes
```

## Unchanged statement

No functional file was changed by Phase 1D. `labs/`/live scripts, AGR/AGF/AST/ASI/TXA/ANM, prefab, config/input/keyBindingMenu, `.meta`/GUID, G3B2, production Weapons/Core/worlds are byte-identical to HEAD. Only this report and the plan were committed.

STOP — no candidate staged/installed; owner review first.
