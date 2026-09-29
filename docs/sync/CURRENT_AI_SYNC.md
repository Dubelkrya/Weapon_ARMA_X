# CURRENT_AI_SYNC.md — handoff state for AI/local-agent sessions

**Purpose:** a single short file that tells the next session what is true right
now, what was just done, and what must not be repeated or assumed. It is a
*state* file, not a policy file — policy lives in
[`../../AGENTS.md`](../../AGENTS.md).

**Last updated:** 2026-09-29

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
| Live addon | `test_weapon` | `965edc5671e47221d277830439ab906342899348` |
| Live addon `main` | frozen | `8d234c3c3e6430b596fcd5bf9bb35aac7df2bff4` |
| Tools repo | `agent/local-worktree-snapshot-2026-09-25` | `06f69a8355f5147692e4a4741159c5e456a9b991` |

`main` in the live addon is **frozen** — do not commit to it.

## 4. Live addon state — preserve this

The live addon carries **uncommitted user work**. It is not cleanup material and
must not be reverted, stashed, or reset:

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
| `Assets/addons/Dovetail/Data/Collimator_dot_A.edds.meta` | untracked |
| `Assets/addons/Dovetail/Data/DefaultMaterial_A.edds` | untracked |
| `Assets/addons/Dovetail/Data/DefaultMaterial_A.edds.meta` | untracked |
| `Assets/addons/Dovetail/Data/collimat.emat` | untracked |
| `Assets/addons/Dovetail/Data/collimat.emat.meta` | untracked |

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

## 7. Do not repeat

- Do not "fix" the min/max-Z audit claim on Groza; the earlier claim was
  mathematically false and the rebuild is correct.
- Do not re-run a full audit to rediscover §6. It is recorded.
- Do not treat an inherited context as a missing one.
- Do not add a `BulletInitSpeedCoef` override to Groza.
- Do not invent muzzle coordinates or sight pivots.

## 8. State of this repository

- `AGENTS.md` — the 14 startup rules. Read first, every session.
- `artifacts/` — git-ignored scratch output.
- `docs/guides/` — authoring guides (RU), migrated from the addon's `docs/`.
- `reports/live-addon/`, `tools/live-addon/` — imported verbatim from the
  addon's former `agent/` directory. See `reports/live-addon/README.md` for
  provenance and the caveat that these tools still carry their original
  hardcoded paths.

## 9. Session start checklist

1. Read [`../../AGENTS.md`](../../AGENTS.md).
2. Read this file.
3. `python agent/scripts/addon_path.py` — confirm the addon resolves.
4. `git -C <addon> status --short` — confirm the user's dirt in §4 is still there.
5. Confirm the branch you are on is the one you are authorised to change.
