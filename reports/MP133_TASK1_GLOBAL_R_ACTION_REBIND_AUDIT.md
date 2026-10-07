# MP-133 Task #1 — Global keyboard-R action rebind / dispatch audit

Status: **T4B_GLOBAL_R_ACTION_REBIND_AUDIT_COMPLETE**
Date: 2026-10-07
Task: Issue #34 — comment `6035595614`.
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `14d88b4a6ce78eff273879fc089c38da3c7525a9`.
Mode: **SOURCE / STATIC READ-ONLY.** No implementation, no staging, no live/labs change.

Evidence classes: **INSTALLED_VANILLA_SOURCE**, **OFFICIAL_SOURCE**, **OWNER_WORKBENCH_EVIDENCE**, **PUBLIC_WORKING_MOD**, **INFERENCE**, **UNRESOLVED**.

---

## Proven state (not reopened)

- GUID-preserving override `{795184CF9AD764DB}Configs/System/chimeraInputCommon.conf` works; `ARMST_MP133_Reload` is registered and receives physical R.
- ActionContext flag/priority selective ownership is BLOCKED (Overlay keeps vanilla alive; Exclusive-alone `0x8`; no editor-supported Overlay+Exclusive).
- Global `modded SCR_CharacterCommandHandlerComponent.HandleWeaponReloading` remains REJECTED.

---

## AUDIT A — exact vanilla reload action / input structure

**Result: UNRESOLVED for the exact action.** The selected config `{795184CF9AD764DB}Configs/System/chimeraInputCommon.conf` lives inside the packed game `data.pak` files (`C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\addons\data\*.pak`). A byte search of the paks for `chimeraInputCommon` returned **no plaintext hit** (entries compressed/indexed), and there is **no extracted copy** in the repo `catalog/`, `references/`, Tools, or the user profiles. `customInputConfigs` (game profile) is **empty** and `ReforgerUserInput.conf` does **not exist** on disk.

What IS proven:

| Fact | Class |
|---|---|
| `InputManagerSettings Default "{795184CF9AD764DB}Configs/System/chimeraInputCommon.conf"` | INSTALLED_VANILLA_SOURCE (game `addons/data/ArmaReforger.gproj` L331–333) |
| `InputSettingsPath "ReforgerUserInput.conf"` (user bindings stored separately) | INSTALLED_VANILLA_SOURCE (same gproj, L10) |
| `UiMappings "{0AD37213EFEB0B61}Configs/System/chimeraMapping.conf"`, `InputButtonLayoutConfig` | INSTALLED_VANILLA_SOURCE (gproj) |
| Vanilla action names follow a `Character*` / `Menu*` / `Inventory_*` convention | PUBLIC_WORKING_MOD — Overthrow `Configs/System/chimeraInputCommon.conf` references `"CharacterForward"`, `"CharacterRight"`, `"CharacterSprint"`, `"Inventory_InspectZoom"`, `"MenuBack"`, `"MenuSelect"`, `"MenuUp/Down/Left/Right"` |
| The ordinary reload action's exact **name**, containing **context**, and its **keyboard `KC_R` + gamepad** child sources | **UNRESOLVED** |

There is no accessible installed/official text that names the reload action. (`Page_Input.html` documents contexts, not action names; `keyBindingMenu.conf` is a rebinding-menu config, and the only copies on disk — Core and T4B — list only ARMST entries.) The likely name is `CharacterReload` by convention, but this is **inference, not evidence**, and is not relied on.

**Gamepad structure cannot be described** for the same reason (whether keyboard and gamepad are sibling `InputSourceValue`/`InputSourceCombo` children under one `InputSourceSum`, and the `FilterPreset`/`InputFilter` chain) → **UNRESOLVED**.

---

## AUDIT B — can a GUID-preserving override modify an EXISTING action selectively?

**Classification: `EXISTING_ACTION_SELECTIVE_OVERRIDE = POSSIBLE_UNPROVEN`.**

Evidence gathered:

