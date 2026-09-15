# STUDY AND SYNC — primary ARMST weapon mod

## Goal

Study the authoritative ARMST weapon addon deeply and synchronize repository knowledge from it without damaging canonical/manual knowledge.

Authoritative addon root:

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`

Repository:

`C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X`

Prepared branch:

`agent/primary-mod-knowledge-sync`

This task is not a gameplay rebalance task and not a prefab-edit task. The addon is READ ONLY for this pass.

## Authority

Read first:

- `agent/PRIMARY_MOD_POLICY.md`
- `reports/KNOWLEDGE_STATUS.md`
- `agent/SAFE_PREFAB_EDITOR.md`
- `reports/PREFAB_AUTHORING_GUIDE.md`
- `reports/CONFIG_AUTHORING_GUIDE.md`
- `reports/SCRIPT_MODULE_AUTHORING_GUIDE.md`
- `reports/OPTICS_COMPATIBILITY_SYSTEM_V2.md`
- `reports/AMMO_AP_BP_POLICY.md`

Do not replace active gameplay policy with raw source facts. Raw source inventory and active project policy are separate layers.

## Important scanner behavior

`agent/scripts/scan_build.py` deletes/recreates `catalog/`, `indexes/`, `reports/` and `schema/` under `REPO_ROOT`.

Therefore DO NOT run the scanner with `REPO_ROOT` equal to the repository root.

Use an isolated candidate snapshot first:

`C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X\snapshots\primary_candidate`

Only after review may selected generated data be synchronized into canonical generated areas.

## Phase 0 — clean state and source guard

Use PowerShell.

```powershell
$Repo = 'C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X'
$Mod  = 'C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons'
$Out  = Join-Path $Repo 'snapshots\primary_candidate'

Set-Location $Repo

git fetch origin

git switch agent/primary-mod-knowledge-sync
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

git pull --ff-only origin agent/primary-mod-knowledge-sync
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$dirty = git status --porcelain
if ($dirty) {
    Write-Host 'STOP: repository dirty before primary study'
    $dirty
    exit 10
}

if (-not (Test-Path $Mod)) {
    Write-Host "STOP: primary addon not found: $Mod"
    exit 11
}

$before = Join-Path $env:TEMP 'armst_primary_before.sha256.txt'
$after  = Join-Path $env:TEMP 'armst_primary_after.sha256.txt'

Get-ChildItem $Mod -Recurse -File |
    Where-Object { $_.Extension.ToLowerInvariant() -in '.et','.conf','.meta','.c' } |
    Sort-Object FullName |
    ForEach-Object {
        $h = Get-FileHash $_.FullName -Algorithm SHA256
        "{0}  {1}" -f $h.Hash, $_.FullName
    } | Set-Content -Encoding UTF8 $before
```

Record:
- source file count;
- branch HEAD;
- current canonical `agent/scan_state.json` counts;
- exact addon path.

## Phase 1 — isolated full scan

Remove only an old candidate snapshot, never top-level canonical knowledge:

```powershell
if (Test-Path $Out) {
    Remove-Item $Out -Recurse -Force
}
New-Item -ItemType Directory -Path $Out | Out-Null

$env:MOD_ROOT  = $Mod
$env:REPO_ROOT = $Out
python agent/scripts/scan_build.py
$scanExit = $LASTEXITCODE
if ($scanExit -ne 0) {
    Write-Host "STOP: scanner exit $scanExit"
    exit $scanExit
}
```

Then source guard:

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
    Write-Host 'STOP: primary addon changed during read-only study'
    $sourceDiff
    exit 12
}
```

Required result: source hash check PASS.

## Phase 2 — deep study beyond scanner counts

Do not stop at generated entity counts. Inspect the addon and produce a knowledge delta report covering at least:

### Weapons
- all weapon prefab families;
- parent/inheritance chains;
- WeaponComponent and nested component structure;
- FireModes and exact inherited/local instance IDs;
- recoil/sway structure and provenance;
- weight and physical attributes;
- magazine wells/templates;
- muzzle/underbarrel/optic attachment slots;
- sights and zeroing boundaries;
- UI name/description placement;
- animation references where visible.

### Ammunition
- every AmmoConfig in the mod;
- ordered `AmmoResourceArray`;
- every projectile referenced by those configs;
- projectile inheritance;
- `DamageValue` and provenance;
- `PenetrationDepth`, `PenetrationSpeed`, `PenetrationDensity` where present;
- InitSpeed, Mass, Diameter, AirDrag;
- actually referenced ballistic table;
- tracer/incendiary/additive effects separate from primary kinetic damage;
- magazine `AmmoMapping` and loaded-resource mapping.

For the current AP/BP gameplay project, identify candidate pairs per caliber but DO NOT modify ammunition and DO NOT present gameplay classification as real-world cartridge fact.

### Scripts/modules/compatibility
- MagazineWell marker classes;
- muzzle attachment marker classes;
- optic attachment marker classes;
- weapon-side slot requested type;
- module-side `WeaponAttachmentAttributes.AttachmentType`;
- raw built-in/source types versus active ARMST gameplay policy;
- current presence/absence of `AttachmentOpticsARMST_DovetailRU` in the primary mod.

