# MP-133 P/W animation architecture deep dive

Date: 2026-10-07. Branch: `t4b/installed-mag-probe`. Audited HEAD: `edf594d5cabf85a3ccd65a784f939ca784e11c75`.
Mode: source/static/report only. No candidate staged, installed, compiled or run. This report supersedes the narrow proposed Phase 1J discovery, not the frozen rack or owner evidence.

## 1. Result and evidence discipline

The supported model is **character host inputs -> injected P graph**, with **character -> item/W subscription** separately exposed by `SyncWithCharacter`. A weapon-local variable write is not an upstream character request. No inspected native implementation proves the reverse W->P route or a single custom-command fan-out. The most economical next experiment is **equipped-weapon attachment addressability plus isolated P-request/readback**, with explicit P-instance identification and gate telemetry. It is designed below, not implemented.

Three important corrections:

- Actual installed WPROP uses `BindBoolVariable`, `SetBoolVariable`, `GetBoolVariable`. It does **not** call `BindVariableBool` or `SetSharedVariableBool`. The attachment task and owner prose describe the latter, but inspected current bytes decide which API was tested.
- The variable-list W-only result disproves sufficiency of that configuration with the actual W setter. It does not prove every native binding is character->P, that P was evaluated, that the effective list merged, or that Shared was tested.
- A numeric attachment ID and successful readback alone do not prove that the addressed graph is P. The next experiment must independently identify the receiver and record P gates before declaring transport success.

Evidence labels: **API** = installed generated declaration/documentation, not C++ implementation; **SOURCE** = current resource/script; **OWNER_RUNTIME** = owner's supplied observation; **OFFICIAL_DOC** = BI documentation; **INFERENCE** = explicitly derived hypothesis; **UNKNOWN** = unavailable implementation/measurement. Rank: API/native source, vanilla config, working-mod source, official documentation, community, inference. Generated `proto external` declarations are not method bodies. Doxygen versions are not game versions.

Read-first set inspected: AGENTS, CURRENT_AI_SYNC, persistent plan, P_SIDE_ACTIVATION_PATH_DISCOVERY, PACT_PROBE_REVIEW_EVIDENCE, P_OWNER_AND_INSPECTION_ROUTE_DISCOVERY, P_OWNER_RUNTIME_DIAG_STAGE, ANIMINJECTION_BIND_DISCOVERY, ANIMVARIABLE_BIND_PROBE_STAGE. Historical recommendations in these reports are evidence, not fresh authorizations. CURRENT_AI_SYNC still says Phase 0 has not started; the current plan and later owner comments supersede that stale sentence.

Issue #34 comments read: [6043495333](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6043495333), [6043917747](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6043917747), [6044071573](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6044071573), [6044139957](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6044139957), [6044481757](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6044481757), [6044652747](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6044652747), [6044735859](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6044735859), [6044909936](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6044909936), [6044948637](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6044948637).

## 2. Frozen runtime facts and actual local baseline

Rack stays `physical R -> ARMST_MP133_Reload -> SetReloadWeapon(1) -> CMD_Weapon_Reload int=1 -> Weapon_Rack_Bolt`, Tube N-1/chamber 0->1/same Tube. No refactor or activation reuse. G3B2's exactly-one-shell transaction is separately proven offline and **HOLD**. Neither is an animation-transport experiment.

WPROP runs the W shell family through ReturnReady. P family absent. CharacterAnimGraphComponent and character AnimationControllerComponent accessors failed; CharacterAnimationComponent exists. These negative results concern those character accessors, not all engine objects. Phase 1I loaded the additive prefab without serialization errors, but `EFFECTIVE_UI_LIST_VERIFIED=NO`; runtime again W-only. No new runtime is claimed here.

Paths: repository `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\Weapon_ARMA_X`; V/live lab is sibling `ARMSTMP133T4B_InstalledMagProbe`; L is repository `labs/ARMSTMP133T4B_InstalledMagProbe`. Never overwrite V from L wholesale.

| Current file, relative to lab | L SHA-256 | V SHA-256 |
|---|---|---|
| Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c | F5D59DB9D00469E4664DE219CF29110A40D6DCE73DE23846ED60C44B6EFA68C1 | 54404F6B32D9599E4A4F34D3A3519FC5FC2596FDC476AD7FFA94A0F4BD960202 |
| Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c | 7BE1D37513AF31E0C5BC3629BC3301DAFABEC966129AF83D04B688DD4D19BF8A | 411D5E127C5E97D6A3BAAA91D7B79C0CE662F06600D03EC31080A2C878C72640 |
| Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et | F4A856D8452136C13033B893A1F72E72C1D0D99AF204E782726A66853BCC43F4 | 9960A92E9A31C9F2DDC69164F8D68ED673FE5481792E30E365DFE44DFE531AF1 |

V has the PACT/POWNER/WPROP scripts and additive variable-list probe; L has earlier scripts/prefab. Current V was inspected directly, not reconstructed from old staging. V input retains accepted `0xa`; L's historical `0x6` is not installation authority.

## 3. Real ownership/transport map

