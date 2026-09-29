# Pistol Inheritance Audit (READ ONLY)

## Pistols
| file | guid | model |
|---|---|---|
| armst_APB.et | 5D3DA7E84135B278 | `{A72F391188860251}Assets/Apb/APB_weapon.xob` |
| armst_PM.et | C0F7DD85A86B2900 | `(inherited)` |
| armst_PP91.et | 3968B2A856852CBD | `{C783576039056FE8}Assets/Kedr/Kedr_weapons.xob` |
| armst_SR_2.et | 31FB2EC4F4AFFC05 | `{DE11A7B572066CCA}Assets/sr2/SR2.xob` |
| armst_TT.et | 0D469F42B65E350E | `{3142577B6CD35911}Assets/TT/TT_weapon.xob` |
| armst_M9.et | 1353C6EAD1DCFE43 | `(inherited)` |

## Inheritance edges
- `armst_APB.et` -> parent-ref `C0F7DD85A86B2900` `Handguns/armst_PM.et` -> `armst_PM.et` [SUSPICIOUS_CONCRETE_WEAPON_PARENT] **SUSPICIOUS**
- `armst_PM.et` -> parent-ref `B7132459C07777CA` `Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et` -> `Handgun_PM_base.et` [VALID_VARIANT_INHERITANCE]
- `Handgun_PM_base.et` -> parent-ref `EE7028E9DF49763A` `Prefabs/Weapons/Core/Handgun_Base.et` -> `Handgun_Base.et` [COMMON_BASE]
- `Handgun_Base.et` -> parent-ref `E1F14DB52DBFBC57` `Prefabs/Weapons/Core/Weapon_Base.et` -> `Weapon_Base.et` [AMBIGUOUS]
- `Weapon_Base.et` -> parent-ref `None` `None` -> `None` [EXTERNAL_BOUNDARY]
- `armst_PM.et` -> parent-ref `B7132459C07777CA` `Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et` -> `Handgun_PM_base.et` [VALID_VARIANT_INHERITANCE]
- `Handgun_PM_base.et` -> parent-ref `EE7028E9DF49763A` `Prefabs/Weapons/Core/Handgun_Base.et` -> `Handgun_Base.et` [COMMON_BASE]
- `Handgun_Base.et` -> parent-ref `E1F14DB52DBFBC57` `Prefabs/Weapons/Core/Weapon_Base.et` -> `Weapon_Base.et` [AMBIGUOUS]
- `Weapon_Base.et` -> parent-ref `None` `None` -> `None` [EXTERNAL_BOUNDARY]
- `armst_PP91.et` -> parent-ref `C0F7DD85A86B2900` `Handguns/armst_PM.et` -> `armst_PM.et` [SUSPICIOUS_CONCRETE_WEAPON_PARENT] **SUSPICIOUS**
- `armst_PM.et` -> parent-ref `B7132459C07777CA` `Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et` -> `Handgun_PM_base.et` [VALID_VARIANT_INHERITANCE]
- `Handgun_PM_base.et` -> parent-ref `EE7028E9DF49763A` `Prefabs/Weapons/Core/Handgun_Base.et` -> `Handgun_Base.et` [COMMON_BASE]
- `Handgun_Base.et` -> parent-ref `E1F14DB52DBFBC57` `Prefabs/Weapons/Core/Weapon_Base.et` -> `Weapon_Base.et` [AMBIGUOUS]
- `Weapon_Base.et` -> parent-ref `None` `None` -> `None` [EXTERNAL_BOUNDARY]
- `armst_SR_2.et` -> parent-ref `3968B2A856852CBD` `Handguns/New_armst_PP91.et` -> `armst_PP91.et` [AMBIGUOUS]
- `armst_PP91.et` -> parent-ref `C0F7DD85A86B2900` `Handguns/armst_PM.et` -> `armst_PM.et` [SUSPICIOUS_CONCRETE_WEAPON_PARENT] **SUSPICIOUS**
- `armst_PM.et` -> parent-ref `B7132459C07777CA` `Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et` -> `Handgun_PM_base.et` [VALID_VARIANT_INHERITANCE]
- `Handgun_PM_base.et` -> parent-ref `EE7028E9DF49763A` `Prefabs/Weapons/Core/Handgun_Base.et` -> `Handgun_Base.et` [COMMON_BASE]
- `Handgun_Base.et` -> parent-ref `E1F14DB52DBFBC57` `Prefabs/Weapons/Core/Weapon_Base.et` -> `Weapon_Base.et` [AMBIGUOUS]
- `Weapon_Base.et` -> parent-ref `None` `None` -> `None` [EXTERNAL_BOUNDARY]
- `armst_TT.et` -> parent-ref `C0F7DD85A86B2900` `Handguns/armst_PM.et` -> `armst_PM.et` [SUSPICIOUS_CONCRETE_WEAPON_PARENT] **SUSPICIOUS**
- `armst_PM.et` -> parent-ref `B7132459C07777CA` `Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et` -> `Handgun_PM_base.et` [VALID_VARIANT_INHERITANCE]
- `Handgun_PM_base.et` -> parent-ref `EE7028E9DF49763A` `Prefabs/Weapons/Core/Handgun_Base.et` -> `Handgun_Base.et` [COMMON_BASE]
- `Handgun_Base.et` -> parent-ref `E1F14DB52DBFBC57` `Prefabs/Weapons/Core/Weapon_Base.et` -> `Weapon_Base.et` [AMBIGUOUS]
- `Weapon_Base.et` -> parent-ref `None` `None` -> `None` [EXTERNAL_BOUNDARY]
- `armst_M9.et` -> parent-ref `809488C4984AC087` `Prefabs/Weapons/Handguns/M9/Handgun_M9_base.et` -> `Handgun_M9_base.et` [VALID_VARIANT_INHERITANCE]
- `Handgun_M9_base.et` -> parent-ref `EE7028E9DF49763A` `Prefabs/Weapons/Core/Handgun_Base.et` -> `Handgun_Base.et` [COMMON_BASE]
- `Handgun_Base.et` -> parent-ref `E1F14DB52DBFBC57` `Prefabs/Weapons/Core/Weapon_Base.et` -> `Weapon_Base.et` [AMBIGUOUS]
- `Weapon_Base.et` -> parent-ref `None` `None` -> `None` [EXTERNAL_BOUNDARY]

