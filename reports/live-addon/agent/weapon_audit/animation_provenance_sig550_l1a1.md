# Sig550 / L1A1 Animation Provenance (READ ONLY)

## Sig550 (`Prefabs/Weapons/Western/Rifle/Sig550/armst_Rifle_Sig550.et`, guid CA3BEBAADDFAF1DE)
- parent: `{3E413771E1834D2F}Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et`
- model: `{C49097527FAF33B1}Assets/Weapons_NATO/Sig SG 550/SG550.xob`
- WeaponAnimationComponent: 60B4EA76EB15F6E0
- current AnimGraph: VZ58.agr `Assets/Weapons/Rifles/workspaces/VZ58.agr`
- current AnimInstance: VZ58_weapon.asi / VZ58_player.asi
- current IK: `{A467945D1C570C24}Assets/Weapons_NATO/Sig SG 550/Anim/Diff/p_rfl_sg550_ik.anm`
- dedicated SIG550 anim assets EXIST: Assets/Weapons_NATO/Sig SG 550/Anim/sg550.agf, Assets/Weapons_NATO/Sig SG 550/Anim/sg550.agr, Assets/Weapons_NATO/Sig SG 550/Anim/sg550.ast, Assets/Weapons_NATO/Sig SG 550/Anim/sg550_player.asi, Assets/Weapons_NATO/Sig SG 550/Anim/sg550_weapon.asi, Assets/Weapons_NATO/Sig SG 550/Anim/Diff/p_rfl_sg550_ik.anm, Assets/Weapons_NATO/Sig SG 550/Anim/Diff/p_rfl_sg550_offset.anm, Assets/Weapons_NATO/Sig SG 550/Anim/Diff/p_rfl_sg550_safety.anm
- VZ58 anim users: Sig550 + VZ58 base only (dedicated VZ58 resources)
- CLASSIFICATION: **SIG550_ANIMATION_WRONG**
- reason: Dedicated SIG550 animation assets exist (sg550.agr / sg550_weapon.asi / sg550_player.asi) and the file already uses the correct SIG550 IK, but the WeaponAnimationComponent {60B4EA76EB15F6E0} points to VZ58-only assets. VZ58 workspace assets are used only by Sig550 and the VZ58 base -> accidental/dedicated-VZ58 copy, incompatible with the SG550 mesh skeleton.
- proven replacement: {"AnimGraph": "{5C317A2AC249E0D9}Assets/Weapons_NATO/Sig SG 550/Anim/sg550.agr", "AnimInstance": "{5336FDF794F5FECC}Assets/Weapons_NATO/Sig SG 550/Anim/sg550_weapon.asi", "InjectionAnimGraph": "{5C317A2AC249E0D9}Assets/Weapons_NATO/Sig SG 550/Anim/sg550.agr", "InjectionAnimInstance": "{A8686CC60CF49A20}Assets/Weapons_NATO/Sig SG 550/Anim/sg550_player.asi", "IK_already_correct": "{A467945D1C570C24}Assets/Weapons_NATO/Sig SG 550/Anim/Diff/p_rfl_sg550_ik.anm"}

## L1A1 / SLR (`Prefabs/Weapons/Western/Rifle/SLR/armst_SLR.et`, guid C11ED52EAAF856A8)
- current IK: `{B7869ABD0EEE379D}Assets/Weapons/Rifles/AK74/anims/anm/p_ak74_ik.anm`
- dedicated L1A1 IK asset: NONE (only reload/fire/idle .anm found)
- AK74 IK users: G36 (approved) + SLR
- CLASSIFICATION: **UNRESOLVED**
- reason: L1A1/SLR IK pose points to AK74 p_ak74_ik.anm. No dedicated L1A1 IK pose asset found (only L1A1 reload/fire/idle .anm). AK74 IK is also used by G36 (approved workaround) but is not approved for L1A1.
- proven replacement: NONE

LIVE_FILES_CHANGED: NONE
