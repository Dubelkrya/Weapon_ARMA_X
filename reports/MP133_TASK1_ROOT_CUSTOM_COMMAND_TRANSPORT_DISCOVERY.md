# MP133 Task 1 — root custom command transport discovery

Date: 2026-10-07. Branch: t4b/installed-mag-probe.
Source checkpoint: aea719515359eba8429988f085ed9f13ca49443f.
Authority: [Issue 34 comment 6046106020](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6046106020).
Scope: source/static research; report and continuation plan only.

## Result

`ROOT_CUSTOM_COMMAND_PROBE_JUSTIFIED`

A callable character command API and documented character-to-item command subscription exist. Neither the installed public SDK nor the inspected materialized sources proves that binding a name on the character searches commands declared ONLY in its injected graph. Therefore root-to-P custom transport, automatic P/W fan-out, and a complete replacement reload are NOT source-proven.

Exactly one next experiment is proposed in section 6: injection-only custom-command BIND registration, without calling it. It is not staged, installed, or authorized to run by this report.

## 1. Accepted runtime boundary

Owner evidence in comment 6046106020: qualified shell R; rack rejected on state; equipped weapon BindAttachment("Weapon") returned -575451861; probe rejected it; no variable reads occurred. WPROP subsequently showed W only. Same Tube3, 0/3, chamber true, no G3B2. Classify current W attachment route rejected, not all attachment APIs or P existence.

The negative integer is the observed value and the probe's rejection result. The native implementation of BindAttachment and its complete invalid-handle contract are not exposed here; do not infer a universal handle encoding from its sign alone. No retry or changed validity rule is proposed.

Owner Live Debug separately identifies MP133_Astra2_player.asi / MasterControl as present and evaluating. These are owner observations, not new agent runtime tests.

## 2. Exact callable surfaces

Installed documentation root:
`C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs`.
G = ArmaReforgerScriptAPIPublic/html; E = EnfusionScriptAPI/html.
Installed declarations were inspected directly; online wiki semantics are supplementary, not a claim of exact native implementation for 1.8.0.13.

| Object / acquisition | Exact declaration | Evidence |
|---|---|---|
| ChimeraCharacter | proto external CharacterAnimationComponent GetAnimationComponent() | G/interfaceChimeraCharacter.html:126 |
| CharacterControllerComponent | proto external CharacterAnimationComponent GetAnimationComponent() | G/interfaceCharacterControllerComponent.html:127 |
| CharacterAnimationComponent inherits BaseAnimPhysComponent | proto external TAnimGraphCommand BindCommand(string pCommandName) | G/interfaceBaseAnimPhysComponent.html:126; inherited at CharacterAnimationComponent:162 |
| Same character API | proto external void CallCommand(TAnimGraphCommand pCmdIndex, int intParam, float floatParam) | BaseAnimPhysComponent:141; CharacterAnimationComponent:177 |
| Same character API | proto external void CallCommand4I(TAnimGraphCommand pCmdIndex, int intParam1, int intParam2, int intParam3, int intParam4, float floatParam) | BaseAnimPhysComponent:142 |
| Weapon's BaseAnimationControllerComponent family | proto external int BindCommand(string commandName); proto external void CallCommand(int cmdID, int intParam, float floatParam) | E/interfaceBaseAnimationControllerComponent.html, member documentation |
| Same engine controller family | int BindAttachment(string attachmentName); int BindAttCommand(int attachmentName, string commandName); void CallAttCommand(int attachmentName, int cmdID, int intParam, float floatParam), each proto external | same E reference |
| BaseItemAnimationComponent | proto external bool SyncWithCharacter(ChimeraCharacter pCharacter, bool isMainCharacter, string overrideStartNode) | G/interfaceBaseItemAnimationComponent.html |
| Item observer | void OnCharacterCommand(int commandID, int intValue, float floatValue) | same G reference |

The already used character getter avoids rejected character FindComponent enumeration. CharacterAnimationComponent is not BaseAnimationControllerComponent: no justified cast or BindAttachment method on it was found. GetCommandHandler() returns CharacterCommandHandlerComponent; its GetControllerComponent() returns CharacterControllerComponent, whose animation getter returns the same character API family. This is not an exposed engine attachment-controller bridge.

Treat bound handles as belonging to the object/controller and lifecycle that produced them. No inspected contract guarantees cross-controller equality or transferable IDs. Even if two integers coincide, bind W and character independently. TAnimGraphCommand is the character API type; do not assume its representation from the weapon int API.

