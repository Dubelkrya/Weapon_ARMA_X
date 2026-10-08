# MP133 — W synchronized command delivery: design-only

Date: 2026-10-08. Result: **SOURCE_BLOCKED**. This is a bounded design, not a functional candidate or permission to emit a command.

## 1. Authority and current evidence

Direct owner attachment `687d61a7-f192-4da2-82db-60e53abd2289` grants DESIGN_ONLY, experiment A only, two documentation paths only, commit/push to `t4b/installed-mag-probe`. It was not posted to GitHub. Starting HEAD and ancestry verified: `6186aaa433369f4130f1b404d4307632d40923ce`. Owner untracked `reports/CORE_ARMST_READONLY_AUDIT.md` is excluded. AGENTS, sync, continuation plan, previous transport discovery and current sources were inspected; newer plan/owner evidence wins over historical sync.

Owner evidence [6062981503](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6062981503): W named binding returned 3; character binding failed against player_main.agr. This does not prove W-to-P fan-out. Prior owner Live Debug identified an evaluated P MasterControl with MP133_Astra2_player.asi. That historical screenshot is not an observer-health control for a future emission frame. W attachment lookup failed; do not reopen that route.

Current MP133_Astra2.agr declares CMD_ASTRA_TransportProbe, but current MP133_Astra2.agf has no consumer for it. Existing IsCommand/GetCommandI/GetCommandF uses are native rack conditions, not safe diagnostic consumers. Shell-entry booleans and WPROP markers are not command receipts. Synchronized native implementation/mapping remains unknown. B/C and ItemUse are not re-audited here.

## 2. Instance ownership and attribution

Live source root: `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMSTMP133T4B_InstalledMagProbe`.

Prefab `Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et` associates W with nested WeaponComponent `{CFBAA4B706BA66E8}` / AstraV2 animation component `{60B4EA76EB15F6E0}`, AGR `{AF2491EDB3449EED}`, weapon ASI `{5F61684997C53048}`. AnimInjection uses the same AGR, player ASI `{A43FF9780FC454A4}`, BindingName Weapon and BindWithInjection 1. These are resource/component identities, NOT runtime graph-instance handles.

W is the current equipped weapon's item controller. P is the Weapon injection evaluated in that weapon's current owning character animation domain, not the character root controller itself. The same AGR does not identify which instance produced a record. Acceptance needs owner-visible runtime descriptor association to current character, current weapon and respective ASI, plus an unbroken recording across the pulse; equip/respawn/injection replacement invalidates association. No undocumented network-ID or debugger-descriptor API is assumed.

## 3. Preferred passive observer and limitation

