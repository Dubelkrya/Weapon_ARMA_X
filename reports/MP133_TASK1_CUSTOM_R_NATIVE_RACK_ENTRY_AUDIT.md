# MP-133 Task #1 — custom-R → T4B native-equivalent rack entry (audit + staged script)

Status: **T4B_CUSTOM_R_NATIVE_RACK_AUDIT_COMPLETE**
Date: 2026-10-07
Task: Issue #34 — comment `6035862376`.
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `ef096287e1c89a8cd2817d00e9d6e4bfeb462d72`.
Mode: **SOURCE / STATIC ONLY.** One staged script prepared (below); live/labs/input-config untouched.

Evidence classes: **OWNER_RUNTIME**, **PUBLIC_RETAIL_VERIFICATION / PUBLIC_WORKING_MOD**, **LOCAL_LAB_SOURCE**, **INSTALLED_SDK**, **INFERENCE**, **UNRESOLVED**.

---

## Proven input state (given; not reopened)

Owner runtime: selective ownership works (T4B context active, `actionPresent=true`, physical R → `[ARMST-T4B-RINPUT]` repeatedly), normal controls and non-T4B weapons unaffected; **no** `[ARMST_T4B-CMD]` and **no** `Weapon_Rack_Bolt` in the captured segment. `T4BRInputDown()` is log-only → rack is simply not dispatched yet. Input config/context is out of scope here.

---

## AUDIT A — known-good native cmd1 producer path

```
vanilla CharacterReload  (keyboard:KC_R / gamepad0:x)
 -> CharacterWeaponContext (Priority 10)                [PUBLIC_RETAIL_VERIFICATION]
 -> CharacterInputContext reload request (WeaponIsStartReloading / GetWeaponReloadType)
 -> SCR_CharacterCommandHandlerComponent.HandleWeaponReloading(...)   (script bool)
 -> HandleWeaponReloadingDefault(...)                                 (proto external bool)
 -> CMD_Weapon_Reload intValue = 1
 -> weapon/player animation graph: Idle -> Buffer3 -> ReloadRouteSTM -> RackStanceSTM -> RackBoltAnim
       (Source "Reload.ReloadActionBolt")
 -> Weapon_Rack_Bolt  (engine-consumed)
 -> native chamber mutation (tube N -> N-1, chambered 0 -> 1)
```

Sources: owner review `6035717848` (Overthrow `docs/bugs/BUG-156.md` @ `9dbb8fad…` names `CharacterReload`, `CharacterWeaponContext` Priority 10, `keyboard:KC_R`, `gamepad0:x`, verified against retail `chimeraInputCommon.conf` — PUBLIC_RETAIL_VERIFICATION); `MP133_TASK1_ASTRA2_STAGE_A_RACK.md` + `MP133_TASK1_RACK_BYPASS_RECONCILIATION_AUDIT.md` for the cmd1 graph route; `ARMSTMP133T4B_InstalledMagProbe` observer for the `Weapon_Rack_Bolt` event.

Because the ARMST context **suppresses** the vanilla `CharacterReload`, the engine's reload pipeline is not entered from input for the T4B weapon. The rack entry must therefore be *injected below the input layer* while still going through the engine's weapon/reload system (not the animation-command layer).

---

## AUDIT B — rack entry candidates

### B1 `SCR_CharacterControllerComponent.ReloadWeapon()`
- Signature: `proto external bool CharacterControllerComponent.ReloadWeapon()` (INSTALLED_SDK).
- Callsites: **none found** in the addons tree; no SDK body/description shipped → behaviour, authority and command selection **UNPROVEN**.
- Risk: it lets the **engine choose** the reload type; on a fixed tube in the proven state this could select a whole-mag path (cmd2–6) and detach the tube — the worst outcome.
- Class: **PLAUSIBLE_RUNTIME_PROBE** (unsafe to try first).