## 3. What automatic binding proves

[Weapon Components](https://community.bistudio.com/wiki/Arma_Reforger:Weapon_Components?useskin=darkvector), sections Bind With Injection, Auto Command Bind and AnimationAttachmentInfo:

- BindWithInjection delays command binding until character injection setup.
- AutoCommandBind binds the template's commands automatically.
- AnimCommandsToBind is the explicit-list alternative.
- BindingName names a slot in the root graph.

This supports configuration and setup timing, not dynamic extension of a root command namespace. It does not document whether an injected-only command is discoverable by BaseAnimPhysComponent.BindCommand, or whether a successful bind supplies a mapping into the active P instance.

The installed BaseItemAnimationComponent docs explicitly describe subscription to character animation changes/commands, and OnCharacterCommand as notification of a command called in the synchronized character logic. This supports character -> W observation. It does not prove W -> P forwarding, nor P consumption of an arbitrary root call.

Current live prefab Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et:12-25 uses the same Astra AGR for W/P, separate ASIs, Weapon binding, BindWithInjection 1. AutoCommandBind is not explicitly serialized in that block. Its effective value must be inspected before a future experiment; omission is NOT proof of ON.

## 4. Graph and source precedents

Paths below are relative to the named addon, inspected read-only.

| Source | Evidence | Limit |
|---|---|---|
| Live T4B Assets/MP133_AstraShellGraph_test/MP133_Astra2.agr:73-79 | only CMD_Weapon_Reload, CMD_Weapon_Action_Interrupt, CMD_Weapon_Inspection are declared | no custom shell command exists today |
| Live T4B same workspace .agf:221 | shell entry requires request AND eligible, stop/fire/inspection/stance guards, and no reload command | CallCommand alone cannot activate this existing boolean-only entry |
| Core Anims/workspaces/player/player_main.agr:463 onward | root command declarations, including reload, action interrupt, healing | materialized Core graph is not proof of exact runtime-mounted root |
| Core Scripts/Game/Items/ARMST_Consumable.c:255-274 | character getter -> BindCommand for CMD_HealSelf/Other/Revive; rejects negative IDs | normal root commands, not injection-only registration or direct P delivery; never invoke healing as a test |
| Weapon_ARMA_X catalog/Rifles/AK74/Rifle_AK74_base.et:215-220 | vanilla snapshot injection + BindWithInjection 1 | native weapon precedent, not arbitrary custom dispatch implementation |
| Armst_Work bc_ithaca_m37.agr:70 and .agf:239,1026 | custom CMD_BC_Weapon_Rack_Bolt declaration and graph consumers | transport writer is absent from inspected local script corpus |

Chungus historical script excerpts in earlier reports are not fresh full source and cannot prove a reload-free P starter. No Chungus backend is imported. The current source search covered Core scripts, Armst_Work materialized resources, live T4B resources, catalog references and installed API HTML. It did not extract all packed vanilla scripts/native engine bodies. No complete vanilla/mod custom root -> injected-only command example was found within that coverage.

Declaration requirements:
- A consuming graph must have the named command and an explicit consumer.
- Whether injection setup alone makes that name root-bindable remains UNKNOWN.
- Adding it to both root and injected AGR may be an architectural fallback, but is NOT proven sufficient and would cross today's protected root/Core boundary.
- A successful root bind is not delivery; W callback is not P delivery; graph entry requires independent P evidence.

## 5. Timing, dual sinks, multiplayer

[Animation Editor, Commands](https://community.bistudio.com/wiki/Arma_Reforger%3AAnimation_Editor?useskin=darkvector) describes commands as one-frame instructions that reset after execution. They are not persistent booleans or a queue that can safely wait for injection. Bind/dispatch only after the current actor, equipped item and injection lifecycle are ready; invalidate handles on replacement, re-equip or graph rebuild. Exact root/P/W evaluation order and loss/coalescing behavior are not specified by the inspected API.

BaseAnimPhysComponent's SetVariableFloat documentation recommends scripted PreAnimUpdate for variables and warns native character commands may overwrite manually set values. This is a warning about evaluation order, not proof that a custom command must be sent using SetCurrentCommand. Starting/replacing a scripted character command would be a separate architecture, not an innocuous transport helper.

BaseItemAnimationComponent.OnPrepareAnimInput / OnProcessAnimOutput are before/after item controller evaluation; returning true stops default behavior. Do not change their return contract to force the experiment.

Dual-sink design is only conditional: script request -> independently bound W CallCommand and character CallCommand. The second call still needs the unresolved root -> P mapping. Two callable methods do not remove that gap. Also, if character calls already propagate to W, an additional W call can duplicate the pulse. Determine actual delivery before adopting dual sinks; no assumption of atomic same-frame P/W updates.

No inspected command API promises RPC/replication. Future MP presentation must resolve local graph handles per instance, driven by authoritative session/cycle state. Never replicate raw bound IDs. A client animation marker cannot authorize ammo transfer; G3B2 remains on hold. Offline presentation success would not establish dedicated server, remote-client or JIP behavior.

## 6. Exactly one next bounded experiment — root registration of an injected-only custom command

Purpose: answer whether injection setup makes a new command name bindable through the real character API, before emitting any command.

This is a proposed FUTURE stage requiring separate authorization because it needs one additive AGR declaration and diagnostic script changes. Nothing is prepared or installed now.

1. Use current V resources as baseline; preserve hashes. In a separately reviewed candidate, add only an inert command declaration named CMD_ASTRA_TransportProbe to the Astra AGR Commands list. No AGF consumer, no ASI/clip change, no root/Core declaration.
2. Review effective AutoCommandBind=ON and existing BindWithInjection=1; if effective auto-bind cannot be established, classify the test inconclusive rather than silently editing a prefab.
3. Use the proven actor -> CharacterAnimationComponent getter. Log actor/current weapon identity and raw bind results for CMD_ASTRA_TransportProbe; bind the same name independently on W as a declaration control. A root-known command may be bound as a positive control ONLY, never called. Log an absent-name negative control ONLY, never call it.
4. Owner takes one bounded pre-equip/post-equip pair after compile/install approval, with P injection confirmed evaluating post-equip. No R, WPROP, CallCommand, setters, reload, inspection, G3B2 or ammo/chamber changes. Avoid polling or timer guesses.
5. Desired discriminating result: root custom bind changes from absent to resolvable after injection, W resolves it, positive/negative controls differ as expected. This supports injection-dependent REGISTRATION, not P transport.
6. If root result remains indistinguishable from absent-name control while W resolves, stop: injection-only root registration not demonstrated. Do not proceed to command emission, root patching, dual sinks or attachment searches automatically.
7. If both absent and custom names return apparently valid values, bind is not a sufficient existence test; classify INCONCLUSIVE. Handle positivity alone is not proof.
8. Even registration PASS still needs a separately authorized command-consumption experiment to prove P delivery. Do not award P/W animation PASS here.

Rollback: no deployment in this phase. Future candidate rejection means no install; any installed future experiment requires a separately reviewed forward correction from its own baseline, never restoration of old graphs.

Why this experiment: it isolates the unknown namespace registration with the smallest additive declaration, avoids native commands, and cannot confuse W-only animation with P delivery. Dual sinks and root-host attachment are not selected.

## 7. Read-only evidence / validation

Pre/post SHA-256 guards cover .c/.et/.conf/.meta/.layer/.agr/.agf/.asi/.ast, sorted absolute-path + SHA-256 rows, LF-joined UTF-8 then aggregate SHA-256. No compiled/editor resources were generated.

| Root | Files | Aggregate before / after |
|---|---:|---|
| Installed T4B | 76 | 73C95773C27396D3DFEF7C77B598DF5083030B88FF153DE338035581AB559611 |
| Core | 5520 | 52F62C8EA31290883D68D49A9117CE4035F6F88DCED0A9F4532D8914AB1CA805 |
| Weapons | 1209 | C9259A50027D3584A632EB10035355B1A5A2BD2282302922458C0EC2F5C58144 |
| Armst_Work | 152 | 452F397F9320DCE85A04C18C6E98D8864A52C6AC4E0F83C3B1586C0ABEDAE099 |

Final guard comparison PASS: all four aggregates exactly unchanged. GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0. Functional files changed: 0. No install, Workbench, compile, runtime, commands or gameplay writers executed.
Report checks: API signatures, source locations, exact scope/diff and whitespace. Runtime transport remains unverified.
Addon resolver PASS (validated Weapons identity). Repository integrity check reports the same 10 previously known broken Markdown references in SOURCE_ATLAS, V3_T4B report and CURRENT_AI_SYNC; none points to either changed document. No repository-wide green claim. Full Python unit suite was not rerun for this documentation-only discovery; earlier execution restrictions around that suite remain respected. No Enfusion compile was performed.

