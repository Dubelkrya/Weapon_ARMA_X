# MP-133 T4B — Custom R / Astra shell execution plan

## Continuation

```text
LAST_COMPLETED_PHASE = 0
CURRENT_PHASE = 1 (NOT_STARTED)
LAST_SAFE_COMMIT = 6fa72173fff506a73bcc54234d9e4732f7f327cd
CURRENT_BLOCKER = none for source audit; installation is not authorized
NEXT_EXACT_ACTION = After Phase 0 publication, audit current shell entry and transaction ownership; establish safe contract or record bounded blocker before staging.
DO_NOT_REOPEN = input registration/GUID/lifecycle; accepted Flags 0xa; proven SetReloadWeapon(1) rack; rejected global handler; historical tasks/backups
```

LAST_SAFE_COMMIT is the last verified existing predecessor, not a fabricated self-referential SHA. Next phase records the preceding phase commit. On resume verify ancestry and inspect latest plan commit; never reset to this field.

## Current-state snapshot

Date 2026-10-07. Branch `t4b/installed-mag-probe`.
Starting HEAD `6fa72173fff506a73bcc54234d9e4732f7f327cd`; functional checkpoint `86da6559e1a7b6dd79f08c4461edb4828fb8147d`.
Fetched user documentation update and fast-forwarded; gameplay unchanged.

Authority: [6038352310](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6038352310) supersedes 6038288235; [docs sync](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6038536193). AGENTS, current sync, rack audit and source were read before planning. Old unfinished tasks are not execution instructions.

Owner runtime facts (not agent runs):
- [6038204788](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6038204788): custom R -> SetReloadWeapon(1) -> cmd1 -> Weapon_Rack_Bolt; Tube3 1/3 -> 0/3, chamber 0 -> 1, same M1, no cmd2..6 in capture.
- [6038071812](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6038071812): reviewed rack script installed byte-identically.
- [6036068210](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6036068210): accepted Priority 20000 / Flags 0xa and selective R; controls/non-T4B preserved.
- Current sync records [5975205409](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5975205409): G3B2 repeated one-shell donor -> same Tube3, capacity/full/conservation/busy/delayed verification, chamber unchanged. Offline lab proof, not multiplayer proof.

Repo root: `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\Weapon_ARMA_X`.
L = repo `labs/ARMSTMP133T4B_InstalledMagProbe/`.
V = read-only `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMSTMP133T4B_InstalledMagProbe/`.
S = repo `artifacts/astra-rebuild/stageT4BShellDispatcher/`.
PLAN = this file. Optional report = `reports/MP133_TASK1_CUSTOM_R_ASTRA_SHELL_DISPATCH_STAGE.md`.

### Protected actual file SHA-256

Paths relative to L/V. Same means byte-identical, not normalized text.

| Path | L SHA-256 | V SHA-256 |
|---|---|---|
| Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c | F5D59DB9D00469E4664DE219CF29110A40D6DCE73DE23846ED60C44B6EFA68C1 | same |
| Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c | 7BE1D37513AF31E0C5BC3629BC3301DAFABEC966129AF83D04B688DD4D19BF8A | same |
| Scripts/Game/ARMST_T4B/ARMST_T4B_G3B2_Transfer.c | FE4A19008EC290632378C0D3824C5AA7DD82018A761971BFCD920ED1E515FCCF | same |
| Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et | F4A856D8452136C13033B893A1F72E72C1D0D99AF204E782726A66853BCC43F4 | same |
| Prefabs/Test/ARMST_T4B_G3B2_Tube3Mag.et | A4CA7943AD740874846FC6F7B9AD2E77C0C6FA5981602303726090BB8A21BE80 | same |
| Configs/System/chimeraInputCommon.conf | 57778A1D2ED7EDCA8A321CCDF2D5A76A8092E8C0319D0D4ED9DDE07194F60993 | 83E30BC5E1AA72674F6642531A58851DBB2FCBD63DCC248BA0B363175F9167E7 |
| Assets/MP133_AstraShellGraph_test/MP133_Astra2.agf | 55570DE07550E4BE7E41A4FB63D807672701ED42FBBAA71F7C40E27127EA71E8 | 5E569E82473CB91A5B16B3C498B1FCA6B333A43B655A086551C19825A193518D |
| Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr | 8E8BAB3771E0691F5A116AB917A1F506E407245C6CC7E5C8B1DF1ECFCB730FF2 | same |
| Assets/MP133_AstraShellGraph_test/MP133_Astra2.ast | 3A1C9BB03E0DAEB0506C988B03467D2C5B5131DACA5C58321462129F8163234B | F40801F295EED72739DB4642917E3DDC9C58804C01EF96DF8AA2DBDB989CF592 |
| Assets/MP133_AstraShellGraph_test/MP133_Astra2_weapon.asi | 77E2887EE57175D697C226308D6E9349FB53673691AC06E9C9268637D319A72E | 6E7A14514B548F80748030D24BC67355DE3CC3D9CEF6453EFA33792A1960037E |
| Assets/MP133_AstraShellGraph_test/MP133_Astra2_player.asi | 9F850CE79AAF31D33BFB614BFD87961E5ABA511BB462161AF52A333C0546901D | 8A09C99B7D2ECE32F801FC265381314AD1D0D336B928CF89EF35D90E0B808CE7 |

