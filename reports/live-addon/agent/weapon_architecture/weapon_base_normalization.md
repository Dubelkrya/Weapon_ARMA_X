# ARMST Weapon Base Normalization

## Renamed main -> *_base (GUID preserved)
| old | new | guid |
|---|---|---|
| `Prefabs/Weapons/Western/Rifle/HKG33/armst_Rifle_HKG33.et` | `Prefabs/Weapons/Western/Rifle/HKG33/armst_Rifle_HKG33_base.et` | 035CFC7DD44455D0 |
| `Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_hk_g36.et` | `Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_HKG36_base.et` | A802C718201D72DF |
| `Prefabs/Weapons/Western/Rifle/L85/armst_Rifle_L85.et` | `Prefabs/Weapons/Western/Rifle/L85/armst_Rifle_L85_base.et` | 45D3FCA77AF1709B |
| `Prefabs/Weapons/Western/Rifle/SLR/armst_SLR.et` | `Prefabs/Weapons/Western/Rifle/SLR/armst_SLR_base.et` | C11ED52EAAF856A8 |
| `Prefabs/Weapons/Western/Rifle/Sig550/armst_Rifle_Sig550.et` | `Prefabs/Weapons/Western/Rifle/Sig550/armst_Rifle_Sig550_base.et` | CA3BEBAADDFAF1DE |
| `Prefabs/Weapons/Russian/Rifle/Aek971/armst_AEK971_test_v11.et` | `Prefabs/Weapons/Russian/Rifle/Aek971/armst_Rifle_AEK971_base.et` | AC198EAC9BDD9841 |
| `Prefabs/Weapons/Russian/Rifle/SVD/armst_SVD.et` | `Prefabs/Weapons/Russian/Rifle/SVD/armst_Rifle_SVD_base.et` | 3EB02CDAD5F23C82 |
| `Prefabs/Weapons/Russian/Handguns/Pm/armst_PM.et` | `Prefabs/Weapons/Russian/Handguns/Pm/armst_PM_base.et` | C0F7DD85A86B2900 |
| `Prefabs/Weapons/Russian/Handguns/PP_19/armst_PP91.et` | `Prefabs/Weapons/Russian/Handguns/PP_19/armst_PP91_base.et` | 3968B2A856852CBD |
| `Prefabs/Weapons/Russian/Handguns/Sr_2/armst_SR_2.et` | `Prefabs/Weapons/Russian/Handguns/Sr_2/armst_SR_2_base.et` | 31FB2EC4F4AFFC05 |
| `Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB.et` | `Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB_base.et` | 5D3DA7E84135B278 |
| `Prefabs/Weapons/Russian/Handguns/TT/armst_TT.et` | `Prefabs/Weapons/Russian/Handguns/TT/armst_TT_base.et` | 0D469F42B65E350E |
| `Prefabs/Weapons/Western/Handguns/armst_M9.et` | `Prefabs/Weapons/Western/Handguns/armst_M9_base.et` | 1353C6EAD1DCFE43 |
| `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74.et` | `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74_base.et` | FA5C25BF66A53DCF |
| `Prefabs/Weapons/Western/Rifle/armst_Rifle_M16A2.et` | `Prefabs/Weapons/Western/Rifle/armst_Rifle_M16A2_base.et` | 3E413771E1834D2F |
| `Prefabs/Weapons/Western/Rifle/armst_VZ58P.et` | `Prefabs/Weapons/Western/Rifle/armst_VZ58P_base.et` | 9C948630078D154D |
| `Prefabs/Weapons/Western/Rifle/armst_VZ58V.et` | `Prefabs/Weapons/Western/Rifle/armst_VZ58V_base.et` | 443CEFF17E040B11 |
| `Prefabs/Weapons/Russian/MachineGuns/armst_PKM.et` | `Prefabs/Weapons/Russian/MachineGuns/armst_PKM_base.et` | A89BC9D55FFB4CD8 |
| `Prefabs/Weapons/Russian/MachineGuns/armst_RPK74.et` | `Prefabs/Weapons/Russian/MachineGuns/armst_RPK74_base.et` | A7AF84C6C58BA3E8 |

## Classification
- ALREADY_OK: Groza (`armst_Groza_base.et`), 9x91/VAL/VSS/VSK94 bases, AKM (`armst_Rifle_AKM_base.et`)
- RENAME_MAIN_TO_BASE: armst_Rifle_HKG33_base.et, armst_Rifle_HKG36_base.et, armst_Rifle_L85_base.et, armst_SLR_base.et, armst_Rifle_Sig550_base.et, armst_Rifle_AEK971_base.et, armst_Rifle_SVD_base.et, armst_PM_base.et, armst_PP91_base.et, armst_SR_2_base.et, armst_APB_base.et, armst_TT_base.et, armst_M9_base.et, armst_AK74_base.et, armst_Rifle_M16A2_base.et, armst_VZ58P_base.et, armst_VZ58V_base.et, armst_PKM_base.et, armst_RPK74_base.et
- RENAME_AND_REPOINT (main renamed; variant reparent pending REVIEW): AK74 folder, Western/Rifle M16A2

## Variant reparent candidates (REVIEW_REQUIRED, not applied)
- AK74 folder: AK74N (external parent) -> armst_AK74_base; AK74M -> base (currently parent AK74N concrete); AKS -> base (currently AK74N); AK74M_full -> base
- AKM folder: armst_Rifle_AKM_full -> armst_Rifle_AKM_base (currently inherits concrete armst_Rifle_AKM)
- M16 family: SLR/L85/HKG33/Sig550 -> armst_Rifle_M16A2_base (GUID refs already point to the renamed base)

## Validation
```
{
 "renamed": 19,
 "all_guid_preserved": true,
 "all_old_absent": true,
 "all_new_exist": true,
 "all_content_identical": true,
 "old_full_path_refs_remaining": []
}
```
- duplicate_guids: pre-existing (agent backup copies); NONE of the 19 renamed GUIDs are involved.

## Notes
- Only file renames + meta path updates + live reference path updates performed; no component/gameplay edits.
- Historical relative parent paths (e.g. `Rifles/AK74/armst_AK74.et`) may remain in some children but resolve by GUID (preserved).
- Default attachments retained (base is the playable weapon).
- 12ga excluded.

LIVE_FILES_CHANGED: 19 renames (+metas) + worlds/Weapon_test/weapon_test_Layers/default.layer path updates
