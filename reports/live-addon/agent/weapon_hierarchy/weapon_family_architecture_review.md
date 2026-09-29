# Weapon Architecture Normalization Review

Analysis only. Family membership is taken strictly from the finalized graph. No normalization action is authorized.

## Current Metrics

| Metric | Value |
|---|---:|
| total_included_nodes | 51 |
| total_weapon_leaves | 32 |
| total_local_bases | 11 |
| total_local_edges | 29 |
| total_external_parent_edges | 21 |
| total_roots | 22 |
| total_families | 22 |
| cycles | 0 |
| duplicate_guid_owners | 0 |

## Family Classification

| # | Family root | Root GUID | Nodes | Leaves | Depth | External boundary | Core | Shared bases | Current structure | Future review |
|---:|---|---|---:|---:|---:|---|---|---:|---|---|
| 1 | `Prefabs/Weapons/Core/Grenade_Base.et` | `D7EB24176E5CEAA6` | 1 | 0 | 0 | Prefabs/Weapons/Core/Throw_Base.et | False | 0 | EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 2 | `Prefabs/Weapons/Core/Weapon_Base.et` | `E1F14DB52DBFBC57` | 10 | 5 | 4 | NONE | True | 2 | LOCAL_FAMILY_OVER_EXTERNAL+LOCAL_VARIANT_CHAIN+SHARED_INTERMEDIATE_BASE+CORE_HIERARCHY | POSSIBLE_CORE_INTEGRATION |
| 3 | `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et` | `26ADE11C416B3840` | 1 | 0 | 0 | Prefabs/Weapons/Core/Handgun_Base.et | False | 0 | EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 4 | `Prefabs/Weapons/Handguns/armst_M9.et` | `1353C6EAD1DCFE43` | 1 | 1 | 0 | Prefabs/Weapons/Handguns/M9/Handgun_M9_base.et | False | 0 | SINGLE_WEAPON_EXTERNAL_WRAPPER+EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 5 | `Prefabs/Weapons/Handguns/armst_PM.et` | `C0F7DD85A86B2900` | 5 | 3 | 2 | Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et | False | 1 | LOCAL_VARIANT_CHAIN+SHARED_INTERMEDIATE_BASE+EXTERNAL_DEPENDENCY_REVIEW | POSSIBLE_LOCAL_BASE_EXTRACTION |
| 6 | `Prefabs/Weapons/MachineGuns/armst_PKM.et` | `A89BC9D55FFB4CD8` | 1 | 1 | 0 | Prefabs/Weapons/MachineGuns/PKM/MG_PKM_base.et | False | 0 | SINGLE_WEAPON_EXTERNAL_WRAPPER+EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 7 | `Prefabs/Weapons/MachineGuns/armst_RPK74.et` | `A7AF84C6C58BA3E8` | 1 | 1 | 0 | Prefabs/Weapons/MachineGuns/RPK74/MG_RPK74_base.et | False | 0 | SINGLE_WEAPON_EXTERNAL_WRAPPER+EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 8 | `Prefabs/Weapons/Rifles/9a91/armst_Rifle_9a91_base.et` | `E2D8F39AE1B9B8F1` | 1 | 0 | 0 | Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et | False | 0 | EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 9 | `Prefabs/Weapons/Rifles/AK74/armst_AK74.et` | `FA5C25BF66A53DCF` | 2 | 1 | 1 | Prefabs/Weapons/Rifles/AK74/Rifle_AK74_long_base.et | False | 0 | EXTERNAL_DEPENDENCY_REVIEW | EXTERNAL_DEPENDENCY_REVIEW |
| 10 | `Prefabs/Weapons/Rifles/AK74/armst_AK74N.et` | `96DFD2E7E63B3386` | 4 | 2 | 2 | Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et | False | 1 | LOCAL_VARIANT_CHAIN+SHARED_INTERMEDIATE_BASE+EXTERNAL_DEPENDENCY_REVIEW | POSSIBLE_LOCAL_BASE_EXTRACTION |
| 11 | `Prefabs/Weapons/Rifles/AK74/armst_AKS74U.et` | `BFEA719491610A45` | 1 | 1 | 0 | Prefabs/Weapons/Rifles/AKS74U/Rifle_AKS74U_base.et | False | 0 | SINGLE_WEAPON_EXTERNAL_WRAPPER+EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 12 | `Prefabs/Weapons/Rifles/AK74/armst_AKS74UN.et` | `FA0E25CE35EE945F` | 1 | 1 | 0 | Prefabs/Weapons/Rifles/AKS74U/Rifle_AKS74UN_base.et | False | 0 | SINGLE_WEAPON_EXTERNAL_WRAPPER+EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 13 | `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et` | `6C5E2009CDCD0BD3` | 9 | 7 | 2 | Prefabs/Weapons/Rifles/M14/Rifle_M21.et | False | 2 | LOCAL_FAMILY_OVER_EXTERNAL+LOCAL_VARIANT_CHAIN+SHARED_INTERMEDIATE_BASE+EXTERNAL_DEPENDENCY_REVIEW | POSSIBLE_LOCAL_BASE_EXTRACTION |
| 14 | `Prefabs/Weapons/Rifles/VAL/armst_Rifle_val_base.et` | `F25D16BD5F748372` | 1 | 0 | 0 | Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et | False | 0 | EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 15 | `Prefabs/Weapons/Rifles/VSK94/armst_Rifle_VSK94_base.et` | `6005623D3AA5F5C2` | 1 | 0 | 0 | Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et | False | 0 | EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 16 | `Prefabs/Weapons/Rifles/VSS/armst_Rifle_vss_base.et` | `902A79E4B2A66E63` | 1 | 0 | 0 | Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et | False | 0 | EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 17 | `Prefabs/Weapons/Rifles/armst_AEK971_test_v11.et` | `AC198EAC9BDD9841` | 1 | 1 | 0 | Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et | False | 0 | SINGLE_WEAPON_EXTERNAL_WRAPPER+EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 18 | `Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et` | `3E413771E1834D2F` | 5 | 4 | 1 | Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et | False | 1 | SHARED_INTERMEDIATE_BASE+EXTERNAL_DEPENDENCY_REVIEW | POSSIBLE_LOCAL_BASE_EXTRACTION |
| 19 | `Prefabs/Weapons/Rifles/armst_Rifle_M16A2_carbine.et` | `F97A4AC994231900` | 1 | 1 | 0 | Prefabs/Weapons/Rifles/M16/Rifle_M16A2_carbine_base.et | False | 0 | SINGLE_WEAPON_EXTERNAL_WRAPPER+EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 20 | `Prefabs/Weapons/Rifles/armst_SVD.et` | `3EB02CDAD5F23C82` | 1 | 1 | 0 | Prefabs/Weapons/Rifles/SVD/Rifle_SVD_base.et | False | 0 | SINGLE_WEAPON_EXTERNAL_WRAPPER+EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 21 | `Prefabs/Weapons/Rifles/armst_VZ58P.et` | `9C948630078D154D` | 1 | 1 | 0 | Prefabs/Weapons/Rifles/VZ58/Rifle_VZ58_base.et | False | 0 | SINGLE_WEAPON_EXTERNAL_WRAPPER+EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |
| 22 | `Prefabs/Weapons/Rifles/armst_VZ58V.et` | `443CEFF17E040B11` | 1 | 1 | 0 | Prefabs/Weapons/Rifles/VZ58/Rifle_VZ58_base.et | False | 0 | SINGLE_WEAPON_EXTERNAL_WRAPPER+EXTERNAL_DEPENDENCY_REVIEW | LEAVE_UNTIL_FUNCTIONAL_REASON |

