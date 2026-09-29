# Weapon Inheritance Trees

Direction: child -> parent.
└─ Grenade_Base.et | GUID D7EB24176E5CEAA6 | role BASE | physical `Prefabs/Weapons/Core/Grenade_Base.et` | parent Prefabs/Weapons/Core/Throw_Base.et [EXTERNAL_UNAVAILABLE]

└─ Weapon_Base.et | GUID E1F14DB52DBFBC57 | role BASE | physical `Prefabs/Weapons/Core/Weapon_Base.et` | parent NONE [ROOT]
   └─ Rifle_Base.et | GUID 911D6C8DC7BA2D63 | role BASE | physical `Prefabs/Weapons/Core/Rifle_Base.et` | parent Prefabs/Weapons/Core/Weapon_Base.et [LOCAL_RESOLVED]
      ├─ armst_Rifle_AKM_base.et | GUID 140E94F473B60FE3 | role BASE | physical `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et` | parent Prefabs/Weapons/Core/Rifle_Base.et [LOCAL_RESOLVED]
      │  ├─ armst_Rifle_AKM.et | GUID 5BFF97EFD0BF6D9F | role INTERMEDIATE | physical `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM.et` | parent Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et [LOCAL_RESOLVED]
      │  │  └─ armst_Rifle_AKM_full.et | GUID 33BEE1A93C920B26 | role LEAF | physical `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_full.et` | parent Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM.et [LOCAL_RESOLVED]
      │  ├─ armst_Rifle_AKMS.et | GUID 5712F6F88A014F0B | role LEAF | physical `Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKMS.et` | parent Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et [LOCAL_RESOLVED]
      │  ├─ armst_Rifle_SOC94.et | GUID E394112ABBC198D8 | role LEAF | physical `Prefabs/Weapons/Rifles/AKM/armst_Rifle_SOC94.et` | parent Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et [LOCAL_RESOLVED]
      │  └─ armst_Rifle_VPO136.et | GUID 90EADC5DD9AD35D5 | role LEAF | physical `Prefabs/Weapons/Rifles/AKM/armst_Rifle_VPO136.et` | parent Prefabs/Weapons/Rifles/AKM/armst_Rifle_AKM_base.et [LOCAL_RESOLVED]
      ├─ armst_Groza_base.et | GUID 903C7920F00AB654 | role BASE | physical `Prefabs/Weapons/Rifles/Groza/armst_Groza_base.et` | parent Prefabs/Weapons/Core/Rifle_Base.et [LOCAL_RESOLVED]
      └─ armst_Rifle_hk_g36.et | GUID A802C718201D72DF | role LEAF | physical `Prefabs/Weapons/Rifles/armst_Rifle_hk_g36.et` | parent Prefabs/Weapons/Core/Rifle_Base.et [LOCAL_RESOLVED]

└─ armst_Handgun_Knife_base.et | GUID 26ADE11C416B3840 | role BASE | physical `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et` | parent Prefabs/Weapons/Core/Handgun_Base.et [EXTERNAL_UNAVAILABLE]

└─ armst_M9.et | GUID 1353C6EAD1DCFE43 | role LEAF | physical `Prefabs/Weapons/Handguns/armst_M9.et` | parent Prefabs/Weapons/Handguns/M9/Handgun_M9_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_PM.et | GUID C0F7DD85A86B2900 | role INTERMEDIATE | physical `Prefabs/Weapons/Handguns/armst_PM.et` | parent Prefabs/Weapons/Handguns/PM/Handgun_PM_base.et [EXTERNAL_UNAVAILABLE]
   ├─ armst_APB.et | GUID 5D3DA7E84135B278 | role LEAF | physical `Prefabs/Weapons/Handguns/armst_APB.et` | parent Prefabs/Weapons/Handguns/armst_PM.et [LOCAL_RESOLVED]
   ├─ armst_PP91.et | GUID 3968B2A856852CBD | role INTERMEDIATE | physical `Prefabs/Weapons/Handguns/armst_PP91.et` | parent Prefabs/Weapons/Handguns/armst_PM.et [LOCAL_RESOLVED]
   │  └─ armst_SR_2.et | GUID 31FB2EC4F4AFFC05 | role LEAF | physical `Prefabs/Weapons/Handguns/armst_SR_2.et` | parent Prefabs/Weapons/Handguns/armst_PP91.et [LOCAL_RESOLVED]
   └─ armst_TT.et | GUID 0D469F42B65E350E | role LEAF | physical `Prefabs/Weapons/Handguns/armst_TT.et` | parent Prefabs/Weapons/Handguns/armst_PM.et [LOCAL_RESOLVED]

