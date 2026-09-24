# ARMST primary mod policy

## Authoritative working addon

All normal weapon/prefab/config/script authoring and source scans must use this addon as the project source of truth:

`C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`

This path is the default target for local-agent work unless the user explicitly names another addon for a one-off test.

## Armst_Work status

`C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\Armst_Work`

is not the authoritative weapon addon. Treat it only as a temporary/sandbox/test addon when explicitly requested. Do not use it to replace the main catalog, indexes, policies or canonical source snapshot.

## Editing rule

For edits in the primary mod:

1. locate the exact target resource;
2. resolve parent/inherited structure;
3. record size/SHA256 and a small before snippet;
4. create a side-by-side backup;
5. make one minimal logical change;
6. validate structure and diff;
7. stop on ambiguity or unexpected changes;
8. require Workbench validation before claiming runtime success.

Use `agent/SAFE_PREFAB_EDITOR.md` for the detailed editing contract.

## Scanner rule

The checked-in scanner's default `MOD_ROOT` already points to `ARMST-PLATFORM---Weapons`. When refreshing the canonical source snapshot, scan this primary addon, not `Armst_Work`.

Do not run `scan_build.py` with an incomplete/sandbox addon while `REPO_ROOT` points at the repository root, because the scanner recreates generated `catalog/`, `indexes/`, `reports/` and `schema/` directories.

### Read-only scan guard

A scan described as read-only must prove that the consumed gameplay source stayed unchanged:

1. hash all consumed `.et`, `.conf`, `.meta` and `.c` files before the scan;
2. run the scanner;
3. hash the same source set again;
4. compare the before/after hashes;
5. stop and reject the scan if any source file changed.

Scanner success alone is not proof that the live addon was untouched.

### Noncanonical / sandbox scans

Any scan of `Armst_Work`, a test copy, historical backup or other noncanonical root must write to an isolated output root such as `snapshots/<name>/`. It must never replace the top-level canonical generated areas.

The scanner and analysis tooling must adapt to the addon's physical layout. Do not move, rename or reorganize live weapon resources merely to make scanning or indexing easier.

Canonical rescan changes belong on a dedicated review branch and must be accepted from an explainable generated diff, not from entity-count changes alone.

## Priority

Current local primary addon / Workbench evidence > canonical authoring policy > generated snapshot > spreadsheets > archived reports.
