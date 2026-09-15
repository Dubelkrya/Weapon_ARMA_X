# STOP — obsolete Armst_Work rescan runbook

Do not execute this runbook.

Project authority has been corrected: the main weapon addon is

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`

and normal work must target that addon.

`Armst_Work` is only a temporary/sandbox addon when explicitly requested. The previous Armst_Work scan demonstrated useful scanner behavior but is not a canonical refresh path.

If the local repository is still dirty from the earlier failed Armst_Work scan, restore it to the branch HEAD before doing new work, but do not run another Armst_Work canonical rescan.

Return to `main`, pull the latest project policy, and read:

- `agent/PRIMARY_MOD_POLICY.md`
- `agent/SAFE_PREFAB_EDITOR.md`
- `reports/KNOWLEDGE_STATUS.md`
