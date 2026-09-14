# Weapon_ARMA_X — Copilot instructions

For weapon catalog/balance tasks, start with `ai/RULES.md` and `ai/manifest.json`. Load only the relevant `ai/*.jsonl` shard. Do not bulk-read `catalog/`, `indexes/`, `reports/`, or `schema/` unless the compact layer is insufficient; they are legacy/debug outputs during resolver-v2 migration.

Architecture for catalog resolution: `ARMST addon only -> resolver v2 -> derived catalog/reports`.

ARMST is a frozen duplicate snapshot of the source resources the mod was built against. It intentionally isolates the mod from later vanilla changes. Current vanilla and `Imported/VanillaSources` are not fallback sources for ARMST catalog resolution.

Core data rules:
- Resolve inheritance, magazines, AmmoConfig, projectiles, and configs only from files physically present inside ARMST.
- A short serialized path may be normalized only to a unique target inside the same ARMST root.
- If a referenced resource is absent from ARMST, preserve it as external/missing; never silently fill it from current vanilla.
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

Before editing game resources, verify compact values against resolver provenance/raw ARMST source. Preserve source anomalies instead of silently correcting them.

Primary implementation files are under `agent/scripts/resolver_v2*.py`, `agent/scripts/scan_build_v2.py`, and `Scripts/WorkbenchGame/`. `Imported/VanillaSources` remains a separate generated/local utility output and is not part of the ARMST catalog source path. `agent/v2_output` is generated/local and must not be committed.

Run Python validation with:
`python -m unittest discover -s agent/tests -p 'test_resolver_v2*.py' -v`

Workbench/Enfusion script compatibility cannot be proven by GitHub Actions; treat local Workbench compile checks as a separate validation step for Workbench-only tooling.
