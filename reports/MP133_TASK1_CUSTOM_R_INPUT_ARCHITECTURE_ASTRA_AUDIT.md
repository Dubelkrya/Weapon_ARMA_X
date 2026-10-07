# MP-133 — Custom R input architecture: Astra audit

Date: 2026-10-07. Research/source only. Base: `2aca17379af76b7eb5582287dcd01dcdcb57035d`, branch `t4b/installed-mag-probe`.

## 1. Proven current state

**Main finding:** registration of an independent resource was mistaken for an override of the resource selected by the game. The installed base-game project explicitly selects input GUID **795184CF9AD764DB**. Core preserves that identity; T4B uses **1CECBCDC65A5CA96**. Identical filenames do not establish resource identity.

This audit supersedes the discovery/identity claims in the old B0 report, not its owner observations. No old report or gameplay file was edited. The latest directly supplied owner task authorizes this separate report only; older Issue tasks requesting code changes or edits to the B0 report are historical.

Evidence classes: **LOCAL_SOURCE** (files inspected now), **OWNER_RUNTIME** (existing owner logs, not agent tests), **OFFICIAL_SOURCE** (BI documentation/installed SDK), **PUBLIC_WORKING_MOD** (published mod source, not locally runtime-certified), **COMMUNITY_CLAIM** (not accepted as engine proof), **INFERENCE** (explicit conclusion from evidence).

- Git HEAD/branch exactly match the requested checkpoint; origin is `https://github.com/Dubelkrya/Weapon_ARMA_X.git`.
- Initial index clean. Sole untracked file: `reports/CORE_ARMST_READONLY_AUDIT.md`; untouched and excluded from commit.
- Read AGENTS, CURRENT_AI_SYNC, B0 report and relevant Issue history, including permanent no-runtime rule [6024370185](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6024370185), registration/review/activation stages and [latest owner result 6032219329](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6032219329).
- Existing owner log `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\logs\logs_2026-10-07_09-16-17\console.log`: lines 271/284/708 identify game **1.8.0.13**; lines 925/992 show `result=false active=false actionPresent=false`. Reading this log did not launch anything.
- `RESOURCE_FILE_REGISTRATION=PASS`, `PLAYERCONTROLLER_LISTENER=PASS`, `T4B_WEAPON_GATE=PASS`, `CUSTOM_R_RECEIVED=NO`, `VANILLA_RELOAD=YES` are owner evidence. Listener log means the registration call ran; it is not proof the action exists.
- Live, labs and staged input config/script contents match byte-for-byte (hashes in verification appendix).

## 2. Why actionPresent=false matters

The probe enumerates `GetGame().GetInputManager().GetActionCount()` / `GetActionName(int)`. Its custom action is absent from that manager, before input conflict resolution. `ActivateContext` cannot repair missing config incorporation. Changing R to F10, tweaking Priority, or reworking listener lifecycle cannot independently establish incorporation.

Scope caveat: this enumeration is evidence about the queried manager, not every conceivable separately registered ActionManager. There is no separate-manager registration in the inspected T4B code. The one-shot scan is not a permanent monitor of later manager rebuilding.

Resource registration, selection by the game, construction of action/context objects, context activation and physical-input dispatch are distinct gates. The previous statement that a registered file works "if and only if" registered was too strong.

## 3. How Reforger loads input configs

**Exact installed source:** `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\addons\data\ArmaReforger.gproj`, PC configuration, lines 331–339:

```text
InputManagerSettings InputManagerSettings "{50A48858902D5F64}" {
 Default "{795184CF9AD764DB}Configs/System/chimeraInputCommon.conf"
 UiMappings "{0AD37213EFEB0B61}Configs/System/chimeraMapping.conf"
 HoldDuration 250
 ClickDuration 250
 DoubleClickDuration 250
 RepeatInitialInterval 400
 RepeatInterval 50
}
```

The project also sets `InputSettingsPath "ReforgerUserInput.conf"` at line 10: user settings are not the default action-definition resource. There is one `Default` resource reference in this installed settings block, not an array or wildcard directory scan. Neither the T4B nor Core descriptor replaces it in inspected source.

