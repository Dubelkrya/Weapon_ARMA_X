# Offline weapon architecture handoff

## Goal

Stop using Workbench as an exploratory scanner. The local agent should first build a strict dependency/architecture graph from sources already available on disk, then ask Workbench for **only exact missing `.et/.conf` resources** if the graph proves they are required.

ARMST is the only editable game-resource root. Vanilla remains read-only evidence.

## Current source set

Use these inputs first:

1. ARMST addon source tree (editable).
2. Existing `Imported/VanillaSources/` materialized vanilla `.et/.conf` dataset (read-only).
3. `Imported/VanillaSources/_wax_materialization.tsv` as authoritative evidence for which materialized files belong to the latest dataset run.
4. Official Bohemia script sources from `BohemiaInteractive/Arma-Reforger-Script-Diff` pinned to game build `1.8.0.13`, commit `3d77cc212d5cda9922daf5f45635c7300d2d4cce`.

Raw vanilla and official script checkouts are gitignored and must never be edited as project fixes.

## Workbench policy

The former `WAX: Export Vanilla Weapon Source Snapshot` broad exporter has been removed.

Do **not**:

- scan all `$ArmaReforger:` resources;
- re-export the whole weapon tree to improve resolver metrics;
- export `.c` scripts through Workbench;
- use filename-keyword script filtering as architecture evidence;
- ask the user to collect resolver statistics manually.

Workbench is allowed again only after the offline dependency graph produces an exact missing-resource request list. A future exact exporter must consume that list and materialize only those `.et/.conf` paths.

## Local-agent one-command build

Run from the Weapon_ARMA_X checkout:

```bat
python agent\scripts\build_architecture_package.py
```

The command performs the offline work:

- validates the materialized vanilla manifest when present;
- rejects stale/unlisted `.et/.conf/.meta` files instead of silently scanning them;
- uses strict GUID/origin-aware resolver identity;
- preserves origin across weapon → magazine → AmmoConfig → projectile traversal;
- builds inheritance and resource-reference edges;
- builds ARMST prefab blueprints with raw instance GUIDs and source order;
- builds an effective architecture tree **without** semantic component reordering heuristics;
- computes dependency closure from ARMST `.et` resources;
- emits exact missing `.et/.conf` references separately from identity-collision gaps;
- fetches the pinned official Bohemia script snapshot unless `--skip-script-sync` is requested;
- indexes script classes/base classes/fields/method names;
- links serialized component/config class names to their script declarations and base-class closure.

Default local output (gitignored):

`agent/architecture_output/`

Important files:

- `package_manifest.json` — compact package/source summary;
- `architecture_summary.json` — resource/dependency counts;
- `architecture_graph.json` — resource index + inheritance/reference graph + dependency closure;
- `weapon_blueprints.json` — ARMST local trees, instance GUIDs, effective component subtrees and provenance;
- `script_class_index.json` — official Enforce class index;
- `script_class_links.json` — only classes relevant to serialized ARMST architecture plus base closure;
- `workbench_export_requests.json` — exact serialized resources absent from both current inputs;
- `resolver_warnings.json` — parser/resolver warnings requiring review.

## Identity rules

Correctness has priority over a high `resolved` count.

- Resource identity is not just a virtual path.
- Proven serialized GUID evidence wins over path/origin heuristics.
- ARMST path collisions remain ambiguous if the target GUID owner cannot be proven.
- Lower/read-only vanilla sources may resolve a collision to their own origin because base-game resources cannot depend upward on editable ARMST.
- Once an origin is selected, keep it through magazine/config/projectile resolution.
- Config loop identity is `(origin, path)`, not path alone.
- `.meta Name` is metadata, not authoritative live Resource GUID evidence.
- Short paths may use suffix matching only when identity remains unambiguous.

## Parser rules

Serialized block syntax such as:

```text
BaseFireMode "{INSTANCE}" : "{RESOURCE_GUID}FireMode.conf" {
```

must preserve the instance GUID separately from the resource reference. Instance GUIDs are required for prefab override recipes and cannot be replaced by heuristic component ordering.

## Workbench decision gate

After the package build:

- If `workbench_export_requests.json` is empty, **do not launch Workbench**.
- If it contains paths, the local agent returns the exact request list and stops. Do not fall back to a broad exporter.
- `ambiguous_identity_edges` are not export requests. They require better identity evidence, not more copies of the same path.

The user should only ever be asked for one GUI action after an exact exporter is ready and there is a non-empty proven request list.

## GitHub handoff

Never commit:

- `Imported/VanillaSources/`;
- `Imported/OfficialScriptDiff/`;
- `agent/v2_output/`;
- `agent/architecture_output/` raw generated workspace.

After local validation, upload only compact derived artifacts needed for remote architectural analysis. Preserve exact origin/path/GUID evidence, instance GUIDs, inheritance chains, reference edges, unresolved gaps, and script source commit metadata.

The derived GitHub layer must be sufficient to answer:

- Which base prefab should a new ARMST weapon inherit from?
- Which components/configs are authored locally versus inherited?
- Which instance GUIDs are valid override targets?
- Which `.conf` chains define fire modes/recoil/ammo behavior?
- Which script classes implement those serialized components/config types?
- How does a weapon resolve to magazine → AmmoConfig → AmmoMapping → projectile physics?
- What is the smallest valid ARMST prefab that changes only the intended fields?
