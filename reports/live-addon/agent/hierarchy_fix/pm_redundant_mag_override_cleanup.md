# PM Redundant Magazine Override Cleanup

- resource: `Prefabs/Weapons/Russian/Handguns/Pm/armst_PM.et`
- removed local MagazineTemplate/WeaponComponent override block (contained only that override)
- effective magazine: `armst_Magazine_9x18_PM_8rnd_Ball.et (resolved by GUID)` (GUID 8B853CDD11BA916E (inherited from Handgun_PM_base))
- well: MagazineWellMakarovPM | capacity: 8

## Removed lines
- `WeaponComponent "{CFBAA4B706BA66E8}" {`
- `components {`
- `MuzzleComponent "{50F64C45E7271D47}" {`
- `MagazineTemplate "{8B853CDD11BA916E}Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball.et"`

## Validation
```
{
 "LOCAL_PM_MAGAZINE_TEMPLATE_OVERRIDE": 0,
 "LOCAL_WEAPONCOMPONENT_OVERRIDE_REMAINING": 0,
 "EFFECTIVE_BEHAVIOR_CHANGED": 0,
 "GUID_CHANGES": 0,
 "OTHER_WEAPONS_CHANGED": 0,
 "META_UNCHANGED": true,
 "braces_balanced": true
}
```
