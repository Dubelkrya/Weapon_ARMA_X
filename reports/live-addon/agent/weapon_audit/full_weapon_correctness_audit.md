# Full ARMST Weapon Correctness Audit (READ ONLY)

TOTAL_WEAPONS_AUDITED: 34
RESULTS: {'PASS': 29, 'PASS_WITH_KNOWN_DEBT': 4, 'REVIEW_REQUIRED': 1}

| weapon | parent | well | default mag | anim | sights | status | notes |
|---|---|---|---|---|---|---|---|
| armst_AK105.et | `{FA5C25BF66A53DCF}Rifles/AK74/armst_AK74.et` | - | `-` | 0 | 0 | PASS | - |
| armst_AK74.et | `{923D948AB0D57A50}Prefabs/Weapons/Rifles/AK74/Rifle_AK74_long_base.et` | - | `-` | 0 | 0 | PASS | - |
| armst_AK74M_full.et | `{5B8E766C0E3C13EE}Prefabs/Weapons/Rifles/AK74/armst_AK74M.et` | - | `-` | 0 | 0 | PASS | - |
| armst_AKS.et | `{96DFD2E7E63B3386}Prefabs/Weapons/Rifles/AK74/armst_AK74N.et` | - | `-` | 0 | 0 | PASS | - |
| armst_AKS74U.et | `{8BA0D0DE316D1B44}Prefabs/Weapons/Rifles/AKS74U/Rifle_AKS74U_base.et` | - | `-` | 0 | 0 | PASS | - |
| armst_AKS74UN.et | `{9AE416F8879DDA6D}Prefabs/Weapons/Rifles/AKS74U/Rifle_AKS74UN_base.et` | - | `-` | 0 | 0 | PASS | - |
| armst_Rifle_AKMS.et | `{140E94F473B60FE3}Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et` | - | `-` | 0 | 0 | PASS | - |
| armst_Rifle_AKM_full.et | `{5BFF97EFD0BF6D9F}Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM.et` | - | `-` | 0 | 0 | PASS | - |
| armst_Rifle_SOC94.et | `{140E94F473B60FE3}Rifles/AKM/armst_Rifle_AKM_base.et` | - | `armst_Magazine_762x39_AKM_10rnd_Ball.et` | 2 | 1 | PASS | - |
| armst_Rifle_VPO136.et | `{140E94F473B60FE3}Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et` | - | `armst_Magazine_762x39_AKM_10rnd_Ball.et` | 0 | 0 | PASS | - |
| armst_AEK971_test_v11.et | `{EAE9A298979C4721}Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et` | - | `-` | 0 | 1 | PASS | - |
| armst_Groza_base.et | `{911D6C8DC7BA2D63}Prefabs/Weapons/Core/Rifle_Base.et` | MagazineWell9x39 | `armst_Magazine_9x39_Groza_20rnd_SP5.et` | 4 | 1 | PASS_WITH_KNOWN_DEBT | CASING |
| armst_SVD.et | `{A3E183EB5A2F3A38}Prefabs/Weapons/Rifles/SVD/Rifle_SVD_base.et` | - | `-` | 0 | 0 | PASS | - |
| armst_Rifle_9a91_base.et | `{1FA22B1F5E7BC80B}Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et` | MagazineWell9x39_9a91 | `armst_Magazine_9x39_20rnd_9a91_SP5.et` | 4 | 1 | PASS | - |
| armst_Rifle_val_base.et | `{1FA22B1F5E7BC80B}Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et` | MagazineWell9x39 | `Magazine_9x39_30rnd_val_SP5.et` | 4 | 1 | PASS | - |
| armst_Rifle_vss_base.et | `{1FA22B1F5E7BC80B}Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et` | MagazineWell9x39 | `armst_Magazine_9x39_20rnd_vss_SP5.et` | 4 | 1 | PASS | - |
| armst_Rifle_VSK94_base.et | `{1FA22B1F5E7BC80B}Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et` | MagazineWell9x39_9a91 | `armst_Magazine_9x39_20rnd_9a91_SP5.et` | 4 | 1 | PASS | - |
| armst_Rifle_HKG33.et | `{C63227C0E70EA62E}Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et` | MagazineWellHK3 | `armst_Magazine_762x51_HK3_20_M80_Ball.et` | 4 | 1 | PASS | - |
| armst_Rifle_hk_g36.et | `{911D6C8DC7BA2D63}Prefabs/Weapons/Core/Rifle_Base.et` | MagazineWellHKG36 | `armst_Magazine_556x45_HKG36.et` | 4 | disabled | PASS_WITH_KNOWN_DEBT | UNRESOLVED_ASSET; APPROVED |
| armst_Rifle_L85.et | `{C63227C0E70EA62E}Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et` | - | `-` | 4 | 1 | PASS | - |
| armst_SLR.et | `{C63227C0E70EA62E}Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et` | MagazineWellL1A1 | `armst_Magazine_762x51_L1A1_20_M80_Ball.et` | 4 | 1 | PASS_WITH_KNOWN_DEBT | UNRESOLVED_ASSET; KNOW_WORKAROUND_CANDIDATE |
| armst_Rifle_Sig550.et | `{3E413771E1834D2F}Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et` | - | `armst_Magazine_556x45_SIG_550.et` | 4 | 1 | REVIEW_REQUIRED | UNRESOLVED_ASSET; UNRESOLVED_ASSET; UNRESOLVED_ASSET; UNRESOLVED_ASSET; ANIMATION_MISMATCH |
| armst_Rifle_M16A2.et | `{C63227C0E70EA62E}Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et` | - | `-` | 4 | 0 | PASS_WITH_KNOWN_DEBT | UNRESOLVED_ASSET; UNRESOLVED_ASSET; UNRESOLVED_ASSET; UNRESOLVED_ASSET |
| armst_Rifle_M16A2_carbine.et | `{9207B5D36C3C8C94}Prefabs/Weapons/Rifles/M16/Rifle_M16A2_carbine_base.et` | - | `-` | 0 | 0 | PASS | - |
| armst_VZ58P.et | `{C19BFAF8A6334FD5}Prefabs/Weapons/Rifles/VZ58/Rifle_VZ58_base.et` | - | `-` | 0 | 0 | PASS | - |
| armst_VZ58V.et | `{C19BFAF8A6334FD5}Prefabs/Weapons/Rifles/VZ58/Rifle_VZ58_base.et` | - | `-` | 0 | 0 | PASS | - |
| armst_PM.et | `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et` | - | `armst_Magazine_9x18_PM_8rnd_Ball_PP.et` | 0 | 0 | PASS | - |
| armst_APB.et | `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et` | MagazineWellAPB | `armst_Magazine_9x18_APB_20rnd_Ball.et` | 0 | 1 | PASS | - |
| armst_PP91.et | `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et` | MagazineWellPP91 | `armst_Magazine_9x18_PP91_30rnd_Ball.et` | 4 | 1 | PASS | - |
| armst_SR_2.et | `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et` | MagazineWellPP91 | `armst_Magazine_9x18_SR2_30rnd_Ball.et` | 4 | 1 | PASS | - |
| armst_TT.et | `{B7132459C07777CA}Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et` | MagazineWell763x25 | `armst_Magazine_763x25_TT_8rnd_Ball.et` | 0 | 1 | PASS | - |
| armst_M9.et | `{809488C4984AC087}Prefabs/Weapons/Handguns/M9/Handgun_M9_base.et` | - | `-` | 0 | 0 | PASS | - |
| armst_PKM.et | `{76C400582D3C4AF9}Prefabs/Weapons/MachineGuns/PKM/MG_PKM_base.et` | - | `-` | 0 | 0 | PASS | - |
| armst_RPK74.et | `{3BFBE9145E9C40B9}Prefabs/Weapons/MachineGuns/RPK74/MG_RPK74_base.et` | - | `-` | 0 | 0 | PASS | - |

