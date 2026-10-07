# MP133 Task 1 — ItemUse / equipped Weapon injection compatibility discovery

2026-10-07. Source-only. Repository checkpoint ba4a2337662a63bf6b6e749da43f8678d62c17e2, branch t4b/installed-mag-probe.
Authority: [6046340236](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6046340236).

## Decision

**CUSTOM_COMMAND_BIND_PROBE_REMAINS_BEST**, as a proposed next diagnostic, not stage authorization.
CUSTOM_COMMAND_STAGE=HOLD. FUNCTIONAL_CHANGES=NO. RUNTIME=HOLD. G3B2=HOLD. RACK=FROZEN.

ItemUse is a real general-purpose engine mechanism and the public API explicitly permits the current weapon. It is NOT rejected as an architecture. However, safe reuse of an already occupied Weapon injection, its teardown/restoration and current MP-133 item-action lifecycle are unproven. The source does not support an animation-only ItemUse trial on the current graph yet.

The CommandID contradiction is narrowed substantially: character-bound IDs are used throughout the public callers, not just mortar. The generated item-component comment is inconsistent with these callers. Native interpretation/remapping is not public; no claim that the engine has been explained completely. Detailed outcome below.

## Evidence scope and provenance

Bohemia public source is pinned to commit **3d77cc212d5cda9922daf5f45635c7300d2d4cce**, rather than floating main. Search returned 13 files for TryUseItemOverrideParams: 11 executable caller files plus 2 generated declarations. All 13 were fetched at that commit. Searches for both graph-binding setters returned the parameter declaration and mortar only. Supporting controller, inventory and health-consumable sources were also fetched.

This is coverage of accessible indexed Bohemia source, not proof that all versions, packed resources or native implementation were searched. Public source commit is not established as byte-identical to installed 1.8.0.13. Installed SDK HTML confirms current-weapon eligibility, the relevant callable parameter methods and cancellation methods; its documentation omits some comments present in public generated source. Live Astra resources and Core scripts were inspected read-only.

Reference keys:

