# 9x18 Ammo Mapping Semantics Audit (READ ONLY)

## Semantics (proven)
- AmmoMapping is one entry per physical cartridge (length == effective capacity).
- `AmmoMapping + { ... }` APPENDS to the inherited array; plain `AmmoMapping { ... }` replaces.
- Each value is an index into the effective AmmoConfig AmmoResourceArray (here only index 0 exists -> Ammo_9x18_Ball_57N181).
- Proof: PM vanilla base declares 8-entry AmmoMapping; APB appends +12 -> 20; PP91/SR2 append +22 -> 30. 36/36 live magazines have effective mapping length == effective capacity.

## AmmoConfig (effective)
- `{4A7B5486D9167E2A}Configs/Weapons/Ammo/Ammo_9x18Mak.conf`
- AmmoResourceArray: {4DE72DF927310A8B}Prefabs/Weapons/Ammo/Ammo_9x18_Ball_57N181.et
- source: Magazine_9x18_PM_8rnd_Base.et (inherited; children do not override AmmoConfig)

## Targets
| mag | capacity | local mapping | effective mapping | classification |
|---|---|---|---|---|
| PM | 8 | None | 8 | **VALID** |
| APB | 20 | 12 | 20 | **VALID** |
| PP91 | 30 | 22 | 30 | **VALID** |
| SR2 | 30 | 22 | 30 | **VALID** |

## Local vs effective mapping
- PM: =8 by Magazine_9x18_PM_8rnd_Base.et (chain: armst_Magazine_9x18_PM_8rnd_Ball.et -> Magazine_9x18_PM_8rnd_Base.et -> Magazine_Base.et)
- APB: =8 by Magazine_9x18_PM_8rnd_Base.et, +12 by armst_Magazine_9x18_APB_20rnd_Ball.et (chain: armst_Magazine_9x18_APB_20rnd_Ball.et -> armst_Magazine_9x18_PM_8rnd_Ball.et -> Magazine_9x18_PM_8rnd_Base.et -> Magazine_Base.et)
- PP91: =8 by Magazine_9x18_PM_8rnd_Base.et, +22 by armst_Magazine_9x18_PP91_30rnd_Ball.et (chain: armst_Magazine_9x18_PP91_30rnd_Ball.et -> armst_Magazine_9x18_PM_8rnd_Ball.et -> Magazine_9x18_PM_8rnd_Base.et -> Magazine_Base.et)
- SR2: =8 by Magazine_9x18_PM_8rnd_Base.et, +22 by armst_Magazine_9x18_SR2_30rnd_Ball.et (chain: armst_Magazine_9x18_SR2_30rnd_Ball.et -> armst_Magazine_9x18_PM_8rnd_Ball.et -> Magazine_9x18_PM_8rnd_Base.et -> Magazine_Base.et)

## Working examples by capacity (effective mapping length == capacity)
- cap 5: armst_12ga_Shell_test.et(5)
- cap 8: armst_Magazine_763x25_TT_8rnd_Ball.et(8), armst_Magazine_9x18_PM_8rnd_Ball.et(8)
- cap 10: 12ga_Buckshot_base.et(10), armst_12ga_Buckshot.et(10), armst_12ga_Shell.et(10), armst_Magazine_762x54_SVD_10rnd_7BZ3API.et(10), armst_Magazine_762x39_AKM_10rnd_Ball.et(10)
- cap 15: armst_Magazine_9x19_M9_15rnd_Ball.et(15), armst_Magazine_9x19_M9_15rnd_Ball_BP.et(15)
- cap 20: armst_Magazine_9x18_APB_20rnd_Ball.et(20), armst_Magazine_9x39_20rnd_9a91_SP5.et(20), armst_Magazine_9x39_20rnd_9a91_SP6.et(20), armst_Magazine_9x39_20rnd_vss_SP5.et(20), armst_Magazine_9x39_20rnd_vss_SP6.et(20)
- cap 30: armst_Magazine_9x18_PP91_30rnd_Ball.et(30), armst_Magazine_9x18_SR2_30rnd_Ball.et(30), armst_Magazine_556x45_HKG36.et(30), armst_Magazine_556x45_HKG36_BP.et(30), armst_Magazine_556x45_SIG_550.et(30)
- cap 45: armst_Magazine_545x39_RPK_45rnd_Ball.et(45), armst_Magazine_545x39_RPK_45rnd_Tracer.et(45)
- cap 250: armst_Box_762x54_PK_250rnd_Ball.et(250)

MAPPING_LENGTH_EQUALS_CAPACITY_RULE: PROVEN
REPAIR_NEEDED: NONE
LIVE_FILES_CHANGED: NONE
