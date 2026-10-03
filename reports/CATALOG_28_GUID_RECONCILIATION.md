# Catalog rescan #28 — GUID reconciliation (READ-ONLY, isolated candidate)

**Status:** `CANONICAL_PUBLICATION_BLOCKED_PENDING_GUID_CROSSWALK_AND_SOURCE_STATE`. No canonical edits/push. Candidate: `%TEMP%\opencode\mp133_rescan\repo`. Source: Issue #28 + comment 5968348043.

## Summary / risk ranking

- deleted entries: **121**; new entries: **32**.
  - deleted classified `RELOCATED_OR_RENAMED`: **91**
  - deleted classified `SOURCE_INTENTIONALLY_ABSENT`: **30**
  - new classified `RELOCATED_OR_RENAMED`: **3**
  - new classified `SOURCE_ADDED`: **29**

Highest risk = `SCANNER_COVERAGE_OR_BUG` (source file still on disk but no longer cataloged) and `UNRESOLVED`. `RELOCATED_OR_RENAMED` = same source GUID present in the candidate (proven by GUID, not name).

## Crosswalk — DELETED (old catalog file -> classification)

| old path | guid | source resource | classification | -> new (same guid) | on disk |
|---|---|---|---|---|---|
| `catalog/ammunition/ammo_12ga.json` | `862E8EB633CED07D` | `Prefabs/Weapons/Ammo/12g/Ammo_12ga.et` | **RELOCATED_OR_RENAMED** | catalog/ammunition/armst_ammo_12ga.json | no |
| `catalog/ammunition/ammo_12ga_shell.json` | `9F7537128778361F` | `Prefabs/Weapons/Ammo/12g/Ammo_12ga_shell.et` | **RELOCATED_OR_RENAMED** | catalog/ammunition/armst_ammo_12ga_shell.json | no |
| `catalog/ammunition/ammo_12ga_shell_test.json` | `9A2EC4D810705428` | `Prefabs/Weapons/Ammo/12g/Ammo_12ga_shell_test.et` | **RELOCATED_OR_RENAMED** | catalog/ammunition/armst_ammo_12ga_shell_test.json | no |
| `catalog/ammunition/ammo_545x39_ball_7n6.json` | `1D9DDE1632F33A9E` | `Prefabs/Weapons/Ammo/Ammo_545x39_Ball_7N6.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/ammunition/ammo_556x45_ball_m193.json` | `9CE4CC890A2A574F` | `Prefabs/Weapons/Ammo/Ammo_556x45_Ball_M193.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/ammunition/ammo_762x39_ball_57n231.json` | `2FBCA0A7CEDDE7B0` | `Prefabs/Weapons/Ammo/Ammo_762x39_Ball_57N231.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/ammunition/ammo_763x25.json` | `8221593DFA48E4B3` | `Prefabs/Weapons/Ammo/Ammo_763x25.et` | **RELOCATED_OR_RENAMED** | catalog/ammunition/armst_ammo_763x25.json | no |
| `catalog/ammunition/ammo_763x25_ball.json` | `5AE7AF31B9D7EB6C` | `Prefabs/Weapons/Ammo/Ammo_763x25_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/ammunition/armst_ammo_763x25_ball.json | no |
| `catalog/ammunition/ammo_9x18_ball_57n181.json` | `4DE72DF927310A8B` | `Prefabs/Weapons/Ammo/Ammo_9x18_Ball_57N181.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/ammunition/ammo_9x19_ball_m882.json` | `9D290AA75ADA4618` | `Prefabs/Weapons/Ammo/Ammo_9x19_Ball_M882.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/ammunition/ammo_9x39_sp5_ball.json` | `2CB8EAD4A52F3290` | `Prefabs/Weapons/Ammo/Ammo_9x39_SP5_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/ammunition/armst_ammo_9x39_sp5_ball.json | no |
| `catalog/ammunition/ammo_9x39_sp6_ball.json` | `FB468B29C75FE46A` | `Prefabs/Weapons/Ammo/Ammo_9x39_SP6_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/ammunition/armst_ammo_9x39_sp6_ball.json | no |
| `catalog/ammunition/ammo_buckshot_pellet.json` | `8A45841AC9BA3AE7` | `Prefabs/Weapons/Ammo/12g/Ammo_Buckshot_pellet.et` | **RELOCATED_OR_RENAMED** | catalog/ammunition/armst_ammo_buckshot_pellet.json | no |
| `catalog/ammunition/ammo_grenade_he_vog25.json` | `262F0D09C4130826` | `Prefabs/Weapons/Ammo/Ammo_Grenade_HE_VOG25.et` | **RELOCATED_OR_RENAMED** | catalog/ammunition/armst_ammo_grenade_he_vog25.json | no |
| `catalog/attachments/handguard_ak74m.json` | `FCE52BA4B5789E65` | `Prefabs/Weapons/Attachments/Stocks/Handguard_AK74M.et` | **RELOCATED_OR_RENAMED** | catalog/attachments/armst_handguard_ak74m.json | no |
| `catalog/attachments/handguard_ak74m2.json` | `7851F29BDAAAD7DB` | `Prefabs/Weapons/Attachments/Handguards/Handguard_AK74M2.et` | **RELOCATED_OR_RENAMED** | catalog/attachments/armst_handguard_ak74m2.json | no |
| `catalog/attachments/handguard_aks.json` | `31E8EF2214161A25` | `Prefabs/Weapons/Attachments/Stocks/Handguard_AKS.et` | **RELOCATED_OR_RENAMED** | catalog/attachments/armst_handguard_aks.json | no |
| `catalog/attachments/stock_akm.json` | `B0E764B069F6A153` | `Prefabs/Weapons/Attachments/Stocks/Stock_akm.et` | **RELOCATED_OR_RENAMED** | catalog/attachments/armst_stock_akm.json | no |
| `catalog/attachments/suppressor_9a91.json` | `E10F09941AF1E123` | `Prefabs/Weapons/Attachments/Muzzle/Suppressor_9a91.et` | **RELOCATED_OR_RENAMED** | catalog/attachments/armst_suppressor_9a91.json | no |
| `catalog/attachments/suppressor_pbs4_base.json` | `5677861A692ED3EB` | `Prefabs/Weapons/Attachments/Muzzle/Suppressor_PBS4/Suppressor_PBS4_base.et` | **RELOCATED_OR_RENAMED** | catalog/attachments/armst_suppressor_pbs4.json | no |
| `catalog/attachments/ugl_gp25.json` | `1ABABE3551512B0A` | `Prefabs/Weapons/Attachments/Underbarrel/UGL_GP25.et` | **RELOCATED_OR_RENAMED** | catalog/attachments/armst_ugl_gp25.json | no |
| `catalog/grenades/armst_smoke_anm8hc.json` | `9DB69176CEF0EE97` | `Prefabs/Weapons/Grenades/armst_Smoke_ANM8HC.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_smoke_anm8hc.json | yes |
| `catalog/grenades/armst_smoke_rdg2.json` | `77EAE5E07DC4678A` | `Prefabs/Weapons/Grenades/armst_Smoke_RDG2.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_smoke_rdg2.json | yes |
| `catalog/grenades/grenade_m67.json` | `E8F00BF730225B00` | `Prefabs/Weapons/Grenades/Grenade_M67.et` | **RELOCATED_OR_RENAMED** | catalog/grenades/armst_grenade_m67.json | no |
| `catalog/grenades/grenade_rgd5.json` | `645C73791ECA1698` | `Prefabs/Weapons/Grenades/Grenade_RGD5.et` | **RELOCATED_OR_RENAMED** | catalog/grenades/armst_grenade_rgd5.json | no |
| `catalog/grenades/smoke_anm8hc.json` | `9DB69176CEF0EE97` | `Prefabs/Weapons/Grenades/Smoke_ANM8HC.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_smoke_anm8hc.json | no |
| `catalog/grenades/smoke_rdg2.json` | `77EAE5E07DC4678A` | `Prefabs/Weapons/Grenades/Smoke_RDG2.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_smoke_rdg2.json | no |
| `catalog/magazines/12ga_buckshot.json` | `B0DFDF7AAA9C5D39` | `Prefabs/Weapons/Magazines/12ga/12ga_Buckshot.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_12ga_buckshot.json | no |
| `catalog/magazines/12ga_shell.json` | `0346C78F29531C70` | `Prefabs/Weapons/Magazines/12ga/12ga_Shell.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_12ga_shell.json | no |
| `catalog/magazines/12ga_shell_test.json` | `5220A773A621C2BB` | `Prefabs/Weapons/Magazines/12ga/12ga_Shell_test.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_12ga_shell_test.json | no |
| `catalog/magazines/armst_magazine_545x39_ak_30rnd_ball.json` | `BBB50A815A2F916B` | `Prefabs/Weapons/Magazines/Russian/5x45/AK74/armst_Magazine_545x39_AK_30rnd_Ball.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/armst_magazine_545x39_ak_30rnd_tracer.json` | `E5912E45754CD421` | `Prefabs/Weapons/Magazines/Russian/5x45/AK74/armst_Magazine_545x39_AK_30rnd_Tracer.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/armst_magazine_545x39_rpk_45rnd_ball.json` | `BC74DAC891D48540` | `Prefabs/Weapons/Magazines/Russian/5x45/AK74/armst_Magazine_545x39_RPK_45rnd_Ball.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/armst_magazine_545x39_rpk_45rnd_tracer.json` | `5897D01F41DB5D2D` | `Prefabs/Weapons/Magazines/Russian/5x45/AK74/armst_Magazine_545x39_RPK_45rnd_Tracer.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/box_762x54_pk_250rnd_ball.json` | `1C260E65B7F290BA` | `Prefabs/Weapons/Magazines/Box_762x54_PK_250rnd_Ball.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/magazine_545x39_ak_30rnd_ball.json` | `BBB50A815A2F916B` | `Prefabs/Weapons/Magazines/5x45/Magazine_545x39_AK_30rnd_Ball.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/magazine_545x39_ak_30rnd_base.json` | `63C1E699345B24F9` | `Prefabs/Weapons/Magazines/Russian/5x45/AK74/Magazine_545x39_AK_30rnd_Base.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/magazine_545x39_ak_30rnd_tracer.json` | `E5912E45754CD421` | `Prefabs/Weapons/Magazines/5x45/Magazine_545x39_AK_30rnd_Tracer.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/magazine_545x39_rpk_45rnd_ball.json` | `BC74DAC891D48540` | `Prefabs/Weapons/Magazines/5x45/Magazine_545x39_RPK_45rnd_Ball.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/magazine_545x39_rpk_45rnd_tracer.json` | `5897D01F41DB5D2D` | `Prefabs/Weapons/Magazines/5x45/Magazine_545x39_RPK_45rnd_Tracer.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/magazine_556x45_stanag_30rnd_m193_ball.json` | `FB5EB0F6D447E859` | `Prefabs/Weapons/Magazines/5x56/Magazine_556x45_STANAG_30rnd_M193_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_556x45_stanag_30rnd_m193_ball.json | no |
| `catalog/magazines/magazine_556x45_stanag_30rnd_m196_tracer.json` | `4575737B3D3A4505` | `Prefabs/Weapons/Magazines/5x56/Magazine_556x45_STANAG_30rnd_M196_Tracer.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/magazine_556x45_stanag_30rnd_m855_ball.json` | `2EBF60EF24B108FC` | `Prefabs/Weapons/Magazines/5x56/Magazine_556x45_STANAG_30rnd_M855_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_556x45_stanag_30rnd_m855_ball.json | no |
| `catalog/magazines/magazine_556x45_stanag_30rnd_m856_tracer.json` | `A9A385FE1F7BF4BD` | `Prefabs/Weapons/Magazines/5x56/Magazine_556x45_STANAG_30rnd_M856_Tracer.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/magazine_762x39_akm_10rnd_ball.json` | `07805AE177F52646` | `Prefabs/Weapons/Magazines/7x62/Magazine_762x39_AKM_10rnd_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_762x39_akm_10rnd_ball.json | no |
| `catalog/magazines/magazine_762x39_akm_30rnd_ball.json` | `48720FC416263FC1` | `Prefabs/Weapons/Magazines/7x62/Magazine_762x39_AKM_30rnd_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_762x39_akm_30rnd_ball.json | no |
| `catalog/magazines/magazine_762x39_akm_30rnd_tracer.json` | `FAFA0D71E75CEBE2` | `Prefabs/Weapons/Magazines/7x62/Magazine_762x39_AKM_30rnd_Tracer.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/magazine_762x54_svd_10rnd_7bz3api.json` | `19600CCA33279D20` | `Prefabs/Weapons/Magazines/Magazine_762x54_SVD_10rnd_7BZ3API.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_762x54_svd_10rnd_7bz3api.json | no |
| `catalog/magazines/magazine_762x54_svd_10rnd_sniper.json` | `9CCB46C6EE632C1A` | `Prefabs/Weapons/Magazines/Magazine_762x54_SVD_10rnd_Sniper.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/magazines/magazine_763x25_tt_8rnd_ball.json` | `AA99F5E678010DB3` | `Prefabs/Weapons/Magazines/Magazine_763x25_TT_8rnd_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_763x25_tt_8rnd_ball.json | no |
| `catalog/magazines/magazine_9x18_apb_20rnd_ball.json` | `389EB226473CD590` | `Prefabs/Weapons/Magazines/Magazine_9x18_APB_20rnd_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_9x18_apb_20rnd_ball.json | no |
| `catalog/magazines/magazine_9x18_pm_8rnd_ball.json` | `8B853CDD11BA916E` | `Prefabs/Weapons/Magazines/Magazine_9x18_PM_8rnd_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_9x18_pm_8rnd_ball.json | no |
| `catalog/magazines/magazine_9x18_pp91_30rnd_ball.json` | `4488C415F3CA1890` | `Prefabs/Weapons/Magazines/Magazine_9x18_PP91_30rnd_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_9x18_pp91_30rnd_ball.json | no |
| `catalog/magazines/magazine_9x18_sr2_30rnd_ball.json` | `2610CA8D8632DEF4` | `Prefabs/Weapons/Magazines/Magazine_9x18_SR2_30rnd_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_9x18_sr2_30rnd_ball.json | no |
| `catalog/magazines/magazine_9x19_m9_15rnd_ball.json` | `9C05543A503DB80E` | `Prefabs/Weapons/Magazines/Magazine_9x19_M9_15rnd_Ball.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_9x19_m9_15rnd_ball.json | no |
| `catalog/magazines/magazine_9x39_20rnd_9a91_sp5.json` | `B7EC6D4222AE12BE` | `Prefabs/Weapons/Magazines/9x39/Magazine_9x39_20rnd_9a91_SP5.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_9x39_20rnd_9a91_sp5.json | no |
| `catalog/magazines/magazine_9x39_20rnd_9a91_sp6.json` | `3F47C33B88171646` | `Prefabs/Weapons/Magazines/9x39/Magazine_9x39_20rnd_9a91_SP6.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_9x39_20rnd_9a91_sp6.json | no |
| `catalog/magazines/magazine_9x39_20rnd_vss_sp5.json` | `70D023F899C9C226` | `Prefabs/Weapons/Magazines/9x39/Magazine_9x39_20rnd_vss_SP5.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_9x39_20rnd_vss_sp5.json | no |
| `catalog/magazines/magazine_9x39_20rnd_vss_sp6.json` | `51E9CE2EB27B3DBD` | `Prefabs/Weapons/Magazines/9x39/Magazine_9x39_20rnd_vss_SP6.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_9x39_20rnd_vss_sp6.json | no |
| `catalog/magazines/magazine_9x39_30rnd_val_sp5.json` | `6C22F58BBF5D6AED` | `Prefabs/Weapons/Magazines/9x39/Magazine_9x39_30rnd_val_SP5.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_9x39_30rnd_val_sp5.json | no |
| `catalog/magazines/magazine_9x39_30rnd_val_sp6.json` | `6CBF1E50EB22F09B` | `Prefabs/Weapons/Magazines/9x39/Magazine_9x39_30rnd_val_SP6.et` | **RELOCATED_OR_RENAMED** | catalog/magazines/armst_magazine_9x39_30rnd_val_sp6.json | no |
| `catalog/optics/optic_4x20.json` | `DB6D823CC95A48F2` | `Prefabs/Weapons/Attachments/Optics/Optic_4x20/Optic_4x20.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/optics/optic_pso1.json` | `C850A33226B8F9C1` | `Prefabs/Weapons/Attachments/Optics/Optic_PSO1.et` | **RELOCATED_OR_RENAMED** | catalog/optics/armst_optic_pso1.json | no |
| `catalog/optics/optic_pso1_ak.json` | `F325FE2E3DDCDDAD` | `Prefabs/Weapons/Attachments/Optics/Optic_PSO1_ak.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/tripods/tripod_6t5.json` | `7C4D1A64D60F2C92` | `Prefabs/Weapons/Tripods/Tripod_6T5.et` | **RELOCATED_OR_RENAMED** | catalog/tripods/armst_tripod_6t5.json | no |
| `catalog/tripods/tripod_6t5_pkm.json` | `723870DBB19D30B0` | `Prefabs/Weapons/Tripods/Tripod_6T5_PKM.et` | **RELOCATED_OR_RENAMED** | catalog/tripods/armst_tripod_6t5_pkm.json | no |
| `catalog/tripods/tripod_6t7_nsv.json` | `29F0CC704A582154` | `Prefabs/Weapons/Tripods/6T7/Tripod_6T7_NSV.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/weapons/armst_ak105.json` | `6FC3151D0DED22A9` | `Prefabs/Weapons/Rifles/AK74/armst_AK105.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_ak105.json | no |
| `catalog/weapons/armst_ak74.json` | `FA5C25BF66A53DCF` | `Prefabs/Weapons/Rifles/AK74/armst_AK74.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_ak74.json | no |
| `catalog/weapons/armst_ak74m.json` | `5B8E766C0E3C13EE` | `Prefabs/Weapons/Rifles/AK74/armst_AK74M.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_ak74m.json | no |
| `catalog/weapons/armst_ak74m_full.json` | `63892659A632A0FD` | `Prefabs/Weapons/Rifles/AK74/armst_AK74M_full.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_ak74m_full.json | no |
| `catalog/weapons/armst_ak74n.json` | `96DFD2E7E63B3386` | `Prefabs/Weapons/Rifles/AK74/armst_AK74N.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_ak74n.json | no |
| `catalog/weapons/armst_aks.json` | `25A64724FD416989` | `Prefabs/Weapons/Rifles/AK74/armst_AKS.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_aks.json | no |
| `catalog/weapons/armst_aks74u.json` | `BFEA719491610A45` | `Prefabs/Weapons/Rifles/AK74/armst_AKS74U.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_aks74u.json | no |
| `catalog/weapons/armst_aks74un.json` | `FA0E25CE35EE945F` | `Prefabs/Weapons/Rifles/AK74/armst_AKS74UN.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/weapons/armst_apb.json` | `5D3DA7E84135B278` | `Prefabs/Weapons/Handguns/armst_APB.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_pistol_apb_base.json | no |
| `catalog/weapons/armst_groza1.json` | `D6699D8C8AF3C786` | `Prefabs/Weapons/Rifles/Groza/armst_groza1.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/weapons/armst_izh_27.json` | `57F153EFAD34E1CA` | `Prefabs/Weapons/Rifles/Shotgun/armst_izh_27.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_shotgun_izh_27.json | no |
| `catalog/weapons/armst_m9.json` | `1353C6EAD1DCFE43` | `Prefabs/Weapons/Handguns/armst_M9.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_pistol_m9.json | no |
| `catalog/weapons/armst_mp_133.json` | `63FF6FDCA4E7E735` | `Prefabs/Weapons/Rifles/Shotgun/armst_mp_133.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_shotgun_mp_133.json | no |
| `catalog/weapons/armst_mp_153.json` | `92DB80A098AABF1C` | `Prefabs/Weapons/Rifles/Shotgun/armst_mp_153.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_shotgun_mp_153.json | no |
| `catalog/weapons/armst_pkm.json` | `A89BC9D55FFB4CD8` | `Prefabs/Weapons/MachineGuns/armst_PKM.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_mgun_pkm.json | no |
| `catalog/weapons/armst_pm.json` | `C0F7DD85A86B2900` | `Prefabs/Weapons/Handguns/armst_PM.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_pistol_pm.json | no |
| `catalog/weapons/armst_pp91.json` | `3968B2A856852CBD` | `Prefabs/Weapons/Handguns/armst_PP91.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_pistol_pp91_base.json | no |
| `catalog/weapons/armst_remington_870.json` | `6DBEF115AA35E404` | `Prefabs/Weapons/Rifles/Shotgun/armst_Remington_870.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_shotgun_remington_870.json | no |
| `catalog/weapons/armst_rpk74.json` | `A7AF84C6C58BA3E8` | `Prefabs/Weapons/MachineGuns/armst_RPK74.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_mgun_rpk74.json | no |
| `catalog/weapons/armst_spas_12.json` | `221AED80163B7C60` | `Prefabs/Weapons/Rifles/Shotgun/armst_spas_12.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_shotgun_spas_12.json | no |
| `catalog/weapons/armst_sr_2.json` | `31FB2EC4F4AFFC05` | `Prefabs/Weapons/Handguns/armst_SR_2.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_pistol_sr_2_base.json | no |
| `catalog/weapons/armst_svd.json` | `3EB02CDAD5F23C82` | `Prefabs/Weapons/Rifles/armst_SVD.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_svd.json | no |
| `catalog/weapons/armst_toz_66.json` | `923B067A74826419` | `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_shotgun_toz_66.json | no |
| `catalog/weapons/armst_toz_66_pantera.json` | `A9B143751CB07F45` | `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_pantera.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_shotgun_toz_66_pantera.json | no |
| `catalog/weapons/armst_toz_66_saw.json` | `9C7C3BE87956383A` | `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_saw.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_shotgun_toz_66_saw.json | no |
| `catalog/weapons/armst_tt.json` | `0D469F42B65E350E` | `Prefabs/Weapons/Handguns/armst_TT.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_pistol_tt_base.json | no |
| `catalog/weapons/armst_vz58p_base.json` | `9C948630078D154D` | `Prefabs/Weapons/Western/Rifle/armst_VZ58P_base.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_vz58p.json | no |
| `catalog/weapons/armst_vz58v_base.json` | `443CEFF17E040B11` | `Prefabs/Weapons/Western/Rifle/armst_VZ58V_base.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_vz58v.json | no |
| `catalog/weapons/groza_base.json` | `903C7920F00AB654` | `Prefabs/Weapons/Rifles/Groza/Groza_base.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_groza_base.json | no |
| `catalog/weapons/handgun_knife_base.json` | `26ADE11C416B3840` | `Prefabs/Weapons/Handguns/Handgun_Knife_base.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_handgun_knife_base.json | no |
| `catalog/weapons/oc_groza.json` | `F0B67D37B1EA76A5` | `Prefabs/Weapons/Rifles/VAL/Oc_Groza.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/weapons/rifle_9a91.json` | `D9E3D87A149B4453` | `Prefabs/Weapons/Rifles/9a91/Rifle_9a91.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/weapons/rifle_9a91_base.json` | `E2D8F39AE1B9B8F1` | `Prefabs/Weapons/Rifles/9a91/Rifle_9a91_base.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_9a91_base.json | no |
| `catalog/weapons/rifle_9a91_suppressor.json` | `0F53A872DF2BC37E` | `Prefabs/Weapons/Rifles/9a91/Rifle_9a91_suppressor.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/weapons/rifle_akm.json` | `5BFF97EFD0BF6D9F` | `Prefabs/Weapons/Rifles/AKM/Rifle_AKM.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_akm.json | no |
| `catalog/weapons/rifle_akm_base.json` | `140E94F473B60FE3` | `Prefabs/Weapons/Rifles/AKM/Rifle_AKM_base.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_akm_base.json | no |
| `catalog/weapons/rifle_akm_full.json` | `33BEE1A93C920B26` | `Prefabs/Weapons/Rifles/AKM/Rifle_AKM_full.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_akm_full.json | no |
| `catalog/weapons/rifle_akms.json` | `5712F6F88A014F0B` | `Prefabs/Weapons/Rifles/AKM/Rifle_AKMS.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_akms.json | no |
| `catalog/weapons/rifle_hk_g36.json` | `A802C718201D72DF` | `Prefabs/Weapons/Rifles/Rifle_hk_g36.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_hkg36_base.json | no |
| `catalog/weapons/rifle_hkg33.json` | `035CFC7DD44455D0` | `Prefabs/Weapons/Rifles/Rifle_HKG33.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_hkg33_base.json | no |
| `catalog/weapons/rifle_l85.json` | `45D3FCA77AF1709B` | `Prefabs/Weapons/Rifles/Rifle_L85.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_l85_base.json | no |
| `catalog/weapons/rifle_m16a2.json` | `3E413771E1834D2F` | `Prefabs/Weapons/Rifles/Rifle_M16A2.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_m16a2.json | no |
| `catalog/weapons/rifle_m16a2_carbine.json` | `F97A4AC994231900` | `Prefabs/Weapons/Rifles/Rifle_M16A2_carbine.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_m4_carbine.json | no |
| `catalog/weapons/rifle_sig550.json` | `CA3BEBAADDFAF1DE` | `Prefabs/Weapons/Rifles/Rifle_Sig550.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_sig550_base.json | no |
| `catalog/weapons/rifle_soc94.json` | `E394112ABBC198D8` | `Prefabs/Weapons/Rifles/AKM/Rifle_SOC94.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_soc94.json | no |
| `catalog/weapons/rifle_val.json` | `70394D8A205527F6` | `Prefabs/Weapons/Rifles/VAL/Rifle_VAL.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/weapons/rifle_val_base.json` | `F25D16BD5F748372` | `Prefabs/Weapons/Rifles/VAL/Rifle_val_base.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_val_base.json | no |
| `catalog/weapons/rifle_vpo136.json` | `90EADC5DD9AD35D5` | `Prefabs/Weapons/Rifles/AKM/Rifle_VPO136.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_vpo136.json | no |
| `catalog/weapons/rifle_vsk94.json` | `71D8E1655668CB36` | `Prefabs/Weapons/Rifles/VSK94/Rifle_VSK94.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/weapons/rifle_vsk94_base.json` | `6005623D3AA5F5C2` | `Prefabs/Weapons/Rifles/VSK94/Rifle_VSK94_base.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_vsk94_base.json | no |
| `catalog/weapons/rifle_vss.json` | `F82DF06C1E34128E` | `Prefabs/Weapons/Rifles/VSS/Rifle_VSS.et` | **SOURCE_INTENTIONALLY_ABSENT** | - | no |
| `catalog/weapons/rifle_vss_base.json` | `902A79E4B2A66E63` | `Prefabs/Weapons/Rifles/VSS/Rifle_vss_base.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_rifle_vss_base.json | no |
| `catalog/weapons/shotgun_base.json` | `6C5E2009CDCD0BD3` | `Prefabs/Weapons/Rifles/Shotgun/shotgun_base.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_shotgun_base.json | no |
| `catalog/weapons/slr.json` | `C11ED52EAAF856A8` | `Prefabs/Weapons/Rifles/SLR.et` | **RELOCATED_OR_RENAMED** | catalog/weapons/armst_slr_base.json | no |

## Crosswalk — NEW (candidate file -> classification)

| new path | guid | source resource | classification | <- old (same guid) |
|---|---|---|---|---|
| `catalog/ammunition/armst_ammo_545x39_bp.json` | `6804DD7F189D26F0` | `Prefabs/Weapons/Ammo/Russian/545x39/armst_Ammo_545x39_BP.et` | **SOURCE_ADDED** | - |
| `catalog/ammunition/armst_ammo_545x39_pp.json` | `A6756977E148ABFC` | `Prefabs/Weapons/Ammo/Russian/545x39/armst_Ammo_545x39_PP.et` | **SOURCE_ADDED** | - |
| `catalog/ammunition/armst_ammo_grenade_hedp_m433.json` | `1663496AE5B9F10B` | `Prefabs/Weapons/Ammo/armst_Ammo_Grenade_HEDP_M433.et` | **SOURCE_ADDED** | - |
| `catalog/attachments/armst_bayonet_6kh4.json` | `98C79F5FAE12F9B6` | `Prefabs/Weapons/Attachments/Bayonets/armst_Bayonet_6Kh4.et` | **SOURCE_ADDED** | - |
| `catalog/attachments/armst_bayonet_m9.json` | `558117556F3880A8` | `Prefabs/Weapons/Attachments/Bayonets/armst_Bayonet_M9.et` | **SOURCE_ADDED** | - |
| `catalog/attachments/armst_suppressor_m16.json` | `E52C9791E1554A5F` | `Prefabs/Weapons/Attachments/Muzzle/Suppressor_M16/armst_Suppressor_M16.et` | **SOURCE_ADDED** | - |
| `catalog/attachments/armst_suppressor_pbs4.json` | `5677861A692ED3EB` | `Prefabs/Weapons/Attachments/Muzzle/Suppressor_PBS4/armst_Suppressor_PBS4.et` | **RELOCATED_OR_RENAMED** | catalog/attachments/suppressor_pbs4_base.json |
| `catalog/attachments/armst_ugl_m203_long.json` | `43FDAF3FA0FF2299` | `Prefabs/Weapons/Attachments/Underbarrel/armst_UGL_M203_long.et` | **SOURCE_ADDED** | - |
| `catalog/attachments/armst_ugl_m203_short.json` | `AB268D088F2D6291` | `Prefabs/Weapons/Attachments/Underbarrel/armst_UGL_M203_short.et` | **SOURCE_ADDED** | - |
| `catalog/magazines/armst_box_556x45_m249_200rnd_4ball_1tracer.json` | `06D722FC2666EB83` | `Prefabs/Weapons/Magazines/Western/5x56/Box/armst_Box_556x45_M249_200rnd_4Ball_1Tracer.et` | **SOURCE_ADDED** | - |
| `catalog/magazines/armst_box_762x51_m60_100rnd_4ball_1tracer.json` | `4D2C1E8F3A81F894` | `Prefabs/Weapons/Magazines/Western/762x51/Box/armst_Box_762x51_M60_100rnd_4Ball_1Tracer.et` | **SOURCE_ADDED** | - |
| `catalog/magazines/armst_box_762x54_pk_100rnd_4ball_1tracer.json` | `E5E9C5897CF47F44` | `Prefabs/Weapons/Magazines/Russian/762x54/armst_Box_762x54_PK_100rnd_4Ball_1Tracer.et` | **SOURCE_ADDED** | - |
| `catalog/magazines/armst_box_762x54_uk59_50rnd_4ball_1tracer.json` | `03094E059B554A9C` | `Prefabs/Weapons/Magazines/Western/762x54/armst_Box_762x54_UK59_50rnd_4Ball_1Tracer.et` | **SOURCE_ADDED** | - |
| `catalog/magazines/armst_magazine_545x39_ak_30rnd_bp.json` | `86DDD923A256EDF8` | `Prefabs/Weapons/Magazines/Russian/5x45/AK74/armst_Magazine_545x39_AK_30rnd_BP.et` | **SOURCE_ADDED** | - |
| `catalog/magazines/armst_magazine_545x39_ak_30rnd_pp.json` | `6696D50A89722FCE` | `Prefabs/Weapons/Magazines/Russian/5x45/AK74/armst_Magazine_545x39_AK_30rnd_PP.et` | **SOURCE_ADDED** | - |
| `catalog/magazines/armst_magazine_545x39_rpk_45rnd_bp.json` | `124F7D3880DA92C6` | `Prefabs/Weapons/Magazines/Russian/5x45/AK74/armst_Magazine_545x39_RPK_45rnd_BP.et` | **SOURCE_ADDED** | - |
| `catalog/magazines/armst_magazine_545x39_rpk_45rnd_pp.json` | `6E4C163536579349` | `Prefabs/Weapons/Magazines/Russian/5x45/AK74/armst_Magazine_545x39_RPK_45rnd_PP.et` | **SOURCE_ADDED** | - |
| `catalog/magazines/armst_magazine_762x51_m14_20rnd_bp.json` | `627255315038152A` | `Prefabs/Weapons/Magazines/Western/762x51/M14/armst_Magazine_762x51_M14_20rnd_BP.et` | **SOURCE_ADDED** | - |
| `catalog/magazines/armst_magazine_762x51_m14_20rnd_pp.json` | `C319540BC96AE9BB` | `Prefabs/Weapons/Magazines/Western/762x51/M14/armst_Magazine_762x51_M14_20rnd_PP.et` | **SOURCE_ADDED** | - |
| `catalog/misc/armst_shotgun_ris_mount.json` | `035155F82E11CBFB` | `Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_RIS_Mount.et` | **SOURCE_ADDED** | - |
| `catalog/misc/asphaltpavement_decal_base.json` | `88EA362E7DDB5485` | `Prefabs/Structures/Infrastructure/Pavements/AsphaltPavement_01/AsphaltPavement_Decal_base.et` | **SOURCE_ADDED** | - |
| `catalog/optics/armst_collim_ap2k.json` | `08286DDBB1F33FF1` | `Prefabs/Weapons/Attachments/Optics/Optic_AP2k/armst_Collim_AP2k.et` | **SOURCE_ADDED** | - |
| `catalog/optics/armst_okp.json` | `BC6E5BBC03350708` | `Prefabs/Weapons/Attachments/Optics/AKDovetailMount/Armst_OKP.et` | **SOURCE_ADDED** | - |
| `catalog/optics/armst_optic_4x20.json` | `BD496EE1B40DC510` | `Prefabs/Weapons/Attachments/Optics/Optic_4x20/armst_Optic_4x20.et` | **SOURCE_ADDED** | - |
| `catalog/optics/armst_optic_artii.json` | `D2018EDB1BBF4C88` | `Prefabs/Weapons/Attachments/Optics/Optic_ARTII/armst_Optic_ARTII.et` | **SOURCE_ADDED** | - |
| `catalog/weapons/armst_mgun_m249.json` | `D2B48DEBEF38D7D7` | `Prefabs/Weapons/Western/MachineGuns/armst_mgun_M249.et` | **SOURCE_ADDED** | - |
| `catalog/weapons/armst_mgun_m60.json` | `D182DCDD72BF7E34` | `Prefabs/Weapons/Western/MachineGuns/armst_mgun_M60.et` | **SOURCE_ADDED** | - |
| `catalog/weapons/armst_mgun_uk59.json` | `026CE108BFB3EC03` | `Prefabs/Weapons/Western/MachineGuns/armst_mgun_UK59.et` | **SOURCE_ADDED** | - |
| `catalog/weapons/armst_rifle_m21.json` | `B31929F65F0D0279` | `Prefabs/Weapons/Western/Rifle/M14/armst_Rifle_M21.et` | **SOURCE_ADDED** | - |
| `catalog/weapons/armst_shotgun_mp_133_ris.json` | `9F8CA2FE5A3540DC` | `Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133_Ris.et` | **SOURCE_ADDED** | - |
| `catalog/weapons/armst_smoke_anm8hc.json` | `9DB69176CEF0EE97` | `Prefabs/Weapons/Grenades/armst_Smoke_ANM8HC.et` | **RELOCATED_OR_RENAMED** | catalog/grenades/armst_smoke_anm8hc.json; catalog/grenades/smoke_anm8hc.json |
| `catalog/weapons/armst_smoke_rdg2.json` | `77EAE5E07DC4678A` | `Prefabs/Weapons/Grenades/armst_Smoke_RDG2.et` | **RELOCATED_OR_RENAMED** | catalog/grenades/armst_smoke_rdg2.json; catalog/grenades/smoke_rdg2.json |

## `Prefabs/Weapons/Rifles/` reference split (candidate)

- candidate catalog JSON files containing the string with `base_game_snapshot:` provenance (external/vanilla, legitimate): **44**.
- candidate catalog JSON files containing the string WITHOUT `base_game_snapshot:` (possible scanner-owned internal ref): **0**.

Note: the raw substring count is **not** a defect count; supplied reference indexes and external vanilla paths are expected.

## MP-133 highlight

- deleted `catalog/weapons/armst_mp_133.json` guid=`63FF6FDCA4E7E735` resource=`Prefabs/Weapons/Rifles/Shotgun/armst_mp_133.et` -> **RELOCATED_OR_RENAMED** new=catalog/weapons/armst_shotgun_mp_133.json on_disk=False
- new `catalog/weapons/armst_shotgun_mp_133_ris.json` guid=`9F8CA2FE5A3540DC` resource=`Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133_Ris.et` <- **SOURCE_ADDED** old=-

## Provenance note

`source.resource_guid` is the stable identity; `RELOCATED_OR_RENAMED` is asserted only when the same GUID appears in the candidate. Names are never used to infer identity. `SOURCE_INTENTIONALLY_ABSENT` = the old source resource is no longer on disk; `SCANNER_COVERAGE_OR_BUG` = the source file still exists but is not cataloged. Human review is required before any promotion.

## Tests / checks

- NOT RUN by agent: Workbench/game. `check_repository_integrity.py` locally: NOT RUN (jsonschema missing). Promotion manifest: **not provided for application** pending owner approval.

---

## Committed-HEAD existence check (deleted `SOURCE_INTENTIONALLY_ABSENT`)

Each deleted entry whose source resource is not on disk and whose GUID is not in the
candidate was checked against the **committed HEAD** with
`git -C ARMST-PLATFORM---Weapons cat-file -e HEAD:<resource>` (read-only; live worktree
untouched):

- **30 / 30 are `HEAD_LACKS`** — the old snapshot referenced resources absent from the
  committed addon too (e.g. `Prefabs/Weapons/Rifles/AK74/armst_AKS74UN.et`,
  `…/Groza/armst_groza1.et`, `…/9a91/Rifle_9a91.et`, `…/VSS/Rifle_VSS.et`, several
  `5x45`/`5x56`/`7x62` tracer magazines, several `Prefabs/Weapons/Ammo/…`).
- These deletions are **not** data loss from the current addon and **not** caused by the
  owner's dirty SPAS-12/`.meta` edits.

**MP-133 (owner's example):** old `catalog/weapons/armst_mp_133.json`
(guid `63FF6FDCA4E7E735`, old path `Prefabs/Weapons/Rifles/Shotgun/armst_mp_133.et`) is
**`RELOCATED_OR_RENAMED`** to `catalog/weapons/armst_shotgun_mp_133.json`, proven by the
**same source GUID**. `armst_shotgun_mp_133_ris.json` (`9F8CA2FE5A3540DC`) is
`SOURCE_ADDED`.

## Candidate consistency (isolated copy)

| check | result |
|---|---|
| `check_data_quality.py` | **exit 0** (INFO-only findings) |
| `build_weapon_index.py --check` | **out of date** (exit 1) |
| `build_weapon_family_pages.py --check` | **out of date** (AK_FAMILY/CALIBER_9X39/SHOTGUNS) |
| `build_balance_pages.py --check` | **out of date** (CALIBER_9X39_BALANCE) |

⇒ the scan alone is not a complete promotion set; the derived pages must be regenerated
in the isolated copy and reviewed together.

## Proposed reviewable promotion manifest (PLAN ONLY)

1. `catalog/{10 dirs}/*.json`: replace the generated set; 91 old→new are GUID-proven
   relocations (replace file), 32 new, 169 changed, 30 old files have sources absent at
   HEAD. **Do not delete the 30 until explicitly approved.**
2. Generated indexes (`indexes/*.json`, `indexes/generated_config_reference/…`) and
   generated reports/schemas from the allowlist.
3. Regenerated derived pages: `WEAPON_INDEX.md`, `reports/families/*.md`,
   `reports/balance/*.md`.
4. Preserved byte-identical: `catalog/**/*.et|.conf|.meta` (1,404), hand-authored
   docs, `docs/sync/CURRENT_AI_SYNC.md`, supplied reference indexes.

**Risk ranking:** (1) 30 source-absent deletions require sign-off; (2) 169 changed
entities; (3) 32 new / 29 added sources; (4) derived-page regeneration.
`SCANNER_COVERAGE_OR_BUG = 0`; internal stale scanner refs = 0 (all
`Prefabs/Weapons/Rifles/` occurrences are `base_game_snapshot:`/supplied).

**Publication remains BLOCKED** pending owner review of this crosswalk and manifest.

