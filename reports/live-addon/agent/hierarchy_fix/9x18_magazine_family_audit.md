# 9x18 Magazine Family Audit (PM / APB / PP91 / SR-2M) - READ ONLY

## Identity / inheritance
| mag | guid | parent | well | cap | mapping | mesh |
|---|---|---|---|---|---|---|
| PM | 8B853CDD11BA916E | Prefabs/Weapons/Magazines/Magazine_9x18_PM_8rnd_Base.et | MagazineWellMakarovPM | 8 | None | inherited: {2482E01261AB2FB5}Assets/Weapons/Magazines/PM/Magazine_8rnd_PM.xob |
| APB | 389EB226473CD590 | Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball.et | MagazineWellAPB | 20 | 12 | {FFCF07878591D096}Assets/Apb/APB_magazine.xob |
| PP91 | 4488C415F3CA1890 | Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball.et | MagazineWellPP91 | 30 | 22 | {616109F8BCB6B70E}Assets/Kedr/Kedr_magazine.xob |
| SR2 | 2610CA8D8632DEF4 | Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball.et | MagazineWellPP91 | 30 | 22 | {F2231EA6A4185BF9}Assets/Weapons_RUS/sr2/SR2_mag.xob |

## Inheritance edges
- PM mag -> VANILLA Magazine_9x18_PM_8rnd_Base : **GENERIC_BASE** - capacity 8, MagazineWellMakarovPM, mesh, vanilla defaults
- APB mag -> ARMST PM mag : **VALID_SHARED_BASE** - editor flags (Enabled 0, m_bAutoRegister NEVER, m_bVisible 0, labels), m_bAutoDetectGridSize 0, m_iCustomGridHeight 1; identity/desc keys; capacity/well/mesh/mapping overridden locally
- PP91 mag -> ARMST PM mag : **VALID_SHARED_BASE** - same shared editor/grid metadata; overridden locally where needed
- SR2 mag -> ARMST PM mag : **VALID_SHARED_BASE** - same shared editor/grid metadata; overridden locally

## Well / compatibility matrix
- PM: mag MagazineWellMakarovPM -> weapon MagazineWellMakarovPM (OK)
- APB: mag MagazineWellAPB -> weapon MagazineWellAPB (OK)
- PP91: mag MagazineWellPP91 -> weapon MagazineWellPP91 (OK)
- SR-2M: mag MagazineWellPP91 -> weapon MagazineWellPP91 (OK, intentionally shared)

## Default magazine matrix
- armst_PM: `Prefabs/Weapons/Magazines/Magazine_9x18_PM_8rnd_Ball.et (VANILLA)` (expected `armst_Magazine_9x18_PM_8rnd_Ball.et`) -> DEVIATION
- armst_APB: `...armst_Magazine_9x18_APB_20rnd_Ball.et` (expected `armst_Magazine_9x18_APB_20rnd_Ball.et`) -> MATCH
- armst_PP91: `...armst_Magazine_9x18_PP91_30rnd_Ball.et` (expected `armst_Magazine_9x18_PP91_30rnd_Ball.et`) -> MATCH
- armst_SR_2: `...armst_Magazine_9x18_SR2_30rnd_Ball.et` (expected `armst_Magazine_9x18_SR2_30rnd_Ball.et`) -> MATCH

## Capacity check: PM 8 / APB 20 / PP91 30 / SR2 30 = all match expected

## Deviations / issues
- PM weapon default magazine: Magazine_9x18_PM_8rnd_Ball.et (VANILLA) (expected armst_Magazine_9x18_PM_8rnd_Ball.et)
- SR2 magazine display Name: PP-91 Magazine (expected SR-2M identity)
- AmmoMapping length vs capacity: APB 12 vs 20; PP91 22 vs 30; SR2 22 vs 30 (expected -)
- AmmoConfig: none authored locally on any of the four (expected -)

## AmmoConfig / AmmoMapping
- PM: none local (vanilla inherited)
- APB: mapping 12 entries / MaxAmmo 20
- PP91: mapping 22 entries / MaxAmmo 30
- SR2: mapping 22 entries / MaxAmmo 30

LIVE_FILES_CHANGED: NONE

Note: the incoming task text was truncated after section 6; this audit covers sections 1-6.