└─ armst_PKM.et | GUID A89BC9D55FFB4CD8 | role LEAF | physical `Prefabs/Weapons/MachineGuns/armst_PKM.et` | parent Prefabs/Weapons/MachineGuns/PKM/MG_PKM_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_RPK74.et | GUID A7AF84C6C58BA3E8 | role LEAF | physical `Prefabs/Weapons/MachineGuns/armst_RPK74.et` | parent Prefabs/Weapons/MachineGuns/RPK74/MG_RPK74_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_Rifle_9a91_base.et | GUID E2D8F39AE1B9B8F1 | role BASE | physical `Prefabs/Weapons/Rifles/9a91/armst_Rifle_9a91_base.et` | parent Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_AK74.et | GUID FA5C25BF66A53DCF | role INTERMEDIATE | physical `Prefabs/Weapons/Rifles/AK74/armst_AK74.et` | parent Prefabs/Weapons/Rifles/AK74/Rifle_AK74_long_base.et [EXTERNAL_UNAVAILABLE]
   └─ armst_AK105.et | GUID 6FC3151D0DED22A9 | role LEAF | physical `Prefabs/Weapons/Rifles/AK74/armst_AK105.et` | parent Prefabs/Weapons/Rifles/AK74/armst_AK74.et [LOCAL_RESOLVED]

└─ armst_AK74N.et | GUID 96DFD2E7E63B3386 | role INTERMEDIATE | physical `Prefabs/Weapons/Rifles/AK74/armst_AK74N.et` | parent Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et [EXTERNAL_UNAVAILABLE]
   ├─ armst_AK74M.et | GUID 5B8E766C0E3C13EE | role INTERMEDIATE | physical `Prefabs/Weapons/Rifles/AK74/armst_AK74M.et` | parent Prefabs/Weapons/Rifles/AK74/armst_AK74N.et [LOCAL_RESOLVED]
   │  └─ armst_AK74M_full.et | GUID 63892659A632A0FD | role LEAF | physical `Prefabs/Weapons/Rifles/AK74/armst_AK74M_full.et` | parent Prefabs/Weapons/Rifles/AK74/armst_AK74M.et [LOCAL_RESOLVED]
   └─ armst_AKS.et | GUID 25A64724FD416989 | role LEAF | physical `Prefabs/Weapons/Rifles/AK74/armst_AKS.et` | parent Prefabs/Weapons/Rifles/AK74/armst_AK74N.et [LOCAL_RESOLVED]

└─ armst_AKS74U.et | GUID BFEA719491610A45 | role LEAF | physical `Prefabs/Weapons/Rifles/AK74/armst_AKS74U.et` | parent Prefabs/Weapons/Rifles/AKS74U/Rifle_AKS74U_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_AKS74UN.et | GUID FA0E25CE35EE945F | role LEAF | physical `Prefabs/Weapons/Rifles/AK74/armst_AKS74UN.et` | parent Prefabs/Weapons/Rifles/AKS74U/Rifle_AKS74UN_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_shotgun_base.et | GUID 6C5E2009CDCD0BD3 | role BASE | physical `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et` | parent Prefabs/Weapons/Rifles/M14/Rifle_M21.et [EXTERNAL_UNAVAILABLE]
   ├─ armst_Remington_870.et | GUID 6DBEF115AA35E404 | role LEAF | physical `Prefabs/Weapons/Rifles/Shotgun/armst_Remington_870.et` | parent Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et [LOCAL_RESOLVED]
   ├─ armst_izh_27.et | GUID 57F153EFAD34E1CA | role LEAF | physical `Prefabs/Weapons/Rifles/Shotgun/armst_izh_27.et` | parent Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et [LOCAL_RESOLVED]
   ├─ armst_mp_133.et | GUID 63FF6FDCA4E7E735 | role LEAF | physical `Prefabs/Weapons/Rifles/Shotgun/armst_mp_133.et` | parent Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et [LOCAL_RESOLVED]
   ├─ armst_mp_153.et | GUID 92DB80A098AABF1C | role LEAF | physical `Prefabs/Weapons/Rifles/Shotgun/armst_mp_153.et` | parent Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et [LOCAL_RESOLVED]
   ├─ armst_spas_12.et | GUID 221AED80163B7C60 | role LEAF | physical `Prefabs/Weapons/Rifles/Shotgun/armst_spas_12.et` | parent Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et [LOCAL_RESOLVED]
   └─ armst_toz_66.et | GUID 923B067A74826419 | role INTERMEDIATE | physical `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66.et` | parent Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et [LOCAL_RESOLVED]
      ├─ armst_toz_66_pantera.et | GUID A9B143751CB07F45 | role LEAF | physical `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_pantera.et` | parent Prefabs/Weapons/Rifles/Shotgun/armst_toz_66.et [LOCAL_RESOLVED]
      └─ armst_toz_66_saw.et | GUID 9C7C3BE87956383A | role LEAF | physical `Prefabs/Weapons/Rifles/Shotgun/armst_toz_66_saw.et` | parent Prefabs/Weapons/Rifles/Shotgun/armst_toz_66.et [LOCAL_RESOLVED]

