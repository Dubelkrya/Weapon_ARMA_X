# Experiment / agent handoff template

Copy this template into a **new** report or issue comment after an engineering task. Do not rewrite historical reports to make them appear newly tested. Replace bracketed placeholders and remove irrelevant rows. The owner alone performs Workbench/game testing unless independently proven otherwise for a specific agent.

## Identity and decision gate

- **Project / issue / experiment:** [name, issue link, task ID]
- **Owner approval and exact scope:** [link, allowed actions]
- **Executor and source branch/worktree:** [agent, branch, independent workspace]
- **Status (one):** `RESEARCH_DONE` / `STATIC_PASS_OWNER_RUN_REQUIRED` / `OWNER_RUNTIME_PASS` / `BLOCKED` / `PAUSED` / `FAILED`
- **STOP conditions triggered / untriggered:** [what required stopping]
- **Last review date:** [YYYY-MM-DD]

## Starting authority and preserved state

| Item | Exact source / path / commit or hash | Verification mode |
|---|---|---|
| Knowledge-repo origin/main | [fresh SHA] | SOURCE: git |
| Target local addon | [resolved path, gproj ID/GUID] | SOURCE: local |
| Installed SDK / APIs | [installed version and docs/files] | SOURCE: SDK |
| Current files and dirty state | [git status, before hashes] | SOURCE: local |
| Protected production / other labs | [before/after manifest] | SOURCE: SHA |

Read `AGENTS.md`, `docs/sync/CURRENT_AI_SYNC.md`, relevant index, issue comments and previous report **before** starting. Local addon/Workbench evidence takes precedence over older generated snapshots.

## Findings, separated by evidentiary level

| Finding | Evidence (exact file/line, event/log line, GUID or method) | Level |
|---|---|---|
| [claim] | [path + relevant excerpt / linked owner log] | `SOURCE` / `OWNER-RUNTIME` / `INFERENCE` / `UNRESOLVED` |

Do not turn a proposed API signature into a proven transaction; a compile result into gameplay success; `srv=1` in an offline session into multiplayer proof; or a diagnostic animation event into a gameplay shot.

## Changed-file manifest and rollback

| File/resource | Change type | Before SHA-256 | After SHA-256 | Approved? |
|---|---|---|---|---|
| [path] | [create/edit/delete] | [hash or N/A] | [hash] | [issue link] |

- **New resource GUIDs and dependencies:** [manifest or N/A]
- **Unchanged-set proof:** [actual before/after hashes; no generic claims]
- **Collision check:** [other agents' worktrees/labs unchanged]
- **Rollback:** [verified restoration path and required precautions]
- **Portable editable source / generator / importer inputs:** [versioned location + SHA or NOT ARCHIVED]

Do not put reports or scratch outputs into the live addon. Do not overwrite dirty owner files or existing `.meta`/GUIDs.

## Verification matrix

| Gate | Result | Exact evidence or limitation |
|---|---|---|
| Source/API audit | `PASS` / `BLOCKED` / `NOT_TESTED` | [method/version] |
| Static syntax and tests | `PASS` / `FAIL` / `NOT_TESTED` | [commands and output] |
| Hosted CI | `PASS` / `FAIL` / `NOT_RUN` | [specific run SHA/URL] |
| Workbench import/compile | `OWNER_PASS` / `FAIL` / `NOT_RUN` | [owner log] |
| In-game offline | `OWNER_PASS` / `FAIL` / `NOT_RUN` | [scenario and owner evidence] |
| Multiplayer / replication | `VERIFIED` / `FAILED` / `NOT_TESTED` | [dedicated-server/client evidence] |

## Owner-only runbook (if needed)

1. [exact addon set / excluded addons, test map and asset]
2. [Workbench rescan/import + Game compile]
3. [one isolated action, initial state, controls and expected state]
4. [full log prefixes, inventory/visual observations and evidence delivery]
5. [what constitutes STOP, failure or a prohibited follow-up]

## Outcome and next authorised action

- **What is confirmed:** [bounded findings]
- **What is blocked/unresolved:** [precise reason and safety consequence]
- **What is saved/recoverable:** [report + source archive link, hash, limitations]
- **Next action permitted by the owner:** [link or NONE — WAIT FOR REVIEW]
- **Next agent reads first:** [AGENTS.md, current sync, exact issue, this report]
