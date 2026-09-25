# ARMST ballistic range probe

> [!IMPORTANT]
> **Status: EXPERIMENTAL / NOT WORKBENCH-VALIDATED.**
>
> The API behaviour used here is documented by Bohemia Interactive, but the
> sample script still needs to compile and run successfully in the current ARMST
> Workbench before its output is treated as authoritative project data.

Sample:

- `reports/samples/ARMST_BallisticRangeProbe.c`

## What it measures

The probe measures the maximum **direct-fire ballistic-table range** for the
**next projectile selected by a `BaseMuzzleComponent`**.

It does not measure:

- maximum sight zeroing;
- `DispersionRange`;
- effective combat range;
- lethal range;
- penetration range.

Those are separate concepts.

## Why the boundary can be detected

Bohemia's public Script API documents:

```c
static proto float BallisticTable.GetAimHeightOfNextProjectile(
    float distance,
    out float time,
    BaseMuzzleComponent muzzleComp,
    bool bDirectFire = true)
```

For a requested distance beyond the projectile's maximum bullet range, the
function returns a **negative `time`** and the aim height corresponding to the
projectile maximum range.

Therefore the probe searches for the boundary:

```text
largest d for which time(d) >= 0
```

It first advances in coarse steps, then performs binary search to the requested
precision.

Official API reference:

- https://community.bistudio.com/wikidata/external-data/arma-reforger/ArmaReforgerScriptAPIPublic/interfaceBallisticTable.html
- https://community.bistudio.com/wikidata/external-data/arma-reforger/ArmaReforgerScriptAPIPublic/interfaceBaseMuzzleComponent.html

Bohemia's weapon-authoring documentation also states that AI ballistic tables
must be generated for ammunition through `ShellMoveComponent -> Generate
ballistic tables`:

- https://community.bistudio.com/wiki/Arma_Reforger:Weapon_Creation/Prefab_Configuration

## Runtime use

Call the helper from a runtime context where the actual weapon muzzle is already
available:

```c
float maxRange = ARMST_BallisticRangeProbe.FindMaxDirectFireRange(muzzleComp);
ARMST_BallisticRangeProbe.LogMaxDirectFireRange(muzzleComp);
```

The sample deliberately does **not** prescribe how to locate a muzzle component,
because that depends on the caller (weapon entity, manager, test harness, editor
tool, etc.). Passing the real runtime `BaseMuzzleComponent` is important:
`GetAimHeightOfNextProjectile` evaluates the **next projectile shot with that
muzzle**.

Default search parameters:

- coarse step: 100 m;
- precision: 1 m;
- probe ceiling: 20,000 m;
- direct fire: true.

Return codes:

- `-1`: invalid input;
- `-2`: no maximum boundary found before the configured probe ceiling.

## ARMST data-quality warning

A ballistic-table range is only meaningful if the projectile is paired with an
appropriate generated ballistic table.

The current catalog contains known cross-caliber table reuse. Examples include:

- current ARMST 9x39 SP-5 -> `AIBT_762x54r_Ball_7N1.conf`;
- current ARMST 7.63x25 Ball -> `AIBT_9x19_Ball_M882.conf`.

These are source-backed facts and must not be silently "corrected", but they mean
the returned range may describe the assigned/stale AIBT rather than a freshly
generated table matching the projectile's current `InitSpeed` and `AirDrag`.

Before using probe output to populate a canonical spreadsheet field:

1. confirm the actually loaded projectile;
2. confirm its assigned ballistic-table config;
3. generate/re-generate the table in Workbench when appropriate;
4. run this probe;
5. record the result together with projectile + table provenance.

## Relationship to the overview spreadsheet

Keep these values separate:

```text
Max sight range        = max(SightsRanges.Y)
Max ballistic range    = BallisticTable boundary where time changes to < 0
Dispersion reference   = DispersionRange
```

The existing overview column `Дальность, м` should not be reinterpreted as
ballistic-table range until its intended semantics are explicitly changed.


## Read-only snapshot inspection before Workbench

The repository already contains evidence that a vanilla weapon/config dataset was
materialized locally in the resolver-v2 research flow, while
`Imported/VanillaSources/` itself was intentionally kept out of Git.

Before relying on the runtime probe, inspect any surviving local materialized
AIBT snapshot with:

```bat
python agent\scripts\inspect_aiballistic_snapshot.py ^
  --output agent\aibt_snapshot_inspection.json
```

Default reference configs:

- `AIBT_545x39_Ball_7N6.conf`
- `AIBT_556x45_Ball_M855.conf`
- `AIBT_762x54r_Ball_7N1.conf`
- `AIBT_9x39_Ball_SP5.conf`

Use `--all` to inspect every materialized AIBT config.

The inspector is deliberately semantic-neutral. It records the parsed config
tree, numeric leaves and 3-number leaves as structural candidates only. It does
not assume which serialized field is distance, aim height or time until the
actual snapshot shape has been reviewed.

This ordering is preferred:

1. inspect the existing materialized AIBT snapshot;
2. establish the exact serialized `BallisticTableArray` shape from evidence;
3. add a source-backed offline max-range extractor;
4. use the Workbench/runtime probe only as an independent cross-check.
