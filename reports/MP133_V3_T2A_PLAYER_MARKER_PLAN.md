# MP-133 V3 — T2a player-only animation-event diagnostic (prep plan)

**Status:** `T2A_PREP_PLAN_READY; AWAITING_OWNER_LOADOUT_CONFIRMATION_AND_MARKER_IMPORT`.
Source: Issue #27 comments 5968619156 (T2a authorization) and 5968662213 (Bohemia docs).
Knowledge-only at this stage; **no** production/Core/V2 lab/gameplay edits; agent does
not run Workbench/game.

## Goal (single question)

Determine **whether an animation event authored in a `_player.asi` clip is received by
the weapon-side `WeaponAnimationComponent.OnAnimationEvent`** (or only by the
character-side invoker), and record duplication/order/authority if seen. T2a does **not**
test shell transfer, ammo, reload or pump behavior.

## Marker (unique, player-only)

- Marker name (collision-free): **`ARMST_T2A_PM_C41F7A29`** (prefix + 8 hex).
- Authored on a **single frame** of a **copied player clip** in the T2A addon only.
- **No** matching marker in `weapon.asi` in T2a; origin is inferred solely from the
  unique player-only placement (the `OnAnimationEvent` signature carries no ASI origin).

## Isolated lab layout (plan; to be created)

New separate local addon `ARMST_MP133_T2A_Diag` with a **distinct addon ID + fresh
GUIDs/meta**. Reuse only the minimum cloned resources (fresh GUIDs), never edit
production/archived V2 files.

| Resource | Plan |
|---|---|
| `addon.gproj` | new ID `ARMSTMP133T2ADiag`, new root GUID |
| cloned `.agr/.agf/.ast/.aw` | copy of the MP-133 animation set, fresh GUIDs |
| cloned `_weapon.asi` | weapon instance, **marker-free** |
| cloned `_player.asi` | player instance; the marker clip is repointed here |
| marker player clip `.txa`→`.anm` | one frame carries `ARMST_T2A_PM_C41F7A29` (owner imports) |
| test prefab | inherits the production MP-133, but wires the cloned graph/ASIs only |
| logging scripts | see below; `super` preserved; no R/reload/ammo logic |

## Logging (both sides, passive)

1. **Weapon side** — a test-only subclass of `WeaponAnimationComponent` on the cloned
   prefab; `override void OnAnimationEvent(...)` → `super.OnAnimationEvent(...)` + log
   `(marker name/id, timeFromStart, weapon entity id)`.
2. **Character side** — a minimal `modded SCR_CharacterControllerComponent` that only
   subscribes to `GetOnAnimationEvent()` and logs the same marker (`OnInit`, passive).
   **No** `HandleWeaponReloading`/`HandleWeaponFire`, no R hook, no input mutation.
   (If a character-side invocation point without a global `modded` component is
   available in the installed SDK, prefer it; otherwise document why the logging-only
   `modded` component is required.)

Every log line records: receiver side, exact marker id/name, count/order, elapsed event
timing, actual weapon instance, authority/client context, and active animation state when
obtainable. `MainPathOnly`/`SyncWithCharacter` forwarding are **not** assumed.

## Owner steps (after confirmation)

1. Confirm the isolated loadout: **only** `ARMST-PLATFORM---Weapons` + the new T2A lab
   enabled; **Core and V2/P2 disabled**.
2. Import the prepared marker `.txa`→`.anm` in the Animation Editor; return the resulting
   ANM ResourceName/GUID (the agent then wires the cloned `player.asi`/graph).
3. Run T2a (native short-R pump unchanged); provide `console.log`/`script.log`.
4. Abort immediately if native short-R pump, hold-R inspection, or any other pump weapon
   regresses.

## Safety / STOP criteria

- No ammo count/inventory change, no shell spawn/delete, no mag replacement, no
  `Weapon_AttachMagazine/SpawnMagazine/MagRelease/Rack_Bolt` events, no extra
  `ReloadWeapon()`, no `ResetAction`, no global R hook, no `modded`
  `SCR_CharacterCommandHandlerComponent`.
- If the marker cannot be authored without prohibited edits, or the installed SDK lacks
  the receiver API, **STOP** (`T2A_BLOCKED`) with a source-backed cause; do not create
  half-wired resources.
- Status ends as `T2A_LOG_ONLY_LAB_READY_FOR_OWNER_TEST` only after static resource/GUID
  wiring is validated; this never proves player→weapon delivery.

## Offline evidence

Static syntax/resource/GUID/reference checks only; Workbench compile and the runtime
result are **OWNER TEST REQUIRED** (NOT RUN by the agent).