- [PARAM](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/generated/Character/ItemUseParameters.c): all parameter fields.
- [CTRL](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/generated/Components/CharacterControllerComponent.c#L332): native entry declaration and eligibility/tag documentation.
- [HANDLER](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/generated/Character/CharacterCommandHandlerComponent.c#L30): IsUsingItem, cancellation/finish.
- [EVENTS](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Character/SCR_CharacterControllerComponent.c#L258): native-to-script callbacks.
- [MORTAR](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/GameCode/Components/SCR_MortarMuzzleComponent.c#L192): explicit graph binding example.
- Installed SDK: Workbench/docs/ArmaReforgerScriptAPIPublic/html/interfaceItemUseParameters.html, interfaceCharacterControllerComponent.html:5684-5689, interfaceCharacterCommandHandlerComponent.html.

## A. Field contract

All setters below are proto external void; implementation/default values are not exposed. “Required” describes what the examined contract supports, not invented engine validation.

| Field / exact setter | Meaning / state relevance | Required vs omitted evidence |
|---|---|---|
| SetEntity(IEntity entity) | Item being used; references an entity, not a request to clone it. No promise that engine will preserve inventory/equip ownership. | Every explicit builder supplies it; must precede SetItemGraphEntryPoint. |
| SetCommandID(int cmdID) | Command to be called. Item-origin comment conflicts with character-origin callers. | Every explicit builder supplies ID; namespace must not be guessed. |
| SetCommandIntArg(int), SetCommandFloatArg(float) | Command arguments, graph-dependent. | Float frequently omitted; mortar omits both. Do not assume omitted values for a custom graph. |
| SetItemGraphEntryPoint(string) | Resolves an item-graph node after entity assignment; getter returns int. | Optional override in callers; only mortar uses it. Not documented as a handle to existing P instance. |
| SetCharGraphBindingName(string) | Character graph binding receiving the item entry node. | Optional override; mortar explicitly uses Weapon. Collision/replace/reuse policy is undocumented. |
| SetKeepInHandAfterSuccess(bool) | Controls post-success hand retention. Cancellation comment allows competing actions to hide the item. | Set in all explicit examples. True is not a guarantee against weapon switching or reparenting. |
| SetIsMainUserOfTheItem(bool) | One main user receives full animation synchronization, including timing correction; short-term extra users should be false. | Usually omitted. Mortar false, disarm mine true. No basis to copy mortar false onto weapon owner. |
| SetAllowMovementDuringAction(bool) | PARAM says whether movement is allowed. | Set by callers, false commonly; detonator true. CTRL's parameter description reverses this wording, another documentation inconsistency; do not infer runtime movement behavior solely from it. |
| SetMaxAnimLength(float) | Timeout sends the selected command with int -1 to start an Out animation; tags may finish sooner. | Placement 15.0, consumables configured duration; others omit. Default and hard-stop guarantee unknown. |
| SetAlignmentPoint(PointInfo) | Alignment target for character hand/prediction. | Optional in practice: build/deploy/detonator omit; support station can pass null; mortar supplies a point. No MP-133 pivot invention. |
| SetKeepGadgetVisible(bool) | Keeps a gadget visible while another item is used. | Mortar true, disarm false, generally omitted. Does not guarantee firearm visibility. |
| SetIntParam(int) | Documented BodyPart value for healing. | Not an Astra phase/command substitute. |
| Reset() | Cleans parameter object. | No evidence it cancels a running action, undoes injection or restores equipment. |
| bool TryUseItemOverrideParams(notnull ItemUseParameters) | Attempts native item-use action. CTRL identifies current gadget OR current weapon. | Return true is accepted/started, not completed: placement distinguishes immediate failure and asynchronous end. |
| bool CanUseItem() | General eligibility. | Deploy source explicitly warns true can occur during gadget equip before animation is ready. Insufficient readiness proof. |

## B. CommandID: what is resolved and what remains native

Observed chain in mortar: CharacterController.GetAnimationComponent -> CharacterAnimationComponent.BindCommand(CMD_Item_Action) -> ItemUseParameters.SetCommandID. Mines, explosive charge, placement, support station, detonator, building and deployment use the same character-origin pattern. Consumable health code binds CMD_HealSelf / CMD_HealOther / CMD_Revive through CharacterAnimationComponent too.

[Health implementation](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Components/Gadgets/SCR_ConsumableEffectHealthItems.c#L105) and [consumable builder](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Components/Gadgets/SCR_ConsumableEffectBase.c#L109) establish the indirect case.

| Hypothesis | Finding |
|---|---|
| IDs are accepted from character API | SOURCE PRECEDENT: repeated across distinct first-party callers. |
| IDs are always interpreted exclusively in root namespace | NOT PROVEN: native dispatcher absent. |
| ItemUse remaps character IDs into item graph | NOT PROVEN: no visible mapping body/table. |
| Generated item-origin comment is stale/incomplete | Proven inconsistency; stale/incomplete is plausible explanation, not verified history. |
| Mortar works because CMD_Item_Action exists in both graphs | NOT PROVEN: no complete pinned mortar graph/root pairing inspected. Even presence would not establish ID equivalence. |
| Some special shared command registry/native handling exists | POSSIBLE, unsupported by available implementation. Do not assume. |

Thus we can reproduce the first-party calling convention for a known item action in design, but cannot safely generalize it to arbitrary custom IDs or swap character/item IDs. Do not compare numbers across controllers as proof.

Locally, Core player_main.agr:574 declares CMD_Item_Action; live Astra AGR does not. Core materialization is not proof of mounted character root identity. The currently known P graph evaluating does not settle item-use command routing.

## C. All accessible executable callers

Links are pinned; “omitted” does not mean false or true. All rows use character-origin command IDs, except consumable dispatcher accepts supplied parameters whose health builder uses character-origin IDs. E/B = explicit item entry / character binding override. None is an inspected held-firearm + pre-existing same Weapon slot preservation example.

| Caller | Entity / already-in-hand evidence | Command; E/B | Keep/Main flags | Lifecycle, state and network evidence |
|---|---|---|---|---|
| [Detonator](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Components/Gadgets/SCR_DetonatorGadgetComponent.c#L184) | GetOwner gadget; IN_HAND mode lifecycle at 458 | named ANIMATION_BIND_COMMAND, int1; no/no | true/omitted; movement true | Animation/ended subscriptions before start, removed at end; gadget toggle has client handling + AskToggleGadget. No Weapon slot override. |
| [Support station](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Components/Gadgets/SCR_SupportStationGadgetComponent.c#L98) | Gadget owner; held-gadget lookup exists, not a firearm | CMD_Item_Action, supplied int, float2; no/no | true/omitted; move false | Optional alignment; separate finish method; no replication guarantee established by this call. |
| [Multipart deploy](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/UserActions/SCR_DeployMultiPartInventoryItemAction.c#L352) | GetHeldGadget; explicit IN_HAND readiness check at 140 | CMD_Item_Action,int1; no/no | true/omitted; move false | FinishItemUse(true) on stop; action cancellation; player/AI owner and entity-owner gates. Deploying object and animated tool are distinct. |
| [Consumable dispatcher](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Components/Gadgets/SCR_ConsumableEffectBase.c#L63) | Supplied consumable item; function itself does not establish equipped state | provided params; base builder health command; no/no | base false/omitted; move false | Returns acceptedAction. Configured timeout; derived effects and finished listeners may consume/delete item. Never copy their gameplay callbacks. |
| [Placement](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Components/SCR_ItemPlacementComponent.c#L257) | m_PlacedItem, inventory-placement workflow | CMD_Item_Action,int1; no/no | false/omitted; move false; max15 | Caller explicitly disables weapon/movement controls; subscribes before call, immediate false path handled; cancel uses CancelItemUse; server RPCs perform placement. These explicit control writes are caller behavior, not proof native ItemUse always does them. |
| [Mortar](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/GameCode/Components/SCR_MortarMuzzleComponent.c#L179) | GetOwner mortar, stationary interaction; not current held shotgun | CMD_Item_Action; FireMasterControl/Weapon | false/false; gadget visible true; move false | Owner/AI split; AI reliable broadcast of loader/shell IDs; animation/end listeners; FinishItemUse(false), camera cleanup. Failure calls TransferShellToMortar: prohibited fallback for our design. |
| [Activate mine](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/UserActions/SCR_ActivateMineUserAction.c#L30) | Action owner mine; transforms it before start | CMD_Item_Action,constant int; no/no | true/omitted; move false | Base action/native lifecycle outside local call; alignment supplied; no proof of arbitrary equipped weapon preservation. |
| [Disarm mine](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/UserActions/SCR_DisarmMineAction.c#L33) | Mine action owner; registers user | named binding command,constant int; no/no | true/true; gadget visible false; move false | Alignment; action/native lifecycle; surrounding mine mutation not reusable. |
| [Explosive charge](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/UserActions/SCR_ExplosiveChargeAction.c#L73) | World/action charge owner | configured use command,int3,float0; no/no | true/omitted; move false | Alignment; end subscription occurs after call; ProcesFinished removes listener, derived action owns effects. MP-133 design must not assume this subscription order race-free. |
| [Campaign build](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/UserActions/SCR_CampaignBuildingBuildUserAction.c#L34) | GetBuildingTool -> held gadget, IN_HAND check | CMD_Item_Action,int1; no/no | true/omitted; move false | Cancel/confirm -> FinishItemUse(true); continuous gameplay action separate from animation. |
| [Campaign disassembly](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/UserActions/SCR_CampaignBuildingDisassemblyUserAction.c#L67) | Held building tool, not destroyed target | CMD_Item_Action,int2; no/no | true/omitted; move false | Player/AI owner gate, finish on cancel; gameplay proxy gate; destruction cleanup calls CancelPlayerAnimation. |

This breadth demonstrates a general item-action framework. It does not demonstrate transparent coexistence with a firearm's active Weapon injection.

## D. Same MP-133 compatibility matrix

| Invariant | Source conclusion |
|---|---|
| Current weapon eligible as entity | YES at public API contract level; also in installed documentation. |
| Same weapon manager ownership/equip slot | UNKNOWN across begin/end/cancel; SetEntity carries reference but is not preservation contract. |
| Same physical Tube3 | No direct mag replacement is required by parameter API; native side effects/events on our graph unproven. Not guaranteed. |
| Chamber unchanged | No chamber setter in proposed parameter construction; no proof native action/graph events leave it unchanged. |
| ADS, fire, safety/firemode | Continuous availability not promised by an item-use action. Restoration unproven; placement shows caller-level controls can be disabled. |
| W controller identity and evaluation | No documented replacement requirement, but active/rest/sync behavior on same held weapon unknown. |
| Existing Weapon P injection | Critical unknown: reuse vs replace vs stack vs teardown; same binding name does not mean same instance. |
| Input context | No input-config edits needed in theory; native action can change accepted inputs. |
| Entity/Rpl identity | Passing entity avoids an explicit new entity request, but no lifecycle/network identity preservation proof. |
| Weapon switch / re-equip | Need cancellation, stale session rejection and fresh binding; no automatic restoration promise found. |

Answer: an equipped weapon is an intended category, but the exact MP-133 combination is NOT proven safe. ItemUse starts a separate action state, not a read-only address lookup. Whether it suspends/replaces the existing weapon injection cannot be settled by these script sources.

## E. Graph requirements and gaps

Live Assets/MP133_AstraShellGraph_test was searched for CMD_Item_Action, TagRItemAction, TagLItemAction and Event_DetachCharacter: no matches. Current AGR has native reload/action-interrupt/inspection commands; shell branch entry is request/eligible boolean-driven. MasterControl continuously evaluates the existing graph and does not by itself define an item-action completion contract.

- Dedicated entry: not universally required by API, but mortar uses one. Reusing MasterControl safely is unproven; it does not magically enter AstraShell.
- Command: native CMD_Item_Action could be the lifecycle envelope with a graph consumer, or a custom command could be designed. Neither activates today's graph as-is.
- Root declaration: CMD_Item_Action exists in materialized Core root, mounted root still requires identity evidence. A new custom root name reintroduces the previous registration uncertainty.
- Injected declaration: a command-based consumer needs it. Current Astra lacks CMD_Item_Action and a custom shell-use command.
- Item action tags/out behavior: CTRL relates early completion to TagRItemAction/TagLItemAction, PARAM sends int -1 on timeout. A max length is not a guaranteed emergency reset. Correct enter/loop/out design must be proven before calling.
- Prefab AnimationAttachmentInfo: API overrides entry/slot at call time, so a prefab change is not demonstrated necessary. That does not establish collision-safe reuse of its existing Weapon binding.
- P/W: main-user timing synchronization is documented, but main-user default and interactions with the existing owner are not. Do not copy mortar's secondary-user false flag.

No AGR/AGF/ASI/prefab changes were made or staged.

## F. Lifecycle / cancellation / MP

EVENTS: native OnItemUseBegan(params) forwards entity/params. OnItemUseEnded(params,successful) invokes Ended listeners, then Finished listeners, then may call characterInventory.UseItem on the hand-slot gadget. Finished listeners may delete consumables. [Inventory OnItemUsed](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Inventory/SCR_CharacterInventoryStorageComponent.c#L1410) filters for consumables before quick-slot restock; this does not establish that all mod listeners are harmless. No direct matching item-use overrides were found in searched local Core/T4B scripts.

| Event | Source / implication |
|---|---|
| Success | Asynchronous ended callback, not boolean return; unsubscribe and verify identities. KeepInHand flag governs post-action policy, not all state. |
| Cancel | HANDLER.CancelItemUse documented immediate, no out animation, hides gadget. PARAM cancellation-retention wording has exceptions. Cannot promise safe firearm rollback. |
| Graceful finish | HANDLER.FinishItemUse(bool) requests finish/Out behavior and retention if possible; no guarantee broken graph exits. |
| Switch | Native interruption details unavailable; need original actor/weapon/tube token validation, never finish a newer unrelated action. |
| Fire / ADS / safety | No per-input cancellation/restore contract found. Do not assume preserved control state or borrow native reload. |
| Movement | Parameter exists; generated descriptions conflict; chosen behavior needs owner check. |
| Damage / incapacitation | Character has damage/state mechanisms, but no exact item-use teardown proof here. Unknown. |
| Timeout | Command int -1 emitted; graph must implement suitable out behavior. Missing tags could instead finish too early. |
| Remote clients | Public examples have explicit ownership logic; one successful local call is not proof of remote P/W playback. |
| AI | Mortar explicitly broadcasts loader/shell data because AI user-action broadcasting differs; not plug-and-play parity. |
| Dedicated server | No requirement to evaluate visible animations for gameplay is established; authoritative transfer must remain independent. |

Possible stuck/hidden/detached outcomes are risks to test, not observed failures. No automatic setter-based repair, force-equip, inventory reparent or timeout Reset workaround is justified.

Future gameplay authority remains separate from presentation. No G3B2 call may be driven by an untrusted remote marker. Replicate semantic session/cycle state and identities, never animation command handle numbers. Public mortar RPCs illustrate specific coordination, not a generic ItemUse replication guarantee.

## G. Comparison and exactly one next experiment

Scores: 0 = no demonstrated support / poor, 1 = conditional, 2 = favorable within the bounded purpose. These are engineering judgments, not runtime results.

| Criterion | Injected-only bind diagnostic | ItemUse explicit binding |
|---|---|---|
| Source support | 1: callable bind, injection-only lookup unknown | 2: current weapon category + explicit binding APIs/caller |
| Changed surface | 2: inert declaration + diagnostic script | 0: lifecycle entry/consumer/tags/out and script need design |
| Existing weapon-state risk | 2: no action/command emitted | 0: native item-use and occupied slot lifecycle unresolved |
| Root/Core edits | 2: none in first diagnostic | 1: possibly none with native envelope, unproven on Astra |
| Reach P | 0: registration only, not delivery | 1: explicit attachment intent, instance reuse unproven |
| Keep W synchronized | 0: not tested | 1: main-user mechanism, existing-owner interplay unknown |
| MP viability | 0: not tested | 1: first-party MP examples, custom path still unproven |
| Reversibility | 2: no action state entered | 0: restoration after cancellation not established |
| Diagnostic power | 2: isolates one namespace question | 1: several coupled unknowns would confound failure |

**Choose ONE: the previously specified injected-only custom-command registration experiment**, with custom stage still HOLD pending explicit subsequent authorization. This choice does not overturn the owner's HOLD. It is a recommendation after comparison, not permission to start.

Future bounded design: add one inert CMD_ASTRA_TransportProbe declaration only in a reviewed Astra copy; use actual character getter and independent W BindCommand, before/after qualified equip; include root-known positive and absent-name controls, no calls/setters/item use/R/WPROP. Verify effective AutoCommandBind and BindWithInjection. If controls do not establish meaningful lookup semantics, return INCONCLUSIVE. A resolved root handle proves at most registration; never P delivery. Details remain in the preceding root transport report, section 6.

Why not ItemUse runtime next: no safe candidate parameter set, graph completion contract or occupied-slot restoration proof exists. A trial would change more than one unresolved mechanism. ItemUse remains the stronger architectural fallback IF binding transport fails, but it needs a lifecycle design and controlled ownership investigation before an actual start.

Rollback for this phase: documentation-only forward correction. No functional candidate exists to install/revert. Do not restore historical scripts/graphs.

## H. Validation and unchanged-source ledger

Guard extensions: .c/.et/.conf/.meta/.layer/.agr/.agf/.asi/.ast. Sorted absolute-path|SHA256 rows, LF UTF-8 aggregate. Pre/post compare performed before commit.

| Root | Files | SHA-256 before/after |
|---|---:|---|
| T4B | 76 | 73C95773C27396D3DFEF7C77B598DF5083030B88FF153DE338035581AB559611 |
| Core | 5520 | 52F62C8EA31290883D68D49A9117CE4035F6F88DCED0A9F4532D8914AB1CA805 |
| Weapons | 1209 | C9259A50027D3584A632EB10035355B1A5A2BD2282302922458C0EC2F5C58144 |
| Armst_Work | 152 | 452F397F9320DCE85A04C18C6E98D8864A52C6AC4E0F83C3B1586C0ABEDAE099 |

Only this report and continuation plan are permitted in commit. Owner CORE_ARMST_READONLY_AUDIT remains excluded. No functional tests, compile or runtime performed for this research. No CallCommand, TryUseItemOverrideParams, native reload or G3B2 executed.

Final guard comparison PASS for all four roots; GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0. Addon resolver validates Weapons. Repository integrity retains 10 existing broken Markdown links in unchanged SOURCE_ATLAS, V3_T4B and CURRENT_AI_SYNC documents; no errors name the two changed files. Full Python suite not rerun for this documentation-only phase, respecting earlier suite execution restrictions. No repository-wide green or runtime compatibility claim.
