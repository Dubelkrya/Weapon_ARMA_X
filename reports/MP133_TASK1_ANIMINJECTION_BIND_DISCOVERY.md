# MP-133 Task #1 — AnimInjection binding discovery (Phase 1H)

Status: **T4B_ANIMINJECTION_BIND_DISCOVERY_COMPLETE**
Date: 2026-10-07
Task: Issue #34 comment `6044481757` (Phase 1H priority correction).
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `3e71d6dd8f0b2512a2f442f6f10e9c3180691c12`.
Mode: **SOURCE / STATIC ONLY.** No prefab/graph/script/input/config/meta/GUID/G3B2 change; nothing staged/installed; no runtime.

Owner-provided effective `Anim Injection` (Workbench) for the canonical T4B weapon:
```
Binding Name = Weapon ; Bind With Injection = ON
Auto Command Bind = ON ; Auto Variables Bind = OFF
Anim Variables To Bind = (1) [ WeaponInspectionState ]
```
This is treated as **OWNER_WORKBENCH_EVIDENCE** (effective/derived), not repo-serialized text.

---

## A. Field inventory (LOCAL_SOURCE, vanilla catalog)

`AnimationAttachmentInfo` / `WeaponAnimationComponent` expose these fields in the vanilla corpus:

| field | kind | example |
|---|---|---|
| `AnimGraph`, `AnimInstance`, `StartNode`, `BindingName` | injection resource/identity | `Handgun_PM_base.et:104-108` (`BindingName "Weapon"`) |
| `BindWithInjection` | bool on the animation component | `Handgun_PM_base.et:110` `BindWithInjection 1` |
| `AutoCommandBind` | bool | `catalog/core/Mortar_Base.et:400` `AutoCommandBind 1` |
| `AutoVariablesBind` | bool | `catalog/core/Mortar_Base.et:401`; `catalog/grenades/M18/Smoke_M18_Base.et:88` |
| `AnimVariablesToBind { "a" "b" }` / `AnimVariablesToBind + { "a" }` | string array of graph-variable names | `Smoke_M18_Base.et:89-91` `{ "MovementSpeed" "Stance" }`; `Handgun_PM_base.et:111-113` `+ { "State" }`; `MG_PKMN.et:7-9` `+ { "HasOpticsAttached" }`; `UGL_M203_base.et:308-310` `{ "" }` |

Key structural facts (SOURCE):
- `AnimVariablesToBind` is an **explicit list of named graph variables** declared on the injection/animation component.
- It supports the **additive operator `+{ ... }`** in a child prefab (`MG_PKMN.et` adds `HasOpticsAttached` to its inherited base) — i.e., a prefab-only, additive binding change is the intended authoring pattern.
- `AutoVariablesBind`/`AutoCommandBind` gate automatic (non-listed) binding.

## B. Current T4B prefab vs production (LOCAL_SOURCE)

- Lab prefab `labs/.../Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et` (L12-21):
  ```
  ARMST_T4B_AstraV2_WeaponAnimationComponent {60B4EA76EB15F6E0} {
   AnimGraph         ... MP133_Astra2.agr
   AnimInstance      ... MP133_Astra2_weapon.asi
   AnimInjection AnimationAttachmentInfo { ... MP133_Astra2.agr + MP133_Astra2_player.asi + BindingName "Weapon" }
   BindWithInjection 1
  }
  ```
  Only `AnimGraph/AnimInstance/AnimInjection/BindingName/BindWithInjection` are serialized.
- Production `armst_Shotgun_mp_133.et` (L73-80) serializes only `AnimGraph/AnimInstance/AnimInjection{AnimGraph,AnimInstance}` — no `BindingName`, no `BindWithInjection`, no `Auto*`, no `AnimVariablesToBind`.
- Base chain `armst_shotgun_base.et` and `catalog/Rifles/M14/Rifle_M21_base.et` carry no `Auto*`/`AnimVariablesToBind`.
- `WeaponInspectionState` does **not appear in any local `.et`** (bounded search).

⇒ The owner-visible `AutoCommandBind=ON`, `AutoVariablesBind=OFF`, `AnimVariablesToBind=[WeaponInspectionState]` are **engine class defaults for the weapon animation component/injection**, not serialized repo text (packed engine; not extractable). Effective source = engine default; explicit serialized source = none. (UNRESOLVED at text level; OWNER_WORKBENCH_EVIDENCE at effective level.)

