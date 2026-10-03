# MP-133 V3 — T2a isolated player-marker lab (prepared)

**Status:** `T2A_LAB_PREPARED; AWAITING_OWNER_MARKER_IMPORT_AND_ASI_REPOINT`.
Local isolated addon only; production/Core/V2 lab untouched; Workbench/game NOT RUN by
the agent. Source: Issue #27 comment 5968619156 (T2a authorization), 5968662213 (Bohemia
docs), and the owner's loadout confirmation.

## Goal

Determine **whether an event authored in a `_player.asi` clip reaches the weapon-side
`WeaponAnimationComponent.OnAnimationEvent`** (vs only the character-side invoker), and
record duplication/order/authority. No ammo/reload/pump behavior is exercised or changed.

## Lab

- Local addon: **`...\addons\ARMSTMP133T2A_Diag`** — new ID `ARMSTMP133T2ADiag`, new root
  GUID `AF1464F772CC998F`; dependencies: base `58D0FB3206B6F859` + Weapons
  `6A70E400C54051DC` (**no Core**, matching the confirmed loadout).
- Cloned MP-133 animation stack with fresh file GUIDs (paths under
  `Assets/Weapons_RUS/Mp_133/T2A/`):
  - `.agr` `F579D9BAB4D1AE9C`, `.agf` `15E51D582D521261`, `.ast` `124C7AD1DEE91314`,
    `.aw` `10C394889E303494`, weapon `.asi` `99E82B778E3C48A7`, player `.asi`
    `1BCB6E5A1AB12EB6`.
  - `.agf` copied verbatim (self-contained graph logic); `.agr`/`.aw`/`.asi` repointed to
    the new AST/AGF/ASI GUIDs; clip rows keep their original clip GUIDs.
- Test prefab `Prefabs/Weapons/MP133_T2A/armst_Shotgun_mp_133_T2A.et` (`5FB844730BED8BD1`,
  entity `7FD677C018140DBC`), inheriting the production MP-133 `{63FF6FDCA4E7E735}` and
  overriding only `WeaponAnimationComponent` (graph + weapon/player ASIs).
- Marker clip source: `Assets/Weapons_RUS/Mp_133/T2A/T2AClips/P_MP133_T2A_Bolt.txa`
  (copy of the player bolt clip) with the **unique marker `ARMST_T2A_PM_C41F7A29` at
  frame 12**; weapon ASI is marker-free.
- Logging only: `Scripts/Game/ARMST_MP133_T2A/ARMST_MP133_T2A_Log.c` — weapon-side
  `modded WeaponAnimationComponent.OnAnimationEvent` (`super` preserved) and a minimal
  character-side `modded SCR_CharacterControllerComponent` subscribing to
  `GetOnAnimationEvent()`. **No** `HandleWeaponReloading`/`HandleWeaponFire`,
  `AddActionListener`, `SetReloadWeapon`, ammo/magazine/chamber code.

## Static validation (agent, offline) — PASS

- All lab files: braces balanced, ASCII clean.
- Marker present **exactly once** in the player `.txa`; **0** in `MP133_T2A_weapon.asi`.
- No R/reload hooks in the script (all scanned patterns = 0).
- GUID wiring resolves: `.agr`→AST+AGF; `.aw`→AST+WASI+PASI+AGR; both `.asi`→AST; prefab→
  AGR+WASI+PASI + production MP-133 parent. New GUIDs are unique across `addons/`.

## Owner steps (import + repoint + run)

1. Confirm loadout (as agreed): **only** `ARMST-PLATFORM---Weapons` + `ARMSTMP133T2A_Diag`;
   **Core and V2/P2 disabled**; other user addons disabled.
2. Import `P_MP133_T2A_Bolt.txa` in the Animation Editor to
   `P_MP133_T2A_Bolt.anm`; report its ANM ResourceName/GUID.
3. The agent then repoints `MP133_T2A_player.asi` `Reload.Erc/Pne.ReloadActionBolt` to the
   imported marker ANM (single-row edit) and re-validates statically.
4. Owner runs: equip `MP-133 [T2A-DIAG]`, perform an **ordinary short R** (native rack),
   capture `console.log`/`script.log`.
5. Capture: which receiver logs the marker — `[ARMST_T2A-CHR]`, `[ARMST_T2A-WPN]`, or both;
   count/order, `isServer`, time, weapon instance.

