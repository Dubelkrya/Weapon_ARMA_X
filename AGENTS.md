# AGENTS.md — operating rules for Weapon_ARMA_X

Read this file completely before doing any work in this repository.

This repository is a **tools and knowledge repository for the ARMST weapons
addon**. It is not the addon. The addon lives on disk at a separate path and is
accessed read/write only through that path.

---

## The one structural rule

```
Weapon_ARMA_X   = tools, policies, audits, reports, generated indexes
ARMST-PLATFORM---Weapons = the actual mod: .et/.conf/.meta/.c/.layer + assets
```

**Everything an agent produces goes in this repository. Nothing an agent
produces goes into the live addon.** The live addon contains only what the game,
Workbench, or the modder's runtime needs.

If you find yourself about to create a report, audit dump, plan, prompt,
handover, scratch script, or diagnostic JSON inside the addon — stop. Write it
here instead.

---

## Startup rules

1. **Resolve the addon path; never hardcode it.** Use
   `agent/scripts/addon_path.py` → `resolve_addon_root()`. It reads
   `ARMST_WEAPONS_ADDON_PATH` (or legacy `MOD_ROOT`), validates the result, and
   raises rather than guessing. `python agent/scripts/addon_path.py` prints the
   resolved root and exits non-zero when it cannot be validated.

2. **Confirm you resolved the right addon, not merely *an* addon.** Seven
   sibling addons in the Workbench `addons/` directory contain `addon.gproj` and
   `Prefabs/`, so a structural check alone is not identity. The resolver also
   checks `addon.gproj`'s `ID` against `EXPECTED_GPROJ_IDS`. An explicitly
   configured path that fails validation is a **hard error**; it never falls
   back to a default, because scanning the wrong addon silently and writing the
   result into `catalog/` is the failure this rule exists to prevent.

3. **Treat the live addon as the source of truth; treat generated data here as a
   snapshot.** `catalog/`, `indexes/`, `reports/` and `schema/` describe the
   addon as of their last scan. Newer live-addon or Workbench evidence wins.
   Authority order: live addon / Workbench evidence > authoring policy here >
   generated snapshot > archived report.

4. **Never write agent output into the live addon.** No reports, no audit
   markdown, no JSON/CSV dumps, no task descriptions, no scratch scripts, no
   handover or prompt files. Default output location is `artifacts/` in this
   repository (see rule 5).

5. **Default tool output to `Weapon_ARMA_X/artifacts/`.** `artifacts/` is
   git-ignored: it is scratch space, not a deliverable. If output is
   genuinely worth keeping, promote it deliberately into `reports/` and say so
   in the summary — do not promote it by accident.

6. **Preserve GUID and meta identity.** Never rewrite, regenerate, reformat or
   "tidy" a `.meta` file, and never change an instance ID inside a `.et`. GUIDs
   are the identity of every resource in the mod. A cleanup, refactor, rename
   or reformat task must leave them byte-identical.

7. **Prove that a read-only task was read-only.** "Read-only", "audit",
   "diagnostic" and "investigate" mean the consumed gameplay source is
   unchanged. Hash the consumed `.et/.conf/.meta/.c/.layer` set before and after,
   compare, and report `GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0`. Scanner success
   is not proof of an untouched addon.

8. **Preserve the user's uncommitted work.** Do not run `git restore`,
   `git stash`, `git reset`, `git checkout --`, or `git clean -fd` over someone
   else's uncommitted changes. Uncommitted modifications in the live addon are
   the user's active work, not cleanup targets. If a dirty file blocks a task,
   report it and stop.

9. **Verify by hash before destroying anything.** For a move, copy → re-hash the
   copy → compare against the pre-move hash → only then delete the source. If the
   hash does not match, abort without deleting. Deleting a file is the last
   step, never the first.

10. **Do not delete something just because an agent created it.** Provenance is
    not a reason. Classify by what the file *is* — runtime resource, Workbench
    artefact, authored documentation, or agent artefact — and record the reason.
    If it cannot be classified, leave it in place and list it for review.

11. **Inheritance is not a defect.** A child prefab that omits a value is
    inheriting it. Missing data that resolves through the parent chain is
    correct. Before calling anything a bug, resolve the chain and check what the
    engine actually inherits — including vanilla engine base classes.

12. **Never invent values.** If a value cannot be reached through the file
    chain, the vanilla `.pak`, or Workbench evidence, it is *unresolved* — and
    unresolved is a valid, reportable answer. Do not fabricate coordinates,
    pivot names, class names, tolerances or expected context names to fill a
    report. Guessed data is worse than a gap.

13. **Separate static validation from runtime validation.** Parsing a prefab,
    resolving an inheritance chain, or hashing a file proves nothing about
    behaviour in-game. World-item interaction, physics, ADS, recoil and
    ballistics need Workbench or in-game confirmation. Never report a static
    check as runtime-verified.

