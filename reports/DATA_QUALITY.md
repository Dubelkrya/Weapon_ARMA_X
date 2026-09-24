# Weapon catalog data quality

> [!IMPORTANT]
> **Status: CURRENT QUALITY GUIDE + SNAPSHOT FINDINGS.** This document records confirmed catalog-quality problems and the rules used to detect them. It does not override the live ARMST addon or Workbench evidence.

The repository now has a read-only checker at `agent/scripts/check_data_quality.py`. It scans weapon, magazine, ammunition and config-reference data for contradictions and coverage gaps without inventing missing gameplay values.

## Severity model

- **ERROR** — two explicit checked-in fields contradict each other.
- **WARNING** — a value or relationship needed for safe authoring is unresolved or missing from the current generated/reference coverage.
- **INFO** — a suspicious relationship is worth reviewing but may be intentional, such as cross-caliber inheritance or ballistic-table reuse.

Current CI runs the checker in **non-blocking mode**. Findings are printed into the workflow summary, but known existing data-quality problems do not make `main` fail. A blocking threshold can be enabled later after the baseline is cleaned.

## Current automated scan summary

The current checked-in snapshot reports **6 errors, 41 warnings and 22 informational findings**.

| Finding class | Count | Meaning in the current snapshot |
|---|---:|---|
| `MAG_CALIBER_ID_MISMATCH` | 6 | All six are the explicit 9×39 → 5.45×39 `caliber_id` contradiction documented below |
| `AMMO_CONFIG_NOT_INDEXED` | 11 | Referenced configs are absent from the current `config_reference/ammo_configs.json` coverage |
| `MAG_CAPACITY_UNRESOLVED` | 20 | A capacity token exists in the resource name, but the catalog does not resolve capacity; the name is not used as the gameplay value |
| `PROJECTILE_DAMAGE_UNRESOLVED` | 2 | ProjectileDamage exists but damage is unresolved in the catalog |
| `WEAPON_MAGAZINE_NOT_CATALOGED` | 8 | A weapon links to a magazine not covered by the current magazine catalog snapshot |
| `AMMO_MAPPING_EMPTY` | 12 | Capacity is resolved but serialized mapping is empty, so loaded projectile composition is not proven |
| `CROSS_CALIBER_BALLISTIC_TABLE` | 4 | Cross-caliber table reuse is visible and requires review, not automatic correction |
| `CROSS_CALIBER_PARENT` | 6 | Cross-caliber projectile inheritance is visible and may be intentional |

These counts are a snapshot. The GitHub Actions data-quality step is the live view after future catalog changes.

## Checks

The checker currently looks for:

- magazine resource caliber vs explicit `caliber_id` contradictions;
- filename capacity tokens such as `20rnd` / `30rnd` vs resolved `max_ammo`;
- magazine `AmmoConfig` references missing from `indexes/config_reference/ammo_configs.json`;
- resolved magazine capacity with an empty serialized `ammo_mapping`;
- projectile `ProjectileDamage` components whose `DamageValue` is unresolved;
- cross-caliber projectile parent / ballistic-table references;
- weapon magazine references that are absent from `catalog/magazines`.

A filename may trigger a consistency check, but it is **never used as the missing gameplay value**.

## Confirmed current 9×39 findings

### Explicit caliber-ID contradiction

The current 9×39 magazine catalog entries expose `#AR-AmmunitionID_545x39mm` as `caliber_id`, despite their source resources and `AmmoConfig` being 9×39.

Affected checked-in entries include:

- [`Magazine_9x39_20rnd_9a91_SP5.et`](../catalog/magazines/magazine_9x39_20rnd_9a91_sp5.json)
- [`Magazine_9x39_20rnd_9a91_SP6.et`](../catalog/magazines/magazine_9x39_20rnd_9a91_sp6.json)
- [`Magazine_9x39_20rnd_vss_SP5.et`](../catalog/magazines/magazine_9x39_20rnd_vss_sp5.json)
- [`Magazine_9x39_20rnd_vss_SP6.et`](../catalog/magazines/magazine_9x39_20rnd_vss_sp6.json)
- [`Magazine_9x39_30rnd_val_SP5.et`](../catalog/magazines/magazine_9x39_30rnd_val_sp5.json)
- [`Magazine_9x39_30rnd_val_SP6.et`](../catalog/magazines/magazine_9x39_30rnd_val_sp6.json)

The checker classifies this as **ERROR** because both sides are explicit catalog fields. It does not automatically rewrite the value.

### AmmoMapping coverage gap

Those 9×39 magazine records currently have empty serialized `ammo_mapping` arrays. Therefore the checked-in snapshot does not prove which projectile is actually loaded in an SP5/SP6-named magazine.

This is intentionally not resolved from the filename. See [the 9×39 balance report](balance/CALIBER_9X39_BALANCE.md).

### VAL capacity unresolved

The checked-in VAL magazine resources contain `30rnd` in their resource names, but the current catalog does not resolve `max_ammo` or a derived capacity.

The checker reports this as **WARNING**, not as “capacity = 30”. The live primary addon must supply the authoritative value.

### AmmoConfig reference coverage

Current 9×39 magazines reference `Configs/Weapons/Ammo/Ammo_9x39.conf`, while the checked-in `indexes/config_reference/ammo_configs.json` snapshot does not contain a 9×39 config entry.

That is a reference-index coverage gap until the primary-addon config snapshot is refreshed.

### Projectile evidence boundary

The current ARMST catalog has:

- `Ammo_9x39_SP5_Ball.et`: unresolved `DamageValue`, 290 m/s, mass 0.01959 kg, penetration depth 3.7, penetration speed 615;
- `Ammo_9x39_SP6_Ball.et`: explicit `DamageValue = 150`, 305 m/s, mass 0.02559 kg, penetration depth 3.7, penetration speed 615.

Both currently reference `AIBT_762x54r_Ball_7N1.conf`. The checker reports this kind of cross-caliber ballistic-table reference as **INFO**, because reuse can be intentional and should not be “fixed” automatically.

Older `Weapons.zip` reference rows use different 9×39 projectile resources and different penetration values. They remain separate historical/reference evidence and must not be merged into the current ARMST resources by name similarity.

## Running the check

Human-readable output:

```bash
python agent/scripts/check_data_quality.py
```

Markdown output suitable for a CI summary:

```bash
python agent/scripts/check_data_quality.py --markdown
```

Optional blocking modes exist for later cleanup:

```bash
python agent/scripts/check_data_quality.py --fail-on error
python agent/scripts/check_data_quality.py --fail-on warning
```

Do not enable a blocking threshold until the existing baseline has been reviewed and the intended exceptions are documented.
