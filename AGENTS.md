# Agent entrypoint

For weapon catalog/balance work, read `ai/RULES.md` and `ai/manifest.json` first, then load only the relevant `ai/*.jsonl` shard.

Do not bulk-load legacy `catalog/`, `indexes/`, `reports/`, or `schema/` unless compact data is insufficient. Before editing a game resource, verify the compact value against resolver provenance/raw source.

Current architecture: `$ArmaReforger -> Workbench materializer -> Imported/VanillaSources -> resolver v2 -> derived outputs`.

Never commit `Imported/VanillaSources` or `agent/v2_output`.
