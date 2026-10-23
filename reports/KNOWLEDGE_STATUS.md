# ARMST knowledge status

> [!IMPORTANT]
> **Status: CURRENT / AUTHORITATIVE MAP.** Use this file to resolve source-of-truth, freshness, active-policy and historical-material conflicts.

Canonical status snapshot for authoring knowledge. This file exists to distinguish live project truth, generated snapshots, active policy and archived material.

## Authority order

1. **Current primary local addon / Workbench validation** — authoritative for what actually opens, mounts and behaves correctly in the current project.
2. **Workbench-validated authoring rules** in `reports/PREFAB_AUTHORING_GUIDE.md` — authoritative for safe prefab editing patterns already confirmed in the editor.
3. **Active gameplay policies** such as `indexes/script_reference/optic_compatibility_policy_v2.json`, `reports/OPTICS_COMPATIBILITY_SYSTEM_V2.md` and `reports/AMMO_AP_BP_POLICY.md`.
4. **Generated indexes/catalogs** — source snapshots with provenance; refresh them from the primary addon when that addon changes.
5. **Google Sheets / exported XLSX views** — convenient working views. They must not override newer source-backed Git or Workbench evidence.
6. **Archived / superseded reports** — historical evidence only.

Unknown values remain unknown. Do not fill gaps from filenames or memory.

## Primary project boundary

Authoritative weapon addon root:

`C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`

Normal local-agent editing, prefab/config/script lookup and canonical source scans must target this addon unless the user explicitly names another root for a temporary test.

`C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\Armst_Work`

is a sandbox/test addon only. It must not replace the main weapon catalog, indexes, policies or source-of-truth snapshot.

The checked-in scanner default root already points to `ARMST-PLATFORM---Weapons`; the committed scanner data therefore represents a snapshot of the correct primary addon at the time it was generated. Refresh the snapshot after meaningful changes in the primary addon rather than substituting a partial sandbox scan.

Primary-root policy: `agent/PRIMARY_MOD_POLICY.md`.

## Current authoring policy

### Prefabs

- child local override > nearest parent > family/common base;
- preserve inherited instance IDs;
- child contains only real differences;
- inherited object: override by existing ID only;
- genuinely new object: new instance ID + correct resource parent/config;
- one logical change per validation step;
- structural validation is not Workbench/runtime validation.

Local-agent prefab editing contract: `agent/SAFE_PREFAB_EDITOR.md`.

### Optics

Active gameplay family for approved Russian/Soviet side-rail weapons and optics:

`DovetailRU` → `AttachmentOpticsARMST_DovetailRU`

This is a gameplay compatibility family. Real-world mount compatibility remains separate research data.

Compatibility is two-sided:

- weapon slot: `AttachmentSlotComponent -> AttachmentType`;
- optic/module: `WeaponAttachmentAttributes -> AttachmentType`.

Physical pivot/snap geometry is independent from compatibility type.

Compatibility data shape is documented in `schema/compatibility.schema.json`.

### Nested Dovetail → RIS research checkpoint

Current live-addon research on a **separate-item** AK dovetail adapter → RIS collimator hierarchy is recorded in:

`reports/NESTED_DOVETAIL_RIS_STORAGE_AUDIT_2026-09-21.md`

Important status:

- separate adapter and collimator item identity is a hard requirement for this feature;
- the fixed composite path is therefore not the production target;
- no stock vanilla attachment-host prefab pattern has been found;
- this does **not** prove nested physical attachment is impossible in Enfusion;
- Arma Reforger 1.8.0.13 proves `InventoryStorageSlot : EntitySlotInfo`, physical attach semantics, and protected `SetupSlotHooks` / `ReleaseSlotHooks` on `BaseInventoryStorageComponent`;
- the main unresolved question is custom slot ownership/construction for a one-slot adapter storage;
- the current live experimental adapter path uses `AttachmentOpticsDovetailAK`; older repo `DovetailRU` policy snapshots must not override newer live Workbench evidence for this specific research branch.

Do not create additional Dovetail/Collimator POCs until the slot-ownership/API gate in that report is resolved.

### Config / ammunition

`AmmoResourceArray` is the allowed ammunition set. `AmmoMapping` defines what is actually loaded. Projectile kinetic damage remains separate from tracer/incendiary effects. Use the projectile's actually referenced ballistic table.

