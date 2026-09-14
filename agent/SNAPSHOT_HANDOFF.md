# Source snapshot handoff

## Goal

Workbench exports raw mounted vanilla source material into this addon. A local agent then reads that raw snapshot together with ARMST, builds a compact architecture/index layer, and commits only the compact derived layer to GitHub.

## Source/edit policy

- ARMST is editable.
- Vanilla is read-only inheritance/reference material.
- Raw vanilla snapshot lives under `Imported/VanillaSources/` and is gitignored.
- Never commit raw vanilla source files.
- Never modify raw vanilla snapshot files as a balance/content fix.
- Any actual game-resource fix belongs in ARMST.

## Workbench export

Use:

`WAX: Export Full Vanilla Source Snapshot`

The exporter attempts to collect mounted text/architecture resources from `$ArmaReforger:`:

- `.et`
- `.conf`
- `.c`
- `.layout`

Existing weapon-only materializer commands remain available for smaller resolver runs.

The raw export preserves vanilla-relative paths under:

`Imported/VanillaSources/`

and writes `_wax_materialization.tsv` with copy/materialization status.

## Local-agent job

Read:

1. ARMST addon source tree.
2. `Imported/VanillaSources/` as read-only resolver/reference context.
3. `_wax_materialization.tsv` to detect unavailable source files.

Produce a compact derived package suitable for GitHub. It should preserve enough information to reconstruct weapon architecture without uploading raw vanilla sources.

Recommended derived data:

- resource index: path, kind, origin, live/reference GUIDs where proven, hashes/status;
- inheritance graph for `.et` and reusable `.conf` chains;
- full component/class tree with instance GUIDs;
- field provenance: ARMST-local vs vanilla-inherited;
- resource-reference edges (`.et`, `.conf`, scripts/classes, magazines, ammo, projectiles, attachments);
- script class index: class name, base class, source file, relevant fields/method names;
- normalized weapon architecture blueprints;
- unresolved/external references and parser gaps;
- minimal prefab recipes derived from proven inheritance/component structure.

Do not flatten away instance GUIDs or provenance.

## GitHub handoff

Commit only the compact derived outputs and parser/indexer code. Raw snapshot directories stay ignored.

The purpose of the GitHub layer is to let remote analysis answer questions such as:

- Which base prefab should a new ARMST weapon inherit from?
- Which components are mandatory vs inherited?
- Which instance GUIDs identify override targets?
- Which `.conf` files define fire modes/recoil/etc.?
- How does the chain reach magazine, AmmoConfig, AmmoMapping and projectile physics?
- What is the smallest valid ARMST prefab that changes only the intended fields?
