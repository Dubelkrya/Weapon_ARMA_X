# Weapon Intelligence V1

## Goal

Build an AI-readable, read-only catalog of the local ARMST Arma Reforger weapons addon without modifying game source files.

The local addon is authoritative. Git output is derived metadata and must preserve uncertainty instead of inventing values.

## Proven design sources

V1 intentionally reuses two already-proven ideas from `Dubelkrya/ReforgerWorkbenchToolkit` as read-only architectural references:

1. `RWTK_CodeIntelligenceScanner` — bounded scanning/indexing of mounted `.c` files into derived metadata instead of source mirrors.
2. `RWTK_ParticleSourceExtractorPlugin` — evidence that Workbench resources may require a separate materialization path when packed native content is not available as a normal physical source file.

This repository does not modify the active RWTK engineering task or branch.

## Local source

Expected local addon root:

```text
C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons
```

The path itself is not written into generated catalog data. Only the source-root folder name and paths relative to it are exported.

## Run

From the `Weapon_ARMA_X` repository root:

```powershell
python tools/weapon_intelligence/scan.py `
  --root "C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons" `
  --out .
```

No third-party Python packages are required.

## Inputs

V1 scans recursively:

- `.et`
- `.conf`
- `.meta`
- `.c`

`.et/.conf/.meta` are parsed as Enfusion text resources. `.c` is indexed separately using bounded lexical extraction inspired by RWTK Code Intelligence.

## Outputs

```text
catalog/
  weapons/
  magazines/
  ammunition/
  ammo_configs/
  attachments/
indexes/
  resources.json
  references.json
  inheritance.json
  scripts.json
reports/
  scan_summary.md
  unresolved_references.md
  inheritance_issues.md
  parse_warnings.json   # only when warnings exist
agent/
  scan_state.json
```

## V1 resource model

The parser is deliberately syntax-preserving rather than hardcoded to one prefab shape. It tokenizes quoted/unquoted tokens, nested `{}` blocks, `+{` collection blocks, properties, instance GUIDs, resource references, and root inheritance declarations.

Unknown blocks and fields remain in the parse tree even when the extractor does not yet assign semantic meaning to them.

### Weapons

Current normalized fields include:

- display name;
- parent prefab reference;
- physical weight/volume/dimensions;
- melee damage;
- `MuzzleComponent` fire modes and instance GUIDs;
- `RoundsPerMinute`;
- `MaxBurst` when explicitly present;
- `BulletInitSpeedCoef`;
- `DispersionDiameter` / `DispersionRange`;
- `MagazineWell`;
- `MagazineTemplate`;
- recoil `Curve Magnitudes` for Linear/Angular/TurnOffset;
- attachment slots/types;
- raw presence of `SightsComponent` and `ZeroingWeaponAimModifier`.

### Magazines

Current normalized fields include `MaxAmmo`, `MagazineWell`, `AmmoConfig`, weight, `WeightPerAmmo`, volume and parent reference.

### Ammunition/projectiles

Current normalized fields include `ShellMoveComponent.InitSpeed`, `Mass`, `AirDrag`, velocity variation and parent reference.

### Enforce Script `.c`

The scanner exports derived script metadata only:

- files and hashes;
- class/interface symbols;
- direct base class names;
- simple method owner/name/arity records.

It does not intentionally mirror full `.c` source bodies into the catalog.

## Reference graph

Every `{GUID}Path/Resource.ext` occurrence is exported to `indexes/references.json` with source file, line, GUID, target path and local-resolution result.

This supports chains such as:

```text
Weapon
-> MagazineTemplate
-> MagazineComponent.AmmoConfig
-> AmmoResourceArray
-> projectile prefab
-> ShellMoveComponent
```

## Inheritance boundary

V1 resolves local parent paths and records inheritance chains, cycle/depth problems and external/missing parents.

V1 does **not** claim a complete effective Enfusion merge. In particular, component-array and instance-GUID override/merge semantics are not yet applied to produce a final engine-equivalent prefab.

Therefore a field absent from a child prefab remains unknown at the child level until a separately validated inheritance/override resolver is implemented.

This is intentional. The scanner must not infer `MaxBurst`, zeroing, damage, recoil or other values merely because they are likely to come from a parent.

## Safety

V1 is read-only with respect to the mod. It has no source edit operation.

A future editor must be a separate stage with explicit provenance, preview/diff, target-file selection and post-edit rescan verification.

## Acceptance for first local run

A useful first run should report:

- non-zero resource file count;
- non-zero weapons count;
- counts for magazines/ammunition where present;
- `.c` discovery/index counts;
- unresolved external references instead of guessed values;
- valid JSON outputs;
- VSS-like prefabs retaining explicit RPM, dispersion, magazine and recoil data while leaving inherited `MaxBurst` unknown when absent from the child.
