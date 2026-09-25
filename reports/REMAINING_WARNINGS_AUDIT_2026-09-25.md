# Remaining Data-Quality Warnings Audit — 2026-09-25

> Status: CURRENT AUDIT. This report classifies the 12 warnings present on canonical main after the scanner-hardening rescan. It does not substitute reference-only evidence for live primary-addon or Workbench evidence.

Baseline:

**0 errors · 12 warnings · 15 info**

Warnings:

- 10 × `MAG_CAPACITY_UNRESOLVED`
- 2 × `PROJECTILE_DAMAGE_UNRESOLVED`

## Summary

The 12 warnings do not have one root cause.

| Class | Count | Treatment |
|---|---:|---|
| Local scanner component-selection gap | 3 | Fix scanner, then canonical rescan |
| Imported vanilla structured-reference evidence available | 7 | Preserve as reference evidence; do not silently promote to canonical |
| Imported projectile reference evidence available; live value unverified | 2 | Preserve reference DamageValue evidence; keep canonical warning until Workbench-mounted/base-game verification |

## A. Local scanner component-selection gap — 3 warnings

Affected catalog rows:

- `catalog/magazines/magazine_545x39_ak_30rnd_base.json`
- `catalog/magazines/armst_magazine_545x39_ak_30rnd_ball.json`
- `catalog/magazines/armst_magazine_545x39_ak_30rnd_tracer.json`

Their inheritance chains are fully local in the primary ARMST addon, but the current catalog contains only inventory/grid data and misses magazine gameplay fields.

The classifier already finds `MagazineComponent` recursively. The legacy extractor previously selected only a top-level component from `components`, so a nested/duplicate functional component could classify the entity as a magazine while still hiding `MaxAmmo`, `AmmoConfig` or `AmmoMapping`.

Current audit branch fix:

- search all resolved `MagazineComponent` instances recursively;
- score candidates by direct gameplay-field presence;
- prefer `AmmoConfig`, then `AmmoMapping`, `MaxAmmo`, `MagazineWell`;
- do not infer capacity from filename.

Expected resolution requires a fresh canonical rescan; no capacity value is written manually.

Classification: **FIX_SCANNER / RESCAN_REQUIRED**.

## B. Imported vanilla magazine reference evidence — 7 warnings

Affected ARMST catalog rows:

- `armst_magazine_545x39_rpk_45rnd_ball`
- `armst_magazine_545x39_rpk_45rnd_tracer`
- `armst_magazine_762x54_svd_10rnd_7bz3api`
- `armst_magazine_763x25_tt_8rnd_ball`
- `armst_magazine_9x18_pm_8rnd_ball`
- `armst_magazine_9x18_pm_8rnd_ball_bp`
- `armst_magazine_9x18_pm_8rnd_ball_pp`

Their current primary-addon inheritance stops at external base-game parent resources.

A read-only inspection of the local `Weapon_ARMA_X` Workbench/reference folder reported three materialized imported vanilla parents with adjacent metadata explicitly classifying them under `Imported/VanillaSources`:

| External parent | ARMST/live reference GUID | Imported local GUID | Explicit imported reference evidence |
|---|---|---|---|
| `Magazine_545x39_RPK_45rnd_Base.et` | `9569026177545A20` | `5208782369C978F0` | `MaxAmmo 45`, `MagazineWellAK545`, 45-entry `AmmoMapping`, 5.45 AmmoConfig |
| `Magazine_762x54_SVD_10rnd_Base.et` | `761A03A9C5BA8D68` | `593B9ED625EF311D` | `MaxAmmo 10`, `MagazineWellSVD`, 10-entry `AmmoMapping`, 7.62×54 AmmoConfig |
| `Magazine_9x18_PM_8rnd_Base.et` | `9B5AA2C731485ACA` | `01733565DD4B5DA3` | `MaxAmmo 8`, `MagazineWellMakarovPM`, 8-entry `AmmoMapping`, 9×18 AmmoConfig |

The existing supplied `indexes/magazine_reference/` independently corroborates the same RPK/SVD/PM family capacities, but supplied indexes remain lower-authority reference material.