### Optics
- PSO and other Russian/Soviet side-rail prefabs;
- inheritance and exact module-side IDs;
- module compatibility types;
- physical/sight mechanics kept distinct from compatibility.

### Known project control points
Specifically verify source-side presence/structure for:
- AEK-971, if present in the primary mod;
- PSO-1 / DovetailRU resources, if present;
- TT / 7.63x25 chain;
- 9x39 SP5/SP6;
- 5.45x39;
- 5.56x45;
- 7.62x39;
- 7.62x51;
- 7.62x54R;
- 9x18;
- 9x19;
- 12.7x99, 12.7x108, 14.5x114, 25x137 if present in configs/resources.

## Phase 3 — compare candidate snapshot with canonical knowledge

Compare:

- `snapshots/primary_candidate/catalog/` vs `catalog/`
- `snapshots/primary_candidate/indexes/` vs `indexes/`
- candidate scan state vs `agent/scan_state.json`
- candidate reports/schema vs canonical generated equivalents where applicable.

Classify every meaningful difference as one of:

1. source changed and canonical generated knowledge is stale;
2. scanner extraction difference/limitation;
3. manual policy knowledge — must be preserved, not overwritten;
4. unresolved/external dependency;
5. new anomaly requiring review.

Do not bulk-copy candidate `reports/` or `schema/` over manual canonical files.

## Phase 4 — synchronization rules

You MAY synchronize source-backed generated data only when the delta is explainable and provenance is retained.

Preferred safe sync targets:
- `catalog/` entity JSONs;
- generated inventory indexes such as `indexes/weapons.json`, `indexes/magazines.json`, `indexes/ammunition.json`, `indexes/attachments.json`, `indexes/optics.json`;
- scanner-owned reference graph/state/scan summary, after review.

DO NOT overwrite these manual/current artifacts from scanner output:
- `reports/KNOWLEDGE_STATUS.md`
- `reports/PREFAB_AUTHORING_GUIDE.md`
- `reports/CONFIG_AUTHORING_GUIDE.md`
- `reports/SCRIPT_MODULE_AUTHORING_GUIDE.md`
- `reports/OPTICS_COMPATIBILITY_SYSTEM_V2.md`
- `reports/AMMO_AP_BP_POLICY.md`
- `indexes/script_reference/optic_compatibility_policy_v2.json`
- `schema/compatibility.schema.json`
- `reports/samples/*`
- `agent/PRIMARY_MOD_POLICY.md`
- `agent/SAFE_PREFAB_EDITOR.md`

If a generated candidate contradicts a manual policy, record the conflict; do not silently replace the policy.

For files with mixed manual + generated history, STOP and report instead of guessing ownership.

## Phase 5 — knowledge delta report

Create on the branch:

`reports/PRIMARY_MOD_KNOWLEDGE_SYNC_REPORT.md`

It must include:
- exact primary addon root;
- source hash PASS/FAIL;
- scanner command;
- before/candidate entity counts;
- new/removed/changed entities;
- new/changed inheritance facts;
- ammo/config/projectile deltas;
- attachment/optic compatibility deltas;
- AEK/PSO/TT control-point findings;
- AP/BP candidate families discovered from source;
- unresolved external dependencies;
- scanner limitations discovered;
- list of canonical files synchronized;
- list of manual files intentionally preserved;
- any STOP conditions or ambiguous items.

## Phase 6 — validation before commit

Required checks:
- primary addon source hashes unchanged;
- candidate JSON parses;
- canonical JSON changed by sync parses;
- no manual protected file unintentionally changed;
- no unexplained mass deletion;
- active DovetailRU policy preserved;
- AP/BP policy preserved as gameplay layer;
- TT supplemental knowledge not silently regressed;
- Git diff contains only explainable knowledge-sync changes and the report.

If any check fails: restore only the attempted repository sync changes, keep evidence/report if safe, and return STOP.

## Commit and push

Only after all checks pass:

```powershell
git status --short
git diff --stat
git diff --name-status
```

Review every changed path. Then:

```powershell
git add catalog indexes agent/scan_state.json reports/scan_summary.json reports/scan_summary.md reports/PRIMARY_MOD_KNOWLEDGE_SYNC_REPORT.md snapshots/primary_candidate
```

If some listed paths were intentionally not synchronized, stage only the actually reviewed paths.

Do NOT stage unrelated files.

Commit:

```powershell
git commit -m "Study primary ARMST mod and synchronize source knowledge"
git push -u origin agent/primary-mod-knowledge-sync
```

Do not merge to `main`.

## Required return report

Return:
- branch;
- base SHA;
- primary addon root;
- scanner command;
- source file count;
- source hash PASS/FAIL;
- old/candidate entity counts by category;
- warnings/errors;
- source-backed knowledge deltas;
- AP/BP candidate map found from source;
- protected/manual file status;
- synchronized canonical paths;
- unresolved/ambiguous findings;
- resulting commit SHA if committed;
- final recommendation: `SAFE TO REVIEW` or `STOP`.
