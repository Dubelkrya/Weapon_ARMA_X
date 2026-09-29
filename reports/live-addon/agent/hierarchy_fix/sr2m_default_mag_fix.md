# SR-2M Default Magazine Fix

- resource: `Prefabs/Weapons/Russian/Handguns/Sr_2/armst_SR_2.et`
- GUID: 31FB2EC4F4AFFC05
- field: `MuzzleComponent {50F64C45E7271D47} > MagazineTemplate`
- well: KEEP `MagazineWellPP91`
- default magazine before: `{4488C415F3CA1890}Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PP91_30rnd_Ball.et`
- default magazine after: `{2610CA8D8632DEF4}Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_SR2_30rnd_Ball.et`

## Validation
```
{
 "display_name_preserved": true,
 "parent_preserved": true,
 "GUID_CHANGES": 0,
 "PATH_CHANGES": 0,
 "META_UNCHANGED": true,
 "braces_balanced": true,
 "OTHER_GAMEPLAY_CHANGES": 0,
 "OTHER_WEAPONS_CHANGED": 0,
 "checks": {
  "pp91_mag_template_refs_remaining": false,
  "sr2_mag_template_present": true,
  "well_present": true
 }
}
```
