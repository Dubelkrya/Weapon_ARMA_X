# Local task — refresh knowledge snapshot from Armst_Work

## Purpose

Regenerate scanner-derived catalogs/indexes/reports from the **current working addon**, replacing the stale scanner snapshot that was built from `ARMST-PLATFORM---Weapons`.

Current addon root:

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\Armst_Work`

Repository working copy:

`C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X`

## Safety boundary

This task is a **read-only scan of the addon**. Do not modify any file under `Armst_Work`.

Generated repository outputs may be rewritten only by the scanner pipeline. Do not hand-edit generated JSON/catalog counts to make them look current.

Before running:

1. Ensure repository working tree is clean or record every pre-existing local change.
2. Create a Git branch from current `main`, suggested name: `agent/armst-work-rescan`.
3. Record current `main` SHA.
4. Confirm the addon root exists exactly at the path above.
5. Confirm the scanner command/options from the checked-in scanner script rather than guessing CLI flags.

## Scan

Use the repository scanner pipeline with the addon root set to `Armst_Work`.

The existing committed snapshot used `agent/scripts/scan_build.py`. If its interface has changed locally, use the checked-in script/interface that actually owns the generated `catalog/`, `indexes/`, `reports/` and `agent/scan_state.json` outputs.

Do not switch to an experimental resolver branch merely to perform this refresh. Experimental branches are reviewed separately.

## Required checks before accepting output

Verify at minimum:

- `agent/scan_state.json` records `Armst_Work` as `mod_root`;
- scan date is current;
- parser/inheritance/reference stages report completion;
- generated JSON parses successfully;
- no source file under `Armst_Work` was modified;
- no unexplained large deletion of canonical authoring guides/samples/schema occurred;
- `reports/KNOWLEDGE_STATUS.md`, `reports/PREFAB_AUTHORING_GUIDE.md`, active optics v2 policy and current Workbench samples are preserved;
- generated source inventory is not allowed to overwrite active gameplay policy documents;
- old built-in dovetail types found in source prefabs remain source facts, while active policy remains `AttachmentOpticsARMST_DovetailRU`;
- TT supplemental `Configs(1).zip` resolution is not regressed to the stale unresolved claim without source evidence.

## Diff review

Separate the diff into:

1. generated snapshot changes caused by `Armst_Work`;
2. unexpected changes;
3. manual/canonical files that should not have been touched.

If category 2 or 3 contains unexplained changes, stop and do not merge.

## Report

Return:

- branch name;
- base/main SHA;
- exact scanner command used;
- resolved addon root;
- counts before/after;
- warnings/errors;
- list of generated files changed;
- confirmation `Armst_Work` was read-only;
- any conflicts between new source inventory and canonical active policies;
- recommendation: safe to review/merge or STOP.

Do not claim Workbench/runtime validation from this scan. This task refreshes source/index knowledge only.
