# Agent entrypoint

For weapon catalog/balance work, read `ai/RULES.md` and `ai/manifest.json` first, then load only the relevant `ai/*.jsonl` shard.

Do not bulk-load legacy `catalog/`, `indexes/`, `reports/`, or `schema/` unless compact data is insufficient. Before editing a game resource, verify the compact value against resolver provenance/raw source.

## Source policy

ARMST is the **frozen source snapshot** for this catalog. Its duplicated resources intentionally preserve the version the mod was built against even if current vanilla changes later.

Operational resolver flow:

`ARMST addon only -> resolver v2 -> derived outputs`

Rules:
- Resolve weapon/base/magazine/ammo/config inheritance only from files physically present inside the ARMST addon.
- Do not use current `$ArmaReforger` or `Imported/VanillaSources` as fallback when building the ARMST catalog.
- Short serialized ARMST paths may be normalized to their unique path inside the same ARMST root.
- If a referenced resource is not present inside ARMST, keep it external/missing; do not silently fill it from current vanilla.
- The Workbench vanilla materializer is a separate utility and is not part of the ARMST catalog resolver path.

Never commit `Imported/VanillaSources` or `agent/v2_output`.
