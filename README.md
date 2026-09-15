# Weapon_ARMA_X

AI-friendly weapon intelligence catalog and local scanner for the ARMST Arma Reforger weapons addon.

The local addon is the source of truth. Repository data is derived analysis/export and must not silently invent missing engine values.

## Prefab authoring source

For new weapon prefabs, use these repository artifacts before inventing or copying values manually:

- `indexes/prefab_authoring/manifest.json` — entrypoint to the full 162-entry authoring index generated from `Weapons.zip`.
- `indexes/prefab_authoring/shard_01.json` … `shard_04.json` — parent paths/GUIDs, instance IDs and discovered handling fields for indexed weapon-like prefabs/configs.
- `indexes/prefab_authoring_reference.json` — verified canonical component IDs, family baselines, handgun recoil structure and resolved TT source/target separation.
- `indexes/config_reference/manifest.json` — entrypoint for the `Configs.zip` layer: 11 AmmoConfig files, 80 AIBallistic configs and the magazine→config→projectile resolution rules.
- `indexes/config_reference/ammo_configs.json` — exact ordered `AmmoResourceArray` entries. Array order is significant because `AmmoMapping` stores indexes into this list.
- `indexes/config_reference/key_magazine_mappings.json` — source-resolved PM/M9/RPK/PKM mapping examples; demonstrates that allowed ammunition and loaded ammunition are different concepts.
- `indexes/config_reference/aiballistic_inventory.json` — inventory of the 80 supplied AIBallistic configs. A matching name is not permission to replace a projectile's actual `BallisticTableConfig`.
- `reports/PREFAB_AUTHORING_GUIDE.md` — minimal-override rules and a worked TT-33 example.
- `reports/CONFIG_AUTHORING_GUIDE.md` — AmmoConfig / AmmoMapping / projectile resolution rules and TT-33 config exception.
- `reports/samples/armst_TT_authoring_sample_v4.et` — TT example using inherited PM recoil IDs rather than duplicate recoil objects.
- `catalog/weapons/*.json` and `catalog/ammunition/*.json` — per-entity resolved facts with provenance. Source-backed projectile/config fields are materialized here when resolved.

Resolution priority: **child local block/value > nearest parent > common family base**. If a child contains its own recoil/fire-mode block, that local block wins even when its numeric values still need resolution.

Ammo resolution priority: **magazine AmmoConfig defines the allowed ordered resource list; magazine AmmoMapping defines what is actually loaded**. Mixed magazine counts must come from the serialized mapping, not from the filename. Primary kinetic damage stays separate from additive tracer/incendiary effects.

Authoring rule: keep the parent prefab as the base and override only real differences using inherited instance IDs. Unknown engine values stay unknown.

## Current TT-33 boundary

`Configs.zip` contains no 7.63×25 / 7.62×25 magazine config. Therefore `Ammo_763x25.conf` and the TT projectile chain remain ARMST-local and unresolved by the vanilla config snapshot. Do not substitute a 9×18, 9×19, or other vanilla config.
