# PP / BP Final Creation Plan (Read-Only)

No files were created, moved, renamed, or edited.
PP and BP are user-requested local labels. Their exact ballistic meaning is NOT defined by the project and was NOT assumed.

## Global findings

- PP/BP literal ammunition convention: NOT FOUND.
- The addon uses per-caliber `MagazineConfig` + `AmmoResourceArray` to select ammo resources.
- All four target calibers currently depend on external/vanilla ammo resources and configs.
- Two distinct external source templates exist for every caliber, but for 5.56x45, 9x19 and 7.62x39 the armor-piercing equivalent is NOT listed in the external magazine `AmmoResourceArray`.

## 5.56x45

- CURRENT SOURCE: external config `Configs/Weapons/Ammo/Ammo_556x45.conf` (GUID `2689915ED0E00994`); ammo M855/M193, parent `Ammo_Bullet_Base.et` (GUID `67FED88E5085F63F`).
- PP SOURCE TEMPLATE: `Ammo_556x45_Ball_M855.et` (external GUID `AC26AB660097633D`).
- BP SOURCE TEMPLATE: `Ammo_556x45_AP_M995.et` (external; parent M855).
- LOCAL PARENT: `Prefabs/Weapons/Core/Ammo_Bullet_Base.et` (GUID `67FED88E5085F63F`) for PP; PP for BP.
- LOCAL CONFIG PLAN: REVIEW_REQUIRED. AP M995 is absent from `Ammo_556x45.conf`; local config would be required to expose BP.
- LOCAL PROJECTILE PLAN: inherit external ammo parent; no local projectile body exists.
- FIELDS TO COPY: InitSpeed, InitSpeedVariation, Mass, AirDrag, Diameter, PenetrationDepth, PenetrationSpeed, MushroomingDamageMultiplier, TumblingDamageMultiplier, BallisticTableConfig.
- FIELDS EXPECTED TO DIFFER: the ShellMoveComponent fields above between M855-class and M995-class.
- PP TARGET PATH: `Prefabs/Weapons/Ammo/Western/5x56/Ammo_556x45_PP.et`
- BP TARGET PATH: `Prefabs/Weapons/Ammo/Western/5x56/Ammo_556x45_BP.et`
- MAGAZINES THAT WILL EVENTUALLY USE THESE: STANAG Base/M193/M855, HKG36, SIG550.
- CREATION_STATUS: REVIEW_REQUIRED

## 7.62x51

- CURRENT SOURCE: external config `Configs/Weapons/Ammo/Ammo_762x51.conf` (GUID `533A763E304771D9`); parent magazine base `Magazine_762x51_M14_20rnd_Base.et`.
- PP SOURCE TEMPLATE: `Ammo_762x51_Ball_M80.et` (external GUID `C14C5DE6F97F06F0`).
- BP SOURCE TEMPLATE: `Ammo_762x51_AP_M61.et` (external GUID `9F39DD07E2860466`, parent M80).
- LOCAL PARENT: `Ammo_Bullet_Base.et` (`67FED88E5085F63F`) for PP; M80 for BP.
- LOCAL CONFIG PLAN: REVIEW_REQUIRED. Both templates are present in the external config; local config creation still undecided.
- LOCAL PROJECTILE PLAN: inherit external templates; no local projectile body.
- FIELDS TO COPY: InitSpeed, InitSpeedVariation, Mass, DamageValue, AirDrag, Diameter, Length, PenetrationDepth, PenetrationSpeed, MushroomingDamageMultiplier, TumblingDamageMultiplier, BallisticTableConfig.
- FIELDS EXPECTED TO DIFFER: Mass, Length, PenetrationDepth, PenetrationSpeed, AirDrag, MushroomingDamageMultiplier, TumblingDamageMultiplier, BallisticTableConfig, models.
- PP TARGET PATH: `Prefabs/Weapons/Ammo/Western/762x51/Ammo_762x51_PP.et`
- BP TARGET PATH: `Prefabs/Weapons/Ammo/Western/762x51/Ammo_762x51_BP.et`
- MAGAZINES THAT WILL EVENTUALLY USE THESE: HK3 20rnd, L1A1 20/30rnd.
- CREATION_STATUS: REVIEW_REQUIRED

