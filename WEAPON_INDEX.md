# Weapon index

> [!NOTE]
> **Status: GENERATED SNAPSHOT + VALIDATION NAVIGATION.** Catalog rows are derived from `catalog/weapons/*.json`. Workbench control points are listed separately. Live addon / Workbench evidence and `reports/KNOWLEDGE_STATUS.md` remain authoritative.

This page is the human-readable entry point into the ARMST Arma Reforger weapon catalog. It does not invent missing values: unresolved or absent fields stay unresolved.

Current catalog entries: **55** (`39` leaf entries, `16` base/template entries).

## Catalog overview

### By weapon type

| Type | Entries |
|---|---:|
| Rifles | 36 |
| Shotguns | 9 |
| Handguns | 7 |
| Machine guns | 2 |
| Other / unresolved | 1 |

### By explicit caliber evidence

| Caliber | Entries |
|---|---:|
| 12 ga | 10 |
| 5.56×45 | 2 |
| 7.62×39 | 9 |
| 7.62×51 | 2 |
| 7.63×25 | 1 |
| 9×18 | 5 |
| 9×19 | 1 |
| 9×39 | 9 |
| Unresolved in current catalog entry | 16 |

## Workbench-validated control points

These controls are kept separate from the generated catalog so validation evidence is not confused with scanner coverage.

| Control | Status | Catalog coverage | Sample | Note |
|---|---|---|---|---|
| AEK-971 prototype | **Workbench validated** | Not present in current generated catalog | [`armst_AEK971_test_v12_NAME_DESCRIPTION.et`](reports/samples/armst_AEK971_test_v12_NAME_DESCRIPTION.et) | Current weapon control point in reports/KNOWLEDGE_STATUS.md |

## Catalog by weapon type and caliber

### Rifles (36)

#### 5.56×45 (2)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`rifle_hk_g36`](catalog/weapons/rifle_hk_g36.json) | leaf | `Rifle_hk_g36` | `Rifle_hk_g36.et` | `Magazine_556x45_HKG36.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_sig550`](catalog/weapons/rifle_sig550.json) | leaf | `Rifle_Sig550` | `Rifle_Sig550.et` | `Magazine_556x45_SIG_550.et` | — | Catalog snapshot | 0 |

#### 7.62×39 (9)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_groza1`](catalog/weapons/armst_groza1.json) | leaf | `armst_groza1` | `armst_groza1.et` | `Magazine_762x39_AKM_30rnd_Ball.et` | Single, Auto | Catalog snapshot | 0 |
| [`groza_base`](catalog/weapons/groza_base.json) | base | `Groza_base` | `Groza_base.et` | `Magazine_762x39_AKM_30rnd_Ball.et` | Single, Auto | Catalog snapshot | 0 |
| [`oc_groza`](catalog/weapons/oc_groza.json) | leaf | `AS Val` | `Oc_Groza.et` | `Magazine_762x39_Groza_20rnd_Ball.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_akm`](catalog/weapons/rifle_akm.json) | base | `AKM` | `Rifle_AKM.et` | `Magazine_762x39_AKM_30rnd_Ball.et` | unresolved | Catalog snapshot | 0 |
| [`rifle_akm_base`](catalog/weapons/rifle_akm_base.json) | base | `Rifle_AKM_base` | `Rifle_AKM_base.et` | `Magazine_762x39_Vz58_30rnd_Last_5Tracer.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_akm_full`](catalog/weapons/rifle_akm_full.json) | leaf | `AKM` | `Rifle_AKM_full.et` | `Magazine_762x39_AKM_30rnd_Ball.et` | unresolved | Catalog snapshot | 0 |
| [`rifle_akms`](catalog/weapons/rifle_akms.json) | leaf | `AKM` | `Rifle_AKMS.et` | `Magazine_762x39_Vz58_30rnd_Last_5Tracer.et` | unresolved | Catalog snapshot | 0 |
| [`rifle_soc94`](catalog/weapons/rifle_soc94.json) | leaf | `SOK-94` | `Rifle_SOC94.et` | `Magazine_762x39_AKM_10rnd_Ball.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_vpo136`](catalog/weapons/rifle_vpo136.json) | leaf | `VPO-136` | `Rifle_VPO136.et` | `Magazine_762x39_AKM_10rnd_Ball.et` | unresolved, unresolved | Catalog snapshot | 0 |

