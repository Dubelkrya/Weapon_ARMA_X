# PM Default Magazine Fix

- resource: `Prefabs/Weapons/Russian/Handguns/Pm/armst_PM.et`
- GUID: C0F7DD85A86B2900
- parent: `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`

- Finding: Handgun_PM_base MagazineTemplate references GUID {8B853CDD11BA916E} with a stale vanilla path; that GUID is the ARMST PM magazine -> effective default was already the ARMST PM magazine. Override added to serialize the exact ARMST path.
- effective default before: ARMST PM magazine (by GUID 8B853CDD11BA916E; serialized path in base was vanilla/stale)
- effective default after: ARMST PM magazine (explicit local override, exact ARMST path)

## Added lines
- `WeaponComponent "{CFBAA4B706BA66E8}" {`
- `components {`
- `MuzzleComponent "{50F64C45E7271D47}" {`
- `MagazineTemplate "{8B853CDD11BA916E}Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball.et"`

## Compatibility
```
{
 "PM_weapon_well": "MagazineWellMakarovPM {26EA67622A1DA48B} (inherited)",
 "ARMST_PM_mag_well": "MagazineWellMakarovPM {05B3A6C89A212814}",
 "class_match": true,
 "capacity": 8
}
```
## Validation
```
{
 "GUID_CHANGES": 0,
 "PATH_CHANGES": 0,
 "META_UNCHANGED": true,
 "braces_balanced": true,
 "OTHER_GAMEPLAY_CHANGES": 0,
 "OTHER_WEAPONS_CHANGED": 0
}
```
