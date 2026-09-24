# Reports index

This directory contains weapon-specific authoring guides, active gameplay policies, research checkpoints, generated scanner output, and historical debugging material for the ARMST **Arma Reforger** weapons addon.

> [!IMPORTANT]
> [`KNOWLEDGE_STATUS.md`](KNOWLEDGE_STATUS.md) is the entry point for deciding what is current. When another report conflicts with it, use the authority order defined there.

## Status legend

- **CURRENT / AUTHORITATIVE** — active source-of-truth or authoring guidance.
- **CURRENT POLICY** — active gameplay/design policy.
- **WORKBENCH VALIDATED** — backed by a confirmed editor/runtime control point.
- **GENERATED SNAPSHOT** — scanner-derived data that can become stale.
- **EXPERIMENTAL** — research or proof-of-concept work; not production guidance.
- **HISTORICAL / SUPERSEDED** — retained only for debugging or design history.

## Weapon catalog navigation

Use [`WEAPON_INDEX.md`](../WEAPON_INDEX.md) for the human-readable generated weapon catalog. It is a navigation view over `catalog/weapons/*.json`, not a replacement for live-addon or Workbench evidence.

Use [`families/README.md`](families/README.md) for generated side-by-side comparisons of the AK/RPK family, explicit 9×39 weapons and shotguns.

Use [`balance/README.md`](balance/README.md) for evidence-preserving gameplay balance comparisons that keep weapon, magazine and projectile layers separate.

## Current authoring references

| File | Purpose |
|---|---|
| [`KNOWLEDGE_STATUS.md`](KNOWLEDGE_STATUS.md) | Current source-of-truth, freshness and authority map |
| [`PREFAB_AUTHORING_GUIDE.md`](PREFAB_AUTHORING_GUIDE.md) | Safe weapon prefab inheritance and override rules |
| [`CONFIG_AUTHORING_GUIDE.md`](CONFIG_AUTHORING_GUIDE.md) | Ammunition, magazine, AmmoConfig and projectile resolution |
| [`SCRIPT_MODULE_AUTHORING_GUIDE.md`](SCRIPT_MODULE_AUTHORING_GUIDE.md) | Weapon compatibility modules, attachment slots and sights |
| [`OPTICS_COMPATIBILITY_SYSTEM_V2.md`](OPTICS_COMPATIBILITY_SYSTEM_V2.md) | Active optics gameplay compatibility design |
| [`AMMO_AP_BP_POLICY.md`](AMMO_AP_BP_POLICY.md) | Active ammunition gameplay-role policy |

## Current research

| File | Purpose |
|---|---|
| [`NESTED_DOVETAIL_RIS_STORAGE_AUDIT_2026-09-21.md`](NESTED_DOVETAIL_RIS_STORAGE_AUDIT_2026-09-21.md) | Ongoing nested Dovetail → RIS storage/attachment research |

Research files may describe experiments, blockers, or unvalidated paths. They are not automatically production authoring rules.

## Workbench-backed samples

The [`samples/`](samples/) directory contains weapon-specific examples and control artifacts used by the authoring documentation.

Important current examples include:

- `armst_AEK971_test_v12_NAME_DESCRIPTION.et`;
- `armst_Optic_PSO1_DovetailRU.et`;
- `armst_TT_authoring_sample_v4.et`;
- `AttachmentOpticsARMST.c`.

Always check [`KNOWLEDGE_STATUS.md`](KNOWLEDGE_STATUS.md) before treating a sample as the newest control point.

## Historical / superseded material

These files remain useful as debugging history or design context, but should not override current policy:

| File | Status |
|---|---|
| [`AEK971_TEST_CHECKPOINT_V8.md`](AEK971_TEST_CHECKPOINT_V8.md) | Historical AEK checkpoint; newer validated sample exists |
| [`OPTICS_COMPATIBILITY_SYSTEM.md`](OPTICS_COMPATIBILITY_SYSTEM.md) | Older optics-system design; V2 is the active policy |

## Generated scanner reports

The following files are scanner-derived or snapshot-oriented outputs:

- `scan_summary.md` / `scan_summary.json`;
- `anomalies.md` / `anomalies.json`;
- `inheritance_issues.md` / `inheritance_issues.json`;
- `unresolved_references.md` / `unresolved_references.json`;
- `weapon_ballistics.json`.

> [!WARNING]
> Generated reports describe the snapshot that produced them. They can become stale after weapon-addon changes. Do not use an older generated report to override newer live-addon or Workbench evidence.

## Authority rule

For weapon work, use this order:

1. current primary addon / Workbench validation;
2. Workbench-validated authoring rules;
3. active gameplay policies;
4. generated catalogs and indexes;
5. external/tabular working views;
6. archived or superseded reports.

Unknown weapon values should remain unknown until they are resolved from project evidence.