L still has Flags 0x6; V has accepted 0xa. V AST/ASI remove Reload_InsertMag/Reload_RemoveMag mappings retained in L. AGF difference is RackBoltAnim EditorPos only. Never deploy L wholesale onto V. Documentation update did not synchronize gameplay. No correction/synchronization authorized here.

Owner-untracked `reports/CORE_ARMST_READONLY_AUDIT.md` excluded from all commits; SHA256 `924DF1E42AD5C4D1ADA41BA57A1553DB9EE7962BC6488E301B042621F0182B55`.

## Target architecture / invariants

```text
R on equipped T4B
  chamber empty AND Tube3 > 0 -> EXISTING PROVEN RACK UNCHANGED
  otherwise eligible -> current Astra Start -> Grab -> Insert
    -> one authenticated commit token -> proven G3B2 transaction
    -> verified continuation or End
  otherwise -> fail closed
```

No auto-rack-after-shell; chambering remains a later independent R. Shell branch generates no cmd1..6 and no whole-mag reload/chamber mutation. Preserve rack helper/constant/semantics, input lifecycle, firing, inspection, switching, idle, safety, modes, IK and clip identities. No extra key/toggle/parallel reload system.

One authoritative transaction owner. Preserve donor uniqueness/membership, installed target entity/component, capacity 3, ammo type, donor-first ordering, conservation, latch, immutable op token, +250/+1000 verification and terminal quarantine. No blind partial-write retry/refund. Client marker is not server authorization. Repeat waits for transaction verification, not merely clip completion. Stop on full/no donor/weapon switch/tube replacement/invalid state/interruption. Do not execute a committed insertion twice.

No speculative setters or character-to-weapon propagation assumptions. CURRENT HEAD wins over historical instructions, while owner live modifications are separately protected.

## Phase table

Every phase sets IN_PROGRESS before work, updates actual results/decisions/continuation, then commits/pushes separately. Never batch architectural phases.

### PHASE_ID = 0

- STATUS = DONE.
- GOAL: Persistent plan before implementation.
- INPUT_FILES: AGENTS.md; current sync/index; rack audit; current scripts/prefab/graph and owner comments.
- FILES_ALLOWED_TO_CHANGE: PLAN only.
- EXACT_INTENDED_CHANGE: Record baseline, phases and continuation; commit/push plan alone.
- INVARIANTS_TO_PRESERVE: all target invariants above; L/V/Core/Weapons/meta unchanged; rack protected.
- STATIC_ACCEPTANCE: Plan-only diff; mandatory fields and source hashes.
- OWNER_RUNTIME_ACCEPTANCE: None.
- ROLLBACK: do not install staged files; retain current sources/history. Documentation-only phases need no gameplay rollback. After separately authorized install, stop on failure and request forward correction, never historical restoration.
- NEXT_PHASE: 1.

### PHASE_ID = 1

- STATUS = NOT_STARTED.
- GOAL: Current-source shell entry and integration contract.
- INPUT_FILES: Current input/observer/G3B2/prefab/AGR/AGF/AST/P-W ASI/clips; installed SDK.
- FILES_ALLOWED_TO_CHANGE: PLAN; optional phase report.
- EXACT_INTENDED_CHANGE: Trace supported producer -> graph -> W marker -> authoritative transaction. Resolve source/live differences, API ownership, cancellation and verification timing before staging.
- INVARIANTS_TO_PRESERVE: all target invariants above; L/V/Core/Weapons/meta unchanged; rack protected.
- STATIC_ACCEPTANCE: Exact API declarations/callsites; entry and receiver provenance; explicit blocker rather than speculative API.
- OWNER_RUNTIME_ACCEPTANCE: Stop for owner if source cannot establish a safe entry; no probe without review.
- ROLLBACK: do not install staged files; retain current sources/history. Documentation-only phases need no gameplay rollback. After separately authorized install, stop on failure and request forward correction, never historical restoration.
- NEXT_PHASE: 2.

