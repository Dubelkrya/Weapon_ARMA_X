# M16 Animation Cleanup

- M16 path: `Prefabs/Weapons/Western/Rifle/armst_Rifle_M16A2.et`
- GUID: 3E413771E1834D2F
- parent before/after: `{C63227C0E70EA62E}Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et` -> `{C63227C0E70EA62E}Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et` (unchanged=True)
- provenance: LOCAL_OVERRIDE (authored directly in M16)
- evidence: `Weapon_ARMA_X\Weapons\Rifles\M16\Rifle_M16A2_base.et`

## Bad L1A1 refs removed
- `{0E3ECFC4E84386BC}Assets/NATO/L1A1/Anim/L1A1.agr`
- `{3B86B943995121A3}Assets/NATO/L1A1/Anim/L1A1_weapon.asi`
- `{0E3ECFC4E84386BC}Assets/NATO/L1A1/Anim/L1A1.agr`
- `{C0D828720150454F}Assets/NATO/L1A1/Anim/L1A1_player.asi`

## Correct M16 refs now used
- AnimGraph: `{C10E1E127E210526}Assets/Weapons/Rifles/workspaces/m16.agr`
- AnimInstance: `{278604E4583F2647}Assets/Weapons/Rifles/workspaces/m16_weapon.asi`
- InjectionAnimGraph: `{C10E1E127E210526}Assets/Weapons/Rifles/workspaces/m16.agr`
- InjectionAnimInstance: `{DCD895D5C03E42AB}Assets/Weapons/Rifles/workspaces/m16_player.asi`

## Validation
```
{
 "M16_PARENT_CHANGED": 0,
 "L1A1_ANIMATION_REFS_IN_M16": 0,
 "GUID_CHANGES": 0,
 "PATH_CHANGES": 0,
 "MODEL_CHANGES": 0,
 "MAGAZINE_WELL_CHANGES": 0,
 "FIREMODE_CHANGES": 0,
 "WEAPON_STAT_CHANGES": 0,
 "OTHER_WEAPONS_CHANGED": 0,
 "12GA_CHANGED": 0,
 "only_anim_lines_changed": true,
 "correct_refs_match_parent": true
}
```
