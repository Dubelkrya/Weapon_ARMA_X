# Compact weapon architecture digest

`architecture/generated/` is the tracked machine-readable handoff for remote source-architecture analysis.

It contains **derived data only**. Raw ARMST/vanilla source snapshots and the official Bohemia script checkout do not belong here.

## Build locally

From the Weapon_ARMA_X checkout, the local agent should run:

```bat
python agent\scripts\build_architecture_package.py
python agent\scripts\publish_architecture_digest.py
```

The first command builds the gitignored working package under `agent/architecture_output/`. The second command publishes only compact derived artifacts under `architecture/generated/`.

## Expected generated artifacts

- `package_manifest.json` — source/version and package summary;
- `architecture_summary.json` — compact dependency statistics;
- `resource_graph.json` — resource index, inheritance/reference edges and dependency closure;
- `blueprint_index.json` — ARMST prefab-to-shard lookup;
- `blueprints/*.json` — one provenance-preserving prefab blueprint per ARMST `.et`;
- `script_class_links.json` — serialized classes relevant to the blueprints plus base-class closure;
- `workbench_export_requests.json` — exact missing `.et/.conf` resources only;
- `resolver_warnings.json` — parser/identity gaps that must not be silently guessed;
- `publication_manifest.json` — hashes/sizes for published derived files.

## Safety / interpretation

- ARMST is the only editable game-resource root.
- Materialized vanilla is read-only evidence.
- Official Bohemia scripts are read-only evidence pinned to a specific game build.
- A path collision is not resolved merely because ARMST has higher priority.
- Ambiguous identity edges are not Workbench export requests.
- Workbench is only justified when `workbench_export_requests.json` contains proven missing serialized `.et/.conf` references.
- Never commit `Imported/VanillaSources/`, `Imported/OfficialScriptDiff/`, `agent/v2_output/`, or `agent/architecture_output/`.

Generated architecture data is evidence for reconstruction and recipe generation; actual game-resource changes still belong only in ARMST.
