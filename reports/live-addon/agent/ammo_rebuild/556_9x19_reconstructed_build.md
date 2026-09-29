# 5.56 + 9x19 Reconstructed PP/BP Build

## Projectiles

| Role | Path | Local GUID | Parent | Delta |
|---|---|---|---|---|
| 556_PP | `Prefabs/Weapons/Ammo/Western/5x56/Ammo_556x45_PP.et` | `62FA6A6363394955` | `Prefabs/Weapons/Ammo/Ammo_556x45_Ball_M855.et` | thin |
| 556_BP | `Prefabs/Weapons/Ammo/Western/5x56/Ammo_556x45_BP.et` | `716F41EFBBB14F9C` | `Prefabs/Weapons/Ammo/Ammo_556x45_Ball_M855.et` | exported M995 delta |
| 9x19_PP | `Prefabs/Weapons/Ammo/Western/9x19/Ammo_9x19_PP.et` | `DFADF7628FAC4A05` | `Prefabs/Weapons/Ammo/Ammo_9x19_HP_JHP.et` | thin |
| 9x19_BP | `Prefabs/Weapons/Ammo/Western/9x19/Ammo_9x19_BP.et` | `9F5580C950084760` | `Prefabs/Weapons/Ammo/Ammo_9x19_AP_7N21.et` | exported 7N31 delta |

## Configs

| Config | GUID | index0 | index1 |
|---|---|---|---|
| `Configs/Weapons/Ammo/ARMST/Ammo_556x45_ARMST.conf` | `5513C2BA0B7B48F8` | `62FA6A6363394955` | `716F41EFBBB14F9C` |
| `Configs/Weapons/Ammo/ARMST/Ammo_9x19_ARMST.conf` | `48496091DE244325` | `DFADF7628FAC4A05` | `9F5580C950084760` |

## Magazines

| Magazine | GUID unchanged | parent unchanged | all-zero mapping |
|---|---|---|---|
| `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_Base.et` | True | True | True |
| `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M193_Ball.et` | True | True | True |
| `Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M855_Ball.et` | True | True | True |
| `Prefabs/Weapons/Magazines/Western/5x56/HKG36/Magazine_556x45_HKG36.et` | True | True | True |
| `Prefabs/Weapons/Magazines/Western/5x56/SIG550/Magazine_556x45_SIG_550.et` | True | True | True |
| `Prefabs/Weapons/Magazines/Western/9x19/M9/Magazine_9x19_M9_15rnd_Ball.et` | True | True | True |

## Exported child deltas

M995 delta over M855: ShellMoveComponent {851AA4A2AE0A5691} -> InitSpeed 1030, DispersionMultiplier 1.03, Mass 0.0034, BallisticTableConfig AIBT_556x45_AP_M995.conf, AirDrag 0.0000035, MushroomingDamageMultiplier 0, PenetrationDepth 12, PenetrationSpeed 926.

7N31 delta over 7N21: ShellMoveComponent {851AA4A2AE0A5691} -> InitSpeed 600, Mass 0.0042, BallisticTableConfig AIBT_9x19_AP_7N31.conf, AirDrag 0.0000149, Diameter 9.2, PenetrationDepth 3.9, PenetrationSpeed 574.

STATUS: PASS

## Global safety

- weapons_found: 32
- weapon_dangling_refs: 0
- parent_guid_differences: 0
- dangling_ammo_refs: 0
- dangling_magazine_refs_introduced: 0
- 762x51_changed: 0
- val_magazines_changed: 0
- akm_tracer_recreated: 0
- 12ga_changed: 0
- 762x39_changed: 0
- backups_inside_active_addon: 2
- backups_inside_active_addon_created_by_this_task: 0
- pre_existing_agent_enfusion_backup_files: 114

