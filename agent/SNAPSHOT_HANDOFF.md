# Weapon source snapshot handoff

## Goal

Workbench exports only the vanilla source material relevant to weapon architecture into this addon. A local agent then reads that raw snapshot together with ARMST, builds a compact architecture/index layer, and commits only the compact derived layer to GitHub.

## Source/edit policy

- ARMST is editable.
- Vanilla is read-only inheritance/reference material.
- Raw vanilla snapshot lives under `Imported/VanillaSources/` and is gitignored.
- Never commit raw vanilla source files.
- Never modify raw vanilla snapshot files as a balance/content fix.
- Any actual game-resource fix belongs in ARMST.

## Workbench export

Use:

`WAX: Export Vanilla Weapon Source Snapshot`

The exporter is deliberately weapon-scoped. It does **not** export the whole game.

Current scope:

- `$ArmaReforger:Prefabs/Weapons` → `.et`, `.conf`
- `$ArmaReforger:Configs/Weapons` → `.conf`
- `$ArmaReforger:Scripts/Game` → only `.c` files whose path is weapon-domain related (`Weapon`, `Magazine`, `Ammo`, `Projectile`, `Muzzle`, `Recoil`, `FireMode`, `Attachment`, `Optic`)

The raw export preserves vanilla-relative paths under:

`Imported/VanillaSources/`

and writes `_wax_materialization.tsv` with copy/materialization status.

The snapshot exporter intentionally does **not** call `RegisterResourceFile` for every copied file. These files are local-agent input, not addon resources that Workbench needs to register/import.

If architecture analysis later proves that a specific referenced class/config lives outside the current scope, add a targeted source root or dependency rule. Do not broaden the exporter back to the whole `$ArmaReforger:` tree.

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
- Which script classes implement the components/config behavior involved?
- How does the chain reach magazine, AmmoConfig, AmmoMapping and projectile physics?
- What is the smallest valid ARMST prefab that changes only the intended fields?
