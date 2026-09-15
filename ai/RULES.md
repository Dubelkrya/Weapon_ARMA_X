# ARMST AI compact rules

This directory is the **machine-facing entry point** for weapon balance/catalog work.

## Read order
1. `ai/RULES.md`
2. The single relevant JSONL shard (`weapons_*`, `magazines`, or `ammunition`)
3. Resolver/source files only when provenance, nested collections, attachments, recoil curves, architecture, or an edit decision requires deeper evidence.

For prefab/source-architecture questions, prefer the tracked compact digest under `architecture/generated/` when present. Its local source is produced by `agent/scripts/build_architecture_package.py` and published by `agent/scripts/publish_architecture_digest.py`.

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

## Strict identity policy
- Correctness is more important than maximizing `resolved` counts.
- Resource identity is origin + virtual path + proven live Resource GUID evidence where available.
- A same-path ARMST/vanilla collision stays ambiguous unless the serialized GUID or other proven identity evidence selects a target.
- Lower/read-only vanilla resources may resolve a collision to their own origin because base-game resources cannot depend upward on ARMST.
- Once an origin is selected, preserve it through weapon -> magazine -> AmmoConfig -> projectile resolution.
- Config loop identity is `(origin, path)`, not path alone.
- `.meta Name` is metadata only and must not override live serialized Resource GUID evidence.

## Architecture/source acquisition
- Do not recreate or use a broad Workbench source snapshot exporter.
- Do not export vanilla `.c` files through Workbench.
- Vanilla scripts come from `BohemiaInteractive/Arma-Reforger-Script-Diff`, pinned by `agent/scripts/sync_vanilla_scripts.py` to the matching game build.
- Build dependency closure offline from ARMST plus the existing read-only materialized vanilla dataset.
- `workbench_export_requests.json` contains only proven missing serialized `.et/.conf` resources.
- `ambiguous_identity_edges` are identity problems, not export requests.
- Ask for Workbench only when the exact request list is non-empty and an exact-path exporter is ready.

## Data semantics
- Compact rows are **resolved/effective summaries** unless a field is absent.
- Missing key = pending/unknown. Never infer `0` or `null`.
- Scalar inheritance: child local -> nearest parent -> higher parents, including read-only vanilla ancestors when actually referenced.
- Collections/components: resolve by instance GUID/override semantics. Never blindly merge/copy parent lists.
- Serialized instance GUIDs must remain distinct from resource-reference GUIDs.
- Resource identity is not path alone. `.meta Name` is metadata only.
- Entity ID is not globally unique.
- Magazine capacity comes only from resolved `MagazineComponent.MaxAmmo`; never from filenames.
- Effective muzzle velocity = mapped projectile `InitSpeed` * weapon `BulletInitSpeedCoef`.
- `AmmoConfig` with several projectile types requires exact `AmmoMapping` before selecting projectile physics.
- AI ballistic table is separate from projectile flight physics; mismatch is an AI-aiming/table anomaly.
- Base weapon TTX must stay separate from runtime attachment modifiers.
- The semantic `_prefer_functional_components` ordering is not prefab-architecture evidence; architecture blueprints preserve raw/source ordering and instance GUIDs.
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
- `IDENTITY_AMBIGUOUS`: same-path/multi-root target cannot be proven; do not guess

## Editing rule
Use compact files for retrieval/comparison. Before modifying game resources, confirm the field in resolver provenance/raw source. Read vanilla as evidence when inheritance requires it, but **edit ARMST only**. Never edit from a compact row alone.

Never commit `Imported/VanillaSources/`, `Imported/OfficialScriptDiff/`, `agent/v2_output/`, or `agent/architecture_output/`.
