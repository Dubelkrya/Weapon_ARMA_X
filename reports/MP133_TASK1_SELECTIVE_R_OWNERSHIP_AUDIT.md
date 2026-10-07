# MP-133 Task #1 — Selective R ownership via ActionContext precedence (audit)

Status: **T4B_SELECTIVE_R_OWNERSHIP_AUDIT_COMPLETE**
Date: 2026-10-07
Task: Issue #34 — comment `6034920100`.
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `0f575ef212382241ce8b893037b763f8a3581532`.
Mode: **SOURCE / STATIC READ-ONLY.** No live/labs change, no staged config created (proof did not pass — see AUDIT C/E).

Evidence classes: **OFFICIAL_SOURCE** (Bohemia docs shipped with the installed SDK), **INSTALLED_VANILLA_SOURCE**, **PUBLIC_WORKING_MOD**, **OWNER_WORKBENCH_EVIDENCE**, **INFERENCE**, **UNRESOLVED**.

---

## 0. Proven state (given; not reinvestigated)

`GUID 795184CF9AD764DB` override registered; owner runtime `actionPresent=true`, `active=true`, `RINPUT=YES`, vanilla `cmd1..6=YES`. Registration/activation/physical custom-R delivery are solved. The only open item is **selective ownership of R**.

Current accepted T4B context (labs, SHA-256 `57778A1D2ED7EDCA8A321CCDF2D5A76A8092E8C0319D0D4ED9DDE07194F60993`):

```
ActionContext ARMST_MP133_ReloadContext {
 Priority 20000
 Flags 0x6 0
 ActionRefs {
  "ARMST_MP133_Reload"
 }
}
```

Owner Workbench UI reading for `Flags 0x6`: **Overlay ON, Cursor Visible ON, Exclusive OFF, Force Cursor OFF, Capture Cursor OFF** (OWNER_WORKBENCH_EVIDENCE).

---

## AUDIT A — exact vanilla reload ownership

**Installed vanilla resource is packed and NOT extractable in this audit.** The game ships `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\addons\data\ArmaReforger.gproj` (text) plus `data.pak`/`data001..010.pak` (binary). A byte search of the paks for `chimeraInputCommon` returned no hit (entries are compressed / indexed), and no extracted copy exists in the repo `catalog/` (glob `**/Configs/System/**` matches only the T4B labs files), in `references/`, in `Arma Reforger Tools\Workbench\addons\core`, or in the user profile. ⇒ The **exact vanilla `CharacterReload` action name and its containing context/Priority/Flags are UNRESOLVED** here.

What IS source-proven:

- **Selected default resource** (INSTALLED_VANILLA_SOURCE, `addons/data/ArmaReforger.gproj`, `InputManagerSettings`): `Default "{795184CF9AD764DB}Configs/System/chimeraInputCommon.conf"`. One `Default`, GUID-qualified.
- **Official vanilla context model** (OFFICIAL_SOURCE, installed `...\Arma Reforger Tools\Workbench\docs\EnfusionScriptAPI\html\Page_Input.html`, §"Action Contexts", lines 184–216):

| Context | Priority | Flags | Role |
|---|---|---|---|
| `CharacterLookContext` | 1 | *(none)* | mouse look |
| `CharacterMovementContext` | 2 | Overlay | W,A,S,D movement |
| `InventoryContext` | 2 | CursorVisible | mouse UI interaction |
| `InGameMenuContext` | 3 | CursorVisible | mouse UI interaction |

The exact name/priority/flags of the context that contains the ordinary reload action are **not stated** in the shipped docs and could not be read from the packed vanilla config → **UNRESOLVED**. The task lead (`CharacterPlacementContext` Priority 45 / `Flags 0xa`) could **not** be independently confirmed from installed source; `CharacterPlacementContext` does not appear anywhere in the installed docs or the repo. (The lead is corroborated only for the public mod, §AUDIT B/C.)

---

## AUDIT B — arbitration semantics

OFFICIAL_SOURCE, `Page_Input.html` lines 187–191 and 213–215, quoted verbatim:

> "During update, InputManager iterates through contexts. **If a context was activated by the game in the current frame and there is no active context with higher priority, it processes its actions.** Otherwise values of actions are zeroed or unchanged (depending on action type)."
> "Context flags: **Overlay** - allows contexts with lower priority to also be updated when this context is active. **CursorVisible** - tells InputManager that the context uses the mouse cursor."