## Family Details

### 1. Prefabs/Weapons/Core/Grenade_Base.et

- root GUID: `D7EB24176E5CEAA6`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Core/Throw_Base.et`
- local node count: 1
- weapon leaves: 0
- max local depth: 0
- shared local bases: none
- current structure: EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Core/Grenade_Base.et` | GUID `D7EB24176E5CEAA6` | role `BASE` | parent `Prefabs/Weapons/Core/Throw_Base.et`

### 2. Prefabs/Weapons/Core/Weapon_Base.et

- root GUID: `E1F14DB52DBFBC57`
- root parent status: `ROOT`
- external boundary: `NONE`
- local node count: 10
- weapon leaves: 5
- max local depth: 4
- shared local bases: `Prefabs/Weapons/Core/Rifle_Base.et`, `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et`
- current structure: LOCAL_FAMILY_OVER_EXTERNAL, LOCAL_VARIANT_CHAIN, SHARED_INTERMEDIATE_BASE, CORE_HIERARCHY
- current chain:
  - depth 0: `Prefabs/Weapons/Core/Weapon_Base.et` | GUID `E1F14DB52DBFBC57` | role `BASE` | parent `NONE`
  - depth 1: `Prefabs/Weapons/Core/Rifle_Base.et` | GUID `911D6C8DC7BA2D63` | role `BASE` | parent `Prefabs/Weapons/Core/Weapon_Base.et`
  - depth 2: `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et` | GUID `140E94F473B60FE3` | role `BASE` | parent `Prefabs/Weapons/Core/Rifle_Base.et`
  - depth 2: `Prefabs/Weapons/Rifles/Groza/armst_Groza_base.et` | GUID `903C7920F00AB654` | role `BASE` | parent `Prefabs/Weapons/Core/Rifle_Base.et`
  - depth 2: `Prefabs/Weapons/Rifles/armst_Rifle_hk_g36.et` | GUID `A802C718201D72DF` | role `LEAF` | parent `Prefabs/Weapons/Core/Rifle_Base.et`
  - depth 3: `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM.et` | GUID `5BFF97EFD0BF6D9F` | role `INTERMEDIATE` | parent `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et`
  - depth 3: `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKMS.et` | GUID `5712F6F88A014F0B` | role `LEAF` | parent `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et`
  - depth 3: `Prefabs/Weapons/Rifles/AKM/armst_Rifle_SOC94.et` | GUID `E394112ABBC198D8` | role `LEAF` | parent `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et`
  - depth 3: `Prefabs/Weapons/Rifles/AKM/armst_Rifle_VPO136.et` | GUID `90EADC5DD9AD35D5` | role `LEAF` | parent `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et`
  - depth 4: `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_full.et` | GUID `33BEE1A93C920B26` | role `LEAF` | parent `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM.et`