#### 7.62×51 (2)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`rifle_hkg33`](catalog/weapons/rifle_hkg33.json) | leaf | `Rifle_HKG33` | `Rifle_HKG33.et` | `Magazine_762x51_HK3.et` | — | Catalog snapshot | 0 |
| [`slr`](catalog/weapons/slr.json) | leaf | `SLR` | `SLR.et` | `Magazine_762x51_L1A1_20.et` | — | Catalog snapshot | 0 |

#### 9×39 (9)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`rifle_9a91`](catalog/weapons/rifle_9a91.json) | leaf | `9A91` | `Rifle_9a91.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_9a91_base`](catalog/weapons/rifle_9a91_base.json) | base | `Rifle_9a91_base` | `Rifle_9a91_base.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_9a91_suppressor`](catalog/weapons/rifle_9a91_suppressor.json) | leaf | `Rifle_9a91_suppressor` | `Rifle_9a91_suppressor.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_val`](catalog/weapons/rifle_val.json) | base | `AS Val` | `Rifle_VAL.et` | `Magazine_9x39_30rnd_val_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_val_base`](catalog/weapons/rifle_val_base.json) | base | `Rifle_val_base` | `Rifle_val_base.et` | `Magazine_9x39_30rnd_val_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_vsk94`](catalog/weapons/rifle_vsk94.json) | leaf | `VSK-94` | `Rifle_VSK94.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_vsk94_base`](catalog/weapons/rifle_vsk94_base.json) | base | `Rifle_VSK94_base` | `Rifle_VSK94_base.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_vss`](catalog/weapons/rifle_vss.json) | leaf | `VSS Vintorez` | `Rifle_VSS.et` | `Magazine_9x39_20rnd_vss_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`rifle_vss_base`](catalog/weapons/rifle_vss_base.json) | base | `Rifle_vss_base` | `Rifle_vss_base.et` | `Magazine_9x39_20rnd_vss_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |

#### Caliber unresolved (14)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_ak105`](catalog/weapons/armst_ak105.json) | leaf | `#AR-Weapon_AK74_Name` | `armst_AK105.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_ak74`](catalog/weapons/armst_ak74.json) | base | `#AR-Weapon_AK74_Name` | `armst_AK74.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_ak74m`](catalog/weapons/armst_ak74m.json) | base | `AK-74M` | `armst_AK74M.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_ak74m_full`](catalog/weapons/armst_ak74m_full.json) | leaf | `AK-74M` | `armst_AK74M_full.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_ak74n`](catalog/weapons/armst_ak74n.json) | base | `#AR-Weapon_AK74_Name` | `armst_AK74N.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_aks`](catalog/weapons/armst_aks.json) | leaf | `AK-74M` | `armst_AKS.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_aks74u`](catalog/weapons/armst_aks74u.json) | leaf | `armst_AKS74U` | `armst_AKS74U.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_aks74un`](catalog/weapons/armst_aks74un.json) | leaf | `armst_AKS74UN` | `armst_AKS74UN.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_svd`](catalog/weapons/armst_svd.json) | leaf | `#AR-Weapon_SVD_Name` | `armst_SVD.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_vz58p`](catalog/weapons/armst_vz58p.json) | leaf | `armst_VZ58P` | `armst_VZ58P.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_vz58v`](catalog/weapons/armst_vz58v.json) | leaf | `armst_VZ58V` | `armst_VZ58V.et` | `—` | — | Catalog snapshot | 0 |
| [`rifle_l85`](catalog/weapons/rifle_l85.json) | leaf | `Rifle_L85` | `Rifle_L85.et` | `—` | — | Catalog snapshot | 0 |
| [`rifle_m16a2`](catalog/weapons/rifle_m16a2.json) | base | `Rifle_M16A2` | `Rifle_M16A2.et` | `—` | — | Catalog snapshot | 0 |
| [`rifle_m16a2_carbine`](catalog/weapons/rifle_m16a2_carbine.json) | leaf | `Rifle_M16A2_carbine` | `Rifle_M16A2_carbine.et` | `—` | — | Catalog snapshot | 0 |

### Shotguns (9)

