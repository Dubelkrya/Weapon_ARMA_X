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

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`

Normal local-agent editing, prefab/config/script lookup and canonical source scans must target this addon unless the user explicitly names another root for a temporary test.

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\Armst_Work`

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

- Generated catalogs/indexes are snapshots of the primary addon and should be refreshed after material edits to `ARMST-PLATFORM---Weapons`.
- `indexes/script_reference/manifest.json` is a supplied-snapshot inventory and may still list old built-in dovetail types for source assets; active authoring policy is v2 `DovetailRU`.
- The native technical/balance Sheets have had the known TT `ARRAYFORMULA` spill blockers removed; manual values must not be written into those formula spill ranges again.
- Raw `.xlsx` copies on Drive are archived snapshots; the native Google Sheets are the active tabular working views.
- Experimental branches `agent/resolver-v2` and `agent/weapon-intelligence-v1` are divergent research branches; do not merge wholesale into `main` without selective review.
- AP/BP ammunition roles are design targets until each caliber family is locally authored and Workbench-tested; do not mark untested families as implemented.
- The failed `Armst_Work` rescan is not canonical and must not be merged as a replacement for the main snapshot.

## Required next refresh

When the primary addon changes enough to warrant a refresh, run the scanner against `ARMST-PLATFORM---Weapons` and review the generated diff before merge. Do not substitute `Armst_Work` or another partial addon as the canonical source root.