### 3. Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et

- root GUID: `26ADE11C416B3840`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Core/Handgun_Base.et`
- local node count: 1
- weapon leaves: 0
- max local depth: 0
- shared local bases: none
- current structure: EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et` | GUID `26ADE11C416B3840` | role `BASE` | parent `Prefabs/Weapons/Core/Handgun_Base.et`

### 4. Prefabs/Weapons/Handguns/armst_M9.et

- root GUID: `1353C6EAD1DCFE43`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Handguns/M9/Handgun_M9_base.et`
- local node count: 1
- weapon leaves: 1
- max local depth: 0
- shared local bases: none
- current structure: SINGLE_WEAPON_EXTERNAL_WRAPPER, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Handguns/armst_M9.et` | GUID `1353C6EAD1DCFE43` | role `LEAF` | parent `Prefabs/Weapons/Handguns/M9/Handgun_M9_base.et`

### 5. Prefabs/Weapons/Handguns/armst_PM.et

- root GUID: `C0F7DD85A86B2900`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`
- local node count: 5
- weapon leaves: 3
- max local depth: 2
- shared local bases: `Prefabs/Weapons/Handguns/armst_PM.et`
- current structure: LOCAL_VARIANT_CHAIN, SHARED_INTERMEDIATE_BASE, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Handguns/armst_PM.et` | GUID `C0F7DD85A86B2900` | role `INTERMEDIATE` | parent `Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et`
  - depth 1: `Prefabs/Weapons/Handguns/armst_APB.et` | GUID `5D3DA7E84135B278` | role `LEAF` | parent `Prefabs/Weapons/Handguns/armst_PM.et`
  - depth 1: `Prefabs/Weapons/Handguns/armst_PP91.et` | GUID `3968B2A856852CBD` | role `INTERMEDIATE` | parent `Prefabs/Weapons/Handguns/armst_PM.et`
  - depth 1: `Prefabs/Weapons/Handguns/armst_TT.et` | GUID `0D469F42B65E350E` | role `LEAF` | parent `Prefabs/Weapons/Handguns/armst_PM.et`
  - depth 2: `Prefabs/Weapons/Handguns/armst_SR_2.et` | GUID `31FB2EC4F4AFFC05` | role `LEAF` | parent `Prefabs/Weapons/Handguns/armst_PP91.et`

