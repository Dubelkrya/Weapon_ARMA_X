# Interrupted Weapon Move Forensic

READ ONLY. No recovery, rollback, or retry performed.

## First Touched Resource

- resource: `Prefabs/Weapons/Handguns/armst_APB.et`
- GUID: `5D3DA7E84135B278`
- old path: `Prefabs/Weapons/Handguns/armst_APB.et`
- new path: `Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB.et`
- ET location now: `Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB.et`
- META location now: `Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB.et.meta`
- exact meta content:
```text
MetaFileClass {
 Name "{5D3DA7E84135B278}Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB.et"
 Configurations {
  EntityTemplateResourceClass PC {
  }
  EntityTemplateResourceClass XBOX_ONE : PC {
  }
  EntityTemplateResourceClass XBOX_SERIES : PC {
  }
  EntityTemplateResourceClass PS4 : PC {
  }
  EntityTemplateResourceClass PS5 : PC {
  }
  EntityTemplateResourceClass HEADLESS : PC {
  }
 }
}
```

## Transaction States

### UNTOUCHED (7)
- `Prefabs/Weapons/MachineGuns/armst_PKM.et`
- `Prefabs/Weapons/MachineGuns/armst_RPK74.et`
- `Prefabs/Weapons/Rifles/AK74/armst_AK105.et`
- `Prefabs/Weapons/Rifles/AK74/armst_AKS74U.et`
- `Prefabs/Weapons/Rifles/AK74/armst_AKS74UN.et`
- `Prefabs/Weapons/Rifles/armst_Rifle_M16A2_carbine.et`
- `Prefabs/Weapons/Rifles/armst_Rifle_Sig550.et`

### PARTIAL_REFERENCE_UPDATE (25)
- `Prefabs/Weapons/Handguns/armst_APB.et`
- `Prefabs/Weapons/Handguns/armst_M9.et`
- `Prefabs/Weapons/Handguns/armst_SR_2.et`
- `Prefabs/Weapons/Handguns/armst_TT.et`
- `Prefabs/Weapons/Rifles/AK74/armst_AK74M_full.et`
- `Prefabs/Weapons/Rifles/AK74/armst_AKS.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKMS.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_full.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_SOC94.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_VPO136.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_Remington_870.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_izh_27.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_mp_133.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_mp_153.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_spas_12.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_pantera.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_saw.et`
- `Prefabs/Weapons/Rifles/armst_AEK971_test_v11.et`
- `Prefabs/Weapons/Rifles/armst_Rifle_HKG33.et`
- `Prefabs/Weapons/Rifles/armst_Rifle_L85.et`
- `Prefabs/Weapons/Rifles/armst_Rifle_hk_g36.et`
- `Prefabs/Weapons/Rifles/armst_SLR.et`
- `Prefabs/Weapons/Rifles/armst_SVD.et`
- `Prefabs/Weapons/Rifles/armst_VZ58P.et`
- `Prefabs/Weapons/Rifles/armst_VZ58V.et`

## Reference Forensics

- old identity refs remaining: 0
- new identity refs present: 28
- plain old path occurrences: 1
- plain new path occurrences: 28

