# MP-133 Task #1 — Weapon-local neutralization of vanilla reload (audit)

Status: **T4B_NATIVE_RELOAD_NEUTRALIZATION_AUDIT_COMPLETE**
Date: 2026-10-07
Task: Issue #34 — comment `6034137496` ("NON-ASTRA AGENT TASK — analyze weapon-local neutralization of vanilla reload").
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `7ff15179c2cc477e299834f22440f748b3c8d517`.
Mode: **SOURCE / STATIC READ-ONLY.** No gameplay, config, graph, prefab, script or meta change.

Evidence classes: **SOURCE** (files / installed SDK read now), **RUNTIME** (owner logs recorded in prior Issue #34 comments / reports), **INFERENCE** (explicit conclusion from the above), **UNRESOLVED** (not provable from available source).

---

## 0. Proven current state (given; not re-investigated)

```
actionPresent=true
active=true
RINPUT=YES
vanilla reload cmd1..6=YES
CUSTOM_R_DOUBLE_FIRE_CONFIRMED
```

The alternative question is therefore: can the **vanilla reload command** be made weapon-local inert for the T4B MP-133 only, while the custom `ARMST_MP133_Reload` route drives the real reload through ARMST + ASTRA?

Closed topics (NOT re-opened in this audit): GUID / resource registration / listener lifecycle / `keyBindingMenu` / Core integration.

Current lab sources, **live == labs byte-identical** (verified this session):

| File | SHA-256 |
|---|---|
| `Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c` | `7BE1D37513AF31E0C5BC3629BC3301DAFABEC966129AF83D04B688DD4D19BF8A` |
| `Scripts/Game/ARMST_T4B/ARMST_T4B_InstalledMagProbe.c` | `D581B9C9EE270725FFEC94C7685CBBCB2AB41DBA717F2B4FBCF8C4AC8DDCBEB1` |
| `Scripts/Game/ARMST_T4B/ARMST_T4B_G3B2_Transfer.c` | `FE4A19008EC290632378C0D3824C5AA7DD82018A761971BFCD920ED1E515FCCF` |
| `Scripts/Game/ARMST_T4B/ARMST_T4B_CharacterMagEventObserver.c` | `88BC52CB0FED611F8039EFD7C5754D1835BD348D9214825AC70AF1E69E181738` |
| `Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `A87E3722DD69AB1164ECB363D688CA4FB81331D7A8FF5710BD212B578D96B1AB` |
| `Scripts/Game/ARMST_T4B/ARMST_T4B_NormalRHandlerProbe.c` | `D5BA3052C07CD9B470F638AFF10DFB6C97ED835F08CF95D57E228A332F2658DE` (NO handler override — rejected A/B) |

`NormalRHandlerProbe.c` proves the current lab carries **no** `modded SCR_CharacterCommandHandlerComponent.HandleWeaponReloading` override (only the two inert constants `ARMST_T4B_INERT_RELOAD_CMD=10`, `ARMST_T4B_RELOAD_COMMAND_ID=0`). The A/B result `RACK_RECOVERED_WITH_T4B_HANDLER_REMOVED` is therefore the live baseline.

---

## 1. Reload command values 1..6 — producer / receiver / mutation boundary

Sources: production `MP133.agf` reload graph (`reports/MP133_V3_RELOAD_GRAPH_AUDIT.md` §2.3), official Bohemia `SampleWeapon_01.agf` (`references/bohemia/Arma-Reforger-Samples/83f12390/`), installed SDK 1.8.0.13. (SOURCE)

| cmd | meaning | producer | command surface | first physical effect | script receiver |
|---|---|---|---|---|---|
| 1 | rack / bolt | engine reload decision | `CMD_Weapon_Reload` `intValue=1` | `Weapon_Rack_Bolt` (chamber) | `OnCharacterCommand` (void) |
| 2 | insert whole mag (empty well) | engine | `intValue=2` | `Weapon_SpawnMagazine` → `Weapon_AttachMagazine` (new mag becomes ammo source) | `OnCharacterCommand` (void) |
| 3 | insert + rack | engine | `intValue=3` | attach, then rack | `OnCharacterCommand` (void) |
| 4 | remove + insert | engine | `intValue=4` | `Weapon_DetachMagazine`/`Despawn` then attach | `OnCharacterCommand` (void) |
| 5 | remove + insert + rack | engine | `intValue=5` | detach installed tube, attach new, rack | `OnCharacterCommand` (void) |
| 6 | remove | engine | `intValue=6` | `Weapon_MagRelease` → `Weapon_DetachMagazine` → `Weapon_DespawnMagazine` | `OnCharacterCommand` (void) |

Producer chain (SOURCE, prior producer audit): ordinary R → `CharacterInputContext` (`WeaponIsStartReloading` / `GetWeaponReloadType`) → `SCR_CharacterCommandHandlerComponent.HandleWeaponReloading(...)` (script) → `HandleWeaponReloadingDefault(...)` (**`proto external`**, engine) → engine selects reload type, sets `CMD_Weapon_Reload` and performs the native magazine operations. A **script producer** of the `intValue` values was **not found** (UNRESOLVED) — the values come from the internal engine reload decision.

Mutation boundary (RUNTIME + INFERENCE):
- cmd5 arrives with the installed tube present; the **first following snapshot is already `GetCurrentMagazine()==null`**; a later, separate `cmd3` update follows.
- **Neither** the weapon-side `BaseItemAnimationComponent.OnAnimationEvent` **nor** the character-side `SCR_CharacterControllerComponent.GetOnAnimationEvent` observed **any** `Weapon_MagRelease`/`Detach`/`Despawn`/`Spawn`/`Attach` event, yet the magazine physically disappeared.
- The active lab graph `MP133_Astra2.agf` contains **no** cmd2–6 states, yet the swap still happened.
- ⇒ The native physical mutation is performed **below / outside** the animation graph and both animation-event callbacks (`NATIVE_MUTATION_PATH_BELOW_OR_OUTSIDE_OBSERVED_ANIMATION_EVENT_CALLBACKS = STRONGLY_SUPPORTED`). Removing graph states/callbacks does not stop it.

Effects by operation: magazine identity (detach/attach), chamber/bolt (`Weapon_Rack_Bolt`), muzzle supply telemetry (muzzle `GetAmmoCount` is supply, not the round; chamber is `IsCurrentBarrelChambered`), UI/busy flags (below §8).

---

## 2. The current `[ARMST-T4B-CMD]` / `[ARMST-T4B-CMDROUTE]` receiver

`ARMST_T4B_WeaponAnimationComponent.OnCharacterCommand` (`ARMST_T4B_InstalledMagProbe.c` L131–141): `super.OnCharacterCommand(...)` then `probe.T4BLogCmd(commandID, intValue, floatValue)` → `[ARMST-T4B-CMD]`.
`ARMST_T4B_AstraV2_WeaponAnimationComponent.OnCharacterCommand` (`ARMST_T4B_AstraV2_...c` L54–64): `super.OnCharacterCommand(...)` then `[ARMST-T4B-CMDROUTE] receiver=weapon commandID=… intValue=… isReloadCommand=… inert=…`.

SDK signature (**SOURCE**, installed `ArmaReforgerScriptAPIPublic`, `interfaceBaseItemAnimationComponent.html`; inherited by `WeaponAnimationComponent`):

```
void  OnAnimationEvent (AnimationEventID, AnimationEventID, int, float, float)
void  OnCharacterCommand (int commandID, int intValue, float floatValue)
bool  OnPrepareAnimInput (IEntity owner, float ts)
bool  OnProcessAnimOutput (IEntity owner, float ts)
```

Answers to the required sub-questions:

1. **Before or after native mutation?** The *notification* is emitted **before** the physical mutation (cmd5 is observed while the tube is still installed; the tube then vanishes before cmd3). But being notified earlier does not confer veto power (below).
2. **Does the return value matter?** No. `OnCharacterCommand` is `void` — there is no return value and no "handled/consumed" contract.
3. **Can skipping `super` make reload commands inert?** **No (INFERENCE, strongly supported).** `OnCharacterCommand` is a downstream notification on the weapon's animation component; the reload decision and the physical magazine operations are performed by `HandleWeaponReloadingDefault` (engine) and are proven to occur **without** any animation callback being able to observe the magazine events, and **independently of the graph**. There is no source evidence that `super.OnCharacterCommand` participates in the mutation; skipping it would at most suppress the notification, leaving the engine reload intact. (Not runtime-tested here — this is the one conclusion labelled INFERENCE rather than RUNTIME.)
4. **Can it be selective to reload commands and T4B MP-133 only?** **Detection** yes — the receiver already gates on the T4B probe and can test `commandID==0 && intValue in 1..6` (it distinguishes cmd1 vs cmd5). **Neutralization** no — selection without veto has no effect on the engine mutation.
5. **What unrelated weapon commands would break?** `OnCharacterCommand` carries **all** character→weapon commands, not just reload. Dropping `super` unconditionally (or mis-gating) would suppress unrelated notifications. A reload-only gate would be safe for detection but, per (3), ineffective.

---

## 3. Weapon-local interception points — classification

| Candidate | Declared on | Local? | Class |
|---|---|---|---|
| `BaseItemAnimationComponent.OnCharacterCommand(int,int,float)` → void | weapon anim component | weapon-local | **OBSERVATION_ONLY** (time-wise pre-mutation, effect-wise none) |
| `BaseItemAnimationComponent.OnAnimationEvent(...)` → void | weapon anim component | weapon-local | **AFTER_MUTATION_ONLY** (notification; mag events not even observed) |
| `BaseItemAnimationComponent.OnPrepareAnimInput(IEntity,float)` → bool | weapon anim component | weapon-local | **UNKNOWN** (animation-input preparation; not source-proven to gate the reload/mag decision) |
| `BaseItemAnimationComponent.OnProcessAnimOutput(IEntity,float)` → bool | weapon anim component | weapon-local | **UNKNOWN** (animation-output processing; same caveat) |
| magazine attach/detach admission hook | — | weapon/mag | **ABSENT** (no such API in SDK: only `BaseMagazineComponent.SetAmmoCount` and `BaseMuzzleComponent.ClearChamber` writers) |
| `SCR_CharacterControllerComponent.GetOnAnimationEvent` invoker | character controller | character | **AFTER_MUTATION_ONLY** |
| `CharacterControllerComponent.OnReloaded(IEntity, BaseWeaponComponent)` | character controller | character | **AFTER_MUTATION_ONLY** |
| `BaseWeaponComponent.IsReloadPossible()` → `proto external bool` | weapon **class** | global `modded` | **UNPROVEN** pre-mutation candidate; not proven that the native reload reads it; **all-or-nothing** (cannot distinguish cmd1 from cmd2–6) |
| `SCR_WeaponAttachmentsStorageComponent.CanRemoveItem/CanReplaceItem` | storage **class** | global `modded` | **UNPROVEN**; not proven the detach passes through weapon storage |
| `CharacterControllerComponent.DetachCurrentMagazine()` / `ReloadWeaponWith(IEntity,bool)` | character controller | character | **NOT_APPLICABLE** (this *is* the mutation / producer, not a gate) |
| `BaseMagazineComponent.SetAmmoCount` / `BaseMuzzleComponent.ClearChamber` | mag / muzzle | local | **NOT_APPLICABLE** (writers, not detach admission) |
| `CharacterInputContext.SetReloadWeapon(int)` | input context | character | **PRE_MUTATION** technically, but historically broke rack → **REJECTED** |
| `SCR_CharacterCommandHandlerComponent.HandleWeaponReloading(...)` | character command handler | **global** | **PROVEN PRE_MUTATION consumption point**, but **owner-rejected** (blanket override broke native rack) and forbidden by this task |

Key result: the **only source-proven point where physical R is consumed before the native reload** is the character-side command handler — a global `modded` layer that the owner has explicitly rejected. Every weapon-local hook that fires before the mutation is `void` (observation only), and the only weapon-local `bool` hooks are animation input/output hooks with no source-backed reload-decision role.

---

## 4. cmd1 special case

**OPTION A — keep the native cmd1 rack, neutralize cmd2..6.**
Blocked. Selectively vetoing cmd2–6 while allowing cmd1 requires a weapon-local hook that (a) fires before the mutation and (b) can veto per reload type. No such hook exists: `OnCharacterCommand` cannot veto; `IsReloadPossible()` is all-or-nothing; the bool anim hooks do not encode reload type. On this evidence Option A is **not achievable weapon-locally**.

**OPTION B — neutralize cmd1..6 and re-implement rack through ARMST/ASTRA.**
Blocked by the same neutralization gap (if anything, more so: it must additionally reproduce rack across all stance/control paths). **Worse** than Option A. Not recommended even if neutralization were solved.

---

## 5. Decision — can native physical mutation be prevented weapon-locally?

```
CAN_NATIVE_PHYSICAL_MUTATION_BE_PREVENTED_WEAPON_LOCALLY = NO
```

- For **all** weapon-local receiver/observer hooks the answer is provably **NO**: they are `void` notifications that fire before/after the mutation but cannot consume it, and the mutation is performed engine-side, below/outside both animation-event callbacks and below the graph.
- The only residual **UNPROVEN** candidates are the two weapon-local `bool` animation hooks (`OnPrepareAnimInput` / `OnProcessAnimOutput`) and the two global-`modded` class candidates (`IsReloadPossible`, storage `CanRemoveItem`). The bool animation hooks are semantically animation-in/out and, critically, the proven engine mutation is **independent of animation execution**, so even a successful anim abort would not stop it. The global-`modded` candidates cannot distinguish cmd1 from cmd2–6 and are against the no-global-hook policy.
- The single source-proven pre-mutation consumption point (`HandleWeaponReloading`) is owner-rejected and forbidden here.

Therefore, **for the required capability (selectively neutralise vanilla cmd2–6 for the T4B MP-133 while keeping cmd1 rack and leaving all other weapons vanilla), no weapon-local mechanism exists on current evidence.**

---

## 6. Extracting `TryTransferOneShell(character, weapon)` from `ARMST_T4B_G3B2_Transfer.c` (outline only, NOT implemented)

Current structure (`ARMST_T4B_G3B2_TransferAction : ScriptedUserAction`, SHA `FE4A1900…`):
`PerformAction` → capture op context → `T4B2Scan()` (read-only donor classification) → `T4B2Preflight()` (fail-closed) → write gate `m_bG3B2WriteEnabled` → `T4B2Execute()`:
`T4B2Boundary()` → latch → **donor −1** (`SetAmmoCount`) → `T4B2AfterDonor()` → `T4B2Between()` → **target +1** (`SetAmmoCount`) → `T4B2AfterTarget()` → `T4B2Commit()` (conservation `donorBefore+targetBefore == donorAfter+targetAfter`) → telemetry → delayed read-only samples (+250/+1000 ms).

Proposed extraction (design only):
- Move the op context + helpers + `T4B2Scan/Preflight/Boundary/AfterDonor/Between/AfterTarget/Commit` into a **server-side service** exposing
  `bool ARMST_T4B_ShellTransferService.TryTransferOneShell(IEntity character, BaseWeaponComponent weapon, out string reason)`.
- Keep: `Replication.IsServer()` guard, single-op latch, conservation check, fail-closed donor whitelist / inventory-wide ownership, "donor is not the installed target / not inside a weapon storage", ammo-type match, 3-round target-capacity gate.
- Drop from the extracted path: the `ScriptedUserAction` owner/actor binding (replaced by the `character`/`weapon` arguments) and any UI text.
- Delayed (+250/+1000 ms) read-only verification is **optional** and can live outside the synchronous transfer (it does not mutate).
- Call site: the **already-present** receiver branch in `ARMST_T4B_AstraV2_WeaponAnimationComponent.OnAnimationEvent` for `ASTRA_ShellInsertCommit_W` (currently only logs `diagnostic_candidate_no_transfer`, L95–103). Replace that diagnostic branch with a gated call to `TryTransferOneShell`.
- Authority/replication and exactly-once semantics are **not** solved by this outline and remain a separate design item.

---

## 7. Future route — design only (NOT implemented)

```
physical R
  └─ ARMST_MP133_Reload (custom action, already registered: commandID=0 path via custom context)
     └─ ARMST code decides rack vs shell reload          <- needs weapon state discriminator (UNRESOLVED)
        └─ ASTRA graph (ShellReloadSTM 5 phases)
           StartReload → GrabShell → InsertShell
           └─ ASTRA_ShellInsertCommit_W
              └─ TryTransferOneShell(character, weapon)  <- §6 extraction
                 └─ ASTRA_Shell_CheckContinue_W
                    └─ ASTRA_Shell_EndReload_W
     other weapons / non-shell -> existing vanilla route
```

Prerequisites / blockers (all unresolved):
1. **Neutralize vanilla cmd2–6** for the T4B MP-133 — blocked by §5 (no weapon-local hook; the only proven layer is the rejected global handler).
2. **Weapon-local ASTRA request setter** — the previous audits recorded that `ASTRA_ShellRequest` has no setter and that `BindVariableBool` P→W propagation is not proven; the weapon-local variable setter is absent in 1.8.0.13.
3. **Registration of the five `Reload.Erc.<Phase>` rows** — previously pruned/mis-assigned by Workbench; unresolved.
4. **Server authority / exactly-once transfer** — the G3B2 transaction is a synchronous same-op double `SetAmmoCount`; multiplayer authority is unproven.

---

## 8. Non-physical side effects if the vanilla command stays alive but its mutation is blocked

Conditional (the mutation cannot currently be blocked; listed for completeness):

| Domain | Risk if CMD_Weapon_Reload remains but the mag operation is suppressed |
|---|---|
| animation state | vanilla reload clips/states may still be entered by the engine reload STM (double animation with the ASTM/ASTRA route) |
| busy / reload flag | `CharacterControllerComponent.IsReloading()` may stay set for the reload duration → fire/ADS blocked |
| sounds | magazine/rack sounds may still play |
| UI | weapon info / ammo widget may show a reloading state |
| command queue | `CMD_Weapon_Reload` stays set until the engine clears it → graph conditions that read it may misbehave |
| replication | server/client divergence if a client-only suppression is attempted |
| cooldown / state machine | engine reload cooldown/state transitions may still fire |

Because neutralization is not available, none of these can be validated; they are **UNRESOLVED**.

---

## 9. Other weapons must remain completely vanilla

Any future mechanism must be gated **per weapon** (e.g. presence of `ARMST_T4B_WeaponProbe` on the weapon entity, already used by every current lab file) so that non-T4B weapons keep the untouched vanilla `HandleWeaponReloading` path. A blanket global `modded` override is exactly what regressed native rack in the prior A/B and is not acceptable.

---

## 10. Comparison

| Architecture | Source proof | Selectivity (T4B only) | Keeps cmd1 rack | Other weapons safe | Risk | Verdict |
|---|---|---|---|---|---|---|
| **INPUT_SUPPRESSION** (custom context / Priority / Flags) | context/priority/flags semantics UNRESOLVED; `SetReloadWeapon` historically broke rack | yes | not proven (rack already regressed once) | global-ish | overblocks movement/fire/look; double-fire | **Rejected** |
| **WEAPON_LOCAL_NATIVE_NEUTRALIZATION** | no pre-mutation weapon-local veto hook exists (§3) | yes (detection) | n/a (cannot vet) | inherently safe | none engineered | **Not available** |
| **HYBRID** (leave vanilla R alive, block only T4B mutation) | requires the weapon-local neutralization of column 2, which does not exist | yes | n/a | yes | depends on neutralization | **Blocked** until a neutralization layer exists |

---

## 11. Required final answer

```
SAFE_TO_START_ASTRA_BINDING = NO_NATIVE_MUTATION_MUST_BE_SOLVED_FIRST
```

Reason: the alternative architecture depends on making the vanilla reload commands weapon-local inert for the T4B MP-133 while preserving the native cmd1 rack and leaving other weapons vanilla. No weapon-local mechanism with that capability is proven to exist; the only source-proven pre-mutation consumption point is the owner-rejected global `SCR_CharacterCommandHandlerComponent.HandleWeaponReloading`. Until native reload mutation neutralization is solved at a layer that can actually veto it, binding the reload flow to ASTRA would run alongside the native whole-mag swap.

---

## 12. What is NOT claimed / restrictions honoured

- No runtime or compile test was performed; the `super`-skip question is answered by inference, not by a runtime A/B.
- The global `HandleWeaponReloading` was **not** used or proposed for restoration.
- No ammo/mag/chamber writer, graph, prefab, config, meta or production/Core file was changed.

```
WORKBENCH_LAUNCHED = NO
REFORGER_LAUNCHED = NO
GAME_MODE_LAUNCHED = NO
RUNTIME_TEST = NO
COMPILE_TEST = NOT_RUN_BY_AGENT
LIVE_CHANGED = NO
LABS_GAMEPLAY_CHANGED = NO
CONFIG_CHANGED = NO
META_CHANGED = NO
GUID_CHANGED = NO
CORE_CHANGED = NO
SCRIPT_CHANGED = NO
GRAPH_CHANGED = NO
```

Final status: `T4B_NATIVE_RELOAD_NEUTRALIZATION_AUDIT_COMPLETE`. STOP.