### 6. Prefabs/Weapons/MachineGuns/armst_PKM.et

- root GUID: `A89BC9D55FFB4CD8`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/MachineGuns/PKM/MG_PKM_base.et`
- local node count: 1
- weapon leaves: 1
- max local depth: 0
- shared local bases: none
- current structure: SINGLE_WEAPON_EXTERNAL_WRAPPER, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/MachineGuns/armst_PKM.et` | GUID `A89BC9D55FFB4CD8` | role `LEAF` | parent `Prefabs/Weapons/MachineGuns/PKM/MG_PKM_base.et`

### 7. Prefabs/Weapons/MachineGuns/armst_RPK74.et

- root GUID: `A7AF84C6C58BA3E8`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/MachineGuns/RPK74/MG_RPK74_base.et`
- local node count: 1
- weapon leaves: 1
- max local depth: 0
- shared local bases: none
- current structure: SINGLE_WEAPON_EXTERNAL_WRAPPER, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/MachineGuns/armst_RPK74.et` | GUID `A7AF84C6C58BA3E8` | role `LEAF` | parent `Prefabs/Weapons/MachineGuns/RPK74/MG_RPK74_base.et`

### 8. Prefabs/Weapons/Rifles/9a91/armst_Rifle_9a91_base.et

- root GUID: `E2D8F39AE1B9B8F1`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et`
- local node count: 1
- weapon leaves: 0
- max local depth: 0
- shared local bases: none
- current structure: EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/9a91/armst_Rifle_9a91_base.et` | GUID `E2D8F39AE1B9B8F1` | role `BASE` | parent `Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et`

### 9. Prefabs/Weapons/Rifles/AK74/armst_AK74.et

- root GUID: `FA5C25BF66A53DCF`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/AK74/Rifle_AK74_long_base.et`
- local node count: 2
- weapon leaves: 1
- max local depth: 1
- shared local bases: none
- current structure: EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/AK74/armst_AK74.et` | GUID `FA5C25BF66A53DCF` | role `INTERMEDIATE` | parent `Prefabs/Weapons/Rifles/AK74/Rifle_AK74_long_base.et`
  - depth 1: `Prefabs/Weapons/Rifles/AK74/armst_AK105.et` | GUID `6FC3151D0DED22A9` | role `LEAF` | parent `Prefabs/Weapons/Rifles/AK74/armst_AK74.et`

### 10. Prefabs/Weapons/Rifles/AK74/armst_AK74N.et

- root GUID: `96DFD2E7E63B3386`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et`
- local node count: 4
- weapon leaves: 2
- max local depth: 2
- shared local bases: `Prefabs/Weapons/Rifles/AK74/armst_AK74N.et`
- current structure: LOCAL_VARIANT_CHAIN, SHARED_INTERMEDIATE_BASE, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/AK74/armst_AK74N.et` | GUID `96DFD2E7E63B3386` | role `INTERMEDIATE` | parent `Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et`
  - depth 1: `Prefabs/Weapons/Rifles/AK74/armst_AK74M.et` | GUID `5B8E766C0E3C13EE` | role `INTERMEDIATE` | parent `Prefabs/Weapons/Rifles/AK74/armst_AK74N.et`
  - depth 1: `Prefabs/Weapons/Rifles/AK74/armst_AKS.et` | GUID `25A64724FD416989` | role `LEAF` | parent `Prefabs/Weapons/Rifles/AK74/armst_AK74N.et`
  - depth 2: `Prefabs/Weapons/Rifles/AK74/armst_AK74M_full.et` | GUID `63892659A632A0FD` | role `LEAF` | parent `Prefabs/Weapons/Rifles/AK74/armst_AK74M.et`