**Answers:** InputManager initialization consumes a project-assigned default resource; its assignment is a GameProject setting, not an inferred hardcoded filename. Native C++ initialization code is not shipped in inspected sources, so the exact internal function/call stack is unavailable. The reference is GUID-qualified. BI's [Input Manager documentation](https://community.bohemia.net/wiki/Arma_Reforger%3AInput_Manager?useskin=darkvector) independently identifies the config's purpose.

There is one selected default **resource identity**, which can have multiple addon override layers. This does **not** imply the engine permits only one config/manager overall: InputBinding custom config arrays and RegisterActionManager are exposed separately (§7/§10). No source-backed automatic discovery of every same-path, differently identified addon config was found.

## 4. Same-path resource behavior

[BI Data Modding Basics](https://community.bohemia.net/wiki/Arma_Reforger%3AData_Modding_Basics) distinguishes override, duplicate and inherited resources. Overrides retain the original GUID; duplicate/inherited resources have separate identities. Configs support selective overrides, not whole-file replacement. Multiple addon overrides are explicitly described. [Workbench Metadata](https://community.bohemia.net/wiki/Arma_Reforger%3AWorkbench_Metadata?useskin=darkvector) identifies GUID as the engine identity; the path stored in metadata is informational.

| Owner | Virtual path | Resource identity | Relationship to selected input resource |
|---|---|---|---|
| Installed vanilla project | `Configs/System/chimeraInputCommon.conf` | `795184CF9AD764DB` in Default | Selected base identity |
| Local Core | same | `795184CF9AD764DB` in `.meta`, line 2 | Override identity matches |
| T4B live/labs | same | `1CECBCDC65A5CA96` in `.meta`, line 2 | Independent resource; identity does not match |
| T4B staged config | same | No staged `.meta` | Text candidate, not independently registered input layer |

**Classification: F — GUID-selected configuration with type-specific override composition.** Neither A "all same paths merge" nor B "last same-path file entirely replaces previous" describes this mechanism. Dependency ordering can matter between legitimate overrides; it cannot turn a distinct GUID into the selected resource.

`CORE_PLUS_SYNTAX_PROVES_MULTI_ADDON_RESOURCE_MERGE = NO`.

`ActionRefs +{` is an additive operation within a participating config object. It does not cause that resource to participate. Core's syntax alone never proved discovery; Core's matching identity supplies the missing explanation. Same-path/different-GUID resources can exist in different addon namespaces, but coexistence does not mean both feed this manager. The exact fallback for a bare path collision is not established and is unnecessary to explain the GUID-qualified default.

Bounded source result: **T4B is not an override of the selected default input identity.** Confidence HIGH. Actual effective mounted layers and the result after correction still require owner verification; no post-fix runtime success is claimed.

## 5. Core vs T4B

Core root: `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Core`.

Core chain from current source:

```text
GameProject Default GUID 795184CF9AD764DB
  -> matching Core .conf.meta -> config override content
  -> ARMST_PDA_Touch / Wheel / WheelMinus declarations
  -> ARMST_Pda3DContext and ARMST_Pda3DFocusContext
  -> owner-local PDA inspection context activation
  -> mouse bindings -> listener / value polling -> PDA interaction
```

- `Configs/System/chimeraInputCommon.conf`: Touch uses `mouse:button0`, Wheel `mouse:wheel+`, WheelMinus `mouse:wheel-`; contexts at lines 234–269 reference these actions.
- `Scripts/Game/Devices/ARMST_PDA_COMPONENT.c`: lines 633–634 activate the contexts, 966/971 read wheel values, 1319–1320 bind DOWN/UP to OnCursorDown/OnCursorUp, 1328–1329 remove listeners. ResetContext calls at 406–407 reset action state; they are not documented DeactivateContext calls.
- Core also writes `CharacterFire=0` and freelook action values around 637–641. Thus PDA success does not independently prove selective R consumption by context priority alone.
- `Scripts/Game/Camera/ARMST_CharacterCameraCustomPoint.c:122` also activates the PDA context.
- T4B's equivalent file has a new independent resource identity, no parent declaration and no project Default reassignment. Its registered action definition has no demonstrated route into the selected default resource.

Core's live runtime success is owner-reported; this audit traces its static implementation, not a new PDA test. The failing log's list of addon search directories is not proof every listed addon was mounted.

The key-binding menu is a separate identity: SDK `SCR_SettingsManagerKeybindModule.KEY_BINDING_CONFIG` is `{4EE7794C9A3F11EF}Configs/System/keyBindingMenu.conf`; T4B uses `4EE7794C9A3F11F0`. That is a second selection mismatch for the rebinding UI, **not the cause that must be fixed to run an already defined Action**. Core Touch/Wheel do not require corresponding key-menu entries. Do not change both identities in the first experiment.

## 6. Dependency/load-order analysis

Current descriptors:

| Project | GUID | Direct dependencies relevant here |
|---|---|---|
| T4B | `B1C2D3E4F5061728` | Arma `58D0FB3206B6F859`, Weapons `6A70E400C54051DC` |
| Weapons | `6A70E400C54051DC` | Arma, `6922BE16974B3AED` (owner log names ARMST PLATFORM UI) |
| Core | `69E4C3542B6CDC19` | Arma, Weapons, plus equipment/items/sounds/other ARMST projects |

T4B has **no direct Core dependency**. Core and T4B share dependencies; neither descriptor establishes T4B-after-Core precedence. The packed UI dependency's loose `addon.gproj` was not accessible at the historical logged path, so its complete transitive closure is UNRESOLVED. Do not infer it is empty, nor add Core as a dependency without a separate decision.

The installed default GUID already explains why the unique T4B resource can be registered but unused. "Core wins because loaded last" is not proven, and Core need not be loaded for this mismatch to exist. Reordering dependencies alone is not a remedy for wrong override identity. Same-GUID conflicts on overlapping fields would be a later compatibility problem, not evidence for arbitrary same-path auto-merge.

## 7. RegisterActionManager investigation

Installed docs root: `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs\EnfusionScriptAPI\html`.

Verified declarations in `interfaceInputManager.html`:

```c
proto external bool RegisterActionManager(ActionManager pManager);
proto external bool UnregisterActionManager(ActionManager pManager);
proto external ref InputBinding CreateUserBinding();
```

This is **PROVEN_SUPPORTED for registration of an existing manager**, not proof of loading a `.conf` by string. No resource/config argument is accepted. The inspected `interfaceActionManager.html` public member list provides activation, state access, enumeration and listeners, but no documented constructor accepting a config, `Load`, `AddAction`, `AddContext` or factory. No end-to-end Reforger usage was found in inspected ARMST scripts or ACE source search; global search also returned unrelated Go/Java and DayZ results, which are not Reforger evidence.

Therefore an independent config-backed runtime manager is **POSSIBLE_NOT_PROVEN**, not an implementation recipe. Unknown: construction from a Resource/BaseContainer, native instance ownership, reference lifetime, registration order, integration with the default manager's contexts, and cleanup guarantees. A hypothetical owner-local lifecycle must pair successful registration/unregistration and listener teardown, but inventing `new ActionManager(path)` or assuming BaseContainerTools can instantiate this native class is prohibited.

Do not confuse `ActionsManagerComponent` (world UserActions) with `ActionManager` (input).

## 8. Existing vanilla action reuse

The installed SDK exposes:

```c
proto external void AddActionListener(string actionName, EActionTrigger trigger, ActionListenerCallback callback);
void ActionListenerCallback(float value = 0.0, EActionTrigger reason = 0, string actionName = string.Empty);
proto external void SetActionValue(string actionName, float value);
proto external void ResetAction(string actionName);
```

The callback returns **void**, not a consumed/handled boolean. Registering another listener is not a veto of native reload. ResetAction resets state; SetActionValue changes a value. Neither declaration promises pre-native ordering, cancellation of queued reload commands, or suppression of other listeners. Core's PDA value writes demonstrate use, not a safe reload interception contract.

Existing vanilla reload/inspection actions could provide remappable input without a new Action, but a listener alone gives double-route risk. Numeric `SetReloadWeapon(int)` is a gameplay request, not physical-input consumption.

`HandleWeaponReloading(CharacterInputContext, float, int)` and `HandleWeaponReloadingDefault(...)` exist in installed character-handler docs. Nevertheless [owner A/B 6009350264](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6009350264) recovered rack by removing the global override and explicitly rejected that architecture. Current `ARMST_T4B_NormalRHandlerProbe.c` contains only inert constants. **Do not restore the global handler.** No safe pre-mutation weapon-local veto was proven by this audit.

## 9. UserAction/Gadget alternative

Core detector is a real example of avoiding a custom input resource, but is not an equivalent weapon-reload dispatcher:

- `Prefabs/Items/devices/armst_itm_atmos.et:43`: animation attachment `BindingName "Gadget"`.
- The same prefab has `UserActionContext "Toggles"` at line 97.
- `Scripts/Game/Devices/ARMST_DETECTOR_COMPONENTS.c:78`: `ARMST_DETECTOR_COMPONENTS : SCR_GadgetComponent` overrides ActivateAction and calls detector behavior.
- `ARMST_USER_DETECTOR_TOGGLE : ScriptedUserAction` begins at 492; visibility uses character inspection at 546.

These are gadget activation and contextual interaction entry points. The source does not establish a single sequential chain where an Input Action automatically becomes a UserAction of the same name. A weapon's interaction action can call a shared reload service, but cannot by itself seize physical R from native reload. Requiring inspection/selection is a different UX and violates the requested normal-R-only outcome. Replacing weapon ownership with a gadget risks fire/aim/pump behavior. **NOT_APPLICABLE as the final R router**; useful only as a backend invocation pattern, not a new button proposal.

## 10. Other discovered architectures

### A. Proper default-resource override (recommended registration mechanism)

The independent addon retains the selected vanilla input GUID through a **Workbench-created Override**, contributing only its action/context delta. This is not a unique-GUID duplicate. No production Core file needs editing. Local metadata and public ACE examples support this mechanism. Current policy forbids changing metas in this audit: any correction needs new owner GO, backups and owner-generated override metadata; no hand-made GUID edits are performed here.

### B. Separate context resource, referenced by the selected config

Core already embeds `ActionContext PdaContext : "{57717AB802C72243}Configs/System/PDA/PdaContext.conf"` and BookContext similarly. A modular MP-133 context resource can be referenced by a small legitimate override of the selected input config. **PROVEN_SUPPORTED as config composition**, not autonomous discovery of an arbitrary file. Its object type must match ActionContext; an ActionManager root cannot be substituted casually.

### C. Explicit project Default replacement/inheritance

`InputManagerSettings.Default` is an actual selection point. A project could select a separately identified ActionManager config inheriting the vanilla resource. Static config selection is proven; a correct T4B project override and interaction with other addons are not tested. This competes over a global setting and can omit base bindings if misconstructed. Inferior to an additive default-resource override here.

### D. InputBinding custom-config list / controller presets

Verified in installed `interfaceInputBinding.html`:

```c
proto external void GetCustomConfigs(out notnull array<ResourceName> customConfigs);
proto external void SetCustomConfigs(notnull array<ResourceName> customConfigs);
proto external BaseContainer FindContext(string contextName);
proto external BaseContainer FindAction(string actionName);
proto external void GetContexts(out array<string> contextNames);
```

Installed `ArmaReforgerScriptAPIPublic/html/interfaceSCR__SettingsManagerKeybindModule.html:143–148` documents SelectControllerPresets/SelectJoystickPreset/SelectJoystickPresetPath feeding this list. Thus **multiple additional binding configs are real**, not hypothetical. However documented purpose is binding/preset configuration, not a guarantee of appending previously unknown gameplay actions/contexts to a live manager. Replacing that list may overwrite user controller presets; Save persists settings. Reload timing, preservation and action creation need separate research/runtime authorization. Ranked below the normal override, not selected as next experiment.

The old report's blanket "context enumeration unavailable" is too broad: these query APIs exist on **InputBinding**, although not on ActionManager itself. Their view of binding containers is not identical to proving active runtime dispatch.

### E. Context-local vanilla action remapping

Core's context-local Escape and ACE Finger's context-local action prove contextual definitions are possible. A weapon-specific context could redefine the effective vanilla reload action's input and expose a custom action. This could preserve other contexts better than a global exclusive context, but exact lower-priority fallback, empty-binding behavior and multi-filter release/hold routing are not proven. Candidate design only; no invented numeric Flags or config removal syntax.

### F. Weapon-local listener / context-free action / raw keyboard

A component can scope listener ownership to the equipped weapon; it still subscribes to the same input system and has no documented native consume return. It does not solve registration or double reload. `ActivateAction(string,int)` exists, so direct action activation is worth distinguishing from context activation; it does not create a missing action or suppress another one. BI describes action grouping in contexts. A globally active action with script-only gating leaves vanilla R alive.

Low-level keyboard handlers are exposed by InputManager, but no source-proven keyboard-consumption route was found here. Polling physical R would sacrifice remapping/gamepad support and still require a native-reload veto. Not recommended.

### G. Controlled Core integration / existing Core context

Adding the action directly to Core's selected config could load it, but is unnecessary while the independent GUID-preserving override is supported. If later chosen, isolate an additive block and exact backup/rollback, never replace Core's config wholesale. Extending PDA contexts couples reload to PDA state; adding to CharacterGeneralContext registers/enables an action but does not isolate its native R competitor. These are not fixes for input ownership.

### H. Nonconflicting key proof

An F-key can separate physical-key conflicts from dispatch **after registration**, but changing R cannot resolve actionPresent=false. It is not selected and is not implemented. No extra diagnostic key is introduced.

## 11. External examples

| Class | Source | What it establishes / limitation |
|---|---|---|
| OFFICIAL_SOURCE | [Data Modding Basics](https://community.bohemia.net/wiki/Arma_Reforger%3AData_Modding_Basics), [Metadata](https://community.bohemia.net/wiki/Arma_Reforger%3AWorkbench_Metadata?useskin=darkvector) | GUID-preserving config overrides versus distinct resources; not full native merge implementation |
| OFFICIAL_SOURCE | [Input Manager](https://community.bohemia.net/wiki/Arma_Reforger%3AInput_Manager?useskin=darkvector) | Context priority/overlay/exclusive concepts; not a numeric `0x6` mapping or per-key consumption guarantee |
| OFFICIAL_SOURCE | [InputManager API](https://community.bistudio.com/wikidata/external-data/arma-reforger/EnfusionScriptAPIPublic/interfaceInputManager.html), [ActionManager](https://community.bistudio.com/wikidata/external-data/arma-reforger/EnfusionScriptAPIPublic/interfaceActionManager.html), [InputBinding](https://community.bistudio.com/wikidata/external-data/arma-reforger/EnfusionScriptAPIPublic/interfaceInputBinding.html) | Signatures cross-checked against installed docs; existence is not an end-to-end lifecycle proof |
| OFFICIAL_SOURCE | [Settings keybind module](https://community.bistudio.com/wikidata/external-data/arma-reforger/ArmaReforgerScriptAPIPublic/interfaceSCR__SettingsManagerKeybindModule.html) | Custom preset configs and separate key-menu identity |
| PUBLIC_WORKING_MOD | ACE-Anvil immutable revision `acf4cb4b53ab347986be439b18cf90f465424b84`: [Core config](https://github.com/acemod/ACE-Anvil/blob/acf4cb4b53ab347986be439b18cf90f465424b84/addons/core/Configs/System/chimeraInputCommon.conf), [Core meta](https://github.com/acemod/ACE-Anvil/blob/acf4cb4b53ab347986be439b18cf90f465424b84/addons/core/Configs/System/chimeraInputCommon.conf.meta), [Finger config](https://github.com/acemod/ACE-Anvil/blob/acf4cb4b53ab347986be439b18cf90f465424b84/addons/finger/Configs/System/chimeraInputCommon.conf), [Finger meta](https://github.com/acemod/ACE-Anvil/blob/acf4cb4b53ab347986be439b18cf90f465424b84/addons/finger/Configs/System/chimeraInputCommon.conf.meta), [Finger project](https://github.com/acemod/ACE-Anvil/blob/acf4cb4b53ab347986be439b18cf90f465424b84/addons/finger/addon.gproj) | Core and Finger both retain input GUID 795184CF9AD764DB. Core adds ACE_StopCarrying; Finger adds map action; not two arbitrary unique-GUID files |
| PUBLIC_WORKING_MOD | [ACE Finger listener](https://github.com/acemod/ACE-Anvil/blob/acf4cb4b53ab347986be439b18cf90f465424b84/addons/finger/scripts/Game/ACE_Finger/Map/ComponentsUI/ACE_Finger_MapUIPointerContainer.c) | Search excerpt shows DOWN/UP listeners for config-defined action. No local runtime reproduction claimed |
| COMMUNITY_CLAIM | [Aegis maintainer changelog](https://reforger.armaplatform.com/workshop/6A4B2AAD8FD06D7D-AegisAdminTools/changelog) | Warns about competing input overrides; not accepted as proof that all .conf layers use last-file replacement |
| COMMUNITY_CLAIM | [EveronLife discussion](https://github.com/EveronLife/EveronLife/discussions/143), [SHS author's input guide](https://shadowhavenstudios.org/Lucalis/SHS-NV-and-Lights-Wiki/wiki/SHS-Night-Vision-%26-Lights) | Suggest config actions/listeners; not proof of registration identity or selective R interception |

Search also covered RegisterActionManager construction/usage, separate input configs, SetCustomConfigs, project settings, gadgets and user actions. No supported native C++ loader implementation or tested separate-manager factory emerged. Negative search results are bounded, not proof no such mechanism exists. Doxygen footer `1.13.2` is a **documentation-generator version**, not an Enfusion game version; installed game version is established from the owner log above.

## 12. Architecture comparison matrix

Legend: Supported = source-proven building block, not an MP-133 runtime acceptance result. Conditional = extra proof required.

| Architecture | Source proof | Works from separate addon? | Can isolate MP-133? | Can suppress vanilla R? | Core modification required? | Risk | Recommendation |
|---|---|---|---|---|---|---|---|
| Same-path unique-GUID config (current) | Identity mismatch proven | Not through current Default | Intended only | No evidence | No | Silent non-loading | Reject |
| GUID-preserving default override + custom context | BI, installed Default, Core, ACE | Supported | Script/context gate | Conditional; not per-key proof | No | Context overblocking | Preferred registration foundation |
| Separate unreferenced MP133Input.conf | No loader demonstrated | Not automatically | Possible | Unproven | No | Unused resource | Reject standalone |
| Separate referenced ActionContext resource | Core Pda/Book inheritance | Supported with small selected-config override | Yes by gate | Conditional | No | Lower if additive | Good modular packaging |
| Runtime RegisterActionManager | API only; missing construction path | Possible, unproven | Possible | Unproven across managers | No | Ownership/order | Research fallback |
| Reuse vanilla reload listener | SDK listener | Yes for observation | Yes for own callback | No documented consume | No | Double reload | Not standalone solution |
| UserAction/Gadget route | Core detector | Supported for gadget/interaction | Item-local | Not native weapon R | No | UX/weapon lifecycle | Not applicable final router |
| Weapon-local component listener | InputManager API | Yes | Listener ownership yes | No independent veto | No | Duplicate dispatch | Packaging only |
| Direct Core input integration | Matching selected identity | Requires Core | Custom gate | Still conditional | Yes | Production coupling | Unnecessary now |
| Existing Core context extension | Core ActionRefs | Via legitimate override | PDA/general gates insufficient | Not by adding action alone | Not necessarily | Context conflicts | Avoid PDA coupling |
| InputBinding.SetCustomConfigs | SDK + preset module | Config list supported; new Action creation unproven | Additional gate | Unproven | No | User settings/preset rebuild | Secondary candidate |
| Project Default -> inherited custom manager config | Installed selection field | Possible | Additional gate | Conditional | No | Global setting collision | Lower rank than override |
| Context-local remapping of existing reload Action | Core/ACE contextual Actions | Supported syntax, behavior unproven | Yes by context | Candidate, must prove | No | Hold/release/fallback | Later input-ownership design |
| Context-free action/direct ActivateAction | SDK method | Existing action only | Script gate | No | No | Double route | Insufficient |
| Global HandleWeaponReloading override | SDK + owner negative A/B | Technically exposed | Failed tested approach | Unsafe in this lab | No | Proven rack regression | Rejected; do not restore |

## 13. Ranked recommendations

### A. MOST LIKELY ROOT CAUSE

**An independently registered config was supplied where the game selects a GUID-preserving override.** HIGH confidence: project Default, both live metas, no T4B loader/reference, matching ACE pattern and owner absence all agree. Static identity mismatch is proven; exhaustive native runtime causality is not claimed. This is stronger than "Core may shadow T4B by load order" and survives the counterexample of Core being unloaded.

Falsifier: evidence that the effective session Default actually references T4B's GUID, that another verified loader incorporates it, or a controlled correct-identity experiment still lacks the action despite confirmed override participation. In that case investigate config parsing/effective layers rather than declaring success.

### B. BEST LONG-TERM ARCHITECTURE

**Independent addon, normal default-resource override, weapon-scoped input ownership, one reload service.** HIGH confidence in the registration mechanism; MEDIUM in complete R routing until selective suppression is measured.

```text
selected input resource + addon delta
  -> eligible local equipped MP-133 context
  -> exactly one request dispatcher
  -> Astra five-phase coordinator
  -> insertion event/token -> authoritative one-round transfer -> loop/end
other weapons -> existing vanilla input route
```

No global reload-handler override. No PDA-context dependency. No user-profile edits. Keep Core untouched. Source-backed registration is the first gate, not a finished reload architecture.

Important acceptance risks: a high-priority context containing only one action can suppress movement/look/fire, not just R; overlay may permit vanilla reload too. Do not ship Priority 20000/Flags 0x6 as a proven selective mask. The final input map must preserve other controls, menus, key remapping, hold-R inspection and native rack without reopening whole-mag commands. A dispatcher must distinguish rack from shell loading using verified state/API; this audit does not invent that discriminator. Multiplayer authority/exactly-once transfers remain separate from client input.

Falsifier: no supported context arrangement can isolate native reload while retaining required controls and pump behavior. Then this design remains blocked at selective ownership; revisit native producer APIs, not global hook restoration or a second button.

### C. FASTEST SAFE EXPERIMENT TO PROVE IT

**One-variable input-identity correction, then registry-only owner observation without pressing R.** HIGH confidence in diagnostic value; it separates incorporation from dispatch and avoids known mag-swap paths. This is the sole selected next experiment. No experiment was prepared or run in this audit.

## 14. Minimal next experiment

```text
NEXT_EXPERIMENT:
  OWNER-GO-GATED GUID-preserving input override; registry-only observation.
GOAL:
  Determine whether correcting participation in Default produces actionPresent=true.
FILES_TO_CHANGE:
  Only T4B Configs/System/chimeraInputCommon.conf.meta (live and labs mirror),
  using owner-generated metadata from Override of the selected vanilla resource.
  Expected input resource identity: 795184CF9AD764DB, not a fabricated new GUID.
  Keep .conf bytes, script, priority/flags, dependencies and key-menu files unchanged.
  Owner ResourceDB refresh is incidental Workbench state, not an agent edit.
EXPECTED_RESULT_A:
  actionPresent=true on fresh T4B entry. Identity/incorporation hypothesis supported.
  active=false would be a separate context problem; active=true is not R safety proof.
EXPECTED_RESULT_B:
  actionPresent=false persists after effective override identity is confirmed.
  STOP; inspect parser errors and actual selected/layered resource. Do not tweak R.
ROLLBACK:
  Before any future change, retain exact current .conf/.meta backups and hashes.
  Restore only the authorized test delta from those backups; owner refreshes ResourceDB.
  No git reset/clean, no deleting owner assets, no Core or key-menu edits.
RUNTIME_OWNER_ACTION:
  Only after NEW explicit GO: owner creates/verifies the legitimate override through
  Workbench (Navigate to Original/Override should show the base resource relation).
  Do not regenerate the independent file's metadata and expect another unique GUID to help.
  If the existing file blocks the UI operation, STOP and agree a reversible procedure;
  do not delete it blindly or hand-edit identities during this audit.
  Review exact diff; fresh owner session and equip canonical T4B only for existing logs.
  Capture weapon_gate_pass and context_activate_result. DO NOT PRESS R, fire or invoke
  transfer actions. No stock magazine-replacement test. Stop on compile/parser errors.
```

This changes override identity intentionally, so it requires an explicit exception to the usual meta-preservation rule under new owner GO. It is **not** authorized by this report-only task. F10, Core edits and SetCustomConfigs are not parallel experiments.

## 15. What is still unknown

- Effective native C++ loading implementation and exact runtime override list for the failing session; no loader trace was present in its console excerpt.
- Complete transitive dependencies of packed ARMST UI and conflict resolution for overlapping legitimate override fields.
- Exact numeric Flags interpretation, selective lower-context suppression, action-filter timing and R hold/release behavior in 1.8.0.13.
- Whether SetCustomConfigs can safely add unknown gameplay actions/contexts, rather than only binding presets, without persistent user-setting side effects.
- A source-proven standalone ActionManager construction/config-loading path and cross-manager input arbitration.
- Native rack-preserving custom dispatcher, full Astra integration and multiplayer transaction correctness. None is declared completed by this audit.

### Verification appendix

Hashes were computed from sorted full-path + SHA256 rows for `.c/.conf/.et/.meta/.layer/.gproj/.agr/.agf/.asi/.ast`. Counts cover the consumed gameplay categories plus extra protected resources, not all binary assets. Production paths were read only. Weapons resolver returned the validated ARMST Weapons addon. No scanner against live ARMST was launched.

| Guarded root (under Workbench addons) | Files | Before aggregate SHA256 |
|---|---:|---|
| ARMSTMP133T4B_InstalledMagProbe | 79 | AB54E311B0274B6B8122B7F5EF56F55F98B0D4F9AE2FC5370356B00E4A6D873E |
| ARMST-PLATFORM---Core | 5521 | 2EDF4D1DCA02F0C662AE1CA567D8B9655C374BC817883B7625A7AF02D8860B4B |
| ARMST-PLATFORM---Weapons | 1210 | 7CB4CBCBB8A799C6C811F71CF746110CC2C80A1F9A1D244043FD4C7B40349810 |
| Weapon_ARMA_X/labs | 44 | 135DF24EAAB69DE14C88D0DB417FBA16E42F12C8C8BCD0A3F1C9F6955660437E |
| Weapon_ARMA_X/artifacts/astra-rebuild/stageCustomRInput | 3 | E6481B8AB4E62B987F0D0CDFA5582C5D244A2A558C96BF1C2528068FE847F4C6 |

Current live/labs/staged matching SHA256:

- input .conf: `57778A1D2ED7EDCA8A321CCDF2D5A76A8092E8C0319D0D4ED9DDE07194F60993`;
- key-menu .conf: `368B51F7862B245C730E40CA1C226B369F845C7E0DC9B604E822F2078BCDC01D`;
- CustomRInputProbe.c: `A87E3722DD69AB1164ECB363D688CA4FB81331D7A8FF5710BD212B578D96B1AB`.

Untracked Core audit guard: `924DF1E42AD5C4D1ADA41BA57A1553DB9EE7962BC6488E301B042621F0182B55`.

Post-audit hashes and counts exactly match all five rows above (6,857 files).
`GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0`. The untracked Core report is unchanged.

Repository checks (Python only, no Enfusion compilation):

- `python -B agent/scripts/addon_path.py`: PASS, validated Weapons path.
- `python -B -m unittest discover -s agent/tests -p "test_*.py"`: **96 tests, 2 failures, 10 errors** after retry outside sandbox. Eight errors require missing `MP133_AstraShellGraph_test/MP133_Astra.agf`; two require missing `ARMST_T4B_AstraV2_Bridge_TestWeapon.et`. Two stale integration assertions reject the current observer's OnCharacterCommand and expect five rows where the old path yields zero. These inputs/tests were not changed by the report. Initial sandbox attempt additionally failed on temporary-directory permissions; it is not the final test result.
- `python -B agent/scripts/check_repository_integrity.py --check`: **FAIL, 10 existing broken links**: one in `ENFUSION_WEAPON_SOURCE_ATLAS_2026-10-04.md`, eight in `MP133_V3_T4B_INSTALLED_MAG_PROBE.md`, one in CURRENT_AI_SYNC. No broken link attributed to this new report. No automatic repair made.
- These failures prevent claiming a green repository, but do not invalidate the independently checked project/config identity evidence. Report-only publication does not certify gameplay or resolve historical test drift.

```text
WORKBENCH_LAUNCHED = NO
REFORGER_LAUNCHED = NO
GAME_MODE_LAUNCHED = NO
RUNTIME_TEST = NO
COMPILE_TEST = NOT_RUN_BY_AGENT
LIVE_CHANGED = NO
LABS_GAMEPLAY_CHANGED = NO
CONFIG_CHANGED = NO
META_CHANGED = NO
GUID_CHANGED = NO
CORE_CHANGED = NO
```

Final research status: `T4B_CUSTOM_R_ASTRA_INPUT_ARCHITECTURE_RESEARCH_COMPLETE`.
STOP for owner review and separate experiment GO; no runtime or implementation authorized here.