Prefer built-in per-instance Live Debug recording, not a generic callback. Official [Live Debug tutorial](https://community.bistudio.com/wiki/Arma_Reforger:Animation_Editor:_Live_Debug_Tutorial) describes Fetch/Attach, recording, rewind and inspection of commands and returned events/tags. This supports a real observation tool for P and W independently selected instances. It does not document simultaneous recording of both for one pulse, complete one-frame capture, integer argument visibility, or predicate/node execution evidence.

[File Types](https://community.bistudio.com/wiki/Arma_Reforger:File_Types) describes .adeb descriptors and per-frame debug instances. This is potential multi-instance evidence, not proof that this installed debugger collects both instances concurrently. No parser, format fields, export command or common timestamp API is invented.

A recorded input command is stronger than a sender log, but it is not automatically proof that a diagnostic graph predicate evaluated and consumed it. Therefore built-in command recording alone does not satisfy all acceptance conditions. There is presently no established source-supported complete observer; stage remains blocked.

## 4. Capability ledger and passive instrumentation fallback

Installed SDK roots: `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs\EnfusionScriptAPI\html` and `ArmaReforgerScriptAPIPublic\html`.

| Capability | Evidence | Boundary |
|---|---|---|
| W named bind and integer/float emission | BaseAnimationController BindCommand(string), CallCommand(int,int,float) declarations; owner W binding | A bound ID is controller-local; sending is not consumption; no call this phase |
| Graph command predicate/arguments | Live MP133_Astra2.agf lines 259/301 uses IsCommand, GetCommandI and GetCommandF | Do not reuse native rack branches; diagnostic predicate not currently present |
| Script command-read observer | Inspected BaseAnimationController declarations expose binding/calling, variables/events/tags | No equivalent per-instance command-read/consumer-trace accessor established |
| Character-to-item hook | BaseItemAnimationComponent OnCharacterCommand / SyncWithCharacter | Wrong direction and not independent P receipt |
| Per-instance debug recording | Official Live Debug tutorial above | Dual capture/coverage/argument display and consumption trace are gaps |
| Passive variable wrapper | Official [Nodes](https://community.bistudio.com/wiki/Arma_Reforger:Animation_Editor:_Nodes); Core Anims/Player/Facials.agf lines 103–114, 257–269 | VarSet is subtree-scoped; values restore at parent return. PostEval applies stored values to subtree next frame. Not a proven persistent externally readable latch |

Smallest fallback to investigate: diagnostic wrapper on each actual active evaluation path, preserve the existing child, evaluate only the custom command predicate, expose a diagnostic evaluation indication and receipt indication in that same instance's trace. This is a proposed topology, NOT an exact runnable node schema. Current MasterControl is AnimSrcNodeBlend, Child0 IdleReloadSTM, Child1 SightPose, Optimization Always eval both (AGF 412 onwards). Wrapping or changing roots can alter initialization/caching even when retaining children.

Do not claim `VarSet(LastValue+1)` is a globally readable heartbeat: subtree restoration and debugger sampling location are unresolved. Core float-expression examples demonstrate local variable operations, not P/W-safe externally persistent receipts. Do not substitute Sound/inspection events or tags returned via a W callback; tags can be game-consumed. Before a candidate, establish exact serialization, visibility at the diagnostic node, lifetime, independent unsynchronized storage, and pose/transition preservation. No such fallback is implementation-ready today.

## 5. Observation controls

Negative baseline: both independently identified instances recorded while stable/equipped, no diagnostic command in the observation window, no receipt indications. No buttons, R, native commands or ShellRequest writes.

Positive observer control: documented debugger recording and advancing P evaluations establish that capture is alive, but do NOT establish that the diagnostic predicate works. Its validity additionally needs source-supported evaluated-node/predicate evidence at the command frame, or a separately authorized safe observer-calibration experiment. Do not send a second command silently to manufacture calibration; this proposed delivery test allows exactly one pulse.

If the only health evidence is a graph name, moving character, shared marker, W callback, or an earlier screenshot, P observer validity is NO. If diagnostics could be synchronized/copied from W, receipt attribution is ambiguous. No PASS based on W-only evidence.

## 6. Independent P evaluation control

Future owner must identify character -> injected MP133_Astra2.agr -> player ASI -> MasterControl in the recorded data; show advancing evaluations before, during and after the pulse and actual observer-path evaluation in the relevant P frame. W must be a separate weapon-ASI descriptor. Resource identity alone is insufficient. Debugger paused, missing updates while alt-tabbed, missing frames or instance replacement invalidate a negative conclusion. Source currently supports recording evaluation, but not the entire diagnostic-path health/coverage proof. This requirement is unresolved, not waived.

## 7. Future candidate paths and proposed delta

No candidate exists. Provisional smallest laboratory set, only after exact observer-source gap closure and a separate GO:

- `Assets/MP133_AstraShellGraph_test/MP133_Astra2.agf`: if required, diagnostic-only wrapper preserving original child/pose route. Exact node/condition diff is BLOCKED pending proven lifetime and readout; no guessed patch included.
- `Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr`: only if a proven diagnostic variable declaration is needed; retain commands, GUID, roots and current flags. Do not toggle Synchronized as part of this single test.
- Current laboratory `ARMST_T4B_AstraV2_WeaponAnimationComponent.c`: future named bind, one explicit diagnostic emission at a reviewed evaluation boundary and producer-only log, without touching CustomR/rack or gameplay. Not a new input button or polling/retry service. Exact entry point needs separate review.

Read-only debugger-only route would omit graph changes, but cannot currently meet consumption/observer-health acceptance. No player_main.agr, prefab, ASI, input, Core, production Weapons or old_pa changes. No copies of historical resources.

## 8. Graph and gameplay risks

Wrapper evaluation/initialization, state-machine restarts, blend paths, caching, variable scope, propagated tags/events, accidental native-command subscriptions and diagnostic-variable synchronization can all invalidate passivity or attribution. Diagnostic nodes must not start shell phases or change Firing/inspection/stance conditions. Preserve existing rack conditions and dispatcher. Never test CMD2–6 replacement behavior. Tube3 identity/ammo and chamber must be unchanged. Source plausibility is not a runtime guarantee.

## 9. One-pulse protocol and expected evidence

Conditional future protocol (NOT executable until gaps close): collect baseline and observer health for both stable instances; bind CMD_ASTRA_TransportProbe by name on current W; emit once at a source-verified controller/evaluation boundary; record from the last complete P/W evaluations before emission through the first complete evaluations processing it and subsequent return to baseline. No fixed wall-clock timeout can replace complete frame coverage. Abort before sending if dual recording/observer readiness is absent. After sending, never retry; incomplete capture is INCONCLUSIVE.

Integer payload is supported by the W call signature and current graph GetCommandI syntax, but end-to-end P payload transport and debugger visibility are UNPROVEN. A nonce may be proposed only after both observers can expose its value. Alternative: isolated single producer/single pulse/no other command-name writer in one continuously attributed shared capture; no nonce proof is claimed. If that common capture cannot be established, the alternative is also blocked.

Expected evidence labels below are report transcription labels, NOT implemented engine log APIs:

```text
PRODUCER: command=CMD_ASTRA_TransportProbe binding=<current W-local ID> count=1
W_TRACE: descriptor=<owner-verified W> asi=MP133_Astra2_weapon.asi command-input=<observed> consumer-evaluation=<observed or UNKNOWN>
P_TRACE: descriptor=<owner-verified injection P> asi=MP133_Astra2_player.asi evaluation=<observed> observer-health=<observed or UNKNOWN> command-input=<observed> consumer-evaluation=<observed or UNKNOWN>
```

Separate input receipt from actual consumer receipt. Never translate UNKNOWN into NO; never label a forwarded W event P_TRACE. Each positive receipt requires an independently attributed evaluated diagnostic predicate, or equivalent source-proven per-instance consumption trace. That last capability is the blocker.

## 10. Interpretation

| W receipt | P receipt | P observer/evaluation valid | Result |
|---|---|---|---|
| YES | YES | YES | Delivery observed in tested configuration |
| YES | NO | YES | Delivery not observed in tested configuration |
| NO | Any | Any | Invalid emission/receipt test |
| YES | NO | NO | INCONCLUSIVE |
| YES | Ambiguous | Any | INCONCLUSIVE |

YES here means qualified consumer evidence, not producer success. A positive result does not establish Synchronized causality or multiplayer replication. A negative result does not reject every Enfusion transport architecture.

## 11. Future owner gates

1. Owner reviews this blocked design; obtain source/debugger evidence for the gaps without assuming authority to run anything now.
2. Separate explicit CANDIDATE-STAGING GO only after observer design is established. Present exact minimal diff and static scope/hash checks; stop before installation.
3. Separate exact-file installation authorization with current owner PRE and reviewed SOURCE/POST hashes. Never install stale laboratory bytes over newer live bytes.
4. Separate compile authorization; clean Game scripts/editor graph diagnostics required. Compile is not receipt PASS.
5. Separate runtime authorization; observer-only readiness first. No pulse until simultaneous capture and attribution/health gates PASS; one pulse only. Collect qualified P/W receipts and nonmutation evidence. No G3B2, reload/rack commands, retries or multiplayer claim.

## 12. Guards and static checks

Fresh PRE and POST protected inventories match. Method: recursively enumerate `.et,.conf,.meta,.c,.layer,.agr,.agf,.asi,.ast,.gproj,.anm,.txa`, sort FullName, SHA-256 each file; aggregate SHA-256 of UTF-8 `absolutePath|SHA256` rows joined by LF (no terminal LF). Includes names/counts, not only contents.

| Root | Files | PRE = POST aggregate SHA-256 |
|---|---:|---|
| ARMSTMP133T4B_InstalledMagProbe | 105 | D540BE18C0EA0A4754F34D27C260F1BAF9971DC9C1B76674D095C26BC3B48B76 |
| ARMST-PLATFORM---Core | 5521 | 2EDF4D1DCA02F0C662AE1CA567D8B9655C374BC817883B7625A7AF02D8860B4B |
| ARMST-PLATFORM---Weapons | 1584 | A7C611FE0417F5A5E1DA6E4209F01E3CF846295E9ADA57999713FF1B4CC2AECF |
| Armst_Work | 163 | 62AD288141B18B222E058011B29672E23996D7B651C8C4C79E7535BD24123E29 |

Owner current AGR C55D757EB85A7454DCAE27567CA96980441560805DC0B268B15DBC64ECAF97FF; CustomR 9ADD4AD9979382AC6B42F88209A47A11A29EB6038BE832F13D3B3EF4AA628249; AstraV2 component 241E6EC19633812740BBD25DB960E21F77A928AC2FD273C81D74B75E86BAA7BC; prefab 9960A92E9A31C9F2DDC69164F8D68ED673FE5481792E30E365DFE44DFE531AF1.

Static Python resolver PASS. Integrity --check fails on missing jsonschema and 10 existing broken links. Sandbox unittest run: 96 tests, 2 failures/52 errors, including temporary-directory permission errors. One authorized escalated run returned nonzero; retained tail contains fixture-write messages, not a complete test summary. Existing connector tests use TemporaryDirectory; protected inventories remained identical. Further full-suite retry was rejected by safety review due to fixture-write messages and was not bypassed. Do not report an independently verified fresh 2-failure/10-error summary or repository-green validation. No dependency/test repair.

Commit gate: only new report and continuation diff; git diff --check; exclude owner untracked audit; verify no plan-body edit. Tests here are Python static tooling tests, not Enfusion compile or gameplay runtime.

## 13. Rollback

This phase has no functional installation to roll back. Documentation corrections are forward commits. For a future candidate, save and hash the exact current owner bytes before installation, only for its individually authorized paths; rollback requires owner authorization and hash verification against that capture, not old_pa, historical Git resources or the older labs snapshot. Never reset owner work or undo proven rack.

## 14. Blockers and result ledger

Source gaps: (1) complete dual P/W capture, current runtime identity association and frame coverage; (2) per-instance actual diagnostic consumer evaluation and independently valid P observer; (3) safe diagnostic wrapper serialization/lifetime/readout, or equivalent native consumer trace; (4) independently observable payload or adequate single-pulse shared-capture correlation. Synchronized semantics remain unspecified. Resolving one gap does not waive the others.

```text
MP133_W_SYNCHRONIZED_COMMAND_DELIVERY_DESIGN_RESULT
STATUS: SOURCE_BLOCKED
REPOSITORY: Dubelkrya/Weapon_ARMA_X
BRANCH: t4b/installed-mag-probe
STARTING_HEAD: 6186aaa433369f4130f1b404d4307632d40923ce
FINAL_HEAD: containing documentation commit; resolve with git rev-parse HEAD (no self-referential hash)
AUTHORIZATION: DESIGN_ONLY
W_OBSERVER_DESIGN: prefer per-instance Live Debug + proven consumer trace; incomplete
W_OBSERVER_SOURCE_SUPPORT: command recording YES; actual consumption/coverage incomplete
P_OBSERVER_DESIGN: independently identified injection trace + observer-path health; incomplete
P_OBSERVER_SOURCE_SUPPORT: Live Debug evaluation/command inspection YES; complete receipt observer NO
P_EVALUATION_CONTROL: independent recorded evaluations required; historical screenshot insufficient
INSTANCE_ATTRIBUTION: resource/ASI ownership known; concurrent runtime association unproven
NONCE_OR_PAYLOAD_DESIGN: int signature/graph accessor supported; end-to-end observability unproven
COMMAND_CONSUMER_DESIGN: diagnostic-only wrapper proposal; exact safe diff SOURCE_BLOCKED
SYNCHRONIZED_SEMANTICS: SOURCE GAP
W_TO_P_TRANSPORT_STATUS: UNTESTED
MULTIPLAYER_STATUS: UNTESTED
CANDIDATE_STAGED: NO
GRAPH_FILES_CHANGED: NO
GAMEPLAY_FILES_CHANGED: NO
RACK_CHANGED: NO
G3B2_CHANGED: NO
WORKBENCH_RUN: NO
RUNTIME_RUN: NO
CALLCOMMAND_EXECUTED: NO
PROTECTED_HASH_GUARDS: PASS, four roots unchanged
STATIC_CHECKS: resolver PASS; repository checks NOT GREEN; doc scope checked before commit
DOCUMENTS_CHANGED: this report; continuation only in Astra plan
COMMIT: containing documentation commit; exact SHA in handoff
PUSH: verified separately after commit; no claim from this pre-commit text
SOURCE_GAPS: listed above
NEXT_REQUIRED_AUTHORIZATION: OWNER_REVIEW_THEN_SEPARATE_CANDIDATE_GO
```

HARD STOP after documentation-only commit/push. No candidate GO inferred from this report.
