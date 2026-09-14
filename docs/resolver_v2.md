# Resolver v2 — Workbench materialize-first workflow

Resolver v2 does **not** require a separately unpacked vanilla Arma Reforger data tree.

The authoritative flow is:

`mounted $ArmaReforger resources -> Workbench materializer -> Imported/VanillaSources -> resolver v2 -> derived catalog/reports`

Raw/materialized vanilla files remain local and are gitignored. Only semantic/resolved data is considered for later catalog promotion.

## 1. Inputs

- ARMST root: local/workbench source root of `ARMST-PLATFORM---Weapons`.
- Weapon_ARMA_X checkout: opened as a Workbench addon.
- Base Arma Reforger dependency: GUID `58D0FB3206B6F859`, which mounts `$ArmaReforger:` inside Workbench.

There is no prerequisite `C:\vanilla\...` directory.

## 2. Materialize vanilla weapon resources in Workbench

Open the `agent/resolver-v2` checkout as the `Weapon_ARMA_X` addon in Arma Reforger Workbench, then run the Resource Manager plugin:

`WAX: Materialize Vanilla Weapon Dataset`

The plugin searches mounted base-game resources under:

- `$ArmaReforger:Prefabs/Weapons` for `.et` and `.conf` resources;
- `$ArmaReforger:Configs/Weapons` for `.conf` resources.

It writes them into this addon under:

- `Imported/VanillaSources/Prefabs/Weapons/...`
- `Imported/VanillaSources/Configs/Weapons/...`

The vanilla-relative directory structure is intentionally preserved. A live reference such as:

`{GUID}Prefabs/Weapons/Rifles/AK74/Rifle_AK74_base.et`

therefore resolves against the Python resource root:

`Imported/VanillaSources`

without path rewriting.

The materializer first tries to copy a physical text source exposed by Workbench. If that source is unavailable because the mounted game resource is packed, it falls back to loading the mounted resource and serializing its `BaseContainer` into the addon.

A local manifest is written to:

`Imported/VanillaSources/_wax_materialization.tsv`

with source path, destination-relative path, materialization method and status.

A second plugin, `WAX: Materialize Selected Vanilla Sources`, remains available for targeted debugging of selected `$ArmaReforger:` `.et/.conf` resources.

## 3. Run resolver v2

After Workbench materialization, from the repository root run:

```bat
agent\run_resolver_v2.bat
```

The launcher uses, by default:

`%REPO_ROOT%\Imported\VanillaSources`

as its vanilla/materialized resource root. You only need to set `VANILLA_ROOT` if you intentionally materialized to another location.

The resolver reads the copied files from the addon. It does not expect direct filesystem access to the base game's packed data.

## 4. Output

Resolver v2 writes only to:

`agent/v2_output/`

It does **not** overwrite legacy `catalog/`, `indexes/`, or `reports/` yet.

Important reports:

- `agent/v2_output/reports/scan_summary_v2.json`
- `agent/v2_output/reports/anomalies_v2.json`
- `agent/v2_output/reports/resolver_v2_diff.json`
- `agent/v2_output/reports/reference_cases_v2.json`

## 5. What v2 resolves

1. `.et` parent inheritance across ARMST and materialized base-game resources.
2. Instance overrides by serialized instance GUID/ID.
3. Non-ID fields by `name + same-name occurrence`.
4. Nested `.conf` templates such as FireMode and recoil configs.
5. `MagazineTemplate -> MagazineComponent -> AmmoConfig -> AmmoResourceArray -> AmmoMapping`.
6. Per-projectile physical fields from `ShellMoveComponent`.
7. Effective muzzle velocity per actually mapped projectile: `InitSpeed x BulletInitSpeedCoef`.
8. AI ballistic-table validation separately from projectile physics.

## 6. Promotion gate

Do not replace the legacy catalog until all of these are true:

1. Resolver v2 Python CI is green.
2. Workbench compiles the materializer plugin successfully.
3. `WAX: Materialize Vanilla Weapon Dataset` completes and creates the preserved `Prefabs/...` / `Configs/...` tree.
4. A real ARMST + materialized-vanilla resolver scan completes.
5. `resolver_v2_diff.json` is reviewed for systematic changes.
6. AK/VSS/SVD/VZ58/PKM/RPK/M16/M21 reference cases match manual verification.
7. Remaining `partial` chains correspond to genuinely missing/unserializable resources rather than parser defects.
8. `Imported/VanillaSources` remains uncommitted.
