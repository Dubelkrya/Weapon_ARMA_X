# Resolver v2 — Workbench runbook

Resolver v2 reads ARMST and materialized vanilla resources as separate roots. It never copies raw vanilla source into the public catalog. Only semantic values, provenance, derived metrics, and anomaly reports are exported.

## Inputs

- ARMST root: the unpacked/workbench source root of `ARMST-PLATFORM---Weapons`.
- Vanilla root(s): a materialized mirror that preserves base-game resource paths such as `Prefabs/Weapons/...` and `Configs/Weapons/...`.
- Repository root: `Weapon_ARMA_X` checkout containing `agent/scripts` and the legacy `catalog/` for v1/v2 comparison.

The materialized vanilla root may be the `Imported/VanillaSources` directory produced by the Weapon_ARMA_X Workbench materializer, as long as the directory beneath it starts with the same resource paths referenced by prefabs (`Prefabs/...`, `Configs/...`).

## Recommended command on Windows

```bat
cd /d C:\path\to\Weapon_ARMA_X

python agent\scripts\scan_build_v2.py ^
  --armst-root "C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons" ^
  --vanilla-root "base=C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\Weapon_ARMA_X-agent-weapon-intelligence-v1\Imported\VanillaSources" ^
  --repo-root .
```

If vanilla resources are split across several materialized roots, repeat `--vanilla-root`:

```bat
  --vanilla-root "weapons=C:\materialized\weapons" ^
  --vanilla-root "configs=C:\materialized\configs"
```

Higher-priority path collisions are resolved in this order: ARMST first, then vanilla roots in command-line order.

## Output

By default v2 writes only to:

`agent/v2_output/`

It does **not** overwrite the legacy `catalog/`, `indexes/`, or `reports/` yet.

Important files:

- `agent/v2_output/catalog/` — v2 semantic catalog (`local`, `resolved`, provenance).
- `agent/v2_output/indexes/` — entity indexes with resolution status.
- `agent/v2_output/reports/scan_summary_v2.json` — counts and resolution coverage.
- `agent/v2_output/reports/anomalies_v2.json` — parser/resolver/ammo/AIBT warnings.
- `agent/v2_output/reports/resolver_v2_diff.json` — field-by-field legacy v1 → v2 differences.
- `agent/v2_output/reports/resolver_v2_diff.md` — readable first 500 differences.

## What v2 resolves

1. `.et` parent inheritance across ARMST and vanilla roots.
2. Instance overrides by serialized instance GUID/ID.
3. Non-ID fields by `name + same-name occurrence`, not absolute sibling index.
4. Nested `.conf` templates such as FireMode and recoil configs.
5. `MagazineTemplate → MagazineComponent → AmmoConfig → AmmoResourceArray → AmmoMapping`.
6. Per-projectile physical fields from `ShellMoveComponent`.
7. Effective muzzle velocity per actually mapped projectile: `InitSpeed × BulletInitSpeedCoef`.
8. AI ballistic-table validation separately from projectile physics.

## Promotion gate

Do not replace the legacy catalog until all of these are true:

1. Resolver v2 CI is green.
2. A real ARMST + materialized vanilla scan completes without parser errors.
3. `resolver_v2_diff.json` is reviewed for large systematic changes.
4. Known reference cases match manual verification: AK-74 family, VSS/VAL/VSK-94/9A-91, SVD, VZ58, PKM/RPK-74, M16/M21.
5. Remaining `partial` chains correspond to genuinely missing resources, not parser/extractor defects.
6. No raw vanilla source is present in the committed output.