The ARMST TT chain is resolved by the later `Configs(1).zip` snapshot: `Ammo_763x25.conf` → `Ammo_763x25_Ball.et`.

Active gameplay design for ammunition roles is documented in `reports/AMMO_AP_BP_POLICY.md`. The project distinguishes a high-damage/low-penetration anti-personnel role (`АП`) from a lower-damage/high-penetration role (`БП`). This is a gameplay classification layer and must remain separate from real-world cartridge designations. Tracer, incendiary, subsonic and precision remain secondary tags rather than replacing the primary role.

The first Workbench validation targets are 9×39 and 5.56×45 because current source snapshots already contain suitable two-resource families. The policy must be tested one caliber family at a time before wider rollout.

## CURRENT MP-133 execution update (2026-10-03)

- **G2 owner-runtime confirmed:** existing T4b installed magazine accepts one synthetic `+1`; manual short-R chambers it; owner fires. Offline only; projectile/damage/MP unverified.
- **G3-A:** published source/API audit on `t4b/installed-mag-probe`. **G3-B1:** isolated *donor-only* source is now published in the same existing local T4b addon at [`a165e80`](https://github.com/Dubelkrya/Weapon_ARMA_X/commit/a165e804df1e571c58806bb39ea74e5eee993191). Source review and owner-only Workbench/game run are pending. **G3-B2/G4/G5:** not authorised.
- **Core SHIFT+R reload:** does not work per owner, regardless of historical code references. Core donor-transfer RPC is a locally reported unverified candidate ([#33](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/33)).
- **One local active MP-133 laboratory:** `ARMSTMP133T4B_InstalledMagProbe`; additional named fixtures stay inside it. No new T4c addon, no PR per small experiment. Documentation PR #31 must be reconciled with the active T4b branch before merging.
- **#28/#29:** published catalog and green hosted CI ([run 37135291162](https://github.com/Dubelkrya/Weapon_ARMA_X/actions/runs/37135291162)). Historical statements below are preserved as checkpoints, not a current task list.

## Historical MP-133 V3 research (2026-10-03)

[`MP133_INDEX.md`](MP133_INDEX.md) is the evidence/navigation index; [Issue #27](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27) is the chronological approval and owner-observation log. [`MP133_LAB_REGISTRY.md`](MP133_LAB_REGISTRY.md) records lab ownership and archival state. Earlier reports retain historical wording; the following statuses supersede it:

- **T0 owner-run native baseline: PASS.** Three shots with manual short-R pump and hold-R inspect were observed with Weapons only; no claim about Core-on compatibility or an instrumented physical magazine at T0.
- **T2b/T2c: diagnostic findings.** Paired player/weapon markers were observed, and the native command trace identifies manual rack as `intValue=1` and whole-mag swap as `4/5` depending on chamber state. Paired markers alone do not establish ammo authority.
- **T3 owner runtime: confirmed native whole-mag exchange.** Installed references changed `M1 → null → M3` and `M3 → null → M5`; the chambered round can remain when a partially loaded magazine is exchanged. The exact attach instant and old-mag inventory identity were not fully instrumented.
- **T3F limited passive diagnostic: corrected script ran in the owner's game.** The 760-line owner log yielded 100 T3F, 77 T3 and 18 T2c records with no `SCRIPT (E)`; it is not an isolated one-shot/rack/dry-fire test and supplies **no independent `gameplay_shot` callback**. `Weapon_EnableFire` is permission to shoot during bolt/reload animation, not a shot; the +300-ms snapshot is not post-shot. Astra's separate read-only audit suggested `OnProjectileShot` and `GameAnimationUtils.GetEventString` as **unverified follow-ups**, not implemented functionality.
- **T4 Phase A: `T4_API_OR_TRANSACTION_BLOCKED` for real shell transfer.** SDK 1.8.0.13 exposes `BaseMagazineComponent.SetAmmoCount(int)` but no verified atomic donor→installed-mag transfer, authoritative write, or recovery contract. No real transfer lab was implemented under Phase A.
- **Historical T4a checkpoint: `T4A_LAB_PREPARED_OWNER_RUN_REQUIRED`** ([report](MP133_V3_T4A_SETAMMOCOUNT_SEMANTICS.md); [scope](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5970853781)). The primary agent prepared an isolated disposable-magazine lab `ARMSTMP133T4A_SetProbe` (GUID `A7C41E90D3B24F68`) with one guarded `SetAmmoCount(+1)` action (default key P). Static checks were reported; **Workbench compile/gameplay not yet tested**. No real donor depletion, installed-mag mutation or multiplayer transfer is authorised.
- **Astra animation/graph task: PAUSED by owner** ([checkpoint](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5970888887)). The local `astra_build.py` draft is unfinished and unverified; do not run, overwrite, or hand it to another agent before explicit resumption.
- **Owner alone runs Workbench and the game.** Agent static checks, GitHub CI and offline `srv=1` do not prove engine/runtime/multiplayer correctness. The frozen V2/P2 labs, production Weapons and Core remain outside these tasks.

## Current Workbench-validated AEK-971 control point

The current validated prototype is newer than the historical V8 checkpoint.

Current parent:

`{EAE9A298979C4721}Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et`

Validated project-level facts:

- Safe inherited;
- Single inherited;
- Auto inherited object `{B80A64F4A8EF8333}` overridden to 900 RPM;
- new 3-round Burst object `{619AB45BF76565F3}` using `FireMode_Burst.conf`, 900 RPM;
- weight 3.5;
- provisional recoil overrides only `LinearData` and `AngularData`; `TurnOffsetData` remains inherited;
- optic slot `{55349E9229B55E29}` uses `AttachmentOpticsARMST_DovetailRU` through inherited AttachmentType object `{5A16F04B258689D6}`;
- optic geometry remains inherited from AK74N (`slot_optics` / `snap_weapon` were not locally rewritten);
- thin PSO-1 child using the same `DovetailRU` type mounts successfully in Workbench;
- user-facing name is `AEK-971` with the current Russian description stored in inventory and weapon UI info.

Canonical samples:

- `reports/samples/armst_AEK971_test_v12_NAME_DESCRIPTION.et`
- `reports/samples/armst_Optic_PSO1_DovetailRU.et`

Historical `reports/AEK971_TEST_CHECKPOINT_V8.md` remains as debugging history only and must not be used as the current resume point.

## Data freshness / known debt

- **Catalog #28 was published** on 2026-10-03 (generated-only commit [`5c443a9`](https://github.com/Dubelkrya/Weapon_ARMA_X/commit/5c443a94ff0f53b839e7a1909c4f11e382825e47)): 181 cataloged entities, reviewed GUID reconciliation and corrected grenade classification. Hosted CI was successful, including the [latest checked run on `7101fd6`](https://github.com/Dubelkrya/Weapon_ARMA_X/actions/runs/37135291162). This is a reviewed **snapshot**, not proof that the local addon has had no later changes; rescan only after checking a fresh source diff. The older ~1,455-stale-path note describes historical pre-rescan debt. Never hand-edit generated paths or delete the imported vanilla source corpus.
- `indexes/script_reference/manifest.json` is a supplied-snapshot inventory and may still list old built-in dovetail types for source assets; active authoring policy is v2 `DovetailRU`.
- The native technical/balance Sheets have had the known TT `ARRAYFORMULA` spill blockers removed; manual values must not be written into those formula spill ranges again.
- Raw `.xlsx` copies on Drive are archived snapshots; the native Google Sheets are the active tabular working views.
- Older reports may mention `agent/resolver-v2` and `agent/weapon-intelligence-v1` as historical research refs. The accessible GitHub branch listing at this checkpoint showed only `main`; verify actual local and remote refs before reusing historical names.
- AP/BP ammunition roles are design targets until each caliber family is locally authored and Workbench-tested; do not mark untested families as implemented.
- The failed `Armst_Work` rescan is not canonical and must not be merged as a replacement for the main snapshot.

## Required next refresh

When the primary addon changes after the published #28 snapshot, run the scanner against `ARMST-PLATFORM---Weapons` and review the generated diff before merge. Do not substitute `Armst_Work` or another partial addon as the canonical source root. Concurrent knowledge-repo documentation work should use an isolated branch/PR; the live addon's separate `main`-only branch policy is unchanged.
