# tools/live-addon — imported from the live addon's `agent/` directory

**Provenance.** These 27 Python files were moved verbatim out of the live addon
on 2026-09-29, out of `ARMST-PLATFORM---Weapons/agent/<subdirectory>/`. Each
file is byte-identical to what was in the addon: copied, re-hashed, and the
hash compared against the pre-move hash before the source was deleted.

Report and dump output produced by these tools went to
[`../../reports/live-addon/`](../../reports/live-addon/), preserving the original
directory layout under `live-addon/agent/<subdirectory>/`.

## Read this before running anything

**These tools still contain their original hardcoded paths.** They were written
to run from inside the live addon's `agent/` directory, and many of them assume
that location, that `MOD_ROOT`-style constants, and relative output paths. They
have **not** been refactored to use
[`addon_path.py`](../../agent/scripts/addon_path.py) or to write into
[`artifacts/`](../../artifacts/).

Before running one:

1. Read it. Check for hardcoded `ARMST-PLATFORM---Weapons` paths, hardcoded
   `C:\Users\yshky\...` paths, and `os.chdir` calls.
2. Redirect its output. Point it at `artifacts/`, not at the repository root
   and **never** at the live addon.
3. Treat it as read-only unless you have verified exactly what it writes.

Adopting one of these into `agent/scripts/` means making it use
`resolve_addon_root()` and honour the output policy in
[`../../AGENTS.md`](../../AGENTS.md) rules 1 and 5.

## Not part of CI

`.github/workflows/repository-integrity.yml` does not run any of these. They are
archived, unmaintained tooling. The maintained toolchain is in
[`../../agent/scripts/`](../../agent/scripts/), which has regression tests in
[`../../agent/tests/`](../../agent/tests/).

## Subdirectories

| Directory | Contents |
|---|---|
| `colliders/` | `ebt_add_colliders.py` — EBT collider helper |
| `prefab_audit/` | `audit_prefabs.py`, `fix_audit.py` |
| `refcheck/` | `refcheck.py` — reference checker |
| `structura/` | 23 `structura_*.py` modules — BSP/room/model tooling |
