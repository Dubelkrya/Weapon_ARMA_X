# Description Rewrite Report

## Scope
- Rifles targeted: 19 (1 skipped)
- Magazines targeted: 39

## Result
- Rifles rewritten with ARMST keys: 18
- Magazines rewritten with ARMST keys: 39
- External-parent UIInfo overrides created: rifles 13, magazines 23

## Localization tables
- Language/localization.<locale>.conf for 13 vanilla locales
- Keys: 59 (18 rifle descriptions, 2 fixed names, 39 magazine descriptions)

## Fixed bad keys
- HK G36: M16A2 Name/Description keys removed -> ARMST_Weapon_G36_*
- AK-105: #AR-Weapon_AK74_Name removed -> ARMST_Weapon_AK105_*

## Skipped (REVIEW_REQUIRED)
- armst_Rifle_HKG33.et: model asset Hk3.xob indicates HK G3 (7.62x51); HK33 identity not proven -> not renamed

## Notes
- armst_Rifle_L85.et model asset is L86.xob (L86 LSW); described conservatively as SA80-family
- PP/BP siblings share identical physical description, differing only by the loaded-ammunition suffix

## Safety
- GUID/path/parent/capacity/AmmoConfig/AmmoMapping/ballistics changes: 0
- Gameplay line diff vs backups: 0
- 12ga untouched; AKM tracer absent
- Backups: C:\Users\Muroy\Documents\ARMST_Backups\ARMST-PLATFORM---Weapons\description_rewrite
