# MP-133 Task #1 — `Flags 0xA` (Overlay + Exclusive) stage review

Status: **FLAGS_0XA_NOT_SAFE_TO_STAGE**
Date: 2026-10-07
Task: Issue #34 — comment `6035455627`.
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `b9c722dd15ca6632d5edc4fbd86058a4b93a4b07`.
Mode: **SOURCE / STATIC READ-ONLY.** No staged candidate created, no live/labs change.

Evidence classes: **OWNER_WORKBENCH_EVIDENCE**, **OFFICIAL_SOURCE**, **PUBLIC_WORKING_MOD**, **INFERENCE**, **UNRESOLVED**.

---

## 0. Outcome up front

The requested one-variable candidate `Flags 0x6 0 → Flags 0xa 0` (Priority 20000) was **not staged**, because the evidence review surfaced a **direct contradiction signal for the Overlay + Exclusive combination**:

- Owner Workbench operation `Exclusive ON` on the `0x6` context serialized to **`Flags 0x8 0`**, i.e. the editor **cleared Overlay + CursorVisible** instead of producing the expected `0xE` (0x6 | 0x8) — see owner evidence `6035409494`.
- The installed official docs define only `Overlay` and `CursorVisible`; `Exclusive` is **undocumented**, and there is no official statement that it may be combined with `Overlay`.
- The only positive co-existence example is a **hand-authored third-party conf** (Overthrow), which is corroboration only.

Per the task's own gate ("if evidence contradicts the combination, STOP with `FLAGS_0XA_NOT_SAFE_TO_STAGE` and do not prepare a runtime candidate"), the combination is treated as **not safely supported**.

---

## 1. Required evidence review

### 1.1 `0x8 = Exclusive` — OWNER_WORKBENCH_EVIDENCE
Owner saved the T4B context after toggling `Exclusive`; serialized `Flags 0x8 0` with `.meta` `{795184CF9AD764DB}` preserved (comment `6035409494`). **Proven.**

### 1.2 `0x2 = Overlay` — strength classification
- **OWNER_WORKBENCH_EVIDENCE:** `Flags 0x6` corresponds to UI *Overlay ON + Cursor Visible ON* (two bits `0x2,0x4` ↔ two checkboxes) — but the `0x6` reading alone does **not** say which of `0x2/0x4` is which flag.
- **PUBLIC_WORKING_MOD:** `ArmaOverthrow/Overthrow.Arma4` `Configs/System/chimeraInputCommon.conf` uses `Flags 2` on `OverthrowGeneralContext` (an additive/co-existent general context = Overlay behaviour) and `Flags 4` on all menu contexts (cursor contexts = CursorVisible).
- **INFERENCE:** therefore `0x2 = Overlay`, `0x4 = CursorVisible`.
- **VERDICT:** strongly triangulated, **not** OFFICIAL numeric enum proof. (No official numeric mapping for these flags was found in the installed docs.)

### 1.3 `0xa` public examples
- PUBLIC_WORKING_MOD, exact path `https://github.com/ArmaOverthrow/Overthrow.Arma4/blob/main/Configs/System/chimeraInputCommon.conf`:
  - `ActionContext OverthrowPlaceContext { Priority 46; Flags 0xa; ... }` — input-claiming placement context (primary example).
  - `Flags 8` alone on `OverthrowBuildContext`; `Flags 0x26` on `OverthrowMapLayersContext`; `Flags 0x2e` on `OverthrowMapCommandContext`.
- No **official** example of `0xa` was found.

### 1.4 Any source/example where Overlay + Exclusive co-exist
Only the third-party Overthrow `0xa` line above. It is hand-authored; the Workbench editor did **not** produce it (see 1.5). No official source.

