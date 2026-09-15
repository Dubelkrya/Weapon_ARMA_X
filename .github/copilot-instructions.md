# Weapon_ARMA_X — Copilot instructions

For weapon catalog/balance tasks, start with `ai/RULES.md` and `ai/manifest.json`. Load only the relevant `ai/*.jsonl` shard. Do not bulk-read `catalog/`, `indexes/`, `reports/`, or `schema/` unless the compact layer is insufficient; they are legacy/debug outputs during resolver-v2 migration.

For source architecture / prefab reconstruction, read `agent/SNAPSHOT_HANDOFF.md` first. Build the offline package before proposing any Workbench action:

`python agent/scripts/build_architecture_package.py`

Architecture for catalog resolution:

`ARMST editable sources + read-only materialized vanilla -> strict resolver v2 -> derived catalog/reports`

Architecture for prefab reconstruction:

`ARMST + existing vanilla materialization + pinned official Bohemia scripts -> offline dependency/architecture graph -> exact missing .et/.conf requests only`

ARMST is the only editable game-resource root. Our weapons and duplicated source prefabs live there. Some ARMST duplicates still inherit from vanilla, so materialized vanilla remains a read-only reference/base layer for inheritance and dependency resolution.

Core data rules:
- Export catalog entities from ARMST only.
- Resolve from ARMST resources and follow actual parent/config/magazine/ammo references into materialized vanilla when inheritance requires it.
- Never edit, patch, rewrite, or recommend direct changes to vanilla or `Imported/VanillaSources`; all source/balance edits belong in ARMST.
- Preserve provenance across ARMST -> vanilla inheritance chains.
- Correctness outranks a high `resolved` count. Same-path ARMST/vanilla collisions remain ambiguous unless identity is proven.
- Use proven serialized Resource GUID evidence before origin/path heuristics.
- Once a target origin is selected, preserve it through magazine -> AmmoConfig -> projectile resolution.
- Config loop identity is `(origin, path)`, not path alone.
- A short serialized path may be normalized only when its target remains unambiguous.
- If a referenced resource is absent from both ARMST and materialized vanilla, preserve it as external/missing.
- Missing child field inherits from nearest parent; missing is never automatically 0/null.
- Keep raw/local separate from resolved/effective.
- Resolve nested collections/components by serialized instance GUID/override semantics.
- Serialized instance GUIDs and resource-reference GUIDs are different identities; never conflate them.
- Resource GUID comes from live `{GUID}path`/proven reference evidence; `.meta Name` is metadata only.
- Entity ID is not globally unique.
- Magazine capacity only from resolved `MagazineComponent.MaxAmmo`, never filename.
- Resolve `MagazineTemplate -> AmmoConfig -> AmmoResourceArray -> AmmoMapping -> projectile` before assigning projectile physics.
- Effective muzzle velocity = projectile `InitSpeed * BulletInitSpeedCoef`.
- AIBallisticTable is AI aiming data, separate from projectile flight physics.
- Do not fold suppressor/optic/UGL runtime effects into base TTX without resolving attachment behavior.
- The semantic `_prefer_functional_components` ordering is not prefab-architecture evidence. Architecture blueprints preserve source ordering and instance GUIDs.
- `RESOLVED` does not mean `VERIFIED`.

Source acquisition rules:
- Do not recreate/use a broad Workbench vanilla snapshot exporter.
- Do not export vanilla `.c` through Workbench.
- Vanilla script source comes from `BohemiaInteractive/Arma-Reforger-Script-Diff`, pinned by `agent/scripts/sync_vanilla_scripts.py` to the matching game build.
- Workbench is allowed only when `workbench_export_requests.json` contains exact proven missing `.et/.conf` paths and an exact-path exporter is ready.
- `ambiguous_identity_edges` require identity evidence, not more copies of the same path.

Before editing game resources, verify compact values against resolver provenance/raw source. Vanilla may be consulted as read-only inheritance evidence, but **edit ARMST only**. Preserve source anomalies instead of silently correcting them.

Primary implementation files are under `agent/scripts/resolver_v2*.py`, `agent/scripts/scan_build_v2*.py`, `agent/scripts/architecture_index.py`, `agent/scripts/build_architecture_package.py`, `agent/scripts/script_class_index.py`, and `agent/scripts/publish_architecture_digest.py`.

Never commit `Imported/VanillaSources`, `Imported/OfficialScriptDiff`, `agent/v2_output`, or `agent/architecture_output`. The tracked compact architecture handoff is `architecture/generated/` and is produced only by `agent/scripts/publish_architecture_digest.py` after local validation.

Run Python validation with:
`python -m unittest discover -s agent/tests -p 'test_resolver_v2*.py' -v`

Workbench/Enfusion compatibility cannot be proven by GitHub Actions. Do not use a green Python CI result as proof that a Workbench plugin compiles.
