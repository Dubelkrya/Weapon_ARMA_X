# MP133 — vanilla character-first animation route

2026-10-08. **Final classification: PARTIALLY_SUPPORTED**.

The character-first P/W architecture is source-supported. A safe, animation-only entry for the current custom shell branch is NOT established. No implementation/test authorization follows from this classification.

Authority: attachment 944c7a8a-3e10-4409-9c94-b998e76f74d3, SOURCE-ONLY. Verified HEAD `8d3e896b96d3b14a269d678e76d946eb5d40c708`, branch `t4b/installed-mag-probe`. Read AGENTS/current sync/continuation and previous binding/injection/transport evidence. Latest fetched Issue #34 owner result remains [6062981503](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-6062981503); current direct owner UI correction supersedes Fetch instructions. Owner audit and preceding local MP133_MINIMAL_GRAPH_DIAGNOSTIC_DESIGN.md preserved. No plan edit, commit, push, candidate, launch, compile, runtime or command emission. Rack FROZEN; G3B2 HOLD.

## 1. Exact supported path and opaque native boundaries

```text
CharacterController.GetInputContext()
  -> CharacterInputContext.SetReloadWeapon(type)
  -> [native character weapon/reload processing: body not public]
  -> character animation domain / CMD_Weapon_Reload
       +-> root Weapon attachment -> injected P weapon graph + player ASI
       +-> synced item subscription -> W weapon graph + weapon ASI
```

This is NOT a proven serial P -> W command forwarder. P attachment evaluation and W subscription are two mechanisms fed from character animation logic. Their order, native remapping and exact delivery frame are not exposed by the inspected declarations.

