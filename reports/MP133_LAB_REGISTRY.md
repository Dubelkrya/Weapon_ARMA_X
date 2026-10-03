# MP-133 lab registry and archival checkpoint

**Status:** evidence-based registry, as of 2026-10-03. This file is **not** proof that files exist or hashes match on the owner's computer today. Inspect the local filesystem and compare hashes on each resumption. Latest owner permissions and STOP gates: [Issue #27](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27).

## Boundaries and owners

| Lab / work area | Ownership and purpose | Last evidenced state | Preserve / next action |
|---|---|---|---|
| Production `ARMST-PLATFORM---Weapons` + Core | Owner's live gameplay addons | Weapons ~29 and Core ~4 dirty entries in the latest agent reports; these are historical counts, **not** a current git-status check | Never reset, stash, clean or merge experimental sources here without separate permission |
| `ARMSTMP133T2A_Diag` | Primary-agent passive T2a/T2b/T2c/T3/T3F diagnostics | Reported root GUID `AF1464F772CC998F`; diagnostic prefab `{5FB844730BED8BD1}`; corrected T3F lab script SHA-256 `E978EDAF373D882EE3F6798D5D0BF41DA264E638B1371E302AD164D982A3339B` (agent report); owner game log confirms passive logging, not embedded file SHA | **Read-only** for Astra/T4a. Reconfirm actual local file hash before assuming this checkpoint is current |
| Legacy `ARMST_MP133_AnimationLab` (V2) and P2 | Frozen historical studies | V2 restore instructions and source hashes are in [`MP133_LAB_RESTORE_INSTRUCTIONS.md`](MP133_LAB_RESTORE_INSTRUCTIONS.md); no verified Git remote for V2 | Do not repurpose as V3, regenerate GUIDs, or restore over an active experiment |
| Astra `ARMST_MP133_AstraShellGraph` proposal | Astra alone owns isolated graph/animation work | **PAUSED / UNVERIFIED WIP**; owner supplied a partial generator draft at `outputs/mp133-astra-worktree/artifacts/astra_build.py`; no verified addon build, imports, compile or owner runtime. [Pause notice](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5970888887) | Preserve the local worktree untouched. Do not run the draft generator, edit, copy over, or assign another agent until owner resumes Astra |
| T4 Phase A | Primary agent SDK audit | [`MP133_V3_T4_ONE_SHELL_TRANSFER.md`](MP133_V3_T4_ONE_SHELL_TRANSFER.md): **`T4_API_OR_TRANSACTION_BLOCKED`** for real shell transfer | Historical audit remains authoritative for its measured SDK limitations |
| T4a disposable-magazine lab | Primary agent; independent of Astra | [T4a authorisation](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5970853781) exists; no lab files or owner runtime evidenced in this registry | Agent may prepare an **independent isolated lab** and stop for owner Workbench/game testing; no donor depletion or installed-mag changes |

## Minimal archival manifest for EACH lab, on creation or resumption

1. **Identity:** exact addon folder (resolved, not guessed), `addon.gproj` ID and GUID, prefab ResourceName/GUID, declared addon dependencies, owner agent and issue/approval link.
2. **Sources and tools:** complete editable input files (`.agf/.agr/.ast/.aw/.asi/.txa/.c/.et` as applicable), generator/script version, required installed SDK and Blender/Workbench importer version, and any asset licensing constraints. Do not claim an imported `.anm` can be reproduced without the editable source/import settings.
3. **Hashes and manifest:** SHA-256 for all owned source files and generated runtime resources, dependency baseline HEAD, protected-file before/after hashes, dirty-file inventory and explicit changed-file allowlist. Preserve existing `.meta` identity; never regenerate it to match a new script.
4. **Reproduction:** exact inputs, command(s) or manual owner steps, expected outputs, dependency mount/load order, Workbench import/compile instructions, a clean-room path that does **not** overwrite another lab, and tested rollback.
5. **Evidence:** separate `STATIC_PASS`, `OWNER_WORKBENCH_PASS`, `OWNER_GAME_PASS`, `MP_VERIFIED`, `BLOCKED` and `NOT_TESTED` statuses. Link owner logs and name untested cases; do not treat Python generation or hosted CI as an engine test.
6. **Storage:** store reports and the portable **source manifest** in the knowledge repo (review branch/PR if concurrent). Keep temporary logs in git-ignored `artifacts/`. Preserve large/private/binary authoring assets in a separately versioned backup with recorded location + SHA and recovery instructions, not an unverified local-only path. Do not upload Astra WIP while its freeze is in force.

## Resume / collision control

- Fresh `origin/main`, then `AGENTS.md`, [`CURRENT_AI_SYNC.md`](../docs/sync/CURRENT_AI_SYNC.md), [`MP133_INDEX.md`](MP133_INDEX.md), newest issue comments and this registry **before** editing.
- Take actual local and Git state; names/hashes above are historical evidence until rechecked. Never automatically run a partially authored generator.
- One agent owns one isolated lab/worktree. Knowledge-repo concurrent changes should use separate branches/PRs. This does not change the **live Weapons addon's** distinct `main`-only branch policy.
- Require owner approval before unfreezing Astra, mutating another agent's lab, promoting source to production or performing a new live-game test.
