# MP-133 — V3 current status and historical research index

> **CURRENT NAVIGATION / DESIGN STATUS (2026-10-03).** This is a map of evidence, not proof of a finished V3. For any disagreement use current live-addon/owner Workbench evidence first, then [KNOWLEDGE_STATUS.md](KNOWLEDGE_STATUS.md). The [tracking Issue #27](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27) records approvals, owner observations and STOP conditions.

## Start here in a new agent session

1. Read [`AGENTS.md`](../AGENTS.md) and [`docs/sync/CURRENT_AI_SYNC.md`](../docs/sync/CURRENT_AI_SYNC.md) **before taking action**.
2. Check the latest [Issue #27](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27) comments and the local addon/SDK. Historical SHAs and generated catalog snapshots are not substitutes for current sources.
3. Read the [V3 design and baseline assessment](MP133_V3_DESIGN_AND_BASELINE_ASSESSMENT.md), [P2 interference investigation](MP133_V3_1_I1_LAB_INTERFERENCE_INVENTORY.md), [native animation-event finding](MP133_V3_2_ANIM_EVENT_FINDING.md), and [T0/T1/T2 research and diagnostic design](MP133_V3_T0_T1_T2_DESIGN.md).
4. Preserve all local uncommitted work. Only write knowledge reports to this repository. The legacy `ARMST_MP133_AnimationLab` has no Git remote, is frozen V2 history and is **not** the V3 implementation.

## CURRENT STATUS (supersedes historical table and old Next safe work)

- **G2:** owner-tested synthetic one-round addition in existing T4b M1 magazine, native manual pump/chamber and one owner-reported shot. Runtime evidence is offline only.
- **G3-A:** published read-only SDK 1.8 donor/transaction audit on the [active T4b branch](https://github.com/Dubelkrya/Weapon_ARMA_X/blob/t4b/installed-mag-probe/reports/MP133_V3_G3_REAL_DONOR_PHASE_A.md).
- **G3-B1:** one disposable inventory-donor decrement fixture published at [`a165e80`](https://github.com/Dubelkrya/Weapon_ARMA_X/commit/a165e804df1e571c58806bb39ea74e5eee993191) within the **same existing T4b addon**; source review and owner Workbench/game trial pending. **G3-B2 and G4/G5 NOT authorised.**
- **Core SHIFT+R:** no working reload according to owner ([#33](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/33)); legacy code presence is not evidence of a functioning feature. Core RPC repacking candidate is unverified.
- **Coordination:** documentation PR #31 is independent and cannot be merged over evolving T4b shared documents without reconciliation. Historical T4a/T2a/V2/P2 are not current work; Astra paused. Catalog #28 and CI #29 completed with [hosted green run](https://github.com/Dubelkrya/Weapon_ARMA_X/actions/runs/37135291162).

## Historical verified versus still open (see current status above)

| Topic | Current evidence / status |
| --- | --- |
| T0 native MP-133 | **OWNER-RUNTIME FUNCTIONAL PASS:** three shots with manual short-R pumping and hold-R inspect with Weapons only; Core-on interaction not tested. |
| T2b paired markers | Player/weapon markers were observed in paired owner cycles; delivery is not proof of ammunition authority or exact animation synchronisation. |
| T2c native commands | Short-R manual rack: `commandID=0,intValue=1`. Native whole-mag reload observed as `intValue=5` (empty/chambering path) or `4` (partial magazine/chambered round). |
| T3 physical-mag identity | **OWNER RUNTIME:** installed magazine `M1 → null → M3`, then `M3 → null → M5`. The `M2/M4` tags are null-state sentinels, not physical objects. The chamber may retain one round during partial-mag exchange. Exact native attach timing and old-mag inventory identity are unresolved. [Read-out](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5970509383). |
| T3F passive event trace | **CORRECTED-SCRIPT OWNER RUNTIME:** 100 T3F entries, 77 T3 entries, 18 T2c commands and no `SCRIPT (E)`. No independent `gameplay_shot` signal; isolated single-shot/rack/dry-trigger controls were not completed. `Weapon_EnableFire` means firing permission during bolt/reload animation, **not a shot**. [Read-out](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5970720618). |
| T4 actual one-shell transfer | **`T4_API_OR_TRANSACTION_BLOCKED`** after read-only SDK Phase A. `SetAmmoCount` exists; legitimate donor decrement, atomic transfer, authority, replication and rollback remain unverified. No real-transfer implementation authorised. |
| T4a disposable-setter probe | **`T4A_LAB_PREPARED_OWNER_RUN_REQUIRED`:** primary agent prepared isolated `ARMSTMP133T4A_SetProbe` (GUID `A7C41E90D3B24F68`), one guarded action on a disposable, non-installed test magazine (default key P). Static checks reported; **Workbench/game NOT TESTED**. No real donor transfer or installed-mag mutation. [Report](MP133_V3_T4A_SETAMMOCOUNT_SEMANTICS.md). |
| Astra animation graph lab | **PAUSED BY OWNER.** Separate proposed `ARMST_MP133_AstraShellGraph`; local `astra_build.py` is incomplete/unverified WIP, not a functional or archived prototype. [Pause](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5970888887). |
| Production V3 / Core / MP | **NOT IMPLEMENTED / NOT VERIFIED.** Preserve native pump/fire, hold-R and other weapons; Core SHIFT+R reload is not functional according to the owner; no global input interception. |

**Intended V3 controls, not current T0 behavior:** short R performs the necessary verified native pump (if required) and then per-shell tube loading; a second short R or trigger requests safe stop; hold R preserves native inspection; Core SHIFT+R reload is a historical, nonworking mechanism, not a current dependency. If standard R cannot be intercepted without affecting native behavior, a separate load action is a possible fallback **only after the owner's decision**.

## Current design / evidence reports

| Report | Role |
| --- | --- |
| [`MP133_V3_DESIGN_AND_BASELINE_ASSESSMENT.md`](MP133_V3_DESIGN_AND_BASELINE_ASSESSMENT.md) | Initial V3 architecture and strict baseline gate; its historical `PENDING` wording is superseded by the owner T0 observation above. |
| [`MP133_V3_T0_T1_T2_DESIGN.md`](MP133_V3_T0_T1_T2_DESIGN.md) | Completed **read-only designs** for T1 input and T2 event-routing diagnostics; no code implemented. |
| [`MP133_V3_1_I1_LAB_INTERFERENCE_INVENTORY.md`](MP133_V3_1_I1_LAB_INTERFERENCE_INVENTORY.md) | P2 A/B, global-handler implication and rejected speculation about double-calling native defaults. |
| [`MP133_V3_2_ANIM_EVENT_FINDING.md`](MP133_V3_2_ANIM_EVENT_FINDING.md) | Exact owner-edited native-event keyframes, stale TXA versus ANM and unknown active-clip/mag-identity boundaries. |
| [`MP133_V3_INSERT_EVENT_AUDIT.md`](MP133_V3_INSERT_EVENT_AUDIT.md) | Read-only audit of the `Reload_InsertMag` events: `Weapon_SpawnMagazine(10)/AttachMagazine(43)/MagRelease(64)` are stock **whole-magazine** operations; there is no native per-shell insert (cmd 7 excluded by the MP-133 graph). One logging-only T3 probe proposed. |
| [`MP133_V3_RELOAD_GRAPH_AUDIT.md`](MP133_V3_RELOAD_GRAPH_AUDIT.md) | Full read-only reload-graph audit: production vs T2A graph logic proven identical (GUID-normalized), complete `IdleReloadSTM`/`WeaponReloadSTM`/`MagReloadSTM` state/transition map with exact conditions, ASI/clip event mapping, lifecycle/interrupt, per-shell feasibility options and one minimal next gate. |
| [`MP133_V3_T2C_COMMAND_TRACE.md`](MP133_V3_T2C_COMMAND_TRACE.md) | Installed-SDK-verified passive native command trace; owner-runtime int 1/4/5 routing documented in Issue #27. |
| [`MP133_V3_T3_MAG_IDENTITY_TRACE.md`](MP133_V3_T3_MAG_IDENTITY_TRACE.md) | Getter-only current-mag entity tags and chamber snapshots; owner runtime established the native whole-mag replacement. |
| [`MP133_V3_T3F_FIRE_EVENT_AUDIT.md`](MP133_V3_T3F_FIRE_EVENT_AUDIT.md) | T3F Phase A + limited passive Phase B. Corrected script ran in owner's game; **independent shot signal unresolved**. |
| [`MP133_V3_T4_ONE_SHELL_TRANSFER.md`](MP133_V3_T4_ONE_SHELL_TRANSFER.md) | T4 Phase A API audit; real transfer blocked; T4a disposable-setter experiment authorised separately in Issue #27. |
| [`MP133_V3_T4A_SETAMMOCOUNT_SEMANTICS.md`](MP133_V3_T4A_SETAMMOCOUNT_SEMANTICS.md) | Primary agent's isolated disposable-magazine setter lab, actual resources/SDK signatures and owner-only Workbench runbook; static-only and awaiting owner runtime. |
| [`MP133_LAB_REGISTRY.md`](MP133_LAB_REGISTRY.md) | Local/frozen/paused laboratory ownership, source availability and archiving obligations. |
| [Issue #27](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27) | **Current approval and decision record**. Read newer comments before acting on its original V2.2 body. |

## Frozen historical V1/V2 evidence (retain; not V3 instructions)

| Report | What it preserves |
| --- | --- |
| [`MP133_ANIMATION_LAB_HANDOFF.md`](MP133_ANIMATION_LAB_HANDOFF.md) | Large cross-version experiment log and owner observations. Historical, **not** current design authority. |
| [`MP133_ANIMATION_LAB_ISSUE_COMMENT.md`](MP133_ANIMATION_LAB_ISSUE_COMMENT.md) | Earlier coordination snapshot. |
| [`MP133_ANIMATION_LAB_V1.md`](MP133_ANIMATION_LAB_V1.md) | Initial lab implementation. |
| [`MP133_ANIMATION_LAB_V1_TEST_CHECKLIST_RU.md`](MP133_ANIMATION_LAB_V1_TEST_CHECKLIST_RU.md) | V1 owner test checklist. |
| [`MP133_ANIMATION_LAB_V23_IMPORT_AND_R.md`](MP133_ANIMATION_LAB_V23_IMPORT_AND_R.md) | V2.3 animation import and R investigation. |
| [`MP133_ANIMATION_LAB_V23_R_TEST_RU.md`](MP133_ANIMATION_LAB_V23_R_TEST_RU.md) | V2.3 input tests. |
| [`MP133_ANIMATION_LAB_V25_INPUT_PREFLIGHT.md`](MP133_ANIMATION_LAB_V25_INPUT_PREFLIGHT.md) | V2.5 input preflight. |
| [`MP133_ANIMATION_LAB_V26_PUMP_CHAMBER_TRACE.md`](MP133_ANIMATION_LAB_V26_PUMP_CHAMBER_TRACE.md) | V2.6 pump/chamber traces. |
| [`MP133_ANIMATION_LAB_V27_C2_TRACE_AND_CORE_ISOLATION.md`](MP133_ANIMATION_LAB_V27_C2_TRACE_AND_CORE_ISOLATION.md) | V2.7 lab/Core isolation. |
| [`MP133_ANIMATION_LAB_V28_REFERENCE_COMPARISON.md`](MP133_ANIMATION_LAB_V28_REFERENCE_COMPARISON.md) | V2.8 comparison against a working pump reference. |
| [`MP133_ANIMATION_LAB_E0_ISOLATION_PLAN.md`](MP133_ANIMATION_LAB_E0_ISOLATION_PLAN.md) | Older E0 diagnosis and separation plan. |
| [`MP133_LAB_RESTORE_INSTRUCTIONS.md`](MP133_LAB_RESTORE_INSTRUCTIONS.md) | Archived V2 recovery instructions; **do not restore into an active V3 test** without explicit approval. |

**Historical V2 tooling (do not run for V3):** [`agent/scripts/mp133_lab_connect_anims.py`](../agent/scripts/mp133_lab_connect_anims.py), [`mp133_lab_r_gate_model.py`](../agent/scripts/mp133_lab_r_gate_model.py), [`validate_mp133_lab.py`](../agent/scripts/validate_mp133_lab.py) and their corresponding `agent/tests/test_mp133_lab_*.py` tests. Retained for regression analysis, not deleted or migrated into the live addon.

## Next safe work

1. **Current G3-B1:** independently review the newly published donor-only fixture on the active T4b branch; then the owner compiles/tests it in Workbench and reports inventory, identity, ammo and delayed snapshots. Real two-sided G3-B2 transfer remains gated.
2. **Astra:** keep the graph/animation lab and its partially authored local script **paused** until explicit owner resumption. Do not run, overwrite, or migrate unverified generator output.
3. **Production/Core/V2/P2/T2A:** no new edits under these assignments. T3F passive logging already ran; independent `OnProjectileShot`/event-name follow-ups require separate scope, not an automatic T4a dependency.
4. **Knowledge maintenance:** use [the phase handoff template](../docs/guides/EXPERIMENT_HANDOFF_TEMPLATE.md), update this index and [the lab registry](MP133_LAB_REGISTRY.md) when new owner evidence arrives, and check [Issue #27](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27) for newer approvals. The catalog #28 rescan was published; any **future** rescan needs a fresh source/diff review and must stay separate from MP-133 experimental edits.
