# Agent entrypoint

For weapon catalog/balance work, read `ai/RULES.md` and `ai/manifest.json` first, then load only the relevant `ai/*.jsonl` shard.

For source architecture / prefab reconstruction work, read `agent/SNAPSHOT_HANDOFF.md` and use the offline package builder before asking for any Workbench action:

```bat
python agent\scripts\build_architecture_package.py
```

Do not bulk-load legacy `catalog/`, `indexes/`, `reports/`, or `schema/` unless compact data is insufficient. Before editing a game resource, verify the compact value against resolver provenance/raw source.

## Source and editing policy

ARMST contains the duplicated sources used by our mod and is the **only editable game-resource root**. Some ARMST duplicates still inherit from vanilla resources, so current/materialized vanilla must remain available to the resolver as **read-only inheritance/reference context**.

Operational resolver flow:

`ARMST editable sources + read-only materialized vanilla -> strict resolver v2 -> derived outputs`

Operational architecture flow:

`ARMST + existing vanilla materialization + official pinned Bohemia scripts -> offline dependency/architecture package -> exact missing .et/.conf requests only`

Rules:
- Catalog entities are exported from ARMST only.
- Start weapon/base/magazine/ammo/config resolution from ARMST resources.
- Follow actual inheritance/dependency references into materialized vanilla when ARMST still inherits from vanilla.
- Vanilla is evidence/reference only: never edit, patch, rewrite, or propose resource changes under `Imported/VanillaSources` or `$ArmaReforger`.
- All game-resource corrections and balance changes belong in the ARMST addon.
- Preserve provenance so every effective value says whether it was defined in ARMST or inherited from vanilla.
- Resource collisions must be resolved by proven GUID/origin evidence; do not maximize `resolved` counts by guessing.
- Once a concrete origin is selected, keep it through magazine -> AmmoConfig -> projectile resolution.
- Config identity/loops are `(origin, path)`, not path alone.
- Short serialized ARMST paths may be normalized only when they resolve unambiguously.
- If a reference is absent from both ARMST and materialized vanilla, keep it external/missing rather than inventing a value.
- Do not run or recreate a broad Workbench snapshot exporter. Workbench is allowed only for an exact missing `.et/.conf` request list produced by the offline dependency graph.
- Do not export vanilla `.c` via Workbench. Use the official `BohemiaInteractive/Arma-Reforger-Script-Diff` checkout pinned by `agent/scripts/sync_vanilla_scripts.py`.

Never commit `Imported/VanillaSources`, `Imported/OfficialScriptDiff`, `agent/v2_output`, or `agent/architecture_output`.
