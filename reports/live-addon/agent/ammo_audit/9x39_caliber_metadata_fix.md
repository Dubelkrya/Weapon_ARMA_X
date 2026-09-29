# 9x39 Caliber Metadata Fix - SAFETY GATE (READ ONLY)

## Targets (6)
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP5.et` (guid B7EC6D4222AE12BE, 9a91, SP5, cap 20)
- `Prefabs/Weapons/Magazines/Russian/9x39/9a91/armst_Magazine_9x39_20rnd_9a91_SP6.et` (guid 3F47C33B88171646, 9a91, SP6, cap 20)
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_20rnd_vss_SP5.et` (guid 70D023F899C9C226, VSS, SP5, cap 20)
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_20rnd_vss_SP6.et` (guid 51E9CE2EB27B3DBD, VSS, SP6, cap 20)
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_30rnd_val_SP5.et` (guid 6C22F58BBF5D6AED, VAL, SP5, cap inherited)
- `Prefabs/Weapons/Magazines/Russian/9x39/VSS/armst_Magazine_9x39_30rnd_val_SP6.et` (guid 6CBF1E50EB22F09B, VAL, SP6, cap inherited)

## Proven 9x39 value
- PROVEN_9X39_VALUE = **NONE**
- vanilla AmmunitionID keys: AR-AmmunitionID_127x108mm, AR-AmmunitionID_127x99mm, AR-AmmunitionID_145x114mm, AR-AmmunitionID_25x137mm, AR-AmmunitionID_30mm, AR-AmmunitionID_40mm, AR-AmmunitionID_40x46mm, AR-AmmunitionID_545x39mm, AR-AmmunitionID_556x45mm, AR-AmmunitionID_64_105mm, AR-AmmunitionID_66mm, AR-AmmunitionID_68mm, AR-AmmunitionID_70mm, AR-AmmunitionID_72_5mm, AR-AmmunitionID_762x39mm, AR-AmmunitionID_762x51mm, AR-AmmunitionID_762x54mm, AR-AmmunitionID_81mm, AR-AmmunitionID_82mm, AR-AmmunitionID_93mm, AR-AmmunitionID_9x18mm, AR-AmmunitionID_9x19mm
- no 9x39 AmmunitionID key in vanilla or ARMST -> cannot fix with a proven value

## Semantics
- m_sAmmoCaliber is UI/inventory ammo-caliber metadata on MagazineComponent>UIInfo MagazineUIInfo; projectile selection is driven by AmmoConfig {710039458DA9911D} + AmmoMapping (index0 SP5 / index1 SP6), so a label change would not alter ammo behavior.

## Safety gate
- TRIPPED - no proven existing 9x39 caliber metadata value exists (vanilla table has no AR-AmmunitionID_9x39mm; ARMST has no 9x39 AmmunitionID key). Task forbids inventing the key.

## Options for review
- Author a new ARMST caliber key (e.g. #AR-ARMST_AmmunitionID_9x39mm) via a localization task, then reference it.
- Remove the wrong m_sAmmoCaliber field so no incorrect label is shown (needs approval).
- Confirm whether vanilla/another mod defines a 9x39 ammo ID to reuse.

LIVE_FILES_CHANGED: NONE
