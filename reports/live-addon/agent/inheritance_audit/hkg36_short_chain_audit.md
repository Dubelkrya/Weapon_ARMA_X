# HK G36 Short-Inheritance Completeness Audit (READ ONLY)

## Inheritance chain
- `Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_hk_g36.et` [G36 gameplay weapon (self-contained)] - all visible gameplay: sound, mesh, rigidbody, melee, storage override, stats manager, WeaponComponent (sights/muzzle/magwell/firemodes/aim), animation, actions
- `Prefabs/Weapons/Core/Rifle_Base.et` [core rifle base] - EPF_PersistenceComponent, SCR_WeaponAttachmentsStorageComponent {51F080D5CE45A1A2} (overridden locally by G36)
- `Prefabs/Weapons/Core/Weapon_Base.et` [core weapon base] - ARMST_ITEMS_STATS_COMPONENTS {657ABA0547189DD7}, EPF_PersistenceComponent {5A28749C602565F8}, ActionsManagerComponent {A29AE67FF4D82B0F}
- `(unavailable) parent above Weapon_Base` [game/base weapon root] - UNKNOWN - not present in local evidence (packed); not required for this audit

- INHERITANCE_DEPTH: 3 resolvable levels in local evidence (G36 -> Rifle_Base -> Weapon_Base); one further parent unavailable (packed). Depth is NOT an error.

## Functional areas
- VISUAL_PHYSICS: PRESENT_AND_VALID - MeshObject (local, HKG36.xob), RigidBody (local {6A0470709BAE05BC})
- INVENTORY: PRESENT_AND_VALID - SCR_WeaponAttachmentsStorageComponent {51F080D5CE45A1A2} local override; ItemDisplayName/ItemPhysAttributes/ItemAnimationAttributes
- CORE_WEAPON: PRESENT_AND_VALID - WeaponComponent {CFBAA4B706BA66E8}: MuzzleComponent {CA6BE4D6B867541F}, MagazineWell MagazineWellHKG36, default template armst_Magazine_556x45_HKG36.et, FireModes, dispersion, aim modifiers
- ANIMATION: PRESENT_AND_VALID - WeaponAnimationComponent {60B4EA76EB15F6E0} HKg36.agr + HKg36_weapon.asi + HKg36_player.asi injection. IK uses AK74 workaround (intentional)
- ATTACHMENTS: PRESENT_AND_VALID - Bayonet/Muzzle slots + unique top-module slot {6A0470709BAE058E} type AttachmentOpticsG36 with factory default; no RIS1913 on weapon
- SIGHTS: INTENTIONALLY_DISABLED - weapon local SightsComponent {BB23A637957CFFF8} Enabled 0; active optic owned by attached handle
- SOUND: PRESENT_AND_VALID - local WeaponSoundComponent {5A8685198A9AEEDD} referencing M16A2 sound configs (pre-existing/legacy)
- ACTIONS: PRESENT_AND_VALID - ActionsManagerComponent {A29AE67FF4D82B0F} (same instance as Weapon_Base), attachment action contexts
- STATS: PRESENT_AND_VALID - local SCR_WeaponStatsManagerComponent {6A0470709BAE0581}; inherited ARMST_ITEMS_STATS_COMPONENTS {657ABA0547189DD7}; SCR_MeleeWeaponProperties

## Local components required by short chain
- MeshObject
- RigidBody
- SCR_WeaponAttachmentsStorageComponent override
- WeaponComponent (Muzzle/MagWell/FireModes/Aim)
- WeaponAnimationComponent
- WeaponSoundComponent
- ActionsManagerComponent
- SCR_WeaponStatsManagerComponent

MISSING_REQUIRED_COMPONENTS: NONE

## Foreign / suspicious
- Muzzle particle {DDF8E6F5BCEABCCC}Particles/Weapon/Muzzle_M16A2_Open.ptc [FOREIGN_SUSPICIOUS] M16A2 muzzle effect on G36 (pre-existing)
- WeaponSoundComponent filenames Weapons_Rifles_M16A2_* [FOREIGN_SUSPICIOUS] M16A2 sound set on G36 (pre-existing/legacy shared)
- AttachmentType AttachmentBayonetM9 [VALID_SHARED] M9 bayonet compatibility (pre-existing)

## Intentional exceptions
- AK74 AnimationIKPose {B7869ABD0EEE379D}Assets/Weapons/Rifles/AK74/anims/anm/p_ak74_ik.anm (user-approved workaround, not flagged)

## Top-module hierarchy
```
{
 "unique_top_slot_count": 1,
 "slot_instance": "{6A0470709BAE058E}",
 "slot_type": "AttachmentOpticsG36",
 "default_prefab": "{EDBDAAE1FC7F4723}Prefabs/Weapons/Attachments/Optics/HKG36/armst_HKG36_CarryHandle_Optic.et",
 "factory_handle_exists": true,
 "picatinny_handle_exists": true,
 "direct_RIS1913_on_weapon": false
}
```

G36_FAMILY_BASE_NEEDED_NOW: NO (single G36 variant; configuration is self-contained; no duplicated config to share)
CLASSIFICATION: SHORT_CHAIN_COMPLETE_WITH_LOCAL_IMPLEMENTATION
INHERITANCE_COUNT_ITSELF: NOT_AN_ERROR

LIVE_FILES_CHANGED: NONE
