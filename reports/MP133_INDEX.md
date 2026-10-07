# MP-133 — current status and historical research index

> **CURRENT NAVIGATION / EXECUTION STATUS (2026-10-07).** Active Task #1 authority is current branch state plus latest owner evidence in [Issue #34](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34). Historical V1/V2/V3 reports below remain evidence, not instructions. When they disagree with this section, this section wins.

## CURRENT HANDOFF / NEXT TASK

- **Branch:** `t4b/installed-mag-probe`.
- **Functional code checkpoint before this documentation-only sync:** `86da6559e1a7b6dd79f08c4461edb4828fb8147d`.
- **Selective R ownership — OWNER RUNTIME PASS:** T4B context `Priority 20000 / Flags 0xa` keeps character controls and non-T4B weapon behavior intact while physical keyboard R is delivered to `ARMST_MP133_Reload` for the T4B MP-133. The `0x8` Exclusive-only experiment killed the lower control stack and is closed.
- **Custom rack — OWNER RUNTIME PASS:** `R -> T4BRInputDown() -> SetReloadWeapon(1) -> CMD_Weapon_Reload intValue=1 -> Weapon_Rack_Bolt`. Owner trace proved Tube3 `1/3 -> 0/3`, chamber `0 -> 1`, same installed Tube3 identity, and no cmd2..6 in the captured rack run. See Issue #34 comment `6038204788`.
- **G3-B2 one-shell backend — OWNER RUNTIME PASS (offline lab):** repeated one-shell donor -> same installed physical Tube3 transfer, conservation, full 3/3 rejection, busy guard and unchanged chamber flag are proven in Issue #34 comment `5975205409`. Multiplayer/production remain unverified.
- **Protected rack invariant:** do not refactor or replace the proven `SetReloadWeapon(1)` branch while wiring shell reload.
- **Next implementation target:** complementary ASTRA per-shell branch only: when rack is not required and shell load is eligible, enter current ASTRA shell animation and perform exactly one proven G3B2 transfer at the deterministic insert-commit marker; repeat/stop only while valid.
- **GPT Astra task:** Issue #34 comment `6038352310` supersedes `6038288235`. Astra must create a persistent phased plan first at `docs/tasks/MP133_T4B_CUSTOM_R_ASTRA_SHELL_PLAN.md`, commit Phase 0 alone, then execute one phase per commit while maintaining the continuation block. At this checkpoint the plan file does not yet exist.
- **Owner-only runtime:** agents must not launch Workbench/Reforger/Game Mode/Animation Editor or runtime/compile tests.

## Start here in a new agent session

