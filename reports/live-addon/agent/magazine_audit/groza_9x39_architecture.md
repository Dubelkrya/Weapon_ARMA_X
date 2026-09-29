# Groza 9x39 Magazine + Caliber Architecture Audit (READ ONLY)

## Current Groza state
- well: `MagazineWellVZ58_762 {5464E0EAAF7815B4} (7.62x39 - legacy/wrong for 9x39)`
- template: `{48720FC416263FC1}Prefabs/Weapons/Magazines/Russian/7x62/AKM/armst_Magazine_762x39_AKM_30rnd_Ball.et (legacy 7.62x39)`
- casing: `(KEEP)`
- casing particle: `Casing_762x39_PS.ptc`; muzzle: `Muzzle_AK74.ptc` (KEEP)
- MuzzleComponent {CA6BE4D6B867541F}; CaseEjecting {5122AAD190FCA21D}; SCR_MuzzleEffect {C9B3271BB22CDB68}

## Groza_mag model
- `Assets/Weapons_RUS/Groza/Groza_mag.xob` guid `9889FE707F31F4A2`; users: NONE

## Existing 9x39 family
- config `Configs/Weapons/Ammo/armst_Ammo_9x39.conf` [index0 SP5, index1 SP6]
- VAL 30rnd SP5/SP6: well MagazineWell9x39, model val_magazine, mapping 30x0 / 30x1
- VSS 20rnd SP5/SP6: well MagazineWell9x39, MaxAmmo 20, model vss_magazine
- proven well class: `MagazineWell9x39` (Scripts/Gamecode/Magazine9x39.c); weapon users armst_Rifle_val_base / armst_Rifle_vss_base

## Capacity
- PROVEN_CAPACITY = **UNKNOWN** (no local evidence; do not assume real-world)

## Casing
- no dedicated 9x39/VSS/VAL casing particle exists -> AMBIGUOUS
- reassessment of previous fix: `Casing_762x39_PS.ptc` = **WRONG_FOR_9x39** (previous task changed 762x51 -> 762x39; neither is 9x39)

## Required weapon changes (future)
- A_MagazineWell: MagazineWellVZ58_762 -> MagazineWell9x39 [PROVEN_FIX] 
- B_default_MagazineTemplate: legacy 7.62x39 -> dedicated 9x39 Groza magazine (SP5) [AMBIGUOUS] capacity UNKNOWN; no Groza 9x39 magazine prefab exists
- C_casing_particle: Casing_762x39_PS -> dedicated 9x39 casing [AMBIGUOUS] no proven 9x39 casing particle exists
- D_caliber_refs: none on weapon; note VAL/VSS mags carry wrong m_sAmmoCaliber #AR-AmmunitionID_545x39mm [AMBIGUOUS] 
- muzzle: KEEP / INTENTIONAL_SHARED_EFFECT

## Proposed magazines (conditional, not finalized)
- `armst_Magazine_9x39_Groza_<capacity>rnd_SP5.et` / `armst_Magazine_9x39_Groza_<capacity>rnd_SP6.et` (capacity unknown)
- model Groza_mag.xob; well MagazineWell9x39; config armst_Ammo_9x39.conf; SP5 all0 / SP6 all1

LIVE_FILES_CHANGED: NONE