### B2 `CharacterInputContext.SetReloadWeapon(1)` — **selected**
- Signature: `proto external void CharacterInputContext.SetReloadWeapon(int ReloadType)` (INSTALLED_SDK).
- Consumer evidence: in the V1 inert-command probe the script handler called `SetReloadWeapon(10)` and the engine propagated it — the weapon observer saw `commandID=0 intValue=10`. So the value is consumed by the engine's native reload/command pipeline (LOCAL_LAB_SOURCE).
- Rack precedent: production Core `ARMST-PLATFORM---Core/Scripts/Game/Items/ARMST_WEAPONS_HANDLER.c`, `OnRackBoltMDown()` (`L354–388`) calls `inputCtx.SetReloadWeapon(1)` to trigger the rack (comment: "Déclenche l'anim qui émettra l'AnimEvent"). The lab constant is `LAB_RACK_CMD = 1; // pump (Core ARMST sends this)` (`ARMST_MP133_Lab_Character.c` L39).
- Type-pinned: `1` = rack, so it cannot request cmd2–6 → narrowest/safest probe.
- Caveats (honest): Core **also** performs manual ammo/chamber handling on the rack (`TAO_DecrementAmmoOnRack` / `TAO_ClearChamberIfNoMagOrEmpty`), and the lab notes "rack ammo stays in Core". Whether the **engine natively** performs tube→chamber from `SetReloadWeapon(1)` on this weapon is **UNPROVEN** and is exactly what the owner runtime must discriminate. If it only plays the animation, the task's "no manual write" constraint means STOP.
- Class: **PLAUSIBLE_RUNTIME_PROBE** (best source-backed, type-pinned).

### B3 animation-command route
`BaseAnimPhysComponent.BindCommand("CMD_Weapon_Reload")` → `TAnimGraphCommand`; `CallCommand(TAnimGraphCommand,int,float)`; `SetCurrentCommand(AnimPhysCommandScripted)` (INSTALLED_SDK). These drive the **animation graph command** only; they do not run the engine weapon/reload mutation, and the character-side command stream is owned by the engine. **ANIMATION_ONLY → rejected.**

### B4 any better native API
SDK method scan for Rack/Bolt/Pump/Chamber found only read-only/adjacent APIs: `IsBarrelChambered`, `IsCurrentBarrelChambered`, `IsChamberingNecessary`, `IsChamberingPossible`, `GetOpenBoltState`, and the writers `ClearChamber` (forbidden) / `DetachCurrentMagazine` / `ReloadWeaponWith` (mutation-specific). **No dedicated "rack bolt" API exists.** `ReloadWeaponWith(IEntity,bool)` needs a specific ammo entity → NOT_APPLICABLE.

---

## AUDIT C — state gate (fail-closed)

Selected predicate (source-proven reads only):

```
current weapon = canonical T4B MP-133   (ARMST_T4B_WeaponProbe on the weapon entity)
installed magazine present              (weapon.GetCurrentMagazine() != null)
magazine ammo > 0                       (magazine.GetAmmoCount())
chamber empty                           (muzzle.IsCurrentBarrelChambered() == false)
controller not already reloading        (ctrl.IsReloading() == false)
```

Considered but **not** added: `WeaponIsRaised()`, `IsChamberingPossible()`, `CurrentBarrelIndex` — their exact required value for the rack path is not source-proven, and adding an unknown-false condition would silently block the probe. Fail-closed here means: dispatch only when the proven core state holds; otherwise log `phase=reject`.

---

## AUDIT D — exactly-once / held-R

The input config binds `ARMST_MP133_Reload` to a single `InputSourceValue { Input "keyboard:KC_R" }` **with no filter** (no `InputFilterRepeat`), so `EActionTrigger.DOWN` is an edge event → one per physical press. In-flight protection uses the source-proven `ctrl.IsReloading()` gate (no timers, no guessed latch): while a native reload is running, a new request is rejected. No persistent latch is needed; repeated presses are user-driven and each is bounded by `IsReloading()`.

---

## AUDIT E — mutation / conservation

The staged script performs **no** ammo/mag/chamber writes (0 `SetAmmoCount`, 0 `ClearChamber`, 0 `DetachCurrentMagazine`). Native/engine rack logic must perform the tube→chamber transition. Owner runtime acceptance:

```
before: Tube3 N, chambered=0
after : Tube3 N-1, chambered=1, same installed mag identity, no detach, no cmd2..6
Weapon_Rack_Bolt observed (if it remains part of the native path)
```

If the probe shows the engine does **not** chamber natively and would require a manual write, this path is a dead end (no manual writes allowed).

---

