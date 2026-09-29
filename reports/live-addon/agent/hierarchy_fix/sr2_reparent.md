# SR-2 -> PM Base Reparent

- path: `Prefabs/Weapons/Russian/Handguns/Sr_2/armst_SR_2.et`
- GUID: 31FB2EC4F4AFFC05
- parent before: `{3968B2A856852CBD}Handguns/New_armst_PP91.et`
- parent after: `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`

## PP91 contributions bypassed
- ARMST_ITEMS_STATS_COMPONENTS {657ABA0547189DD7}
- SCR_EditableEntityComponent {65F28786D4603482}: Enabled 0, m_bAutoRegister NEVER, m_UIInfo labels
- Attributes SCR_ItemAttributeCollection {51F080D5C64F12C5}: m_bAutoDetectGridSize 0, m_iCustomGridHeight 2 (width 4 already local)

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
- `m_iCustomGridHeight 2`

## Final handgun tree
- `armst_PM.et` -> `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`
- `armst_PP91.et` -> `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`
- `armst_APB.et` -> `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`
- `armst_TT.et` -> `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`
- `armst_SR_2.et` -> `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`
- `armst_M9.et` -> `{809488C4984AC087}Prefabs/Weapons/Handguns/M9/Handgun_M9_base.et`

LOCAL_CONCRETE_HANDGUN_PARENT_EDGES: 0

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