```text
local SCR_PlayerController.T4BRInputDown
  -> ctrl.GetWeaponManagerComponent().GetCurrentWeapon().GetOwner()
  -> current ARMST_T4B_AstraV2_WeaponAnimationComponent
       -> SetBoolVariable(local ID) -> W controller / MP133_Astra2_weapon.asi

character CharacterAnimationComponent / native character animation logic
  -> root inputs and attachment-node translation
  -> root binding "Weapon" -> injected MP133_Astra2.agr / MP133_Astra2_player.asi
  -> SyncWithCharacter subscription -> OnCharacter* on item/W

equipped weapon BaseAnimationControllerComponent.BindAttachment("Weapon")
  -?-> actual P injection                  [UNTESTED OWNER/ADDRESSABILITY]
```

| Edge | Mechanism/source | Classification |
|---|---|---|
| Physical R -> script -> current weapon | V CustomRInputProbe, guarded current-weapon lookup | SOURCE + OWNER_RUNTIME |
| Script -> W variables -> shell family | V AstraV2 T4BWPropBind/Request; local engine API | SOURCE + OWNER_RUNTIME |
| Item description -> character injection | V prefab AnimationAttachmentInfo; official component documentation | SOURCE + OFFICIAL_DOC; native attach call unavailable |
| Root -> P | attachment node translates parent controls into attached graph; Core Anims/Player/Locomotion.agf:1685-1687 `WeaponAttachment`, binding Weapon | SOURCE + OFFICIAL_DOC; actual current root evaluation UNKNOWN |
| Character -> item/W | BaseItemAnimationComponent.SyncWithCharacter and OnCharacterCommand/variable callbacks | API; rack command callback runtime precedent |
| W-local write -> P | no proven forwarding edge; Phase 1I W-only | rejected as automatic/sufficient route, not universal impossibility |
| W controller -> attachment -> P | inherited attachment APIs exist; ownership not established | API + UNKNOWN |

SOURCE for synchronized character controls is character animation logic. HOST for `Weapon` attachment is the character root graph, not the physical weapon mesh. TARGET is a separate injected graph using P ASI. OWNER of registration is native item/character synchronization; exact storage pointer/creation call unavailable. Script receiver owns W, not automatically the host's attachment. BindingName names a slot in the root, not a globally registered component. Same AGR defines compatible names, not shared runtime storage or equal bound IDs.