Worked example (lines 213–215):
- Regular gameplay: Movement (2, Overlay) keeps Look (1) updated → walk + look.
- Inventory open: Inventory (2, **no Overlay**) → "**only contexts with priority 2 or higher are updated**".
- In-game menu: InGameMenu (3) → "**character does not react to any input**".

Answers:

| Question | Answer | Class |
|---|---|---|
| Higher vs lower priority | Active context is processed only if **no active context has higher priority**; lower-priority contexts are suppressed | OFFICIAL_SOURCE |
| Equal priority | Both process (suppression is strict `>`, not `>=`) | OFFICIAL_SOURCE |
| Overlay meaning | Lets **lower-priority** contexts still update | OFFICIAL_SOURCE |
| Exclusive meaning | **Not documented** in the shipped engine docs | UNRESOLVED |
| Suppress whole lower context or only colliding inputs | **Whole lower-priority context** ("character does not react to any input") | OFFICIAL_SOURCE |
| Do lower contexts keep unclaimed movement/look/fire | Only if they are **not lower priority** (e.g. Movement at 2 ≥ Inventory at 2). A strictly-higher non-Overlay context suppresses them entirely | OFFICIAL_SOURCE |
| Overlay + Exclusive legitimate | Exclusive is undocumented; combination not resolvable from official source | UNRESOLVED |

**Consequence (INFERENCE, high confidence): the documented arbitration is tier/priority-wide, not per-input.** A context high enough to suppress the vanilla reload context also suppresses every lower-priority context — movement, look and fire included. The current `Flags 0x6` has **Overlay ON**, which is exactly why the lower vanilla reload context still runs (double-fire confirmed by owner runtime). Removing Overlay suppresses the whole lower tier, not just R → **unsafe** (fails AUDIT E).

---

## AUDIT C — exact numeric flag mapping

- `0x2 = Overlay`, `0x4 = CursorVisible` — **PROVEN by two independent lines**:
  - OWNER_WORKBENCH_EVIDENCE: `0x6` lights exactly *Overlay + Cursor Visible* ⇒ the two set bits `0x2,0x4` are those two flags.
  - PUBLIC_WORKING_MOD: `ArmaOverthrow/Overthrow.Arma4` (`Configs/System/chimeraInputCommon.conf`) uses `Flags 2` on `OverthrowGeneralContext` (additive/coexistent = Overlay) and `Flags 4` on all menu contexts (= CursorVisible).
- `0xa = 0x2 | 0x8`. So `0xa` sets **Overlay + an extra bit `0x8`**. PUBLIC_WORKING_MOD uses exactly this on `OverthrowPlaceContext` (Priority 46, `Flags 0xa`), an input-claiming placement context, and `Flags 8` alone on `OverthrowBuildContext`; `0x26`/`0x2e` appear on map contexts (`0x20 | 0x4 | 0x2` and `0x20 | 0x8 | 0x4 | 0x2`). This is **consistent** with a bit layout `0x1 = ?`, `0x2 = Overlay`, `0x4 = CursorVisible`, `0x8 = Exclusive`, `0x10 = ForceCursor`, `0x20 = CaptureCursor`.
- **But the bit values for `Exclusive` / `Force Cursor` / `Capture Cursor` are NOT provable from any available source.** The five checkboxes exist in the Workbench binary (all five strings are present in `ArmaReforgerWorkbenchSteamDiag.exe`), yet the official docs define only `Overlay` and `CursorVisible`. The assignment `0x8 = Exclusive` is a **triangulation**, not a proof — `0x8` could equally be `ForceCursor` (`0x1/0x10/0x20` are unobserved for those flags). Therefore the **meaning of `Flags 0xa` is not safely proven**.

```
SELECTIVE_R_FLAGS_NOT_PROVEN
```

---

## AUDIT D — one-variable candidate

Current: `Priority 20000` / `Flags 0x6 0`. The single-variable candidate would be `Flags 0x6 → 0xa` (keep `Priority 20000`). This is **not authorised for staging** because:

