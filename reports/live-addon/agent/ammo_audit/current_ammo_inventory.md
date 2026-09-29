# Canonical Ammo + Magazine Audit

Read-only audit. No ballistics changed.

## Summary

- live_ammo_resources: 17
- gameplay_projectiles: 16
- projectile_bases: 0
- test_projectiles: 1
- ammo_configs: 7
- gameplay_magazines: 39
- pp_bp_pairs_expected: 10
- pp_bp_pairs_valid: 20
- pp_magazines_loading_pp: 10
- bp_magazines_loading_bp: 10
- mapping_out_of_range: 0
- unresolved_external_config: 8
- projectiles_used: 14
- config_only_projectiles: 0
- referenced_non_magazine_projectiles: 1
- orphan_projectiles: 2

## Projectiles

| name | guid | class | role | usage | membership | magazines |
|---|---|---|---|---|---|---|
| `armst_Ammo_12ga.et` | `862E8EB633CED07D` | GAMEPLAY_PROJECTILE | UNKNOWN | USED | 1 | 3 |
| `armst_Ammo_12ga_shell.et` | `9F7537128778361F` | GAMEPLAY_PROJECTILE | UNKNOWN | USED | 1 | 1 |
| `armst_Ammo_12ga_shell_test.et` | `9A2EC4D810705428` | TEST | UNKNOWN | USED | 1 | 1 |
| `armst_Ammo_Buckshot_pellet.et` | `8A45841AC9BA3AE7` | GAMEPLAY_PROJECTILE | Buckshot | REFERENCED_NON_MAGAZINE | 0 | 0 |
| `armst_Ammo_762x39_BP.et` | `1785D92E5A104937` | GAMEPLAY_PROJECTILE | BP | USED | 1 | 2 |
| `armst_Ammo_762x39_PP.et` | `3E395A4A4B0C4F0E` | GAMEPLAY_PROJECTILE | PP | USED | 1 | 2 |
| `armst_Ammo_763x25.et` | `8221593DFA48E4B3` | GAMEPLAY_PROJECTILE | UNKNOWN | ORPHAN | 0 | 0 |
| `armst_Ammo_763x25_Ball.et` | `5AE7AF31B9D7EB6C` | GAMEPLAY_PROJECTILE | Ball | USED | 1 | 1 |
| `armst_Ammo_9x39_SP5_Ball.et` | `2CB8EAD4A52F3290` | GAMEPLAY_PROJECTILE | Ball | USED | 1 | 3 |
| `armst_Ammo_9x39_SP6_Ball.et` | `FB468B29C75FE46A` | GAMEPLAY_PROJECTILE | Ball | USED | 1 | 3 |
| `armst_Ammo_Grenade_HE_VOG25.et` | `262F0D09C4130826` | GAMEPLAY_PROJECTILE | Grenade | ORPHAN | 0 | 0 |
| `armst_Ammo_556x45_BP.et` | `716F41EFBBB14F9C` | GAMEPLAY_PROJECTILE | BP | USED | 1 | 4 |
| `armst_Ammo_556x45_PP.et` | `62FA6A6363394955` | GAMEPLAY_PROJECTILE | PP | USED | 1 | 5 |
| `armst_Ammo_762x51_BP.et` | `647D4F418F9F4655` | GAMEPLAY_PROJECTILE | BP | USED | 1 | 3 |
| `armst_Ammo_762x51_PP.et` | `8FAC2EB7CA474E5E` | GAMEPLAY_PROJECTILE | PP | USED | 1 | 3 |
| `armst_Ammo_9x19_BP.et` | `9F5580C950084760` | GAMEPLAY_PROJECTILE | BP | USED | 1 | 1 |
| `armst_Ammo_9x19_PP.et` | `DFADF7628FAC4A05` | GAMEPLAY_PROJECTILE | PP | USED | 1 | 1 |

## PP/BP pairs validation

- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/armst_Magazine_762x39_AKM_10rnd_Ball.et` | map 0 0 0 0 0  | loaded [(0, '3E395A4A4B0C4F0E')]
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/armst_Magazine_762x39_AKM_10rnd_Ball_BP.et` | map 1 1 1 1 1  | loaded [(1, '1785D92E5A104937')]
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/armst_Magazine_762x39_AKM_30rnd_Ball.et` | map 0 0 0 0 0  | loaded [(0, '3E395A4A4B0C4F0E')]
- `Prefabs/Weapons/Magazines/Russian/7x62/AKM/armst_Magazine_762x39_AKM_30rnd_Ball_BP.et` | map 1 1 1 1 1  | loaded [(1, '1785D92E5A104937')]
- `Prefabs/Weapons/Magazines/Western/5x56/HKG36/armst_Magazine_556x45_HKG36.et` | map 0 0 0 0 0  | loaded [(0, '62FA6A6363394955')]
- `Prefabs/Weapons/Magazines/Western/5x56/HKG36/armst_Magazine_556x45_HKG36_BP.et` | map 1 1 1 1 1  | loaded [(1, '716F41EFBBB14F9C')]
- `Prefabs/Weapons/Magazines/Western/5x56/SIG550/armst_Magazine_556x45_SIG_550.et` | map 0 0 0 0 0  | loaded [(0, '62FA6A6363394955')]
- `Prefabs/Weapons/Magazines/Western/5x56/SIG550/armst_Magazine_556x45_SIG_550_BP.et` | map 1 1 1 1 1  | loaded [(1, '716F41EFBBB14F9C')]
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/armst_Magazine_556x45_STANAG_30rnd_M193_Ball.et` | map 0 0 0 0 0  | loaded [(0, '62FA6A6363394955')]
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/armst_Magazine_556x45_STANAG_30rnd_M193_Ball_BP.et` | map 1 1 1 1 1  | loaded [(1, '716F41EFBBB14F9C')]
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/armst_Magazine_556x45_STANAG_30rnd_M855_Ball.et` | map 0 0 0 0 0  | loaded [(0, '62FA6A6363394955')]
- `Prefabs/Weapons/Magazines/Western/5x56/STANAG/armst_Magazine_556x45_STANAG_30rnd_M855_Ball_BP.et` | map 1 1 1 1 1  | loaded [(1, '716F41EFBBB14F9C')]
- `Prefabs/Weapons/Magazines/Western/762x51/HK3/armst_Magazine_762x51_HK3_20_M80_Ball.et` | map 0 0 0 0 0  | loaded [(0, '8FAC2EB7CA474E5E')]
- `Prefabs/Weapons/Magazines/Western/762x51/HK3/armst_Magazine_762x51_HK3_20_M80_Ball_BP.et` | map 1 1 1 1 1  | loaded [(1, '647D4F418F9F4655')]
- `Prefabs/Weapons/Magazines/Western/762x51/L1A1/armst_Magazine_762x51_L1A1_20_M80_Ball.et` | map 0 0 0 0 0  | loaded [(0, '8FAC2EB7CA474E5E')]
- `Prefabs/Weapons/Magazines/Western/762x51/L1A1/armst_Magazine_762x51_L1A1_20_M80_Ball_BP.et` | map 1 1 1 1 1  | loaded [(1, '647D4F418F9F4655')]
- `Prefabs/Weapons/Magazines/Western/762x51/L1A1/armst_Magazine_762x51_L1A1_30_M80_Ball.et` | map 0 0 0 0 0  | loaded [(0, '8FAC2EB7CA474E5E')]
- `Prefabs/Weapons/Magazines/Western/762x51/L1A1/armst_Magazine_762x51_L1A1_30_M80_Ball_BP.et` | map 1 1 1 1 1  | loaded [(1, '647D4F418F9F4655')]
- `Prefabs/Weapons/Magazines/Western/9x19/M9/armst_Magazine_9x19_M9_15rnd_Ball.et` | map 0 0 0 0 0  | loaded [(0, 'DFADF7628FAC4A05')]
- `Prefabs/Weapons/Magazines/Western/9x19/M9/armst_Magazine_9x19_M9_15rnd_Ball_BP.et` | map 1 1 1 1 1  | loaded [(1, '9F5580C950084760')]

## Special states

- STANAG Base PP: inheritance-only, no BP sibling.
- Deleted redundant/legacy resources remain absent.
- VAL magazines untouched.
