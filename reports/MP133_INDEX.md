# MP-133 — V3 current status and historical research index

> **CURRENT NAVIGATION / DESIGN STATUS (2026-10-03).** This is a map of evidence, not proof of a finished V3. For any disagreement use current live-addon/owner Workbench evidence first, then [KNOWLEDGE_STATUS.md](KNOWLEDGE_STATUS.md). The [tracking Issue #27](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27) records approvals, owner observations and STOP conditions.

## Start here in a new agent session

1. Read [`AGENTS.md`](../AGENTS.md) and [`docs/sync/CURRENT_AI_SYNC.md`](../docs/sync/CURRENT_AI_SYNC.md) **before taking action**.
2. Check the latest [Issue #27](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27) comments and the local addon/SDK. Historical SHAs and generated catalog snapshots are not substitutes for current sources.
3. Read the [V3 design and baseline assessment](MP133_V3_DESIGN_AND_BASELINE_ASSESSMENT.md), [P2 interference investigation](MP133_V3_1_I1_LAB_INTERFERENCE_INVENTORY.md), [native animation-event finding](MP133_V3_2_ANIM_EVENT_FINDING.md), and [T0/T1/T2 research and diagnostic design](MP133_V3_T0_T1_T2_DESIGN.md).
4. Preserve all local uncommitted work. Only write knowledge reports to this repository. The legacy `ARMST_MP133_AnimationLab` has no Git remote, is frozen V2 history and is **not** the V3 implementation.

## Verified versus still open

| Topic | Current evidence / status |
| --- | --- |
| Clean native MP-133 (T0) | **OWNER-RUNTIME FUNCTIONAL PASS**: only Weapons addon loaded; three actual successive shots with ordinary short-R manual pumping; 10-round tube supply depleted; hold R inspection works. [Owner result](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5967911774) |
| Strict physical-mag identity | **NOT INSTRUMENTED**: no before/after physical magazine entity identity or complete last-round chamber trace. Do not claim no silent replacement solely from the functional T0. |
| Core interaction | **NOT TESTED IN T0**: Core was not loaded; frozen LSHIFT+R must be considered separately in a safe controlled test. |
| Legacy V2 global R regression | **P2 OWNER-RUNTIME**: excluding the old global `modded SCR_CharacterCommandHandlerComponent` restored ordinary R on other pumps. The exact `super`/native failure mechanism is unknown. |
| Owner's native-event edit | Visible chamber-insert behavior reportedly recovered after restoring `Weapon_SpawnMagazine/AttachMagazine/MagRelease` in a lab clip. This is **not** proof of magazine continuity, chamber correctness or ammo conservation. |
| Chung's animation reference | Provided AGF/AGR/AST, player/weapon ASI, code and selected player-event screenshots support separate pump, grab, insert and safe stop/continue paths. Actual player→weapon event routing and possible duplicate commit are **UNRESOLVED**. |
| T1 input routing | **READ-ONLY DESIGN PUBLISHED**; stock R action name, short/hold edge arbitration and whether a listener can suppress native reload remain unproven. |
| T2 event routing | **READ-ONLY DESIGN PUBLISHED**; diagnostic player-only, weapon-only and paired-marker experiments proposed; no test code or asset edit authorized. |
| V3 actual code | **NOT AUTHORIZED / NOT IMPLEMENTED**. Real one-shell server transaction, once-only commit, safe stop, network and low-FPS tests are future gates. |

**Intended V3 controls, not current T0 behavior:** short R performs the necessary verified native pump (if required) and then per-shell tube loading; a second short R or trigger requests safe stop; hold R preserves native inspection; LSHIFT+R is the unchanged Core action. If standard R cannot be intercepted without affecting native behavior, a separate load action is a possible fallback **only after the owner's decision**.

## Current design / evidence reports

| Report | Role |
| --- | --- |
| [`MP133_V3_DESIGN_AND_BASELINE_ASSESSMENT.md`](MP133_V3_DESIGN_AND_BASELINE_ASSESSMENT.md) | Initial V3 architecture and strict baseline gate; its historical `PENDING` wording is superseded by the owner T0 observation above. |
| [`MP133_V3_T0_T1_T2_DESIGN.md`](MP133_V3_T0_T1_T2_DESIGN.md) | Completed **read-only designs** for T1 input and T2 event-routing diagnostics; no code implemented. |
| [`MP133_V3_1_I1_LAB_INTERFERENCE_INVENTORY.md`](MP133_V3_1_I1_LAB_INTERFERENCE_INVENTORY.md) | P2 A/B, global-handler implication and rejected speculation about double-calling native defaults. |
| [`MP133_V3_2_ANIM_EVENT_FINDING.md`](MP133_V3_2_ANIM_EVENT_FINDING.md) | Exact owner-edited native-event keyframes, stale TXA versus ANM and unknown active-clip/mag-identity boundaries. |
| [`MP133_V3_INSERT_EVENT_AUDIT.md`](MP133_V3_INSERT_EVENT_AUDIT.md) | Read-only audit of the `Reload_InsertMag` events: `Weapon_SpawnMagazine(10)/AttachMagazine(43)/MagRelease(64)` are stock **whole-magazine** operations; there is no native per-shell insert (cmd 7 excluded by the MP-133 graph). One logging-only T3 probe proposed. |
| [`MP133_V3_RELOAD_GRAPH_AUDIT.md`](MP133_V3_RELOAD_GRAPH_AUDIT.md) | Full read-only reload-graph audit: production vs T2A graph logic proven identical (GUID-normalized), complete `IdleReloadSTM`/`WeaponReloadSTM`/`MagReloadSTM` state/transition map with exact conditions, ASI/clip event mapping, lifecycle/interrupt, per-shell feasibility options and one minimal next gate. |
| [`MP133_V3_T2C_COMMAND_TRACE.md`](MP133_V3_T2C_COMMAND_TRACE.md) | T2c lab-only passive `OnCharacterCommand(commandID,intValue,floatValue)` trace in `ARMST_T2A_WeaponAnimationComponent`; installed-SDK (not 1.13.2) compatibility verified. Owner run required; no input/graph/ammo change. |
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

- T1/T2 design is already committed in [`MP133_V3_T0_T1_T2_DESIGN.md`](MP133_V3_T0_T1_T2_DESIGN.md). **Do not task another agent to repeat the same report.**
- Separately approve an isolated **logging-only** T2 event-routing experiment and T1 input observation, if and when the owner elects to run them. No per-shell ammo changes in these diagnostics.
- Verify physical magazine entity stability when instrumentation becomes available; do not redo the completed functional three-shot T0 without a reason.
- Later, independently review the real one-shell transfer (same tube entity, compatible homogeneous ammo source, server-authoritative once-only commit) and Core integration before implementing V3.
- The **canonical catalog rescan is separate work**: the 2026-09-29 sync records approximately 1,455 stale `Prefabs/Weapons/Rifles/` references. Preserve imported vanilla corpus; review generated diffs. Do not mix rescan changes into MP-133 research.
