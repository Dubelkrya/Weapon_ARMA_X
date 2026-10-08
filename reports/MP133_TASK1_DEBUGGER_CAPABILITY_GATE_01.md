# MP133 — DEBUGGER_CAPABILITY_GATE_01

2026-10-08. **Classification: OWNER_UI_INSPECTION_REQUIRED**.

Authorization: direct owner GO, SOURCE-ONLY. Branch `t4b/installed-mag-probe`; starting HEAD `7d08fd3723a85735a64b14b1ef189ce7ffa9268f`, branch/origin/ancestry verified. This report is the ONLY authorized change. No plan/sync update, candidate, graph, prefab, script, input or gameplay change. No launch, compile, runtime, UI interaction or command emission by agent. Rack FROZEN; G3B2 HOLD. Tests/dependencies not rerun or repaired.

## 1. Startup and scope

Read AGENTS.md, CURRENT_AI_SYNC.md, current Astra continuation and previous design report. Newer owner GO and continuation supersede historical sync, including its obsolete Phase 0 instruction. Latest accessible Issue #34 owner evidence remains [6062981503](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6062981503): custom W binding exists, character bind looks up player_main.agr and fails for the injection-only name. That is registration evidence, not debugger capability or delivery evidence.

Preserved owner-untracked `reports/CORE_ARMST_READONLY_AUDIT.md`; excluded from commit. No re-investigation of transport alternatives B/C, ItemUse, rack or gameplay architecture.

## 2. Source ledger

### Official documentation, retrieved this phase

