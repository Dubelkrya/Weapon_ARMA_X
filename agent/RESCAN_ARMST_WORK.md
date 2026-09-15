# Local task — scan Armst_Work as an overlay snapshot

## Purpose

Capture the **current working addon** `Armst_Work` without replacing the historical/base ARMST scanner snapshot or deleting canonical authoring knowledge.

Current addon root:

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\Armst_Work`

Repository working copy:

`C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X`

Overlay output root:

`C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X\snapshots\armst_work`

## Why this is an overlay, not a replacement

A controlled scan on 2026-09-15 proved that `Armst_Work` contains only a subset of the resources represented by the older ARMST source snapshot: 25 entities versus 124 in the older scan, with many dependencies resolving outside the working addon.

The existing scanner deletes/recreates `catalog/`, `indexes/`, `reports/` and `schema/` under `REPO_ROOT`. Pointing `REPO_ROOT` at the repository root therefore destroys unrelated canonical/manual knowledge. That run was correctly rejected and not committed.

From now on:

- top-level `catalog/`, `indexes/`, `reports/`, `schema/` remain the base/canonical knowledge layer;
- `snapshots/armst_work/` is the scanner-generated working-overlay layer;
- overlay entities may reference external/base resources that are not present inside `Armst_Work`;
- an overlay scan must never be interpreted as a complete replacement inventory.

## Safety boundary

The addon is READ ONLY.

Never modify any file under `Armst_Work` during a scan.

Do not point scanner `REPO_ROOT` at the repository root for this task.

Do not switch to experimental resolver branches merely to perform the scan.

## Scanner invocation

The checked-in scanner interface is:

```powershell
$env:MOD_ROOT  = 'C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\Armst_Work'
$env:REPO_ROOT = 'C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X\snapshots\armst_work'
python agent/scripts/scan_build.py
```

The scanner's debug `agent/scripts/working_tables` directory is not canonical output and may be removed after the run if it was generated.

## Required checks

Before accepting an overlay snapshot, verify:

- source hashes for consumed `.et/.conf/.meta/.c` files are unchanged before/after;
- `snapshots/armst_work/agent/scan_state.json` records `Armst_Work` as `mod_root`;
- JSON output parses;
- only `snapshots/armst_work/` is staged for the snapshot commit;
- no top-level canonical file under `catalog/`, `indexes/`, `reports/`, `schema/` was changed by the scan;
- Workbench-validated guides/samples and active gameplay policies remain untouched;
- unresolved external parents/references are reported as overlay dependencies rather than silently guessed;
- no Workbench/runtime claim is inferred from scanner success.

## Acceptance interpretation

A lower entity count than the base snapshot is expected and is not itself a failure. `Armst_Work` is an overlay.

A mass deletion of top-level base/canonical knowledge is always a failure.

## Review

Run the scan on a dedicated branch, currently `agent/armst-work-rescan`.

Commit only the isolated overlay directory after review. Do not merge automatically to `main`.

For the exact current retry procedure, use `agent/RUN_NOW_ARMST_WORK_RESCAN.md` on the rescan branch.
