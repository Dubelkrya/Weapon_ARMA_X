# L86 Reparent

- path: `Prefabs/Weapons/Western/Rifle/L85/armst_Rifle_L85.et`
- GUID: 45D3FCA77AF1709B
- parent before: `{3E413771E1834D2F}Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et`
- parent after: `{C63227C0E70EA62E}Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et`

## Intermediate parent contributions (now bypassed)
- SCR_MeleeWeaponProperties {5534745C44D1EFF6} m_fDamage 2
- WeaponComponent>WeaponAnimationComponent {60B4EA76EB15F6E0} M16 anims

## Effective state before
```
{
 "model": "{0F26972BB6E3CA5F}Assets/Weapons_NATO/L86/L86.xob",
 "magazine_well": null,
 "magazine_template": null,
 "animation_refs": [
  "{C43E8470702AEDE4}Assets/Weapons_NATO/L86/Anim/L86.agr",
  "{B702ED8F6D2CACB7}Assets/Weapons_NATO/L86/Anim/L86_weapon.asi",
  "{C43E8470702AEDE4}Assets/Weapons_NATO/L86/Anim/L86.agr",
  "{4C5C7CBEF52DC85B}Assets/Weapons_NATO/L86/Anim/L86_player.asi"
 ],
 "ik_pose": "{9B94312176361ECC}Assets/Weapons_NATO/L86/Anim/Diff/p_rfl_L86_ik.anm",
 "has_sights": true,
 "has_uiinfo_desc": true,
 "melee_damage": "2",
 "fire_modes_local": false,
 "sounds_local": false,
 "attachment_slots_local": true
}
```
## Effective state after
```
{
 "model": "{0F26972BB6E3CA5F}Assets/Weapons_NATO/L86/L86.xob",
 "magazine_well": null,
 "magazine_template": null,
 "animation_refs": [
  "{C43E8470702AEDE4}Assets/Weapons_NATO/L86/Anim/L86.agr",
  "{B702ED8F6D2CACB7}Assets/Weapons_NATO/L86/Anim/L86_weapon.asi",
  "{C43E8470702AEDE4}Assets/Weapons_NATO/L86/Anim/L86.agr",
  "{4C5C7CBEF52DC85B}Assets/Weapons_NATO/L86/Anim/L86_player.asi"
 ],
 "ik_pose": "{9B94312176361ECC}Assets/Weapons_NATO/L86/Anim/Diff/p_rfl_L86_ik.anm",
 "has_sights": true,
 "has_uiinfo_desc": true,
 "melee_damage": "2",
 "fire_modes_local": false,
 "sounds_local": false,
 "attachment_slots_local": true
}
```
## Validation
```
{
 "PARENT_CHANGED": 1,
 "GUID_CHANGES": 0,
 "PATH_CHANGES": 0,
 "MODEL_CHANGED": 0,
 "ANIMATION_BEHAVIOR_CHANGED": 0,
 "MAGAZINE_WELL_CHANGED": 0,
 "MAGAZINE_COMPATIBILITY_CHANGED": 0,
 "FIRE_MODES_CHANGED": 0,
 "SIGHTS_CHANGED": 0,
 "SOUNDS_CHANGED": 0,
 "WEAPON_STATS_CHANGED": 0,
 "UIINFO_CHANGED": 0,
 "ATTACHMENT_SLOTS_CHANGED": 0,
 "UNINTENDED_EFFECTIVE_CHANGES": 0
}
```
