# 7.62x51 PP/BP Control Build

- PP: `Prefabs/Weapons/Ammo/Western/762x51/Ammo_762x51_PP.et` GUID `8FAC2EB7CA474E5E` parent M80 `C14C5DE6F97F06F0`
- BP: `Prefabs/Weapons/Ammo/Western/762x51/Ammo_762x51_BP.et` GUID `647D4F418F9F4655` parent M61 `9F39DD07E2860466`
- Local config: `Configs/Weapons/Ammo/ARMST/Ammo_762x51_ARMST.conf` GUID `94FC75B17BBA4DB7` (index0 PP, index1 BP)
- Control magazine: `Prefabs/Weapons/Magazines/Western/762x51/HK3/L1A1/armst_Magazine_762x51_HK3_20_M80_Ball.et`
- Control magazine GUID unchanged: 6D18CC33708EE713
- Control parent GUID unchanged: 6D18CC33708EE712
- Capacity unchanged: MaxAmmo stays inherited (20)
- Config rebound: YES
- AmmoMapping: PP-only index0 for all 20 rounds

## Validation

- NEW_PROJECTILES: 2
- LOCAL_CONFIGS_CREATED: 1
- CONTROL_MAGAZINES_CHANGED: 1
- WEAPONS_FOUND: 32
- WEAPON_DANGLING_REFS: 0
- PARENT_GUID_DIFFERENCES: 0
- DANGLING_MAGAZINE_REFS: 2
- DANGLING_AMMO_REFS: 0
- VAL_MAGAZINES_CHANGED: 0
- AKM_TRACER_RECREATED: 0
- 12GA_RESOURCES_CHANGED: 0
- OTHER_CALIBER_AMMO_CHANGED: 0
