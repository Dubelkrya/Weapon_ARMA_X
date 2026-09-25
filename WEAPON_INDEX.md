# Weapon index

> [!NOTE]
> **Status: GENERATED SNAPSHOT + VALIDATION NAVIGATION.** Catalog rows are derived from `catalog/weapons/*.json`. Workbench control points are listed separately. Live addon / Workbench evidence and `reports/KNOWLEDGE_STATUS.md` remain authoritative.

This page is the human-readable entry point into the ARMST Arma Reforger weapon catalog. It does not invent missing values: unresolved or absent fields stay unresolved.

Current catalog entries: **63** (`41` leaf entries, `22` base/template entries).

## Catalog overview

### By weapon type

| Type | Entries |
|---|---:|
| Shotguns | 9 |
| Handguns | 11 |
| Machine guns | 2 |
| Other / unresolved | 41 |

### By explicit caliber evidence

| Caliber | Entries |
|---|---:|
| 12 ga | 10 |
| 5.56×45 | 4 |
| 7.62×39 | 6 |
| 7.63×25 | 2 |
| 9×18 | 8 |
| 9×39 | 10 |
| Unresolved in current catalog entry | 23 |

## Workbench-validated control points

These controls are kept separate from the generated catalog so validation evidence is not confused with scanner coverage.

| Control | Status | Catalog coverage | Sample | Note |
|---|---|---|---|---|
| AEK-971 prototype | **Workbench validated** | Not present in current generated catalog | [`armst_AEK971_test_v12_NAME_DESCRIPTION.et`](reports/samples/armst_AEK971_test_v12_NAME_DESCRIPTION.et) | Current weapon control point in reports/KNOWLEDGE_STATUS.md |

## Family comparison pages

- [AK / RPK family](reports/families/AK_FAMILY.md)
- [9×39 family](reports/families/CALIBER_9X39.md)
- [Shotguns](reports/families/SHOTGUNS.md)

## Balance analysis

- [9×39 weapon / magazine / projectile balance](reports/balance/CALIBER_9X39_BALANCE.md)

## Catalog by weapon type and caliber

### Shotguns (9)

#### 12 ga (9)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_shotgun_base`](catalog/weapons/armst_shotgun_base.json) | base | `armst_shotgun_base` | `armst_shotgun_base.et` | `armst_12ga_Buckshot.et` | — | Catalog snapshot | 0 |
| [`armst_shotgun_izh_27`](catalog/weapons/armst_shotgun_izh_27.json) | leaf | `armst_Shotgun_izh_27` | `armst_Shotgun_izh_27.et` | `armst_12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_shotgun_mp_133`](catalog/weapons/armst_shotgun_mp_133.json) | leaf | `armst_Shotgun_mp_133` | `armst_Shotgun_mp_133.et` | `armst_12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_shotgun_mp_153`](catalog/weapons/armst_shotgun_mp_153.json) | leaf | `armst_Shotgun_mp_153` | `armst_Shotgun_mp_153.et` | `armst_12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_shotgun_remington_870`](catalog/weapons/armst_shotgun_remington_870.json) | leaf | `armst_Shotgun_Remington_870` | `armst_Shotgun_Remington_870.et` | `armst_12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_shotgun_spas_12`](catalog/weapons/armst_shotgun_spas_12.json) | leaf | `armst_Shotgun_spas_12` | `armst_Shotgun_spas_12.et` | `armst_12ga_Buckshot.et` | unresolved, Auto | Catalog snapshot | 0 |
| [`armst_shotgun_toz_66`](catalog/weapons/armst_shotgun_toz_66.json) | base | `armst_Shotgun_toz_66` | `armst_Shotgun_toz_66.et` | `armst_12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_shotgun_toz_66_pantera`](catalog/weapons/armst_shotgun_toz_66_pantera.json) | leaf | `armst_Shotgun_toz_66_pantera` | `armst_Shotgun_toz_66_pantera.et` | `armst_12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |
| [`armst_shotgun_toz_66_saw`](catalog/weapons/armst_shotgun_toz_66_saw.json) | leaf | `armst_Shotgun_toz_66_saw` | `armst_Shotgun_toz_66_saw.et` | `armst_12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |

### Handguns (11)

