# ARMST Naming Audit

Read-only. No files renamed or changed.

## Summary

- total: 124
- compliant: 53
- non_compliant: 71
- non_compliant_magazines: 30
- non_compliant_ammo: 17
- non_compliant_ammo_configs: 4
- non_compliant_other_prefabs: 20
- safe_rename: 62
- review_required: 9

## Non-compliant magazines

- `Prefabs/Weapons/Magazines/12ga/12ga_Buckshot.et` | GUID `B0DFDF7AAA9C5D39` -> `armst_12ga_Buckshot.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/12ga/12ga_Buckshot_base.et` | GUID `9F9380F5E2ECAF59` -> `armst_12ga_Buckshot_base.et` | refs 1 | REVIEW_REQUIRED
- `Prefabs/Weapons/Magazines/12ga/12ga_Shell.et` | GUID `0346C78F29531C70` -> `armst_12ga_Shell.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/12ga/12ga_Shell_test.et` | GUID `5220A773A621C2BB` -> `armst_12ga_Shell_test.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_AK_30rnd_Ball.et` | GUID `BBB50A815A2F916B` -> `armst_Magazine_545x39_AK_30rnd_Ball.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_AK_30rnd_Base.et` | GUID `63C1E699345B24F9` -> `armst_Magazine_545x39_AK_30rnd_Base.et` | refs 2 | REVIEW_REQUIRED
- `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_AK_30rnd_Tracer.et` | GUID `E5912E45754CD421` -> `armst_Magazine_545x39_AK_30rnd_Tracer.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_RPK_45rnd_Ball.et` | GUID `BC74DAC891D48540` -> `armst_Magazine_545x39_RPK_45rnd_Ball.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_RPK_45rnd_Tracer.et` | GUID `5897D01F41DB5D2D` -> `armst_Magazine_545x39_RPK_45rnd_Tracer.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/762x54/SVD/Box_762x54_PK_250rnd_Ball.et` | GUID `1C260E65B7F290BA` -> `armst_Box_762x54_PK_250rnd_Ball.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/762x54/SVD/Magazine_762x54_SVD_10rnd_7BZ3API.et` | GUID `19600CCA33279D20` -> `armst_Magazine_762x54_SVD_10rnd_7BZ3API.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/763x25/TT/Magazine_763x25_TT_8rnd_Ball.et` | GUID `AA99F5E678010DB3` -> `armst_Magazine_763x25_TT_8rnd_Ball.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/Magazine_762x39_AKM_10rnd_Ball.et` | GUID `07805AE177F52646` -> `armst_Magazine_762x39_AKM_10rnd_Ball.et` | refs 2 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/Magazine_762x39_AKM_30rnd_Ball.et` | GUID `48720FC416263FC1` -> `armst_Magazine_762x39_AKM_30rnd_Ball.et` | refs 3 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/Magazine_9x18_APB_20rnd_Ball.et` | GUID `389EB226473CD590` -> `armst_Magazine_9x18_APB_20rnd_Ball.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/Magazine_9x18_PM_8rnd_Ball.et` | GUID `8B853CDD11BA916E` -> `armst_Magazine_9x18_PM_8rnd_Ball.et` | refs 5 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/Magazine_9x18_PP91_30rnd_Ball.et` | GUID `4488C415F3CA1890` -> `armst_Magazine_9x18_PP91_30rnd_Ball.et` | refs 2 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/Magazine_9x18_SR2_30rnd_Ball.et` | GUID `2610CA8D8632DEF4` -> `armst_Magazine_9x18_SR2_30rnd_Ball.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/Magazine_9x39_20rnd_9a91_SP5.et` | GUID `B7EC6D4222AE12BE` -> `armst_Magazine_9x39_20rnd_9a91_SP5.et` | refs 2 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/Magazine_9x39_20rnd_9a91_SP6.et` | GUID `3F47C33B88171646` -> `armst_Magazine_9x39_20rnd_9a91_SP6.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_20rnd_vss_SP5.et` | GUID `70D023F899C9C226` -> `armst_Magazine_9x39_20rnd_vss_SP5.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_20rnd_vss_SP6.et` | GUID `51E9CE2EB27B3DBD` -> `armst_Magazine_9x39_20rnd_vss_SP6.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_30rnd_val_SP5.et` | GUID `6C22F58BBF5D6AED` -> `armst_Magazine_9x39_30rnd_val_SP5.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_30rnd_val_SP6.et` | GUID `6CBF1E50EB22F09B` -> `armst_Magazine_9x39_30rnd_val_SP6.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Western/5x56/HKG36/Magazine_556x45_HKG36.et` | GUID `969F6FFF810D2145` -> `armst_Magazine_556x45_HKG36.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Western/5x56/SIG550/Magazine_556x45_SIG_550.et` | GUID `E3DC6C2FBBE4F825` -> `armst_Magazine_556x45_SIG_550.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_Base.et` | GUID `11B9CC1FB4AEE740` -> `armst_Magazine_556x45_STANAG_30rnd_Base.et` | refs 1 | REVIEW_REQUIRED
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M193_Ball.et` | GUID `FB5EB0F6D447E859` -> `armst_Magazine_556x45_STANAG_30rnd_M193_Ball.et` | refs 2 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M855_Ball.et` | GUID `2EBF60EF24B108FC` -> `armst_Magazine_556x45_STANAG_30rnd_M855_Ball.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Magazines/Western/9x19/M9/Magazine_9x19_M9_15rnd_Ball.et` | GUID `9C05543A503DB80E` -> `armst_Magazine_9x19_M9_15rnd_Ball.et` | refs 0 | SAFE_RENAME

## Non-compliant ammo

- `Prefabs/Weapons/Ammo/12g/Ammo_12ga.et` | GUID `862E8EB633CED07D` -> `armst_Ammo_12ga.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/12g/Ammo_12ga_shell.et` | GUID `9F7537128778361F` -> `armst_Ammo_12ga_shell.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/12g/Ammo_12ga_shell_test.et` | GUID `9A2EC4D810705428` -> `armst_Ammo_12ga_shell_test.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/12g/Ammo_Buckshot_pellet.et` | GUID `8A45841AC9BA3AE7` -> `armst_Ammo_Buckshot_pellet.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Eastern/762x39/Ammo_762x39_BP.et` | GUID `1785D92E5A104937` -> `armst_Ammo_762x39_BP.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Eastern/762x39/Ammo_762x39_PP.et` | GUID `3E395A4A4B0C4F0E` -> `armst_Ammo_762x39_PP.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Russian/763x25/Ammo_763x25.et` | GUID `8221593DFA48E4B3` -> `armst_Ammo_763x25.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Russian/763x25/Ammo_763x25_Ball.et` | GUID `5AE7AF31B9D7EB6C` -> `armst_Ammo_763x25_Ball.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Russian/9x39/Ammo_9x39_SP5_Ball.et` | GUID `2CB8EAD4A52F3290` -> `armst_Ammo_9x39_SP5_Ball.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Russian/9x39/Ammo_9x39_SP6_Ball.et` | GUID `FB468B29C75FE46A` -> `armst_Ammo_9x39_SP6_Ball.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Russian/grenade/Ammo_Grenade_HE_VOG25.et` | GUID `262F0D09C4130826` -> `armst_Ammo_Grenade_HE_VOG25.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Western/5x56/Ammo_556x45_BP.et` | GUID `716F41EFBBB14F9C` -> `armst_Ammo_556x45_BP.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Western/5x56/Ammo_556x45_PP.et` | GUID `62FA6A6363394955` -> `armst_Ammo_556x45_PP.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Western/762x51/Ammo_762x51_BP.et` | GUID `647D4F418F9F4655` -> `armst_Ammo_762x51_BP.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Western/762x51/Ammo_762x51_PP.et` | GUID `8FAC2EB7CA474E5E` -> `armst_Ammo_762x51_PP.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Western/9x19/Ammo_9x19_BP.et` | GUID `9F5580C950084760` -> `armst_Ammo_9x19_BP.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Ammo/Western/9x19/Ammo_9x19_PP.et` | GUID `DFADF7628FAC4A05` -> `armst_Ammo_9x19_PP.et` | refs 1 | SAFE_RENAME

## Non-compliant ammo configs

- `Configs/Weapons/Ammo/ARMST/Ammo_556x45_ARMST.conf` | GUID `5513C2BA0B7B48F8` -> `armst_Ammo_556x45_ARMST.conf` | refs 5 | SAFE_RENAME
- `Configs/Weapons/Ammo/ARMST/Ammo_762x39_ARMST.conf` | GUID `EA0E25BAF3BD459F` -> `armst_Ammo_762x39_ARMST.conf` | refs 2 | SAFE_RENAME
- `Configs/Weapons/Ammo/ARMST/Ammo_762x51_ARMST.conf` | GUID `94FC75B17BBA4DB7` -> `armst_Ammo_762x51_ARMST.conf` | refs 1 | SAFE_RENAME
- `Configs/Weapons/Ammo/ARMST/Ammo_9x19_ARMST.conf` | GUID `48496091DE244325` -> `armst_Ammo_9x19_ARMST.conf` | refs 1 | SAFE_RENAME

## Non-compliant other prefabs

- `Prefabs/Weapons/Attachments/Handguards/Handguard_AK74M2.et` | GUID `7851F29BDAAAD7DB` -> `armst_Handguard_AK74M2.et` | refs 2 | SAFE_RENAME
- `Prefabs/Weapons/Attachments/Muzzle/Suppressor_9a91.et` | GUID `E10F09941AF1E123` -> `armst_Suppressor_9a91.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Attachments/Muzzle/Suppressor_PBS4/Suppressor_PBS4_base.et` | GUID `5677861A692ED3EB` -> `armst_Suppressor_PBS4_base.et` | refs 2 | REVIEW_REQUIRED
- `Prefabs/Weapons/Attachments/Optics/Optic_PSO1.et` | GUID `C850A33226B8F9C1` -> `armst_Optic_PSO1.et` | refs 4 | SAFE_RENAME
- `Prefabs/Weapons/Attachments/Optics/Optic_PSO1_ak.et` | GUID `F325FE2E3DDCDDAD` -> `armst_Optic_PSO1_ak.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Attachments/Optics/WeaponOptic_Base.et` | GUID `966B4E5523D2F166` -> `armst_WeaponOptic_Base.et` | refs 0 | REVIEW_REQUIRED
- `Prefabs/Weapons/Attachments/Stocks/Handguard_AK74M.et` | GUID `FCE52BA4B5789E65` -> `armst_Handguard_AK74M.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Attachments/Stocks/Handguard_AKS.et` | GUID `31E8EF2214161A25` -> `armst_Handguard_AKS.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Attachments/Stocks/Stock_akm.et` | GUID `B0E764B069F6A153` -> `armst_Stock_akm.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Attachments/Underbarrel/UGL_GP25.et` | GUID `1ABABE3551512B0A` -> `armst_UGL_GP25.et` | refs 2 | SAFE_RENAME
- `Prefabs/Weapons/Core/Grenade_Base.et` | GUID `D7EB24176E5CEAA6` -> `armst_Grenade_Base.et` | refs 0 | REVIEW_REQUIRED
- `Prefabs/Weapons/Core/Magazine_Base.et` | GUID `F9E1A46E3ABA116F` -> `armst_Magazine_Base.et` | refs 8 | REVIEW_REQUIRED
- `Prefabs/Weapons/Core/Rifle_Base.et` | GUID `911D6C8DC7BA2D63` -> `armst_Rifle_Base.et` | refs 3 | REVIEW_REQUIRED
- `Prefabs/Weapons/Core/Weapon_Base.et` | GUID `E1F14DB52DBFBC57` -> `armst_Weapon_Base.et` | refs 1 | REVIEW_REQUIRED
- `Prefabs/Weapons/Grenades/Grenade_M67.et` | GUID `E8F00BF730225B00` -> `armst_Grenade_M67.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Grenades/Grenade_RGD5.et` | GUID `645C73791ECA1698` -> `armst_Grenade_RGD5.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Grenades/Smoke_ANM8HC.et` | GUID `9DB69176CEF0EE97` -> `armst_Smoke_ANM8HC.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Grenades/Smoke_RDG2.et` | GUID `77EAE5E07DC4678A` -> `armst_Smoke_RDG2.et` | refs 0 | SAFE_RENAME
- `Prefabs/Weapons/Tripods/Tripod_6T5.et` | GUID `7C4D1A64D60F2C92` -> `armst_Tripod_6T5.et` | refs 1 | SAFE_RENAME
- `Prefabs/Weapons/Tripods/Tripod_6T5_PKM.et` | GUID `723870DBB19D30B0` -> `armst_Tripod_6T5_PKM.et` | refs 0 | SAFE_RENAME

## References of non-compliant resources

### `Prefabs/Weapons/Ammo/12g/Ammo_12ga.et`
- `Configs/Weapons/Ammo/Ammo_12g.conf`
### `Prefabs/Weapons/Ammo/12g/Ammo_12ga_shell.et`
- `Configs/Weapons/Ammo/Ammo_12g.conf`
### `Prefabs/Weapons/Ammo/12g/Ammo_12ga_shell_test.et`
- `Configs/Weapons/Ammo/Ammo_12g.conf`
### `Prefabs/Weapons/Ammo/12g/Ammo_Buckshot_pellet.et`
- `Prefabs/Weapons/Ammo/12g/Ammo_12ga.et`
### `Prefabs/Weapons/Ammo/Eastern/762x39/Ammo_762x39_BP.et`
- `Configs/Weapons/Ammo/ARMST/Ammo_762x39_ARMST.conf`
### `Prefabs/Weapons/Ammo/Eastern/762x39/Ammo_762x39_PP.et`
- `Configs/Weapons/Ammo/ARMST/Ammo_762x39_ARMST.conf`
### `Prefabs/Weapons/Ammo/Russian/763x25/Ammo_763x25.et`
- no live references
### `Prefabs/Weapons/Ammo/Russian/763x25/Ammo_763x25_Ball.et`
- `Configs/Weapons/Ammo/Ammo_763x25.conf`
### `Prefabs/Weapons/Ammo/Russian/9x39/Ammo_9x39_SP5_Ball.et`
- `Configs/Weapons/Ammo/Ammo_9x39.conf`
### `Prefabs/Weapons/Ammo/Russian/9x39/Ammo_9x39_SP6_Ball.et`
- `Configs/Weapons/Ammo/Ammo_9x39.conf`
### `Prefabs/Weapons/Ammo/Russian/grenade/Ammo_Grenade_HE_VOG25.et`
- no live references
### `Prefabs/Weapons/Ammo/Western/5x56/Ammo_556x45_BP.et`
- `Configs/Weapons/Ammo/ARMST/Ammo_556x45_ARMST.conf`
### `Prefabs/Weapons/Ammo/Western/5x56/Ammo_556x45_PP.et`
- `Configs/Weapons/Ammo/ARMST/Ammo_556x45_ARMST.conf`
### `Prefabs/Weapons/Ammo/Western/762x51/Ammo_762x51_BP.et`
- `Configs/Weapons/Ammo/ARMST/Ammo_762x51_ARMST.conf`
### `Prefabs/Weapons/Ammo/Western/762x51/Ammo_762x51_PP.et`
- `Configs/Weapons/Ammo/ARMST/Ammo_762x51_ARMST.conf`
### `Prefabs/Weapons/Ammo/Western/9x19/Ammo_9x19_BP.et`
- `Configs/Weapons/Ammo/ARMST/Ammo_9x19_ARMST.conf`
### `Prefabs/Weapons/Ammo/Western/9x19/Ammo_9x19_PP.et`
- `Configs/Weapons/Ammo/ARMST/Ammo_9x19_ARMST.conf`
### `Prefabs/Weapons/Attachments/Handguards/Handguard_AK74M2.et`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74M.et`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AKS.et`
### `Prefabs/Weapons/Attachments/Muzzle/Suppressor_9a91.et`
- `Prefabs/Weapons/Russian/Rifle/VSK94/armst_Rifle_VSK94_base.et`
### `Prefabs/Weapons/Attachments/Muzzle/Suppressor_PBS4/Suppressor_PBS4_base.et`
- `Prefabs/Weapons/Attachments/Muzzle/Suppressor_9a91.et`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74M_full.et`
### `Prefabs/Weapons/Attachments/Optics/Optic_PSO1.et`
- `Prefabs/Weapons/Attachments/Optics/Optic_PSO1_ak.et`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74M_full.et`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM_full.et`
- `armst_Optic_PSO1_DovetailRU.et`
### `Prefabs/Weapons/Attachments/Optics/Optic_PSO1_ak.et`
- no live references
### `Prefabs/Weapons/Attachments/Optics/WeaponOptic_Base.et`
- no live references
### `Prefabs/Weapons/Attachments/Stocks/Handguard_AK74M.et`
- no live references
### `Prefabs/Weapons/Attachments/Stocks/Handguard_AKS.et`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AKS.et`
### `Prefabs/Weapons/Attachments/Stocks/Stock_akm.et`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM.et`
### `Prefabs/Weapons/Attachments/Underbarrel/UGL_GP25.et`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74M_full.et`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM_full.et`
### `Prefabs/Weapons/Core/Grenade_Base.et`
- no live references
### `Prefabs/Weapons/Core/Magazine_Base.et`
- `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_AK_30rnd_Base.et`
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/Magazine_9x39_20rnd_9a91_SP5.et`
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/Magazine_9x39_20rnd_9a91_SP6.et`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_20rnd_vss_SP5.et`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_20rnd_vss_SP6.et`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_30rnd_val_SP5.et`
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_30rnd_val_SP6.et`
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_Base.et`
### `Prefabs/Weapons/Core/Rifle_Base.et`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM_base.et`
- `Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et`
- `Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_hk_g36.et`
### `Prefabs/Weapons/Core/Weapon_Base.et`
- `Prefabs/Weapons/Core/Rifle_Base.et`
### `Prefabs/Weapons/Grenades/Grenade_M67.et`
- no live references
### `Prefabs/Weapons/Grenades/Grenade_RGD5.et`
- no live references
### `Prefabs/Weapons/Grenades/Smoke_ANM8HC.et`
- no live references
### `Prefabs/Weapons/Grenades/Smoke_RDG2.et`
- no live references
### `Prefabs/Weapons/Magazines/12ga/12ga_Buckshot.et`
- `Prefabs/Weapons/Western/Shotgun/armst_shotgun_base.et`
### `Prefabs/Weapons/Magazines/12ga/12ga_Buckshot_base.et`
- `Prefabs/Weapons/Magazines/12ga/12ga_Buckshot.et`
### `Prefabs/Weapons/Magazines/12ga/12ga_Shell.et`
- no live references
### `Prefabs/Weapons/Magazines/12ga/12ga_Shell_test.et`
- no live references
### `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_AK_30rnd_Ball.et`
- no live references
### `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_AK_30rnd_Base.et`
- `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_AK_30rnd_Ball.et`
- `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_AK_30rnd_Tracer.et`
### `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_AK_30rnd_Tracer.et`
- no live references
### `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_RPK_45rnd_Ball.et`
- no live references
### `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_RPK_45rnd_Tracer.et`
- no live references
### `Prefabs/Weapons/Magazines/Russian/762x54/SVD/Box_762x54_PK_250rnd_Ball.et`
- no live references
### `Prefabs/Weapons/Magazines/Russian/762x54/SVD/Magazine_762x54_SVD_10rnd_7BZ3API.et`
- no live references
### `Prefabs/Weapons/Magazines/Russian/763x25/TT/Magazine_763x25_TT_8rnd_Ball.et`
- `Prefabs/Weapons/Russian/Handguns/TT/armst_TT.et`
### `Prefabs/Weapons/Magazines/Russian/7x62/AKM/Magazine_762x39_AKM_10rnd_Ball.et`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_SOC94.et`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_VPO136.et`
### `Prefabs/Weapons/Magazines/Russian/7x62/AKM/Magazine_762x39_AKM_30rnd_Ball.et`
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/Magazine_762x39_AKM_10rnd_Ball.et`
- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM.et`
- `Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et`
### `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/Magazine_9x18_APB_20rnd_Ball.et`
- `Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB.et`
### `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/Magazine_9x18_PM_8rnd_Ball.et`
- `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et`
- `Prefabs/Weapons/Magazines/Russian/763x25/TT/Magazine_763x25_TT_8rnd_Ball.et`
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/Magazine_9x18_APB_20rnd_Ball.et`
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/Magazine_9x18_PP91_30rnd_Ball.et`
- `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/Magazine_9x18_SR2_30rnd_Ball.et`
### `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/Magazine_9x18_PP91_30rnd_Ball.et`
- `Prefabs/Weapons/Russian/Handguns/PP_19/armst_PP91.et`
- `Prefabs/Weapons/Russian/Handguns/Sr_2/armst_SR_2.et`
### `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/Magazine_9x18_SR2_30rnd_Ball.et`
- no live references
### `Prefabs/Weapons/Magazines/Russian/9x39/9a91/Magazine_9x39_20rnd_9a91_SP5.et`
- `Prefabs/Weapons/Russian/Rifle/9a91/armst_Rifle_9a91_base.et`
- `Prefabs/Weapons/Russian/Rifle/VSK94/armst_Rifle_VSK94_base.et`
### `Prefabs/Weapons/Magazines/Russian/9x39/9a91/Magazine_9x39_20rnd_9a91_SP6.et`
- no live references
### `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_20rnd_vss_SP5.et`
- `Prefabs/Weapons/Russian/Rifle/VSS/armst_Rifle_vss_base.et`
### `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_20rnd_vss_SP6.et`
- no live references
### `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_30rnd_val_SP5.et`
- no live references
### `Prefabs/Weapons/Magazines/Russian/9x39/VSS/Magazine_9x39_30rnd_val_SP6.et`
- no live references
### `Prefabs/Weapons/Magazines/Western/5x56/HKG36/Magazine_556x45_HKG36.et`
- `Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_hk_g36.et`
### `Prefabs/Weapons/Magazines/Western/5x56/SIG550/Magazine_556x45_SIG_550.et`
- `Prefabs/Weapons/Western/Rifle/Sig550/armst_Rifle_Sig550.et`
### `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_Base.et`
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M855_Ball.et`
### `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M193_Ball.et`
- `Prefabs/Weapons/Magazines/Western/5x56/HKG36/Magazine_556x45_HKG36.et`
- `Prefabs/Weapons/Magazines/Western/5x56/SIG550/Magazine_556x45_SIG_550.et`
### `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M855_Ball.et`
- no live references
### `Prefabs/Weapons/Magazines/Western/9x19/M9/Magazine_9x19_M9_15rnd_Ball.et`
- no live references
### `Prefabs/Weapons/Tripods/Tripod_6T5.et`
- `Prefabs/Weapons/Tripods/Tripod_6T5_PKM.et`
### `Prefabs/Weapons/Tripods/Tripod_6T5_PKM.et`
- no live references
### `Configs/Weapons/Ammo/ARMST/Ammo_556x45_ARMST.conf`
- `Prefabs/Weapons/Magazines/Western/5x56/HKG36/Magazine_556x45_HKG36.et`
- `Prefabs/Weapons/Magazines/Western/5x56/SIG550/Magazine_556x45_SIG_550.et`
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_Base.et`
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M193_Ball.et`
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M855_Ball.et`
### `Configs/Weapons/Ammo/ARMST/Ammo_762x39_ARMST.conf`
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/Magazine_762x39_AKM_10rnd_Ball.et`
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/Magazine_762x39_AKM_30rnd_Ball.et`
### `Configs/Weapons/Ammo/ARMST/Ammo_762x51_ARMST.conf`
- `Prefabs/Weapons/Magazines/Western/762x51/HK3/armst_Magazine_762x51_HK3_20_M80_Ball.et`
### `Configs/Weapons/Ammo/ARMST/Ammo_9x19_ARMST.conf`
- `Prefabs/Weapons/Magazines/Western/9x19/M9/Magazine_9x19_M9_15rnd_Ball.et`