### 1.5 Any source indicating Exclusive disables Overlay / forces other checkboxes off
- **OWNER_WORKBENCH_EVIDENCE (direct):** starting from `Flags 0x6` (Overlay + CursorVisible), enabling `Exclusive` serialized **`Flags 0x8`**, not `0xE`. The prior Overlay + CursorVisible bits were cleared. This is evidence the Workbench flag editor does **not** co-serialize Overlay with Exclusive — i.e. the two are not freely combinable in the tooling that produces the accepted configs.
- Installed `Page_Input.html` §"Action Contexts" (OFFICIAL_SOURCE) defines only:
  - `Overlay` — "allows contexts with lower priority to also be updated when this context is active",
  - `CursorVisible` — "tells InputManager that the context uses the mouse cursor".
  `Exclusive` / `Force Cursor` / `Capture Cursor` are **not defined**; the Workbench UI exposes them as checkboxes (all five strings exist in `ArmaReforgerWorkbenchSteamDiag.exe`), but no semantics or compatibility rule is published.

**No evidence was found that Overlay + Exclusive are documented or editor-producible as a pair; there is direct owner evidence they were separated by the editor.**

---

## 2. Why this fails the stage gate

1. The candidate's meaning depends on an **undocumented** flag (`Exclusive`) whose interaction with `Overlay` is unproven.
2. The engine's documented model is **priority-tier wide-context** arbitration (`Page_Input.html`): Overlay lets lower contexts update; a non-Overlay context suppresses lower tiers wholesale. If `Exclusive` behaves as the logical counterpart of `Overlay` (sole/exclusive ownership), then `0xa` is **internally contradictory** — the two bits express opposite intent.
3. The only co-existence support is a third-party hand-authored conf; the owner's own Workbench save **cleared Overlay when Exclusive was enabled**, so the accepted-config tooling does not exhibit the combination.
4. Staging `0xa` at `Priority 20000` and then running it could suppress movement/look/fire (whole-tier) — the exact unsafe outcome the task warns about.

Under the task gate ("internally contradictory or unsupported" → do not stage), the combination is treated as **unsafe to stage**.

---

## 3. What was NOT done

- `artifacts/astra-rebuild/stageSelectiveROwnership/Configs/System/chimeraInputCommon.conf` was **not created**; no `git add -f` performed.
- No `.meta` copied or touched; GUID `795184CF9AD764DB` unchanged.
- The owner's current live Workbench file (which currently contains the temporary `Flags 0x8 0` save, live conf SHA-256 `ABBE77489BFFB1FA4556F11CC12610EC3A063C0C77C69E833F523D82CD4DACC9`) was **read only** and **not modified**.

Diff against the accepted repo config — **no change produced**:

```diff
(accepted labs conf, SHA-256 57778A1D2ED7EDCA8A321CCDF2D5A76A8092E8C0319D0D4ED9DDE07194F60993)
  Priority 20000
- Flags 0x6 0
(nothing staged)
```

---

## 4. Unblock path (owner-only, no runtime)

Before `0xa` can be staged safely, resolve the Overlay ↔ Exclusive compatibility **in Workbench only** (no Game Mode, no R):

1. Open `ARMST_MP133_ReloadContext` properties with `Flags 0x6 0` (Overlay + Cursor Visible on).
2. Check `Exclusive` **without** unchecking Overlay / Cursor Visible.
3. Read the resulting hex and the checkbox states:
   - if it becomes `0xe` (or `Overlay` stays checked) → `Overlay + Exclusive` is editor-supported; re-task: stage the `0xa` candidate (one-variable).
   - if it becomes `0x8` and Overlay is auto-cleared → the editor treats them as mutually exclusive → the `0xa` combination is not safely usable; STOP stands.
4. Close **without saving** a modified config, or revert to `0x6`.

The alternative one-bit step already suggested in review `6035165095` (`0x6 → 0xe`, add Exclusive only, keep Overlay + CursorVisible) is only valid if step 3 shows the editor keeps Overlay checked — which the current `0x8` save suggests it does not.

---

## 5. Confirmation / boundaries

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

Final status: `FLAGS_0XA_NOT_SAFE_TO_STAGE`. STOP.
