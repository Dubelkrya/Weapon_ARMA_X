# ARMST AI compact rules

This directory is the **machine-facing entry point** for weapon balance/catalog work.

## Read order
1. `ai/RULES.md`
2. The single relevant JSONL shard (`weapons_*`, `magazines`, or `ammunition`)
3. Resolver/source files only when provenance, nested collections, attachments, recoil curves, or an edit decision requires deeper evidence.

Do **not** bulk-load `catalog/`, `indexes/`, `reports/`, or `schema/` for normal analysis. Those are legacy/debug outputs while resolver v2 is being validated.

## Source policy
- ARMST is the only editable game-resource source for this project.
- Our weapons and duplicated sources live in ARMST, but some of those duplicates still inherit from vanilla resources.
- Materialized vanilla is therefore a **read-only inheritance/reference source** for resolver v2.
- Export catalog entities from ARMST only; vanilla participates only in resolving inherited/effective values and dependencies.
- Never edit, patch, rewrite, or recommend changes directly to vanilla or `Imported/VanillaSources`.
- All balance fixes and source corrections must be made in ARMST.
- Preserve provenance across ARMST -> vanilla chains so inherited values are distinguishable from ARMST-local values.
- If a reference cannot be resolved in either ARMST or materialized vanilla, keep it external/missing and report the gap.
- Short serialized paths may be normalized only when the target is unambiguous.

## Data semantics
- Compact rows are **resolved/effective summaries** unless a field is absent.
- Missing key = pending/unknown. Never infer `0` or `null`.
- Scalar inheritance: child local -> nearest parent -> higher parents, including read-only vanilla ancestors when actually referenced.
- Collections/components: resolve by instance GUID/override semantics. Never blindly merge/copy parent lists.
- Resource identity = resource path + live Resource GUID. `.meta Name` is metadata only.
- Entity ID is not globally unique.
- Magazine capacity comes only from resolved `MagazineComponent.MaxAmmo`; never from filenames.
- Effective muzzle velocity = mapped projectile `InitSpeed` * weapon `BulletInitSpeedCoef`.
- `AmmoConfig` with several projectile types requires exact `AmmoMapping` before selecting projectile physics.
- AI ballistic table is separate from projectile flight physics; mismatch is an AI-aiming/table anomaly.
- Base weapon TTX must stay separate from runtime attachment modifiers.
- `RESOLVED` is not the same as `VERIFIED`.

## Status
`PENDING_DETAIL | PARTIAL | RESOLVED | VERIFIED`

## Common flags
- `PENDING_DETAIL`: only indexed / detail not resolved
- `PARENT_MISSING`: parent-chain gap after checking ARMST + read-only vanilla
- `AMMO_PENDING`: ammo chain incomplete after checking ARMST + read-only vanilla
- `MAPPING_PENDING`: exact AmmoMapping incomplete
- `CAPACITY_PENDING`: MaxAmmo not proven
- `RECOIL_GAP`: recoil collection/config incomplete
- `SOURCE_MISMATCH`: source data internally inconsistent; preserve source, do not auto-correct
- `AIBT_MISMATCH`: AI ballistic table likely stale/wrong for projectile
- `ATTACHMENT_EFFECTS`: attachment runtime effects not folded into base TTX
- `FIREMODE_PENDING`: mode type/semantics/RPM incomplete
- `META_GUID_DIFF`: metadata GUID differs from live Resource GUID; this is allowed
- `COLLECTION_VERIFY`: nested collection override requires raw verification

## Editing rule
Use compact files for retrieval/comparison. Before modifying game resources, confirm the field in resolver provenance/raw source. Read vanilla as evidence when inheritance requires it, but **edit ARMST only**. Never edit from a compact row alone.
