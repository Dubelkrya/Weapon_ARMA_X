# MP-133 V3 — T0 checklist + T1/T2 read-only designs

**Original design status:** `V3_STAGE1_T0_OWNER_TEST_PENDING / T1_T2_READONLY_DESIGN_APPROVED / T1_T2_CODE_NOT_AUTHORIZED`. Read-only. **No gameplay file changed, no Workbench/game run, no new addons created, no implementation.** Source: Issue #27 comment 5967836589.

**Subsequent owner update, 2026-10-03:** `T0_CLEAN_FUNCTIONAL_PASS / PHYSICAL_MAG_ENTITY_IDENTITY_NOT_INSTRUMENTED`. The three-shot native-pump baseline and hold-R inspection were confirmed with only the Weapons addon loaded. The T1/T2 designs below are complete as documents, but implementing diagnostics remains **NOT AUTHORIZED**. See [`MP133_INDEX.md`](MP133_INDEX.md) and Issue #27 comments 5967858916 / 5967911774.

**Engine target:** installed Enfusion **1.8.0.13** (`ArmaReforgerSteam.exe` FileVersion),
Tools build 24870687. SDK reference used: local
`...\Arma Reforger Tools\Workbench\docs\ArmaReforgerScriptAPIPublic` (may differ from the
public web docs). Evidence grades: `OWNER-RUNTIME` / `SOURCE` / `SDK` / `SCREENSHOT` /
`INFERENCE` / `UNRESOLVED`.

---

## 1. Sources read (and the honest gaps)