### 11. Prefabs/Weapons/Rifles/AK74/armst_AKS74U.et

- root GUID: `BFEA719491610A45`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/AKS74U/Rifle_AKS74U_base.et`
- local node count: 1
- weapon leaves: 1
- max local depth: 0
- shared local bases: none
- current structure: SINGLE_WEAPON_EXTERNAL_WRAPPER, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/AK74/armst_AKS74U.et` | GUID `BFEA719491610A45` | role `LEAF` | parent `Prefabs/Weapons/Rifles/AKS74U/Rifle_AKS74U_base.et`

### 12. Prefabs/Weapons/Rifles/AK74/armst_AKS74UN.et

- root GUID: `FA0E25CE35EE945F`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/AKS74U/Rifle_AKS74UN_base.et`
- local node count: 1
- weapon leaves: 1
- max local depth: 0
- shared local bases: none
- current structure: SINGLE_WEAPON_EXTERNAL_WRAPPER, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/AK74/armst_AKS74UN.et` | GUID `FA0E25CE35EE945F` | role `LEAF` | parent `Prefabs/Weapons/Rifles/AKS74U/Rifle_AKS74UN_base.et`

### 13. Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et

- root GUID: `6C5E2009CDCD0BD3`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/M14/Rifle_M21.et`
- local node count: 9
- weapon leaves: 7
- max local depth: 2
- shared local bases: `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et`, `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66.et`
- current structure: LOCAL_FAMILY_OVER_EXTERNAL, LOCAL_VARIANT_CHAIN, SHARED_INTERMEDIATE_BASE, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et` | GUID `6C5E2009CDCD0BD3` | role `BASE` | parent `Prefabs/Weapons/Rifles/M14/Rifle_M21.et`
  - depth 1: `Prefabs/Weapons/Rifles/Shotgun/armst_Remington_870.et` | GUID `6DBEF115AA35E404` | role `LEAF` | parent `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et`
  - depth 1: `Prefabs/Weapons/Rifles/Shotgun/armst_izh_27.et` | GUID `57F153EFAD34E1CA` | role `LEAF` | parent `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et`
  - depth 1: `Prefabs/Weapons/Rifles/Shotgun/armst_mp_133.et` | GUID `63FF6FDCA4E7E735` | role `LEAF` | parent `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et`
  - depth 1: `Prefabs/Weapons/Rifles/Shotgun/armst_mp_153.et` | GUID `92DB80A098AABF1C` | role `LEAF` | parent `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et`
  - depth 1: `Prefabs/Weapons/Rifles/Shotgun/armst_spas_12.et` | GUID `221AED80163B7C60` | role `LEAF` | parent `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et`
  - depth 1: `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66.et` | GUID `923B067A74826419` | role `INTERMEDIATE` | parent `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et`
  - depth 2: `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_pantera.et` | GUID `A9B143751CB07F45` | role `LEAF` | parent `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66.et`
  - depth 2: `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_saw.et` | GUID `9C7C3BE87956383A` | role `LEAF` | parent `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66.et`

### 14. Prefabs/Weapons/Rifles/VAL/armst_Rifle_val_base.et

- root GUID: `F25D16BD5F748372`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et`
- local node count: 1
- weapon leaves: 0
- max local depth: 0
- shared local bases: none
- current structure: EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/VAL/armst_Rifle_val_base.et` | GUID `F25D16BD5F748372` | role `BASE` | parent `Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et`

### 15. Prefabs/Weapons/Rifles/VSK94/armst_Rifle_VSK94_base.et