1. Read [`AGENTS.md`](../AGENTS.md) and [`docs/sync/CURRENT_AI_SYNC.md`](../docs/sync/CURRENT_AI_SYNC.md) first.
2. Read the latest [Issue #34](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34) comments. Current key checkpoints are `6038204788` (rack runtime PASS) and `6038352310` (Astra plan-first task).
3. If `docs/tasks/MP133_T4B_CUSTOM_R_ASTRA_SHELL_PLAN.md` exists, use its continuation block as the execution resume point. If it does not exist, the only Astra action is Phase 0: create and commit that plan before implementation.
4. Treat current HEAD/current files as authoritative. Do not reconstruct an older ASTRA intention from model memory, backups, archived reports or older commits.
5. Preserve the working `Flags 0xa` selective-R architecture, the proven `SetReloadWeapon(1)` rack path, the G3B2 transaction safeguards, all GUID/meta identity, and owner-local Workbench work.

## Current verified vs open

| Topic | Current evidence / status |
| --- | --- |
| Selective physical R ownership | **OWNER-RUNTIME PASS** on T4B with `Priority 20000 / Flags 0xa`; controls and non-T4B behavior remain normal. |
| Exclusive-only `0x8` | **RUNTIME FAIL / CLOSED**: suppresses lower character controls broadly. |
| T4B native-equivalent rack | **OWNER-RUNTIME PASS** via `SetReloadWeapon(1)`; cmd1 + `Weapon_Rack_Bolt` + real Tube3→chamber transition, same installed mag identity. |
| G3B2 one-shell transfer | **OWNER-RUNTIME PASS (offline lab)** for repeated donor→same Tube3 transfer, conservation, full rejection, busy guard, delayed verification; MP/production still open. |
| ASTRA shell animation phases/markers | Existing current-head resources/observer contain shell-phase concepts; exact current entry/commit integration must be re-audited from current HEAD, not assumed from historical trigger designs. |
| Custom-R shell dispatcher | **NOT YET IMPLEMENTED**. This is the next active engineering target. |
| Auto-rack after inserting first shell into empty tube | **NOT AUTHORIZED**. Current design leaves chambering to a later explicit R/rack. |
| Native cmd2..6 whole-mag path | **MUST NOT BE REINTRODUCED** into the T4B custom-R architecture. |
| Global `HandleWeaponReloading` override | **REJECTED / DO NOT REOPEN**. |
| Multiplayer/replication/production promotion | **UNVERIFIED / NOT CURRENT GATE**. |

**Intended current dispatcher:**

```
R on T4B
├─ chambered == 0 && Tube3 > 0
│  -> SetReloadWeapon(1)        # proven rack
└─ otherwise, if shell load eligible
   -> ASTRA shell path
   -> one G3B2 transfer at insert commit
   -> repeat/stop safely
```

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
| [`MP133_V3_G3B2_TRANSACTION_DESIGN.md`](MP133_V3_G3B2_TRANSACTION_DESIGN.md) | G3-B2 **design-only** (no code), **rev 2** after review `5973710199`: eligibility/prewrite checks, one-shot state machine `IDLE→PREFLIGHT→DONOR_WRITTEN→TARGET_WRITTEN→COMMITTED` with `REJECTED` (repeatable, no-write) / `INDETERMINATE→QUARANTINED` (new-instance reset only), donor-first order + tradeoff, commit criteria (chamber = `IsCurrentBarrelChambered`/barrel index; muzzle `GetAmmoCount` = supply telemetry only), telemetry, acceptance/negative matrix (mocks call no setter), **packaging = fresh child of production MP-133 with T4b probe + B2 action only** (inherited-action suppression not provable → pre-implementation gate), weapon-installed-donor exclusion + fail-closed storage whitelist, source/uncertainty matrix, implementation allowlist, `GAMEPLAY_FILES_CHANGED_BY_DESIGN=0`. **§11 implementation:** bounded additive lab source + production-child prefab published with `m_bG3b2WriteEnabled=false` and empty donor whitelist — new `ARMST_T4B_G3B2_Transfer.c` (`FE4A1900…`, rev 11) + canonical `ARMST_T4B_G3B2_TestWeapon.et`(`68F67CAB…`) + preflight `…_Preflight_TestWeapon.et`(`DAD5B732…`) + write-test `…_WriteTestWeapon.et`(`BBED7C0E…`) + write-ON `…_WriteOn_TestWeapon.et`(`A9282110…`) + **inventory-wide OFF** `…_InventoryWide_TestWeapon.et`(`4829F51B…`)(`.meta D972C7FA…`, `m_bG3B2InventoryWide 1`, `m_bG3B2WriteEnabled 0`). New opt-in `m_bG3B2InventoryWide` (default false) allows whole-inventory donor search (nested pouches/backpack) while keeping actor-ownership, weapon-installed/weapon-storage exclusion, ammo-type, one-donor (`ambiguous-donor`), latch/quarantine; whitelist mode unchanged. Telemetry adds `storagePolicy`/`inventoryOwnerValid`/`storageSnapshotValid` (exactOwnerMatch = N/A in inventory-wide). Owner evidence `5974314749` (write-OFF exact-owner PASS); `5974730107` task. Status `INVENTORY_WIDE_OFF_SOURCE_PREPARED / LEGACY_FIXTURES_UNCHANGED / COMPILER_UNVERIFIED / NO_B2_WRITES / STOP_FOR_INDEPENDENT_REVIEW`.
- **G3-B2 cleanup (comment 5974842072, 2026-10-04):** lab `Prefabs/Test` reduced to the shared T4b baseline, the donor prefabs (used by the production test world), the retained historical `G3B1_DonorDevice`, and **two** G3-B2 fixtures: Inventory-Wide **OFF** (`4829F51B…`) and new Inventory-Wide **WRITE-ON** (`36640D9D…`, `.meta 6972BC1F…`, `m_bG3B2InventoryWide 1` + `m_bG3B2WriteEnabled 1`, UI `INVENTORY-WIDE WRITE ENABLED`; GUIDs `{78899AABBCDDEEFF}`/`899AABBCDDEEFF00`/`99AABBCDDEEFF011`/`AABBCDDEEFF01122`/`ABBCDDEEFF011223`). **Deleted (unused) .et+.meta pairs:** `G3B1_TestWeapon`, `G3B2_TestWeapon`, `G3B2_Preflight_TestWeapon`, `G3B2_WriteTestWeapon`, `G3B2_WriteOn_TestWeapon` — preserved via Git history and tag `archive/2026-10-04/g3b2-pre-cleanup` (`66c808f4`). Kept-with-reason: `ARMST_T4B_TestWeapon.et` (shared baseline parent, referenced in docs/README/T4b+G3B1 scripts as purpose text), `G3B1_DonorMag.et` + `G3B2_InventoryWide_TestWeapon.et` (**hard refs in production world `ARMST-PLATFORM---Weapons\worlds\Weapon_test\...\default.layer`**), `G3B1_DonorDevice.et` (owner Workbench artefact). Manifest updated; local==published. Status `TWO_ACTIVE_G3B2_FIXTURES / LEGACY_FIXTURES_ARCHIVED / COMPILER_UNVERIFIED / NO_B2_WRITES / STOP_FOR_INDEPENDENT_REVIEW`. |
| [`MP133_G4A_RELOAD_SWAP_ROUTE_AUDIT.md`](MP133_G4A_RELOAD_SWAP_ROUTE_AUDIT.md) | G4-A **read-only** audit + lab-only design: proves the native whole-magazine reload (cmd 2–5/6 → inject/remove clips with `Weapon_Spawn/Attach/MagRelease`) replaces the installed 3-round tube on empty-R and rapid double-R (OWNER-RUNTIME); preferred lab-only fix = lab-owned sanitized-clip graph/ASI (V2 pattern); magwell/resource gate no proven field; input interception = global-hook risk. `READONLY_GAMEPLAY_FILES_CHANGED=0`. `G4A_AUDIT_STATUS_COMPLETE / STOP_FOR_OWNER_REVIEW`. |
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