#### 12 ga (9)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_izh_27`](catalog/weapons/armst_izh_27.json) | leaf | `armst_izh_27` | `armst_izh_27.et` | `12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_mp_133`](catalog/weapons/armst_mp_133.json) | leaf | `armst_mp_133` | `armst_mp_133.et` | `12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_mp_153`](catalog/weapons/armst_mp_153.json) | leaf | `armst_mp_153` | `12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_remington_870`](catalog/weapons/armst_remington_870.json) | leaf | `armst_Remington_870` | `armst_Remington_870.et` | `12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_spas_12`](catalog/weapons/armst_spas_12.json) | leaf | `armst_spas_12` | `armst_spas_12.et` | `12ga_Buckshot.et` | unresolved, Auto | Catalog snapshot | 0 |
| [`armst_toz_66`](catalog/weapons/armst_toz_66.json) | base | `armst_toz_66` | `armst_toz_66.et` | `12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_toz_66_pantera`](catalog/weapons/armst_toz_66_pantera.json) | leaf | `armst_toz_66_pantera` | `armst_toz_66_pantera.et` | `12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_toz_66_saw`](catalog/weapons/armst_toz_66_saw.json) | leaf | `armst_toz_66_saw` | `armst_toz_66_saw.et` | `12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`shotgun_base`](catalog/weapons/shotgun_base.json) | base | `shotgun_base` | `shotgun_base.et` | `12ga_Buckshot.et` | — | Catalog snapshot | 0 |

### Handguns (7)

#### 7.63×25 (1)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_tt`](catalog/weapons/armst_tt.json) | leaf | `TT` | `armst_TT.et` | `Magazine_763x25_TT_8rnd_Ball.et` | Single | [Catalog snapshot + authoring sample](reports/samples/armst_TT_authoring_sample_v4.et) | 2 |

#### 9×18 (5)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_apb`](catalog/weapons/armst_apb.json) | leaf | `APB` | `armst_APB.et` | `Magazine_9x18_APB_20rnd_Ball.et` | Auto | Catalog snapshot | 0 |
| [`armst_pm`](catalog/weapons/armst_pm.json) | base | `#AR-Weapon_PM_Name` | `armst_PM.et` | `Magazine_9x18_PM_8rnd_Ball.et` | Single | Catalog snapshot | 1 |
| [`armst_pp91`](catalog/weapons/armst_pp91.json) | base | `PP-91` | `armst_PP91.et` | `Magazine_9x18_PP91_30rnd_Ball.et` | unresolved, Auto | Catalog snapshot | 0 |
| [`armst_sr_2`](catalog/weapons/armst_sr_2.json) | leaf | `PP-91` | `armst_SR_2.et` | `Magazine_9x18_PP91_30rnd_Ball.et` | unresolved, Auto | Catalog snapshot | 0 |
| [`handgun_knife_base`](catalog/weapons/handgun_knife_base.json) | leaf | `Handgun_Knife_base` | `Handgun_Knife_base.et` | `Magazine_9x18_PM_8rnd_Ball.et` | — | Catalog snapshot | 0 |

#### 9×19 (1)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_m9`](catalog/weapons/armst_m9.json) | leaf | `#AR-Weapon_BerettaM9_Name` | `armst_M9.et` | `Magazine_9x19_M9_15rnd_Ball.et` | Single | Catalog snapshot | 1 |

### Machine guns (2)

#### Caliber unresolved (2)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_pkm`](catalog/weapons/armst_pkm.json) | leaf | `armst_PKM` | `armst_PKM.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rpk74`](catalog/weapons/armst_rpk74.json) | leaf | `armst_RPK74` | `armst_RPK74.et` | `—` | — | Catalog snapshot | 0 |

### Other / unresolved (1)

#### 12 ga (1)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`1`](catalog/weapons/1.json) | leaf | `1` | `1.et` | `12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |

## Reading the index

- `Type` grouping comes only from the prefab resource path (`Rifles`, `Shotgun`, `Handguns`, `MachineGuns`); unknown paths remain unresolved.
- Caliber is shown only when an explicit magazine / AmmoConfig / loaded-projectile path contains a recognized caliber marker. It is never inferred from a weapon name.
- `Source name` is preserved exactly from the generated catalog; localization keys such as `#AR-...` are not guessed or replaced.
- `unresolved` means the current catalog entry does not expose a readable fire-mode label at this level.
- Blank magazine/fire-mode data does not mean the weapon has none; the value may be inherited outside the current local snapshot.
- `Catalog snapshot + authoring sample` means a matching file exists in `reports/samples/`; it does **not** automatically mean Workbench validation.
- A warning count greater than zero means the catalog JSON contains source/provenance warnings that should be read before authoring.

Regenerate this file with `python agent/scripts/build_weapon_index.py` after refreshing the weapon catalog.
