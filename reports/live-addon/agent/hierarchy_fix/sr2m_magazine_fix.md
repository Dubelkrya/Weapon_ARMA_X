# SR-2M Veresk Magazine Setup - SAFETY GATE (READ ONLY)

- resource: `Prefabs/Weapons/Russian/Handguns/Sr_2/armst_SR_2.et`
- SR2 magazine: `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_SR2_30rnd_Ball.et`
- SR2 magazine GUID: 2610CA8D8632DEF4 | capacity 30
- SR2 magazine parent: `{8B853CDD11BA916E}Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball.et`
- SR2 magazine declared well: `MagazineWellPP91 {05B3A6C89A212814}`

## MagazineWellSR2
- defined: Scripts/Gamecode/MagazinePP91.c (class MagazineWellSR2 : BaseMagazineWell)
- resource users: NONE - no prefab/resource anywhere declares `MagazineWell MagazineWellSR2 "{GUID}"`

## MagazineWellPP91 users
- armst_Magazine_9x18_PP91_30rnd_Ball.et (MagazineWellPP91 {05B3A6C89A212814})
- armst_Magazine_9x18_SR2_30rnd_Ball.et (MagazineWellPP91 {05B3A6C89A212814})
- armst_PP91.et (MagazineWellPP91 {26EA67622A1DA48B})
- armst_SR_2.et (MagazineWellPP91 {26EA67622A1DA48B})

## Compatibility proof
- The SR2 magazine declares `MagazineWell MagazineWellPP91 "{05B3A6C89A212814}"` - the SAME well class+instance as the PP91 magazine. It is therefore compatible with MagazineWellPP91, NOT with MagazineWellSR2 (which is class-defined but used by no magazine).

## Decision: DO NOT MODIFY (REVIEW_REQUIRED)
- Requested well change `MagazineWellPP91 -> MagazineWellSR2` is NOT proven: the SR2 magazine uses MagazineWellPP91, and MagazineWellSR2 is unused by any resource. Switching the weapon well would break SR2 magazine compatibility.
- Default magazine template change (PP91 -> SR2) would be compatible (both use MagazineWellPP91) but is not applied because the task bundles it with the unproven well change and its gate says stop when unproven.

LIVE_FILES_CHANGED: NONE