The imported resources are not under the canonical primary ARMST scan root and are explicitly materialized/reference copies. Therefore their values must not silently populate canonical `derived.capacity` as if they came from current live base-game resources.

Current audit branch adds:

`agent/scripts/imported_vanilla_reference.py`

The adapter:

- is opt-in;
- scans exactly four fixed imported parent filenames: three magazines plus the 7.62×54R projectile parent;
- treats the GUID in imported metadata as a **local import GUID**, not as the live/base-game GUID;
- verifies identity by the declared `Imported/VanillaSources/<original resource path>`;
- retains the ARMST/live reference GUID separately as cross-reference provenance;
- parses magazine `MaxAmmo`, `AmmoMapping`, `AmmoConfig`, `MagazineWell`;
- parses projectile `ProjectileDamage` / `DamageValue` when explicitly serialized;
- records SHA-256 for `.et` and `.meta`;
- labels all output `STRUCTURED_REFERENCE_SOURCE`;
- marks `canonical_authority = false`;
- does not modify canonical catalog/checker output.

Classification: **STRUCTURED_REFERENCE_SOURCE / CORROBORATED_EXTERNAL_PARENT**.

Workbench-mounted verification remains preferred before promoting these values as current-game canonical base-game evidence.

## C. Projectile DamageValue reference evidence — 2 warnings

Affected rows:

- `catalog/ammunition/armst_ammo_763x25.json`
- `catalog/ammunition/armst_ammo_9x39_sp5_ball.json`

Both canonical ARMST catalog rows still expose `ProjectileDamage` while `DamageValue`, `DamageType` and `MinimumDamage` remain unresolved/null in the current primary-addon snapshot.

The repository audit found a physical imported vanilla reference copy of:

`Ammo_762x54r_Ball_57N323S.et`

with imported local GUID:

`CABAABDCADDAB3EE`

and declared original identity:

`Imported/VanillaSources/Prefabs/Weapons/Ammo/Ammo_762x54r_Ball_57N323S.et`

ARMST/catalog references use live/reference GUID:

`AC29AE3D5ECD6390`

The GUIDs are intentionally different identities: the first is the local materialized import GUID, while the second is the GUID observed by ARMST references. The imported reference explicitly serializes:

`ProjectileDamage -> DamageValue 130`

This is strong **STRUCTURED_REFERENCE_SOURCE** evidence for the materialized vanilla snapshot. It is not automatically current live base-game authority.

Therefore:

- do not copy `130` directly into canonical ARMST catalog output;
- do not remove the two `PROJECTILE_DAMAGE_UNRESOLVED` warnings solely from the imported snapshot;
- use RWTK/Workbench-mounted evidence to verify the current base-game resource/effective inheritance before promotion.

Classification: **STRUCTURED_REFERENCE_SOURCE_AVAILABLE / LIVE_WORKBENCH_VERIFICATION_REQUIRED / KEEP_WARNING**.

## Trust boundary

Evidence order for this audit:

1. current primary ARMST addon / Workbench-mounted effective values;
2. Workbench-validated authoring/runtime evidence;
3. canonical generated ARMST snapshot;
4. imported vanilla structured references;
5. supplied/reference indexes;
6. filenames/historical notes.

A lower layer may corroborate a higher-layer hypothesis but must not be promoted silently.

## Next validation sequence

1. Run the audit branch scanner against the authoritative primary ARMST addon.
2. Require source hash guard PASS.
3. Check whether the three local 5.45 AK capacity warnings disappear from source-backed extraction.
4. Run `imported_vanilla_reference.py` against the local `Weapon_ARMA_X` checkout and retain its four-target JSON as reference evidence only; imported identity must match declared original resource path, not live GUID.
5. Confirm the imported projectile snapshot reports explicit `DamageValue 130` while `canonical_authority=false`.
6. Run RWTK Weapon Evidence Scanner V1 in Workbench for current mounted-game verification, especially `Ammo_762x54r_Ball_57N323S.et`.
7. Reclassify/promote values only after the appropriate evidence level is available.

No warning should be removed merely because a filename contains `30rnd`, `45rnd`, `10rnd` or `8rnd`.
