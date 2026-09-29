# Аудит префабов аддона: наследование и правила (read-only)

- Префабов разобрано: **144**
- Всего в аддоне `.et` (вкл. `agent/`): **217**

## Сводка

| Проверка | Найдено |
|---|---|
| `.et` без `.meta` | 0 |
| дубли ID компонентов в файле | 0 |
| один класс компонента 2+ раз | 0 |
| новый ID вместо override унаследованного класса | 0 |
| компоненты с `Enabled 0` | 89 |
| родитель не разрешается (ни аддон, ни ваниль) | 0 |
| `meta.Name` путь != фактический | 0 |
| висячие ссылки `Prefab "{GUID}*.et"` | 0 |

## 1. Префабы без .meta

_нет_

## 2. Дубли ID компонентов

_нет_

## 3. Один класс компонента 2+ раза

_нет_

## 4. Новый ID вместо override (класс уже приходит по наследованию)

_нет_

## 5. Родитель не разрешается

_нет_

## 6. meta.Name путь != фактический

_нет_

## 7. Висячие ссылки Prefab

_нет_

## 8. Enabled 0 (для ручного разбора)

- `Prefabs/Weapons/Ammo/12g/armst_Ammo_12ga.et` стр.25 — `Enabled 0`
- `Prefabs/Weapons/Ammo/12g/armst_Ammo_12ga_shell_test.et` стр.5 — `Enabled 0`
- `Prefabs/Weapons/Ammo/12g/armst_Ammo_12ga_shell_test.et` стр.31 — `Enabled 0`
- `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et` стр.44 — `Enabled 0`
- `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et` стр.47 — `Enabled 0`
- `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et` стр.74 — `Enabled 0`
- `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et` стр.77 — `Enabled 0`
- `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et` стр.86 — `Enabled 0`
- `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et` стр.94 — `Enabled 0`
- `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et` стр.114 — `Enabled 0`
- `Prefabs/Weapons/Magazines/12ga/armst_12ga_Shell.et` стр.50 — `Enabled 0`
- `Prefabs/Weapons/Magazines/12ga/armst_12ga_Shell_test.et` стр.46 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/5x45/AK74/armst_Magazine_545x39_AK_30rnd_Ball.et` стр.17 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/762x54/SVD/armst_Box_762x54_PK_250rnd_Ball.et` стр.19 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/762x54/SVD/armst_Magazine_762x54_SVD_10rnd_7BZ3API.et` стр.18 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/763x25/TT/armst_Magazine_763x25_TT_8rnd_Ball.et` стр.27 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/armst_Magazine_762x39_AKM_10rnd_Ball.et` стр.28 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/armst_Magazine_762x39_AKM_10rnd_Ball_BP.et` стр.28 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/armst_Magazine_762x39_AKM_30rnd_Ball.et` стр.26 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/armst_Magazine_762x39_AKM_30rnd_Ball_BP.et` стр.26 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_APB_20rnd_Ball.et` стр.31 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_APB_20rnd_Ball_BP.et` стр.31 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball.et` стр.19 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball_BP.et` стр.23 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball_PP.et` стр.23 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP5.et` стр.48 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP6.et` стр.48 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x39/Groza/armst_Magazine_9x39_Groza_20rnd_SP5.et` стр.28 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x39/Groza/armst_Magazine_9x39_Groza_20rnd_SP6.et` стр.28 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_20rnd_vss_SP5.et` стр.49 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_20rnd_vss_SP6.et` стр.49 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_30rnd_val_SP5.et` стр.47 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_30rnd_val_SP6.et` стр.47 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/5x56/HKG36/armst_Magazine_556x45_HKG36.et` стр.29 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/5x56/HKG36/armst_Magazine_556x45_HKG36_BP.et` стр.29 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/5x56/SIG550/armst_Magazine_556x45_SIG_550.et` стр.27 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/5x56/SIG550/armst_Magazine_556x45_SIG_550_BP.et` стр.27 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/armst_Magazine_556x45_STANAG_30rnd_M193_Ball.et` стр.25 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/armst_Magazine_556x45_STANAG_30rnd_M193_Ball_BP.et` стр.25 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/762x51/HK3/armst_Magazine_762x51_HK3_20_M80_Ball.et` стр.31 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/762x51/HK3/armst_Magazine_762x51_HK3_20_M80_Ball_BP.et` стр.31 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/762x51/L1A1/armst_Magazine_762x51_L1A1_20_M80_Ball.et` стр.31 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/762x51/L1A1/armst_Magazine_762x51_L1A1_20_M80_Ball_BP.et` стр.31 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/9x19/M9/armst_Magazine_9x19_M9_15rnd_Ball.et` стр.23 — `Enabled 0`
- `Prefabs/Weapons/Magazines/Western/9x19/M9/armst_Magazine_9x19_M9_15rnd_Ball_BP.et` стр.23 — `Enabled 0`
- `Prefabs/Weapons/Russian/Handguns/PP_19/armst_PP91_base.et` стр.14 — `Enabled 0`
- `Prefabs/Weapons/Russian/Handguns/Pm/armst_PM_base.et` стр.14 — `Enabled 0`
- `Prefabs/Weapons/Russian/Handguns/Sr_2/armst_SR_2_base.et` стр.14 — `Enabled 0`
- `Prefabs/Weapons/Russian/Handguns/TT/armst_TT_base.et` стр.10 — `Enabled 0`
- `Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB_base.et` стр.14 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/9a91/armst_Rifle_9a91_base.et` стр.32 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK105.et` стр.16 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74M.et` стр.23 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74N.et` стр.7 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74_base.et` стр.5 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74_base.et` стр.20 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AKS.et` стр.13 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AKS.et` стр.42 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AKS74U.et` стр.19 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM.et` стр.5 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM.et` стр.30 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKMS.et` стр.5 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_VPO136.et` стр.5 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_VPO136.et` стр.26 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/Aek971/armst_Rifle_AEK971_base.et` стр.8 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/Aek971/armst_Rifle_AEK971_base.et` стр.29 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et` стр.8 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et` стр.27 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et` стр.46 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et` стр.64 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/SVD/armst_Rifle_SVD_base.et` стр.5 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/VAL/armst_Rifle_val_base.et` стр.52 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/VSK94/armst_Rifle_VSK94_base.et` стр.32 — `Enabled 0`
- `Prefabs/Weapons/Russian/Rifle/VSS/armst_Rifle_vss_base.et` стр.60 — `Enabled 0`
- `Prefabs/Weapons/Russian/Shotgun/armst_izh_27.et` стр.33 — `Enabled 0`
- `Prefabs/Weapons/Russian/Shotgun/armst_toz_66.et` стр.36 — `Enabled 0`
- `Prefabs/Weapons/Tripods/armst_Tripod_6T5_PKM.et` стр.5 — `Enabled 0`
- `Prefabs/Weapons/Western/Handguns/armst_M9_base.et` стр.7 — `Enabled 0`
- `Prefabs/Weapons/Western/Rifle/HKG33/armst_Rifle_HKG33_base.et` стр.26 — `Enabled 0`
- `Prefabs/Weapons/Western/Rifle/HKG33/armst_Rifle_HKG33_base.et` стр.29 — `Enabled 0`
- `Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_HKG36_base.et` стр.78 — `Enabled 0`
- `Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_HKG36_base.et` стр.102 — `Enabled 0`
- `Prefabs/Weapons/Western/Rifle/L85/armst_Rifle_L85_base.et` стр.38 — `Enabled 0`
- `Prefabs/Weapons/Western/Rifle/L85/armst_Rifle_L85_base.et` стр.41 — `Enabled 0`
- `Prefabs/Weapons/Western/Rifle/SLR/armst_SLR_base.et` стр.26 — `Enabled 0`
- `Prefabs/Weapons/Western/Rifle/SLR/armst_SLR_base.et` стр.29 — `Enabled 0`
- `Prefabs/Weapons/Western/Rifle/Sig550/armst_Rifle_Sig550_base.et` стр.26 — `Enabled 0`
- `Prefabs/Weapons/Western/Rifle/Sig550/armst_Rifle_Sig550_base.et` стр.29 — `Enabled 0`
- `Prefabs/Weapons/Western/Shotgun/armst_shotgun_base.et` стр.32 — `Enabled 0`
