# RUN NOW — Armst_Work overlay rescan

This runbook replaces the failed destructive run. The previous STOP proved that `scan_build.py` treats `REPO_ROOT` as an output root and deletes/recreates `catalog/`, `indexes/`, `reports/` and `schema/` under it. Therefore **do not point `REPO_ROOT` at the repository root when scanning `Armst_Work`**.

## Architecture decision

`Armst_Work` is a working overlay addon, not a complete replacement for the historical/base ARMST source snapshot. It contains only a subset of entities and depends on resources outside this addon. Its scan must therefore be stored as a separate overlay snapshot.

Base/canonical repository data remains untouched.

Overlay output root:

`C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X\snapshots\armst_work`

Addon — READ ONLY:

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\Armst_Work`

Branch:

`agent/armst-work-rescan`

Scanner:

`python agent/scripts/scan_build.py`

## Authorized cleanup of the failed run

The previous run started from a clean tree and its report proves that the dirty state was created by the scanner. Cleanup of that failed run is therefore explicitly authorized before retry.

Use PowerShell:

```powershell
$Repo = 'C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X'
$Mod  = 'C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\Armst_Work'
$Out  = Join-Path $Repo 'snapshots\armst_work'

Set-Location $Repo

# Restore tracked files deleted/rewritten by the failed scan.
git restore --source=HEAD --staged --worktree .

# Preview scanner-created untracked files only in the known generated areas.
git clean -fdn -- catalog indexes reports schema agent/scripts/working_tables

# The preview must contain only artifacts from the failed scan. If anything else appears: STOP.
git clean -fd -- catalog indexes reports schema agent/scripts/working_tables

if (git status --porcelain) {
    Write-Host 'STOP: repository is not clean after authorized cleanup'
    git status --short
    exit 20
}

git fetch origin
git pull --ff-only origin agent/armst-work-rescan
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
```

## Source hash guard

```powershell
if (-not (Test-Path $Mod)) {
    Write-Host "STOP: addon root not found: $Mod"
    exit 21
}

$before = Join-Path $env:TEMP 'armst_work_source_before.sha256.txt'
$after  = Join-Path $env:TEMP 'armst_work_source_after.sha256.txt'

Get-ChildItem $Mod -Recurse -File |
    Where-Object { $_.Extension.ToLowerInvariant() -in '.et','.conf','.meta','.c' } |
    Sort-Object FullName |
    ForEach-Object {
        $h = Get-FileHash $_.FullName -Algorithm SHA256
        "{0}  {1}" -f $h.Hash, $_.FullName
    } | Set-Content -Encoding UTF8 $before
```

## Isolated scan

The critical difference from the failed run is `REPO_ROOT = $Out`, not the repository root.

```powershell
# Recreate only the isolated overlay snapshot.
if (Test-Path $Out) {
    Remove-Item $Out -Recurse -Force
}
New-Item -ItemType Directory -Path $Out | Out-Null

$env:MOD_ROOT  = $Mod
$env:REPO_ROOT = $Out

python agent/scripts/scan_build.py
$scanExit = $LASTEXITCODE
if ($scanExit -ne 0) {
    Write-Host "STOP: scanner exited with code $scanExit"
    exit $scanExit
}
```

`scan_build.py` currently writes its debug `working_tables` beside the scanner script rather than under `REPO_ROOT`. That directory is not canonical output. Remove only that generated debug directory after the scan:

```powershell
if (Test-Path (Join-Path $Repo 'agent\scripts\working_tables')) {
    Remove-Item (Join-Path $Repo 'agent\scripts\working_tables') -Recurse -Force
}
```

## Verify addon stayed read-only

```powershell
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
    exit 22
}

Write-Host 'Addon source hash check: PASS'
```

## Acceptance checks

All of these must pass:

1. Repository top-level canonical `catalog/`, `indexes/`, `reports/`, `schema/` are unchanged.
2. Protected authoring guides, DovetailRU policy, AEK V12 sample and PSO sample remain present.
3. `snapshots/armst_work/agent/scan_state.json` records the `Armst_Work` path.
4. Overlay JSON files parse successfully.
5. Source hash check is PASS.
6. The low entity count is accepted as an **overlay fact**, not compared as a replacement for the historical/base 124-entity snapshot.
7. External/unresolved parent/resources are reported as overlay dependencies, not treated as regression by themselves.
8. No file under `Armst_Work` is modified.
9. After removal of `agent/scripts/working_tables`, the only repository changes are under `snapshots/armst_work/`.

Verify:

```powershell
Write-Host '--- repository status ---'
git status --short

Write-Host '--- changed files ---'
git diff --name-status

Write-Host '--- overlay scan state ---'
Get-Content (Join-Path $Out 'agent\scan_state.json')
```

If any changed path lies outside `snapshots/armst_work/`, STOP.

## Commit rule

Only if all acceptance checks pass:

```powershell
git add snapshots/armst_work

git diff --cached --name-status

git commit -m "Add Armst_Work overlay scanner snapshot"
git push -u origin agent/armst-work-rescan
```

Do not merge to `main` automatically.

## Required return report

Return:

- branch;
- commit before scan;
- exact scanner command and environment values;
- resolved `MOD_ROOT` and overlay `REPO_ROOT`;
- scanner exit code;
- source hash PASS/FAIL;
- overlay entity/category counts;
- warning/error counts;
- list of changed repository paths;
- confirmation that no top-level canonical knowledge file changed;
- unresolved/external dependencies found in the overlay;
- resulting commit SHA if committed;
- final recommendation: `SAFE TO REVIEW` or `STOP`.
