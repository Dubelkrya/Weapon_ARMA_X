# RUN NOW — Armst_Work source rescan

This is an execution contract for the local agent. Do not research weapon values, do not redesign authoring policy, and do not edit the addon. Execute the checked-in scanner against the current addon and return the diff for review.

## Fixed inputs

Repository:

`C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X`

Addon — READ ONLY:

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\Armst_Work`

Git branch prepared for this run:

`agent/armst-work-rescan`

Base `main` SHA at task creation:

`091fdc5a0d2beb4f6b567f036e96e00aacd14e13`

Scanner entrypoint and interface are already known from current `main`:

`python agent/scripts/scan_build.py`

Environment variables:

- `MOD_ROOT` = addon root
- `REPO_ROOT` = repository root

Do not invent other CLI flags.

## Agent rules

1. Never write into `Armst_Work`.
2. Do not edit `.et`, `.conf`, `.meta`, `.c`, `.xob`, textures, models or any other addon resource.
3. Do not switch to `agent/resolver-v2` or `agent/weapon-intelligence-v1`.
4. Do not hand-edit generated catalog/index/report counts after the scan.
5. Preserve canonical/manual files unless the task explicitly says otherwise.
6. Scanner output is source/index validation only. It is NOT Workbench/runtime validation.
7. If the repository is dirty before starting, STOP and report the exact dirty paths. Do not stash, discard or overwrite them automatically.
8. If the addon source manifest changes during the run, STOP and report it.

## Protected canonical files

The scan must not silently delete or replace these manual/current artifacts:

- `reports/KNOWLEDGE_STATUS.md`
- `reports/PREFAB_AUTHORING_GUIDE.md`
- `reports/CONFIG_AUTHORING_GUIDE.md`
- `reports/SCRIPT_MODULE_AUTHORING_GUIDE.md`
- `reports/OPTICS_COMPATIBILITY_SYSTEM_V2.md`
- `indexes/script_reference/optic_compatibility_policy_v2.json`
- `schema/compatibility.schema.json`
- `reports/samples/AttachmentOpticsARMST.c`
- `reports/samples/armst_AEK971_test_v12_NAME_DESCRIPTION.et`
- `reports/samples/armst_Optic_PSO1_DovetailRU.et`
- `agent/SAFE_PREFAB_EDITOR.md`
- `agent/RESCAN_ARMST_WORK.md`
- this file

Generated source inventory may contain old engine dovetail types because they exist in source. That does not replace the active gameplay policy `AttachmentOpticsARMST_DovetailRU`.

## Exact execution sequence

Use PowerShell.

```powershell
$Repo = 'C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X'
$Mod  = 'C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\Armst_Work'

Set-Location $Repo

git fetch origin

$dirty = git status --porcelain
if ($dirty) {
    Write-Host 'STOP: repository is dirty before scan'
    $dirty
    exit 10
}

# Use the prepared branch. If it does not yet exist locally, track the remote branch.
$localBranch = git branch --list 'agent/armst-work-rescan'
if ($localBranch) {
    git switch agent/armst-work-rescan
} else {
    git switch --track origin/agent/armst-work-rescan
}

if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$base = git rev-parse HEAD
Write-Host "SCAN BASE: $base"

if (-not (Test-Path $Mod)) {
    Write-Host "STOP: addon root not found: $Mod"
    exit 11
}

# Hash only source text resources that the scanner consumes. This proves the scan did not rewrite them.
$before = Join-Path $env:TEMP 'armst_work_source_before.sha256.txt'
$after  = Join-Path $env:TEMP 'armst_work_source_after.sha256.txt'

Get-ChildItem $Mod -Recurse -File |
    Where-Object { $_.Extension.ToLowerInvariant() -in '.et','.conf','.meta','.c' } |
    Sort-Object FullName |
    ForEach-Object {
        $h = Get-FileHash $_.FullName -Algorithm SHA256
        "{0}  {1}" -f $h.Hash, $_.FullName
    } | Set-Content -Encoding UTF8 $before

$env:MOD_ROOT  = $Mod
$env:REPO_ROOT = $Repo
python agent/scripts/scan_build.py
$scanExit = $LASTEXITCODE
if ($scanExit -ne 0) {
    Write-Host "STOP: scanner exited with code $scanExit"
    exit $scanExit
}

Get-ChildItem $Mod -Recurse -File |
    Where-Object { $_.Extension.ToLowerInvariant() -in '.et','.conf','.meta','.c' } |
    Sort-Object FullName |
    ForEach-Object {
        $h = Get-FileHash $_.FullName -Algorithm SHA256
        "{0}  {1}" -f $h.Hash, $_.FullName
    } | Set-Content -Encoding UTF8 $after

$sourceDiff = Compare-Object (Get-Content $before) (Get-Content $after)
if ($sourceDiff) {
    Write-Host 'STOP: addon source changed during scan'
    $sourceDiff
    exit 12
}

Write-Host 'Addon source hash check: PASS'

Write-Host '--- git status ---'
git status --short

Write-Host '--- diff stat ---'
git diff --stat

Write-Host '--- changed files ---'
git diff --name-status

Write-Host '--- scan state ---'
Get-Content agent/scan_state.json
```

## Acceptance checks

Before committing anything, verify all of the following:

- `agent/scan_state.json` points to `...\addons\Armst_Work`;
- scan completed without parser/runtime exception;
- JSON output files parse;
- addon source hash comparison says PASS;
- no protected canonical file was unexpectedly deleted or rewritten;
- no unexplained mass deletion occurred;
- `reports/KNOWLEDGE_STATUS.md` still states the active authority model;
- DovetailRU v2 policy remains active;
- the AEK V12 and PSO DovetailRU samples remain present;
- TT is not silently regressed to an unresolved state merely because an older source snapshot lacked `Configs(1).zip`.

If any check fails, do not commit generated output. Return `STOP` and the evidence.

## Commit rule

Only if all acceptance checks pass:

```powershell
git add catalog indexes reports schema agent/scan_state.json
```

Then review the staged names before commit:

```powershell
git diff --cached --name-status
```

Do not stage unrelated local files. If the staged set is clean and explainable:

```powershell
git commit -m "Refresh scanner snapshot from Armst_Work"
git push -u origin agent/armst-work-rescan
```

Do not merge to `main`.

## Required return report

Return exactly these facts to the user/reviewer:

- branch;
- base SHA used;
- exact scanner command;
- resolved `MOD_ROOT`;
- scanner exit code;
- source hash check PASS/FAIL;
- old/new entity counts when available;
- warning/error counts;
- changed-file list;
- protected-file status;
- conflicts between generated source inventory and active policy, if any;
- resulting commit SHA if committed;
- final recommendation: `SAFE TO REVIEW` or `STOP`.