## Candidate common base
- path: `Prefabs/Weapons/Core/Handgun_Base.et`
- engine GUID: `EE7028E9DF49763A`
- class: EntityTemplateResourceClass
- direct examples: Handgun_PM_base.et, Handgun_M9_base.et

## Per-pistol delta (if reparented to Handgun_Base)
### armst_APB.et — HIGH_RISK (lose 15, critical 5)
  - `0F2AA6AEBF450F0F` RigidBody (from Handgun_PM_base.et)
  - `5EEACC0F11A30F18` ZeroingWeaponAimModifier (from Handgun_PM_base.et)
  - `51B2B2E3D520136A` AnimInjection (from Handgun_PM_base.et)
  - `5A1E58F7B04F9BE5` UserActionContext (from Handgun_PM_base.et)
  - `5A1E58F7AED270D4` UserActionContext (from Handgun_PM_base.et)
### armst_PP91.et — HIGH_RISK (lose 12, critical 4)
  - `0F2AA6AEBF450F0F` RigidBody (from Handgun_PM_base.et)
  - `5EEACC0F11A30F18` ZeroingWeaponAimModifier (from Handgun_PM_base.et)
  - `5A1E58F7B04F9BE5` UserActionContext (from Handgun_PM_base.et)
  - `5A1E58F7AED270D4` UserActionContext (from Handgun_PM_base.et)
### armst_SR_2.et — HIGH_RISK (lose 12, critical 4)
  - `0F2AA6AEBF450F0F` RigidBody (from Handgun_PM_base.et)
  - `5EEACC0F11A30F18` ZeroingWeaponAimModifier (from Handgun_PM_base.et)
  - `5A1E58F7B04F9BE5` UserActionContext (from Handgun_PM_base.et)
  - `5A1E58F7AED270D4` UserActionContext (from Handgun_PM_base.et)
### armst_TT.et — HIGH_RISK (lose 16, critical 6)
  - `5A8685198A9AEEDD` WeaponSoundComponent (from Handgun_PM_base.et)
  - `0F2AA6AEBF450F0F` RigidBody (from Handgun_PM_base.et)
  - `5EEACC0F11A30F18` ZeroingWeaponAimModifier (from Handgun_PM_base.et)
  - `51B2B2E3D520136A` AnimInjection (from Handgun_PM_base.et)
  - `5A1E58F7B04F9BE5` UserActionContext (from Handgun_PM_base.et)
  - `5A1E58F7AED270D4` UserActionContext (from Handgun_PM_base.et)

## Risk classification
```
{
 "SAFE_SIMPLE_REPARENT": [],
 "REPARENT_WITH_SMALL_OVERRIDES": [],
 "HIGH_RISK": [
  "armst_APB.et",
  "armst_PP91.et",
  "armst_SR_2.et",
  "armst_TT.et"
 ],
 "AMBIGUOUS": []
}
```

LIVE_FILES_CHANGED: NONE
