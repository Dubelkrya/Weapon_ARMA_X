# 9x18 PP/BP Architecture Plan (READ ONLY)

## Current ammo state
- config: `{4A7B5486D9167E2A}Configs/Weapons/Ammo/Ammo_9x18Mak.conf`
- AmmoResourceArray: {4DE72DF927310A8B}Prefabs/Weapons/Ammo/Ammo_9x18_Ball_57N181.et
- Ball_57N181: thin child of Ammo_Bullet_Base (AIBT_9x18_Ball_57N181)
- AP_7N25: child of Ammo_Bullet_Base; InitSpeed 490 / Mass 0.0036 / AirDrag 0.0000115 / Diam 9.27 / PenDepth 5 / PenSpeed 490

## Canonical 9x19 pattern (reference)
- projectile: Prefabs/Weapons/Ammo/Western/9x19/armst_Ammo_9x19_PP.et (child of {9DA944F4D6A611BA}Ammo_9x19_HP_JHP.et; ID only)
- projectile: Prefabs/Weapons/Ammo/Western/9x19/armst_Ammo_9x19_BP.et (child of {7687761020B01947}Ammo_9x19_AP_7N21.et; ShellMove overrides)
- config: Configs/Weapons/Ammo/ARMST/armst_Ammo_9x19_ARMST.conf
- magazines: armst_Magazine_9x19_M9_15rnd_Ball.et (PP), armst_Magazine_9x19_M9_15rnd_Ball_BP.et (BP)
- convention: {"parent": "both siblings parent to Magazine_9x19_M9_15rnd_Base.et (not PP->BP)", "component": "MagazineComponent {CA6BE4D6B4DAFD69}", "AmmoConfig": "ARMST config on both", "AmmoMapping": "plain (no +), full length == capacity; PP all 0, BP all 1", "instance": "MagazineComponent {CA6BE4D6B4DAFD69} reused on both"}

## Proposed layer
- armst_Ammo_9x18_PP.et <- Prefabs/Weapons/Ammo/Ammo_9x18_Ball_57N181.et (new ID only (thin child) - mirror 9x19 PP) [HIGH]
- armst_Ammo_9x18_BP.et <- Prefabs/Weapons/Ammo/Ammo_9x18_AP_7N25.et (new ID only; AP_7N25 already carries BP ballistics (PenDepth 5) - or explicit overrides if project wants BP deltas) [HIGH]
- config armst_Ammo_9x18_ARMST.conf: index0 PP, index1 BP

## Proposed magazines
- PM PP: armst_Magazine_9x18_PM_8rnd_Ball.et (existing, modify AmmoConfig -> ARMST; mapping stays all 0)
- PM BP: armst_Magazine_9x18_PM_8rnd_Ball_BP.et (NEW; parent vanilla PM base; plain AmmoMapping 8x1)
- APB PP: armst_Magazine_9x18_APB_20rnd_Ball.et (existing, modify AmmoConfig -> ARMST; mapping 20x0)
- APB BP: armst_Magazine_9x18_APB_20rnd_Ball_BP.et (NEW; plain AmmoMapping 20x1)
- PP91 PP: armst_Magazine_9x18_PP91_30rnd_Ball.et (existing, modify AmmoConfig -> ARMST; mapping 30x0)
- PP91 BP: armst_Magazine_9x18_PP91_30rnd_Ball_BP.et (NEW; plain AmmoMapping 30x1)

## Mapping plan
- PM_PP: 8x0 (inherited 8x0 or local +8x0)
- PM_BP: plain 8x1
- APB_PP: 8 base +12 append = 20x0
- APB_BP: plain 20x1
- PP91_PP: 8 base +22 append = 30x0
- PP91_BP: plain 30x1
- rule_note: BP siblings must use plain AmmoMapping (full length) to override the inherited base zeros; PP can keep all-zero mapping.

## SR-2M
- SR2M_CALIBER_REVIEW_REQUIRED (excluding from 9x18 PP/BP implementation)

## Implementation set
### PROJECTILES_TO_CREATE
- armst_Ammo_9x18_PP.et
- armst_Ammo_9x18_BP.et
### CONFIGS_TO_CREATE
- armst_Ammo_9x18_ARMST.conf
### MAGAZINES_TO_CREATE
- armst_Magazine_9x18_PM_8rnd_Ball_BP.et
- armst_Magazine_9x18_APB_20rnd_Ball_BP.et
- armst_Magazine_9x18_PP91_30rnd_Ball_BP.et
### MAGAZINES_TO_MODIFY
- armst_Magazine_9x18_PM_8rnd_Ball.et
- armst_Magazine_9x18_APB_20rnd_Ball.et
- armst_Magazine_9x18_PP91_30rnd_Ball.et
### EXISTING_RESOURCES_TO_KEEP
- Ammo_9x18_Ball_57N181.et
- Ammo_9x18_AP_7N25.et
- Ammo_9x18Mak.conf
- armst_Magazine_9x18_SR2_30rnd_Ball.et (SR2M separate)

LIVE_FILES_CHANGED: NONE
