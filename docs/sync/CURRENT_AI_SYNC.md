# CURRENT_AI_SYNC.md — handoff state for AI/local-agent sessions

**Purpose:** a single short file that tells the next session what is true right
now, what was just done, and what must not be repeated or assumed. It is a
*state* file, not a policy file — policy lives in
[`../../AGENTS.md`](../../AGENTS.md).

**Last updated:** 2026-10-03

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

The live addon is on `main` and its working tree is **clean**. `test_weapon`
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
- **Next:** V3 Stage 1 requires the owner to prove the clean native baseline
  (`shot → short R pump → shot` ×3, hold-R inspection, tube/chamber baseline). Until
  proven, report `BASELINE_RUNTIME_REQUIRED` and do **not** implement. Owner reports
  pumps work with lab OFF but has not yet stated the exact 3-shot/hold-R result →
  `V3_CLEAN_BASELINE_PARTIALLY_CONFIRMED`. Optional owner diagnostics P1–P5
  (see V3.1 report) localize the cause.

