# Groza Reparent Safety Probe (READ ONLY)

- resource: `Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et`
- GUID: 903C7920F00AB654
- model: `{277CC12370C4BCF0}Assets/Weapons_RUS/Groza/GROZA.xob`
- parent current: `{911D6C8DC7BA2D63}Prefabs/Weapons/Core/Rifle_Base.et`
- target parent: `{923D948AB0D57A50}Prefabs/Weapons/Rifles/AK74/Rifle_AK74_long_base.et`
- chain before: ['{911D6C8DC7BA2D63}Prefabs/Weapons/Core/Rifle_Base.et', '{E1F14DB52DBFBC57}Prefabs/Weapons/Core/Weapon_Base.et']

## TARGET_COMPONENTS_ADDED (31)
### Critical (5)
- `51F6738D2EC74BE1` AttachmentSlotComponent
- `5A1E5C47AE23F25A` UserActionContext
- `5F189C826D592450` AttachmentSlotComponent
- `60ECB1EBE1387B1B` UserActionContext
- `618A84270A2BFDC0` UserActionContext
### Other
- `55349E9229B55E74` SightsPointFront
- `55349E9229B55E7A` SightsPointRear
- `584CED329E401420` SightRangeInfo
- `584CED329E40145B` WeaponPosition
- `584CED329E42F017` WeaponPosition
- `584CED329E42F0E4` SightRangeInfo
- `584CED329E44A70D` SightRangeInfo
- `584CED329E44A73B` WeaponPosition
- `584CED329E45D8C3` WeaponPosition
- `584CED329E45D8D6` SightRangeInfo
- `584CED329E469695` WeaponPosition
- `584CED329E46976E` SightRangeInfo
- `584CED329E478DA3` SightRangeInfo
- `584CED329E478DAA` WeaponPosition
- `584CED329E484221` SightRangeInfo
- `584CED329E484228` WeaponPosition
- `584CED329E49782B` SightRangeInfo
- `584CED329E497853` WeaponPosition
- `584CED329E4A3248` SightRangeInfo
- `584CED329E4A3270` WeaponPosition
- `584CED329E4B2895` SightRangeInfo
- `584CED329E4B289C` WeaponPosition
- `584CED329E4D1BD6` SightRangeInfo
- `584CED329E4D1BDE` WeaponPosition
- `60ECB1EBE48BA151` Position
- `618A842792A66B70` Position

## CURRENT_COMPONENTS_LOST (5)
- `51F080D5C64F12C5` Attributes
- `51F080D5CE45A1A2` SCR_WeaponAttachmentsStorageComponent
- `5222CB07CFF6712A` ItemDisplayName
- `5A28749C602565F8` EPF_PersistenceComponent
- `5A28749F9ED6F91D` m_pSaveData

## FIELDS_THAT_WOULD_CHANGE
- `58789524E765774D` LinearData.['Curve Magnitudes'] -> ['1.4 1.2 1']
- `58789524E7CAB55F` AngularData.['Curve Magnitudes'] -> ['1.4 1.2 1']
- `4E2B66CBA589F625` AttachmentSlotComponent.['InspectionWidgetOffset'] -> ['0 0.07 0.568']
- `BB23A63796688E69` SightsPosition.['PivotID'] -> ['"eye"']
- `58789524E0951484` TurnOffsetData.['Curve Magnitudes'] -> ['1.4 1.2 0']

## Foreign / pre-existing refs
- magazine template: `{48720FC416263FC1}Prefabs/Weapons/Magazines/Russian/7x62/AKM/armst_Magazine_762x39_AKM_30rnd_Ball.et`
- magazine well: `{5464E0EAAF7815B4}`
- note: AK74 muzzle particle `Particles/Weapon/Muzzle_AK74.ptc` is pre-existing locally

## Decision
```
{
 "SAFE_TO_REPARENT": "NO",
 "critical_additions": 5,
 "total_additions": 31,
 "unshadowed_shared_fields": 5
}
```
- AK74_long_base would inject %d components Groza does not shadow (%d gameplay-critical: 2 AttachmentSlotComponent, 3 UserActionContext) plus AK74 sight-range nodes and unshadowed recoil/sight fields. Preserving Groza state would require many explicit neutralizing overrides; duplicate/foreign instance risk.

LIVE_FILES_CHANGED: NONE