## STOP conditions

- Any regression of native short-R pump, hold-R inspection, or other weapons → stop.
- No ammo/reload/magazine/chamber/pump changes; no global R hook; no T2b/T2c/shell work
  without a new approval.
- If the marker cannot be authored/imported without prohibited edits, or the installed SDK
  lacks the receiver API → `T2A_BLOCKED` with a source-backed cause.

## NOT RUN

Workbench import/compile and the runtime T2a result are **OWNER TEST REQUIRED**; static
wiring does **not** prove player→weapon event delivery.

---

## Compile fix (owner Workbench, 2026-10-03)

Owner Workbench reported: `Engine class 'WeaponAnimationComponent' cannot be modded.`
(`ARMST_MP133_T2A_Log.c` line 11, the forbidden `modded WeaponAnimationComponent`).

Fix (lab-only):

- Removed the forbidden `modded class WeaponAnimationComponent`.
- Added a dedicated subclass
  `class ARMST_T2A_WeaponAnimationComponent : WeaponAnimationComponent` overriding
  `OnAnimationEvent` with `super.OnAnimationEvent(...)` preserved; it only registers the
  marker `ARMST_T2A_PM_C41F7A29` and logs `[ARMST_T2A-WPN]`.
- The test prefab now assigns `ARMST_T2A_WeaponAnimationComponent "{60B4EA76EB15F6E0}"`
  **in place of** the inherited `WeaponAnimationComponent` (same instance GUID; no second
  animation component).
- Character-side stays `modded SCR_CharacterControllerComponent` (logging only; the same
  modded pattern compiled in the V2 lab). Logging uses `int` server flags instead of
  `bool.ToString()`.
- Removed the stale generated `resourceDatabase.rdb` from the lab so Workbench rescans.
- Static recheck: `modded WeaponAnimationComponent` = 0; subclass/override/super present;
  prefab assigns the subclass; braces/ASCII clean (binary `rdb` ignored); R/reload hooks = 0.

**Unverified → OWNER WORKBENCH:** whether the engine accepts replacing an inherited
component's class in a child prefab, and whether the subclass/`override` compile. If
Workbench rejects the class replacement or the prefab fails to load, **STOP** and report —
do not bypass with global (`modded`) changes.

The two ResourceDB warnings (`Collimator_dot_A.edds.meta`,
`Prefabs/Weapons/Rifles.meta`) belong to the main Weapons addon and are a **separate**
task; untouched.

Status: `T2A_COMPILE_FIX_APPLIED; OWNER WORKBENCH RECOMPILE REQUIRED`.

### Class-helper fix (owner Workbench, latest)

Next owner compile reported `Missing Component Class for
'ARMST_T2A_WeaponAnimationComponentClass'`. Enfusion requires a companion `_Class`
declaration for the script component. Added, per the official component docs and the
project's `[ComponentEditorProps]` precedent:

```
[ComponentEditorProps(category: "ARMST/T2A", description: "T2a diagnostic weapon animation listener")]
class ARMST_T2A_WeaponAnimationComponentClass : WeaponAnimationComponentClass
{
}
```

Base verified in the local SDK: `WeaponAnimationComponentClass` exists
(`interfaceWeaponAnimationComponentClass.html`). The component, prefab assignment and the
character-side `modded` handler are unchanged; `resourceDatabase.rdb` removed again for a
clean rescan.

Status: `T2A_CLASS_HELPER_ADDED; OWNER WORKBENCH RECOMPILE REQUIRED`.

---

## Marker wired + ready for owner run (2026-10-03)

- Imported marker ANM GUID: **`{3581B839F53FC345}`** at
  `Assets/Weapons_RUS/Mp_133/T2A/T2AClips/P_MP133_T2A_Bolt.anm` (owner import; no
  re-import needed).
- Repointed both `Reload.Erc.ReloadActionBolt` and `Reload.Pne.ReloadActionBolt` in the
  cloned `MP133_T2A_player.asi` to that ANM; the weapon ASI remains marker-free.
- Verified: marker `ARMST_T2A_PM_C41F7A29` at **frame 12** in the source `.txa`; weapon
  ASI marker = 0; the ANM `.meta` GUID matches the ASI reference; text files braces/ASCII
  clean (the `.anm`/`.rdb` are binary). Removed the regenerated `resourceDatabase.rdb` so
  Workbench rescans the changed ASI.
