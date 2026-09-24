# Shotguns

> [!NOTE]
> **Status: GENERATED SNAPSHOT.** The main family table uses the explicit `/Shotgun/` prefab path.

Current matching catalog entries: **9**.

All entries in the explicit shotgun branch currently resolve `MagazineWell12g` and the 12 ga buckshot template. A missing RPM or dispersion diameter remains unresolved rather than being treated as zero.

## Current catalog comparison

| Entry | Role | Parent | Magazine | RPM | Velocity coef | Dispersion | Slots | Warnings |
|---|---|---|---|---:|---:|---|---:|---:|
| [`armst_izh_27`](../../catalog/weapons/armst_izh_27.json) | leaf | `shotgun_base.et` | `12ga_Buckshot.et` | 1500 | — | R=701 | 1 | 0 |
| [`armst_mp_133`](../../catalog/weapons/armst_mp_133.json) | leaf | `shotgun_base.et` | `12ga_Buckshot.et` | 1400 | — | R=701 | 1 | 0 |
| [`armst_mp_153`](../../catalog/weapons/armst_mp_153.json) | leaf | `shotgun_base.et` | `12ga_Buckshot.et` | 1400 | — | R=701 | 1 | 0 |
| [`armst_remington_870`](../../catalog/weapons/armst_remington_870.json) | leaf | `shotgun_base.et` | `12ga_Buckshot.et` | — | — | R=701 | 1 | 0 |
| [`armst_spas_12`](../../catalog/weapons/armst_spas_12.json) | leaf | `shotgun_base.et` | `12ga_Buckshot.et` | 1400 | — | R=701 | 1 | 0 |
| [`armst_toz_66`](../../catalog/weapons/armst_toz_66.json) | base | `shotgun_base.et` | `12ga_Buckshot.et` | 1600 | — | R=701 | 1 | 0 |
| [`armst_toz_66_pantera`](../../catalog/weapons/armst_toz_66_pantera.json) | leaf | `armst_toz_66.et` | `12ga_Buckshot.et` | 1600 | — | R=701 | 1 | 0 |
| [`armst_toz_66_saw`](../../catalog/weapons/armst_toz_66_saw.json) | leaf | `armst_toz_66.et` | `12ga_Buckshot.et` | 1600 | — | R=701 | 1 | 0 |
| [`shotgun_base`](../../catalog/weapons/shotgun_base.json) | base | `Rifle_M21.et` | `12ga_Buckshot.et` | — | — | R=701 | 1 | 0 |

## Related 12 ga entries outside the shotgun prefab path

These are not automatically promoted into the shotgun family because their source path does not prove the same prefab family.

| Entry | Role | Parent | Magazine | RPM | Velocity coef | Dispersion | Slots | Warnings |
|---|---|---|---|---:|---:|---|---:|---:|
| [`1`](../../catalog/weapons/1.json) | leaf | `Rifle_M21_base.et` | `12ga_Buckshot.et` | 50 | 0.95 | D=0.1 | 1 | 0 |
