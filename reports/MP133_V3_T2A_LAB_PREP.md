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
