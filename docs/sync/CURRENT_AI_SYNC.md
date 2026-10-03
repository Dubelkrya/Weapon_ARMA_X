# CURRENT_AI_SYNC.md — handoff state for AI/local-agent sessions

**Purpose:** a single short file that tells the next session what is true right
now, what was just done, and what must not be repeated or assumed. It is a
*state* file, not a policy file — policy lives in
[`../../AGENTS.md`](../../AGENTS.md).

**Last updated:** 2026-10-03

---

## CURRENT BRANCH-RECONCILIATION NOTICE (2026-10-03, supersedes historical resume instructions)

**Owner-confirmed MP-133 state:** G2 T4b offline trial succeeded: one synthetic `+1` remains in the SAME installed M1 magazine, native manual short-R chambers the round, and the owner reports firing once. The earlier `G0 recompile pending` / `T4a owner run required` statuses are historical and are **not** the current next task. No projectile damage or multiplayer claims.

**Active G3 work:** G3-A read-only report is published on [`t4b/installed-mag-probe`](https://github.com/Dubelkrya/Weapon_ARMA_X/blob/t4b/installed-mag-probe/reports/MP133_V3_G3_REAL_DONOR_PHASE_A.md). G3-B1 **lab source is now published** on that SAME branch at [`a165e80`](https://github.com/Dubelkrya/Weapon_ARMA_X/commit/a165e804df1e571c58806bb39ea74e5eee993191), awaiting independent source review and **owner-only Workbench/game test**. B1 decrements ONE disposable inventory donor only; installed target/chamber untouched. G3-B2 two-sided transfer and G4/G5 are NOT authorised. Use the **existing single T4b local addon**, with separate named experiment fixtures inside it only as needed; no extra T4c addon or branch. The original T4b script SHA256 remains `D581B9C9EE270725FFEC94C7685CBBCB2AB41DBA717F2B4FBCF8C4AC8DDCBEB1`; its weapon prefab was re-saved by the **owner** at `a165e80` and must not be silently reverted.

**Core correction:** per owner, the Core SHIFT+R reload does **not work**; its legacy input references must NOT be used as a functioning requirement. A local Core read-only audit/report remains unpublished ([#33](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/33)); a reported RPC repacking mechanism is a candidate requiring verification and does not prove an installed-magazine transfer.

**Coordination:** PR [#31](https://github.com/Dubelkrya/Weapon_ARMA_X/pull/31) is documentation-only and must be reconciled against the active `t4b/installed-mag-probe` branch before any merge. Catalog #28 and CI #29 have completed source-backed publication and [green hosted CI](https://github.com/Dubelkrya/Weapon_ARMA_X/actions/runs/37135291162). Astra and original T2a/T4a/V2/P2 remain inactive; production Weapons/Core, owner worlds/layers and untracked files remain protected.

---

## 0. Historical checkpoint (superseded where different from notice above) — read before historical sections

**Date:** 2026-10-03; last verified knowledge-repo `main` before reconciliation:
[`bcf3ab4`](https://github.com/Dubelkrya/Weapon_ARMA_X/commit/bcf3ab41c5aec230ae3a5333ed1ca40678e51d30). Recheck current `origin/main` and local addon state at every new session. The history in §§10–11 includes older `OWNER_RUN_REQUIRED` and `PUBLICATION_BLOCKED` statements; the **later evidence below supersedes those historical checkpoints**.

- **MP-133 T2b/T2c/T3:** paired markers and native command routing observed; T3 owner runtime proved physical **whole-magazine replacement** (`M1 → null → M3`, `M3 → null → M5`). See [`MP133_INDEX.md`](../../reports/MP133_INDEX.md) and [Issue #27](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27).
- **T3F:** owner ran the **corrected** T3F diagnostic after commit `99c1819`. Owner log: 100 `[ARMST_T3F-FIRE]`, 77 `[ARMST_T3-MAG]`, 18 `[ARMST_T2C-CMD]`, no `SCRIPT (E)`. Independent gameplay-shot callback and isolated controls **unresolved**. `Weapon_EnableFire` enables firing during bolt/reload animation; it is **not** a shot event. [Runtime read-out](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5970720618). Do not ask for a rerun merely to prove the passive logger runs.
- **T4:** Phase A remains `T4_API_OR_TRANSACTION_BLOCKED` for an actual donor→installed-mag transfer. **T4a:** primary agent prepared isolated `ARMSTMP133T4A_SetProbe` (GUID `A7C41E90D3B24F68`) for a *disposable, non-installed* magazine `SetAmmoCount(+1)` action (default key P); [report](../../reports/MP133_V3_T4A_SETAMMOCOUNT_SEMANTICS.md). **`T4A_LAB_PREPARED_OWNER_RUN_REQUIRED`**: statically checked by agent, only the **owner** can compile/run in Workbench/game. No donor transfer, installed-mag test or MP claim.
- **Astra graph/animation lab:** `ASTRA_GRAPH_ANIM_PAUSED_OWNER_LIMIT` by owner's decision. The `astra_build.py` generator is unverified, locally WIP and **not archived as a working prototype**. Do not execute or modify its worktree until explicitly resumed. [Pause checkpoint](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5970888887).
- **Catalog #28:** reviewed canonical 181-entity rescan **published** in commit `5c443a9` after classifying fixes; the earlier §11 `PUBLICATION_BLOCKED` stage is historical. **CI #29:** hosted validation succeeded; [latest run for `7101fd6`](https://github.com/Dubelkrya/Weapon_ARMA_X/actions/runs/37135291162) is successful. A successful CI does not validate local gameplay.
- **Lab inventory and source archival:** [`MP133_LAB_REGISTRY.md`](../../reports/MP133_LAB_REGISTRY.md). Use [`EXPERIMENT_HANDOFF_TEMPLATE.md`](../guides/EXPERIMENT_HANDOFF_TEMPLATE.md) for future phase reports, clearly separating static, owner-runtime, MP-unverified and blocked status.

**Historical resume point (superseded):** T4a was prepared as a separate disposable-magazine probe. The current execution point is the G3-B1 source review and owner-run test in the existing T4b addon, as set out at the top of this document.

---

## 1. Layout

| Role | Location |
|---|---|
| Live addon (source of truth) | `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons` |
| Tools repo (this) | `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\Weapon_ARMA_X` |

These are two **separate Git roots with separate remotes**. `git mv` cannot move
a file between them; use copy → verify SHA256 → delete.

- Live addon remote: `https://github.com/romzet/ARMST-PLATFORM---Weapons.git`
- Tools repo remote: `https://github.com/Dubelkrya/Weapon_ARMA_X.git`

Do not turn the addon into a junction or symlink to this repo. Do not copy
mod resources into this repo. The addon stays a real, independent project.

## 2. Resolving the addon

```powershell
python agent/scripts/addon_path.py
```

Order: `ARMST_WEAPONS_ADDON_PATH` → legacy `MOD_ROOT` →
`addon_path.local.json` → built-in default. A candidate must have
`addon.gproj`, `Prefabs/`, and an `addon.gproj` `ID` of `ARMSTPLATFORMWeapons`.

An explicitly configured but invalid path is a **hard error** with no fallback.
Seven sibling addons (`ARMST-PLATFORM---Core`, `---MO-Furnitures`,
`---MO-Vehicles`, `---Core` variants, `ARMST_RangeScanner`, `Armst_Work`,
`Arm_Structura`) pass the structural check, so identity matters.
Set `ARMST_WEAPONS_ALLOW_ANY_ADDON=1` only for a genuine fork.

## 3. Current Git state (as of this update)

| Repo | Branch | HEAD |
|---|---|---|
| Live addon | `main` | `6ec5015f572720223789cd82c4e3232097f11b99` |
| Tools repo | `main` | see `git log` |

At the recorded 2026-09-29 checkpoint the live addon was on `main` with a **clean** working tree. Its current local worktree has **not** been rechecked by this documentation update. `test_weapon`
was fully promoted to `main` and then deleted, locally and remotely; it must not
be recreated automatically. Normal addon development happens directly on
`main`. Do not create feature branches unless the user explicitly asks.

The checkpoint SHA above is a point-in-time marker, not a permanent expected
HEAD — future `main` commits will advance it. Re-read it with
`git -C <addon> rev-parse HEAD` rather than trusting this line.

### Branch history (for provenance only)

| SHA | Meaning |
|---|---|
| `8d234c3` | previously frozen `main`; fast-forwarded to the `test_weapon` tip |
| `80dcbde` | artifact cleanup landed here |
| `6ec5015` | the 13 previously-uncommitted user files committed by the user |

## 4. Live addon state — preserve this

The work that was uncommitted at the time of the cleanup has since been
committed by the user as `6ec5015`. It is now part of `main`:

| File | Note |
|---|---|
| `Assets/addons/Dovetail/coll.fbx` | re-exported collider source |
| `Assets/addons/Dovetail/coll.txo` | re-exported collider |
| `Assets/addons/Dovetail/coll.xob` | re-exported; still exports no geometry |
| `Assets/addons/Dovetail/coll.xob.meta` | meta for the above |
| `Prefabs/.../Optics/armst_Optic_Collimator.et` | sight/reticle data added |
| `Prefabs/.../Groza/armst_Rifle_Groza_base.et` | post-rebuild tuning |
| `resourceDatabase.rdb` | Workbench-generated |
| `worlds/Weapon_test/weapon_test_Layers/default.layer` | **never touch** |
| `Assets/addons/Dovetail/Data/Collimator_dot_A.edds.meta` | added in `6ec5015` |
| `Assets/addons/Dovetail/Data/DefaultMaterial_A.edds` | added in `6ec5015` |
| `Assets/addons/Dovetail/Data/DefaultMaterial_A.edds.meta` | added in `6ec5015` |
| `Assets/addons/Dovetail/Data/collimat.emat` | added in `6ec5015` |
| `Assets/addons/Dovetail/Data/collimat.emat.meta` | added in `6ec5015` |

These are committed, but they are still the user's authored work. Do not revert,
reset or "tidy" them. The general rule stands regardless of commit status: never
automatically `stash`, `reset`, `restore`, `clean` or discard dirty Workbench
files, and preserve `.meta` and GUID identity.

## 5. Completed work

**OTs-14 Groza prefab rebuild.** Rebuilt on the AK74 short-base inheritance
chain rather than the previous, structurally broken base. ARMST GUIDs preserved.
Committed `965edc5`, pushed `c2421a6..965edc5`.

**Weapon/optic contextual-interaction audit (read-only).** Vanilla architecture
is asymmetric: the optic supplies the action
(`SCR_AttachItemFromInventoryAction` + `ParentContextList { "optic" }` on
`WeaponOptic_Base`/`WeaponCollimator_Base`) and the **weapon** must supply a
`UserActionContext` with `ContextName "optic"`. Vanilla `Weapon_Base`,
`Rifle_Base` and `AK74_base` declare no `ContextName`. Result:
6 weapons with a missing optic context, 1 case-mismatch (`"Optic"`), 1 unnamed
context, 1 physics-blocked optic. `GAMEPLAY_FILES_CHANGED=0`.

**Artifact cleanup (2026-09-29).** 312 dev/agent files moved out of the live
addon: 308 from `agent/` and 4 authoring guides from `docs/`.
`GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0`, `META_FILES_CHANGED=0`,
`GUID_CHANGES=0`, `UNKNOWN_FILES_REQUIRING_REVIEW=0`. The addon path itself is
unchanged.

## 6. Open issues — do not re-derive

- **Optic context names.** VSS, 9A91, AKM, AK105 and L85 optics slots need a
  local `{ ContextName "optic" }`. `VAL` uses `"Optic"` and must be lowercase.
  SOC94's context has `PivotID "slot_optics"` but no `ContextName`.
- **AKM muzzle pivot.** AKM context `{65AE4CB5E23C0CE9}` is named `bayonet` and
  pivots to `slot_barrel_muzzle`, which is absent from
  `akm_weapons_nonstock.xob`.
- **Collimator physics.** `coll.xob` exports no geometry, so the inherited
  `RigidBody { ModelGeometry 1 }` cannot build physics. Aiming works;
  world-item/pickup interaction does not. Re-exporting the collider did not fix
  it.
- **Unresolved by design.** `armst_Handgun_Knife_base.et` contexts are
  `UNRESOLVED` (effective model is vanilla `Bayonet_6Kh4.xob`, not on disk).
  `armst_Rifle_AK74N.et` references a `slot_optics` with no model on disk.
  These are honest gaps, not tasks to guess at.
- **Stale generated catalog (2026-09-29, found during the main merge).** The
  addon reorganised prefab paths (`Prefabs/Weapons/Rifles/…` →
  `Prefabs/Weapons/Russian/Rifle/…`, `Western/Rifle/…`). The generated
  `catalog/**/*.json` on **both** merge sides still reference the old
  `Prefabs/Weapons/Rifles/` paths, which no longer exist in the addon — the
  directory itself is gone. Roughly 1455 stale references remain. During the
  merge, `origin/main`'s version was kept for the 9 entities it had already
  rescanned, because it was the more current of the two.
  **The real fix is to regenerate** `catalog/`, `indexes/`, `reports/` and
  `schema/` with `python agent/scripts/scan_build.py`, which now resolves the
  external addon via `addon_path.py`. This has deliberately *not* been done yet
  — it rewrites generated data and deserves its own reviewed commit. Do not
  hand-edit the JSON to chase paths.

## 7. Do not repeat

- Do not "fix" the min/max-Z audit claim on Groza; the earlier claim was
  mathematically false and the rebuild is correct.
- Do not re-run a full audit to rediscover §6. It is recorded.
- Do not treat an inherited context as a missing one.
- Do not add a `BulletInitSpeedCoef` override to Groza.
- Do not invent muzzle coordinates or sight pivots.

## 8. State of this repository

- `AGENTS.md` — the startup rules. Read first, every session.
- `artifacts/` — git-ignored scratch output.
- `docs/guides/` — authoring guides (RU), migrated from the addon's `docs/`.
- `reports/live-addon/`, `tools/live-addon/` — imported verbatim from the
  addon's former `agent/` directory. See `reports/live-addon/README.md` for
  provenance and the caveat that these tools still carry their original
  hardcoded paths.
- `catalog/` — generated per-entity JSON *plus* the imported vanilla reference
  corpus (`catalog/**/*.et|.conf|.meta`). The corpus is intentional reference
  material and must survive any rescan; `clean_generated_outputs()` exists to
  guarantee exactly that.
- `reports/MP133_INDEX.md` — current MP-133 V3 status and categorized V1/V2 history.

## 9. Session start checklist

1. Read [`../../AGENTS.md`](../../AGENTS.md).
2. Read this file.
3. `python agent/scripts/addon_path.py` — confirm the addon resolves.
4. `git -C <addon> status --short` — confirm the user's dirt in §4 is still there.
5. Confirm the branch you are on is the one you are authorised to change.

---

## 10. MP-133 AnimationLab — frozen, backup, and V3 direction (2026-10-03)

`ARMST_MP133_AnimationLab` is a **separate local addon** under `addons\` with **no Git
remote** (rules: do not push its sources to GitHub). Its V2.x state is **frozen
historical material**; the owner approved **V3** (Issue #27 comment 5966570978,
`V3_DESIGN_APPROVED; CLEAN_BASELINE_RUNTIME_GATE_PENDING`).

- **Pre-restore backup (outside the restored tree):**
  `C:\Users\yshky\Documents\MP133_Lab_Backups\MP133_Lab_Backup_20261003-002026\`
  — full `lab_addon\` (30 files) + git-ignored `artifacts\MP133_Lab` + copies of lab
  knowledge files; `MANIFEST.sha256` (54 files) verified 0 mismatches.
  Restore guide: `reports/MP133_LAB_RESTORE_INSTRUCTIONS.md`.
- **Critical known state:** the old lab addon globally broke ordinary R on **all**
  pump-action shotguns. **I1 (owner A/B):** lab ON → all pumps fail; lab OFF → work.
  **P2 (owner runtime, comment 5966964438):** with only
  `Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_CommandHandler.c` excluded, ordinary R
  works again →
  `P2_R_RESTORED / LEGACY_HANDLER_IMPLICATED / V3_STAGE1_PENDING`. The cause is bounded
  to the presence/behavior of the global `modded SCR_CharacterCommandHandlerComponent`,
  but the exact mechanism is **unknown** (do not assert `super` vs `...Default`; P3
  withdrawn). P2 is OFF for the clean baseline; P3/P4/P5 not required. Details:
  `reports/MP133_V3_1_I1_LAB_INTERFERENCE_INVENTORY.md`,
  `reports/MP133_ANIMATION_LAB_E0_ISOLATION_PLAN.md`.
- **Git state at freeze:** knowledge `main` at `4be4d42`; Weapons `main` `b88bc53`
  (dirty anim `.meta`/SPAS-12 per restore); Core `main` `08cb1f38` (dirty weather/rdb).
- **Controls decided:** ordinary R = native manual cycle (keep); hold R = native
  inspection; LSHIFT+R = existing Core action (unchanged/frozen). J-held loading is
  **cancelled** by V3.
- **Discontinued:** E1–E4, Core suppression, native mag-swap reintroduction, V2.x
  insert gate. Both `m_bLabInsertEnabled` gates are OFF.
- **Owner animation-event finding (V3.2, comment 5967161341):** the lab P/W insert
  clips were re-imported (2026-10-02 20:34) with **vanilla** events
  `Weapon_SpawnMagazine(10)/Weapon_AttachMagazine(43)/Weapon_MagRelease(64)` replacing
  `ARMST_Lab_Shell_Spawn/Commit/Release`; the `.txa` sources are stale. Owner reports the
  chamber insert "began working" — an independent finding from P2. With vanilla events
  the **engine** (not the lab script) receives them, and the lab scripted commit no
  longer fires; mag identity / ammo conservation are unverified. Current lab ASI maps
  InsertMag to the lab clip, while the owner described the production clip — confirm.
  See `reports/MP133_V3_2_ANIM_EVENT_FINDING.md`.

- **T0 owner clean functional result (comments 5967858916 / 5967911774):** the
  owner tested the original MP-133 with only the Weapons addon loaded, no V2/P2
  laboratory or Core. Three consecutive actual shots with short-R manual pumps
  succeeded; 10-round magazine ammunition depleted; hold R performed inspection.
  Status: `T0_CLEAN_FUNCTIONAL_PASS / PHYSICAL_MAG_ENTITY_IDENTITY_NOT_INSTRUMENTED`.
  Detailed final-round telemetry and stable physical magazine *entity* identity were
  not measured, so do not claim full system-level proof. Do not needlessly repeat
  the completed three-shot functional test.
- **T1/T2 READ-ONLY DESIGN PUBLISHED (commit 7d645f3, Issue #27):**
  `reports/MP133_V3_T0_T1_T2_DESIGN.md` provides input-routing and
  animation-event-routing experiments and STOP criteria.
- **T2a lab PREPARED (local, isolated; commit for the plan/report under reports/):**
  `addons\ARMSTMP133T2A_Diag` — ID `ARMSTMP133T2ADiag`, root GUID `AF1464F772CC998F`,
  deps base `58D0FB3206B6F859` + Weapons `6A70E400C54051DC` (**no Core**). Cloned MP-133
  graph/ASI with fresh GUIDs; unique player-only marker `ARMST_T2A_PM_C41F7A29` at frame
  12 of `T2AClips/P_MP133_T2A_Bolt.txa`; logging-only script (weapon
  `WeaponAnimationComponent.OnAnimationEvent` + character `GetOnAnimationEvent`; no
  R/reload/ammo). Static checks PASS; marker absent from `MP133_T2A_weapon.asi`.
  Status `T2A_ROUTE_OBSERVED / BRIDGE_DESIGN_AUTHORIZED_ONLY`. **Run 2 (owner):**
  diagnostic prefab `{5FB844730BED8BD1}` equipped, `hasT2AWpnComp=1`; weapon callback
  received `BlendIn`/`Weapon_EnableFire`/`Weapon_Rack_Bolt`; character invoker received 4
  markers (`isServer=1`) but **no weapon-side marker** → the player event is not
  auto-forwarded to the weapon component. Bridge design (owner review before
  implementation): `reports/MP133_V3_EVENT_BRIDGE_DESIGN.md` (explicit char observer →
  resolve equipped lab MP-133 → call a dedicated weapon method; token dedupe;
  weapon-switch/interrupt/MP handling; weapon-side-marker alternative; dependency check).
  Run 1 (marker ANM `{3581B839F53FC345}` wired): `[ARMST_T2A-CHR]` fired ×6
  (t≈0/0.0333, `isServer=1`); **no** `[ARMST_T2A-WPN]`; diagnostic prefab load not
  confirmed. v2 lab-only diagnostic added: weapon-side generic event trace + MARKER,
  one-shot subscription guard + `init #n`, and a 1 Hz
  `weapon prefab=… hasT2AWpnComp=0|1` confirmation (subclass assignment check). Report:
  `reports/MP133_V3_T2A_LAB_PREP.md`.
- **T2b (owner change of direction; BRIDGE PAUSED):** add a weapon-only marker
  `ARMST_T2B_WM_6E28B9A4` to a lab copy of the weapon `ReloadActionBolt` clip (native
  events preserved; frame 12 = equivalent phase), keep the player marker, and compare
  both on both receivers during short-R racks. Lab `.txa` prepared:
  `Assets/Weapons_RUS/Mp_133/T2A/T2AClips/W_MP133_T2B_Bolt.txa`; script logs both markers
  on both sides. Awaiting owner import (`W_MP133_T2B_Bolt.anm` GUID), then the agent
  repoints the cloned `MP133_T2A_weapon.asi` `ReloadActionBolt` rows. Report:
  `reports/MP133_V3_T2B_WEAPON_MARKER_PREP.md`. **Owner imported the weapon clip**
  (`W_MP133_T2B_Bolt.anm` = `{0C775A2108B6D5AD}Assets/Weapons_RUS/Mp_133/T2A/T2AClips/W_MP133_T2B_Bolt.anm`)
  but the import was **empty (44 B)** because the first lab `.txa` carried a UTF-8 BOM;
  the agent rebuilt the `.txa` byte-identically to production (no BOM, CRLF) with only the
  marker line added, removed the empty `.anm`, kept the `.anm.meta` (GUID preserved), and
  repointed only `Reload.Erc/Pne.ReloadActionBolt` in the cloned weapon ASI (new ANM 2×,
  production bolt 0×, other rows unchanged, `.meta` GUID consistent, stale rdb removed).
  Status `BRIDGE_PAUSED / T2B_TXA_REBUILT_NO_BOM; AWAITING_OWNER_REIMPORT`.
- **Next:** owner re-imports `W_MP133_T2B_Bolt.txa` (confirm non-trivial `.anm` +
  `ReloadActionBolt` green), then equips `MP-133 [T2A-DIAG]` and runs several short-R racks;
  the agent compares marker order/count/time on both receivers. Preserve the native pump and
  owner-authored assets. No bridge, T2c, or per-shell implementation until T2b results.
- **T3 insert-event AUDIT (read-only, 2026-10-03):** `MP133_V3_INSERT_EVENT_AUDIT.md`.
  `Reload_InsertMag` (107f@30) carries `Weapon_SpawnMagazine(10)/Weapon_AttachMagazine(43)/
  Weapon_MagRelease(64)`; remove carries `MagRelease(6)/DetachMagazine(10)/DespawnMagazine(15)`.
  These are all engine **whole-magazine** operations — there is **no native per-shell insert**
  (the engine's single-projectile `CMD_Weapon_Reload=7` is excluded by `MP133.agf`, 7–9).
  The MP-133 "tube" is a detachable 10-round `MagazineWell12g` (`armst_12ga_Buckshot`).
  Restoring the native events "made the insert work" only by letting the engine attach a full
  magazine (V2: `3/3 → 10/10`), so mag identity/ammo are not preserved. One **logging-only T3
  probe** proposed (attribute the mag/ammo change to a specific event; measure physical mag
  survival). Status `INSERT_EVENT_AUDIT_DONE; ONE_MINIMAL_TEST_PROPOSED; NOT_RUN`.
- **Reload-graph READ-ONLY AUDIT (2026-10-03):** `MP133_V3_RELOAD_GRAPH_AUDIT.md`. Production
  and T2A graph logic proven **identical** (`.agf` GUID-normalized line-identical 1066 lines;
  `.ast` identical; ASIs differ only in `ReloadActionBolt` marker clips). Complete
  `IdleReloadSTM`/`WeaponReloadStanceSTM`/`WeaponReloadSTM`/`MagReloadSTM` state map with exact
  conditions: cmd 1→`ReloadActionBolt`, 2/3→`Reload_InsertMag`, 4/5→remove+insert,
  6→`Reload_RemoveMag`, **7–9 excluded/no state**. Frozen V2 lab had a `InsertSingleProjectile`
  (cmd 7) self-loop on `BlendOut` (historical pattern). One minimal next gate proposed: a
  passive lab-only `OnCharacterCommand` trace to establish the actual command ids.
  `GAMEPLAY_FILES_CHANGED_BY_AUDIT=0`; status
  `RELOAD_GRAPH_READONLY_AUDIT_DONE / T3_RUNTIME_NOT_RUN`.
- **T2c command trace (lab-only, 2026-10-03):** `MP133_V3_T2C_COMMAND_TRACE.md`. Added a
  passive `OnCharacterCommand(int commandID, int intValue, float floatValue)` override
  (super always called) to `ARMST_T2A_WeaponAnimationComponent`, logging
  `[ARMST_T2C-CMD] #n commandID=.. intValue=.. floatValue=.. srv=.. wep=..`. Compatibility
  verified against the **installed** SDK docs
  (`…\Arma Reforger Tools\Workbench\docs\ArmaReforgerScriptAPIPublic`, 2026-09-19), not the
  online 1.13.2 pages. No input/graph/ASI/clip/ammo change; static PASS; rdb removed. Owner
  run required (one ordinary short R + one stock magazine reload). Status
  `T2C_LOGGING_ADDED; OWNER_RUN_REQUIRED`.
- **Owner correction (comment 5970274540):** `CMD_Weapon_Reload` **10** is not vetoed by the
  `IdleReloadSTM` entry (`inRange(…,7,9)` excludes 7–9 only); 10 passes entry but
  `WeaponReloadSTM` defines no state for it. `MP133_V3_RELOAD_GRAPH_AUDIT.md` amended.
- **T2c OWNER-PASS / native mag exchange confirmed:** `commandID=0,intValue=1` on rack,
  `commandID=0,intValue=5` on the stock remove+insert+bolt path; owner's 3-round test showed a
  **separate full magazine** installed (HUD 10) and the old **partly depleted** magazine
  returned to inventory still partial → real whole-magazine exchange, not a refill. V3
  per-shell loading must operate on the **already-installed** magazine.
- **T3 passive identity trace (lab-only, 2026-10-03):** `MP133_V3_T3_MAG_IDENTITY_TRACE.md`.
  Added `[ARMST_T3-MAG]` getter-only snapshots (magazine/weapon entity **reference tags**,
  `GetAmmoCount/GetMaxAmmoCount`, muzzle/barrel/chamber) at baseline/pre-super/post-super and a
  delayed final after `BlendOut`, in the existing `OnAnimationEvent`; targeted logging uncapped.
  Only one file changed; production/Core/V2/graph/ASI/clip/prefab unchanged; static PASS.
  Owner run required: one native R magazine swap with 7/10 old + known 10/10 inventory mag.
  Status `T2C_OWNER_PASS / NATIVE_MAG_EXCHANGE_OWNER_CONFIRMED / T3_LOGGING_ADDED; OWNER_RUN_REQUIRED`.
- **T3 OWNER RUNTIME read-out (comment 5970509383):** 73 `[ARMST_T3-MAG]` snapshots; native
  magazine lifecycle events **ARE delivered** weapon-side; installed owning-entity references
  change `M1 → null → M3` (and `M3 → null → M5`); the new magazine appears **between** the
  post-super `Weapon_AttachMagazine` snapshot and the next pre-super `Weapon_MagRelease`; old
  mag stays partial until detach; `muzzle` is an aggregate (can read `11/10`). Status
  `T3_RUNTIME_MAG_EXCHANGE_CONFIRMED; EVENT_DELIVERY_CONFIRMED; PRECISE_NATIVE_ATTACH_TIMING_UNRESOLVED`.
- **T3F (lab-only, 2026-10-03):** `MP133_V3_T3F_FIRE_EVENT_AUDIT.md`. Phase A: fire path
  (`Reload.Erc.Fire`/`Trigger` → base-game AK74 clips; graph `FireAnim`/`FireEmptyAnim` on `Firing`/`Empty`)
  and installed-SDK callback audit → **no weapon-level actual-shot callback**; real-shot
  signals are muzzle-effect `OnFired`/`OnWeaponFired` (prefab subclass / global, out of scope).
  Phase B limited: `[ARMST_T3F-FIRE]` logs every `OnAnimationEvent` + inline mag/muzzle/chamber
  sample + one deferred snapshot after `Weapon_EnableFire`; `gameplay_shot` NOT emitted (shot
  evidenced by ammo delta). Single lab file changed (SHA T3 `A66B4CCF…` → T3F `E978EDAF…`; first
  draft failed compile — split formatter + dropped the unsupported `AnimationEventID.ToString`); no
  clip/graph/ASI edits; 23-file asset set unchanged; static PASS. Owner run required (3 scenarios).
  Historical checkpoint; **superseded** by the corrected-script owner-runtime observation in §0.
- **T4 Phase A (read-only, 2026-10-03):** `MP133_V3_T4_ONE_SHELL_TRANSFER.md`. Installed SDK:
  the only magazine-ammo writer is `BaseMagazineComponent.SetAmmoCount(int)`; **no** atomic
  transfer, no legitimate donor-consumption API, inventory APIs are item-level, muzzle has only
  `ClearChamber`; `SetAmmoCount` authority/replication/rollback UNRESOLVED. Per the Phase A HARD
  STOP no isolated T4 lab was created → **`T4_API_OR_TRANSACTION_BLOCKED`**; one minimal next
  experiment (throwaway-mag `SetAmmoCount` runtime probe, or explicit owner authorisation of a
  local setter-based PoC) proposed. Production/Core/T2A/V2/Astra untouched. **Later owner decision and preparation:** only the separate disposable-magazine **T4a** experiment is authorised and statically prepared (see §0); the real T4 transfer remains blocked.

---

- **T4a (isolated lab, 2026-10-03; primary agent's later main commit `bcf3ab4`):**
  [`MP133_V3_T4A_SETAMMOCOUNT_SEMANTICS.md`](../../reports/MP133_V3_T4A_SETAMMOCOUNT_SEMANTICS.md).
  New addon `ARMSTMP133T4A_SetProbe` (ID `ARMSTMP133T4ASetProbe`, GUID
  `A7C41E90D3B24F68`, deps base+Weapons) with a disposable
  `ARMST_T4A_TestMagazine.et` and `ARMST_T4A_SETTER_ACTION` (default P).
  It logs one guarded `SetAmmoCount(+1)` and refuses repeated/full operations.
  Agent static checks only; no agent Workbench/game. **`T4A_LAB_PREPARED_OWNER_RUN_REQUIRED`.**
  No donor, installed-mag or chamber changes, no real transfer; Astra remains paused.

## 11. CI (#29) and catalog rescan (#28) — 2026-10-03

- **#29 (priority):** root cause = `agent/scripts/scan_build.py` resolves the live addon
  at **import** (SystemExit) + `test_mp133_lab_validation.py` needs the local lab/original
  addon in `setUp`. **Implemented (approved correction):** lazy `resolve_mod_root()` in
  `scan_build.py`; `validate_mp133_lab` gained injectable `resolve_*` + a
  `local_dependency_decision` (`run`/`skip`/`fail`) so an **explicitly configured but
  invalid** path **FAILS** and only implicit absence skips `LOCAL_ONLY`; new offline
  `test_mp133_lab_dependency_gate.py` (7 tests incl. scanner-CLI exit/no-write). Env: use
  `MP133_LAB_ADDON_PATH` + `MP133_ORIGINAL_ADDON_PATH`. Local: 80 OK; isolated hosted
  simulation: 80, 0 failures, 14 skipped. `CI_FIXED` only after fresh hosted CI passes.
  Report: `reports/CI_29_SEPARATE_OFFLINE_AND_LOCAL_TESTS.md`.
- **#28:** Phase A preflight **PASS**; **final candidate preparation done** (isolated).
  GUID crosswalk: 121 deleted → **91 `RELOCATED_OR_RENAMED`** (same GUID), **30
  `SOURCE_ABSENT_AT_HEAD`** (all absent at committed HEAD; 9 unreferenced, 21 only via
  generated `ammo_configs.json` / preserved `reports/live-addon/**`, no live entities);
  0 `SCANNER_COVERAGE_OR_BUG`; internal stale scanner refs 0. MP-133 preserved by GUID
  (`63FF6FDCA4E7E735`); 18 additive leaf changes (deeper base-game resolution; core
  magazine/animation fields unchanged). Dirty worktree vs **committed HEAD** →
  **identical catalog** (181 entities, 0 diff). 149 catalog-changed (106 `data`).
  Two smoke grenades `grenade→weapon` = **scanner `classify()` ordering defect**
  (separate fix). Derived pages regenerated → `--check` exit 0. **Publication BLOCKED**
  pending owner approval of the promotion manifest + the 30-deletion batch. Reports:
  `reports/CATALOG_28_RESCAN_PREFLIGHT.md`, `CATALOG_28_GUID_RECONCILIATION.md`,
  `CATALOG_28_FINAL_PROMOTION_MANIFEST.md`.
- **#28 final (2026-10-03):** scanner `classify()` fixed (grenades before
  WeaponComponent; commit `ca4c870`, tests 8/8, full 82 OK). MP-133←M21 inheritance is
  the pre-existing ARMST chain (no action). 106 `data`-changed reviewed: chiefly resolved
  base-game inheritance; 52 genuine value changes in ammo/mag `AmmoMapping`; flagged odd
  `Assets/Toz/1.et` → `weapons/1.json`. Final isolated candidate: **181 entities** (68
  weapons / 4 grenades), `--check`/data-quality all exit 0, dirty==HEAD. Promotion set
  ready; **published** to `main` as generated-only commit `5c443a94ff0f53b839e7a1909c4f11e382825e47`
  (177 M / 119 D / 30 A; + the approved 9x39 test update). Fresh hosted CI run
  `37119940835`: **`validate` job = success — all steps green** (scanner/parser
  regressions, repository integrity, weapon index/family/balance freshness,
  data-quality). `CI_ALL_CHECKS_PASS`. Frozen input `b88bc53` unchanged; corpus 1404
  SHA `15380703…` preserved. T2a is now unblocked.
