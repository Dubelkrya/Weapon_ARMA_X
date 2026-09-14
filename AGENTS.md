# Agent entrypoint

For weapon catalog/balance work, read `ai/RULES.md` and `ai/manifest.json` first, then load only the relevant `ai/*.jsonl` shard.

Do not bulk-load legacy `catalog/`, `indexes/`, `reports/`, or `schema/` unless compact data is insufficient. Before editing a game resource, verify the compact value against resolver provenance/raw source.

## Source and editing policy

ARMST contains the duplicated sources used by our mod and is the **only editable game-resource root**. Some ARMST duplicates still inherit from vanilla resources, so current/materialized vanilla must remain available to the resolver as **read-only inheritance/reference context**.

Operational resolver flow:

`ARMST editable sources + read-only materialized vanilla -> resolver v2 -> derived outputs`

Rules:
- Catalog entities are exported from ARMST only.
- Start weapon/base/magazine/ammo/config resolution from ARMST resources.
- Follow actual inheritance/dependency references into materialized vanilla when ARMST still inherits from vanilla.
- Vanilla is evidence/reference only: never edit, patch, rewrite, or propose resource changes under `Imported/VanillaSources` or `$ArmaReforger`.
- All game-resource corrections and balance changes belong in the ARMST addon.
- Preserve provenance so every effective value says whether it was defined in ARMST or inherited from vanilla.
- Short serialized ARMST paths may be normalized only when they resolve unambiguously.
- If a reference is absent from both ARMST and materialized vanilla, keep it external/missing rather than inventing a value.

Never commit `Imported/VanillaSources` or `agent/v2_output`.
