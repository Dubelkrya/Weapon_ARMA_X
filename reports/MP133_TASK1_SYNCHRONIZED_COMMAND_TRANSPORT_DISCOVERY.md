# MP133 Task 1 — synchronized command / AnimCommandsToBind transport discovery

Date: 2026-10-08. SOURCE / STATIC ONLY.
Repository: Dubelkrya/Weapon_ARMA_X, branch t4b/installed-mag-probe.
Starting HEAD: 4bf4f5876e97de641ecfc79a9806a37bae34199b.
Authority: [Issue 34, owner runtime + discovery task 6062981503](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6062981503), supplemented by the owner's attached detailed assignment.

## 1. Executive result

**W_SYNCHRONIZED_COMMAND_PROBE_JUSTIFIED**

Select exactly ONE future experiment: **A — W_SYNCHRONIZED_COMMAND_DELIVERY_PROBE**, with independent, passive graph-instance receipt controls. This is a recommendation to design/review that experiment after separate GO, NOT a staged candidate, install permission, command emission or runtime PASS.

There is no source-proven automatic W -> P bridge in the inspected material. The exact native meaning/default/storage of AnimSrcGCTCmd.Synchronized remains a SOURCE GAP. Nevertheless, a W-only emission experiment can directly discriminate the remaining architecture without the root BindCommand namespace already rejected by Phase 1J. It is justified as a black-box transport diagnostic, not by interpreting the checkbox label.

**Do NOT simply call the observed integer 3 on today's graph.** The inert command has no AGF consumer. Today's shell entry is boolean-driven, so absent P shell markers would be meaningless. An independently attributable P AND W receipt measurement is a prerequisite. If that cannot be designed without prohibited gameplay/pose/lifecycle changes, STOP at SOURCE_BLOCKED before any stage/install/call.

B is not selected: an explicit list with AutoCommandBind already ON does not establish a missing reverse-direction bridge. C remains a real fallback, but introduces occupied Weapon-slot and item-use lifecycle uncertainties instead of isolating command delivery.

## 2. Phase 1J runtime boundary

PROVEN BY RUNTIME means owner-supplied evidence, not a new run by this agent.

Owner [6062981503](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6062981503) reports:

```text
weapon_gate_pass
player_main.agr doesn't have command CMD_ASTRA_TransportProbe
player_main.agr doesn't have command CMD_ASTRA_AbsentProbe_ZZZ
customW=3 customCharValid=0 rootCtlValid=1 absentValid=0
```

Compile PASS is separately accepted in [6062948043](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6062948043).

- PROVEN BY RUNTIME: W can bind the custom declaration in the current equipped instance.
- PROVEN BY RUNTIME: character lookup reports player_main.agr; the root positive control succeeds and absent-name control fails.
- REJECTED FOR CURRENT RUNTIME: injected-only declaration -> ordinary CharacterAnimationComponent.BindCommand(custom).
- The explicit namespace error narrows the earlier timing caveat substantially. It is not evidence that all engine bridges are impossible.
- Earlier accepted owner evidence: P MP133_Astra2_player.asi / MasterControl exists/evaluates; WPROP yields W-only; explicit custom variable list did not deliver W -> P; W-host BindAttachment("Weapon") was unavailable.
- None of these tests emitted the custom command. W-command propagation, its graph consumption and network delivery remain untested.

Rack remains frozen: separate R in chamber-empty + Tube3>0 uses the proven SetReloadWeapon(1) route. G3B2 remains HOLD; no transport probe may reach its transaction or physical setters.

## 3. Synchronized — exact evidence and unresolved semantics

### Inspected source

Live T4B Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr:73–82 declares reload, interrupt, inspection and CMD_ASTRA_TransportProbe as four empty AnimSrcGCTCmd blocks. The custom declaration is at line 80. Full AGR contains no Sync token. Current SHA-256 equals the owner's C55D757E… checkpoint (full hash in section 13).

The owner's editor shows Synchronized=ON. That establishes the observed effective UI setting, not a serialization format or a transport direction.

