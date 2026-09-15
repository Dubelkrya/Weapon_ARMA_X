# ARMST knowledge status

Canonical status snapshot for authoring knowledge. This file exists to distinguish live project truth, generated snapshots, active policy and archived material.

## Authority order

1. **Current local addon / Workbench validation** — authoritative for what actually opens, mounts and behaves correctly in the current project.
2. **Workbench-validated authoring rules** in `reports/PREFAB_AUTHORING_GUIDE.md` — authoritative for safe prefab editing patterns already confirmed in the editor.
3. **Active gameplay policies** such as `indexes/script_reference/optic_compatibility_policy_v2.json` and `reports/OPTICS_COMPATIBILITY_SYSTEM_V2.md`.
4. **Generated indexes/catalogs** — snapshots of supplied archives or prior addon roots. They provide provenance and instance IDs but are not automatically live.
5. **Google Sheets / exported XLSX views** — convenient working views. They must not override newer source-backed Git or Workbench evidence.
6. **Archived / superseded reports** — historical evidence only.

Unknown values remain unknown. Do not fill gaps from filenames or memory.

## Current local project boundary

Current working addon root reported by the project workflow:

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\Armst_Work`

The generated scanner state currently committed in `agent/scan_state.json` was produced from the older root:

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`

Therefore `agent/scan_state.json`, `reports/scan_summary.*`, base catalogs and scanner-derived reports must be treated as **historical snapshots** until a new scan is run against `Armst_Work`.

Do not hand-edit generated scanner output to pretend it is current. Regenerate it from the live addon instead.

## Current authoring policy

### Prefabs

- child local override > nearest parent > family/common base;
- preserve inherited instance IDs;
- child contains only real differences;
- inherited object: override by existing ID only;
- genuinely new object: new instance ID + correct resource parent/config;
- one logical change per validation step;
- structural validation is not Workbench/runtime validation.

### Optics

Active gameplay family for approved Russian/Soviet side-rail weapons and optics:

`DovetailRU` → `AttachmentOpticsARMST_DovetailRU`

This is a gameplay compatibility family. Real-world mount compatibility remains separate research data.

Compatibility is two-sided:

- weapon slot: `AttachmentSlotComponent -> AttachmentType`;
- optic/module: `WeaponAttachmentAttributes -> AttachmentType`.

Physical pivot/snap geometry is independent from compatibility type.

### Config / ammunition

`AmmoResourceArray` is the allowed ammunition set. `AmmoMapping` defines what is actually loaded. Projectile kinetic damage remains separate from tracer/incendiary effects. Use the projectile's actually referenced ballistic table.

The ARMST TT chain is resolved by the later `Configs(1).zip` snapshot: `Ammo_763x25.conf` → `Ammo_763x25_Ball.et`.

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

- Scanner outputs are stale relative to `Armst_Work`.
- `indexes/script_reference/manifest.json` is a supplied-snapshot inventory and may still list old built-in dovetail types for source assets; active authoring policy is v2 `DovetailRU`.
- Google Sheets may contain manually materialized values that block `ARRAYFORMULA` expansion. Formula health must be checked after manual edits.
- The two native Sheets and their `.xlsx` exports are not authoritative mirrors of each other unless explicitly regenerated.
- Experimental branches `agent/resolver-v2` and `agent/weapon-intelligence-v1` are divergent research branches; do not merge wholesale into `main` without selective review.

## Required next refresh

When local automation is available, run a fresh scanner against `Armst_Work`, then reconcile generated catalogs/indexes with this status file. Until then, new Workbench-confirmed facts should be added to the authoring guides/samples rather than falsifying generated snapshot metadata.
