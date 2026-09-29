# APB -> PM Base Reparent

- path: `Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB.et`
- GUID: 5D3DA7E84135B278
- parent before: `{C0F7DD85A86B2900}Handguns/armst_PM.et`
- parent after: `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`

## armst_PM contributions bypassed
- ARMST_ITEMS_STATS_COMPONENTS {657ABA0547189DD7}
- SCR_EditableEntityComponent {65F28786D4603482}: Enabled 0, m_bAutoRegister NEVER, m_UIInfo labels (grid fields already fully local on APB)

## Local overrides added
- `GenericEntity : "{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et" {`
- `ARMST_ITEMS_STATS_COMPONENTS "{657ABA0547189DD7}" {`
- `Enabled 0`
- `m_bAutoRegister NEVER`
- `m_aAuthoredLabels {`
- `CONTENT_MODDED 4141368`
- `m_aAutoLabels {`
- `4141368`

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
