# MP-133 V3 — T3F fire-event audit + passive fire-accounting trace (lab-only)

**Status:** `T3F_PHASE_A_AUDIT_DONE / PHASE_B_LIMITED_IMPLEMENTED / STATIC_PASS / OWNER_RUN_REQUIRED`.
Lab-only; production Weapons/Core, frozen V2/P2 and all graph/ASI/clip/prefab/GUID/meta
unchanged; Workbench/game NOT run by the agent. Source: Issue #27 comment 5970537191 (T3F)
and comment 5970509383 (T3 runtime read-out).

Statement labels: **SOURCE** (file), **OWNER-RUNTIME** (owner log), **INFERENCE**, **UNRESOLVED**.

---

## Phase A — read-only audit

### A.1 Fire state in the active graph (**SOURCE**, `MP133.agf`)
- `AnimSrcNodeSource FireAnim` (line 10): `Source "Reload.Erc.Fire"`, `Looptype "No Loop"`.
- `AnimSrcNodeSource FireEmptyAnim` (line 15): `Source "Reload.Erc.Trigger"`, `No Loop`.
- `Queue 1` enqueues them (lines 311–320):
  `FireAnim` on `Firing && HasVariableChanged(Firing) && !Empty`;
  `FireEmptyAnim` on `Firing && HasVariableChanged(Firing) && Empty`.
- The graph has **no event nodes** on the fire path; it reacts to the `Firing`/`Empty`
  variables. Command routing is unchanged (reload STM as in
  `MP133_V3_RELOAD_GRAPH_AUDIT.md`).

### A.2 Which clips the fire rows resolve to (**SOURCE**)
| ASI row | Player (`MP133_player.asi`) | Weapon (`MP133_weapon.asi`) |
|---|---|---|
| `Reload.Erc/Pne.Fire` | `{240822D89A9449F9}Assets/Weapons/Rifles/AK74/anims/anm/p_rfl_ak74_erc_fire.anm` | `{4644F33E2CADCF0A}…/w_rfl_ak74_erc_fire.anm` |
| `Reload.Erc/Pne.Trigger` | `{240822D89A9449F9}p_rfl_ak74_erc_fire.anm` | `{01F1072211063BE5}…/w_rfl_ak74_erc_trigger.anm` |

These are **base-game AK74 clips**, not present as local `.txa`; their authored animation
events are therefore **UNRESOLVED from local source** — do not infer events from filenames.
Whether the fire clip delivers any events to the weapon-side `OnAnimationEvent` is
**UNRESOLVED** until a run (T3 runtime already proved that native **magazine** events are
delivered weapon-side — `OWNER-RUNTIME`, comment 5970509383).

