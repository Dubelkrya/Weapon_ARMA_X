# 9x39 Caliber Metadata Audit (READ ONLY)

## 9x39 resources
- weapons (8):
  - [R] `Prefabs/Weapons/Attachments/Muzzle/armst_Suppressor_9a91.et`
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP5.et`
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP6.et`
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/Groza/armst_Magazine_9x39_Groza_20rnd_SP5.et`
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/Groza/armst_Magazine_9x39_Groza_20rnd_SP6.et`
  - [R] `Prefabs/Weapons/Russian/Rifle/9a91/armst_Rifle_9a91_base.et`
  - [R] `Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et`
  - [R] `Prefabs/Weapons/Russian/Rifle/VSK94/armst_Rifle_VSK94_base.et`
- magazines (8):
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP5.et`
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP6.et`
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/Groza/armst_Magazine_9x39_Groza_20rnd_SP5.et`
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/Groza/armst_Magazine_9x39_Groza_20rnd_SP6.et`
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_20rnd_vss_SP5.et`
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_20rnd_vss_SP6.et`
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_30rnd_val_SP5.et`
  - [R] `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_30rnd_val_SP6.et`
- configs (3):
  - [R] `Configs/Weapons/Ammo/armst_Ammo_9x39.conf`
  - [S] `Configs/Weapons/AIBallisticTables/AIBT_9x39_AP_SP6.conf`
  - [S] `Configs/Weapons/AIBallisticTables/AIBT_9x39_Ball_SP5.conf`
- projectiles (6):
  - [R] `Prefabs/Weapons/Ammo/Russian/9x39/armst_Ammo_9x39_SP5_Ball.et`
  - [R] `Prefabs/Weapons/Ammo/Russian/9x39/armst_Ammo_9x39_SP6_Ball.et`
  - [V] `Ammo/Ammo_9x39_AP_SP6.et`
  - [V] `Ammo/Ammo_9x39_Ball_SP5.et`
  - [S] `Prefabs/Weapons/Ammo/Ammo_9x39_AP_SP6.et`
  - [S] `Prefabs/Weapons/Ammo/Ammo_9x39_Ball_SP5.et`

## Wrong `545x39` metadata in 9x39 resources (6)
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP5.et` -> `#AR-AmmunitionID_545x39mm`
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP6.et` -> `#AR-AmmunitionID_545x39mm`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_20rnd_vss_SP5.et` -> `#AR-AmmunitionID_545x39mm`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_20rnd_vss_SP6.et` -> `#AR-AmmunitionID_545x39mm`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_30rnd_val_SP5.et` -> `#AR-AmmunitionID_545x39mm`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_30rnd_val_SP6.et` -> `#AR-AmmunitionID_545x39mm`

## Proven 9x39 metadata value
- NONE (no #AR-AmmunitionID_9x39mm style key found in live or exported resources; the only 9x39 #AR keys are magazine Description keys)
- Other calibers use #AR-AmmunitionID_<cal>mm (e.g. #AR-AmmunitionID_9x18mm, #AR-AmmunitionID_762x39mm); the 9x39 equivalent is not present locally.

## Field semantics
- m_sAmmoCaliber is authored inside MagazineComponent>UIInfo MagazineUIInfo (next to m_MagIndicator) = inventory/display metadata for the ammo-type label/filter; NOT gameplay ballistics (ballistics come from projectile/AmmoConfig). Placement evidence only; not runtime-verified.

## Classification
- CONFIRMED_WRONG: 6 (all six proven 9x39 magazines)
- AMBIGUOUS: 0

## Groza casing
- OPEN_TECHNICAL_DEBT / NO_PROVEN_9x39_CASING (unchanged)

LIVE_FILES_CHANGED: NONE