#### 7.63×25 (2)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_pistol_tt`](catalog/weapons/armst_pistol_tt.json) | leaf | `armst_pistol_TT` | `armst_pistol_TT.et` | `armst_Magazine_763x25_TT_8rnd_Ball.et` | — | Catalog snapshot | 0 |
| [`armst_pistol_tt_base`](catalog/weapons/armst_pistol_tt_base.json) | base | `armst_pistol_TT_base` | `armst_pistol_TT_base.et` | `armst_Magazine_763x25_TT_8rnd_Ball.et` | — | Catalog snapshot | 0 |

#### 9×18 (8)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_handgun_knife_base`](catalog/weapons/armst_handgun_knife_base.json) | leaf | `armst_Handgun_Knife_base` | `armst_Handgun_Knife_base.et` | `armst_Magazine_9x18_PM_8rnd_Ball.et` | — | Catalog snapshot | 0 |
| [`armst_pistol_apb`](catalog/weapons/armst_pistol_apb.json) | leaf | `armst_pistol_APB` | `armst_pistol_APB.et` | `armst_Magazine_9x18_APB_20rnd_Ball.et` | Auto | Catalog snapshot | 0 |
| [`armst_pistol_apb_base`](catalog/weapons/armst_pistol_apb_base.json) | base | `armst_pistol_APB_base` | `armst_pistol_APB_base.et` | `armst_Magazine_9x18_APB_20rnd_Ball.et` | Auto | Catalog snapshot | 0 |
| [`armst_pistol_pm`](catalog/weapons/armst_pistol_pm.json) | leaf | `armst_pistol_PM` | `armst_pistol_PM.et` | `armst_Magazine_9x18_PM_8rnd_Ball_PP.et` | — | Catalog snapshot | 0 |
| [`armst_pistol_pp91`](catalog/weapons/armst_pistol_pp91.json) | leaf | `armst_pistol_PP91` | `armst_pistol_PP91.et` | `armst_Magazine_9x18_PP91_30rnd_Ball.et` | unresolved, Auto | Catalog snapshot | 0 |
| [`armst_pistol_pp91_base`](catalog/weapons/armst_pistol_pp91_base.json) | base | `armst_pistol_PP91_base` | `armst_pistol_PP91_base.et` | `armst_Magazine_9x18_PP91_30rnd_Ball.et` | unresolved, Auto | Catalog snapshot | 0 |
| [`armst_pistol_sr_2`](catalog/weapons/armst_pistol_sr_2.json) | leaf | `armst_pistol_SR_2` | `armst_pistol_SR_2.et` | `armst_Magazine_9x18_SR2_30rnd_Ball.et` | unresolved, Auto | Catalog snapshot | 0 |
| [`armst_pistol_sr_2_base`](catalog/weapons/armst_pistol_sr_2_base.json) | base | `armst_pistol_SR_2_base` | `armst_pistol_SR_2_base.et` | `armst_Magazine_9x18_SR2_30rnd_Ball.et` | unresolved, Auto | Catalog snapshot | 0 |

#### Caliber unresolved (1)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_pistol_m9`](catalog/weapons/armst_pistol_m9.json) | leaf | `armst_pistol_M9` | `armst_pistol_M9.et` | `—` | — | Catalog snapshot | 0 |

### Machine guns (2)

#### Caliber unresolved (2)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_mgun_pkm`](catalog/weapons/armst_mgun_pkm.json) | leaf | `armst_mgun_PKM` | `armst_mgun_PKM.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_mgun_rpk74`](catalog/weapons/armst_mgun_rpk74.json) | leaf | `armst_mgun_RPK74` | `armst_mgun_RPK74.et` | `—` | — | Catalog snapshot | 0 |

### Other / unresolved (41)

#### 12 ga (1)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`1`](catalog/weapons/1.json) | leaf | `1` | `1.et` | `armst_12ga_Buckshot.et` | unresolved | Catalog snapshot | 0 |

#### 5.56×45 (4)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_rifle_hkg36`](catalog/weapons/armst_rifle_hkg36.json) | leaf | `armst_Rifle_HKG36` | `armst_Rifle_HKG36.et` | `armst_Magazine_556x45_HKG36.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_hkg36_base`](catalog/weapons/armst_rifle_hkg36_base.json) | base | `armst_Rifle_HKG36_base` | `armst_Rifle_HKG36_base.et` | `armst_Magazine_556x45_HKG36.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_sig550`](catalog/weapons/armst_rifle_sig550.json) | leaf | `armst_Rifle_Sig550` | `armst_Rifle_Sig550.et` | `armst_Magazine_556x45_SIG_550.et` | — | Catalog snapshot | 0 |
| [`armst_rifle_sig550_base`](catalog/weapons/armst_rifle_sig550_base.json) | base | `armst_Rifle_Sig550_base` | `armst_Rifle_Sig550_base.et` | `armst_Magazine_556x45_SIG_550.et` | — | Catalog snapshot | 0 |