### A.3 Installed-SDK callback audit for an *actual shot* (**SOURCE**)
Read from `…\Arma Reforger Tools\Workbench\docs\ArmaReforgerScriptAPIPublic\html\` (installed
1.8.0.13 docs):
- `BaseWeaponComponent` exposes **no** public fire/shot callback or invoker — only
  `GetCurrentFireModeName/Type`, `OnWeaponActive/OnWeaponInactive`, `GetCurrentMuzzle`,
  `IsChambering*`.
- `SCR_WeaponComponent.GetOnWeaponStateChanged()` exists, but it is a **weapon active/inactive
  state** invoker, **not** a per-shot signal.
- The genuine "a round was fired" callbacks live on **muzzle-effect** components, not on the
  weapon component:
  - `MuzzleEffectComponent.OnFired(IEntity effectEntity, BaseMuzzleComponent muzzle, IEntity projectileEntity)` — protected;
  - `SCR_WeaponBlastComponent.OnWeaponFired(IEntity, BaseMuzzleComponent, IEntity)` — protected;
  - `SCR_MuzzleEffectComponent.GetOnWeaponFired()` — a script invoker, plus `OnFired(...)`.
  Observing these requires a **lab-prefab subclass of the effect component** (a second
  gameplay file / prefab edit) or a **global `modded` hook** → out of this task's scope.
- `OnAmmoCountChanged(weapon, muzzle, magazine, ammoCount, isBarrelChambered)` appears only on
  HUD/scenario consumers (`SCR_WeaponInfo`, `SCR_WeaponInfoVehicle`, `SCR_WeaponInfo_MultiWeaponTurret`,
  `SCR_ScenarioFrameworkOnWeaponAmmoCountChangedAction`); Core overrides
  `SCR_WeaponInfo.OnAmmoCountChanged` (HUD-side, `ARMST_WEAPONS_HANDLER.c:74`). No public
  weapon-side invoker.
- Project code (read-only): Core reacts to `Weapon_Rack_Bolt` on the character
  (`ARMST_WEAPONS_HANDLER.c:169`); no project shot observation.

### A.4 Gate verdict
There is **no confirmed weapon-level actual-shot callback** accessible to the existing lab
component. Per the gate, none is invented; no global `modded`, no fire-handler override, and a
fire **animation marker is NOT treated as a shot**. Gathering animation events + ammo/chamber
**deltas** via unchanged existing callbacks does **not** require broader gameplay changes, so a
**limited Phase B** was implemented: `gameplay_shot` is intentionally **not** emitted
(`UNRESOLVED`); a real shot is evidenced by the chamber/muzzle ammo **delta**.

---

## Phase B — passive `[ARMST_T3F-FIRE]` trace (single lab file)

`ARMSTMP133T2A_Diag/Scripts/Game/ARMST_MP133_T2A/ARMST_MP133_T2A_Log.c` — inside the existing
`ARMST_T2A_WeaponAnimationComponent` (**no second gameplay file touched**):

- On **every** delivered `OnAnimationEvent`: one line
  `[ARMST_T3F-FIRE] #n kind=animation_event ev=<name|?> t=<s> srv=<0|1> wpnTag=Wn magTag=Mn ammo=a/m muzzle=a/m barrel=i chNeed=0|1 chPoss=0|1 mzChPoss=0|1`.
- One bounded deferred `kind=snapshot phase=post-enablefire+300ms …` 300 ms after the
  `Weapon_EnableFire` fire indicator (guarded; single pending).
- Event-name resolution via the installed SDK for the known engine weapon events
  (`Weapon_EnableFire`, `BlendIn/Out`, `Weapon_Rack_Bolt`, `Weapon_Spawn/Attach/Detach/DespawnMagazine`,
  `Weapon_MagRelease`); unknown events log `ev=?` (no filename inference; the installed script
  API does not expose `AnimationEventID.ToString`, so the raw id is not printed).
- Independent identity tags (`m_t3f*`) so the T3 trace/tags are not perturbed.
- Bounded: `T3F_EVENT_CAP = 400`; no per-frame logging.
- `kind=command` is **not** duplicated here — it is covered by the unchanged `[ARMST_T2C-CMD]`
  trace (filter includes it). `OnCharacterCommand` is left untouched.
- T2a/T2b markers, T2c trace and T3 `[ARMST_T3-MAG]` snapshots are unchanged; both `super`
  calls preserved; getter-only (`BaseWeaponComponent/BaseMagazineComponent/BaseMuzzleComponent`).

---

## Static checks / scope

- Braces 42/42, parens 298/298, ASCII clean.
- `super.OnAnimationEvent` / `super.OnCharacterCommand` present; `[ARMST_T3-MAG]` and
  `[ARMST_T2C-CMD]` still emitted.
- No disallowed calls: `SetAmmoCount`, `SetMaxAmmoCount`, `Delete`, `SpawnEntity`,
  `CreateEntity`, `SetReloadWeapon`, `ReloadWeapon(`, `AddActionListener`,
  `HandleWeaponReloading`, `HandleWeaponFire`, `Rpc(`, `RpcDo_`, inventory access — all absent.