- root GUID: `6005623D3AA5F5C2`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et`
- local node count: 1
- weapon leaves: 0
- max local depth: 0
- shared local bases: none
- current structure: EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/VSK94/armst_Rifle_VSK94_base.et` | GUID `6005623D3AA5F5C2` | role `BASE` | parent `Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et`

### 16. Prefabs/Weapons/Rifles/VSS/armst_Rifle_vss_base.et

- root GUID: `902A79E4B2A66E63`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et`
- local node count: 1
- weapon leaves: 0
- max local depth: 0
- shared local bases: none
- current structure: EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/VSS/armst_Rifle_vss_base.et` | GUID `902A79E4B2A66E63` | role `BASE` | parent `Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et`

### 17. Prefabs/Weapons/Rifles/armst_AEK971_test_v11.et

- root GUID: `AC198EAC9BDD9841`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et`
- local node count: 1
- weapon leaves: 1
- max local depth: 0
- shared local bases: none
- current structure: SINGLE_WEAPON_EXTERNAL_WRAPPER, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/armst_AEK971_test_v11.et` | GUID `AC198EAC9BDD9841` | role `LEAF` | parent `Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et`

### 18. Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et

- root GUID: `3E413771E1834D2F`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et`
- local node count: 5
- weapon leaves: 4
- max local depth: 1
- shared local bases: `Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et`
- current structure: SHARED_INTERMEDIATE_BASE, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et` | GUID `3E413771E1834D2F` | role `INTERMEDIATE` | parent `Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et`
  - depth 1: `Prefabs/Weapons/Rifles/armst_Rifle_HKG33.et` | GUID `035CFC7DD44455D0` | role `LEAF` | parent `Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et`
  - depth 1: `Prefabs/Weapons/Rifles/armst_Rifle_L85.et` | GUID `45D3FCA77AF1709B` | role `LEAF` | parent `Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et`
  - depth 1: `Prefabs/Weapons/Rifles/armst_Rifle_Sig550.et` | GUID `CA3BEBAADDFAF1DE` | role `LEAF` | parent `Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et`
  - depth 1: `Prefabs/Weapons/Rifles/armst_SLR.et` | GUID `C11ED52EAAF856A8` | role `LEAF` | parent `Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et`

### 19. Prefabs/Weapons/Rifles/armst_Rifle_M16A2_carbine.et

- root GUID: `F97A4AC994231900`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/M16/Rifle_M16A2_carbine_base.et`
- local node count: 1
- weapon leaves: 1
- max local depth: 0
- shared local bases: none
- current structure: SINGLE_WEAPON_EXTERNAL_WRAPPER, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/armst_Rifle_M16A2_carbine.et` | GUID `F97A4AC994231900` | role `LEAF` | parent `Prefabs/Weapons/Rifles/M16/Rifle_M16A2_carbine_base.et`

### 20. Prefabs/Weapons/Rifles/armst_SVD.et

- root GUID: `3EB02CDAD5F23C82`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/SVD/Rifle_SVD_base.et`
- local node count: 1
- weapon leaves: 1
- max local depth: 0
- shared local bases: none
- current structure: SINGLE_WEAPON_EXTERNAL_WRAPPER, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/armst_SVD.et` | GUID `3EB02CDAD5F23C82` | role `LEAF` | parent `Prefabs/Weapons/Rifles/SVD/Rifle_SVD_base.et`

### 21. Prefabs/Weapons/Rifles/armst_VZ58P.et

- root GUID: `9C948630078D154D`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/VZ58/Rifle_VZ58_base.et`
- local node count: 1
- weapon leaves: 1
- max local depth: 0
- shared local bases: none
- current structure: SINGLE_WEAPON_EXTERNAL_WRAPPER, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/armst_VZ58P.et` | GUID `9C948630078D154D` | role `LEAF` | parent `Prefabs/Weapons/Rifles/VZ58/Rifle_VZ58_base.et`

### 22. Prefabs/Weapons/Rifles/armst_VZ58V.et

