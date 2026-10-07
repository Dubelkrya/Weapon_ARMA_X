# MP-133 T4B — Custom R / Astra shell execution plan

## Continuation

```text
LAST_COMPLETED_PHASE = 1F (P-owner + inspection discovery) ; 1G staged
CURRENT_PHASE = 1G (P-OWNER RUNTIME DIAG STAGE) — read-only diagnostic staged, awaiting owner review
LAST_SAFE_COMMIT = d20cbcc8337b50d99ea4025f9185b3601199f51b
CURRENT_BLOCKER = P owner unresolved (CharacterAnimGraphComponent runtime-unavailable); AnimationControllerComponent candidate staged for a read-only runtime check. Inspection regression leading cause = input-context, unproven.
NEXT_EXACT_ACTION = Owner reviews the 1G report (complete diff) and, if acceptable, authorizes install + one qualified shell R to capture [ARMST-T4B-POWNER]; plus owner-only inspection A/B. No install/runtime by agent.
DO_NOT_REOPEN = input registration/GUID/lifecycle; accepted Flags 0xa; proven SetReloadWeapon(1) rack; rejected global handler; character-root variable setter; native-reload P activation; W->P propagation assumption
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

### PHASE_ID = 1A — P/W BINDING PROBE

- STATUS = BLOCKED_SOURCE.
- GOAL: one animation-only normal-R cycle on BOTH P and W, no physical mutation.
- INPUT_FILES: current source at 32f4f72e1a1cbd7eeb77b2d7a3bde1d3ae5eb581; installed SDK in both documentation trees; current prefab/graph read-only.
- FILES_ALLOWED_TO_CHANGE: PLAN/report; only staged CustomRInputProbe.c, AstraV2_WeaponAnimationComponent.c and one optional T4B helper under artifacts/astra-rebuild/stageT4BPWBindingProbe/Scripts/Game/ARMST_T4B/.
- EXACT_INTENDED_CHANGE: first prove W and P bind/set/read callable ownership; then minimal single-cycle request/reset and bounded session-tagged evidence, only in complementary non-rack state.
- INVARIANTS_TO_PRESERVE: rack helper/call/conditions frozen; no graph/prefab/input/meta/labs/live/G3B2 edits or G3B2 calls; no ammo/chamber/inventory writers, no native reload command from probe.
- STATIC_ACCEPTANCE: exact SDK signatures and owning object acquisition for both sides; handles/lifetime/reset source-backed; no W-only candidate; preserve protected hashes; no guessed timers or APIs.
- OWNER_RUNTIME_ACCEPTANCE: NOT AUTHORIZED TO RUN. After separate review/install GO, exactly one normal R in non-rack state must show attributable P AND W Start/Grab/Insert/End-or-ReturnReady, deterministic reset, same Tube3 and unchanged tube/donor/chamber; zero cmd1 from probe, zero cmd2..6, no detach/spawn, controls/non-T4B preserved. Either side missing is FAIL.
- ROLLBACK: do not install staged files; no historical restoration.
- NEXT_PHASE: BLOCKED_OWNER after qualified preparation, or BLOCKED_SOURCE if P API gate fails; never Phase 2/3/4 from this GO.

Authority: [6038870461](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6038870461). This narrower subphase overrides broader implementation allowlists for this run. No graph synchronization in either direction.

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

- STATUS = BLOCKED_SOURCE.
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

## Phase 1 actual findings / stop checkpoint

Phase 0 was committed and pushed alone as `e9dcfb97008bdca6cb1d6a484512474a5870e7e2`. Phase 1 read-only work follows that publication. No functional candidate has been staged; phases 2–7 remain NOT_STARTED.

### D4 — correction: weapon-local setters DO exist in the inspected SDK

- DECISION: reject the old blanket claim that WeaponAnimationComponent has no variable setters. Do not repeat that conclusion from its Reforger-only member page.
- EVIDENCE: installed `Workbench/docs/ArmaReforgerScriptAPIPublic/html/hierarchy.html` rows 6/6_0/6_0_5 give AnimationControllerComponent -> BaseItemAnimationComponent -> WeaponAnimationComponent. Separate `Workbench/docs/EnfusionScriptAPI/html/interfaceAnimationControllerComponent.html` inherits BaseAnimationControllerComponent. That engine API documents `int BindBoolVariable(string)`, `void SetBoolVariable(int,bool)`, `bool GetBoolVariable(int)`, plus BindAttachment/BindAttBoolVariable/SetAttBoolVariable. Both documentation trees must be read together. Installed engine API file timestamp 2026-09-19; Doxygen footer is NOT game version.
- ALTERNATIVES_REJECTED: invent methods; conclude absence from a cross-package-incomplete member list; use character-root BindVariableBool again.
- WHY: a direct weapon-instance variable write is a source-backed candidate. This is not proof that the separately injected P graph receives the same write. No compiler or runtime claim is made.

Official cross-check: [Reforger hierarchy](https://community.bistudio.com/wikidata/external-data/arma-reforger/ArmaReforgerScriptAPIPublic/hierarchy.html), [engine controller API](https://community.bistudio.com/wikidata/external-data/arma-reforger/EnfusionScriptAPIPublic/interfaceBaseAnimationControllerComponent.html). Local installed declarations remain the implementation reference.

### D5 — architecture correction: Chungus does not prove a custom pre-reload P accessor; P-accessor search DEFERRED

- DECISION: mark the special P-controller-accessor search `DEFERRED / NOT REQUIRED YET`; make a W-local request propagation probe the immediate next step.
- EVIDENCE: Issue #34 comment [6039392248](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6039392248) (current architecture authority, supersedes 6039128706 as immediate action) after re-reading the raw Chungus sources.
- FINDING: Chungus enters its shell workflow through the vanilla reload pipeline; only after the running reload emits `StartReloadTimer` does `BC_PumpShotgunComponent.InitReloadSequence()` call `InitPlayerAnimVariables()`, binding/writing character-side variables through ordinary `CharacterAnimationComponent` and weapon-side variables directly on `WeaponAnimationComponent`. It therefore demonstrates separate W-local and character-side variable control, but does NOT prove that an arbitrary custom T4B shell request can address our P injection before a native reload has activated/synchronized it.
- ALTERNATIVES_REJECTED: keeping Phase 1A as authoritative; Chungus `ReloadWeapon()` / `SetAmmoCount` / dummy +1 / fallback magazine spawn/attach / native-reload dependence (NON-PORTABLE, forbidden); reopening P-controller discovery now.
- WHY: the smaller next step is a bounded animation-only W-local propagation probe (Phase 1C) that tests whether weapon-local setters can drive the current P+W shell graph without any direct P setter and without native reload.

### Current graph and actual integration gap

- Current prefab binds W and character `AnimInjection` to MP133_Astra2.agr, separate W/P ASIs, BindingName `Weapon`, BindWithInjection 1. This establishes resources, not script-side variable propagation direction.
- Current AGR declares ShellRequest/Repeat/Stop/Eligible/FireStop. Current AGF line 221 consumes ShellRequest for Idle -> AstraShell and line 237 waits for request reset. Thus the variable is genuinely present NOW, not something to restore from history. It still needs correct P AND W ownership.
- Current observer lines 85–120 tracks phases; insert marker yields only `diagnostic_candidate_no_transfer`. It contains no entry setter or G3B2 call.
- Current W InsertShell TXA line 2395 contains `ASTRA_ShellInsertCommit_W` at frame 11. ASI binds the imported W clip; source marker presence is not fresh runtime delivery proof.
- CharacterAnimationComponent derives from BaseAnimPhysComponent, a different API family. Its BindVariableBool targets character root. Existing [owner evidence 5983965875](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983965875) showed root player_main lacks ASTRA_ShellRequest. This historical observation explains an API ownership failure only; its old task/graph instructions are NOT resumed. Current inspection has not established a replacement injection-targeted setter callsite.
- Engine BindAttachment/BindAttBoolVariable is a candidate only after proving WHICH controller owns the actual character Weapon attachment. Do not call BindAttachment("Weapon") on the weapon controller merely because the prefab uses that binding name on the character, and do not reinterpret an integer engine handle as TAnimGraphVariable.
- Search of current T4B, Weapons and Core scripts found no BindAttBoolVariable/SetAttBoolVariable/BindAttachment/BindBoolVariable callsite proving this P-W route. This is a bounded negative result, not proof the engine cannot do it.

### G3B2 extraction contract retained for subsequent phase

Current transaction is inside ScriptedUserAction and uses GetOwner() as action weapon. A reusable service must replace that ownership dependency with an explicit bound weapon and keep actor current-weapon equality. The current fixture has no G3B2 action to invoke; calling PerformAction opportunistically is not an integration architecture.

Current G3B2 scans actual carried inventory, excludes installed magazines/weapon storage, requires one compatible donor, rechecks before writes, decrements donor before incrementing the same installed target, and quarantines indeterminate writes. Server gate alone is not an authenticated client request path. Preserve all these bodies and their delayed sample tokens in any later extraction.

Important loop constraint: current CheckContinue TXA is six frames at 30 fps, while transaction latch is released only after successful +250 and +1000 ms samples. A blind repeat=true can enter another cycle before verification and/or quarantine legitimate later count changes. Design a verified-wait shell condition or end after a single verified cycle before enabling repeat; do not remove the proven delay/latch. No graph change made.

### Why Phase 1 stops before staging

The missing contract is narrow: how a weapon-local request controls BOTH current W and P injected instances without the failed character-root bind, native reload commands or global graph edits. Direct W API availability resolves half, not the whole mechanism. A W-only animation plus real ammo writes would not satisfy synchronized reload. Also, any graph candidate sourced from Git must not reintroduce live-removed mag mappings on installation.

Requested owner decision: confirm authoritative current graph bundle for future staging and provide an existing injection-targeted API/example if available; alternatively explicitly authorize a bounded animation-only P-W binding probe. No extra physical key or toggle, no ammo transfer, no input registration changes. This is a new gate, not permission to rerun the obsolete ASTRA PROBE action.

If a probe is separately approved/prepared: owner reviews exact stage diff, separately authorizes installation, compiles manually, equips canonical T4B in a shell-eligible non-rack state, and issues one normal R. Required evidence is independently attributable P and W shell start/phase/return-ready plus request reset, same Tube3/count/chamber and zero cmd2..6. A successful W setter/readback alone is not PASS. Stop on compile error, missing P/W side, failed reset, any physical mutation or control regression. No agent editor/runtime launch. Do not execute this protocol on current files: no probe candidate exists yet.

### Preservation result

Fresh task baseline and post-audit aggregate hashes match (sorted full-path + file SHA256 rows; extensions c/conf/et/meta/layer/gproj/agr/agf/asi/ast/txa/anm):

| Root | Files | Before = after SHA256 |
|---|---:|---|
| V | 105 | C54B383CA5ECFFC200A8ADB7A3624CD3E1F0BBF7BB47AA56AB8F2451D566E03D |
| ARMST-PLATFORM---Core | 5521 | 2EDF4D1DCA02F0C662AE1CA567D8B9655C374BC817883B7625A7AF02D8860B4B |
| ARMST-PLATFORM---Weapons | 1584 | A7C611FE0417F5A5E1DA6E4209F01E3CF846295E9ADA57999713FF1B4CC2AECF |
| repository labs | 58 | 505C52A752D320DC69DD4E53E297AF87EF10ECC622AC04CDB07D2FEBC38D644C |
| stageCustomRInput (existing, untouched) | 3 | E6481B8AB4E62B987F0D0CDFA5582C5D244A2A558C96BF1C2528068FE847F4C6 |

GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0. CURRENT_LABS_CHANGED=NO; LIVE_CHANGED=NO; PROVEN_RACK_BRANCH_CHANGED=NO; HISTORICAL_FILE_ROLLBACK=NO; OLD_TASK_RESURRECTED=NO. WORKBENCH_LAUNCHED=NO; REFORGER_LAUNCHED=NO; GAME_MODE_LAUNCHED=NO; RUNTIME_TEST=NO; COMPILE_TEST=NOT_RUN_BY_AGENT.

## Phase 1A result — T4B_PW_BINDING_PROBE_BLOCKED_SOURCE

Authority: 6038870461. CURRENT_HEAD_BASE = 32f4f72e1a1cbd7eeb77b2d7a3bde1d3ae5eb581. Plan-only preparation commit 5fa37e9 preceded this API gate. Parent Phase 1 is NOT DONE. No staged script, helper or staging directory was created; source/staged hash ledger has zero candidate rows. No W-only candidate was written.

### Exact API audit

Installed docs root: `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs`.

| Owner / installed HTML | Exact callable signatures | Finding |
|---|---|---|
| EnfusionScriptAPI/html/interfaceBaseAnimationControllerComponent.html | `proto external int BindBoolVariable(string varName)`; `proto external void SetBoolVariable(int varId, bool value)`; `proto external bool GetBoolVariable(int varId)` | W path exists through weapon component inheritance, as established in D4. |
| Same engine class | `proto external int BindAttachment(string attachmentName)`; `proto external int BindAttBoolVariable(int attachmentName, string varName)`; `proto external void SetAttBoolVariable(int attachmentName, int varId, float value)`; `proto external bool GetAttBoolVariable(int attachmentName, int varId)` | Attachment access exists, but requires the correct owning controller. Note documented setter value is FLOAT, not bool; do not silently rewrite its signature. |
| ArmaReforgerScriptAPIPublic/html/interfaceChimeraCharacter.html | `proto external CharacterAnimationComponent GetAnimationComponent()` | Returns character physics-animation API, not the engine controller type above. |
| ArmaReforgerScriptAPIPublic/html/interfaceBaseAnimPhysComponent.html | `proto external TAnimGraphVariable BindVariableBool(string pVariableName)`; `proto external void SetVariableBool(TAnimGraphVariable varIdx, bool value)` | Root graph API; not an attachment-specific overload. Documentation warns character commands can overwrite manually set variables before animation evaluation. |
| CharacterAnimationComponent | `proto external void SetSharedVariableBool(TAnimGraphVariable varIdx, bool value, bool varHasOtherUsers)` | Still needs a valid handle on this API's graph. Does not solve the already observed root binding failure. |
| EnfusionScriptAPI/html/interfaceCharacterAnimGraphComponent.html | `proto external bool SetAttachment(string bindingName, ResourceName resNameAttachedGraph, ResourceName resNameAttachedInst, int attachedNodeIndex, bool attachAsManaged)` | Documents managed attachment controls, but no established accessor from current ChimeraCharacter to the existing injected controller. Reattaching/replacing the graph is NOT this probe and would disturb engine ownership. |
| EnfusionScriptAPI/html/interfaceIEntity.html and interfaceAnimation.html | `proto external Animation GetAnimation()` | Animation exposes bones/meshes/morphs, not graph attachment variable ownership. Not an alternate graph accessor. |

P-side hypothesis: the existing character Weapon injection is owned by an engine animation controller supporting BindAttachment/BindAttBoolVariable. Missing evidence is a callable way to obtain THAT instance in current Reforger character setup. `FindComponent(CharacterAnimGraphComponent)` is syntactically imaginable but no inspected current prefab/callsite proves that component exists or owns this injection. Casting CharacterAnimationComponent across unrelated API families is not justified. Binding "Weapon" on the W controller would assume the ownership the task expressly requires us to prove.

Search scope: both installed SDK class/member/hierarchy trees; current T4B prefab and scripts; Core scripts/prefabs, Weapons scripts; repository references/tools; public searches for Reforger BindAttBoolVariable, CharacterAnimGraphComponent FindComponent and GetAnimationController. No end-to-end P receiver acquisition found. Negative result is bounded, not a claim that engine support is impossible. No native C++ implementation was available in these inspected sources.

### Handles, lifetime and reset gate

Engine API uses integer IDs; character API uses TAnimGraphVariable. They are not proven interchangeable. Inspected bind documentation does not specify an invalid-ID sentinel or lifetime across detach/re-equip; do not invent those contracts. A future candidate must bind against identified current instances, validate ownership, invalidate sessions on weapon/attachment changes, and not reuse stale IDs.

Intended one-cycle behavior remains Request=true, Repeat=false, Eligible only if required by current graph; no Stop/FireStop overwrite without restoring prior state. Reset must follow attributable end/ReturnReady on both relevant sides, with safe cancellation semantics. Without P addressing, deterministic P reset/readback cannot be implemented. W ReturnReady alone cannot reset or certify P. No guessed reset timer is proposed.

### Acceptance / owner handoff

There is NO runnable candidate; do not install anything or repeat the old root-binding probe. Owner runtime protocol in Phase 1A remains conditional on a future source-qualified candidate and separate review/install approval.

| Later owner observation | Classification |
|---|---|
| Attributable P AND W phases, exactly one request, reset, same Tube3, unchanged tube/donor/chamber, no native reload from probe, controls intact | PASS only after actual owner evidence |
| W-only or P-only, missing reset, unknown receiver/invalid handle | FAIL / ownership unresolved; never PASS |
| Any ammo/chamber/entity mutation or cmd2..6 | Immediate FAIL / stop |
| Compile error | COMPILE_STOP; no runtime |

Next exact evidence needed: source declaration plus existing Reforger callsite/accessor identifying the P-injection controller (including attachment/handle contract), or new explicit authority for read-only runtime component-ownership discovery. This run does not authorize that expanded diagnostic and does not require another speculative setter test.

Static checks rerun: validated Weapons resolver PASS; integrity still 10 pre-existing broken links; 96 Python tests, 2 failures/10 errors (existing baseline). No claim of green suite. Pre/post hash guard identical: V 105 files, labs 58, Core 5521, Weapons 1584, matching preceding preservation table. GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0.

```text
CURRENT_HEAD_BASE = 32f4f72e1a1cbd7eeb77b2d7a3bde1d3ae5eb581
CURRENT_LABS_CHANGED = NO
LIVE_CHANGED = NO
GRAPH_CHANGED = NO
PREFAB_CHANGED = NO
INPUT_CONFIG_CHANGED = NO
META_CHANGED = NO
GUID_CHANGED = NO
G3B2_CHANGED = NO
G3B2_CALLED = NO
AMMO_WRITES_ADDED = NO
CHAMBER_WRITES_ADDED = NO
PROVEN_RACK_BRANCH_CHANGED = NO
CMD2_6_ROUTE_ADDED = NO
WORKBENCH_LAUNCHED = NO
REFORGER_LAUNCHED = NO
GAME_MODE_LAUNCHED = NO
RUNTIME_TEST = NO
COMPILE_TEST = NOT_RUN_BY_AGENT
```

## Phase 1C — W-LOCAL REQUEST PROPAGATION PROBE (O1)

Authority: [6039392248](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6039392248). Starting HEAD `b7312401444501a67a4849d6dd54bbcbf3a02a19`. Status: **T4B_WPROP_PROBE_STAGE_READY_OWNER_REVIEW** (staged scratch only; not committed, not installed).

### Probe question
Can source-proven weapon-local `WeaponAnimationComponent` variable setters drive the CURRENT Astra shell graph so that the existing P injection also executes, without any direct P setter and without native reload?

### W-local API used (source-proven, installed SDK)
`BaseAnimationControllerComponent` (EnfusionScriptAPI), inherited by `WeaponAnimationComponent` via `AnimationControllerComponent` → `BaseItemAnimationComponent` → `WeaponAnimationComponent`:
```
proto external int  BindBoolVariable(string varName)
proto external void SetBoolVariable(int varId, bool value)
proto external bool GetBoolVariable(int varId)
```
Only current graph variables are bound: `ASTRA_ShellRequest`, `ASTRA_ShellEligible`, `ASTRA_ShellRepeat`, `ASTRA_ShellStop`. `ASTRA_FireStop` is NOT bound (relies on its existing default; conditions read `!ASTRA_FireStop`).

### Graph contract (current, read-only)
- AGR declares `ASTRA_ShellRequest` / `ASTRA_ShellRepeat` / `ASTRA_ShellStop` / `ASTRA_ShellEligible`.
- AGF Idle → AstraShell entry (L221): `ASTRA_ShellRequest && ASTRA_ShellEligible && !ASTRA_ShellStop && !ASTRA_FireStop && !Firing && WeaponInspectionState == 0 && Stance == 0 && !IsCommand(CMD_Weapon_Reload)`.
- AGF exit (L237): `!ASTRA_ShellRequest` (AstraShell → Idle).
- ShellReloadSTM transitions read `ASTRA_ShellEligible && !ASTRA_ShellStop && !ASTRA_FireStop && !Firing` and `ASTRA_ShellRepeat`.

### Probe behaviour (animation-only)
Request is one cycle: write `Eligible=true`, `Repeat=false`, `Stop=false`, then `Request=true`; readback logged. Deterministic reset on the existing `ASTRA_Shell_ReturnReady_W` W marker (no timer): write `Request=false`, `Eligible=false`. Diagnostics prefix `[ARMST-T4B-WPROP]` cover bind ids, request/eligible/repeat writes + readback, session id, first P marker, first W marker, return-ready, reset readback. No ammo/mag/chamber writes; no `SetReloadWeapon` in the shell branch; no cmd1..6; no G3B2 call.

### P/W marker classification (static, local labs clips)
`P_Astra_*.txa` contain only `*_P` markers; `W_Astra_*.txa` contain only `*_W` markers. Exact P markers: `ASTRA_Shell_StartReload_P`, `ASTRA_Shell_GrabShell_P`, `ASTRA_Shell_InsertShell_P`, `ASTRA_ShellInsertCommit_P`, `ASTRA_Shell_CheckContinue_P`, `ASTRA_Shell_EndReload_P`, `ASTRA_Shell_ReturnReady_P`, `ASTRA_Shell_Stop_P`; W clips carry the matching `*_W` names. ⇒ `*_P` originate only from P sources and `*_W` only from W sources, so an owner log containing both families proves both source sides executed even when callbacks arrive on the same weapon receiver. Gameplay authority remains W-only (`ASTRA_ShellInsertCommit_W`).

### Frozen rack branch
`T4BRTryRack(...)` body/constant are byte-identical to the installed rack dispatch; the custom-R caller still invokes it first with the same arguments. The shell probe runs only in the complementary non-rack branch `!(magPresent && ammo > 0 && chambered == 0)`.

### Staged scratch (NOT committed; `artifacts/*` is git-ignored, no `git add -f`)
Root: `artifacts/astra-rebuild/stageT4BWPropagationProbe/`.

| Staged file | SOURCE_HEAD | SOURCE_SHA256 | STAGED_SHA256 | diff |
|---|---|---|---|---|
| Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c | b7312401444501a67a4849d6dd54bbcbf3a02a19 | F5D59DB9D00469E4664DE219CF29110A40D6DCE73DE23846ED60C44B6EFA68C1 | 3EF896890ADF29D1FF75E3CB07984BAA2BEBC603D9A524B8A60FCC4B34E82B07 | +65 / -0 |
| Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c | b7312401444501a67a4849d6dd54bbcbf3a02a19 | 7BE1D37513AF31E0C5BC3629BC3301DAFABEC966129AF83D04B688DD4D19BF8A | BC01EEF185AAB8FD9AE608FBDF67760FFC8023AE9CDF8D8280A142CFD7A34CFF | +112 / -0 |

Static checks on staged files: CustomRInputProbe braces 38/38 parens 174/174; AstraV2 braces 32/32 parens 186/186; `SetAmmoCount`/`ClearChamber`/mag detach-attach-spawn/`HandleWeaponReloading`/`CallLater` = 0 in both; `SetReloadWeapon` only in the frozen rack helper; `G3B2` only as a header-comment word. Current labs sources and all graph/prefab/config/meta/GUID are byte-unchanged by O1.

### Owner runtime (NOT authorized; description only)
Non-rack shell-eligible state, physical R once. Expected: RINPUT=YES; WPROP branch exactly once; cmd2..6=0; shell-probe cmd1=0; G3B2=0; ammo/donor/chamber before==after; same Tube3 identity; W phase family executes; P phase family executes; request reset=yes; controls functional. W-only is NOT PASS; P-only is NOT PASS; any gameplay-state mutation is FAIL.

```text
START_HEAD = b7312401444501a67a4849d6dd54bbcbf3a02a19
PLAN_COMMIT = (this O1 plan commit; recorded after push)
STAGED_CUSTOM_R_SOURCE_SHA256 = F5D59DB9D00469E4664DE219CF29110A40D6DCE73DE23846ED60C44B6EFA68C1
STAGED_CUSTOM_R_SHA256 = 3EF896890ADF29D1FF75E3CB07984BAA2BEBC603D9A524B8A60FCC4B34E82B07
STAGED_ASTRA_COMPONENT_SOURCE_SHA256 = 7BE1D37513AF31E0C5BC3629BC3301DAFABEC966129AF83D04B688DD4D19BF8A
STAGED_ASTRA_COMPONENT_SHA256 = BC01EEF185AAB8FD9AE608FBDF67760FFC8023AE9CDF8D8280A142CFD7A34CFF
CURRENT_LABS_CHANGED = NO
LIVE_CHANGED = NO
GRAPH_CHANGED = NO
PREFAB_CHANGED = NO
INPUT_CONFIG_CHANGED = NO
META_CHANGED = NO
GUID_CHANGED = NO
WORKBENCH_LAUNCHED = NO
REFORGER_LAUNCHED = NO
GAME_MODE_LAUNCHED = NO
RUNTIME_TEST = NO
COMPILE_TEST = NOT_RUN_BY_AGENT
```

## Phase 1C-R — WPROP SAFETY + REVIEW-EVIDENCE CORRECTION (O1R)

Authority: [6041185715](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6041185715). Base HEAD `524f43f4358e52114d9cf2fea8878ad047598ef2`. O1 architecture `ACCEPTED`; O1 runtime GO `WITHHELD`; O1R `AUTHORIZED`. Status: **T4B_WPROP_PROBE_REVIEW_READY_OWNER_GO**.

Corrections applied to the same ignored staging root `artifacts/astra-rebuild/stageT4BWPropagationProbe/`:

- **R1 fail-closed shell gate.** Before any W request the helper requires `magPresent==true && maxAmmo>0 && ammo>=0 && ammo<maxAmmo && (chambered==0 || chambered==1)`; unresolved telemetry now rejects with `reason=unresolved-ammo` / `reason=unresolved-chamber`. The frozen rack predicate/call is untouched.
- **R2 deterministic manual abort (no timer).** Explicit `m_bWPropActive`; a second qualified R while active resets WPROP variables to safe defaults and logs `phase=manual-abort` instead of opening a second session; normal `ASTRA_Shell_ReturnReady_W` reset clears active; a failed/non-observable bind/write/readback never leaves the session marked active; per-session P/W observation flags reset on a new session.

Durable review evidence: `reports/MP133_TASK1_WPROP_PROBE_REVIEW_EVIDENCE.md` — source HEAD/blob + SHA-256, COMPLETE unified diffs of both staged scripts (no omissions), static writer/call-site scan, exact fail-closed gate, exact abort/reset path, exact P/W marker classification, owner runtime protocol, unchanged-boundary statement.

Updated staged identities (O1R supersedes the O1 staged SHAs in the Phase 1C block above):

```text
STAGED_CUSTOM_R_SOURCE_SHA256 = F5D59DB9D00469E4664DE219CF29110A40D6DCE73DE23846ED60C44B6EFA68C1
STAGED_CUSTOM_R_SHA256 = ECD8DF6F8A96292E4646EBD9F2DF17C1E4153E19361C6D1B08131E8F3E2FC95A
STAGED_ASTRA_COMPONENT_SOURCE_SHA256 = 7BE1D37513AF31E0C5BC3629BC3301DAFABEC966129AF83D04B688DD4D19BF8A
STAGED_ASTRA_COMPONENT_SHA256 = 8176B363B876AD105110303C49321266B133C892CF985DFAB9453DABF90B215D
CURRENT_LABS_CHANGED = NO
LIVE_CHANGED = NO
GRAPH_CHANGED = NO
PREFAB_CHANGED = NO
INPUT_CONFIG_CHANGED = NO
META_CHANGED = NO
GUID_CHANGED = NO
WORKBENCH_LAUNCHED = NO
REFORGER_LAUNCHED = NO
RUNTIME_TEST = NO
COMPILE_TEST = NOT_RUN_BY_AGENT
```

NEXT: owner reviews the report and decides whether to authorize install + one owner R (non-rack shell-eligible state). GPT Astra HOLD. No install/runtime by agent.

## Phase 1D — P-SIDE ACTIVATION PATH DISCOVERY

Authority: [6042238284](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6042238284). READ-ONLY source/static (no graph edit, no install, no runtime). Status: **P_TRIGGER_PATH_MULTIPLE_CANDIDATES**. Report: `reports/MP133_TASK1_P_SIDE_ACTIVATION_PATH_DISCOVERY.md`.

Runtime context (owner `6042146419`): WPROP = **W_ONLY** (`sawP=false sawW=true`); the W-local `ASTRA_ShellRequest` started the W graph only. ⇒ W and P are **separate graph instances** (`MP133_Astra2_weapon.asi` = W; `MP133_Astra2_player.asi` = P via `AnimInjection BindingName "Weapon"`), each with independent per-instance variables; there is no automatic W→P propagation.

Findings:
- **P owner (UNRESOLVED):** strongest candidate = engine `CharacterAnimGraphComponent` (a `BaseAnimationControllerComponent`) hosting attachment `"Weapon"`; the game-side accessor (`CharacterEntity.GetAnimGraphComponent()` / `FindComponent(CharacterAnimGraphComponent)`) is not proven from installed game sources.
- **Injection-aware API (source-proven signatures):** `BindAttachment`, `BindAttBoolVariable`, `SetAttBoolVariable` (float value), `GetAttBoolVariable`, `BindAttCommand`, `CallAttCommand`, `SetAttachment`/`RemoveAttachment` (engine `BaseAnimationControllerComponent`).
- **Character-root setter route REJECTED:** the character root graph (`player_main.agr`) does not declare `ASTRA_ShellRequest` (owner evidence 5983965875).
- **Dual custom command/event:** `BindCommand`/`CallCommand` exist on both controller families and `BindAttCommand`/`CallAttCommand` on the attachment; a single emission reaching both P and W is **not proven**; BC/Chungus calls both sinks explicitly.
- **Chungus distinction:** ACTIVATION = vanilla reload context; SYNC = `InitPlayerAnimVariables()` after `StartReloadTimer`. No custom pre-reload P starter.

Ranked candidates: (1) injection-aware attachment variable/command write (best; no graph change if it works); (2) custom command/event to both; (3) minimal P follower/sync graph (requires graph edit). Next minimal probe = bounded animation-only PACT probe (obtain CharacterAnimGraphComponent → `BindAttachment("Weapon")` + `BindAttBoolVariable("ASTRA_ShellRequest")` → write/readback → observe P markers → deterministic reset), no gameplay writes.

No functional file changed (GRAPH/PREFAB/CONFIG/META/GUID/G3B2/LIVE unchanged).

## Phase 1E — PACT ATTACHMENT ACCESS PROBE (STAGE ONLY)

Authority: [6042531682](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6042531682) + R1 correction [6042807676](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6042807676). Stage-only; no install/compile/runtime. Status: **PACT_PROBE_STAGE_READY_OWNER_REVIEW_R1**. Report: `reports/MP133_TASK1_PACT_PROBE_REVIEW_EVIDENCE.md`.

Source baseline = owner's local lab (verified): CustomR `ECD8DF6F…`, AstraV2 `8176B363…`; no drift.

Staged R1 (git-ignored, not committed): `artifacts/astra-rebuild/stageT4BPACTProbe/Scripts/Game/ARMST_T4B/`
- `ARMST_T4B_CustomRInputProbe.c` → `2568DA60441BE34D6E0E96613393B4099A07B70875EC5AAB2CE10E8C8289D3E6` (all-4 readback, mismatch safe-reset, active-from-readback);
- `ARMST_T4B_AstraV2_WeaponAnimationComponent.c` → `411D5E127C5E97D6A3BAAA91D7B79C0CE662F06600D03EC31080A2C878C72640` (P-primary reset; W only no-P fallback).

R1 corrections (supersede the earlier `68AE302E…`/`8F84BFE4…` staging): (1) request readback now verifies `req&&elig&&!rep&&!stop`, else safe-reset all four and log `phase=reject reason=request-state-mismatch`; (2) reset/manual-abort keeps `m_bPactActive=(rbReq||rbElig)` and logs `resetClean`; (3) reset source is `p-return-ready` (primary) / `w-return-ready-no-p` (fallback) / `manual-abort`.

Accessor (compile-visible evidence): `CharacterAnimGraphComponent.Cast(controlled.FindComponent(CharacterAnimGraphComponent))`, fallback `CharacterEntity.Cast(controlled).GetAnimGraphComponent()`. Engine API `EnfusionScriptAPI` (`interfaceCharacterEntity`, `interfaceCharacterAnimGraphComponent`, `interfaceBaseAnimationControllerComponent`, `interfaceIEntity.FindComponent`); same `Cast(FindComponent(...))` pattern already used in Core (`ARMST_MUTANTS_ANIM_COMPONENT.c:31`, `ARMST_MUTANT_MOVEMENT_COMPONENT.c:143`) for a sibling engine animation-controller class.

PACT on the non-rack shell branch: `BindAttachment("Weapon")` → `BindAttBoolVariable("ASTRA_Shell*")` → `SetAttBoolVariable` (Request=true, Eligible=true, Repeat=false, Stop=false) → readback. Cleanup deterministic (no timer): preferred W `ASTRA_Shell_ReturnReady_W` → `SCR_PlayerController.T4BPactResetFromEvent()` (write Request/Eligible=false + readback); fallback second qualified R `phase=manual-abort`. Frozen rack branch byte-identical; no gameplay writes; no native reload; no cmd1..6; no G3B2.

Owner runtime (deferred, not authorized): Tube3<3, chambered=1, one R; PASS = P+W families + clean reset + no mutation (`PACT_PW_PASS`); fail classes `PACT_P_ONLY_FAIL` / `PACT_W_ONLY_FAIL` / `PACT_BIND_FAIL` / `PACT_COMPILE_BLOCKED` / `PACT_GAMEPLAY_MUTATION_FAIL`.

No functional file changed (GRAPH/PREFAB/CONFIG/META/GUID/G3B2/LIVE unchanged).

## Phase 1F — P-OWNER + INSPECTION ROUTE DISCOVERY

Authority: [6043917747](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6043917747). SOURCE/STATIC only. Status: **T4B_P_OWNER_INSPECTION_ROUTE_DISCOVERY_COMPLETE**. Report: `reports/MP133_TASK1_P_OWNER_AND_INSPECTION_ROUTE_DISCOVERY.md`.

Runtime context: PACT installed/compiled/PASS; `PACT_BIND_FAIL = YES`, subreason `CHARACTER_ANIM_GRAPH_OWNER_UNAVAILABLE`; `W_LOCAL_REQUEST = WORKS`, `P_FAMILY = NO`.

Findings:
- Inspection receiver = `CharacterControllerComponent.SetInspect`/`SetInspectState`/`GetInspectState`/`OnInspectionModeChanged`; vanilla action `CharacterInspect` (referenced in Core conf L265). Its binding/context is in the packed vanilla conf → **UNRESOLVED locally**. Graph inspection path (`WeaponInspectionState`, `CMD_Weapon_Inspection`, `WeaponInspectionSTM`, AST `Inspection`) is **source-intact**.
- Live T4B overlay = `Priority 20000 / Flags 0xa / ActionRefs { ARMST_MP133_Reload } / keyboard:KC_R`. It can only affect KC_R-bound actions; if `CharacterInspect` is R-bound, the active Exclusive context suppresses inspection (leading candidate for the regression).
- P-owner candidates: `CharacterAnimGraphComponent` (runtime FAIL), `AnimationControllerComponent` via `FindComponent` (Core precedent; UNTESTED), `CharacterAnimationComponent` (no attachment API → NO), weapon W component (W-only proven), native engine injection (no script accessor).

Classifications:
```
INSPECTION_REGRESSION_CLASSIFICATION = INSPECTION_REGRESSION_MULTIPLE_CANDIDATES   (leading: INPUT_CONTEXT; graph PROVEN intact)
P_OWNER_CLASSIFICATION              = P_OWNER_DISCOVERY_NEEDS_RUNTIME_DIAG
```

Next: owner-only input A/B (Overlay-only / context-off inspection test) + bounded read-only animation/controller enumeration diagnostic for the P owner. No input/graph change by agent.

No functional file changed (GRAPH/PREFAB/CONFIG/META/GUID/G3B2/LIVE unchanged).

## Phase 1G — P-OWNER RUNTIME DIAGNOSTIC (STAGE ONLY)

Authority: [6044071573](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6044071573). Stage-only; read-only diagnostic. Status: **P_OWNER_DIAG_STAGE_READY_OWNER_REVIEW**. Report: `reports/MP133_TASK1_P_OWNER_RUNTIME_DIAG_STAGE.md`.

Base = installed PACT probe (`ARMST_T4B_CustomRInputProbe.c` `2568DA60…`, blob `f661cd9`). Staged read-only delta: `artifacts/astra-rebuild/stageT4BPOwnerDiag/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` → `54404F6B32D9599E4A4F34D3A3519FC5FC2596FDC476AD7FFA94A0F4BD960202` (blob `dfbadb3`, +41/-0).

Diagnostic (`T4BRTryPOwner`, called once per qualified shell R): logs `[ARMST-T4B-POWNER] phase=owner`; `phase=find animController=.. charAnimGraph=.. charAnim=..` (via `FindComponent` for `AnimationControllerComponent`, `CharacterAnimGraphComponent`, `CharacterAnimationComponent`); `phase=bindAtt owner=animationController binding=Weapon id=.. valid=..` and (if found) the same for `characterAnimGraph`. `BindAttachment("Weapon")` is the only API call — **no** attachment-variable writes, **no** commands, **no** graph mutation, **no** gameplay writes; WPROP/PACT/rack paths unchanged.

Also included: owner-only inspection A/B plan (A = custom context active; B = context disabled / Overlay-only; same T4B, inspect only). No input variant installed.

No functional file changed (GRAPH/PREFAB/CONFIG/META/GUID/G3B2/LIVE unchanged).