1. `0xa`’s `0x8` bit is not proven to be `Exclusive`, and `Exclusive` semantics are undocumented (AUDIT B/C).
2. Even if `0x8 = Exclusive`, its scope (per-collision vs whole-tier) is unproven.
3. `Priority 20000` is valid-looking (above every documented value) but, under documented semantics, a non-Overlay high priority suppresses the whole lower tier; keeping `Priority 20000` is therefore only safe **if** `0xa` turns out to be collision-scoped. Priority must **not** be changed as part of this experiment.

---

## AUDIT E — collision scope of a `KC_R`-only context

For `ARMST_MP133_ReloadContext` containing only `ARMST_MP133_Reload` (`keyboard:KC_R`):

| Control | Expected under documented semantics |
|---|---|
| R / vanilla reload | suppressed **only if** the T4B context is non-Overlay and higher priority — but that also suppresses movement/look/fire |
| WASD movement | suppressed with a high non-Overlay context (Movement priority 2 < 20000) |
| mouse look | suppressed (Look priority 1) |
| fire | suppressed (weapon/fire context priority below 20000) |
| aim / interact / switch / menus | suppressed or hijacked |

⇒ A high-priority **non-Overlay** candidate suppresses the **whole character/weapon tier**, not just R → **rejected as unsafe** per the task's own criterion. A **high-priority + Overlay** candidate (the current `0x6`) lets the lower tier (incl. vanilla reload) run → double-fire. The documented flag set therefore **cannot** claim only R.

---

## AUDIT F — state-gated ownership (DESIGN ONLY, not implemented)

If a collision-scoped flag is ever proven, the next phase would be:

```
non-T4B weapon: ARMST_MP133_ReloadContext inactive -> vanilla only
T4B MP-133, chamber empty AND Tube3 ammo > 0: do NOT claim R -> native cmd1 rack
otherwise: claim R -> ARMST route, vanilla reload suppressed
unknown/unsafe state -> fail closed toward ARMST / no-op (never native cmd5/cmd3)
```

Context activation/deactivation stays event-driven (`OnWeaponChangeComplete` / `OnWeaponActive` / `OnWeaponInactive`), local-player gated, no per-frame polling. Physical-input ownership vs the ASTRA route remains a separate gate.

---

## STAGING

**None.** AUDIT C returned `SELECTIVE_R_FLAGS_NOT_PROVEN` and AUDIT E shows the only source-backed candidates are unsafe. `artifacts/astra-rebuild/stageSelectiveROwnership/` was **not** created; `Flags 0x6 0`, `Priority 20000`, the action, `ActionRefs`, `.meta`, `keyBindingMenu`, script, ASTRA, G3B2, prefab and Core are untouched.

---

## FINAL CLASSIFICATION

```
SELECTIVE_R_OWNERSHIP_SOURCE_PARTIAL_NO_SAFE_STAGE
```

Rationale: the Overlay mechanism explaining the current double-fire is **proven** (OFFICIAL_SOURCE + owner UI + public mod), which is the "partial" proof. However (a) the exact vanilla reload context/priority is unreadable from packed installed source, and (b) the only candidate for per-input selectivity — the undocumented `0x8` "Exclusive" bit / `Flags 0xa` — is **not source-proven**, and the documented arbitration is priority-tier-wide, so every proven candidate either suppresses the whole lower tier (unsafe) or leaves vanilla reload alive (double-fire). No safe staged variant can be prepared.

**Rollback for the (unstaged) candidate, if it is ever authorised:** restore `Flags 0x6 0` (SHA-256 of the current accepted conf `57778A1D2ED7EDCA8A321CCDF2D5A76A8092E8C0319D0D4ED9DDE07194F60993`).

---

## Confirmation / boundaries

```
WORKBENCH_LAUNCHED = NO
REFORGER_LAUNCHED = NO
GAME_MODE_LAUNCHED = NO
RUNTIME_TEST = NO
COMPILE_TEST = NOT_RUN_BY_AGENT
LIVE_CHANGED = NO
LABS_CHANGED = NO
META_CHANGED = NO
GUID_CHANGED = NO
KEYBINDING_CHANGED = NO
SCRIPT_CHANGED = NO
ASTRA_CHANGED = NO
G3B2_CHANGED = NO
CORE_CHANGED = NO
PRODUCTION_WEAPONS_CHANGED = NO
```

Final status: `T4B_SELECTIVE_R_OWNERSHIP_AUDIT_COMPLETE`. STOP.