14. **Stop and report on ambiguity.** Stop before pushing when branch authority
    is unclear, before deleting when classification is unclear, and before
    editing when the target is unclear. State what you know, what you verified,
    and what remains unverified. One repo, one branch, one logical change per
    commit — and push only the branch you were explicitly authorised to push.

---

## The live ARMST addon

The game addon is a **separate project on a separate disk path with its own
remote**:

```
C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons
```

`Weapon_ARMA_X` is tooling only. It is not the mod, and it must never be
mistaken for it.

### Branch policy for the live addon

```
main            = the only active, permanent branch
test_weapon     = retired; deleted locally and remotely
```

Normal addon development happens directly on `main`.

- **Never recreate `test_weapon` automatically.**
- **Do not create feature branches** unless the user explicitly requests one.
- Do not force-push the addon, and do not reset or rewrite its history.

### Current checkpoint

```
ARMST-PLATFORM---Weapons  main = 6ec5015f572720223789cd82c4e3232097f11b99
ARMST-PLATFORM---Weapons  test_weapon = DELETED
```

This SHA is a **checkpoint, not a permanent expected HEAD** — future `main`
commits will advance it. Re-read it with `git -C <addon> rev-parse HEAD`; never
treat a stale value here as authoritative.

### Never discard the user's Workbench work

Do not automatically run `git stash`, `git reset`, `git restore`, `git clean` or
any other discard against the live addon. Uncommitted changes there are the
user's active work, not cleanup targets. Preserve `.meta` files and GUID
identity at all times.

### Artifacts belong here, not in the addon

Agent prompts, reports, audits, task documents, scanner dumps and diagnostics
must **never** be written into the live addon. They belong in `Weapon_ARMA_X`.
Default scratch output is `artifacts/` (rule 5).

---

## Repository map

| Path | Purpose |
|---|---|
| `agent/` | Agent policies, scanner, parser, tests |
| `agent/scripts/addon_path.py` | Addon path resolution policy (rule 1–2) |
| `artifacts/` | Git-ignored scratch output (rule 5) |
| `catalog/` | Generated per-entity facts |
| `docs/guides/` | Authoring guides (RU) migrated out of the live addon |
| `indexes/` | Generated and curated lookup data |
| `reports/` | Reports, policies, generated comparisons |
| `reports/live-addon/` | Imported verbatim from the live addon's former `agent/` directory |
| `tools/live-addon/` | Imported dev tooling from the live addon's former `agent/` directory |
| `schema/` | JSON schemas |

## Concurrent knowledge-repo work and experiment handoff

This **knowledge repo** may use an isolated topic branch and PR for concurrent documentation/tooling changes. Before opening a branch, read the current `origin/main` and identify other agents' active files. Do not overwrite another agent's branch, worktree or unfinished experiment. **This does not change the separate live Weapons addon's `main`-only policy above.**

After each significant research or implementation phase, record the result using [`docs/guides/EXPERIMENT_HANDOFF_TEMPLATE.md`](docs/guides/EXPERIMENT_HANDOFF_TEMPLATE.md): exact approval, source/SDK version, changed-file allowlist, pre/post hashes, findings, static-vs-Workbench-vs-game-vs-MP verification, unresolved gates, rollback and precise next owner-authorised action. Historical reports remain historical rather than being silently rewritten as newly tested.

For isolated owner-authorised **lab runtime assets**, see [`reports/MP133_LAB_REGISTRY.md`](reports/MP133_LAB_REGISTRY.md) for lab ownership and a portable source/restore manifest. A lab addon is not the production Weapons addon: its minimum required runtime resources may live in its **own** isolated addon, while reports, generation manifests, scratch output and handoff documentation belong in this knowledge repo or a separately versioned owner-approved archive. A local-only generator draft is not an archived, tested prototype. If a lab is paused, its files and worktree stay untouched until the owner resumes it.

## Before you commit

```powershell
python agent/scripts/addon_path.py                 # resolves the right addon
python agent/scripts/check_repository_integrity.py  # JSON/schemas/links still valid
python -m unittest discover -s agent/tests -p "test_*.py"
```

Then confirm: the live addon's path is unchanged, no gameplay file changed, and
no GUID changed.

Note that `catalog/` holds both generated JSON and the imported vanilla
reference corpus (`catalog/**/*.et|.conf|.meta`). The corpus is intentional and
must survive a rescan — never hand-edit generated catalog JSON to chase a
changed prefab path, regenerate it with `python agent/scripts/scan_build.py`.

## See also

- [`reports/KNOWLEDGE_STATUS.md`](reports/KNOWLEDGE_STATUS.md) — what is current
- [`agent/PRIMARY_MOD_POLICY.md`](agent/PRIMARY_MOD_POLICY.md) — addon selection
- [`agent/SAFE_PREFAB_EDITOR.md`](agent/SAFE_PREFAB_EDITOR.md) — editing contract
- [`docs/sync/CURRENT_AI_SYNC.md`](docs/sync/CURRENT_AI_SYNC.md) — current session state
