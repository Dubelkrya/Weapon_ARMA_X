# TT -> PM Base Reparent

- path: `Prefabs/Weapons/Russian/Handguns/TT/armst_TT.et`
- GUID: 0D469F42B65E350E
- parent before: `{C0F7DD85A86B2900}Handguns/armst_PM.et`
- parent after: `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`

## armst_PM contributions bypassed
- ARMST_ITEMS_STATS_COMPONENTS {657ABA0547189DD7}
- SCR_EditableEntityComponent {65F28786D4603482}: Enabled 0, m_bAutoRegister NEVER, m_UIInfo labels
- Attributes SCR_ItemAttributeCollection {51F080D5C64F12C5}: m_bAutoDetectGridSize 0, m_iCustomGridWidth 2, m_iCustomGridHeight 2 (TT had no local grid fields)

## WeaponSoundComponent provenance
- B_INHERITED_FROM_HANDGUN_PM_BASE
- armst_PM.et declares no WeaponSoundComponent; TT has no local sound; WeaponSoundComponent comes from Handgun_PM_base and is retained after reparent. Not C.

## Local overrides added
- `GenericEntity : "{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et" {`
- `ARMST_ITEMS_STATS_COMPONENTS "{657ABA0547189DD7}" {`
- `Enabled 0`
- `m_bAutoRegister NEVER`
- `m_aAuthoredLabels {`
- `CONTENT_MODDED 4141368`
- `m_aAutoLabels {`
- `4141368`
- `m_bAutoDetectGridSize 0`
- `m_iCustomGridWidth 2`
- `m_iCustomGridHeight 2`

## Foreign refs
- none introduced; TT uses its own model/MagazineWell763x25/763x25 mag template. TT has no local animations/IK and continues to inherit PM-family handgun animations from Handgun_PM_base exactly as before (pre-existing, not repaired).

## Validation
```
{
 "PARENT_CHANGED": 1,
 "GUID_CHANGES": 0,
 "PATH_CHANGES": 0,
 "META_UNCHANGED": true,
 "braces_balanced": true,
 "effective_behavior_preserved": "YES",
 "OTHER_WEAPONS_CHANGED": 0
}
```
