# 9×39 balance comparison

> [!IMPORTANT]
> **Status: GENERATED ANALYSIS / NOT A BALANCE POLICY.** Values come from the current checked-in catalog. Unknown values remain unknown. No projectile is assigned to a magazine from its filename.

This report keeps three evidence layers separate: weapon handling, magazine capacity/compatibility, and projectile lethality/penetration.

## Weapon handling

| Weapon entry | Role | Magazine | Capacity | Mag well | RPM | Velocity coef | Dispersion | Warnings |
|---|---|---|---:|---|---:|---:|---|---:|
| [`armst_rifle_9a91`](../../catalog/weapons/armst_rifle_9a91.json) | leaf | `armst_Magazine_9x39_20rnd_9a91_SP5.et` | 20 | `MagazineWell9x39_9a91` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 0 |
| [`armst_rifle_9a91_base`](../../catalog/weapons/armst_rifle_9a91_base.json) | base | `armst_Magazine_9x39_20rnd_9a91_SP5.et` | 20 | `MagazineWell9x39_9a91` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 0 |
| [`armst_rifle_groza`](../../catalog/weapons/armst_rifle_groza.json) | leaf | `armst_Magazine_9x39_Groza_20rnd_SP5.et` | 20 | `MagazineWell9x39` | 750 | — | D=0.058, R=100, 1.994 MOA | 0 |
| [`armst_rifle_groza_base`](../../catalog/weapons/armst_rifle_groza_base.json) | base | `armst_Magazine_9x39_Groza_20rnd_SP5.et` | 20 | `MagazineWell9x39` | 750 | — | D=0.058, R=100, 1.994 MOA | 0 |
| [`armst_rifle_val`](../../catalog/weapons/armst_rifle_val.json) | leaf | `armst_Magazine_9x39_30rnd_val_SP5.et` | 30 | `MagazineWell9x39` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 0 |
| [`armst_rifle_val_base`](../../catalog/weapons/armst_rifle_val_base.json) | base | `armst_Magazine_9x39_30rnd_val_SP5.et` | 30 | `MagazineWell9x39` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 0 |
| [`armst_rifle_vsk94`](../../catalog/weapons/armst_rifle_vsk94.json) | leaf | `Magazine_9x39_20rnd_9a91_SP5.et` | — | `MagazineWell9x39_9a91` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 0 |
| [`armst_rifle_vsk94_base`](../../catalog/weapons/armst_rifle_vsk94_base.json) | base | `Magazine_9x39_20rnd_9a91_SP5.et` | — | `MagazineWell9x39_9a91` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 0 |
| [`armst_rifle_vss`](../../catalog/weapons/armst_rifle_vss.json) | leaf | `armst_Magazine_9x39_20rnd_vss_SP5.et` | 20 | `MagazineWell9x39` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 0 |
| [`armst_rifle_vss_base`](../../catalog/weapons/armst_rifle_vss_base.json) | base | `armst_Magazine_9x39_20rnd_vss_SP5.et` | 20 | `MagazineWell9x39` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 0 |

### Handling snapshot

All current 9×39 weapon entries resolve to 700 RPM, velocity coefficient 0.835 and dispersion 0.4 at 200 (approximately 6.875 MOA). Capacity is shown only when the linked magazine catalog resolves it.

## Magazine layer

