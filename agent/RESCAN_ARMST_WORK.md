# DEPRECATED — Armst_Work rescan task

This task is no longer part of the active project workflow.

Authoritative weapon addon:

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`

`Armst_Work` is not the canonical weapon source and must not be used to replace or refresh the main `catalog/`, `indexes/`, `reports/` or `schema/` knowledge layers.

Do not execute the old Armst_Work rescan workflow unless the user explicitly requests a temporary sandbox/overlay scan.

For normal work, follow:

- `agent/PRIMARY_MOD_POLICY.md`
- `agent/SAFE_PREFAB_EDITOR.md`
- `reports/KNOWLEDGE_STATUS.md`

The earlier failed scan remains useful evidence that `scan_build.py` recreates generated directories under `REPO_ROOT`; therefore never point a partial/sandbox addon at the canonical repository output root.
