# PP91 -> PM Base Reparent

- path: `Prefabs/Weapons/Russian/Handguns/PP_19/armst_PP91.et`
- GUID: 3968B2A856852CBD
- parent before: `{C0F7DD85A86B2900}Handguns/armst_PM.et`
- parent after: `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`

## armst_PM contributions bypassed (materialized locally)
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

## SR_2 check
- SR_2 (do not edit) inherits these from PP91; since all bypassed armst_PM fields were materialized on PP91, SR_2 effective state is unchanged.

## Validation
```
{
 "PARENT_CHANGED": 1,
 "GUID_CHANGES": 0,
 "PATH_CHANGES": 0,
 "META_UNCHANGED": true,
 "braces_balanced": true,
 "pp91_effective_behavior_preserved": "YES",
 "sr2_effective_behavior_preserved": "YES",
 "OTHER_WEAPONS_CHANGED": 0,
 "lines_added": 10,
 "lines_removed": 1
}
```