└─ armst_Rifle_val_base.et | GUID F25D16BD5F748372 | role BASE | physical `Prefabs/Weapons/Rifles/VAL/armst_Rifle_val_base.et` | parent Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_Rifle_VSK94_base.et | GUID 6005623D3AA5F5C2 | role BASE | physical `Prefabs/Weapons/Rifles/VSK94/armst_Rifle_VSK94_base.et` | parent Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_Rifle_vss_base.et | GUID 902A79E4B2A66E63 | role BASE | physical `Prefabs/Weapons/Rifles/VSS/armst_Rifle_vss_base.et` | parent Prefabs/Weapons/Rifles/AK74/Rifle_AK74_short_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_AEK971_test_v11.et | GUID AC198EAC9BDD9841 | role LEAF | physical `Prefabs/Weapons/Rifles/armst_AEK971_test_v11.et` | parent Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_Rifle_M16A2.et | GUID 3E413771E1834D2F | role INTERMEDIATE | physical `Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et` | parent Prefabs/Weapons/Rifles/M16/Rifle_M16A2_base.et [EXTERNAL_UNAVAILABLE]
   ├─ armst_Rifle_HKG33.et | GUID 035CFC7DD44455D0 | role LEAF | physical `Prefabs/Weapons/Rifles/armst_Rifle_HKG33.et` | parent Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et [LOCAL_RESOLVED]
   ├─ armst_Rifle_L85.et | GUID 45D3FCA77AF1709B | role LEAF | physical `Prefabs/Weapons/Rifles/armst_Rifle_L85.et` | parent Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et [LOCAL_RESOLVED]
   ├─ armst_Rifle_Sig550.et | GUID CA3BEBAADDFAF1DE | role LEAF | physical `Prefabs/Weapons/Rifles/armst_Rifle_Sig550.et` | parent Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et [LOCAL_RESOLVED]
   └─ armst_SLR.et | GUID C11ED52EAAF856A8 | role LEAF | physical `Prefabs/Weapons/Rifles/armst_SLR.et` | parent Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et [LOCAL_RESOLVED]

└─ armst_Rifle_M16A2_carbine.et | GUID F97A4AC994231900 | role LEAF | physical `Prefabs/Weapons/Rifles/armst_Rifle_M16A2_carbine.et` | parent Prefabs/Weapons/Rifles/M16/Rifle_M16A2_carbine_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_SVD.et | GUID 3EB02CDAD5F23C82 | role LEAF | physical `Prefabs/Weapons/Rifles/armst_SVD.et` | parent Prefabs/Weapons/Rifles/SVD/Rifle_SVD_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_VZ58P.et | GUID 9C948630078D154D | role LEAF | physical `Prefabs/Weapons/Rifles/armst_VZ58P.et` | parent Prefabs/Weapons/Rifles/VZ58/Rifle_VZ58_base.et [EXTERNAL_UNAVAILABLE]

└─ armst_VZ58V.et | GUID 443CEFF17E040B11 | role LEAF | physical `Prefabs/Weapons/Rifles/armst_VZ58V.et` | parent Prefabs/Weapons/Rifles/VZ58/Rifle_VZ58_base.et [EXTERNAL_UNAVAILABLE]