| Source | Supported capability | Not established |
|---|---|---|
| [Live Debug Tutorial, oldid 371017](https://community.bistudio.com/wiki?title=Arma_Reforger:Animation_Editor:_Live_Debug_Tutorial&oldid=371017) | Fetch available instances; attach to a selected one; record evaluation; pause/rewind and inspect commands, variables, returned events/tags | Concurrent P/W recording, complete frame coverage, command parameter display, per-predicate execution trace |
| [Animation Editor](https://community.bistudio.com/wiki/Arma_Reforger:Animation_Editor?useskin=darkvector), indexed official content | Live Debug entity attachment; one-frame commands; Evaluation Information with clip/time/events/tags/bones; timeline inspection | Those displays are not documented as evaluated command-consumer proofs. Preview timeline is not necessarily live simulation frame numbering |
| [File Types](https://community.bistudio.com/wiki/Arma_Reforger:File_Types), indexed official content | .adeb binary recording includes descriptors and per-frame debug instances; load through Live Debug | Full field layout, descriptor ownership schema, common simulation clock, capture loss policy, command records/payload encoding |
| [Weapon Animation Setup](https://community.bistudio.com/wiki/Arma_Reforger:Weapon_Animation_Setup), indexed official content | A second Animation Editor instance is supported for workspace work | This is a justified way to inspect whether two live attachments can coexist, NOT proof of two live recording subscriptions |

Direct fetch of main editor/file-types pages returned 403 in this phase; official search-index excerpts were available. Live Debug tutorial fetched directly. No third-party assertion used as engine proof.

### Installed SDK, checked directly

Root: `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs\EnfusionScriptAPI\html`.

| File | Specific finding | SHA-256 |
|---|---|---|
| Page_FileTypes.html, line 116 | Local extension is **.adbg**, not online .adeb. Same high-level descriptor/frame description; explicitly no backward version compatibility | 8334B7EA7F4C69CAA31E7F45646BD4280E1EA5DA73DBEF5B56D4946BA95D48D5 |
| interfaceAnimEditor.html, lines 122 onwards | No AnimEditor-specific debug recording/instance/frame APIs listed; inherited WBModuleDef resource/container/save/close/plugin methods are not debugger-read APIs | CBBA51493585EC2491218EDBCFE0593DD234E6B8BC804071FDE64381D371F8C5 |
| interfaceBaseAnimationControllerComponent-members.html, lines 140/147/148 | BindCommand, CallCommand and CallCommand4I exist; no command receipt/predicate execution reader found in inspected member list | 2DB116491EE9C0269F1F44BFA71C6DFB083F3603CE8F98BE4BAB26F718A4E1D3 |

Targeted searches across both installed SDK HTML/JS/source documentation trees for `.adeb`, AnimDebuggerSerializationVersion, animation debugger and Live Debug produced the file-types description, not a full recording schema. An initial unbounded substring `adeb` also matched generated hexadecimal link identifiers; those are false positives, excluded. No binary parser or recording automation API was invented. An absence in this search scope does not establish absence in native engine implementation.

Important compatibility gate: inspect the installed Open dialog's actual file filters and any existing recording's version/load result. Do not rename .adbg to .adeb, assume compatibility, or convert unknown binary fields. Prefer the same tool build that created a recording.

## 3. Answers to the required capability questions

| Question | Source-only finding | Evidence owner inspection must supply |
|---|---|---|
| Can W and injection-P share one captured interval? | NOT PROVEN. Multi-instance file structure permits the idea but does not establish collection/subscription behavior | Both current runtime descriptors in one recording/frame context, or two recordings with a displayed common simulation-frame identifier. Separate wall clocks/screenshots are insufficient |
| Can identity be attributed independently? | P/W AGR is shared; ASIs differ. Owner previously identified P, but identity must be reacquired in the same inspected record | Character -> Weapon injection -> MP133_Astra2_player.asi and equipped weapon -> MP133_Astra2_weapon.asi, distinct stable descriptors |
| Are command inputs visible? | YES, general command inspection is documented. Exact P-injection command-view placement and argument visibility remain unknown | Read-only command record view scoped to the selected P descriptor, and equivalent W view; show actual fields, not editable declarations |
| Can debugger distinguish input from consumer evaluation? | NOT PROVEN. Evaluation Information is not documented as condition-result tracing | A recorded evaluated-node/condition-result view, its selected instance/frame and documented/visible read-only meaning; mere highlighting or pose output is insufficient |
| Can P observer health be checked at a relevant frame? | Evaluation recording/rewind is supported. Exact frame coverage/observer-path health is not established | Advancing recorded P evaluation, correct instance, and per-frame consumer-path evidence if such a facility exists. Historical screenshot or generic callback does not suffice |

Current live `Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr` declares CMD_ASTRA_TransportProbe at line 80 and MasterControl default root at 127. Current AGF has MasterControl at 412 but **no CMD_ASTRA_TransportProbe consumer**. Existing command predicates are native reload/rack conditions. Therefore no read-only UI inspection can demonstrate execution of this absent diagnostic consumer. It may discover a native input-receipt trace and generic evaluation trace; these are distinct evidence classes, not permission to redefine the previous acceptance criteria.

## 4. Exact owner-only read-only UI inspection procedure

**Prepared only; not executed. Requires separate owner approval to inspect UI/use a recording or run a no-input observation session. This source-only GO is not runtime permission. No diagnostic pulse at any step.**

Preferred input: an already existing owner recording from the current tool build/session, opened read-only. If none exists, owner separately authorizes a no-input session; the agent does not launch anything. No fixture spawn/re-equip/reset to create a baseline. Existing test setup may have initialization effects: do not claim its startup is mutation-free merely because debugger actions are observational.

1. Record tool build/version, recording provenance if present, current character/weapon context and screenshot of Live Debug UI. Open the existing workspace only; do not save, change Attachments Debug, drag nodes, change properties, run preview Play/default-node or double-click nodes. No R/fire/inspection/actions, command buttons, variable sliders or setters.
2. For an existing recording: use its actual visible load/open control in Live Debug, if offered. Capture its dialog filters and exact file extension/version/load errors. If no load control is visible, STOP this branch and report it; do not invent a menu path or converter. No export/save is required. Never alter the source recording.
3. For a separately authorized existing live session: use documented **Fetch** and screenshot the complete returned instance list. Select the current character and use **Attach**. Inspect the existing injected graph selection, as in owner's prior P screenshot. Record every displayed descriptor label/ID/path, MP133_Astra2.agr, MP133_Astra2_player.asi, MasterControl and its character association. If only root player_main is available, record that; do not set up a synthetic attachment.
4. Locate W similarly: actual equipped weapon, MP133_Astra2.agr, MP133_Astra2_weapon.asi. Screenshot descriptor association. If duplicate indistinguishable MP-133s/descriptors prevent association, mark IDENTITY=UNKNOWN and STOP; graph filename alone is not an ID. Do not resolve ambiguity by gameplay actions.
5. Inspect whether a loaded recording lets both descriptors be selected within the same recorded frame context. If inspecting live and one editor cannot expose both, open a second Animation Editor instance **only if owner-approved and available**, using the same existing workspace without saving. Attach P in the first and W in the second with Fetch/Attach. Leave both attached while naturally advancing idle evaluation. Watch whether attaching the second detaches/freezes/replaces the first. This is a capability check, not an assumption that multi-editor subscription works. If only one can record, return SIMULTANEOUS_RECORDING=NO for this tested UI route; do not retry via a new transport architecture.
6. Pause only the debugger recording with its documented recording pause/rewind facility; do not pause/step simulation or use preview playback as a substitute. Inspect adjacent saved records for BOTH descriptors. Transcribe whatever capture-frame/sequence/time fields the UI actually displays. Ask: same parent recording? same frame identifier? both records present before/during/after the interval? A preview clip frame counter, separate elapsed timers or video timestamp is **not** a common simulation-frame ID. If no common frame identifier/completeness indication is offered, mark CORRELATION/COVERAGE=UNKNOWN; idle recording cannot prove one-frame command capture losslessness.
7. In each selected instance's recorded frame, inspect the read-only command-data display referenced by Live Debug documentation. Screenshot the heading and fields. Distinguish command declarations in Controls from captured command inputs. Do not click an editable command control to test it. Transcribe command name/ID/int/float fields only if actually shown. An empty idle command list is valid baseline evidence, not a positive receipt calibration. Use existing recorded commands only if already in the supplied recording; never generate new ones, including native reload.
8. At that SAME selected P record, show MasterControl and any read-only evaluated-node/path/condition information the UI exposes. Single-select existing nodes only; never double-click, play or edit. Check whether values are tied to the recorded instance/frame rather than a local preview/re-evaluation. If provenance is unclear, label CONSUMER_TRACE=UNKNOWN. Evaluation Information's clip/time/event/tag fields alone do not prove IsCommand execution. The absent custom consumer is recorded as CONSUMER_PRESENT=NO, not an observation failure or presumed engine inability.
9. Inspect rewind across adjacent P records: verify current P descriptor/ASI remains selected and recorded evaluation advances. If the command view is empty, its ability to retain a positive command is UNKNOWN unless supported by existing recording metadata/evidence. Do not use W callbacks or common marker labels as P-health evidence. Capture any missing-frame/drop status if available; absence of a status indicator is not proof of no drops.
10. Return screenshots and the worksheet below. Stop. No pulse, graph change, compile or candidate follows automatically. If required capability is absent/ambiguous, name the exact UI route and missing field; do not claim it is absent from all engine builds.

Troubleshooting boundary: if debugger is disabled or evaluation freezes on editor focus, report that and stop this procedure. Documentation mentions Start Debugger/forced updates, but changing configuration or restarting runtime is outside this prepared read-only inspection. Do not quietly repair prerequisites. Two separate idle captures are not one-pulse evidence.

## 5. Owner evidence worksheet and interpretation

```text
BUILD / RECORDING_OR_SESSION_PROVENANCE:
ACTUAL_RECORDING_EXTENSION / LOAD_RESULT:
P_DESCRIPTOR / CHARACTER_ASSOCIATION / P_ASI:
W_DESCRIPTOR / EQUIPPED_WEAPON_ASSOCIATION / W_ASI:
SIMULTANEOUS_RECORDING: YES / NO / UNKNOWN
COMMON_SIMULATION_FRAME_OR_RECORD_CONTEXT: <actual displayed field or UNKNOWN>
FRAME_COVERAGE_AND_DROP_INDICATION: <actual field or UNKNOWN>
P_COMMAND_INPUT_VIEW: AVAILABLE / UNAVAILABLE / UNKNOWN
W_COMMAND_INPUT_VIEW: AVAILABLE / UNAVAILABLE / UNKNOWN
COMMAND_ARGUMENT_FIELDS: <actual fields or UNKNOWN>
P_RECORDED_EVALUATION_ADVANCES: YES / NO / UNKNOWN
P_EVALUATED_NODE_CONDITION_VIEW: AVAILABLE / UNAVAILABLE / UNKNOWN
VIEW_IS_CAPTURED_NOT_PREVIEW_REEVALUATION: YES / NO / UNKNOWN
DIAGNOSTIC_CONSUMER_PRESENT: NO (current source)
DIAGNOSTIC_CONSUMER_EXECUTION: NOT_APPLICABLE_NO_CONSUMER
POSITIVE_COMMAND_CAPTURE_CALIBRATION: <existing evidence or UNKNOWN>
COMMAND_EMITTED_BY_INSPECTION: NO
GAMEPLAY_INPUT_USED: NO
```

- If independently scoped native P command input is visible in an existing record, that proves observed P input for that record, not a new W-to-P test, causal origin, custom-consumer execution or multiplayer synchronization.
- If dual identities/common frame context can be shown, the synchronization-of-observation gap narrows. Coverage/positive retention and absent consumer remain separate gates.
- If only one live subscription or no injection-specific command view is available, identify that specific restriction; the current read-only debugger-only route cannot satisfy the corresponding one-pulse requirement.
- If evaluation is healthy but command-view calibration is missing, a later empty P view remains INCONCLUSIVE, not delivery NO.
- If all general UI features exist, still do NOT mark DEBUGGER_OBSERVER_CAPABILITY_PROVEN for the full previous consumer criterion: the custom consumer does not exist and no pulse has been emitted. Owner must decide the precise next criterion/authorization explicitly.

This procedure can test concrete remaining debugger questions safely; it cannot manufacture an absent consumer or prove future pulse capture reliability through idle alone. That bounded usefulness supports OWNER_UI_INSPECTION_REQUIRED rather than a blanket claim of proven capability or no justified inspection path.

## 6. Protected hashes and documentation verification

PRE/POST method: recursively enumerate `.et,.conf,.meta,.c,.layer,.agr,.agf,.asi,.ast,.gproj,.anm,.txa`, sort FullName; SHA-256 UTF-8 `absolutePath|fileSHA256` rows joined by LF, no final LF. All protected roots unchanged.

| Root | Files | PRE = POST aggregate SHA-256 |
|---|---:|---|
| ARMSTMP133T4B_InstalledMagProbe | 105 | D540BE18C0EA0A4754F34D27C260F1BAF9971DC9C1B76674D095C26BC3B48B76 |
| ARMST-PLATFORM---Core | 5521 | 2EDF4D1DCA02F0C662AE1CA567D8B9655C374BC817883B7625A7AF02D8860B4B |
| ARMST-PLATFORM---Weapons | 1584 | A7C611FE0417F5A5E1DA6E4209F01E3CF846295E9ADA57999713FF1B4CC2AECF |
| Armst_Work | 163 | 62AD288141B18B222E058011B29672E23996D7B651C8C4C79E7535BD24123E29 |

Resolver PASS this phase. User explicitly prohibits rerunning unrelated failing tests/dependency repairs; no unit/integrity rerun and no repository-wide green claim. Documentation-only static check: staged name allowlist equals this report, git diff --cached --check, previous plan/sync untouched; owner audit remains excluded. Commit SHA and push result are supplied in final handoff to avoid self-referential SHA in the committed document.

## 7. Stop ledger

```text
RESULT: OWNER_UI_INSPECTION_REQUIRED
AUTHORIZATION: SOURCE_ONLY
STARTING_HEAD: 7d08fd3723a85735a64b14b1ef189ce7ffa9268f
BRANCH: t4b/installed-mag-probe
DOCUMENTS_CHANGED: reports/MP133_TASK1_DEBUGGER_CAPABILITY_GATE_01.md only
PROTECTED_HASH_GUARDS: PASS
CANDIDATE_STAGED: NO
GRAPH_PREFAB_SCRIPT_INPUT_GAMEPLAY_CHANGES: NO
WORKBENCH_COMPILE_RUNTIME_UI_EXECUTED: NO
COMMAND_EMISSION: NO
RACK: FROZEN
G3B2: HOLD
FUNCTIONAL_CANDIDATE_GO: NOT_GIVEN
NEXT: owner review; separately authorized owner-only read-only debugger inspection
```

STOP after this report's documentation-only commit/push. No implementation/install/runtime continuation.