- The config system supports **new** actions and **additive** edits to **existing contexts**: Core `ARMST-PLATFORM---Core/Configs/System/chimeraInputCommon.conf` and ACE-Anvil `addons/core/Configs/System/chimeraInputCommon.conf` both use `ActionContext <Existing> { ActionRefs +{ "<NewAction>" } }`; ACE-Anvil `addons/finger/...` injects a new action into the existing `MapContext` via an inline `Actions { ... }` block. (SOURCE / PUBLIC_WORKING_MOD)
- **No local or public example was found that re-declares an existing `Action` to change/remove one of its `InputSource` children.** (bounded negative result)
- The additive operator `+{ ... }` is proven for named **arrays** (ActionRefs). A **subtract/remove** operator for array elements (`-{ ... }` or equivalent) was **not found** anywhere in source/installed docs → UNRESOLVED.
- Whether re-declaring `Action CharacterReload { InputSource ... }` **replaces the `InputSource` member** or **merges/adds** to it is **not source-proven**. If it replaces the member, a gamepad-only source tree could be supplied; if it merges, the vanilla keyboard `KC_R` source would remain. (UNRESOLVED)
- GUID/source identity preservation is necessary but **not sufficient** — it governs resource participation, not member-merge semantics. (INFERENCE)
- Redefining the action in the input resource would also affect the **keybinding UI/preset** view of that action (`keyBindingMenu.conf` entries keyed by `m_sActionName`). (INFERENCE)

Answers: can an addon redeclare the existing vanilla reload action? — likely POSSIBLE, semantics UNPROVEN. Replace whole action vs merge fields? UNPROVEN. Remove only keyboard KC_R while preserving gamepad? POSSIBLE_UNPROVEN (depends on replace/merge and on a subtract operator that was not found). Replace an `InputSourceSum` safely? UNPROVEN.

---

## AUDIT C — designs for a single keyboard-R owner

| Design | Mechanism | Regression risk | Remap impact | Gamepad | Scope |
|---|---|---|---|---|---|
| **C1 strip keyboard R** | Keep vanilla action, remove only the keyboard `KC_R` child; add ARMST KC_R action | needs selective child removal (B unproven) | user reload remap diverges from ARMST | preserved | global input change |
| **C2 replace whole source** | Re-declare vanilla action with gamepad-only source tree + ARMST KC_R action | if merge-not-replace, vanilla KC_R survives → double-fire; if replace drops gamepad on error | same | risky (easy to drop) | global |
| **C3 keep action, change consumer** | Keep vanilla action, block native consumption and dispatch ourselves | **requires the rejected global handler** or per-weapon veto that does not exist | n/a | n/a | global/rejected |
| **C4 keybinding-layer neutralize** | Neutralize default keyboard R via `keyBindingMenu.conf`/presets/user config | keyBindingMenu defines **rebind UI entries**, not runtime bindings; user bindings live in `ReforgerUserInput.conf` (absent) | directly the remap surface | n/a | NOT_SUPPORTED from data available |

C3 is rejected (only proven pre-mutation consumption point is the forbidden global handler; see prior neutralization audit). C4 fails because the available configs do not carry runtime default bindings.

---

## AUDIT D — where ARMST keyboard R should live if it becomes global

`GLOBAL_ARMST_R_DELIVERY_WITHOUT_CONTEXT_SUPPRESSION = PROVEN_MECHANISM (delivery) / UNPROVEN (behavior)`.

- **Additive reference on an always-active vanilla context** — `ActionContext <AlwaysActive> { ActionRefs +{ "ARMST_MP133_Reload" } }` — is the proven mechanism (Core/ACE use exactly this on `CharacterMovementContext` / `CharacterGeneralContext`). (PUBLIC_WORKING_MOD)
- This delivers R to the ARMST action for every on-foot weapon **without a custom suppressing context**, so movement/look/fire keep working. The dispatcher then decides T4B vs non-T4B behaviour.
- Which vanilla context is "always active on foot" precisely (CharacterGeneralContext vs CharacterWeaponContext vs CharacterMovementContext) is **UNRESOLVED** because the vanilla context list is packed (AUDIT A). `CharacterGeneralContext` is used by Core (proven existing/active); `CharacterWeaponContext` is only named in the task, not source-proven here.
- Keeping a custom **Overlay** context active globally also delivers R without whole-tier suppression but is unnecessary given the additive-reference route.

---

## AUDIT E — dispatching NON-T4B weapons back into vanilla reload

Candidates (installed SDK, `ArmaReforgerScriptAPIPublic`):