## Findings
- [KNOWN_DEBT/CASING] armst_Groza_base.et: Casing_762x39_PS.ptc WRONG_FOR_9x39 no proven replacement
- [INFO/UNRESOLVED_ASSET] armst_Rifle_hk_g36.et: {B7869ABD0EEE379D}Assets/Weapons/Rifles/AK74/anims/anm/p_ak74_ik.anm
- [INTENTIONAL/APPROVED] armst_Rifle_hk_g36.et: AK74 IK workaround
- [INFO/UNRESOLVED_ASSET] armst_SLR.et: {B7869ABD0EEE379D}Assets/Weapons/Rifles/AK74/anims/anm/p_ak74_ik.anm
- [MEDIUM/KNOW_WORKAROUND_CANDIDATE] armst_SLR.et: AK74 IK pose on L1A1 (pre-existing; earlier classified AMBIGUOUS)
- [INFO/UNRESOLVED_ASSET] armst_Rifle_Sig550.et: {E7E67E4426E24066}Assets/Weapons/Rifles/workspaces/VZ58.agr
- [INFO/UNRESOLVED_ASSET] armst_Rifle_Sig550.et: {FFB391312D0E84C5}Assets/Weapons/Rifles/workspaces/VZ58_weapon.asi
- [INFO/UNRESOLVED_ASSET] armst_Rifle_Sig550.et: {E7E67E4426E24066}Assets/Weapons/Rifles/workspaces/VZ58.agr
- [INFO/UNRESOLVED_ASSET] armst_Rifle_Sig550.et: {04ED0000B50FE029}Assets/Weapons/Rifles/workspaces/VZ58_player.asi
- [HIGH/ANIMATION_MISMATCH] armst_Rifle_Sig550.et: Sign550 animation refs point to VZ58 workspace assets (foreign family) - verify
- [INFO/UNRESOLVED_ASSET] armst_Rifle_M16A2.et: {C10E1E127E210526}Assets/Weapons/Rifles/workspaces/m16.agr
- [INFO/UNRESOLVED_ASSET] armst_Rifle_M16A2.et: {278604E4583F2647}Assets/Weapons/Rifles/workspaces/m16_weapon.asi
- [INFO/UNRESOLVED_ASSET] armst_Rifle_M16A2.et: {C10E1E127E210526}Assets/Weapons/Rifles/workspaces/m16.agr
- [INFO/UNRESOLVED_ASSET] armst_Rifle_M16A2.et: {DCD895D5C03E42AB}Assets/Weapons/Rifles/workspaces/m16_player.asi

## Known exceptions
- armst_Rifle_hk_g36.et: AK74 IK workaround (approved)
- armst_Rifle_hk_g36.et: M16-derived sound/muzzle (do not reopen)
- armst_Rifle_hk_g36.et: short Rifle_Base chain (accepted)
- armst_Rifle_hk_g36.et: top-module factory+picatinny architecture (accepted)
- armst_Groza_base.et: Muzzle_AK74.ptc intentional shared effect
- armst_SR_2.et: MagazineWellPP91 intentional shared compatibility
- armst_Rifle_L85.et: resource filename L85 but mesh L86 (ambiguous historical filename; not renamed)
- armst_Rifle_HKG33.et: resource filename HKG33 but semantic identity HK G3

## Known debt
- armst_Groza_base.et: Casing_762x39_PS.ptc WRONG_FOR_9x39 NO_PROVEN_REPLACEMENT (known debt)

INTENTIONAL_EXCEPTIONS_COUNT: 1
KNOWN_DEBT_COUNT: 1
LIVE_FILES_CHANGED: NONE
