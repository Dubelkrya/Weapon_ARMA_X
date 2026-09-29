# HK G3 / HK G36 Identity Fix

## HK G3 (`Prefabs/Weapons/Western/Rifle/HKG33/armst_Rifle_HKG33.et`)
- before: ItemDisplayName/UIInfo Name inherited `#AR-Weapon_M16A2_Name`; Description inherited `#AR-Weapon_M16A2_Description`
- after: **"HK G3"**
- fields changed: ItemDisplayName WeaponUIInfo {5222CB07CFF6712A} Name; WeaponComponent>UIInfo WeaponUIInfo {CC3BA6A2C42F09F4} Name

## HK G36 (`Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_hk_g36.et`)
- already **"HK G36"** via `#AR-ARMST_Weapon_G36_Name`; no change

## Validation
```
{
 "WRONG_HKG33_PLAYER_DISPLAY_REFS": 0,
 "WRONG_M16_OR_OLD_G36_PLAYER_DISPLAY_REFS": 0,
 "GUID_CHANGES": 0,
 "PATH_CHANGES": 0,
 "META_UNCHANGED": true,
 "braces_balanced": true,
 "GAMEPLAY_DIFF": 0,
 "OTHER_WEAPONS_CHANGED": 0
}
```

## Description identity
- HK G3: #AR-Weapon_M16A2_Description still inherited (identifies M16) - NOT rewritten per scope
- HK G36: CLEAN (#AR-ARMST_Weapon_G36_Description)

LIVE_FILES_CHANGED: armst_Rifle_HKG33.et (Name fields only)