## C. Answers to the required questions

1. **Does `AnimVariablesToBind` explicitly bridge named graph variables into the injection?** — **YES at structure level (SOURCE).** It is an explicit named-variable list on the injection; vanilla examples bind character/context variables (`MovementSpeed`, `Stance`, `State`, `HasOpticsAttached`) into injected graphs. The exact direction/owner of the source value (weapon-W instance vs character host) is **not documented locally → UNRESOLVED**.
2. **With Auto Variables Bind OFF, are unlisted variables guaranteed not to propagate?** — **STRONGLY SUPPORTED (INFERENCE from the effective UI + runtime).** Only the explicit list is bound; `ASTRA_*` are not listed; the P graph stayed inert (`W works / P family NO`) — fully consistent.
3. **Would adding `ASTRA_ShellRequest` etc. to `AnimVariablesToBind` let a W-side write reach P?** — **UNPROVEN** (depends on the unresolved direction). This is exactly what the minimal prefab-only bind probe must decide.
4. **Does `AutoCommandBind=ON` bind arbitrary AGR commands or only engine-known?** — **UNPROVEN.** No local doc. `CMD_Weapon_Inspection` (declared in the AGR) may auto-bind; whether an arbitrary custom command would is not established.
5. **Is `WeaponInspectionState` the mechanism by which inspection reaches P?** — **STRONGLY SUPPORTED.** It is the sole explicit entry in the effective bind list, inspection writes it (`CharacterControllerComponent.SetInspect/SetInspectState`), and the injected graph's `WeaponInspectionSTM` reads it. This explains the historical inspection P-route.
6. **Where do the effective values originate?** — **Engine defaults** for the weapon animation component/injection (not serialized in T4B/production/base prefabs). Exact native default table: UNRESOLVED locally.

## D. Decision

```
INJECTION_BIND_PROBE_JUSTIFIED
```
Rationale: explicit variable binding is source-proven as the injection's intended bridging mechanism, and `WeaponInspectionState` (the only listed variable) is exactly the standard state that reaches the injected P graph — verified against the owner's effective UI and the runtime (`W works / P inert`). The one missing fact is the **direction/owner of the bound value** for a *custom* variable, which is not documented; therefore the next step is the smallest **prefab-only binding test**, not another owner-search probe. (`INJECTION_VARIABLE_BIND_SOURCE_PROVEN` would be the label if the direction were also proven; it is not.)

Rejected for now: `INJECTION_COMMAND_BIND_SOURCE_PROVEN` (auto-command binding of arbitrary custom commands unproven), `W_HOST_P_ATTACHMENT_PROBE_JUSTIFIED` (owner-search probe deprioritized by this evidence), `SOURCE_BLOCKED`.

## E. Smallest next probe (design only — NOT staged/installed here)

Prefab-only, additive, in the lab T4B weapon only:
```
ARMST_T4B_AstraV2_WeaponAnimationComponent {60B4EA76EB15F6E0} {
  ...unchanged...
  AnimVariablesToBind + {
   "ASTRA_ShellRequest"
   "ASTRA_ShellEligible"
   "ASTRA_ShellRepeat"
   "ASTRA_ShellStop"
  }
 }
```
- Keep the existing `WeaponInspectionState` binding (use `+{`, do not replace).
- No script/graph/input/meta/GUID/G3B2 change.
- Owner compile + one qualified shell R; observe `[ARMST-T4B-WPROP]` family `sawP` and P markers.
- PASS: P family observed → explicit variable binding bridges W→P (then `INJECTION_VARIABLE_BIND_SOURCE_PROVEN` confirmed at runtime).
- FAIL: still `P family NO` → direction is host→injected and the character host lacks the variable; escalate to a different bridge (dual command / follower).

## F. No-functional-change statement

No functional file was changed. `labs/`, live, AGR/AGF/AST/ASI/TXA/ANM, prefab (including `ARMST_T4B_AstraRebuild_TestWeapon.et`), config/input/keyBindingMenu, `.meta`/GUID, G3B2, production Weapons/Core are byte-identical. Only this report (and an optional plan update) are committed.

STOP — no prefab change, no stage, no install, no runtime.