Read: `AGENTS.md`, `docs/sync/CURRENT_AI_SYNC.md`, Issue #27, `reports/MP133_V3_DESIGN_AND_BASELINE_ASSESSMENT.md`,
`reports/MP133_V3_1_I1_LAB_INTERFERENCE_INVENTORY.md`, `reports/MP133_V3_2_ANIM_EVENT_FINDING.md`,
Chung/BC-Ithaca `bc_ithaca_m37.agf/.agr/.ast/_player.asi/_weapon.asi` and
`BC_PumpShotgunComponent.md` / `SCR_IthacaAnimationComponent.md` (present at
`C:\Users\yshky\Documents\Codex\...\ASTRA_MP133_V3_Handoff\Chung\` and
`...\addons\Armst_Work\`), ASTRA `EVIDENCE_DOSSIER_RU.md`, legacy logs, current local
addons/SDK.

**Gaps (UNRESOLVED):** actual Chung `.anm/.txa`; native SDK source for
`HandleWeaponReloading` / `Weapon_AttachMagazine` / `Weapon_Rack_Bolt`; base-game input
`.conf`; fresh full Stage 1 log; full P2 compile trace. No behaviour is inferred from
static data alone.

---

## 2. T0 — OWNER game test (pending; agent cannot run)

With **all V2/P2/lab OFF**, fresh Workbench session, original non-lab MP-133:
1. Note initial physical magazine identity (entity/GUID, not just prefab), ammo
   count/capacity, chamber, and a compatible real ammo source.
2. `shoot → ordinary short R (native rack) → shoot` for **three actual successive shots**
   (enough initial ammo); verify chamber transitions, tube decrease, **no magazine swap**.
   Afterwards separately test the last round and the dry/empty condition (so empty ammo
   is not mistaken for a broken pump).
3. **Hold R** → vanilla inspection without accidental pump/load. Core LSHIFT+R: check only
   if safe in a **separately controlled** case — do **not** trigger the known shell-wasting
   Core path as part of baseline.
4. Provide a summary, resource/load/compile errors, and relevant log lines.

**No Stage 1 PASS from P2 merely showing the R animation.** If T0 fails, stop downstream
implementation and diagnose the clean baseline. → `V3_STAGE1_T0_OWNER_TEST_PENDING`.

---

## 3. T1 — input-routing research + design (read-only, no code)

### 3.1 Established facts
- **`ARMST_LIGHT_RELOAD_ACTION` = keyboard R + LSHIFT** (`ARMST-PLATFORM---Core\Configs\System\chimeraInputCommon.conf:113-125`) → LSHIFT+R. `SOURCE`
- **Stock reload / inspection action names are NOT in project configs**; the base-game
  input config lives in the game paks. `UNRESOLVED` — must be resolved from the base
  config/`data.pak`, SDK enumeration, or owner keybindings before any listener can target it.
- `CharacterInputContext` exposes reload **state** (`GetWeaponReloadType`,
  `WeaponIsStartReloading`, `WeaponIsRaised`, `WeaponIsPullingTrigger`) and
  `SetReloadWeapon`, but **no physical key DOWN/UP edge**. `SDK`
- `CharacterControllerComponent.ReloadWeapon()` exists (native). `SDK`
- `InputManager.AddActionListener(action, EActionTrigger.DOWN/UP, fn)` is the project
  pattern (Core). `SOURCE`
- `ResetAction` cancelling an **already accepted** reload is **not proven**. `UNRESOLVED`

### 3.2 Routing map (to be confirmed by T1)
`vanilla R → input action <name?> → SCR_CharacterCommandHandlerComponent.HandleWeaponReloading
(script) → reload type 1 / native pump → engine`; `hold R → inspection (<path?>)`.
A weapon-scoped `AddActionListener` is **observational** unless it can suppress the native
action — that must be proven, not assumed.

### 3.3 Verification table (owner-run, instrumentation-only, reversible; after separate approval)
| Check | Question | Result |
|---|---|---|
| Action name | exact stock R reload / inspection action names, context, filter | UNRESOLVED |
| Edges | does a listener receive DOWN and UP? | UNRESOLVED |
| Native coexistence | does native R still run with a passive listener? | UNRESOLVED |
| Suppression | can a weapon-scoped listener prevent ONLY the MP-133 native reload? | UNRESOLVED |
| `ResetAction` | does it cancel an accepted reload? | UNRESOLVED |
| Hold | does hold-R map to inspection, distinct from tap? | UNRESOLVED |

### 3.4 Minimal owner-only T1 matrix (design only)
- **T1a** passive listener on the resolved R action (DOWN/UP) → **log only**; confirm edges
  and that native R still runs.
- **T1b** add a hold-threshold log (no suppression) → confirm tap vs hold edges and that
  hold-R inspection is intact.
- **T1c** (only if T1a/b prove edges) design a **MP-133-instance-only** suppression test.
- **STOP/FAIL:** if no action name resolves, or edges are not delivered, or suppression
  cannot be weapon-scoped → `UNRESOLVED / OWNER TEST REQUIRED`; do **not** present a
  passive listener as consumption.

### 3.5 Fallback (requires owner decision)
A **separate action to start loading** (dedicated key). Not adopted unilaterally.

---

## 4. T2 — player/weapon/graph animation-event routing research + design (read-only)

### 4.1 Established facts
- `WeaponAnimationComponent.OnAnimationEvent(AnimationEventID, AnimationEventID, int, float, float)`
  — the **weapon-side** receiver. `SDK`
- `WeaponAnimationComponent.SyncWithCharacter(ChimeraCharacter, bool isMainCharacter, string overrideStartNode)`
  — sync API. `SDK`
- The character controller exposes an animation-event invoker via `GetOnAnimationEvent()`
  (project usage). `SOURCE`
- Chung binds **separate `.anm` per row** in `_player.asi` vs `_weapon.asi`; the weapon
  component is on the weapon (`WeaponComponent.components.WeaponAnimationComponent`). `SOURCE`
- Chung events: `PumpShotgunSpawnShell(1)` / `PumpShotgunSetAmmoCount(11)` authored in
  **player** clips; `Weapon_Rack_Bolt[12]` in `Reload_CloseAction`; `PumpShotgunAdjustAmmoCount`
  is a **graph** event. `SCREENSHOT/SOURCE`
- `Main Path Only` semantics, `BlendOut` vs `BlendOut2` routing, and duplicate delivery
  when a key exists on both instances: `UNRESOLVED`.
- Whether a `player.asi` generic event reaches the weapon component, needs a matching
  `weapon.asi` key, or is forwarded by `SyncWithCharacter`: **UNPROVEN**.

### 4.2 Test design (three sequential, separately approved; NEW isolated cloned lab; logging only)
- **T2a** unique **player-only** marker event → map which receiver(s) observe it.
- **T2b** unique **weapon-only** marker event → map receiver(s).
- **T2c** distinct/paired markers to test duplicate delivery; include a graph-origin event
  if relevant.
- Each run records: receiver (character controller invoker vs `WeaponAnimationComponent.OnAnimationEvent`),
  network authority/proxy, weapon entity, event ID/name, time, graph/state, count/order.
- `OnAnimationEvent` has no source-ASI argument → label the source only via a **unique
  authored marker** + the experiment mapping.
- No ammo mutation / attach / detach / spawn / commit; no conflicts with native events; do
  **not** add `Weapon_Rack_Bolt` to insert clips.

### 4.3 Minimal patch design (NOT applied)
Add a weapon-scoped `WeaponAnimationComponent` subclass (new lab GUID) that overrides
`OnAnimationEvent`, calls `super.OnAnimationEvent(...)`, registers the marker IDs via
`GameAnimationUtils.RegisterAnimationEvent`, and logs `(id, timeFromStart, entity, isServer,
count)`. The character-side invoker logs the same markers for comparison. No other change.

---

## 5. Proposed isolated-lab resource diff (PLAN only)

- **New, isolated** lab clone with distinct addon ID/GUIDs; V2/P2/prod untouched.
- **Phase 1 (T1):** new prefab variant + a weapon-scoped **logging-only** component
  (no suppression, no ammo). Rollback = delete the clone; validate other weapons unaffected.
- **Phase 2 (T2):** a **new clip copy** with unique marker events (owner imports the
  `.anm`); add the weapon-side override (§4.3). Prod clips untouched.
- Each phase: backup + SHA manifest, one variable, owner-run, STOP criteria.

This is a **plan**; it requires separate authorization and is not created here.

---

## 6. Unknowns / decision gates

Stock action names · edge delivery · suppression feasibility · `ResetAction` ·
player↔weapon event routing · `Main Path Only` · `BlendOut` semantics · native handlers ·
**reliable native pump-completion signal** · safe real-shell transaction.

Gates: **T0 PASS** → T1/T2 instrumentation (separate approval) → T2 routing result →
weapon-scoped V3 design → staged implementation (each separately approved).

---

## 7. Carryover separation (do not conflate)

- **P2:** global lab `modded SCR_CharacterCommandHandlerComponent` presence/behaviour
  implicated in all pumps' R regression; exact `super`/`Default` mechanism UNKNOWN; no
  global override, no P3.
- **Event rename (V3.2):** native `Weapon_SpawnMagazine/AttachMagazine/MagRelease` in the
  lab insert clip "made animation work" in one config; **not** proof of correct chamber/no
  swap/conservation (earlier `reloadType=5` gave `3/3 → 10/10`). Verify via T0/T3.
- `armst_12ga_Shell.et` may hold 10 rounds / mixed mapping → inventory-entity deletion and
  artificial mag +1/dummy ammo are NOT safe per-shell transport. Do not touch ammo.
- Restored MP-133 excludes `CMD_Weapon_Reload=7`; do not propose command 7 without a
  separately authorized graph change. `reloadType=1` is not proof of pump completion.

---

## 8. Bohemia documentation source note for T2a (owner-supplied, comment 5968662213)

Source: official `Arma_Reforger:Weapon_Animation` wiki (+ Setup, Animation Editor,
Custom Properties/Events, Nodes, `WeaponAnimationComponent` API).

**Supported by the docs (SOURCE)**
- A weapon uses **two distinct animation instances**: `_player.asi` (holding character)
  and `_weapon.asi` (weapon); they run simultaneously and corresponding clips normally
  need compatible lengths.
- Distinct roles: `.aw` workspace, `.ast` template, `.agr` graph, `.agf` graph logic, both
  `.asi` instances, `.anm` clip (per-frame events). On the weapon prefab,
  `WeaponAnimationComponent` assigns the graph + weapon AnimInstance; `Anim Injection`
  assigns the same graph + the **player** AnimInstance with root binding `Weapon`.
- Event keys are authored per `.anm`/`.txa` in Animation Editor (fire at a frame); graph
  **Event nodes** also emit events; `MainPathOnly` restricts sampling to the main path.
- Copied weapon `.asi` clips need skeleton/bone compatibility; use unique test-clone
  resources, never edit production/archived V2 clips.

**NOT proven by these pages (UNRESOLVED; T2a must establish)**
- that a marker authored in `_player.asi` reaches
  `WeaponAnimationComponent.OnAnimationEvent`;
- whether `SyncWithCharacter` forwards arbitrary events; callback event provenance;
  duplication across paired player/weapon/graph events; `MainPathOnly` exactly-once;
  server/proxy authority; safe ammo commit from animation callbacks.
- Public docs may be version-shifted vs installed **Enfusion SDK 1.8.0.13** — verify the
  actual class methods/signatures locally.

**T2a guidance (only after the #28 publication/CI gate):** one unique frame event on a
**player-only copied clip**, bound via cloned `player.asi`/Anim Injection; log both the
character-side invoker and the weapon-side `WeaponAnimationComponent.OnAnimationEvent` if
the installed SDK supports it; keep `weapon.asi` marker-free in T2a; record
receiver/marker/time/count/network side. Static/preview wiring does **not** prove
player→weapon delivery. No native reload event, no ammo change, no global R hook, no
T2b/T2c without the next approval.
