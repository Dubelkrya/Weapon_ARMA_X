# Weapon_ARMA_X — Copilot instructions

For weapon catalog/balance tasks, start with `ai/RULES.md` and `ai/manifest.json`. Load only the relevant `ai/*.jsonl` shard. Do not bulk-read `catalog/`, `indexes/`, `reports/`, or `schema/` unless the compact layer is insufficient; they are legacy/debug outputs during resolver-v2 migration.

Architecture for catalog resolution:

`ARMST editable sources + read-only materialized vanilla -> resolver v2 -> derived catalog/reports`

ARMST is the only editable game-resource root. Our weapons and duplicated source prefabs live there. Some ARMST duplicates still inherit from vanilla, so materialized vanilla remains a read-only reference/base layer for inheritance and dependency resolution.

Core data rules:
- Export catalog entities from ARMST only.
- Resolve from ARMST resources first and follow actual parent/config/magazine/ammo references into materialized vanilla when inheritance requires it.
- Never edit, patch, rewrite, or recommend direct changes to vanilla or `Imported/VanillaSources`; all source/balance edits belong in ARMST.
- Preserve provenance across ARMST -> vanilla inheritance chains.
- A short serialized path may be normalized only when its target is unambiguous.
- If a referenced resource is absent from both ARMST and materialized vanilla, preserve it as external/missing.
- Missing child field inherits from nearest parent; missing is never automatically 0/null.
- Keep raw/local separate from resolved/effective.
- Resolve nested collections/components by instance GUID/override semantics.
- Resource GUID comes from live `{GUID}path`/ResourceDB; `.meta Name` is metadata only.
- Entity ID is not globally unique.
- Magazine capacity only from resolved `MagazineComponent.MaxAmmo`, never filename.
- Resolve `MagazineTemplate -> AmmoConfig -> AmmoResourceArray -> AmmoMapping -> projectile` before assigning projectile physics.
- Effective muzzle velocity = projectile `InitSpeed * BulletInitSpeedCoef`.
- AIBallisticTable is AI aiming data, separate from projectile flight physics.
- Do not fold suppressor/optic/UGL runtime effects into base TTX without resolving attachment behavior.
- `RESOLVED` does not mean `VERIFIED`.

Before editing game resources, verify compact values against resolver provenance/raw source. Vanilla may be consulted as read-only inheritance evidence, but **edit ARMST only**. Preserve source anomalies instead of silently correcting them.

Primary implementation files are under `agent/scripts/resolver_v2*.py`, `agent/scripts/scan_build_v2.py`, and `Scripts/WorkbenchGame/`. `Imported/VanillaSources` and `agent/v2_output` are generated/local and must not be committed.

Run Python validation with:
`python -m unittest discover -s agent/tests -p 'test_resolver_v2*.py' -v`

Workbench/Enfusion script compatibility cannot be proven by GitHub Actions; treat a local Workbench compile/materializer smoke test as a merge gate for the materializer utility.
