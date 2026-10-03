# MP-133 — V3 current status and historical research index

> **CURRENT NAVIGATION / DESIGN STATUS (2026-10-03).** This is a map of evidence, not proof of a finished V3. For any disagreement use current live-addon/owner Workbench evidence first, then [KNOWLEDGE_STATUS.md](KNOWLEDGE_STATUS.md). The [tracking Issue #27](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27) records approvals, owner observations and STOP conditions.

## CURRENT HANDOFF / NEXT TASK (overrides historical statuses below)

- **G2 offline owner-run:** original T4b synthetic +1 → same physical installed magazine → manual short-R and native chamber → owner-reported single shot. No hit/damage or MP proof.
- **G3-A:** [read-only donor/transaction audit](MP133_V3_G3_REAL_DONOR_PHASE_A.md) published at `eb2b323`. Two setters remain non-atomic.
- **G3-B1 PASS (owner runtime):** one real carried 12ga donor magazine decremented via the child lab weapon `ARMST_T4B_G3B1_TestWeapon.et` (write enabled `m_bG3b1WriteEnabled 1`), donor `n→n-1` persisted +250 ms/+1 s with the same item/mag identity, installed target excluded, duplicate → `already-used`. Source in the **same existing T4b addon**; T4b diagnostic script and owner-saved prefab unchanged. No new T4c addon.
- **G3-B2 (one donor round → SAME installed magazine):** design **approved** (rev 2, review `5973766922`); **bounded source preparation** published (write OFF) per task `5973770796`. Read-only design + implementation record: [`MP133_V3_G3B2_TRANSACTION_DESIGN.md`](MP133_V3_G3B2_TRANSACTION_DESIGN.md). New additive lab files: `Scripts/Game/ARMST_T4B/ARMST_T4B_G3B2_Transfer.c` + `Prefabs/Test/ARMST_T4B_G3B2_TestWeapon.et`(+`.meta`) — a thin child of the production MP-133 with the T4b probe and **only** the B2 action, `m_bG3b2WriteEnabled=false`, empty donor whitelist. **No Workbench/game run; B2 write-enabled / two-sided owner test, animation/R/input, MP and production are NOT authorised** until independent source review and the owner's separate go-ahead. A Core RPC-repacking candidate from an unpublished local report remains unverified ([#33](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/33)); Core SHIFT+R reload is not working.
- **G4/G5:** not authorised.
- **Coordination:** experimental branch `t4b/installed-mag-probe` owns active G3 work. Documentation PR [#31](https://github.com/Dubelkrya/Weapon_ARMA_X/pull/31) must reconcile overlapping index/sync changes before any merge. Catalog #28 and CI #29 are done. Astra remains paused; historical T4a/T2a/V2/P2 are not current active MP-133 labs.

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
| Core interaction | **NOT TESTED IN T0**: Core was not loaded; owner states Core SHIFT+R reload is nonfunctional; legacy references are not an active integration requirement. |
| Legacy V2 global R regression | **P2 OWNER-RUNTIME**: excluding the old global `modded SCR_CharacterCommandHandlerComponent` restored ordinary R on other pumps. The exact `super`/native failure mechanism is unknown. |
| Owner's native-event edit | Visible chamber-insert behavior reportedly recovered after restoring `Weapon_SpawnMagazine/AttachMagazine/MagRelease` in a lab clip. This is **not** proof of magazine continuity, chamber correctness or ammo conservation. |
| Chung's animation reference | Provided AGF/AGR/AST, player/weapon ASI, code and selected player-event screenshots support separate pump, grab, insert and safe stop/continue paths. Actual player→weapon event routing and possible duplicate commit are **UNRESOLVED**. |
| T1 input routing | **READ-ONLY DESIGN PUBLISHED**; stock R action name, short/hold edge arbitration and whether a listener can suppress native reload remain unproven. |
| T2 event routing | **READ-ONLY DESIGN PUBLISHED**; diagnostic player-only, weapon-only and paired-marker experiments proposed; no test code or asset edit authorized. |
| V3 actual code | **NOT AUTHORIZED / NOT IMPLEMENTED**. Real one-shell server transaction, once-only commit, safe stop, network and low-FPS tests are future gates. |

**Intended V3 controls, not current T0 behavior:** short R performs the necessary verified native pump (if required) and then per-shell tube loading; a second short R or trigger requests safe stop; hold R preserves native inspection; legacy Core SHIFT+R reload is not a functioning dependency. If standard R cannot be intercepted without affecting native behavior, a separate load action is a possible fallback **only after the owner's decision**.

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
| [`MP133_V3_T3_MAG_IDENTITY_TRACE.md`](MP133_V3_T3_MAG_IDENTITY_TRACE.md) | T3 lab-only passive `[ARMST_T3-MAG]` physical-magazine identity trace (mag entity reference tags, ammo/max, chamber) around the native magazine lifecycle; getter-only, installed-SDK verified, one owner native-R swap to run. |
| [`MP133_V3_T3F_FIRE_EVENT_AUDIT.md`](MP133_V3_T3F_FIRE_EVENT_AUDIT.md) | T3F fire-event audit (Phase A): no weapon-level actual-shot callback in the installed SDK (real-shot signals are muzzle-effect `OnFired`/`OnWeaponFired`); limited Phase B `[ARMST_T3F-FIRE]` passive trace (animation events + ammo/chamber sample; no `gameplay_shot`, delta-evidenced). |
| [`MP133_V3_T4_ONE_SHELL_TRANSFER.md`](MP133_V3_T4_ONE_SHELL_TRANSFER.md) | T4 Phase A (read-only): installed SDK exposes only `BaseMagazineComponent.SetAmmoCount(int)` as a magazine-ammo writer; no atomic transfer / legitimate donor consumption / authority / rollback → `T4_API_OR_TRANSACTION_BLOCKED`; minimal next experiment proposed. |
| [`MP133_V3_T4A_SETAMMOCOUNT_SEMANTICS.md`](MP133_V3_T4A_SETAMMOCOUNT_SEMANTICS.md) | T4a isolated lab (`ARMSTMP133T4A_SetProbe`) testing `SetAmmoCount` on a **disposable** magazine via a dedicated action (`ARMST_T4A_SETTER_ACTION`, key P): one-shot guarded +1 with pre/post/reject logs and identity check; no transfer/donor/inventory. `T4A_LAB_PREPARED_OWNER_RUN_REQUIRED`. |
| [`MP133_V3_T4B_INSTALLED_MAG_PROBE.md`](MP133_V3_T4B_INSTALLED_MAG_PROBE.md) | T4b isolated lab (`ARMSTMP133T4B_InstalledMagProbe`): synthetic `+1` into the **already-installed** lab-magazine via `GetCurrentMagazine().SetAmmoCount(old+1)`; weapon-local context action (`ActionsManagerComponent {A29AE67FF4D82B0F}` + `additionalActions +{ … ParentContextList { "default" } … }`), baseline probe, `sameMagazine/sameOwner/chamberUnchanged` logs; no detach/replace/donor/inventory. `T4B_LAB_PREPARED_OWNER_RUN_REQUIRED`. §15/§16 add G3-B1: inventory-donor consume via the child lab weapon `ARMST_T4B_G3B1_TestWeapon.et` (action "G3B1: consume 1 from inventory donor", `[ARMST_T4B-G3B1]`); server-only, strict ammo-type, single-donor; `G3B1_SOURCE_PUBLISHED / PRE_RUNTIME_SOURCE_CORRECTIONS_APPLIED / OWNER_GAME_NOT_RUN`. |
| [`MP133_V3_VARIANT_A_ARCHITECTURE.md`](MP133_V3_VARIANT_A_ARCHITECTURE.md) | Owner decision (Variant A: custom per-shell reload preserving the physical magazine; replaceable transfer backend) + the three independent parts and gates `G0–G5`, with strict stop-after-each-gate review. Documentation only. historical design checkpoint; G2 owner runtime and G3-B1 source publication supersede its pending status. |
| [`MP133_V3_G3_REAL_DONOR_PHASE_A.md`](MP133_V3_G3_REAL_DONOR_PHASE_A.md) | G3 Phase A read-only audit: donor discovery/ownership/ammo-compat via installed SDK inventory APIs, setter/observer and transaction feasibility, failure/concurrency matrix (`REJECTED/COMMITTED/INDETERMINATE`), adapter boundary and one proposed owner-only G3-B test. G3-A report published, G3-B1 donor-only fixture published; owner runtime is pending, real two-sided transfer unimplemented. |
| [`MP133_V3_G3B2_TRANSACTION_DESIGN.md`](MP133_V3_G3B2_TRANSACTION_DESIGN.md) | G3-B2 **design-only** (no code), **rev 2** after review `5973710199`: eligibility/prewrite checks, one-shot state machine `IDLE→PREFLIGHT→DONOR_WRITTEN→TARGET_WRITTEN→COMMITTED` with `REJECTED` (repeatable, no-write) / `INDETERMINATE→QUARANTINED` (new-instance reset only), donor-first order + tradeoff, commit criteria (chamber = `IsCurrentBarrelChambered`/barrel index; muzzle `GetAmmoCount` = supply telemetry only), telemetry, acceptance/negative matrix (mocks call no setter), **packaging = fresh child of production MP-133 with T4b probe + B2 action only** (inherited-action suppression not provable → pre-implementation gate), weapon-installed-donor exclusion + fail-closed storage whitelist, source/uncertainty matrix, implementation allowlist, `GAMEPLAY_FILES_CHANGED_BY_DESIGN=0`. **§11 implementation:** bounded additive lab source + production-child prefab published with `m_bG3b2WriteEnabled=false` and empty donor whitelist — new `ARMST_T4B_G3B2_Transfer.c` (`088E6250…`, rev 3) + `ARMST_T4B_G3B2_TestWeapon.et`(`68F67CAB…`)(`.meta 315C7AB6…`); no Workbench/game run; `B2_SETTER_CALLS_IN_DRY_RUN=0`. Source-review corrections `5973836821` and `5973901925` applied: canonical attribute spelling, shared read-only preflight (incl. `IsBaselineDone` baseline-ready), actual donor storage-component/owner identity, fail-closed delayed checks (membership + target-still-installed + real current weapon + ammo-type), numeric/chamber/second-stage guards, null-safe post-setter semantics. Status `G3B2_DESIGN_APPROVED / G3B2_BOUNDED_SOURCE_PREPARATION_AUTHORIZED / B2_WRITE_ENABLED_RUN_NOT_AUTHORIZED`; source re-review pending. |
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

1. **G3-B1 code reviewer:** inspect `a165e80` lab-only donor fixture, exact SDK signatures, single non-R action, one-shot guard, inventory-owner/slot/identity checks, source manifest and effects on the owner-saved T4b prefab. Do not alter code without a specific reviewed defect.
2. **Owner:** after source review, compile and test G3-B1 in Workbench/game; provide pre/post/+250 ms/+1 s donor ammo and identity, inventory/slot/UI, unchanged weapon magazine/chamber and any script errors. Do not begin two-sided transfer until evidence reviewed.
3. **G3-B2:** separately propose a bounded single donor→installed-magazine trial after B1; `REJECTED / COMMITTED / INDETERMINATE` and no automatic retry for partial transfer.
4. **Docs/Core agents:** reconcile PR #31 against this active branch and verify the unpublished local Core report in its own read-only direction; do not assume Core SHIFT+R or RPC repacking already solves the installed-magazine case. Astra paused and protected.