External source for parent-input translation: [BI Animation Editor: Nodes](https://community.bistudio.com/wiki/Arma_Reforger%3AAnimation_Editor%3A_Nodes), Attachment section. Scoped callable declarations: [BI BaseAnimationControllerComponent API](https://community.bistudio.com/wikidata/external-data/arma-reforger/EnfusionScriptAPIPublic/interfaceBaseAnimationControllerComponent.html); installed E page remains the audited signature authority. Commands are transient graph inputs rather than persistent bool state; [BI Animation Editor](https://community.bistudio.com/wiki/Arma_Reforger%3AAnimation_Editor) describes their one-frame lifetime. This distinction matters for custom-command consumption, not evidence of replication.

Core's materialized root has `WeaponBlendNode` with `Child1 WeaponAttachment`, `BlendWeight 1.0`, `Optimization Always eval both` (Locomotion.agf:5-11). This disproves a blanket claim that *all* weapon attachment evaluation requires vanilla reload. It does not prove the currently equipped T4B character uses that exact Core graph or that every ancestor of that node is active. Trace that actual runtime instance before claiming activation.

## 4. Complete observer inheritance and callable surfaces

Installed SDK base path: `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs`. E = `EnfusionScriptAPI/html`; G = `ArmaReforgerScriptAPIPublic/html`.

| Class -> base | Evidence | Relevant surface/limits |
|---|---|---|
| ARMST_T4B_AstraV2_WeaponAnimationComponent -> ARMST_T4B_WeaponAnimationComponent | V AstraV2.c:22 | WPROP variables, event observer, super forwarding; no injection getter |
| ARMST_T4B_WeaponAnimationComponent -> WeaponAnimationComponent | V InstalledMagProbe.c:49 | passive command/events; no custom host manager |
| WeaponAnimationComponent -> BaseItemAnimationComponent | G hierarchy row_6_0_5; WeaponAnimationComponent reference | weapon-specific native animation behavior |
| BaseItemAnimationComponent -> AnimationControllerComponent | G hierarchy row_6_0 | SyncWithCharacter, RemoveSyncReference, OnCharacterCommand/Bool/Int/FloatVariablet, OnPrepareAnimInput, OnProcessAnimOutput, OnAnimationEvent |
| AnimationControllerComponent -> BaseAnimationControllerComponent | E hierarchy row_58_1_0 | controller update support; inherits command/variable/attachment APIs |
| BaseAnimationControllerComponent -> GenericComponent | E hierarchy row_58_1 | BindCommand/CallCommand, BindBoolVariable/SetBoolVariable/GetBoolVariable, BindAttachment/BindAtt*/CallAtt* |
| GenericComponent | E hierarchy | entity component ownership; not character injection manager |

Exact attachment API on the equipped weapon, by inheritance:

```c
int BindAttachment(string attachmentName)
int BindAttBoolVariable(int attachmentName, string varName)
void SetAttBoolVariable(int attachmentName, int varId, float value)
bool GetAttBoolVariable(int attachmentName, int varId)
int BindAttCommand(int attachmentName, string commandName)
void CallAttCommand(int attachmentName, int cmdID, int intParam, float floatParam)
```

These are `proto external` declarations; the surprising float bool-setter argument is preserved. API existence is certain; ownership of P via this weapon instance is not. Negative bind sentinel and handle lifetime are undocumented in these pages. Rebind per current weapon/equip lifetime; never treat ID 0 as failure or reuse handles across instances without evidence. A nonnegative ID is a provisional gate, not proof of P identity.

`SyncWithCharacter(ChimeraCharacter,bool,string)` subscribes to character variable/command changes. It is native, not a script-overridable equip hook. `RemoveSyncReference` removes that subscription. Prepare/output callbacks run before/after item controller evaluation; returning true suppresses default item animation behavior, so do not use them as a casual hook. `OnCharacterCommand` is notification of an already-issued character command, not a documented upstream relay or veto.

No OnInjectionCreated, GetInjectionController, OnAttachmentAdded, OnCharacterAdded/Removed, or OnEquipped/Unequipped is exposed in the inspected BaseItem/Weapon animation member pages. These hypothetical names must not be implemented. AnimationAttachmentInfo is serialized configuration; no script-accessible runtime getter/handle was found. Native equip synchronization owns installation/removal; exact native lifecycle ordering remains UNKNOWN.

Other accessors checked: `CharacterControllerComponent.GetAnimationComponent` and `ChimeraCharacter.GetAnimationComponent` return CharacterAnimationComponent, not an attachment controller. `CharacterEntity.GetAnimGraphComponent` is API-visible but failed on this fixture. IEntity.GetAnimation returns bone/mesh animation API, not this graph control. Weapon manager supplies the actual current weapon; its animation component is already acquired successfully by WPROP. Core mutant AnimationControllerComponent precedent applies to different entities and does not establish a human host. No supported animation-manager/injection-property bridge was found; do not invent one.

## 5. AnimVariablesToBind: full variable ledger

Two distinct links must not be collapsed: root -> P attachment input translation and character -> W subscription. The [official component reference](https://community.bistudio.com/wiki/Arma_Reforger%3AWeapon_Components) describes additional named variables binding to the weapon animation graph. `SyncWithCharacter` explicitly names a character subscription. Together they support character-input synchronization, not guaranteed W-output fan-out. Exact native copy/sharing implementation is unavailable.

Materialized Core `Anims/workspaces/player/player_main.agr` declares MovementSpeed float L6, Stance int L27, State int L228, WeaponInspectionState int L318, HasOpticsAttached bool L460. This is local graph evidence, not proof of the actual mounted vanilla root. Vanilla per-item AGRs in referenced packed resources are not all materialized locally.

| Variable/type | Graph declaration | Writer/source controller | Injection host/destination | Direction/update mode | Evidence/confidence |
|---|---|---|---|---|---|
| MovementSpeed/float | materialized character root L6; grenade AGR resource referenced, declaration unavailable | native locomotion logic; exact setter body unavailable | character Grenade host -> Player_M18; subscription -> M18 item graph | root->P and character->item supported; native update schedule unknown | Smoke_M18_Base.et:79-91 lists MovementSpeed/Stance; API subscription; medium on transport, low on native writer |
| Stance/int | root L27; Astra2 AGR explicit int default0 range0..2 | native stance/controller logic; no script writer found | Weapon/Grenade host -> injected P and synchronized item | root input translation; character change callback before item evaluation supported, copy order unknown | same grenade config + current Astra declarations/API; medium |
| State/int | root L228; Astra2 AGR int -1..2 | WeaponAnimationComponent native firemode exposure; exact root writer/relay unavailable | PM Weapon host/P; PM item/W | character synchronization requested; native weapon->root population is separate and not a custom setter contract | Handgun_PM_base.et:101-113 adds State; official weapon variables describe firemode; medium type/purpose, low exact direction/order |
| HasOpticsAttached/bool | root L460; PKM AGR only packed reference | native optic/character handling inferred; exact writer unknown | Weapon host/P and PKMN item | additional character-variable subscription supported, root->P translation supported; no bidirectional guarantee | MG_PKMN.et:7-9 additive list; medium declaration/config, low writer |
| WeaponInspectionState/int | root L318; Astra2 explicit -2..2 | CharacterControllerComponent.SetInspect/SetInspectState -> native character logic; variable assignment body unavailable | Weapon host/P; synchronized W | state-driven graph entry; native update timing unknown | owner effective list; current AGF; controller API; high graph role, medium native transport |

No source proves list registration itself creates a missing variable in the host template. Explicit names in an item graph do not establish a root source. ASTRA names are absent in the inspected Core root. `+{}` is a vanilla additive child pattern (PKMN), but Phase 1I did not independently verify merging with nonserialized engine-default entries. Load success is not effective-list proof. Neither failure nor source establishes the exact class-default origin; previous claims of proven engine defaults were too strong. Parent/effective/class-native provenance remains unextracted.

## 6. Shared semantics: a different API family

G BaseAnimPhysComponent exposes `BindVariableBool(string)->TAnimGraphVariable`, `SetVariableBool(TAnimGraphVariable,bool)` and character commands. CharacterAnimationComponent adds `SetSharedVariableBool(TAnimGraphVariable,bool,bool varHasOtherUsers)`; the inspected declaration has no explanatory native body. A graph value getter equivalent to weapon GetBoolVariable is not present in the inspected character member list. Do not invent GetVariableBool on that family.

E BaseAnimationControllerComponent uses integer `BindBoolVariable/SetBoolVariable/GetBoolVariable`; it exposes attachment addressing, but not the character Shared setter. These are not interchangeable ownership domains. The [public CharacterAnimationComponent API](https://community.bistudio.com/wikidata/external-data/arma-reforger/ArmaReforgerScriptAPIPublic/interfaceCharacterAnimationComponent.html) confirms the extra user-sharing flag, not what entities/layers/native users it spans.

Consequently: thread/controller copies, graph layers, network instances, W/P and injection sharing are **all unproven meanings**, not alternatives we can select by naming. Shared is not documented as network replication or W->P delivery. It still requires a valid handle in the character API domain. The failed WPROP experiment did not test it. Missing native semantics are explicitly UNKNOWN rather than an asserted exclusion of every injection relationship.

## 7. AutoCommandBind and custom command feasibility

Official component docs say auto binding covers commands in a template; BindWithInjection delays command binding until character injection setup. Binding resolves a name to a controller-specific ID. `BindCommand(string)->int` / `CallCommand(int,int,float)` operate on the addressed engine controller; attachment versions resolve in an attachment context. `OnCharacterCommand` proves incoming character-to-item notification. None of these facts documents outgoing W-to-character forwarding.

Same AGR permits the same command name in W and P, but does not prove ID equality across bound/root/translated contexts. Always bind independently, never copy W IDs into character or P calls. Current Astra2 declares reload, interrupt, inspection only. A proposed `AnimSrcGCTCmd CMD_ASTRA_ShellReload {}` can be authored in ControlTemplate.Commands, as the local BC graph demonstrates custom declarations. It then also needs an AGF consumer: declaring or emitting it alone cannot activate today's variable-only shell entry.

Whether arbitrary commands are mapped via AutoCommandBind when absent from the character root is UNKNOWN. An automatic name matching mechanism needs some parent command to receive; auto binding is not documented as adding commands to that parent. Root presence could be required for a root-origin call; a correctly addressed attachment call could avoid that requirement. No working source example proves ONE W CallCommand delivers to both W and P. Therefore `AUTO_COMMAND_PROBE_JUSTIFIED` at the API/authoring level, **not AUTO_COMMAND_W_TO_P_SOURCE_PROVEN**. Ideal single-command architecture remains conditional, not chosen over a lower-cost owner test without proof.

## 8. Inspection tracer and independent regression

`CharacterInspect` is referenced in Core chimeraInputCommon.conf. Exact current packed vanilla binding/context is unavailable; near-version controls and past owner Hold-R success support collision, not exact source proof. V custom context claims KC_R at Priority20000/Flags0xa; if owner's actual inspection uses R, input collision is a strong candidate. Other bindings and native eligibility must also be checked. Do not declare a graph deletion or proven context cause.

Native receiver API: CanInspect(target), SetInspect(target), SetInspectState(int), GetInspect, GetInspectState, GetInspectEntity, OnInspectionModeChanged. SetInspectState accepts desired states 0 default/1 alternate; graph state values -2..2 are not a one-to-one public caller enum. Previous report describing GetInspect as IEntity is incorrect: it is bool, while GetInspectEntity returns IEntity.

Current chain: CharacterInspect -> native character handling -> inspection mode/state -> WeaponInspectionState/root controls -> translated Weapon P attachment + character->W subscription -> Idle/Buffer2 -> WeaponInspection/WeaponInspectionSTM. The native command-emission middle is not extracted. Current AGF entry actually reads WeaponInspectionState; CMD_Weapon_Inspection is declared but has no transition consumer in the inspected Astra2 AGF. Therefore this graph's inspection is **variable/state-driven**, not proven command-driven. Keep a declaration distinct from use. Reload int1 exits inspection into rack independently and remains frozen.

Safe tracer design, not selected next experiment and not executed: after separate owner approval, CanInspect(current weapon), one SetInspect(current weapon), desired SetInspectState(0), passive root/P/W state and inspection-clip observation, then documented mode disable after confirming its targetItem disable semantics. No reload command, no ammo writer; preserve input context. Do not guess null-disable or fake graph negative-state values. This tests downstream bridge independently of physical input; context A/B is a separate input experiment, not mixed into shell test.

## 9. Corpus search and non-reload references

Bounded `rg` search covered materialized catalog .et, current Weapons/Core scripts/configs/graphs, installed API trees, and Armst_Work BC graphs; not every packed vanilla resource. Negative coverage is reported, not filled with fabricated examples.

| Family | Current source example | Architecture evidence / remaining gap |
|---|---|---|
| Pistols | catalog/Handguns/PM/Handgun_PM_base.et:101-113; M9:101-110 | separate W/P ASI, Weapon binding, explicit State; native firemode transport not custom W fan-out |
| Rifles | catalog/Rifles/AK74/Rifle_AK74_base.et:215-220; M16:282-287; VZ58:307-312 | item injection + BindWithInjection; inspect/safety/modes are nonreload consumers; native writer bodies unavailable |
| Machine guns | PKMN.et:7-9; PKM_base.et:261-266; M249_base.et:239-244 | additional optic bool; multiple injection config variants; no arbitrary upstream command proof |
| Grenades | Smoke_M18_Base.et:79-91 | BaseItemAnimationComponent, Grenade binding, Player_M18 ASI, MovementSpeed/Stance; throw/pin logic shows transport not restricted to reload |
| Underbarrel | UGL_M203_base.et:307-310, M16A2_M203.et:59 | native context/priority variation, auto variables; reload commands deliberately excluded as transport |
| Launchers/tools | Launcher_M72A3_base.et:237-242; ExplosiveCharge_base.et:132-144 | injection and deploy/unfold/item behavior; official CMD_Weapon_Unfold example is not ammunition reload |
| Binoculars | Core Prefabs/Items/Equipment/Binoculars/Binoculars_M22.et | child references packed vanilla base; no materialized base animation block, so complete transport UNKNOWN |
| Stationary | catalog/core/Mortar_Base.et:384-401; HMG_NSV_base.et:264-270; Tripod_Base.et:167 | separate WeaponMasterControl W start, P injection, AlwaysActive, auto command/variables; proves start nodes can differ |

Inspection is the strongest current nonreload tracer because its AGF/ASI are materialized and owner historically observed it. Mode/safety/fire/optic/mortar examples demonstrate native transport and specializations, not a safe custom shell API. `CharacterControllerComponent.TryUseItemOverrideParams(ItemUseParameters)` also exists: accepts a custom character command, action tags/alignment and item-use handling. It is **not** an animation-only setter and may alter input/item-use state; candidate only after a specific custom-action contract, never a covert native-reload replacement.

## 10. Chungus re-audit: transport only

Current Armst_Work bc_ithaca_m37.agr declares custom CMD_BC_Weapon_Rack_Bolt (L70) plus PumpShotgunStopReloading/CloseActionFlag. AGF consumes that command at rack entry L239 and emits StartReloadTimer L1249. Scripts are absent in inspected local roots; prior report excerpts about BC_PumpShotgunComponent are lower-confidence historical evidence, not freshly verified full source. Public searches found mod identity/integrations, not a complete authoritative current implementation.

Historical excerpts put InitPlayerAnimVariables after StartReloadTimer/native reload activation and describe explicit weaponAnim.CallCommand AND charAnim.CallCommand. These do not prove single-emission fan-out or a reload-free P starter. Useful lesson: custom graph names and two explicit sinks are feasible patterns. Forbidden gameplay ReloadWeapon/dummy/fixups/whole-mag backend is not borrowed. No source claim that Chungus solves our exact gate.

## 11. P graph gates and animation resource health

Current V AGR DefaultRunNode is MasterControl. Owner effective P StartNode also MasterControl. AGF MasterControl always evaluates IdleReloadSTM and SightPose. Idle begins unless inspection state -1/-2. Shell entry at AGF L221 requires ALL:

```text
ASTRA_ShellRequest && ASTRA_ShellEligible
&& !ASTRA_ShellStop && !ASTRA_FireStop && !Firing
&& WeaponInspectionState == 0 && Stance == 0
&& !IsCommand(CMD_Weapon_Reload)
```

All four writes alone are therefore insufficient proof. P Stance, inspection, firing, FireStop, command-in-frame, current state and actual host evaluation are independent gates. Root may supply nondefault Stance while W stays default0. No current P telemetry excludes this alternative. Shell branch selects only Erc; prone/crouched shell entry is not supported by current Stance==0 (rack separately supports Erc/Pne). Do not silently widen it.

Start/Grab stop tests are at clip end; Insert proceeds to CheckContinue; CheckContinue repeats only with Repeat AND eligibility/no stop/fire. Repeat defaults false. End->AstraWaitRelease->Idle requires Request false. W ReturnReady reset can happen before a late P has finished; future dual bridge needs session-aware BOTH-side completion, not W-only reset assumption. No latch rewrite now.

| P ASI mapping | .anm GUID | Bytes | Static result |
|---|---|---:|---|
| Reload.Erc.StartReload | FCB314232D355753 | 4439 | exists, meta matches |
| Reload.Erc.GrabShell | 1D4C14261EFC54DB | 7195 | exists, meta matches |
| Reload.Erc.InsertShell | D3868FB32BF75DEE | 8514 | exists, meta matches |
| Reload.Erc.CheckContinue | 36BCB6296CAE5334 | 4441 | exists, meta matches |
| Reload.Erc.EndReload | D1B33891A663548D | 4584 | exists, meta matches |

Paths are V `Assets/MP133_AstraShellGraph/Clips/P_Astra_<phase>.anm`, intentionally protected original clips referenced by the new graph. AST Reload has Erc/Pne columns and these five source names; current shell GroupSelect chooses Erc. ASI Template matches current AST GUID BDD6F7ED84814A1E; AGR references that template. W mappings are separate W_Astra resources. No missing P shell file/GUID mismatch found. Binary import/event/skeleton validity, resource mounting, actual playability and absence of silent fallback are **OWNER_RUNTIME_REQUIRED**, not statically proven. TXA marker suffix provenance does not establish which compiled resource actually ran. Current repo lacks some materialized live ANMs; never manufacture them to satisfy tests.

## 12. Candidate matrix

API support is not end-to-end proof. MP potential means a design can be replicated later, not that current calls replicate.

| Candidate | Source / runtime support | Simultaneous P/W | Gameplay reload | Graph edit | Script owner | MP potential / risk / proof cost | Recommendation |
|---|---|---|---|---|---|---|---|
| AnimVariablesToBind | native config + character subscription; current experiment W-only | not demonstrated | no | no | valid character source needed | medium; direction/effective list; low but repeat would retest same hypothesis | not repeat unchanged |
| AutoCommandBind | official template binding; no custom fan-out runtime | unknown | no | custom consumer yes | emitting owner unresolved | medium; false fan-out assumption; medium-high | viable only with proven source owner |
| BindAttCommand | exact inherited API; runtime untested on weapon | lookup only, not execution | no | custom declaration yes | correct attachment host | medium; ID/owner; low lookup cost | requires addressability first |
| CallAttCommand | exact inherited API; runtime untested | P plus explicit W maybe | no | consumer yes | identified P host | medium; one-frame/lifetime; medium | after receiver proof |
| Host direct variable bridge | exact inherited Bind/Set/GetAtt API; W host relation unknown | explicit two sinks | no | no | actual equipped weapon plus P address | good design potential; owner/gates; lowest bounded discriminating test | **best next bridge** |
| Custom AGR command | BC declaration precedent; no current custom command | ideal fan-out conditional | no | yes | emitter plus mapped parent | good if supported; root namespace; higher test surface | architecture rank2 |
| Standard engine relay | native inspection/rack precedent | standard actions yes | not necessarily | shell semantics yes | character engine | medium; hijack inspection/gameplay; medium | tracer, not final shell transport |
| Graph follower/root bridge | attachment translation source | possible with real parent signal | no | yes, parent/consumer | root producer still required | medium; protected Core/root scope; high | fallback design only |
| Native reload activation | established old route | may activate both | **yes** | irrelevant | native | unacceptable magazine risk | **rejected** |
| Item-use custom action | TryUseItemOverrideParams API | unknown for this weapon | no reload, but native item-use | yes | character action command | medium; tag/input/lifecycle side effects; high | not first animation-only test |

## 13. Exactly one next bounded experiment (DESIGN ONLY)

Name: **W_HOST_P_ATTACHMENT_IDENTITY_AND_REQUEST**. Not a custom-command gamble and not a new character FindComponent enumeration. No preparation or runtime permission is implied by this report.

After independent approval, prepare a minimal animation-only change against the **current installed V bytes**, not the older L file. No graph/prefab/input/clip changes; no G3B2; rack helper byte-frozen. Scope a single equipped-weapon owner session; no additional physical key or permanent toggle.

1. Owner confirms current mounted graph and actual character `Weapon` attachment in Animation Editor Live Debug. Record root resource, P ASI, start node, current state and all entry gates. If P injection is absent or wrong-resource, stop with `P_INJECTION_NOT_IDENTIFIED`; do not create/replace it.
2. On that actual equipped AstraV2 component, bind `Weapon` using inherited BindAttachment; bind the existing four bools with BindAttBoolVariable; log receiver/weapon/session/IDs and P/W snapshots. Bind/read only first. Rejected/ambiguous handles -> stop with `W_HOST_ATTACHMENT_UNAVAILABLE`; do not fall back to unrelated owner or guess an ID sentinel.
3. Establish receiver identity before activation: keep Request false and observe in owner live debug an Eligible false->true change made only through SetAttBoolVariable, then restore its prior value. Confirm it changes the identified P controls, not merely W/root/another attachment. Unknown identity -> stop, no request. Never change FireStop/Firing/inspection/stance to force a pass; observe them.
4. Only when P is Idle/MasterControl, standing/no inspection/no firing/FireStop false/no reload command and all physical telemetry valid, write P Eligible=true/Repeat=false/Stop=false/Request=true through the verified attachment API. Use the existing complementary W request once in the same session. Setter value argument remains float 0.0/1.0. No native command or ammo mutation.
5. Record P and W first-phase, five phases, insert marker and ReturnReady independently; visually confirm both actual sources. Clean Request/Eligible on identified P deterministically after P ReturnReady; verify four-bool cleanup on both sinks. A qualified manual abort remains cancellation only if independently reviewed; never use W ReturnReady alone to certify P cleanup. No timer or second insertion cycle.
6. Snapshot same Tube3 entity/component, count/capacity, donor, barrel and chamber before/after; no cmd1 from shell, no cmd2..6, no G3B2. Weapon switch/detach/ownership change invalidates all handles/session; cancel safely, no replay. Stop on any gameplay mutation or uncertain cleanup. Owner alone compiles/runs after separate GO.

This ONE experiment separates (a) weapon can address existing P, (b) inherited attachment methods exist but weapon is not host, (c) P input arrives but graph/parent gate blocks evaluation, (d) P runs but resource/event delivery fails. It also prevents a misleading W-only getter pass. The identity step is not proof of bidirectional AnimVariablesToBind or arbitrary custom-command support.

PASS: actual P-instance readback/identity + P and W phase families/visual playback, clean resets, same Tube3, unchanged ammo/donor/chamber and no forbidden commands. FAIL labels: addressability absent; receiver ambiguous; P gate blocked; P evaluated but missing clip/event; W-only; mutation; cleanup failure. Each identifies a distinct boundary. Addressability failure rejects this owner, not every attachment API. Transport success with no P phase means inspect the recorded gate/evaluation evidence, not add reload activation.

Why not custom command first: current graph has no custom command consumer, so it needs both graph authoring and a still-unproven upstream fan-out. This receiver test uses existing variables and phases, minimizes changed surface and establishes the owner needed by both direct-variable and attachment-command designs. Why not repeat list probe: the exact prior practical hypothesis already failed.

Rollback: do not install a candidate without review; if a separately authorized probe fails, stop session, preserve logs and current source, request a forward correction. No old backup/graph restoration, destructive Git, graph reattachment or live wholesale copy.

## 14. Multiplayer architecture, design only

Animation calls are presentation, not automatic replicated intent. No API page inspected makes Shared or CallCommand a broadcast guarantee. Each client must resolve its local W/P instances after replicated equip; do not transmit bound IDs or pointers. Future authority is one server-owned session/cycle transaction, with authenticated actor/current weapon/installed tube/donor checks. Owner input sends intent, not a trusted insert-event reward. Presentation receives accepted phase/session/cycle/stop state and authoritative timing; remote clients execute their local P/W presentation. Late join/switch cancels stale session and rebinding is mandatory.

G3B2 must execute once under authoritative server validation, retain conservation/quarantine/delayed verification, and remain independent of two cosmetic marker deliveries. Dedicated server cannot rely on SimulateOnHeadless clips/events firing. Client P/W marker never authorizes ammo by itself; duplicated cosmetic W/P/network callbacks must not double-transfer. Verification controls continuation. Current offline probe proves neither this replication contract nor remote third-person playback. All promising candidates need this same authority layer. [BI replication overview](https://community.bistudio.com/wikidata/external-data/arma-reforger/EnfusionScriptAPIPublic/Page_Replication_Overview.html) supports separation of simulation and presentation.

## 15. Reassessment of previous assumptions

| Assumption | Verdict | Reason |
|---|---|---|
| WPROP used Shared | PREVIOUS_ASSUMPTION_FALSE | installed and L source call SetBoolVariable |
| Shared means W/P or network | PREVIOUS_ASSUMPTION_WEAK | declaration has no such contract |
| list addition must copy W custom outputs into P | PREVIOUS_ASSUMPTION_FALSE as sufficient current route | owner W-only; exact native direction remains unknown |
| list is an explicit synchronization selection | PREVIOUS_ASSUMPTION_CONFIRMED structurally | config/API/official docs |
| load proves effective default-list merge | PREVIOUS_ASSUMPTION_WEAK | effective UI not verified; serializer/native defaults unavailable |
| AutoCommandBind guarantees reverse W fan-out | PREVIOUS_ASSUMPTION_WEAK | auto registration != upstream emission |
| BindingName Weapon identifies root slot | PREVIOUS_ASSUMPTION_CONFIRMED | official attachment docs + materialized root node |
| BindWithInjection creates an upstream transport | PREVIOUS_ASSUMPTION_FALSE as documented meaning | documented command-binding setup gate, not reverse bus |
| same AGR means shared values/IDs | PREVIOUS_ASSUMPTION_FALSE | distinct instances/ASI and scoped binding |
| only character FindComponent can locate P controls | PREVIOUS_ASSUMPTION_WEAK | equipped weapon inherits attachment API; relation untested |
| missing P marker proves request absent | PREVIOUS_ASSUMPTION_WEAK | state/gates/evaluation/resource/event alternatives remain |
| inspection command triggers today's graph | NEW_FINDING: not supported | state variable controls entry; command declaration unused in AGF |
| vanilla reload is always necessary to evaluate Weapon attachment | PREVIOUS_ASSUMPTION_WEAK | materialized root has always-evaluated Weapon blend; actual runtime root still unknown |

## 16. Static validation and preservation

Weapons path resolver PASS (validated external addon). Repository integrity failed with **10 existing broken Markdown links**, unrelated to this report. Initial sandbox unittest run: 96 tests, 2 failures/52 errors, including temp permission errors and stale Astra fixtures. An escalated run exited1; its captured tail is not a reliable complete summary, so no revised count or green claim is made. A repeat was rejected by safety review because connector tests print writes to graph/ASI fixtures; no bypass/retry performed. Read-only inspection of test_mp133_lab_connect_anims.py shows make_lab uses temporary fixtures; protected-root hashes independently confirm no actual gameplay mutation. No old resources restored to appease tests.

Pre/post SHA-256 guard: sorted absolute full-path plus per-file SHA rows, UTF-8 joined with LF, aggregate SHA-256. Extensions c/conf/et/meta/layer/gproj/agr/agf/asi/ast/anm/txa. Both snapshots match:

| Protected root under addons | Files | Before = after SHA-256 |
|---|---:|---|
| ARMSTMP133T4B_InstalledMagProbe | 105 | 4FEA157584BB49F6177AE83A6D1D48B928637905F46EE543C3CF5258AC464C8E |
| Weapon_ARMA_X/labs | 58 | 505C52A752D320DC69DD4E53E297AF87EF10ECC622AC04CDB07D2FEBC38D644C |
| ARMST-PLATFORM---Core | 5521 | 2EDF4D1DCA02F0C662AE1CA567D8B9655C374BC817883B7625A7AF02D8860B4B |
| ARMST-PLATFORM---Weapons | 1584 | A7C611FE0417F5A5E1DA6E4209F01E3CF846295E9ADA57999713FF1B4CC2AECF |

GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0. Owner-untracked CORE_ARMST_READONLY_AUDIT.md excluded. Only this report and plan continuation are publication scope. No Enfusion executable was launched. External findings above are citations to current official sources, not native implementation claims.

## TOP_3_ARCHITECTURES

1. **Explicit W + identified P attachment variable bridge**, one session coordinator, existing shell graph. Best first proof cost; conditional on actual owner/addressability. Not a parallel gameplay reload system.
2. **One custom command via proven host mapping**, custom AGR command and shell-only consumer, or explicit attachment/W sinks under one coordinator if single fan-out fails. Ideal one emission only if proven; never hardcode cross-controller IDs.
3. **Parent-input/follower architecture** with a real root producer and current P attachment translation. Requires separately authorized root/graph scope and full preservation review; cannot synthesize input from a follower alone.

## REJECTED_ARCHITECTURES

- Native reload/SetReloadWeapon/cmd2..6 as shell activation, dummy ammo or whole-mag replacement.
- Repeating character-root ASTRA binding without a declared source, unavailable human component lookups, guessed injection getters or casts.
- Hijacking inspection as permanent shell transport, unconditional Shared fan-out, W-only PASS, same-AGR shared-memory assumption.
- Gameplay transaction attached before P/W proof, client-event ammo authority, graph follower without producer, historical graph restoration.

```text
PW_ARCHITECTURE_DEEP_DIVE = COMPLETE

ANIMVARIABLESTOBIND_DIRECTION = character synchronization into item/W supported; root-to-P attachment translation documented; native custom reverse/shared direction not proven
SETSHAREDVARIABLE_SEMANTICS = character API with other-users flag; exact native sharing scope unknown; actual WPROP uses SetBoolVariable, not Shared
AUTOCOMMANDBIND_SEMANTICS = template command binding gated by injection setup; no proven W-to-P fan-out
CUSTOM_COMMAND_W_TO_P = authoring and scoped APIs supported; end-to-end single-emission route unproven
W_HOST_ATTACHMENT_API = inherited callable signatures confirmed; ownership of existing P remains untested
INSPECTION_TRANSPORT = native character state to root/P translation and item subscription; current AGF entry is variable-driven; input regression unproven
P_GRAPH_ADDITIONAL_GATES = Idle/evaluated MasterControl; Eligible; no Stop/FireStop/Firing; inspection0; stance0; no reload command in frame
ASI_P_PATH_HEALTH = five shell ANM/meta GUIDs and mappings statically consistent; actual mounted playback/event health owner-runtime required
MP_ARCHITECTURE_RISK = local presentation is not replication or ammo authority; server session/cycle validation and proxy playback still required

BEST_NEXT_BRIDGE = identified existing P attachment addressed from equipped weapon plus explicit W request under one session
BEST_NEXT_PROBE = W_HOST_P_ATTACHMENT_IDENTITY_AND_REQUEST (design only)
WHY_THIS_PROBE = uses current graph and exact inherited APIs; separates ownership, transport, gates and resource/event failure before command redesign
WHAT_IT_PROVES = whether this equipped weapon can actually address and start identified P independently of native reload, alongside W
WHAT_RESULT_PASS_LOOKS_LIKE = identified P readback and both P/W phase families/visual playback, clean resets, same Tube3, unchanged ammo/donor/chamber, no cmd1..6 from shell/G3B2
WHAT_RESULT_FAIL_LOOKS_LIKE = absent or ambiguous attachment, gate/evaluation failure, missing P resource/event, W-only, mutation or failed cleanup; stop at exact failed boundary

FUNCTIONAL_FILES_CHANGED = NO
PREFAB_CHANGED = NO
GRAPH_CHANGED = NO
SCRIPT_CHANGED = NO
INPUT_CONFIG_CHANGED = NO
G3B2_CHANGED = NO
LIVE_CHANGED = NO
WORKBENCH_LAUNCHED = NO
RUNTIME_TEST = NO
```
