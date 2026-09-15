# Weapon_ARMA_X

AI-friendly weapon intelligence catalog and local scanner for the ARMST Arma Reforger weapons addon.

The local addon is the source of truth for current implementation. Real-world research is stored separately and is used to judge what the addon should represent. Gameplay simplifications must be explicit rather than silently replacing real compatibility facts.

## Authoring sources

For new weapon prefabs and modules, use these repository artifacts before inventing or copying values manually:

- `indexes/prefab_authoring/manifest.json` — entrypoint to the full weapon/prefab authoring index generated from `Weapons.zip`.
- `indexes/prefab_authoring/shard_01.json` … `shard_04.json` — parent paths/GUIDs, instance IDs and discovered handling fields.
- `indexes/prefab_authoring_reference.json` — verified canonical component IDs, family baselines, handgun recoil structure and resolved TT source/target separation.
- `indexes/config_reference/manifest.json` — AmmoConfig / AIBallistic / magazine→config→projectile rules from the supplied config snapshot.
- `indexes/script_reference/manifest.json` — script compatibility types, RIS/optic/muzzle/magazine-well authoring model, attachment module inventory and known anomalies.
- `indexes/script_reference/slot_and_sight_summary.json` — resolved weapon-side attachment slot types, representative pivots/default modules and the SightsComponent authoring boundary.
- `indexes/script_reference/optic_compatibility_policy_v2.json` — **active optics gameplay policy** separating researched real compatibility from gameplay compatibility.
- `indexes/script_reference/optic_compatibility_policy_v1.json` — archived strict mount-family proposal kept for analysis/history.
- `reports/PREFAB_AUTHORING_GUIDE.md` — minimal inherited-override rules.
- `reports/CONFIG_AUTHORING_GUIDE.md` — AmmoConfig / AmmoMapping / projectile resolution rules.
- `reports/SCRIPT_MODULE_AUTHORING_GUIDE.md` — general compatibility script, RIS, optic, muzzle, module and sight authoring rules.
- `reports/OPTICS_COMPATIBILITY_SYSTEM_V2.md` — active optics design using `DovetailRU` as an explicit gameplay simplification.
- `reports/samples/AttachmentOpticsARMST.c` — ready-to-copy Enfusion marker script for `AttachmentOpticsARMST_DovetailRU`.
- `reports/samples/armst_TT_authoring_sample_v4.et` — TT example using inherited PM recoil IDs rather than duplicate recoil objects.
- `catalog/weapons/*.json`, `catalog/ammunition/*.json`, `catalog/attachments/*.json` — per-entity facts with provenance.

Resolution priority: **child local block/value > nearest parent > common family base**. If a child contains its own recoil/fire-mode/slot block, that local block wins even when its numeric values still need resolution.

Ammo resolution priority: **magazine AmmoConfig defines the allowed ordered resource list; magazine AmmoMapping defines what is actually loaded**. Mixed magazine counts must come from serialized mapping, not from filenames. Primary kinetic damage stays separate from additive tracer/incendiary effects.

Script/module rule: ARMST's supplied weapon `.c` files are primarily empty compatibility marker types (`MagazineWell*`, `AttachmentMuzzle*`, `AttachmentOptics*`), not per-weapon behavior implementations. `SightsComponent`, ADS, zeroing and sight pivots remain prefab data.

Optic compatibility rule: the engine checks whether the **module type inherits the type required by the weapon slot** (`moduleType.IsInherited(slotType)`). ARMST intentionally groups approved Russian/Soviet side-rail optics and weapons into the gameplay family `DovetailRU`, implemented by `AttachmentOpticsARMST_DovetailRU`. Exact real-world mount/bracket compatibility is preserved separately as `RealCompatibility`. RIS1913/Picatinny and proprietary interfaces such as G36 remain separate.

Authoring rule: keep the parent prefab as the base and override only real differences using inherited instance IDs. Unknown engine values stay unknown.

## Current TT-33 source boundary

`Configs(1).zip` resolves the ARMST TT ammo chain: `Ammo_763x25.conf` allows `Ammo_763x25_Ball.et`, and the TT magazine resolves to 8 rounds through its PM magazine parent. The supplied projectile source sets InitSpeed 430, Mass 0.00804, AirDrag 0.0000125, PenetrationDepth 20 and PenetrationSpeed 355 while inheriting primary kinetic DamageValue 50 from `Ammo_Bullet_Base`. It also references `AIBT_9x19_Ball_M882.conf`; that source fact is preserved rather than silently replaced by real-world Tokarev values.
