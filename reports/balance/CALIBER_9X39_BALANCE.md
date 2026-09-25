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

The handling rows above are generated from the current catalog. Capacity is shown only when the linked magazine catalog resolves it; RPM, velocity coefficient and dispersion remain per-entry evidence rather than family-wide assumptions.

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

> [!NOTE]
> AmmoMapping entry counts and capacities above come from the current catalog. The generator does not infer projectile identity or capacity from magazine filenames; caliber IDs are shown verbatim from resolved source evidence.

> [!NOTE]
> A derived capacity is shown only when the catalog has source-backed evidence (for example, serialized AmmoMapping length when MaxAmmo is absent). Mapping indices must be interpreted through the resolved AmmoConfig resource list.

## Projectile layer

| Projectile | Init speed | Mass | Damage | Penetration depth | Penetration speed | Air drag | Dispersion mult | Ballistic table | Warnings |
|---|---:|---:|---:|---:|---:|---:|---:|---|---:|
| [`armst_Ammo_9x39_SP5_Ball.et`](../../catalog/ammunition/armst_ammo_9x39_sp5_ball.json) | 290 | 0.01959 | — | 3.7 | 615 | 9.4e-06 | 0.55 | `AIBT_762x54r_Ball_7N1.conf` | 0 |
| [`armst_Ammo_9x39_SP6_Ball.et`](../../catalog/ammunition/armst_ammo_9x39_sp6_ball.json) | 305 | 0.02559 | 150 | 5.55 | 615 | 9.4e-06 | 0.55 | `AIBT_762x54r_Ball_7N1.conf` | 0 |

### What the current projectile snapshot actually proves

- `armst_Ammo_9x39_SP5_Ball.et`: InitSpeed=290, Mass=0.01959, Damage=—, PenetrationDepth=3.7, PenetrationSpeed=615, AirDrag=9.4e-06, BallisticTable=`AIBT_762x54r_Ball_7N1.conf`.
- `armst_Ammo_9x39_SP6_Ball.et`: InitSpeed=305, Mass=0.02559, Damage=150, PenetrationDepth=5.55, PenetrationSpeed=615, AirDrag=9.4e-06, BallisticTable=`AIBT_762x54r_Ball_7N1.conf`.

## Authority boundary

The older `indexes/ammunition_reference/part-06.json` contains different 9×39 SP5/SP6 resources from `Weapons.zip` (`Ammo_9x39_Ball_SP5.et` / `Ammo_9x39_AP_SP6.et`) with different penetration values. Those older reference rows are useful historical/source evidence but must not be merged into the current ARMST projectile rows as if they were the same resources.

Before making balance changes, use the current generated AmmoConfig resource list together with serialized magazine AmmoMapping evidence, then validate one projectile/magazine family at a time in Workbench.