- root GUID: `443CEFF17E040B11`
- root parent status: `EXTERNAL_UNAVAILABLE`
- external boundary: `Prefabs/Weapons/Rifles/VZ58/Rifle_VZ58_base.et`
- local node count: 1
- weapon leaves: 1
- max local depth: 0
- shared local bases: none
- current structure: SINGLE_WEAPON_EXTERNAL_WRAPPER, EXTERNAL_DEPENDENCY_REVIEW
- current chain:
  - depth 0: `Prefabs/Weapons/Rifles/armst_VZ58V.et` | GUID `443CEFF17E040B11` | role `LEAF` | parent `Prefabs/Weapons/Rifles/VZ58/Rifle_VZ58_base.et`

## Core Architecture

Core family root: `Prefabs/Weapons/Core/Weapon_Base.et`.
Direct child of Weapon_Base: `Prefabs/Weapons/Core/Rifle_Base.et`.
Rifle_Base direct children: `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et, Prefabs/Weapons/Rifles/Groza/armst_Groza_base.et, Prefabs/Weapons/Rifles/armst_Rifle_hk_g36.et`.
All descendants and leaves are listed in the family detail above.

- BASE `Prefabs/Weapons/Core/Weapon_Base.et` | GUID `E1F14DB52DBFBC57` | direct children: Prefabs/Weapons/Core/Rifle_Base.et | total descendants: 9 | leaf descendants: 5
- BASE `Prefabs/Weapons/Core/Rifle_Base.et` | GUID `911D6C8DC7BA2D63` | direct children: Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et, Prefabs/Weapons/Rifles/Groza/armst_Groza_base.et, Prefabs/Weapons/Rifles/armst_Rifle_hk_g36.et | total descendants: 8 | leaf descendants: 5
- BASE `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et` | GUID `140E94F473B60FE3` | direct children: Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM.et, Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKMS.et, Prefabs/Weapons/Rifles/AKM/armst_Rifle_SOC94.et, Prefabs/Weapons/Rifles/AKM/armst_Rifle_VPO136.et | total descendants: 5 | leaf descendants: 4

## Shared Base Map

### `Prefabs/Weapons/Core/Rifle_Base.et`
- GUID: `911D6C8DC7BA2D63`
- direct children: Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et, Prefabs/Weapons/Rifles/Groza/armst_Groza_base.et, Prefabs/Weapons/Rifles/armst_Rifle_hk_g36.et
- total descendants: 8
- weapon leaf descendants: 5
- core connected: True
- external boundary above: none

### `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et`
- GUID: `6C5E2009CDCD0BD3`
- direct children: Prefabs/Weapons/Rifles/Shotgun/armst_Remington_870.et, Prefabs/Weapons/Rifles/Shotgun/armst_izh_27.et, Prefabs/Weapons/Rifles/Shotgun/armst_mp_133.et, Prefabs/Weapons/Rifles/Shotgun/armst_mp_153.et, Prefabs/Weapons/Rifles/Shotgun/armst_spas_12.et, Prefabs/Weapons/Rifles/Shotgun/armst_toz_66.et
- total descendants: 8
- weapon leaf descendants: 7
- core connected: False
- external boundary above: Prefabs/Weapons/Rifles/M14/Rifle_M21.et

### `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et`
- GUID: `140E94F473B60FE3`
- direct children: Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM.et, Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKMS.et, Prefabs/Weapons/Rifles/AKM/armst_Rifle_SOC94.et, Prefabs/Weapons/Rifles/AKM/armst_Rifle_VPO136.et
- total descendants: 5
- weapon leaf descendants: 4
- core connected: True
- external boundary above: none

### `Prefabs/Weapons/Handguns/armst_PM.et`
- GUID: `C0F7DD85A86B2900`
- direct children: Prefabs/Weapons/Handguns/armst_APB.et, Prefabs/Weapons/Handguns/armst_PP91.et, Prefabs/Weapons/Handguns/armst_TT.et
- total descendants: 4
- weapon leaf descendants: 3
- core connected: False
- external boundary above: Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et

