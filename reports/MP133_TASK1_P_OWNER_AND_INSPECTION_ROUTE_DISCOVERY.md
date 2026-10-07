# MP-133 Task #1 — P-owner + inspection route discovery (Phase 1F)

Status: **T4B_P_OWNER_INSPECTION_ROUTE_DISCOVERY_COMPLETE**
Date: 2026-10-07
Task: Issue #34 comment `6043917747` (Phase 1F, source/static only).
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `3537ccb2e5419f70cfdfd8224f764ec7d4f13a5f`.
Mode: **SOURCE / STATIC ONLY.** No functional file changed; no input/graph/prefab/config/meta/GUID/G3B2/live change; no install; no runtime.

Prior runtime context (owner): `PACT_RUNTIME = COMPLETE`, `PACT_BIND_FAIL = YES`, `PACT_BIND_FAIL_SUBREASON = CHARACTER_ANIM_GRAPH_OWNER_UNAVAILABLE`; W-local request works, `P_FAMILY = NO`. Owner reports a separate regression: weapon inspection ("Inspected") stopped working a few operations ago.

Evidence classes: **LOCAL_SOURCE**, **INSTALLED_ENGINE_SDK** (`EnfusionScriptAPI`), **INSTALLED_GAME_SDK** (`ArmaReforgerScriptAPIPublic`), **RUNTIME** (owner), **INFERENCE**, **UNRESOLVED**.

---

## A. Inspection input → graph route

### A1. Script/API receiver (SOURCE)
`ArmaReforgerScriptAPIPublic/html/interfaceCharacterControllerComponent.html`:
```
proto external void SetInspect(IEntity targetItem)
proto external void SetInspectState(int state)
proto external int  GetInspectState()      // "Returns desired state, see SetInspectState"
proto external IEntity GetInspect() / GetInspectCurrentWeapon() / GetInspectEntity()
proto external bool CanInspect(IEntity targetItem)
void OnInspectionModeChanged(bool newState)
```
`CharacterCommandHandlerComponent` exposes `IsWeaponInspectionAllowed()`, `IsItemInspectionAllowed()`, `HandleWeapons/Default`, but **no** `HandleWeaponInspection` (inspection is driven through the weapon/handling path, not a dedicated handler override).

### A2. Action name (SOURCE, partial)
The vanilla inspection action name is **`CharacterInspect`** — referenced as an `ActionRef` in Core `ARMST-PLATFORM---Core/Configs/System/chimeraInputCommon.conf` (`ARMST_Pda3DFocusContext` ActionRefs, line 265), alongside other vanilla actions. Core does not declare it, so it is a vanilla action.

### A3. Binding / context (UNRESOLVED locally)
`CharacterInspect`'s keyboard/gamepad binding and its containing ActionContext live in the **packed** vanilla `chimeraInputCommon.conf` (`C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\addons\data\*.pak`). Not extractable here; not present in any local/public config (`grep.app "Action CharacterInspect"` = 0 hits; the user `ReforgerUserInput.conf` is absent; `customInputConfigs` empty). **The exact key is UNRESOLVED from local source.**

### A4. Downstream animation (SOURCE)
Current lab AGR/AST/AGF (`labs/.../Assets/MP133_AstraShellGraph_test/`):
- AGR declares `AnimSrcGCTVarInt WeaponInspectionState` and `AnimSrcGCTCmd CMD_Weapon_Inspection` (plus `CMD_Weapon_Reload`, `CMD_Weapon_Action_Interrupt`).
- AGF reachable inspection states: `Idle → Buffer2 → WeaponInspection` on `WeaponInspectionState != 0 && WeaponInspectionState != -2`; `WeaponInspection → Buffer1` on `RemainingTimeLess(0.5) || WeaponInspectionState == -3`; `WeaponInspection → Buffer3` on `IsCommand(CMD_Weapon_Reload) && GetCommandI == 1`; `WeaponInspectionSTM` with left/right in/loop/out; AST group `Inspection` = Left/Right InspectionIn/Loop/Out.
- Task-provided static comparison: OLD `MP133_Astra` vs current `MP133_Astra2` inspection AGF lines identical 107/107; player ASI inspection mappings identical 48/48. My local read confirms the inspection states/transitions are present.

