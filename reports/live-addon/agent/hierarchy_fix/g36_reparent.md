# G36 Reparent — PRE-MUTATION SAFETY GATE

- path: `Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_hk_g36.et`
- GUID: A802C718201D72DF
- model: `{9319B3B8F246C59B}Assets/Weapons_NATO/HKG36/HKG36.xob`
- parent before: `{911D6C8DC7BA2D63}Prefabs/Weapons/Core/Rifle_Base.et`
- parent after (intended): `{C63227C0E70EA62E}Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et`
- inheritance chain before: ['{911D6C8DC7BA2D63}Prefabs/Weapons/Core/Rifle_Base.et', '{E1F14DB52DBFBC57}Prefabs/Weapons/Core/Weapon_Base.et']

## Decision: REPARENT NOT PERFORMED (REVIEW_REQUIRED)

Current parent is `Prefabs/Weapons/Core/Rifle_Base.et` (only 5 components). Reparenting to `Rifle_M16A2_base.et` would newly inherit M16A2-specific components/fields that G36 does not locally shadow, including gameplay-critical ones.

## M16-only critical components that would be newly inherited (17)
- `5534745C44D1EF26` MagazineWell MagazineWellStanag556
- `5534745C44D1EF52` ZeroingWeaponAimModifier 
- `5534745C44D1EF58` AttachmentSlotComponent 
- `5534745C44D1EF5A` AnimInjection AnimationAttachmentInfo
- `5534745C44D1EFF0` RigidBody 
- `5534745C44D1EFF6` SCR_MeleeWeaponProperties 
- `5584D01594F61795` RecoilWeaponAimModifier 
- `56DE9C900611C1AF` AttachmentSlotComponent 
- `58E2B5510A713A07` AttachmentType AttachmentHandGuardM16
- `5A5CDB17A85868B7` AttachmentType AttachmentOpticsCarryHandle
- `5D527627CCB8F756` AttachmentSlotComponent 
- `5D527627EB018141` AttachmentType AttachmentMuzzle556_45
- `5F16E0B4B2D0D72C` AttachmentSlotComponent 
- `60AAE4351FBECDEA` AttachmentType AttachmentBayonetM9
- `60ECB1E9AB301676` UserActionContext 
- `6188FC1045F23E2A` SCR_WeaponStatsManagerComponent 
- `61FECC7EE21E0318` UserActionContext 

## Shared components with unshadowed M16A2 fields (0)

## Foreign / legacy refs recorded (not repaired)
- local IK pose: `{B7869ABD0EEE379D}Assets/Weapons/Rifles/AK74/anims/anm/p_ak74_ik.anm`

## Status
```
{
 "PARENT_CHANGED": 0,
 "mutation_performed": false,
 "SAFETY_GATE": "TRIPPED",
 "AMBIGUOUS_CRITICAL_COUNT": 17,
 "status": "REVIEW_REQUIRED"
}
```