## 9x19

- CURRENT SOURCE: external config `Configs/Weapons/Ammo/Ammo_9x19.conf` (GUID `BC69F995CEEF2196`); parent magazine base `Magazine_9x19_M9_15rnd_Base.et`.
- PP SOURCE TEMPLATE: `Ammo_9x19_Ball_M882.et` (external GUID `9D290AA75ADA4618`).
- BP SOURCE TEMPLATE: `Ammo_9x19_AP_7N21.et` (external; not in config).
- LOCAL PARENT: `Ammo_Bullet_Base.et` (`67FED88E5085F63F`).
- LOCAL CONFIG PLAN: REVIEW_REQUIRED. AP 7N21 is not listed in the external config (only M882/JHP).
- LOCAL PROJECTILE PLAN: inherit external templates; no local projectile body.
- FIELDS TO COPY: InitSpeed, InitSpeedVariation, DispersionMultiplier, Mass, AirDrag, Diameter, PenetrationDepth, PenetrationSpeed, BallisticTableConfig.
- FIELDS EXPECTED TO DIFFER: mass/speed/penetration/drag between M882-class and 7N21-class.
- PP TARGET PATH: `Prefabs/Weapons/Ammo/Western/9x19/Ammo_9x19_PP.et`
- BP TARGET PATH: `Prefabs/Weapons/Ammo/Western/9x19/Ammo_9x19_BP.et`
- MAGAZINES THAT WILL EVENTUALLY USE THESE: `Magazine_9x19_M9_15rnd_Ball.et`.
- CREATION_STATUS: REVIEW_REQUIRED

## 7.62x39

- CURRENT SOURCE: external config `Configs/Weapons/Ammo/Ammo_762x39.conf` (GUID `6810AE1CC6F1621D`); magazine base Vz58/AKM (external).
- PP SOURCE TEMPLATE: `Ammo_762x39_Ball_57N231.et` (external GUID `2FBCA0A7CEDDE7B0`).
- BP SOURCE TEMPLATE: `Ammo_762x39_AP_7N23.et` (external; not in config).
- LOCAL PARENT: `Ammo_Bullet_Base.et` (`67FED88E5085F63F`).
- LOCAL CONFIG PLAN: REVIEW_REQUIRED. AP 7N23 is not listed in the external config (only 57N231/tracer).
- LOCAL PROJECTILE PLAN: inherit external templates; no local projectile body.
- FIELDS TO COPY: InitSpeed, InitSpeedVariation, Mass, DamageValue, AirDrag, Diameter, Length, TumblingDamageMultiplier, PenetrationDepth, PenetrationSpeed, BallisticTableConfig.
- FIELDS EXPECTED TO DIFFER: Mass, DamageValue, PenetrationDepth, PenetrationSpeed, AirDrag, BallisticTableConfig.
- PP TARGET PATH: `Prefabs/Weapons/Ammo/Eastern/762x39/Ammo_762x39_PP.et`
- BP TARGET PATH: `Prefabs/Weapons/Ammo/Eastern/762x39/Ammo_762x39_BP.et`
- MAGAZINES THAT WILL EVENTUALLY USE THESE: `Magazine_762x39_AKM_10rnd_Ball.et`, `Magazine_762x39_AKM_30rnd_Ball.et`.
- CREATION_STATUS: REVIEW_REQUIRED

## Magazine rebind plan (not executed)

Each magazine currently references one `AmmoConfig`; the config `AmmoResourceArray` lists one or more ammo resources. There is no PP/BP selection mechanism in the current local resource architecture. Therefore:
- PP and BP cannot be bound to one magazine simultaneously without separate magazine prefabs, a different config, or an engine-level switching system.
- No switching system is invented here.
- All magazine changes remain future work.

## Summary

- Calibers inspected: 4
- Calibers READY for local creation: none
- Calibers REVIEW_REQUIRED: 5.56x45, 7.62x51, 9x19, 7.62x39