#### 7.62×39 (6)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_rifle_akm`](catalog/weapons/armst_rifle_akm.json) | base | `AKM` | `armst_Rifle_AKM.et` | `armst_Magazine_762x39_AKM_30rnd_Ball.et` | unresolved | Catalog snapshot | 0 |
| [`armst_rifle_akm_base`](catalog/weapons/armst_rifle_akm_base.json) | base | `armst_Rifle_AKM_base` | `armst_Rifle_AKM_base.et` | `Magazine_762x39_Vz58_30rnd_Last_5Tracer.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_akm_full`](catalog/weapons/armst_rifle_akm_full.json) | leaf | `AKM` | `armst_Rifle_AKM_full.et` | `armst_Magazine_762x39_AKM_30rnd_Ball.et` | unresolved | Catalog snapshot | 0 |
| [`armst_rifle_akms`](catalog/weapons/armst_rifle_akms.json) | leaf | `AKM` | `armst_Rifle_AKMS.et` | `Magazine_762x39_Vz58_30rnd_Last_5Tracer.et` | unresolved | Catalog snapshot | 0 |
| [`armst_rifle_soc94`](catalog/weapons/armst_rifle_soc94.json) | leaf | `SOK-94` | `armst_Rifle_SOC94.et` | `armst_Magazine_762x39_AKM_10rnd_Ball.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_vpo136`](catalog/weapons/armst_rifle_vpo136.json) | leaf | `VPO-136` | `armst_Rifle_VPO136.et` | `armst_Magazine_762x39_AKM_10rnd_Ball.et` | unresolved, unresolved | Catalog snapshot | 0 |

#### 9×39 (10)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_rifle_9a91`](catalog/weapons/armst_rifle_9a91.json) | leaf | `armst_Rifle_9a91` | `armst_Rifle_9a91.et` | `armst_Magazine_9x39_20rnd_9a91_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_9a91_base`](catalog/weapons/armst_rifle_9a91_base.json) | base | `armst_Rifle_9a91_base` | `armst_Rifle_9a91_base.et` | `armst_Magazine_9x39_20rnd_9a91_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_groza`](catalog/weapons/armst_rifle_groza.json) | leaf | `armst_Rifle_Groza` | `armst_Rifle_Groza.et` | `armst_Magazine_9x39_Groza_20rnd_SP5.et` | Single, Auto | Catalog snapshot | 0 |
| [`armst_rifle_groza_base`](catalog/weapons/armst_rifle_groza_base.json) | base | `armst_Rifle_Groza_base` | `armst_Rifle_Groza_base.et` | `armst_Magazine_9x39_Groza_20rnd_SP5.et` | Single, Auto | Catalog snapshot | 0 |
| [`armst_rifle_val`](catalog/weapons/armst_rifle_val.json) | leaf | `armst_Rifle_val` | `armst_Rifle_val.et` | `armst_Magazine_9x39_30rnd_val_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_val_base`](catalog/weapons/armst_rifle_val_base.json) | base | `armst_Rifle_val_base` | `armst_Rifle_val_base.et` | `armst_Magazine_9x39_30rnd_val_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_vsk94`](catalog/weapons/armst_rifle_vsk94.json) | leaf | `armst_Rifle_VSK94` | `armst_Rifle_VSK94.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_vsk94_base`](catalog/weapons/armst_rifle_vsk94_base.json) | base | `armst_Rifle_VSK94_base` | `armst_Rifle_VSK94_base.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_vss`](catalog/weapons/armst_rifle_vss.json) | leaf | `armst_Rifle_vss` | `armst_Rifle_vss.et` | `armst_Magazine_9x39_20rnd_vss_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_vss_base`](catalog/weapons/armst_rifle_vss_base.json) | base | `armst_Rifle_vss_base` | `armst_Rifle_vss_base.et` | `armst_Magazine_9x39_20rnd_vss_SP5.et` | unresolved, unresolved | Catalog snapshot | 0 |

#### Caliber unresolved (20)

| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |
|---|---|---|---|---|---|---|---:|
| [`armst_rifle_aek971`](catalog/weapons/armst_rifle_aek971.json) | leaf | `armst_Rifle_AEK971` | `armst_Rifle_AEK971.et` | `—` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_aek971_base`](catalog/weapons/armst_rifle_aek971_base.json) | base | `armst_Rifle_AEK971_base` | `armst_Rifle_AEK971_base.et` | `—` | unresolved, unresolved | Catalog snapshot | 0 |
| [`armst_rifle_ak105`](catalog/weapons/armst_rifle_ak105.json) | leaf | `armst_Rifle_AK105` | `armst_Rifle_AK105.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_ak74`](catalog/weapons/armst_rifle_ak74.json) | leaf | `armst_Rifle_AK74` | `armst_Rifle_AK74.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_ak74m`](catalog/weapons/armst_rifle_ak74m.json) | base | `armst_Rifle_AK74M` | `armst_Rifle_AK74M.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_ak74m_full`](catalog/weapons/armst_rifle_ak74m_full.json) | leaf | `armst_Rifle_AK74M_full` | `armst_Rifle_AK74M_full.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_ak74n`](catalog/weapons/armst_rifle_ak74n.json) | base | `armst_Rifle_AK74N` | `armst_Rifle_AK74N.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_aks`](catalog/weapons/armst_rifle_aks.json) | leaf | `AK-74M` | `armst_Rifle_AKS.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_aks74u`](catalog/weapons/armst_rifle_aks74u.json) | leaf | `armst_Rifle_AKS74U` | `armst_Rifle_AKS74U.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_hkg33`](catalog/weapons/armst_rifle_hkg33.json) | leaf | `armst_Rifle_HKG33` | `armst_Rifle_HKG33.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_hkg33_base`](catalog/weapons/armst_rifle_hkg33_base.json) | base | `armst_Rifle_HKG33_base` | `armst_Rifle_HKG33_base.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_l85`](catalog/weapons/armst_rifle_l85.json) | leaf | `armst_Rifle_L85` | `armst_Rifle_L85.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_l85_base`](catalog/weapons/armst_rifle_l85_base.json) | base | `armst_Rifle_L85_base` | `armst_Rifle_L85_base.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_m16a2`](catalog/weapons/armst_rifle_m16a2.json) | base | `armst_Rifle_M16A2` | `armst_Rifle_M16A2.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_m4_carbine`](catalog/weapons/armst_rifle_m4_carbine.json) | leaf | `armst_Rifle_M4_carbine` | `armst_Rifle_M4_carbine.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_rifle_svd`](catalog/weapons/armst_rifle_svd.json) | leaf | `armst_Rifle_SVD` | `armst_Rifle_SVD.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_slr`](catalog/weapons/armst_slr.json) | leaf | `armst_SLR` | `armst_SLR.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_slr_base`](catalog/weapons/armst_slr_base.json) | base | `armst_SLR_base` | `armst_SLR_base.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_vz58p_base`](catalog/weapons/armst_vz58p_base.json) | leaf | `armst_VZ58P_base` | `armst_VZ58P_base.et` | `—` | — | Catalog snapshot | 0 |
| [`armst_vz58v_base`](catalog/weapons/armst_vz58v_base.json) | leaf | `armst_VZ58V_base` | `armst_VZ58V_base.et` | `—` | — | Catalog snapshot | 0 |

## Reading the index

- `Type` grouping comes only from the prefab resource path (`Rifles`, `Shotgun`, `Handguns`, `MachineGuns`); unknown paths remain unresolved.
- Caliber is shown only when an explicit magazine / AmmoConfig / loaded-projectile path contains a recognized caliber marker. It is never inferred from a weapon name.
- `Source name` is preserved exactly from the generated catalog; localization keys such as `#AR-...` are not guessed or replaced.
- `unresolved` means the current catalog entry does not expose a readable fire-mode label at this level.
- Blank magazine/fire-mode data does not mean the weapon has none; the value may be inherited outside the current local snapshot.
- `Catalog snapshot + authoring sample` means a matching file exists in `reports/samples/`; it does **not** automatically mean Workbench validation.
- A warning count greater than zero means the catalog JSON contains source/provenance warnings that should be read before authoring.

Regenerate this file with `python agent/scripts/build_weapon_index.py` after refreshing the weapon catalog.