### PHASE_ID = 2

- STATUS = NOT_STARTED.
- GOAL: Staged complementary dispatcher.
- INPUT_FILES: Phase 1 contract; CURRENT HEAD CustomRInputProbe.c.
- FILES_ALLOWED_TO_CHANGE: PLAN; S/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c; report.
- EXACT_INTENDED_CHANGE: Add shell-only eligibility/request in non-rack case; keep existing rack helper/constant/behavior untouched. Intermediate candidate not installable alone.
- INVARIANTS_TO_PRESERVE: all target invariants above; L/V/Core/Weapons/meta unchanged; rack protected.
- STATIC_ACCEPTANCE: Rack helper and lifecycle byte comparison; zero new native reload or ammo/chamber writes.
- OWNER_RUNTIME_ACCEPTANCE: Deferred until complete reviewed candidate.
- ROLLBACK: do not install staged files; retain current sources/history. Documentation-only phases need no gameplay rollback. After separately authorized install, stop on failure and request forward correction, never historical restoration.
- NEXT_PHASE: 3.

### PHASE_ID = 3

- STATUS = NOT_STARTED.
- GOAL: Reusable proven G3B2 transaction.
- INPUT_FILES: CURRENT HEAD ARMST_T4B_G3B2_Transfer.c; SDK; Phase 1 contract.
- FILES_ALLOWED_TO_CHANGE: PLAN; S/Scripts/Game/ARMST_T4B/ARMST_T4B_G3B2_Transfer.c; report.
- EXACT_INTENDED_CHANGE: Extract shared TryTransferOneShell(character,weapon) service inside current file, preserve UserAction adapter and all checks. Persistent per-weapon state, never new service per marker. Distinguish rejected/pending/verified/quarantined results.
- INVARIANTS_TO_PRESERVE: all target invariants above; L/V/Core/Weapons/meta unchanged; rack protected.
- STATIC_ACCEPTANCE: Compare mutation/check bodies; only one writer; preserve donor-first, busy latch, immutable callback token, delayed verification, ownership and quarantine; bounded locals/expressions.
- OWNER_RUNTIME_ACCEPTANCE: Offline proof not MP proof; authority/replication requires separate owner evidence.
- ROLLBACK: do not install staged files; retain current sources/history. Documentation-only phases need no gameplay rollback. After separately authorized install, stop on failure and request forward correction, never historical restoration.
- NEXT_PHASE: 4.

### PHASE_ID = 4

- STATUS = NOT_STARTED.
- GOAL: Astra event/commit coordinator.
- INPUT_FILES: CURRENT HEAD observer, clips and Phase 1 contract; staged service.
- FILES_ALLOWED_TO_CHANGE: PLAN; S/Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c; S/Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et only if justified; report.
- EXACT_INTENDED_CHANGE: Bind request/session/cycle to actor+weapon+installed tube; one validated W commit token calls service. Reject duplicates and P marker copies; verified transaction controls continuation; safe cancellation.
- INVARIANTS_TO_PRESERVE: all target invariants above; L/V/Core/Weapons/meta unchanged; rack protected.
- STATIC_ACCEPTANCE: No direct setters in observer; native parent forwarding intact; missing/out-of-order/duplicate markers fail closed; no refund/retry after committed cancellation.
- OWNER_RUNTIME_ACCEPTANCE: Owner must establish marker delivery and exact-one transfer after explicit install GO.
- ROLLBACK: do not install staged files; retain current sources/history. Documentation-only phases need no gameplay rollback. After separately authorized install, stop on failure and request forward correction, never historical restoration.
- NEXT_PHASE: 5.

### PHASE_ID = 5

- STATUS = NOT_STARTED.
- GOAL: Graph necessity gate.
- INPUT_FILES: CURRENT HEAD graph bundle, live differences, coordinator contract.
- FILES_ALLOWED_TO_CHANGE: PLAN; individually justified S/Assets/MP133_AstraShellGraph_test graph copies; report; NO meta/clips.
- EXACT_INTENDED_CHANGE: First decide NO_CHANGE if current graph suffices. Otherwise minimum shell-only entry/wait/exit delta; never whole graph replacement.
- INVARIANTS_TO_PRESERVE: all target invariants above; L/V/Core/Weapons/meta unchanged; rack protected.
- STATIC_ACCEPTANCE: Parsed equality of non-shell rack/fire/idle/safety/inspection/modes/IK; source identities preserved; no repeat while transaction pending; references resolve.
- OWNER_RUNTIME_ACCEPTANCE: Owner-only graph compile/visual P-W verification.
- ROLLBACK: do not install staged files; retain current sources/history. Documentation-only phases need no gameplay rollback. After separately authorized install, stop on failure and request forward correction, never historical restoration.
- NEXT_PHASE: 6.

