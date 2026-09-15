# Weapon_ARMA_X

AI-friendly weapon intelligence catalog and local scanner for the ARMST Arma Reforger weapons addon.

The local addon is the source of truth. Repository data is derived analysis/export and must not silently invent missing engine values.

## Prefab authoring source

For new weapon prefabs, use these repository artifacts before inventing or copying values manually:

- `indexes/prefab_authoring_reference.json` — verified inheritance/component IDs, family baselines, handgun recoil structure and provenance derived from the supplied `Weapons.zip` snapshot.
- `reports/PREFAB_AUTHORING_GUIDE.md` — minimal-override rules and worked TT-33 example.
- `catalog/weapons/*.json` — resolved per-weapon facts with `defined_in` / inherited provenance.

Authoring rule: keep the parent prefab as the base and override only real differences using the inherited instance IDs. Unknown engine values stay unknown.
