# Weapon_ARMA_X

AI-friendly weapon intelligence catalog and local scanner for the ARMST Arma Reforger weapons addon.

The local addon is the source of truth. Repository data is derived analysis/export and must not silently invent missing engine values.

## Prefab authoring source

For new weapon prefabs, use these repository artifacts before inventing or copying values manually:

- `indexes/prefab_authoring/manifest.json` — entrypoint to the full 162-entry authoring index generated from `Weapons.zip`.
- `indexes/prefab_authoring/shard_01.json` … `shard_04.json` — parent paths/GUIDs, instance IDs and discovered handling fields for all indexed weapon-like prefabs/configs.
- `indexes/prefab_authoring_reference.json` — verified canonical component IDs, family baselines, handgun recoil structure and resolved TT source/target separation.
- `reports/PREFAB_AUTHORING_GUIDE.md` — minimal-override rules and a worked TT-33 example.
- `reports/samples/armst_TT_authoring_sample_v4.et` — concrete TT example using inherited PM recoil IDs rather than duplicate recoil objects.
- `catalog/weapons/*.json` — resolved per-weapon facts with `defined_in` / inherited provenance; PM, M9 and TT have been refreshed from the supplied snapshot.

Resolution priority: **child local block/value > nearest parent > common family base**. If a child contains its own recoil/fire-mode block, that local block wins even when its numeric values still need resolution.

Authoring rule: keep the parent prefab as the base and override only real differences using the inherited instance IDs. Unknown engine values stay unknown.
