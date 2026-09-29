# 9x18 PP/BP Magazine Layer (applied)

## New magazines
| mag | path | guid | cap | config | effective mapping | well |
|---|---|---|---|---|---|---|
| PM_PP | `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball_PP.et` | 75B5C65F2DA68A01 | 8 | ARMST | 0 x8 | MagazineWellMakarovPM |
| PM_BP | `Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball_BP.et` | 44EF59B51DB21EA9 | 8 | ARMST | 1 x8 | MagazineWellMakarovPM |
| APB_PP | `.../armst_Magazine_9x18_APB_20rnd_Ball.et` | (existing) | 20 | ARMST | 0 x20 | MagazineWellAPB |
| APB_BP | `.../armst_Magazine_9x18_APB_20rnd_Ball_BP.et` | A67F38168B64541A | 20 | ARMST | 1 x20 | MagazineWellAPB |
| PP91_PP | `.../armst_Magazine_9x18_PP91_30rnd_Ball.et` | (existing) | 30 | ARMST | 0 x30 | MagazineWellPP91 |
| PP91_BP | `.../armst_Magazine_9x18_PP91_30rnd_Ball_BP.et` | 318796D9FD213751 | 30 | ARMST | 1 x30 | MagazineWellPP91 |

- ALL_SIX_AMMOCONFIG = `{F2D8D099211C2451}Configs/Weapons/Ammo/armst_Ammo_9x18_ARMST.conf` (all six config_ok=True)
- ALL_SIX_LEN_EQ_CAP = True
- PM default now: `{75B5C65F2DA68A01}Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_PM_8rnd_Ball_PP.et`

## SR-2M safety gate
- SR2 magazine effective: capacity 30, config `{4A7B5486D9167E2A}Ammo_9x18Mak.conf`, mapping 30x0, well MagazineWellPP91, model SR2_mag.xob
- SR2_MAGAZINE_EFFECTIVE_DIFF = 0
- SR2_WEAPON_EFFECTIVE_DIFF = 0

## Safety / integrity
- PM legacy shared mag UNCHANGED (still no AmmoConfig)
- GUID_COLLISIONS = 0 ; DANGLING_REFS = 0 ; new GUID owner counts = 1

## Changed/created
- created: PM_PP, PM_BP, APB_BP, PP91_BP (+metas)
- modified: armst_PM.et (default -> PM PP), APB PP mag (AmmoConfig), PP91 PP mag (AmmoConfig)

LIVE_FILES_CHANGED: 4 new magazines (+metas); 3 existing files modified