| Magazine | Capacity | Mag well | AmmoConfig | AmmoMapping entries | Caliber ID | Warnings |
|---|---:|---|---|---:|---|---:|
| [`armst_Magazine_9x39_20rnd_9a91_SP5.et`](../../catalog/magazines/armst_magazine_9x39_20rnd_9a91_sp5.json) | 20 | `MagazineWell9x39_9a91` | `armst_Ammo_9x39.conf` | 20 | `#AR-ARMST_AmmunitionID_9x39mm` | 0 |
| [`armst_Magazine_9x39_20rnd_9a91_SP6.et`](../../catalog/magazines/armst_magazine_9x39_20rnd_9a91_sp6.json) | 20 | `MagazineWell9x39_9a91` | `armst_Ammo_9x39.conf` | 20 | `#AR-ARMST_AmmunitionID_9x39mm` | 0 |
| [`armst_Magazine_9x39_20rnd_vss_SP5.et`](../../catalog/magazines/armst_magazine_9x39_20rnd_vss_sp5.json) | 20 | `MagazineWell9x39` | `armst_Ammo_9x39.conf` | 20 | `#AR-ARMST_AmmunitionID_9x39mm` | 0 |
| [`armst_Magazine_9x39_20rnd_vss_SP6.et`](../../catalog/magazines/armst_magazine_9x39_20rnd_vss_sp6.json) | 20 | `MagazineWell9x39` | `armst_Ammo_9x39.conf` | 20 | `#AR-ARMST_AmmunitionID_9x39mm` | 0 |
| [`armst_Magazine_9x39_30rnd_val_SP5.et`](../../catalog/magazines/armst_magazine_9x39_30rnd_val_sp5.json) | 30 | `MagazineWell9x39` | `armst_Ammo_9x39.conf` | 30 | `#AR-ARMST_AmmunitionID_9x39mm` | 0 |
| [`armst_Magazine_9x39_30rnd_val_SP6.et`](../../catalog/magazines/armst_magazine_9x39_30rnd_val_sp6.json) | 30 | `MagazineWell9x39` | `armst_Ammo_9x39.conf` | 30 | `#AR-ARMST_AmmunitionID_9x39mm` | 0 |
| [`armst_Magazine_9x39_Groza_20rnd_SP5.et`](../../catalog/magazines/armst_magazine_9x39_groza_20rnd_sp5.json) | 20 | `MagazineWell9x39` | `armst_Ammo_9x39.conf` | 20 | `#AR-ARMST_AmmunitionID_9x39mm` | 0 |
| [`armst_Magazine_9x39_Groza_20rnd_SP6.et`](../../catalog/magazines/armst_magazine_9x39_groza_20rnd_sp6.json) | 20 | `MagazineWell9x39` | `armst_Ammo_9x39.conf` | 20 | `#AR-ARMST_AmmunitionID_9x39mm` | 0 |

> [!WARNING]
> Current 9×39 magazine records have empty serialized `ammo_mapping` arrays, so this snapshot does **not** prove which projectile is actually loaded in each magazine. The generator therefore does not infer SP5/SP6 from filenames.

> [!WARNING]
> Current 9×39 magazine records expose `#AR-AmmunitionID_545x39mm` as `caliber_id`. This is recorded as a catalog/data-quality anomaly, not silently corrected here.

> [!WARNING]
> The VAL files named `30rnd` do not resolve `max_ammo` / derived capacity in the current catalog. Capacity remains unknown here rather than being inferred from the filename.

## Projectile layer

| Projectile | Init speed | Mass | Damage | Penetration depth | Penetration speed | Air drag | Dispersion mult | Ballistic table | Warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| [`armst_Ammo_9x39_SP5_Ball.et`](../../catalog/ammunition/armst_ammo_9x39_sp5_ball.json) | 290 | 0.01959 | — | 3.7 | 615 | 9.4e-06 | 0.55 | `AIBT_762x54r_Ball_7N1.conf` | 0 |
| [`armst_Ammo_9x39_SP6_Ball.et`](../../catalog/ammunition/armst_ammo_9x39_sp6_ball.json) | 305 | 0.02559 | 150 | 5.55 | 615 | 9.4e-06 | 0.55 | `AIBT_762x54r_Ball_7N1.conf` | 0 |

### What the current projectile snapshot actually proves

- `Ammo_9x39_SP6_Ball.et` has an explicit local `DamageValue` of **150**.
- `Ammo_9x39_SP5_Ball.et` does **not** expose a resolved local/inherited damage value in the current catalog, so its damage remains unknown here.
- Both current catalog projectiles resolve `PenetrationDepth = 3.7` and `PenetrationSpeed = 615`.
- SP5 resolves 290 m/s and mass 0.01959 kg; SP6 resolves 305 m/s and mass 0.02559 kg.
- Both reference `AIBT_762x54r_Ball_7N1.conf` in the current catalog snapshot.

## Authority boundary

The older `indexes/ammunition_reference/part-06.json` contains different 9×39 SP5/SP6 resources from `Weapons.zip` (`Ammo_9x39_Ball_SP5.et` / `Ammo_9x39_AP_SP6.et`) with different penetration values. Those older reference rows are useful historical/source evidence but must not be merged into the current ARMST projectile rows as if they were the same resources.

Before making balance changes, resolve the current `Ammo_9x39.conf` resource list and serialized magazine `AmmoMapping` from the primary addon, then validate one projectile/magazine family at a time in Workbench.
