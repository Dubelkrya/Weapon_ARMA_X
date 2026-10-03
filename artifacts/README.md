# artifacts/ — agent scratch output

**Nothing in this directory is a deliverable.** It is git-ignored.

## What goes here

Default destination for anything an agent or tool produces while working:

- audit dumps and scanner output (`*.json`, `*.csv`, `*.txt`)
- diagnostic logs and traces
- scratch scripts and one-off analysis
- task plans, prompt text, handover notes
- intermediate parse trees and diffs

## What does not go here

Anything meant to be kept. If output is genuinely valuable, promote it
deliberately and say so in the summary:

| Kind of output | Destination |
|---|---|
| Durable report worth reading later | `reports/` |
| Reusable tool | `tools/` or `agent/scripts/` |
| Policy or authoring guidance | `reports/` or `docs/guides/` |
| Structured facts to be queried | regenerate `catalog/` + `indexes/` via `scan_build.py` |

## Never here, and never in the live addon

The live addon is a real mod project. It contains only what the game,
Workbench, or the modder's runtime needs. Reports, audits, plans, scratch
scripts and diagnostics do not belong in it, and this repository is where they
go instead. See [`../AGENTS.md`](../AGENTS.md) rules 4, 5 and 10.

## Housekeeping

`artifacts/` is git-ignored, but local untracked files may be the owner's only copies of logs or test evidence. **Inspect first; do not delete all files automatically.** The tracked `artifacts/README.md` must remain in place.

To list contents before a separately approved cleanup, run from the repository root:

```powershell
Get-ChildItem -Force artifacts | Where-Object { $_.Name -ne 'README.md' }
```

Promote durable evidence to an explicitly reviewed destination. Delete individual confirmed-disposable paths only after classifying them in accordance with [`AGENTS.md`](../AGENTS.md).