### `Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et`
- GUID: `3E413771E1834D2F`
- direct children: Prefabs/Weapons/Rifles/armst_Rifle_HKG33.et, Prefabs/Weapons/Rifles/armst_Rifle_L85.et, Prefabs/Weapons/Rifles/armst_Rifle_Sig550.et, Prefabs/Weapons/Rifles/armst_SLR.et
- total descendants: 4
- weapon leaf descendants: 4
- core connected: False
- external boundary above: Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et

### `Prefabs/Weapons/Rifles/AK74/armst_AK74N.et`
- GUID: `96DFD2E7E63B3386`
- direct children: Prefabs/Weapons/Rifles/AK74/armst_AK74M.et, Prefabs/Weapons/Rifles/AK74/armst_AKS.et
- total descendants: 3
- weapon leaf descendants: 2
- core connected: False
- external boundary above: Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et

### `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66.et`
- GUID: `923B067A74826419`
- direct children: Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_pantera.et, Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_saw.et
- total descendants: 2
- weapon leaf descendants: 2
- core connected: False
- external boundary above: none

## Non-Core Architecture

External-boundary families by topology:

### A. external root with only one local weapon

- `Prefabs/Weapons/Handguns/armst_M9.et` (nodes 1, leaves 1, depth 0)
- `Prefabs/Weapons/MachineGuns/armst_PKM.et` (nodes 1, leaves 1, depth 0)
- `Prefabs/Weapons/MachineGuns/armst_RPK74.et` (nodes 1, leaves 1, depth 0)
- `Prefabs/Weapons/Rifles/AK74/armst_AKS74U.et` (nodes 1, leaves 1, depth 0)
- `Prefabs/Weapons/Rifles/AK74/armst_AKS74UN.et` (nodes 1, leaves 1, depth 0)
- `Prefabs/Weapons/Rifles/armst_AEK971_test_v11.et` (nodes 1, leaves 1, depth 0)
- `Prefabs/Weapons/Rifles/armst_Rifle_M16A2_carbine.et` (nodes 1, leaves 1, depth 0)
- `Prefabs/Weapons/Rifles/armst_SVD.et` (nodes 1, leaves 1, depth 0)
- `Prefabs/Weapons/Rifles/armst_VZ58P.et` (nodes 1, leaves 1, depth 0)
- `Prefabs/Weapons/Rifles/armst_VZ58V.et` (nodes 1, leaves 1, depth 0)

### B. external root with multiple local descendants

- `Prefabs/Weapons/Handguns/armst_PM.et` (nodes 5, leaves 3, depth 2)
- `Prefabs/Weapons/Rifles/AK74/armst_AK74.et` (nodes 2, leaves 1, depth 1)
- `Prefabs/Weapons/Rifles/AK74/armst_AK74N.et` (nodes 4, leaves 2, depth 2)
- `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et` (nodes 9, leaves 7, depth 2)
- `Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et` (nodes 5, leaves 4, depth 1)

### C. external root feeding a multi-level local hierarchy

- `Prefabs/Weapons/Handguns/armst_PM.et` (nodes 5, leaves 3, depth 2)
- `Prefabs/Weapons/Rifles/AK74/armst_AK74N.et` (nodes 4, leaves 2, depth 2)
- `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et` (nodes 9, leaves 7, depth 2)

## Potential Normalization Sets

**SET 1 — ALREADY STRUCTURED**

- Core hierarchy: `Prefabs/Weapons/Core/Weapon_Base.et`.
- Local multi-level families with factual local inheritance are documented above.

**SET 2 — REVIEWABLE**

- Core hierarchy for future project-base review.
- Families with shared local bases or depth >= 2: topology gives a concrete review reason only.

**SET 3 — LEAVE UNTIL THERE IS A FUNCTIONAL REASON**

- Single-node external-boundary wrappers and isolated external branches; topology alone provides no rewrite requirement.

**Architectural interpretation**

- These sets are review categories, not rankings or migration instructions.
- Current facts and future review relevance are kept separate.

## Validation

- Family count: 22
- Nodes accounted: 51
- Weapon leaves accounted: 32
- Every graph node appears in exactly one family.
- Magazine_Base.et is absent.
- No live resources changed.
