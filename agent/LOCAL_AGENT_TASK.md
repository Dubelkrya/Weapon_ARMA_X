# Local agent task — offline architecture validation

This task is for the local coding agent. The human user should not be asked to run Git commands, collect metrics, inspect manifests, or launch Workbench during this phase.

## Objective

Validate the strict resolver and build/publish the compact weapon architecture package using only sources already available locally plus the pinned official Bohemia script repository.

Do not optimize for the old `121/3` resolver count. Identity/provenance correctness is the gate.

## Safety constraints

- Work only on `agent/resolver-v2`.
- Do not modify or merge `main`.
- Keep PR #2 draft.
- Do not edit ARMST game resources in this task.
- Treat `Imported/VanillaSources` as read-only evidence.
- Treat `Imported/OfficialScriptDiff` as read-only external evidence.
- Never commit raw vanilla/script sources or `agent/v2_output` / `agent/architecture_output`.
- Do not recreate or run a broad Workbench snapshot exporter.
- Do not ask the user to run `git pull`, Python, resolver scripts, or report files.

## Phase A — synchronize and validate code locally

1. Fetch and fast-forward the local `agent/resolver-v2` checkout yourself.
2. Confirm working tree is clean before generated work.
3. Run:

```bat
python -m unittest discover -s agent\tests -p "test_resolver_v2*.py" -v
```

4. If tests fail, diagnose and fix code on `agent/resolver-v2`; do not involve the user.
5. Confirm the removed command `WAX: Export Vanilla Weapon Source Snapshot` is absent from current Workbench scripts.

## Phase B — build the offline architecture package

Run:

```bat
python agent\scripts\build_architecture_package.py
```

This command may fetch the pinned official `BohemiaInteractive/Arma-Reforger-Script-Diff` commit for game build `1.8.0.13`. It must not use Workbench.

Inspect:

- `agent/architecture_output/package_manifest.json`
- `architecture_summary.json`
- `architecture_graph.json`
- `weapon_blueprints.json`
- `script_class_index.json`
- `script_class_links.json`
- `workbench_export_requests.json`
- `resolver_warnings.json`

Validate at minimum:

- materialized vanilla manifest check passes for requested `.et/.conf` resources;
- generated `.meta` sidecars do not cause manifest failure;
- official script source marker reports version `1.8.0.13` and commit `3d77cc212d5cda9922daf5f45635c7300d2d4cce`;
- raw/local blueprint instance GUIDs are present;
- effective architecture tree preserves provenance and is not built from semantic component reordering;
- dependency closure separates missing external refs from ambiguous identity collisions;
- no raw vanilla/script files appear in tracked changes.

## Phase C — targeted real-data regression review

Using the generated package, inspect the real chains for at least:

- `armst_ak74`
- `armst_ak105`
- `armst_ak74m`
- `rifle_val`
- `rifle_m16a2`
- VSS / VSK94 or equivalent known-good 9x39 cases
- SVD
- PKM

For each relevant weapon, verify:

- leaf origin is ARMST;
- every parent transition records origin/path and does not cross a same-path collision by priority guess;
- serialized component instance GUIDs survive parsing;
- `MagazineTemplate` selection records target origin;
- `AmmoConfig` keeps origin;
- mapped projectile keeps origin;
- projectile physics comes from that exact selected origin;
- inherited field provenance points to the actual defining resource.

Record identity ambiguities as defects/evidence gaps. Do not force them to `resolved`.

## Phase D — decide whether Workbench is needed

Inspect `workbench_export_requests.json`.

### If it is empty

- Do **not** ask the user to launch Workbench.
- Continue to publication.

### If it is non-empty

- Group exact requests by `.et` / `.conf` and referring ARMST/vanilla resource.
- Verify each request is an actual external/missing serialized edge, not an identity collision.
- Do not fall back to root scans or keyword scans.
- Stop before GUI interaction and prepare an exact-path exporter design/patch that consumes only this request set.
- Only after that exporter compiles from static review and the request list is proven should the human be asked for one Workbench GUI run.

## Phase E — publish compact derived digest

If package validation is successful, run:

```bat
python agent\scripts\publish_architecture_digest.py
```

Review `architecture/generated/` and ensure it contains derived compact data only. In particular, there must be no copied `.et`, `.conf`, `.c`, `.meta`, or raw external repository content.

Commit/push only:

- validated code/test/documentation fixes;
- `architecture/generated/` compact derived package.

Do not commit local workspace/raw inputs.

## Required final report

Return a compact engineering report containing:

1. branch HEAD and test result;
2. architecture package summary;
3. official script source version/commit;
4. exact number and paths of Workbench export requests, if any;
5. ambiguous identity edges grouped by reason;
6. real-chain regression findings for the reference weapons;
7. publication result and tracked-file safety check;
8. explicit decision: `WORKBENCH_NOT_NEEDED` or `EXACT_WORKBENCH_EXPORT_REQUIRED`.

Do not ask the user for any action unless the final decision is `EXACT_WORKBENCH_EXPORT_REQUIRED` **and** the exact exporter is already prepared for one GUI run.