| API | Signature | Assessment |
|---|---|---|
| `SCR_CharacterControllerComponent.ReloadWeapon()` | `proto external bool` | best candidate — direct engine "request reload" entry; body not shipped → does it run normal selection / authority / state gating is UNPROVEN |
| `SCR_CharacterControllerComponent.ReloadWeaponWith(IEntity, bool bForceDetach=false)` | `proto external bool` | reload with a **specific** ammo entity; not a generic reload |
| `CharacterInputContext.SetReloadWeapon(int ReloadType)` | `proto external void` | sets the input-context reload type; historically implicated when the global handler regressed rack |
| `SCR_CharacterControllerComponent.DetachCurrentMagazine()` | `proto external bool` | this is a mutation, not a reload request |
| `SCR_CharacterControllerComponent.IsReloading()` | `proto external bool` | read-only |
| `SCR_CharacterControllerComponent.OnReloaded(IEntity, BaseWeaponComponent)` | `protected` | completion callback, not an entry |

Neither SDK page ships a body, so "invokes normal engine reload selection / authority / no recursion / preserves rifles / rack" cannot be **proven** statically. `HandleWeaponReloading` override is excluded per the task.

**Classification: `NON_T4B_VANILLA_RELOAD_DISPATCH = UNPROVEN`** (with `ReloadWeapon()` as the single most plausible entry; `ReloadWeaponWith` for explicit-magazine cases).

---

## AUDIT F — custom T4B rack after vanilla keyboard R is removed

| Candidate | Assessment |
|---|---|
| `CharacterInputContext.SetReloadWeapon(1)` | directly sets reload type 1 (rack) for the input context the engine handler reads; **UNPROVEN** whether it reproduces native cmd1 outside the engine handler, and prior V1/V2 evidence ties this call to rack regression |
| `BaseAnimPhysComponent.BindCommand("CMD_Weapon_Reload")` + `CallCommand(TAnimGraphCommand,int,float)` | drives the animation graph command; `BindCommand(string)`→`TAnimGraphCommand`, `CallCommand(TAnimGraphCommand,int,float)` exist (SOURCE). Animation-side only; may not perform the chamber mutation; interaction with the engine's own command stream UNPROVEN |
| `SetCurrentCommand(AnimPhysCommandScripted)` | replaces the character's scripted command; broad, conflict-prone; UNPROVEN |
| Custom ASTRA graph request into `RackBoltAnim` / `Reload.ReloadActionBolt` | ASTRA2 already has `CMD1 → RackStanceSTM → RackBoltAnim`; entering it still requires setting `CMD_Weapon_Reload=1` on the character command channel (same setter gap) |
| Manual chamber mutation | forbidden (task + prior policy) |

Historical constraints hold: native cmd1 rack is known-good only while no global handler is present; weapon-side `OnCharacterCommand` is observation-only.

**Classification: `CUSTOM_T4B_RACK_ENTRY = POSSIBLE_UNPROVEN`** (no source-proven manual rack API).

---

## AUDIT G — recursion / double-fire call chains

Premise: vanilla reload no longer owns keyboard `KC_R`; ARMST owns it; dispatcher runs in the `AddActionListener("ARMST_MP133_Reload")` callback.

```
1. keyboard R, normal rifle:
   KC_R -> ARMST_MP133_Reload (action) -> listener -> dispatcher
        -> non-T4B -> ReloadWeapon() [API] -> engine reload selection -> CMD_Weapon_Reload -> vanilla
2. keyboard R, T4B, rack needed:
   KC_R -> ARMST action -> listener -> dispatcher -> T4B+rack -> SetReloadWeapon(1)/graph [UNPROVEN] -> cmd1 -> RackBoltAnim
3. keyboard R, T4B, shell load:
   KC_R -> ARMST action -> listener -> dispatcher -> T4B+shell -> ASTRA pipeline (separate task)
4. gamepad reload, normal rifle:
   gamepad source (untouched) -> vanilla reload action -> vanilla reload
5. gamepad reload, T4B:
   design choice: (a) leave gamepad on vanilla -> T4B gets native whole-mag reload (undesired);
                   (b) also move gamepad into ARMST -> dispatcher must handle non-T4B gamepad too (larger surface)
```