⇒ The **graph inspection path is source-intact**; the regression is not a deleted graph.

## B. Custom R overlay interference

Current **live** T4B overlay (`ARMSTMP133T4B_InstalledMagProbe/Configs/System/chimeraInputCommon.conf`):
```
ActionContext ARMST_MP133_ReloadContext {
 Priority 20000
 Flags 0xa 0
 ActionRefs { "ARMST_MP133_Reload" }
}
Action ARMST_MP133_Reload { InputSource InputSourceValue { Input "keyboard:KC_R" } }
```
(Labs still `Flags 0x6 0`; the `0xa` is the owner-accepted live change. Origin commits: `c069038125…` "install Phase B custom-R input (3 files)" introduced the overlay with `Flags 0x6 0`; `1c22228af1…` changed only the `ActionRefs +{` → `{` operator.)

Static semantics (OFFICIAL `Page_Input.html`): a context processes only if no active context with higher priority exists; `Overlay` lets lower-priority contexts update; the `0xa` bit (accepted interpretation) adds colliding-input exclusivity.

Assessment:
- The overlay is active continuously while the T4B MP-133 is current, at `Priority 20000` (above every observed context), and its only action claims `keyboard:KC_R`.
- Therefore it can only affect actions bound to **KC_R**. If vanilla `CharacterInspect` is bound to `KC_R` (its binding is UNRESOLVED, see A3), the active `0xa` context claims R and suppresses inspection for the T4B weapon — matching "regression a few operations ago" and "non-T4B weapons behave normally".
- It cannot affect inspection if inspection is bound to any other key; in that case the overlay is irrelevant and the regression must be P-side/runtime.

## C. P-owner candidates (Investigation D)

| TYPE | OWNER | ACCESSOR | SOURCE LOCATION | WHEN VALID | CAN ADDRESS P ATTACHMENT | CAN EMIT COMMAND TO P |
|---|---|---|---|---|---|---|
| `CharacterAnimGraphComponent` | character entity (engine) | `CharacterEntity.GetAnimGraphComponent()` / `FindComponent` | `EnfusionScriptAPI/interfaceCharacterEntity.html`, `.../interfaceCharacterAnimGraphComponent.html` | while character exists | UNKNOWN | UNKNOWN |
| `AnimationControllerComponent` (engine) | character entity (engine) | `controlled.FindComponent(AnimationControllerComponent)` → `.Cast` | `EnfusionScriptAPI/interfaceAnimationControllerComponent.html`; **Core precedent** `ARMST_MUTANTS_ANIM_COMPONENT.c:31`, `ARMST_MUTANT_MOVEMENT_COMPONENT.c:143` | while character exists | UNKNOWN | UNKNOWN |
| `CharacterAnimationComponent` / `SCR_CharacterAnimationComponent` (game) | character | `ChimeraCharacter.GetAnimationComponent()` / `CharacterControllerComponent.GetAnimationComponent()` | `ArmaReforgerScriptAPIPublic/interfaceCharacterAnimationComponent.html` | while character exists | **NO** (no `BindAttachment`/`BindAttBoolVariable`) | only character-root command/variable (no attachment) |
| `ARMST_T4B_AstraV2_WeaponAnimationComponent` (W) | weapon | prefab instance `{60B4EA76EB15F6E0}` | `labs/.../ARMST_T4B_AstraV2_WeaponAnimationComponent.c` | equipped | UNKNOWN (W instance proven; character "Weapon" attachment ownership unproven) | W instance only (proven W-only by WPROP) |
| engine injection system (native) | engine | none exposed to script | `AnimInjection AnimationAttachmentInfo { BindingName "Weapon" }` (prefab) | while weapon equipped | — (engine drives it) | engine emits `CMD_Weapon_Inspection`/`WeaponInspectionState` to the injected graph |

Key runtime fact: the **`CharacterAnimGraphComponent` accessor failed at runtime** (`CHARACTER_ANIM_GRAPH_OWNER_UNAVAILABLE`) — so the P instance is not owned by a character-side `CharacterAnimGraphComponent` reachable via `FindComponent`/`CharacterEntity`. The next untested, source-backed candidate is `AnimationControllerComponent` (same engine base, with the attachment APIs, already used in Core on a character entity).