### PHASE_ID = 6

- STATUS = NOT_STARTED.
- GOAL: Static preservation and publication review.
- INPUT_FILES: Complete staged set; source hashes; SDK; repository tests.
- FILES_ALLOWED_TO_CHANGE: PLAN; report only; functional fixes return to relevant phase.
- EXACT_INTENDED_CHANGE: Produce provenance ledger and exact installation allowlist; compare original/staged/protected hashes, tokens, gates and forbidden callsites. Force-add only exact authorized ignored stage files.
- INVARIANTS_TO_PRESERVE: all target invariants above; L/V/Core/Weapons/meta unchanged; rack protected.
- STATIC_ACCEPTANCE: No L/V/Core/Weapons/meta edits; rack unchanged; no cmd2..6/global handler/whole-mag/chamber writes; report existing Python failures honestly.
- OWNER_RUNTIME_ACCEPTANCE: No runtime claim; candidate ready for review only.
- ROLLBACK: do not install staged files; retain current sources/history. Documentation-only phases need no gameplay rollback. After separately authorized install, stop on failure and request forward correction, never historical restoration.
- NEXT_PHASE: 7.

### PHASE_ID = 7

- STATUS = NOT_STARTED.
- GOAL: Owner install/compile/runtime handoff.
- INPUT_FILES: Published candidate commit/manifest and current owner baseline.
- FILES_ALLOWED_TO_CHANGE: PLAN/report only until NEW explicit install authorization.
- EXACT_INTENDED_CHANGE: Mark BLOCKED_OWNER. Request review/install GO; never deploy labs wholesale. Give owner exact files and expected logs. Resume only from owner result.
- INVARIANTS_TO_PRESERVE: all target invariants above; L/V/Core/Weapons/meta unchanged; rack protected.
- STATIC_ACCEPTANCE: Commit/hashes and narrow install list complete; working input 0xa and cleaned live mappings preserved.
- OWNER_RUNTIME_ACCEPTANCE: Owner compiles after GO; one shell gives donor -1/tube +1/same Tube3/unchanged chamber/one commit/delayed PASS. Then full/no donor/busy/duplicate/interrupt/switch; subsequent independent R racks; controls/non-T4B unchanged. Stop on compile failure/cmd2..6/detach/conservation failure. MP remains separately unproven.
- ROLLBACK: do not install staged files; retain current sources/history. Documentation-only phases need no gameplay rollback. After separately authorized install, stop on failure and request forward correction, never historical restoration.
- NEXT_PHASE: Review owner evidence and explicit follow-up.

## Decision log

### D1 — authority

- DECISION: latest docs/source/owner proof supersede old double-fire and rack-unproven conclusions.
- EVIDENCE: 6fa7217 sync, 6038204788.
- ALTERNATIVES_REJECTED: reopen registration/suppression; historical graph recovery; previous neutralization task.
- WHY: those tasks are superseded; rack is protected runtime-PASS.

### D2 — source/live separation

- DECISION: record L/V divergences without synchronizing either.
- EVIDENCE: actual hashes and diffs above.
- ALTERNATIVES_REJECTED: wholesale labs installation, copying live into repo without authority.
- WHY: avoid undoing owner input/graph changes; clarify any graph baseline conflict before staging it.

### D3 — transaction owns continuation

- DECISION: preserve delayed G3B2 verification and quarantine; determine graph waiting contract before implementation.
- EVIDENCE: current G3B2 unlocks after +250/+1000 samples; current observer emits diagnostic_candidate_no_transfer.
- ALTERNATIVES_REJECTED: copy two setters into animation callback, unlock at clip end, client-side ammo mutation.
- WHY: those bypass proven busy/conservation/ownership guarantees.

## Actual results and provenance ledger

Phase 0: plan only; no functional candidate. Phase 0 publication confirmed by Git result, not assumed from file creation.
For EVERY staged file append: SOURCE_PATH / SOURCE_HEAD / SOURCE_SHA256 / STAGED_PATH / STAGED_SHA256 / FUNCTIONAL_DIFF. No staged files exist yet.

Baseline static checks: addon resolver PASS; Python 96 tests, 2 failures/10 errors; integrity 10 existing broken links, before plan creation. Never restore historical fixtures merely to appease old tests; repository-wide green is not claimed.

All phases prohibit Workbench/Reforger/Game Mode/Animation Editor/Enfusion executable launch by agent. No compile/runtime test. No git reset/revert/restore/clean/cherry-pick/rebase/historical checkout. No meta staging/GUID invention. No live edits.

