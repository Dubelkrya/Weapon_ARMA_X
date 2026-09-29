# L1A1 Reparent

- path: `Prefabs/Weapons/Western/Rifle/SLR/armst_SLR.et`
- GUID: C11ED52EAAF856A8
- parent before: `{3E413771E1834D2F}Rifles/armst_Rifle_M16A2.et`
- parent after: `{C63227C0E70EA62E}Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et`

## Intermediate parent contributions (now bypassed)
- SCR_MeleeWeaponProperties {5534745C44D1EFF6} m_fDamage 2
- WeaponComponent>WeaponAnimationComponent {60B4EA76EB15F6E0} M16 anims

## Effective state before
```
{
 "model": "{A0A37569F2DBA5D0}Assets/NATO/L1A1/L1A1.xob",
 "magazine_well": "{7BB9CFBDB7224657}",
 "magazine_template": "{AA9A48AAEE6E4F1B}Prefabs/Weapons/Magazines/Western/762x51/HK3/L1A1/armst_Magazine_762x51_L1A1_20_M80_Ball.et",
 "animation_refs": [
  "{0E3ECFC4E84386BC}Assets/NATO/L1A1/Anim/L1A1.agr",
  "{3B86B943995121A3}Assets/NATO/L1A1/Anim/L1A1_weapon.asi",
  "{0E3ECFC4E84386BC}Assets/NATO/L1A1/Anim/L1A1.agr",
  "{C0D828720150454F}Assets/NATO/L1A1/Anim/L1A1_player.asi"
 ],
 "has_sights": true,
 "has_uiinfo_desc": true,
 "ik_pose": "{B7869ABD0EEE379D}Assets/Weapons/Rifles/AK74/anims/anm/p_ak74_ik.anm",
 "melee_damage": "2",
 "fire_modes_local": false,
 "sounds_local": false
}
```
## Effective state after
```
{
 "model": "{A0A37569F2DBA5D0}Assets/NATO/L1A1/L1A1.xob",
 "magazine_well": "{7BB9CFBDB7224657}",
 "magazine_template": "{AA9A48AAEE6E4F1B}Prefabs/Weapons/Magazines/Western/762x51/HK3/L1A1/armst_Magazine_762x51_L1A1_20_M80_Ball.et",
 "animation_refs": [
  "{0E3ECFC4E84386BC}Assets/NATO/L1A1/Anim/L1A1.agr",
  "{3B86B943995121A3}Assets/NATO/L1A1/Anim/L1A1_weapon.asi",
  "{0E3ECFC4E84386BC}Assets/NATO/L1A1/Anim/L1A1.agr",
  "{C0D828720150454F}Assets/NATO/L1A1/Anim/L1A1_player.asi"
 ],
 "has_sights": true,
 "has_uiinfo_desc": true,
 "ik_pose": "{B7869ABD0EEE379D}Assets/Weapons/Rifles/AK74/anims/anm/p_ak74_ik.anm",
 "melee_damage": "2",
 "fire_modes_local": false,
 "sounds_local": false
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
 "UNINTENDED_EFFECTIVE_CHANGES": 0
}
```