## D. Command/event route (Investigation E)

- The engine populates the standard graph variables/commands on the injected instance(s): `WeaponInspectionState`, `CMD_Weapon_Inspection`, `Stance`, `Firing` etc. — this is how inspection reaches the P/W graphs. It is **engine-populated**, not script-callable for arbitrary custom names.
- Script command emitters: `BindCommand`/`CallCommand` (int cmd IDs) exist on `BaseAnimationControllerComponent` (W + engine controllers) and `BaseAnimPhysComponent` (character). `BindAttCommand`/`CallAttCommand` exist on `BaseAnimationControllerComponent` (attachment-scoped).
- **No source-backed single emission reaching BOTH W and P is proven** (W-local setter proven W-only). The inspection route shows the engine can do it for engine-known variables/commands only.
- A custom shell command carrying to P therefore needs either the true P attachment owner (C) or a graph follower (not this phase).

## E. Rejected / not-viable

- Graph got deleted: **rejected** (inspection states/transitions/ASI intact).
- `CharacterAnimationComponent` attachment access: **not viable** (no attachment API).
- Engine-populated variable reuse for a custom shell request: **rejected** (engine only populates known names).
- Native reload as an activation path: **rejected** per policy.

## F. Smallest next step

- If the inspection binding is proven to be `KC_R` (owner-only check: temporarily deactivate the T4B context / set `Flags` to Overlay-only and test inspection while T4B is current) → the inspection regression is `INSPECTION_REGRESSION_INPUT_CONTEXT_PROVEN` and no graph work is needed.
- For the P owner: a bounded, source-guided **runtime enumeration diagnostic** (not installed in this phase) that, on the controlled character and current weapon, logs only animation/controller/injection-related objects/components reachable via `FindComponent`/`GetComponent` for the candidate types in section C (e.g. `AnimationControllerComponent`, `CharacterAnimGraphComponent`, `CharacterAnimationComponent`), plus `BindAttachment("Weapon")` id on each. Read-only; no gameplay writers. This directly separates "owner exists but different type" from "owner not script-addressable".

## Required classifications

```
INSPECTION_REGRESSION_CLASSIFICATION = INSPECTION_REGRESSION_MULTIPLE_CANDIDATES
  leading = INSPECTION_REGRESSION_INPUT_CONTEXT (0xa context claims KC_R; CharacterInspect binding UNRESOLVED)
  graph    = PROVEN INTACT (not the cause)
  alt      = P-injection/runtime
P_OWNER_CLASSIFICATION = P_OWNER_DISCOVERY_NEEDS_RUNTIME_DIAG
  (CharacterAnimGraphComponent accessor runtime-failed; AnimationControllerComponent candidate untested; no source-proven owner)
```

Answers to the two goal questions:
1. **What owns the character weapon injection?** Not proven. `CharacterAnimGraphComponent` (FindComponent/CharacterEntity) is runtime-unavailable; the leading untested script candidate is `AnimationControllerComponent` (engine, `FindComponent`, Core precedent, attachment APIs). The native engine injection system owns it at C++ level.
2. **How does inspection reach P, and where does it break?** Inspection writes `WeaponInspectionState`/`CMD_Weapon_Inspection` (engine) which drive the injected graph; the graph path is intact. The break is most likely at the **input layer** (the active `Priority 20000 / Flags 0xa` T4B context claims `KC_R`, likely removing R from vanilla `CharacterInspect`), with a secondary possibility that the P instance is not being driven in the current fixture. Binding of `CharacterInspect` is UNRESOLVED locally.

## No-functional-change statement

No functional file was changed by Phase 1F. `labs/`, `labs/.../Assets` (AGR/AGF/AST/ASI/TXA/ANM), prefab, config/input/keyBindingMenu, `.meta`/GUID, G3B2, production Weapons/Core are byte-identical to HEAD. Only this report (and an optional plan update) are committed.

STOP — no install, no runtime, no input/graph change.