- Lab script SHA-256: T2c `03AE04C6…`, T3 checkpoint `A66B4CCFABF6100F0B5168ACD42290D6B9E7C0C4E64619A8AEC139D7BE0CB00A`,
  **T3F `E978EDAF373D882EE3F6798D5D0BF41DA264E638B1371E302AD164D982A3339B`**.
- **Compile fix (owner Workbench log):** the first T3F draft failed EnforceScript:
  `…Log.c,412: Formula too complex` + `Incompatible parameter 'wpnTag'`, and
  `…Log.c,431: Undefined function 'AnimationEventID.ToString'`. Fixed by (a) building the state
  string incrementally (`string s = …; s = s + …;`, <= 3 operators per line — the same fix used
  for the V2 C2 trace) and (b) removing the raw-id print (the installed script API has no
  `AnimationEventID.ToString`). The other `SCRIPT (E)` lines in that log
  (`SCR_FactionManagerSerializer`, `SCR_SpawnLogic` Tuple1, `SCR_MapUIElementContainer`,
  `SCR_PlayerArsenalLoadout`, `SCR_ScenarioFramework*`, `SCR_SpinningWidgetComponent`,
  `SCR_ScenarioUICommon` Tuple2) are base-game/Core-off unrelated, not lab-owned.
- Unchanged set: 23-file graph/ASI/clip/prefab set **pre == post**; frozen V2 graph/ASI hashes
  unchanged; Weapons dirty ≈ 29, Core dirty ≈ 4.

---

## Owner run (one session, three labelled scenarios)

1. Loadout: base + `ARMST-PLATFORM---Weapons` + `ARMSTMP133T2A_Diag`; Core and V2/P2 OFF.
2. Recompile `Game` (lab script changed; rdb removed). Equip the diagnostic `MP-133 [T2A-DIAG]`.
3. Note initial ammo, `muzzle/chamber` and current magazine tag (from a first `[ARMST_T3-MAG]`).
4. **Scenario 1 — one shot:** fire once, wait for settling. Capture.
5. **Scenario 2 — rack without firing:** one manual rack, no shot. Capture.
6. **Scenario 3 — dry trigger on empty:** trigger pull with an empty weapon (if safely
   reachable). Capture.
7. Keep the three actions labelled/separate; **no native magazine exchange** during the test.
8. Send the full log filtered by `[ARMST_T3F-FIRE]`, `[ARMST_T3-MAG]`, `[ARMST_T2C-CMD]`.

## Read-out / acceptance

- Counts for **animation events** (per scenario, from `[ARMST_T3F-FIRE]`), **commands**
  (`[ARMST_T2C-CMD]`), and **ammo/chamber deltas** (`muzzle`/`ammo` in the T3F/T3 lines),
  reported separately.
- A real shot is claimed only if the **chamber/muzzle ammo decreases** in Scenario 1 and does
  **not** in Scenario 2/3; `muzzle` is an aggregate and may exceed mag max (T3 observed
  `11/10`), so do not read capacity from it. The magazine owning-entity tag (W/M) should be
  **unchanged** within a scenario.
- `gameplay_shot` remains **UNRESOLVED** (no callback); no `SHOT_CONFIRMED` tally is produced.
- Event→mutation causality stays **UNRESOLVED** unless the snapshots support it.

## STOP / follow-up

One owner run; then STOP for review. If an actual-shot callback is required later, it needs a
**separate approval** for a lab-prefab muzzle-effect subclass (or `SCR_MuzzleEffectComponent.GetOnWeaponFired()`
subscription if that component is present) — not a global hook, and not a Fire-clip keyframe edit.
T4 one-shell transfer, per-shell loop/graph, input interception and MP logic remain separate
and **not authorised** here.

## Integrity

Only the local lab script changed (no remote). Knowledge repo holds this report + minimal
index/sync pointers. Production/Core/V2 untouched.
