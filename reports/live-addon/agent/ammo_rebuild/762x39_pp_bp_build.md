# 7.62x39 PP/BP Build

- PP: `Prefabs/Weapons/Ammo/Eastern/762x39/Ammo_762x39_PP.et` GUID `3E395A4A4B0C4F0E` method EXPORTED_DELTA parent Ammo_Bullet_Base `67FED88E5085F63F`
- BP: `Prefabs/Weapons/Ammo/Eastern/762x39/Ammo_762x39_BP.et` GUID `1785D92E5A104937` method EXPORTED_DELTA parent Ammo_Bullet_Base `67FED88E5085F63F`
- Config: `Configs/Weapons/Ammo/ARMST/Ammo_762x39_ARMST.conf` GUID `EA0E25BAF3BD459F`
- Baseline DamageValue: 62.82 -> BP 50.256 (=x0.80)
- Baseline PenetrationDepth: 5.4 -> BP 8.1 (=x1.50)
- Other ballistic fields unchanged

## Magazines

| Magazine | GUID unchanged | parent unchanged | config ok | all-zero mapping |
|---|---|---|---|---|
| `Prefabs/Weapons/Magazines/Russian/7x62/AKM/Magazine_762x39_AKM_10rnd_Ball.et` | True | True | True | True |
| `Prefabs/Weapons/Magazines/Russian/7x62/AKM/Magazine_762x39_AKM_30rnd_Ball.et` | True | True | True | True |

## Validation

{
  "pp_equals_57N231_89": true,
  "bp_differs_only": [
    "DamageValue",
    "PenetrationDepth"
  ],
  "mag_guid_unchanged": true,
  "mag_parent_unchanged": true,
  "mag_config_ok": true,
  "mag_mapping_zero": true,
  "new_projectiles": 2,
  "local_configs": 1,
  "status": "PASS"
}

## Global safety

- weapons_found: 32
- weapon_dangling_refs: 0
- dangling_refs_introduced: 0
- 556_changed: 0
- 762x51_changed: 0
- 9x19_changed: 0
- val_magazines_changed: 0
- akm_tracer_recreated: 0
- akm_tracer_still_absent: True
- 12ga_changed: 0
- manually_invented_source_values: 0