- Installed CharacterControllerComponent member list exposes GetInputContext and GetAnimationComponent. Current T4B CustomRInputProbe.c lines 230–236 uses the input context and SetReloadWeapon(1), consistent with owner-proven rack. No replacement is proposed.
- Pinned [CharacterInputContext.c](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/generated/Character/CharacterInputContext.c) declares SetReloadWeapon(int), WeaponIsStartReloading/GetWeaponReloadType. It contains no body exposing conversion into animation commands or physical reload work.
- [BaseItemAnimationComponent.c](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/generated/Components/BaseItemAnimationComponent.c) documents SyncWithCharacter subscription to character animation variables/commands; OnCharacterCommand is a notification from that domain, not proof of P evaluation.
- Official [Nodes](https://community.bistudio.com/wiki/Arma_Reforger:Animation_Editor:_Nodes) documents attachment input translation into an attached graph. Local Core Anims/Player/Locomotion.agf 1685–1687 contains AnimSrcNodeAttachment WeaponAttachment, Binding Weapon. This supports intended P wiring, not a discovered script getter for its instance.
- Core Anims/workspaces/player/player_main.agr declares CMD_Weapon_Reload at 488. However its local GraphFilesResourceNames list is empty at 836: this materialized file alone does NOT reconstruct the complete active root resource chain. The owner's runtime root namespace identification is stronger evidence of active ownership than this incomplete local export.

The native writer between SetReloadWeapon and animation evaluation, exact subscription mapping implementation, and full mounted root graph remain source gaps. Do not fill them with assumed C++ call order or numeric command IDs.

## 2. Bohemia sample: configuration and consumers

Sample source pinned to `83f12390d3dd61ed834d379f621520ed9f1b891d` (not assumed identical to installed SDK):

- [SampleWeapon_01_base.et](https://github.com/BohemiaInteractive/Arma-Reforger-Samples/blob/83f12390d3dd61ed834d379f621520ed9f1b891d/SampleMod_NewWeapon/Prefabs/Weapons/Rifles/SampleWeapon_01_base.et#L244): W graph/weapon ASI at 244–245, injection same graph/player ASI at 247–249, BindingName Weapon at 250, BindWithInjection 1 at 252. AlwaysActive 1 is explicit at 246; not a fan-out proof.
- [sampleweapon_01.agr](https://github.com/BohemiaInteractive/Arma-Reforger-Samples/blob/83f12390d3dd61ed834d379f621520ed9f1b891d/SampleMod_NewWeapon/Assets/Weapons/Rifles/Workspaces/sampleweapon_01.agr#L59) declares CMD_Weapon_Reload; default root MasterControl at 113.
- [sampleweapon_01.agf](https://github.com/BohemiaInteractive/Arma-Reforger-Samples/blob/83f12390d3dd61ed834d379f621520ed9f1b891d/SampleMod_NewWeapon/Assets/Weapons/Rifles/Workspaces/sampleweapon_01.agf#L248): ReloadActionBolt -> RackBoltAnim, start int=1/float=0 at 254. Int 2–6 chooses native magazine/rack branches at 223–261; broad entry excludes 7–9 and -2 at 93/135.
- Both [player ASI](https://github.com/BohemiaInteractive/Arma-Reforger-Samples/blob/83f12390d3dd61ed834d379f621520ed9f1b891d/SampleMod_NewWeapon/Assets/Weapons/Rifles/Workspaces/sampleweapon_01_player.asi) and [weapon ASI](https://github.com/BohemiaInteractive/Arma-Reforger-Samples/blob/83f12390d3dd61ed834d379f621520ed9f1b891d/SampleMod_NewWeapon/Assets/Weapons/Rifles/Workspaces/sampleweapon_01_weapon.asi) map corresponding Reload_InsertMag/Reload_RemoveMag/ReloadActionBolt slots at 16–31 to separate resources. Shared slots select different P/W clips; they do not share command storage.

These files demonstrate graph configuration and native consumers, not an arbitrary custom command magically registered in the character root.

## 3. Current Astra comparison

Live root: `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMSTMP133T4B_InstalledMagProbe`.

| Feature | Sample | Current Astra |
|---|---|---|
| P/W configuration | Shared AGR; separate ASIs; Weapon injection; BindWithInjection 1 | Same architectural arrangement in current AstraRebuild prefab |
| Native root command | CMD_Weapon_Reload | Preserved; owner rack works via SetReloadWeapon(1) |
| Shell entry | Native magazine-state conditions | AGF 221: ASTRA_ShellRequest/Eligible/Stop plus state gates; W-local writing did not activate P |
| Shell clips | Native reload slot resources | P_Astra_* and W_Astra_* existing clips mapped separately; rack slots retained, native insert/remove mappings absent from current ASIs |
| Custom transport | Sample does not demonstrate root registration of arbitrary injection-only command | CMD_ASTRA_TransportProbe exists only in item AGR; no current AGF consumer; root BindCommand rejected against player_main |
| Extra variable subscription | Character-to-item mechanism | AnimVariablesToBind explicitly lists four shell variables; this is not a W-to-P setter or proof root owns those variables |

Removing native mag clip mappings does not prove SetReloadWeapon requests have no native ammo/chamber effects. Owner rack explicitly changed tube/chamber state. Do not reuse reload type 1 to start shell animations, type 7 as assumed shotgun insertion, type 10 as animation-only, or arbitrary reserved values.

## 4. Ranked options and missing capability

1. **An existing non-gameplay character-root command, using named BindCommand/CallCommand, then native attachment/subscription fan-out.** Best structural fit, but no safe usable command established. NEW local lead: CMD_Weapon_Reload_Test at Core player_main.agr 538 (also other Core root copies). Search of consumed Core/Weapons/T4B `.c/.agr/.agf/.et` found declarations only; public pinned Script-Diff search returned no caller. It is absent from current Astra AGR. Actual mounted root presence, native handling and mapping to P/W remain unknown. A Test suffix is not a safety guarantee.
2. **Direct character animation CallCommand on an existing root name.** [BaseAnimPhysComponent.c](https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/generated/Base/BaseAnimPhysComponent.c) exposes named binding/calling and recommends ScriptedCommand/PreAnimUpdate for timing. This avoids explicitly setting reload input, but does NOT prove native gameplay side effects absent. CMD_Weapon_Reload payload tricks remain unsafe; CMD_ASTRA_TransportProbe root lookup is already rejected and must not be repeated.
3. **ScriptedCommand timing/character variables.** Supported root-domain scripting, not an exposed injected-P handle. Does not solve missing custom root namespace or root variable declarations; replacing current character command risks locomotion/equip. Not the minimal next experiment.
4. **SetReloadWeapon / native reload variants.** Known working transport + physical behavior, therefore unsuitable as an animation-only shell entry under these invariants. Existing rack stays frozen, not generalized.

Exact missing capability: a source-supported character-owned, non-gameplay signal with meaningful binding in the ACTUAL root namespace, mapped to the existing injected P and subscribed W, with proven animation-only dispatch/consumer semantics. Alternatively a documented direct P-instance access API would solve addressing, but none is established for current components. Graph topology and SyncWithCharacter alone do not provide either contract. Synchronized/network semantics remain unproven.

## 5. One recommended minimal next experiment

**CHARACTER_FIRST_EXISTING_ROOT_NAME_REGISTRATION_GATE — bind/read-only, NO EMISSION**, only after separate staging/install/owner gates. This tests a NEW existing-root declaration lead, not the rejected injection-only custom lookup.

At current actor/equipped Astra context, obtain character animation component through the source-backed controller getter; bind CMD_Weapon_Reload_Test by name, existing known root command as positive registration control and an absent name as negative control. No SetReloadWeapon, CallCommand, CallAttCommand, ItemUse, graph writes, ammo/chamber writes or SyncWithCharacter override. Record root namespace/build/owner identity and named-binding validity. Do not treat the local Core export as proof it is mounted.

Discrimination: existing-root lead valid + positive valid + negative invalid -> namespace prerequisite supported; lead invalid -> local declaration not exposed in that runtime (stop); invalid/equal controls -> inconclusive. Current W/P graphs have no Reload_Test declaration/consumer, so P/W receipt and actual animation evaluation are explicitly NOT_TESTED. This registration result cannot be PASS for delivery or shell activation.

Why not recommend a pulse immediately: native nonmutation and independent observation are unresolved. After registration and source safety gates, a separately designed future one-character-pulse test would require same-name diagnostic declarations/consumers in allowed item graph only, independently attributed P and W consumer evidence, P-health coverage, no native input request and zero ammo/chamber/tube change. Producer call, OnCharacterCommand notification, graph receipt and evaluated consumer/clip must be logged as separate evidence. W-only is not success; P missing with invalid health is INCONCLUSIVE. Stops: any native reload/rack command, tube identity/count/chamber change, actor/equip mismatch, missing consumer, uncontrolled repeated pulse or ambiguous origin. No such candidate is ready or authorized now.

## 6. Read-only proof and final state

Protected PRE/POST inventories identical, sorted FullName and UTF-8 absolutePath|fileSHA256 rows joined by LF (no trailing LF); extensions `.et,.conf,.meta,.c,.layer,.agr,.agf,.asi,.ast,.gproj,.anm,.txa`:

| Root | Files | PRE = POST SHA-256 |
|---|---:|---|
| ARMSTMP133T4B_InstalledMagProbe | 105 | D540BE18C0EA0A4754F34D27C260F1BAF9971DC9C1B76674D095C26BC3B48B76 |
| ARMST-PLATFORM---Core | 5521 | 2EDF4D1DCA02F0C662AE1CA567D8B9655C374BC817883B7625A7AF02D8860B4B |
| ARMST-PLATFORM---Weapons | 1584 | A7C611FE0417F5A5E1DA6E4209F01E3CF846295E9ADA57999713FF1B4CC2AECF |
| Armst_Work | 163 | 62AD288141B18B222E058011B29672E23996D7B651C8C4C79E7535BD24123E29 |

Resolver PASS; no unrelated tests/dependency fixes; no green validation/runtime claim. HEAD unchanged. This report alone saved locally, no git add/commit/push. PARTIALLY_SUPPORTED refers to the architecture, NOT a safe custom animation-only entry. STOP for owner review.