Read-only command-block inspection of materialized AGR files found:

| Root | AGR files | AnimSrcGCTCmd blocks containing Synchronized |
|---|---:|---:|
| Core | 12 | 0 |
| Weapons | 20 | 0 |
| Armst_Work | 3 | 0 |
| Installed T4B | 4 | 0 |

Core player_main.agr does contain Synchronized 0/1 elsewhere, inside **variable** declarations. Those are not command metadata evidence. Do not borrow a variable's default or semantics for AnimSrcGCTCmd.

First-party [sampleweapon_01.agr](https://github.com/BohemiaInteractive/Arma-Reforger-Samples/blob/83f12390d3dd61ed834d379f621520ed9f1b891d/SampleMod_NewWeapon/Assets/Weapons/Rifles/Workspaces/sampleweapon_01.agr) likewise uses empty command blocks. This is a serialization precedent, not proof of a native default.

No AnimSrcGCTCmd schema/class definition or Synchronized command implementation was found in the installed public HTML/script documentation. Public Script-Diff exposes native callable declarations, not this editor/native implementation. Supplemental exact-name web searches did not resolve the flag; Animation Editor wiki fetches returned 403. No third-party synopsis or unrelated Arma 3 synchronization command is used as evidence.

### Answer ledger

| Question | Source-bounded answer |
|---|---|
| What is synchronized? | UNKNOWN: no precise command-field contract found. |
| Which controllers/instances? | UNKNOWN; not established as W/P, root/attachment, user/item or owner/proxy. |
| Network replication? | UNKNOWN. Neither this UI setting nor item synchronization documentation proves an RPC/reliable network command. |
| Influence on CallCommand? | UNKNOWN beyond the callable W API. |
| Influence on injection? | UNKNOWN; do not equate Synchronized with BindWithInjection. |
| Matching declarations? | A command-based consumer needs a declaration in its own control template. Same Astra AGR supplies both instances here; that is necessary for this design, not proof of routing or a universal engine rule. |
| W emission automatically visible in P? | UNKNOWN; this is A's question, not its premise. |
| Where is the ON value stored? | No explicit token in this AGR. Native class default / effective metadata / another serialized representation are possibilities, not located implementations. |
| Is ON default? | STRONG INFERENCE that some default/effective-property handling explains owner UI ON with empty blocks. Native class default and elision rule remain unverified; no global default assertion. |
| Can empty {} be replaced with guessed Synchronized 1? | NO. No syntax/schema proof and no edit authorization. |

Conclusion: the requested exact semantics cannot be fully established from available sources. This limitation must travel with any future diagnostic; do not publish "Synchronized = P/W fan-out" or "Synchronized = networking".

## 4. AnimCommandsToBind / AutoCommandBind / BindWithInjection

Structural correction: **AnimCommandsToBind is a BaseItem/WeaponAnimationComponent configuration field, not a demonstrated member of AnimationAttachmentInfo.** The actual Mosin prefab places it beside BindWithInjection and AutoCommandBind, outside the AnimInjection object. The live T4B AnimVariablesToBind list is likewise on the component.

[Official Weapon Components reference](https://community.bistudio.com/wiki/Arma_Reforger:Weapon_Components?useskin=darkvector), sections 4.8.6–4.8.8 and 4.8.15, distinguishes delayed binding, automatic template command binding and the explicit list shown when auto-binding is disabled. AnimationAttachmentInfo specifies graph, instance, entry and named root slot. The page has a misplaced synchronization description under Mesh Visibility Configuration, so that line alone is not treated as an exact list-direction contract.

[Bohemia's component parameter draft](https://community.bistudio.com/wiki/User:Reyhard/Sandbox) describes the command list as synchronization with the character graph. That phrase identifies participants, not bidirectional transport or dynamic root registration. Its tabulated generic defaults are not substituted for current inherited owner UI values.

| Mechanism | PROVEN BY SOURCE / configuration | Not established |
|---|---|---|
| AnimationAttachmentInfo | Selects the character attachment resources/entry/slot | Script getter for the existing P instance; command emission bridge |
| BindWithInjection | Command binding is delayed until injection setup | Exact native mapping creation order/frame; W -> P forwarding |
| AutoCommandBind | Automatic binding of template commands | Root namespace extension; reverse delivery |
| AnimCommandsToBind | Explicit command selection alternative | Root name synthesis; W -> P subscription; additive behavior while auto ON |
| SyncWithCharacter | Item subscribes to character animation changes/calls | Reverse subscription from item calls to character/P |
| RemoveSyncReference | Removes the synced character reference | Complete detach/re-equip scheduling or handle lifetime contract |

For ordinary character/root BindCommand(name), Phase 1J proves a root declaration is required in the tested runtime lookup. It does NOT prove that every native injection mapper must use that lookup, or that explicit-list behavior could never differ. Such native behavior remains UNKNOWN.

There is no source evidence that adding the custom name to the list makes it character-bindable. Current AutoCommandBind=ON was already effective during 1J. Under the documented auto/list relationship, adding a list without changing auto would not isolate anything. Switching auto OFF would additionally change the binding set and could break native rack/inspection subscriptions unless all effective existing bindings were preserved; it is not today's selected experiment.

Lifecycle: bind after setup is the documented ordering boundary; exact mapping tables, missing-name policy, resubscription, teardown and reequip are native gaps. Future local handles must be reacquired for the current actor/item/controller and invalidated on switch, rebuild or loss; do not implement an invalid SyncWithCharacter override (earlier owner compile rejected overriding this proto external method).

## 5. Coalition Mosin reachable chain

Pinned prefab/source checkpoint: **5f5edf96807fcbd32d8986bf26995108f99bb6fa**.
[BC_Rifle_Mosin_LINEBATTLE.et](https://github.com/CoalitionArma/Coalition-Reforger-Framework/blob/5f5edf96807fcbd32d8986bf26995108f99bb6fa/Prefabs/Weapons/Rifles/Mosin/BC_Rifle_Mosin_LINEBATTLE.et).

PROVEN BY SOURCE:

```text
M21 parent prefab
 -> WeaponComponent
 -> BCC_BoltAnimationComponent
    W AGR = {6B0505F5995CCCBF} .../BC_Mosin_9130.agr
    W ASI = {88C6B7A2EC699741} .../BC_Mosin_9130_weapon.asi
    AnimInjection:
      P AGR = same resource
      P ASI = {739826937468F3AD} .../BC_Mosin_9130_player.asi
    BindWithInjection = 1
    AutoCommandBind = 1
    AnimCommandsToBind = [CMD_BC_Weapon_Rack_Bolt]
    AutoVariablesBind = 1
    SimulateOnHeadless = 1
```

These are serialized resource references, not inspected graph bodies. BindingName is omitted in this block; do not infer its exact inherited value without resolving the parent/default.

Direct fetches at the pinned commit of BC_Mosin_9130.agr and both referenced ASIs returned 404. Indexed searches for BCC_BoltAnimationComponent and CMD_BC_Weapon_Rack_Bolt returned the prefab, not the class writer. Current search results were at de07d7a17377a6ebf857f8cb6b0bc4a63850c005; all substantive prefab claims above were checked against the pinned 5f5edf… bytes.

[addon.gproj](https://github.com/CoalitionArma/Coalition-Reforger-Framework/blob/5f5edf96807fcbd32d8986bf26995108f99bb6fa/addon.gproj) lists external dependencies, including 620E584B1D2C96A4 (the previously identified Chungus dependency). Thus this public framework is not a self-contained implementation corpus; the exact supplier of each missing GUID/class is not fully resolved.

| Reachable link | Finding |
|---|---|
| Custom declaration in Mosin AGR | SOURCE GAP: referenced AGR unavailable at that path/checkpoint |
| Root declaration | SOURCE GAP; no mounted root inspected for that dependency set |
| P/W consumers | SOURCE GAP: shared AGR reference supports intended reuse, not inspected consumers |
| BindCommand / CallCommand writer | SOURCE GAP: BCC class implementation not found |
| OnCharacterCommand override | SOURCE GAP; cannot transfer local Ithaca findings onto BCC |
| Rack initiator | Serialized click/release settings exist; no executable trigger chain established |
| List mandatory? | NOT PROVEN; AutoCommandBind=1 coexists with it, so the explicit list may be dormant/redundant |
| Actual W -> P fan-out | NOT PROVEN |

No full transport proof is claimed. BC_PumpShotgunComponent is not BCC_BoltAnimationComponent; name similarity is not a dependency resolution.

## 6. Chungus — new accessible local source evidence

A targeted local search found owner-preserved Markdown source exports, not merely the older report summaries:

`C:\Users\yshky\Documents\Codex\2026-09-29\new-chat\outputs\mp133_v3_review\ASTRA_MP133_V3_Handoff\Chung\`

| File | SHA-256 |
|---|---|
| BC_PumpShotgunComponent.md | 1E9B92277AAA868D2FB880080B1554F089D03AD69E1D4321B2327B6AAEDD5BEA |
| SCR_IthacaAnimationComponent.md | CDDD956E61DD570DD153647C8AC5CCF08DE08F898DCBB4302962A63AAA6904C3 |

Both were read completely, decoding HTML entities for viewing only; neither was modified. These are local exports with unknown upstream commit/version, not a claimed fresh upstream repository or current owner runtime proof.

BC_PumpShotgunComponent.md:439–485 TryRackBolt:

- acquires ordinary CharacterAnimationComponent through GetCharAnimComp;
- binds CMD_BC_Weapon_Rack_Bolt independently on character and W;
- calls W command AND character command separately;
- then invokes controller.ReloadWeapon.

This is explicit dual emission PLUS native reload, not one W call proven to reach P. No valid-handle checks or namespace-resolution implementation explain how its character bind succeeds. An additional root override/dependency/native context is a SOURCE GAP, not a reason to disregard our 1J error.

InitReloadSequence invokes InitPlayerAnimVariables after StartReloadTimer; InitPlayerAnimVariables binds ordinary character variables; SetAnimBoolVars writes character and W separately. SCR_IthacaAnimationComponent binds/writes both sides inside animation-event handling and contains no custom command-dispatch solution. Neither exported class defines OnCharacterCommand, SyncWithCharacter, AnimCommandsToBind or its native mapping.

Materialized Armst_Work bc_ithaca_m37.agr:70 declares the custom rack command. Its AGF:239 consumes it in ReloadActionBolt, and :1025–1026 admits it into the reload branch. P/W ASIs exist in the preserved bundle. Their existence is source evidence of separate animation mappings, not proof that either currently evaluates on MP-133.

Git history -S searches across all local refs found this command in research reports (a78d181, c8e48b2, a364a7c), not an additional tracked executable writer/root implementation. Current Core/Weapons script searches found no BC/Ithaca class/custom writer. Public code searches for both class names returned no results; search-index absence is bounded, not universal absence.

Only transport lessons are retained. No native reload, dummy ammo, SetAmmoCount, +1/fixup, spawn/attach fallback or gameplay backend was copied or called.

## 7. BaseItemAnimationComponent directionality

Exact installed SDK root:
`C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs\`

G = ArmaReforgerScriptAPIPublic/html; E = EnfusionScriptAPI/html.

G/interfaceBaseItemAnimationComponent.html:463 onward documents SyncWithCharacter; :284 onward documents OnCharacterCommand. Matching pinned [generated declaration](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/generated/Components/BaseItemAnimationComponent.c):

```text
proto external bool SyncWithCharacter(ChimeraCharacter pCharacter,
                                     bool isMainCharacter, string overrideStartNode)
proto external bool RemoveSyncReference(ChimeraCharacter pCharacter)
event protected void OnCharacterCommand(int commandID, int intValue, float floatValue)
```

PROVEN BY SOURCE: item subscribes to changes/calls made in the synced character logic; its callback observes character commands. This documents **character -> item**, not item -> character. It does not prove that no other native reverse mechanism exists.

P injection and W item are separate graph instances even when their AGR resource is identical. Shared template/resource names do not establish shared runtime command storage. The callback is notification, not an exposed P setter; logging it is not proof of P graph receipt. Callback argument ID namespace/remapping is not explicitly specified; do not compare it blindly with the W-bound integer.

OnPrepareAnimInput and OnProcessAnimOutput bracket item evaluation. Returning true suppresses default behavior; a future observer must preserve superclass/default contracts and avoid intercepting the native rack. No native body exposes whether Synchronized changes this direction.

## 8. W-side CallCommand feasibility

E/interfaceBaseAnimationControllerComponent.html exposes:

```text
proto external int BindCommand(string commandName)
proto external void CallCommand(int cmdID, int intParam, float floatParam)
proto external int BindAttCommand(int attachmentName, string commandName)
proto external void CallAttCommand(int attachmentName, int cmdID, int intParam, float floatParam)
```

W uses this family through AnimationControllerComponent -> BaseItemAnimationComponent -> WeaponAnimationComponent. Character uses BaseAnimPhysComponent's typed BindCommand/CallCommand family ([source](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/generated/Base/BaseAnimPhysComponent.c)). No cast between these owning components is justified.

Correction to potentially misleading earlier terminology: public [ECommandIDs.c](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/GameCode/Base/ECommandIDs.c) declares TAnimGraphCommand as an int typedef. The source does NOT justify saying its underlying numeric representation is inherently different. The real issue is **binding namespace/owner**, not the typedef's storage. Installed 1J compile-compatible validity logging should not be changed for this docs-only task.

| Possible outcome of a W-only emission | Conclusion before testing |
|---|---|
| A: remains in W | Consistent with W-local API and documented subscription direction; STRONG INFERENCE, not measured |
| B: also seen in P | Possible native bridge hypothesis; UNKNOWN |
| C: invokes character/root/OnCharacterCommand | Not promised; UNKNOWN. W callback receipt alone would not prove root or P delivery |
| D: shared/synchronized mapping distributes it | UNKNOWN native implementation; same AGR + ON do not establish it |

Live AGF:221 consumes booleans for shell entry; no CMD_ASTRA_TransportProbe consumer exists. Source-backed IsCommand/GetCommandI expressions exist in live rack logic and local Ithaca consumers. Existing AnimSrcNodeEvent nodes exist at AGF:697/717, but their presence is not a ready-made per-instance diagnostic with proven receiver attribution.

Therefore the callable W API is sufficient to motivate a controlled delivery question, but **not** a runnable meaningful test on unmodified graphs. Never hardcode 3; rebind by name on the current W instance. No command was called in this task.

## 9. Multiplayer / networking

[Bohemia replication documentation](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/GameLib/replication/RplDocs.c) separates simulation/presentation and streaming, and provides explicit replicated properties/RPC mechanisms. It does not identify animation BindCommand IDs as network identities.

PROVEN BY SOURCE: IDs result from a named bind on a controller; RplId is separately documented as network identity. UNKNOWN: a universal cross-machine stability rule for animation IDs. STRONG INFERENCE / engineering requirement: raw IDs must not be the replicated protocol. Resolve semantic command names/phase enum against each current local instance; integer equality is no proof of shared identity.

| Context | A: W-only command | B: explicit binding list | C: explicit ItemUse binding |
|---|---|---|---|
| Local owner | W addressability proven; P delivery untested | Config selection supported; reverse delivery untested | Current weapon eligible; occupied-slot lifecycle untested |
| Remote third-person | No automatic custom-command replication contract found | List alone is not replication | First-party MP caller precedents; exact held-MP133 path unproved |
| Dedicated server | No visible graph-evaluation requirement established | SimulateOnHeadless is configuration, not authority/replication proof | AI/mortar coordination exists; not generic guarantee |
| Command replication | UNKNOWN; Synchronized not established as network flag | UNKNOWN; local sync subscription != RPC | Native behavior not fully exposed; example callers add their own networking |
| JIP / stream-in | No persistent pulse replay guarantee | Configuration may rebuild; does not reconstruct completed cycles | Active action reconstruction/restoration unproved |
| Raw command IDs | Do not send | Do not send mapping IDs | Do not send bound IDs; bind at local target |
| Gameplay authority | Never from an unauthenticated marker | Same | Same |

Future presentation protocol needs authoritative weapon/session/cycle/phase identity, stale/duplicate rejection and join-in-progress state, not repeated ammo commits or old pulse replay. No RPC or MP implementation is proposed now. G3B2 remains the separately authenticated authoritative layer and HOLD; server correctness must not require a rendered P animation callback.

## 10. A/B/C comparison

Scores: 0 = absent/poor evidence for this purpose, 1 = conditional, 2 = favorable. These are design judgments, NOT runtime results. Full dimensions are retained rather than collapsing "callable" into "works".

| Criterion | A W_SYNCHRONIZED_COMMAND_DELIVERY_PROBE | B ANIMCOMMANDSTOBIND_PROBE | C ITEM_USE_EXPLICIT_GRAPH_BINDING |
|---|---|---|---|
| Source support | 1: W callable/bind proven; reverse mechanism unknown | 1: config documented; native mapper unknown | 2: explicit binding API + first-party callers |
| Diagnostic isolation | 2 IF independent graph receipt controls exist; bare call = 0 | 1: auto/list + mapping + missing root coupled | 0: injection collision/action lifecycle/command/tag/entry coupled |
| Reach P | 1: direct measurement, not promise | 0: no demonstrated reverse route or root extension | 1: explicit target intent; existing-instance reuse unknown |
| Keep W | 2: current W controller is sole emitter | 1: native binding-set regression possible | 1: main-user timing path, current W coexistence unknown |
| Core/root edits | None for diagnostic | None for trial; root requirement unresolved | Possibly none using existing item-action envelope, unproved |
| Graph edits | Passive receipt instrumentation required unless verified per-instance trace suffices; no shell/rack route changes | Still needs receipt measurement/consumer for delivery; list-only bind is not delivery | Entry/command/tags/out contract needed on current Astra |
| Prefab edits | None proposed | Yes: auto/list override + preserve current bindings | Not established necessary; runtime binding overrides still alter lifecycle |
| Gameplay-state risk | Low only with inert name/passive sinks/no existing routes invoked | Low physical-write risk, but native command binding regression risk | Higher: action/equip/control/injection teardown uncertain |
| Reversibility | Narrow isolated reviewed candidate; no historical restore | Must preserve complete effective binding configuration | Cancel/finish/restore contract on held firearm unproved |
| MP viability | Presentation design possible; all network behavior unproved | Local config helps no network proof | First-party network precedent, not transparent shotgun compatibility |
| Negative ambiguity | High on today's graph; reduced only by W receipt + independent P evaluation/observer controls | High: inactive list, lifecycle, missing root, no consumer | Highest: several native lifecycle causes |
| Score summary (support / isolation / P / W) | 1 / 2 conditional / 1 / 2 | 1 / 1 / 0 / 1 | 2 / 0 / 1 / 1 |

Why A: it asks the exact remaining **W -> current injected P** question with one producer and no change to command mapping, root namespace or item-use ownership. B does not yet have a source-backed reverse-direction rationale; C changes the architectural envelope. A is selected for causal discrimination, not merely fewer files.

The prior ItemUse report's chosen bind-only experiment has now been performed and failed on character registration. That historical recommendation is consumed, not repeated. Its ItemUse risk analysis remains applicable; no new full ItemUse audit is claimed here.

## 11. Exactly one next experiment — A, with prerequisites

**Proposed future stage only after separate GO: W_SYNCHRONIZED_COMMAND_DELIVERY_PROBE. Nothing is staged now.**

Goal: determine whether a single inert W emission is received by the already-equipped P instance with current owner AutoCommandBind/BindWithInjection/Synchronized settings. Do not assert the flag causes the result.

Preparation/review gates:

1. Re-read CURRENT live hashes, owner-effective settings and this plan. Use current owner graph, not old labs/backups. Freeze rack/input/prefab/native mappings/G3B2.
2. Design **passive command receipt instrumentation** in the active evaluation path of each actual instance, reading only IsCommand(CMD_ASTRA_TransportProbe) and its test nonce argument. It must not enter AstraShell/rack/inspection/reload, alter pose/control outputs, inject native events, set request booleans, replace attachment, or create new animation clips.
3. Prefer a verified per-instance editor trace if it can capture the one-frame command independently. Otherwise any minimal lab graph diagnostic branch/event design needs separate graph-edit GO and source/compile review, including distinct P/W provenance. No unspecified trace API, event node schema, dynamic source-name expression or callback forwarding is assumed available.
4. W receipt is the emission positive control. P must have independently established evaluation and observer/trace coverage at the emission frame; historical P existence alone is insufficient. Generic weapon callback count or a shared marker label cannot identify origin. If a trustworthy P observation cannot be designed, mark SOURCE_BLOCKED and do not stage a bare emitter.
5. Only after exact candidate review, owner install and owner compile PASS may a separate owner-runtime GO permit one pulse. Bind W by name on the same equipped current controller; no hardcoded 3. Log semantic session/nonce + actor/weapon/tube identities. Do not call the failed character bind route, CallAttCommand, ItemUse, native commands or additional WPROP.
6. Keep command args inert and diagnostic-only. Existing normal-R/frozen rack dispatcher is not repurposed in this discovery. No extra user key, input config, gameplay toggle or parallel reload architecture. A future runtime trigger is one-shot diagnostic lifecycle only, separately approved.
7. One trial, then STOP. Verify same Tube3, donor/target count/chamber unchanged and zero cmd2..6; no G3B2 or reload emission. No retry/polling/timing repair.

Interpretation:

| Observation | Classification |
|---|---|
| Fresh nonce received independently in W AND P, one W emission, no other producer/state mutation | Current-config W -> P delivery demonstrated; NOT five-phase reload, MP or Synchronized causal proof |
| W receipt YES; P receipt NO; contemporaneous P evaluation and passive observer validity established | Current-config W -> P delivery NOT observed; reject this narrow candidate, not every possible engine architecture |
| W receipt NO | Emission/evaluation test invalid; no conclusion about P transport |
| P observation/evaluation not controlled, missed-frame capture, ambiguous marker provenance | INCONCLUSIVE, never W-only PASS |
| Any native reload/rack/gameplay/entity mutation or command leakage | FAIL / STOP; no compensating writes or historical rollback |
| P receipt without valid W receipt | Uncontrolled producer/attribution, INCONCLUSIVE |

Synchronized ON-only PASS cannot prove flag causation; establishing that would require a separately authorized controlled flag change, not silently included here. A negative cannot distinguish metadata defaults from native mapping rejection unless further source is provided. No B or C trial is bundled or queued automatically.

Rollback: no deployment in this phase. Future rollback must be an exact reviewed forward correction from its own current owner baseline, never restoration of old graphs/scripts.

## 12. Exact limitations / source gaps

- Native AnimSrcGCTCmd definition, Synchronized contract/default/serializer and target-instance/replication semantics unavailable.
- Native BaseItem command mapping body and auto-vs-explicit precedence not exposed.
- Complete Mosin dependency graph/root/BCC writer/P-W consumers unavailable; referenced files returned 404.
- Local Chungus Markdown exports lack upstream commit/version and do not establish current runtime; explicit dual calls + native reload confound single-fanout claims.
- No implemented/source-validated per-instance passive receipt instrument exists for the inert Astra command today. Its design is a mandatory future gate.
- ItemUse occupied-slot reuse/cancel/restore, native CommandID interpretation and held-firearm network preservation remain prior gaps.
- Public commits are pinned evidence, not assumed byte-identical to installed SDK 1.8.0.13. Doxygen version/footer is not the game version.
- No runtime transport, MP, graph compile or functional reload claim is made.

Evidence categories throughout are intentional: PROVEN BY SOURCE is declaration/config/caller evidence; PROVEN BY RUNTIME is cited owner evidence; STRONG INFERENCE is not an engine guarantee; UNKNOWN/SOURCE GAP are retained, not completed by guesses.

## 13. File / hash guard proof and static validation

Protected-root manifest: recursive files with extensions .c/.et/.conf/.meta/.layer/.gproj/.agr/.agf/.asi/.ast/.anm/.txa. Sort absolute FullName; rows absolute-path|SHA256; LF-join; UTF-8; SHA-256 of the resulting byte sequence. Guards include original and new workspaces and materialized Core/Weapons/Armst_Work resources. No files were normalized.

| Root | Files | Aggregate PRE = POST |
|---|---:|---|
| Installed T4B | 105 | D540BE18C0EA0A4754F34D27C260F1BAF9971DC9C1B76674D095C26BC3B48B76 |
| Core | 5521 | 2EDF4D1DCA02F0C662AE1CA567D8B9655C374BC817883B7625A7AF02D8860B4B |
| Weapons | 1584 | A7C611FE0417F5A5E1DA6E4209F01E3CF846295E9ADA57999713FF1B4CC2AECF |
| Armst_Work | 163 | 62AD288141B18B222E058011B29672E23996D7B651C8C4C79E7535BD24123E29 |

Key current owner files:

| Installed T4B path | SHA-256 |
|---|---|
| Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr | C55D757EB85A7454DCAE27567CA96980441560805DC0B268B15DBC64ECAF97FF |
| Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c | 9ADD4AD9979382AC6B42F88209A47A11A29EB6038BE832F13D3B3EF4AA628249 |
| Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c | 241E6EC19633812740BBD25DB960E21F77A928AC2FD273C81D74B75E86BAA7BC |
| Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et | 9960A92E9A31C9F2DDC69164F8D68ED673FE5481792E30E365DFE44DFE531AF1 |

Owner-untracked reports/CORE_ARMST_READONLY_AUDIT.md is excluded; SHA-256 924DF1E42AD5C4D1ADA41BA57A1553DB9EE7962BC6488E301B042621F0182B55. Tracked diff must contain only this report and the continuation plan; labs/gameplay/resource/meta files are not staged.

Validation: addon resolver PASS. Python static suite executed with bundled Python (-B): 96 tests, failures=2, errors=10, matching recorded pre-existing Astra baseline (missing historical MP133_Astra graph/test assertions). No repairs or historical restoration. Integrity check exit 1: 10 existing broken Markdown links in unchanged reports/sync plus jsonschema absent in this bundled interpreter. No unrelated dependency install and no repository-wide green claim. No scanner build. Tests' fixture-write diagnostics refer to temporary test trees, not an installed candidate; protected root guard confirms unchanged consumed source.

Final pre/post aggregate comparison PASS: all four counts and aggregates match exactly. GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0. Exact documentation-only scope and whitespace checks PASS. Guard evidence is an in-memory comparison for this run; no scratch output was written outside git-ignored space.

## 14. Confirmation / stop

```text
FINAL_STATUS = W_SYNCHRONIZED_COMMAND_PROBE_JUSTIFIED
SELECTED_NEXT_EXPERIMENT = W_SYNCHRONIZED_COMMAND_DELIVERY_PROBE
CANDIDATE_STAGED = NO
WORKBENCH_LAUNCHED = NO
REFORGER_LAUNCHED = NO
RUNTIME_TEST = NO
FUNCTIONAL_CHANGES = NO
GAMEPLAY_FILES_CHANGED_BY_CLEANUP = 0
CALLCOMMAND_EXECUTED = NO
ITEM_USE_EXECUTED = NO
G3B2_CALLED = NO
RACK = FROZEN
NEXT_STAGE = HOLD_PENDING_SEPARATE_GO
```

Publish report + plan only, then STOP. Do not prepare the functional experiment from this recommendation.