**Recursion:** `ReloadWeapon()` is a direct API call, not a physical-input event, so it does **not** re-fire the `AddActionListener` for `ARMST_MP133_Reload`; and `CMD_Weapon_Reload` is an engine command, not an input action. Therefore **no input-recursion loop is expected** — **provided** the vanilla keyboard `KC_R` source is actually removed (otherwise both the vanilla action and the ARMST action fire → the known double-fire). This is INFERENCE, not runtime-proven.

**Gamepad design choice must be explicit** and is not decided here.

---

## AUDIT H — keybinding / remapping

- User bindings persist via `ReforgerUserInput.conf` (separate `InputSettingsPath`, gproj L10); the on-disk copy is absent, and `customInputConfigs` is empty. (INSTALLED_VANILLA_SOURCE)
- `keyBindingMenu.conf` (`SCR_KeyBindingMenuConfig`) defines the **rebind menu entries** (action name → display/preset), not runtime defaults. T4B labs already registers `ARMST_MP133_Reload` there; Core registers its actions. (SOURCE)
- If ARMST owns keyboard R but its keybinding entry is absent or the vanilla "reload" entry no longer maps to the real behaviour, a user who remaps reload would silently break. A keyboard-only interception also ignores the gamepad remap path.
- **Minimum viable experimental path:** ARMST action fixed to KC_R (menu entry optional, temporary) + vanilla reload keyboard source removed; assert no double-fire.
- **Production-ready path:** both keyboard and gamepad reload routing must be reasoned about; the visible "reload" keybinding entry should drive the ARMST dispatch; `keyBindingMenu.conf` work becomes mandatory. Otherwise remap/UX regressions are guaranteed.

---

## DECISION

```
RECOMMENDED_R_OWNERSHIP_ARCHITECTURE = VANILLA_ACTION_REBIND + GLOBAL ARMST DISPATCH
SAFE_TO_STAGE_GLOBAL_R_DISPATCH = INSUFFICIENT_EVIDENCE
```

Comparison: `ACTIONCONTEXT_SUPPRESSION` — blocked (prior audits); `GLOBAL CHARACTER HANDLER` — rejected and forbidden; `VANILLA_ACTION_REBIND + GLOBAL ARMST DISPATCH` — the most promising remaining model, but it currently rests on **three** unproven prerequisites, not one:

1. selective override/removal of the existing vanilla action's keyboard `KC_R` source (AUDIT B, `POSSIBLE_UNPROVEN`; exact vanilla action block UNRESOLVED in AUDIT A);
2. a source-proven non-T4B vanilla reload entry point (AUDIT E, `UNPROVEN`);
3. a source-proven custom T4B rack entry (AUDIT F, `POSSIBLE_UNPROVEN`).

Because more than one independent fact is missing, the gate is `INSUFFICIENT_EVIDENCE` rather than `YES_AFTER_ONE_SOURCE_GATE`.

**Single most valuable next source fact (recommendation, even though the gate is not `YES_AFTER_ONE...`):** obtain the exact vanilla reload `Action` block (name, containing context, full `InputSource` tree with the keyboard `KC_R` and gamepad children) from the base `{795184CF9AD764DB}Configs/System/chimeraInputCommon.conf` — e.g. a read-only owner Workbench browse of the base resource, or an extracted vanilla input config. This resolves AUDIT A and unblocks the AUDIT B replace-vs-merge determination, which is the first real gate.

---

## Confirmation / boundaries

```
WORKBENCH_LAUNCHED = NO
REFORGER_LAUNCHED = NO
GAME_MODE_LAUNCHED = NO
RUNTIME_TEST = NO
COMPILE_TEST = NOT_RUN_BY_AGENT
LIVE_CHANGED = NO
LABS_CHANGED = NO
CONFIG_CHANGED = NO
META_CHANGED = NO
GUID_CHANGED = NO
KEYBINDING_CHANGED = NO
SCRIPT_CHANGED = NO
ASTRA_CHANGED = NO
G3B2_CHANGED = NO
CORE_CHANGED = NO
PRODUCTION_WEAPONS_CHANGED = NO
```

Final status: `T4B_GLOBAL_R_ACTION_REBIND_AUDIT_COMPLETE`. STOP.
