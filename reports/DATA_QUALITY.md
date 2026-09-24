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

**Status as of the canonical rescan on 2026-09-24:** the snapshot on this branch reports **0 errors, 59 warnings and 30 informational findings**.

| Finding class | Count | Meaning in the current snapshot |
|---|---:|---|
| `AMMO_CONFIG_NOT_INDEXED` | 35 | Referenced configs are absent from the current `config_reference/ammo_configs.json` coverage (incl. `Configs/Weapons/Ammo/armst_Ammo_9x39.conf`) |
| `MAG_CAPACITY_UNRESOLVED` | 18 | A capacity token exists in the resource name, but the catalog does not resolve capacity; the name is not used as the gameplay value (incl. VAL 30rnd) |
| `PROJECTILE_DAMAGE_UNRESOLVED` | 2 | ProjectileDamage exists but damage is unresolved in the catalog |
| `WEAPON_MAGAZINE_NOT_CATALOGED` | 4 | A weapon links to a magazine not covered by the current magazine catalog snapshot |
| `AMMO_MAPPING_EMPTY` | 20 | Capacity is resolved but serialized mapping is empty, so loaded projectile composition is not proven (INFO) |
| `CROSS_CALIBER_BALLISTIC_TABLE` | 4 | Cross-caliber table reuse is visible and requires review, not automatic correction (INFO) |
| `CROSS_CALIBER_PARENT` | 6 | Cross-caliber projectile inheritance is visible and may be intentional (INFO) |
| `MAG_CALIBER_ID_MISMATCH` | 0 | **Resolved** — see incident record below |

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

## Incident record: 6 × `MAG_CALIBER_ID_MISMATCH` (resolved as `STALE_SNAPSHOT`)

### Old snapshot (baseline, `main` @ `659fe31`)

- `scan_date`: **2026-09-14**, committed snapshot from the pre-relocation primary addon.
- `mod_root` in `agent/scan_state.json`: `C:\Users\Muroy\...\ARMST-PLATFORM---Weapons`.
- Snapshot stats: 124 entities / 55 weapons / 32 magazines / 14 ammunition / 3 optics.
- Six 9×39 magazine entries exposed `caliber_id = #AR-AmmunitionID_545x39mm` (from the old `Ammo_545x39` era of the live files) while their resources were 9×39 → 6 × `MAG_CALIBER_ID_MISMATCH` (ERROR).

### Root cause

The old snapshot was generated **before** the 9×39 magazine relocation/rebuild (`Prefabs/Weapons/Magazines/9x39/...` → `Prefabs/Weapons/Magazines/Russian/9x39/{9a91,VSS,Groza}/armst_Magazine_9x39_*.et`) and before the live files switched to `m_sAmmoCaliber "#AR-ARMST_AmmunitionID_9x39mm"`. The six mismatches were a **stale snapshot**, not a live addon defect — the live addon contained no 5.45×39 magazine with those GUIDs.

### Resolution

Canonical read-only rescan on **2026-09-24** (branch `agent/primary-addon-canonical-rescan`) against the current authoritative live root `C:\Users\yshky\...\ARMST-PLATFORM---Weapons`:

- `agent/scan_state.json`: `scan_date` **2026-09-24**, `mod_root` updated to the `yshky` path; snapshot stats 158 entities / 63 weapons / 48 magazines / 19 ammunition / 9 optics.
- All **8** live 9×39 magazines now cataloged under new relocation paths; `caliber_id` is `#AR-ARMST_AmmunitionID_9x39mm` on every entry.
- **GUID continuity confirmed** — the six previously-mismatched magazines keep their live GUIDs: `B7EC6D4222AE12BE` (9a91 SP5), `3F47C33B88171646` (9a91 SP6), `70D023F899C9C226` (VSS SP5), `51E9CE2EB27B3DBD` (VSS SP6), `6C22F58BBF5D6AED` (VAL SP5), `6CBF1E50EB22F09B` (VAL SP6). Two Groza entries are new live additions: `77215B3A185D1EFD`, `168348351F5C3F54`.
- Catalog filenames changed to the `armst_*` slugs consistent with the live `armst_Magazine_9x39_*.et` basenames (the old non-prefixed slugs are gone).
- Checker result after rescan: **6 × `MAG_CALIBER_ID_MISMATCH` → 0**. No value was masked or hand-corrected; the contradictory `caliber_id` values no longer exist in the regenerated snapshot.

### Out of scope / not "fixed" during rescan

- `AmmoMapping` arrays remain empty in the 9×39 magazine entries — serialized `AmmoMapping` with zeroed entries is not proven load composition. Not corrected manually.
- VAL 30rnd `max_ammo` / `derived.capacity` is **not resolved** (live file has no `MaxAmmo`, only a 30-slot `AmmoMapping`). The check reports `MAG_CAPACITY_UNRESOLVED` and does **not** substitute `30` from the filename.
- `Configs/Weapons/Ammo/armst_Ammo_9x39.conf` is referenced (and exists in the live addon) but absent from `indexes/config_reference/ammo_configs.json` → `AMMO_CONFIG_NOT_INDEXED` (coverage gap, blocker for projectile-proofing, not data corruption).
- 9×39 projectiles still reference `AIBT_762x54r_Ball_7N1.conf` (`CROSS_CALIBER_BALLISTIC_TABLE`, INFO) and inherit from `Ammo_762x54r_Ball_57N323S.et` (`CROSS_CALIBER_PARENT`, INFO) — recorded separately, not auto-fixed.

## Remaining open 9×39 items (after rescan)

### AmmoMapping coverage gap

The 9×39 magazine records have empty serialized `ammo_mapping` arrays. Therefore the checked-in snapshot does not prove which projectile is actually loaded in an SP5/SP6-named magazine.

This is intentionally not resolved from the filename. See [the 9×39 balance report](balance/CALIBER_9X39_BALANCE.md).

### VAL capacity unresolved

The checked-in VAL magazine resources contain `30rnd` in their resource names, but the current catalog does not resolve `max_ammo` or a derived capacity.

The checker reports this as **WARNING**, not as “capacity = 30”. The live primary addon must supply the authoritative value (`MaxAmmo` or a provable serialized mapping).

### AmmoConfig reference coverage

The 9×39 magazines reference `Configs/Weapons/Ammo/armst_Ammo_9x39.conf`, while the checked-in `indexes/config_reference/ammo_configs.json` snapshot does not contain that entry (it was generated from `Configs.zip`, not from the live addon).

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