- Compilation of the lab is confirmed by the owner (`cannot be modded` and
  `Missing Component Class` are gone).

**Owner run (T2a):** loadout = only `ARMST-PLATFORM---Weapons` + `ARMSTMP133T2A_Diag`
(Core and V2/P2 off); equip `MP-133 [T2A-DIAG]`; perform one ordinary short R (native
rack); capture `console.log`/`script.log` and report which receiver logs the marker —
`[ARMST_T2A-CHR]`, `[ARMST_T2A-WPN]`, or both (count/order/`isServer`). STOP on any
pump/hold-R/other-weapon regression.

Status: `T2A_LAB_READY_FOR_OWNER_RUN`.

**Unrelated log findings (NOT lab-owned; not fixed):** Remington 870 / MP-153 unresolved
`.anm`; unknown `ARMST_ITEMS_STATS_COMPONENTS` (a Core class — Core is disabled in this
loadout); repeated EntityPool `armst_Ammo_12ga.et`. Separate task.

---

## T2a run 1 — results + v2 diagnostic (2026-10-03)

Owner run with the diagnostic prefab: the character handler fired (`[ARMST_T2A-CHR]` ×6;
t≈0 ×2, t≈0.0333 ×4; `isServer=1`); **no** `[ARMST_T2A-WPN]`; the diagnostic prefab load
was not confirmed in the log.

Interpretation: the player marker **does** reach the character-side invoker, but by this
log alone we cannot tell whether the weapon component (a) was not active, (b) receives no
player events, or (c) receives weapon events but not the player marker.

**v2 diagnostic changes (lab-only):**
- weapon-side: generic weapon-event trace (first ~30 events) + explicit `MARKER` line —
  proves whether the component receives events at all;
- character-side: one-shot subscription guard (`m_bT2ASubscribed`) + `init #n` counter;
- 1 Hz `[ARMST_T2A-CHR] weapon prefab=… hasT2AWpnComp=0|1` — confirms the diagnostic
  prefab is equipped and its entity actually carries `ARMST_T2A_WeaponAnimationComponent`
  (i.e. the subclass assignment took effect);
- char handler now logs `MARKER #n … ctrl=0|1 isServer=…`.

**Next run maps the cause:** if `hasT2AWpnComp=1` and `[ARMST_T2A-WPN] event …` appears but
no `MARKER`, the player event does **not** reach the weapon component; if
`hasT2AWpnComp=0`, the subclass assignment was not applied to the equipped prefab; if no
`[ARMST_T2A-WPN]` at all, the weapon-side callback is not being invoked.

**Unrelated log findings (NOT lab; not fixed):** `ARMST_12g_SpreadEffect` (a Core class —
Core is off in this loadout; affects 12ga ammo), `ARMST_ITEMS_STATS_COMPONENTS` /
`m_iCustomGridHeight`, Remington 870 / MP-153 unresolved `.anm`, EntityPool
`armst_Ammo_12ga.et`. Separate task.

Status: `T2A_RUN1_DONE_PLAYER_CONFIRMED; WEAPON_SIDE_PENDING; V2_DIAGNOSTIC_READY`.

---

## T2a run 2 — weapon side confirmed active; player marker NOT forwarded (owner)

- Diagnostic MP-133 prefab `{5FB844730BED8BD1}` equipped; `hasT2AWpnComp=1`.
- Weapon callback received `BlendIn`, `Weapon_EnableFire`, `Weapon_Rack_Bolt` → the
  subclass is live and `OnAnimationEvent` is the weapon-side receiver.
- Character invoker received 4 × `ARMST_T2A_PM_C41F7A29` (`isServer=1`); **no** weapon-side
  marker line.
- Conclusion (tested configuration): the player-authored event is **not** automatically
  forwarded to the weapon component → an explicit bridge or a weapon-side event is required.
- The 4 events / `isServer=1` are not proof of exactly-once or authority.
- Next (owner review required before implementation): `reports/MP133_V3_EVENT_BRIDGE_DESIGN.md`.

Status: `T2A_ROUTE_OBSERVED / BRIDGE_DESIGN_AUTHORIZED_ONLY`.