New identity references:
- `Prefabs/Weapons/Handguns/armst_TT.et.meta` -> `{0D469F42B65E350E}Prefabs/Weapons/Russian/Handguns/armst_TT/armst_TT.et`
- `Prefabs/Weapons/Rifles/armst_Rifle_L85.et.meta` -> `{45D3FCA77AF1709B}Prefabs/Weapons/Western/Rifles/armst_Rifle_L85/armst_Rifle_L85.et`
- `Prefabs/Weapons/Rifles/armst_SVD.et.meta` -> `{3EB02CDAD5F23C82}Prefabs/Weapons/Russian/Rifles/armst_SVD/armst_SVD.et`
- `Prefabs/Weapons/Rifles/armst_VZ58P.et.meta` -> `{9C948630078D154D}Prefabs/Weapons/Eastern/Rifles/armst_VZ58P/armst_VZ58P.et`
- `Prefabs/Weapons/Rifles/armst_VZ58V.et.meta` -> `{443CEFF17E040B11}Prefabs/Weapons/Eastern/Rifles/armst_VZ58V/armst_VZ58V.et`
- `Prefabs/Weapons/Rifles/AK74/armst_AK74M_full.et.meta` -> `{63892659A632A0FD}Prefabs/Weapons/Russian/Rifles/armst_AK74M_full/armst_AK74M_full.et`
- `Prefabs/Weapons/Rifles/AK74/armst_AKS.et.meta` -> `{25A64724FD416989}Prefabs/Weapons/Russian/Rifles/armst_AKS/armst_AKS.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKMS.et.meta` -> `{5712F6F88A014F0B}Prefabs/Weapons/Russian/Rifles/armst_Rifle_AKMS/armst_Rifle_AKMS.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_full.et.meta` -> `{33BEE1A93C920B26}Prefabs/Weapons/Russian/Rifles/armst_Rifle_AKM_full/armst_Rifle_AKM_full.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_SOC94.et.meta` -> `{E394112ABBC198D8}Prefabs/Weapons/Eastern/Rifles/armst_Rifle_SOC94/armst_Rifle_SOC94.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_VPO136.et.meta` -> `{90EADC5DD9AD35D5}Prefabs/Weapons/Russian/Rifles/armst_Rifle_VPO136/armst_Rifle_VPO136.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_izh_27.et.meta` -> `{57F153EFAD34E1CA}Prefabs/Weapons/Russian/Shotguns/armst_izh_27/armst_izh_27.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_mp_133.et.meta` -> `{63FF6FDCA4E7E735}Prefabs/Weapons/Russian/Shotguns/armst_mp_133/armst_mp_133.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_mp_153.et.meta` -> `{92DB80A098AABF1C}Prefabs/Weapons/Russian/Shotguns/armst_mp_153/armst_mp_153.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_Remington_870.et.meta` -> `{6DBEF115AA35E404}Prefabs/Weapons/Western/Shotguns/armst_Remington_870/armst_Remington_870.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_spas_12.et.meta` -> `{221AED80163B7C60}Prefabs/Weapons/Russian/Shotguns/armst_spas_12/armst_spas_12.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_pantera.et.meta` -> `{A9B143751CB07F45}Prefabs/Weapons/Russian/Shotguns/armst_toz_66_pantera/armst_toz_66_pantera.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_saw.et.meta` -> `{9C7C3BE87956383A}Prefabs/Weapons/Russian/Shotguns/armst_toz_66_saw/armst_toz_66_saw.et`
- `Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB.et.meta` -> `{5D3DA7E84135B278}Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `{5D3DA7E84135B278}Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `{1353C6EAD1DCFE43}Prefabs/Weapons/Western/Handguns/armst_M9/armst_M9.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `{31FB2EC4F4AFFC05}Prefabs/Weapons/Russian/Handguns/armst_SR_2/armst_SR_2.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `{0D469F42B65E350E}Prefabs/Weapons/Russian/Handguns/armst_TT/armst_TT.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `{AC198EAC9BDD9841}Prefabs/Weapons/Russian/Rifles/armst_AEK971_test_v11/armst_AEK971_test_v11.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `{035CFC7DD44455D0}Prefabs/Weapons/Western/Rifles/armst_Rifle_HKG33/armst_Rifle_HKG33.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `{45D3FCA77AF1709B}Prefabs/Weapons/Western/Rifles/armst_Rifle_L85/armst_Rifle_L85.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `{A802C718201D72DF}Prefabs/Weapons/Western/Rifles/armst_Rifle_hk_g36/armst_Rifle_hk_g36.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `{C11ED52EAAF856A8}Prefabs/Weapons/Western/Rifles/armst_SLR/armst_SLR.et`

Dangling new identity references (target resource not yet moved):
- `Prefabs/Weapons/Handguns/armst_TT.et.meta` -> `Prefabs/Weapons/Russian/Handguns/armst_TT/armst_TT.et`
- `Prefabs/Weapons/Rifles/armst_Rifle_L85.et.meta` -> `Prefabs/Weapons/Western/Rifles/armst_Rifle_L85/armst_Rifle_L85.et`
- `Prefabs/Weapons/Rifles/armst_SVD.et.meta` -> `Prefabs/Weapons/Russian/Rifles/armst_SVD/armst_SVD.et`
- `Prefabs/Weapons/Rifles/armst_VZ58P.et.meta` -> `Prefabs/Weapons/Eastern/Rifles/armst_VZ58P/armst_VZ58P.et`
- `Prefabs/Weapons/Rifles/armst_VZ58V.et.meta` -> `Prefabs/Weapons/Eastern/Rifles/armst_VZ58V/armst_VZ58V.et`
- `Prefabs/Weapons/Rifles/AK74/armst_AK74M_full.et.meta` -> `Prefabs/Weapons/Russian/Rifles/armst_AK74M_full/armst_AK74M_full.et`
- `Prefabs/Weapons/Rifles/AK74/armst_AKS.et.meta` -> `Prefabs/Weapons/Russian/Rifles/armst_AKS/armst_AKS.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKMS.et.meta` -> `Prefabs/Weapons/Russian/Rifles/armst_Rifle_AKMS/armst_Rifle_AKMS.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_full.et.meta` -> `Prefabs/Weapons/Russian/Rifles/armst_Rifle_AKM_full/armst_Rifle_AKM_full.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_SOC94.et.meta` -> `Prefabs/Weapons/Eastern/Rifles/armst_Rifle_SOC94/armst_Rifle_SOC94.et`
- `Prefabs/Weapons/Rifles/AKM/armst_Rifle_VPO136.et.meta` -> `Prefabs/Weapons/Russian/Rifles/armst_Rifle_VPO136/armst_Rifle_VPO136.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_izh_27.et.meta` -> `Prefabs/Weapons/Russian/Shotguns/armst_izh_27/armst_izh_27.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_mp_133.et.meta` -> `Prefabs/Weapons/Russian/Shotguns/armst_mp_133/armst_mp_133.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_mp_153.et.meta` -> `Prefabs/Weapons/Russian/Shotguns/armst_mp_153/armst_mp_153.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_Remington_870.et.meta` -> `Prefabs/Weapons/Western/Shotguns/armst_Remington_870/armst_Remington_870.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_spas_12.et.meta` -> `Prefabs/Weapons/Russian/Shotguns/armst_spas_12/armst_spas_12.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_pantera.et.meta` -> `Prefabs/Weapons/Russian/Shotguns/armst_toz_66_pantera/armst_toz_66_pantera.et`
- `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_saw.et.meta` -> `Prefabs/Weapons/Russian/Shotguns/armst_toz_66_saw/armst_toz_66_saw.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `Prefabs/Weapons/Western/Handguns/armst_M9/armst_M9.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `Prefabs/Weapons/Russian/Handguns/armst_SR_2/armst_SR_2.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `Prefabs/Weapons/Russian/Handguns/armst_TT/armst_TT.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `Prefabs/Weapons/Russian/Rifles/armst_AEK971_test_v11/armst_AEK971_test_v11.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `Prefabs/Weapons/Western/Rifles/armst_Rifle_HKG33/armst_Rifle_HKG33.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `Prefabs/Weapons/Western/Rifles/armst_Rifle_L85/armst_Rifle_L85.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `Prefabs/Weapons/Western/Rifles/armst_Rifle_hk_g36/armst_Rifle_hk_g36.et`
- `worlds/Weapon_test/weapon_test_Layers/default.layer` -> `Prefabs/Weapons/Western/Rifles/armst_SLR/armst_SLR.et`

## Meta Format Audit

- `Prefabs/Weapons/Handguns/armst_M9.et.meta` | GUID `1353C6EAD1DCFE43` | Name `Prefabs/Weapons/Handguns/M9/Handgun_M9.et` | Name field `True`
- `Prefabs/Weapons/Handguns/armst_SR_2.et.meta` | GUID `31FB2EC4F4AFFC05` | Name `Handguns/New_armst_Veresk_SR_@.et` | Name field `True`
- `Prefabs/Weapons/Rifles/armst_Rifle_AEK971_test_v11.et.meta` | GUID `None` | Name `None` | Name field `False`

## Global Damage Check

- duplicate live GUID owners: NONE
- missing ET/meta pairs: not introduced for untouched resources; APB pair exists at target.
- old/new path coexistence: APB target only; other targets absent.
- core resources changed by transaction: NONE detected.

## Recovery

- classification: `MANUAL_REPAIR_REQUIRED`
- reason: APB pair moved, but the global reference pass updated identity references for resources whose pairs were not moved; those target paths are dangling. No backup was created before abort.
- no rollback or resume executed.

FILES_CHANGED_BY_THIS_INSPECTION: NONE
