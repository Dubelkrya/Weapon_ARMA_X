# 9x18 PP/BP Projectile Layer (created)

## PP resource
- path: `Prefabs/Weapons/Ammo/armst_Ammo_9x18_PP.et`
- guid: 2EECBE22BC8BE0BA
- parent: `{4DE72DF927310A8B}Prefabs/Weapons/Ammo/Ammo_9x18_Ball_57N181.et`
- local fields: ID only

## BP resource
- path: `Prefabs/Weapons/Ammo/armst_Ammo_9x18_BP.et`
- guid: 64F210837ACBAF9E
- parent: `{B3010C5DF1ED82ED}Prefabs/Weapons/Ammo/Ammo_9x18_AP_7N25.et`
- local fields: ID only

## Config
- path: `Configs/Weapons/Ammo/armst_Ammo_9x18_ARMST.conf`
- guid: F2D8D099211C2451
- index 0: {2EECBE22BC8BE0BA}Prefabs/Weapons/Ammo/armst_Ammo_9x18_PP.et
- index 1: {64F210837ACBAF9E}Prefabs/Weapons/Ammo/armst_Ammo_9x18_BP.et

## Validation
```
{
 "AmmoResourceArray_len": 2,
 "index0_is_PP": true,
 "index1_is_BP": true,
 "DANGLING_REFS": [],
 "PP_UNINTENDED_BALLISTIC_DELTA": 0,
 "BP_UNINTENDED_BALLISTIC_DELTA": 0,
 "GUID_COLLISIONS": 0,
 "EXISTING_FILES_CHANGED": 0,
 "MAGAZINES_CHANGED": 0
}
```

Existing 9x18 resources and magazines unchanged (no magazine references the new config yet).