## AUDIT F — interaction with future ASTRA shell reload (design only)

```
if T4B && magPresent && ammo > 0 && chambered == 0  -> rack request (this task)
else                                                -> future shell-reload dispatcher (ASTRA, NOT here)
```

Rack takes priority when the chamber is empty and the tube has ammo. ASTRA/G3B2 are not touched.

---

## STAGED CANDIDATE (stage gate passed)

`CUSTOM_T4B_RACK_ENTRY = PLAUSIBLE_RUNTIME_PROBE` → `T4B_RACK_STAGE_READY_OWNER_REVIEW`.

One staged script, copied from the current accepted probe and changed minimally:

- Path: `artifacts/astra-rebuild/stageT4BRackDispatch/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c`
- Base: current accepted script `A87E3722DD69AB1164ECB363D688CA4FB81331D7A8FF5710BD212B578D96B1AB` (8351 B, live == labs).
- Staged SHA-256: `F5D59DB9D00469E4664DE219CF29110A40D6DCE73DE23846ED60C44B6EFA68C1` (10420 B).
- Diff vs base: `1 file changed, 50 insertions(+), 1 deletion(-)` — only a header note, one constant, one helper `T4BRTryRack(...)`, and one call site in `T4BRInputDown`.

Functional delta:
- `protected const int ARMST_T4B_RACK_RELOAD_TYPE = 1;`
- `T4BRTryRack(...)` — fail-closed gate (`labWeapon`, controller, `magPresent && ammo>0 && chambered==0`, `!IsReloading`, input context) then `ctrl.GetInputContext().SetReloadWeapon(1)` + one-shot `[ARMST-T4B-RACK] phase=request|reject` log.
- call added at the end of `T4BRInputDown`.

Static checks (staged):
```
braces 30/30   parens 138/138
SetAmmoCount=0  ClearChamber=0  DetachCurrentMagazine=0  bare ReloadWeapon(=0
SetReloadWeapon=1 call site    IsReloading=1 gate (2 comment mentions)
HandleWeaponReloading=0        CallLater/Update=0  HandleWeapons=0
ActionRefs / keyBindingMenu / .meta / GUID / ASTRA / G3B2 / configs = untouched
```
Lifetime/context/logs unrelated to rack = byte-identical to base. No `.meta` staged; the runtime install (if authorized) must keep the proven `{795184CF9AD764DB}` meta unchanged.

Stage-gate conditions: (1) callable from the listener path ✓; (2) routes into the engine reload/command pipeline, not the animation-command setter ✓ (with the documented residual risk that it may be animation-only); (3) no global `HandleWeaponReloading` ✓; (4) no ammo/mag/chamber write ✓; (5) T4B-only fail-closed gate ✓; (6) no input-config change ✓.

---

## Owner-only runtime plan (DO NOT RUN here)

Safe rack-capable state: canonical T4B MP-133, Tube3 `N>0`, `chambered=0`. Press R **once**.

Expect:
```
RINPUT = YES
rack request = exactly once ([ARMST-T4B-RACK] phase=request method=SetReloadWeapon type=1)
CMD_Weapon_Reload intValue=1 = YES (if visible)
cmd2..6 = NO
Weapon_Rack_Bolt = YES (if part of native path)
Tube3 N -> N-1 ; chambered 0 -> 1 ; mag identity unchanged
movement/look/fire/aim unaffected
```

STOP immediately if the magazine detaches, cmd2..6 appears, conservation breaks, or controls regress. Rollback = keep the accepted script `A87E3722…` (do not install the staged file) or remove the dispatch. Do not test the empty-tube cmd5/cmd3 state.

---

## Required classifications

```
CUSTOM_T4B_RACK_ENTRY = PLAUSIBLE_RUNTIME_PROBE
T4B_RACK_STAGE_READY_OWNER_REVIEW
```

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
INPUT_CONFIG_CHANGED = NO
META_CHANGED = NO
GUID_CHANGED = NO
KEYBINDING_CHANGED = NO
ASTRA_CHANGED = NO
G3B2_CHANGED = NO
CORE_CHANGED = NO
PRODUCTION_WEAPONS_CHANGED = NO
```

Final status: `T4B_CUSTOM_R_NATIVE_RACK_AUDIT_COMPLETE`. STOP.
