# 9x39 Caliber Metadata Apply

- NEW_KEY: `#AR-ARMST_AmmunitionID_9x39mm`
- EN: 9x39 mm
- RU: 9×39 мм
- SOURCE_KEY_COUNT: 63
- all locales 63 Ids / 63 Texts: True
- identical order: True ; no duplicates: True

## Fixed magazines
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP5.et`: wrong remaining 0, correct 1, only-caliber-line-changed True
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP6.et`: wrong remaining 0, correct 1, only-caliber-line-changed True
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_20rnd_vss_SP5.et`: wrong remaining 0, correct 1, only-caliber-line-changed True
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_20rnd_vss_SP6.et`: wrong remaining 0, correct 1, only-caliber-line-changed True
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_30rnd_val_SP5.et`: wrong remaining 0, correct 1, only-caliber-line-changed True
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_30rnd_val_SP6.et`: wrong remaining 0, correct 1, only-caliber-line-changed True

- WRONG_545X39_METADATA_IN_9X39_MAGS: 0
- CORRECT_9X39_METADATA_REFS: 6
- FIXED_RESOURCE_COUNT: 6
- AMMOCONFIG/MAPPING changes: 0 ; GAMEPLAY_DIFF: 0 ; GUID_CHANGES: 0
- Groza SP5/SP6 magazines untouched

- Groza casing: OPEN_TECHNICAL_DEBT / Casing_762x39_PS.ptc (unchanged)
- Muzzle: INTENTIONAL_SHARED_EFFECT (unchanged)

LIVE_FILES_CHANGED: localization.st + 13 runtime confs + 6 magazines
