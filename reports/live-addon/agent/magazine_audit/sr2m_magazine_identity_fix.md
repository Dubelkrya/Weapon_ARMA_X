# SR-2M Magazine Identity Fix

- resource: `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_SR2_30rnd_Ball.et`
- GUID: 2610CA8D8632DEF4
- value before: "PP-91 Magazine"
- value after: "Магазин СР-2М «Вереск»"

## Fields changed
- ItemDisplayName UIInfo {51FEE38527BFEA5B} Name
- SCR_EditableEntityComponent {65B26504B0CBA6C3} > m_UIInfo SCR_EditableEntityUIInfo {65B26504B5150965} Name

## Validation
```
{
 "WRONG_PP91_DISPLAY_NAME_REFS_IN_SR2_MAG": 0,
 "capacity": 30,
 "magazine_well": "MagazineWellPP91",
 "ammo_mapping_len": 22,
 "description_unchanged_all": true,
 "GUID_CHANGES": 0,
 "META_UNCHANGED": true,
 "braces_balanced": true,
 "GAMEPLAY_DIFF": 0,
 "OTHER_RESOURCES_CHANGED": 0
}
```
