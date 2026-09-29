# Western / Eastern Ammo Inventory

Read-only inventory. No files changed.

Western magazines: 13
Eastern magazines: 0

## Western magazines

| Magazine | GUID | Caliber | ET | Ammo config | Source | Parent |
|---|---|---|---|---|---|---|
| `armst_Magazine_762x51_HK3_20_M80_Ball.et` | `6D18CC33708EE713` | 762x51 | True | - | EXTERNAL/VANILLA_PARENT | Prefabs/Weapons/Magazines/Magazine_762x51_M14_20rnd_Base.et |
| `armst_Magazine_762x51_L1A1_20_M61_AP.et` | `5D4E812AEAA7CC1F` | 762x51 | True | - | EXTERNAL/VANILLA_PARENT | Prefabs/Weapons/Magazines/Western/762x51/HK3/L1A1/armst_Magazine_762x51_L1A1_20_M80_Ball.et |
| `armst_Magazine_762x51_L1A1_20_M80_Ball.et` | `AA9A48AAEE6E4F1B` | 762x51 | True | - | EXTERNAL/VANILLA_PARENT | Prefabs/Weapons/Magazines/Magazine_762x51_M14_20rnd_Base.et |
| `armst_Magazine_762x51_L1A1_30_M61_AP.et` | `E70FEC32673242CB` | 762x51 | True | - | EXTERNAL/VANILLA_PARENT | Prefabs/Weapons/Magazines/Western/762x51/HK3/L1A1/armst_Magazine_762x51_L1A1_30_M80_Ball.et |
| `armst_Magazine_762x51_L1A1_30_M80_Ball.et` | `531AA7DB88D84184` | 762x51 | True | - | EXTERNAL/VANILLA_PARENT | Prefabs/Weapons/Magazines/Western/762x51/HK3/L1A1/armst_Magazine_762x51_L1A1_20_M80_Ball.et |
| `Magazine_556x45_HKG36.et` | `969F6FFF810D2145` | 5x56 | True | - | EXTERNAL/VANILLA_PARENT | Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M193_Ball.et |
| `Magazine_556x45_SIG_550.et` | `E3DC6C2FBBE4F825` | 5x56 | True | - | EXTERNAL/VANILLA_PARENT | Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M193_Ball.et |
| `Magazine_9x19_M9_15rnd_Ball.et` | `9C05543A503DB80E` | 9x19 | True | - | EXTERNAL/VANILLA_PARENT | Prefabs/Weapons/Magazines/Magazine_9x19_M9_15rnd_Base.et |
| `Magazine_556x45_STANAG_30rnd_Base.et` | `11B9CC1FB4AEE740` | 5x56 | True | Configs/Weapons/Ammo/Ammo_556x45.conf | EXTERNAL/VANILLA_CONFIG | Prefabs/Weapons/Core/Magazine_Base.et |
| `Magazine_556x45_STANAG_30rnd_M193_Ball.et` | `FB5EB0F6D447E859` | 5x56 | True | - | EXTERNAL/VANILLA_PARENT | Prefabs/Weapons/Magazines/Magazine_556x45_STANAG_30rnd_M193_Ball.et |
| `Magazine_556x45_STANAG_30rnd_M196_Tracer.et` | `4575737B3D3A4505` | 5x56 | False | - | None | - |
| `Magazine_556x45_STANAG_30rnd_M855_Ball.et` | `2EBF60EF24B108FC` | 5x56 | True | - | EXTERNAL/VANILLA_PARENT | Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_Base.et |
| `Magazine_556x45_STANAG_30rnd_M856_Tracer.et` | `A9A385FE1F7BF4BD` | 5x56 | False | - | None | - |

## Eastern weapons and magazines

- `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_SOC94.et` -> [{'path': 'Prefabs/Weapons/Magazines/Russian/7x62/AKM/Magazine_762x39_AKM_10rnd_Ball.et', 'guid': '07805AE177F52646', 'magazine_region': 'RUSSIAN', 'magazine_caliber': '7x62'}]
- `Prefabs/Weapons/Western/Rifle/armst_VZ58P.et` -> no direct magazine ref
- `Prefabs/Weapons/Western/Rifle/armst_VZ58V.et` -> no direct magazine ref

## Local ammo resources

- `Prefabs/Weapons/Ammo/12g/Ammo_12ga.et`
- `Prefabs/Weapons/Ammo/12g/Ammo_12ga_shell.et`
- `Prefabs/Weapons/Ammo/12g/Ammo_12ga_shell_test.et`
- `Prefabs/Weapons/Ammo/12g/Ammo_Buckshot_pellet.et`
- `Prefabs/Weapons/Ammo/Russian/763x25/Ammo_763x25.et`
- `Prefabs/Weapons/Ammo/Russian/763x25/Ammo_763x25_Ball.et`
- `Prefabs/Weapons/Ammo/Russian/9x39/Ammo_9x39_SP5_Ball.et`
- `Prefabs/Weapons/Ammo/Russian/9x39/Ammo_9x39_SP6_Ball.et`
- `Prefabs/Weapons/Ammo/Russian/grenade/Ammo_Grenade_HE_VOG25.et`

## Local ammo configs

- `Configs/Weapons/Ammo/Ammo_12g.conf`
- `Configs/Weapons/Ammo/Ammo_763x25.conf`
- `Configs/Weapons/Ammo/Ammo_9x39.conf`


## Issues

- `MISSING_MAGAZINE_FILE`: {"type": "MISSING_MAGAZINE_FILE", "guid": "4575737B3D3A4505", "path": "Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M196_Tracer.et"}
- `MISSING_MAGAZINE_FILE`: {"type": "MISSING_MAGAZINE_FILE", "guid": "A9A385FE1F7BF4BD", "path": "Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M856_Tracer.et"}
- `MISSING_MAGAZINE_FILE`: {"type": "MISSING_MAGAZINE_FILE", "guid": "FAFA0D71E75CEBE2", "path": "Prefabs/Weapons/Magazines/Russian/7x62/AKM/Magazine_762x39_AKM_30rnd_Tracer.et"}
- `MAGAZINE_MISPLACED`: {"type": "MAGAZINE_MISPLACED", "guid": "6C22F58BBF5D6AED", "expected": "Prefabs/Weapons/Magazines/Russian/9x39/VAL/", "actual": "Prefabs/Weapons/Magazines/Russian/9x39/VSS/"}
- `MAGAZINE_MISPLACED`: {"type": "MAGAZINE_MISPLACED", "guid": "6CBF1E50EB22F09B", "expected": "Prefabs/Weapons/Magazines/Russian/9x39/VAL/", "actual": "Prefabs/Weapons/Magazines/Russian/9x39/VSS/"}
- `PARENT_GUID_MISMATCH`: {"type": "PARENT_GUID_MISMATCH", "resource": "Prefabs/Weapons/Magazines/Western/5x56/STANAG/Magazine_556x45_STANAG_30rnd_M193_Ball.et", "parent_guid": "FB5EB0F6D447E858", "current_local_guid": "FB5EB0F6D447E859"}
