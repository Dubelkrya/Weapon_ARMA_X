# MP-133 V3 — T4a: disposable `SetAmmoCount` semantics probe

**Status:** `T4A_SINGLE_MANAGER_PATCH_PREPARED_OWNER_RUN_REQUIRED`.
Isolated lab only. Production Weapons/Core, frozen V2/P2, the T2A diagnostic and Astra's
graph lab are byte-identical. Source: Issue #27 comments 5970853781, 5971080837, 5971156650.
Knowledge-repo changes are on branch `t4a/interaction-patch` (PR #31 concurrent; main untouched).

Labels: **SOURCE** (installed SDK / project+snapshot files), **INFERENCE**, **UNRESOLVED**.

---

## 1. Defects fixed in this patch

- Run 1: only a global key-P action existed; no standard interaction (owner could not use it).
  Fixed earlier by adding a `ScriptedUserAction`.
- Run 2 (owner screenshot): the T4a prefab added a **second** `ActionsManagerComponent`
  (`3A5D97896C4BD2F1`), because the magazine chain already inherits one. Two managers conflict;
  the new action sat on the wrong manager. **This patch removes the duplicate and adds the
  action to the inherited manager.**

## 2. Inherited manager identified (evidence)

`ARMST_T4A_TestMagazine.et` → `{B0DFDF7AAA9C5D39}armst_12ga_Buckshot.et` →
`12ga_Buckshot_base.et` (local, no manager) → `Magazine_762x51_M14_20rnd_Base.et` →
`Prefabs/Weapons/Core/Magazine_Base.et` (base game, packed).

The inherited `ActionsManagerComponent` GUID is **`{F092E6B0537754FD}`** with
`UserActionContext "{5086F9AB010868CE}"` — it appears identically in the base-game magazine
snapshots `catalog/magazines/Magazine_9x19_M9_15rnd_Base.et`,
`catalog/magazines/Magazine_545x39_RPK_45rnd_Base.et`, `Box_*`, `Magazine_762x39_Vz58_30rnd_Base.et`
and others, all inheriting `Magazine_Base.et` (**SOURCE**, snapshot corpus). The stock
pickup/attach actions live on this manager.

**Residual risk (UNRESOLVED):** the base-game `Magazine_Base.et` is inside a packed `.pak`
(unreadable locally), so the GUID is **inferred** from 9+ sibling magazine snapshots, not read
from the exact parent file. The effective tree must be confirmed in Workbench before gameplay.

## 3. Fixed prefab (single manager)

`Prefabs/Test/ARMST_T4A_TestMagazine.et`:
```
GenericEntity : "{B0DFDF7AAA9C5D39}Prefabs/Weapons/Magazines/12ga/armst_12ga_Buckshot.et" {
 ID "C9E63012F5D46B8A"
 components {
  ActionsManagerComponent "{F092E6B0537754FD}" {
   additionalActions +{
    ARMST_T4A_AddRoundUserAction "{6D80CBBC9F7E0524}" {
    }
   }
  }
  ARMST_T4A_SetterProbe "{DAF7412306E57C9B}" {
  }
 }
}
```
- Only **one** `ActionsManagerComponent`; it is the inherited one (same GUID), so its stock
  pickup/attach actions and context are preserved.
- The T4a action is added with the array-merge operator `+{` (project-proven syntax, e.g.
  `m_aAuthoredLabels +{`, `ClassesFilter +{`), so the inherited `additionalActions` list is
  extended, not replaced.
- No new `ActionContexts`; the action uses the inherited default context.
- Removed the duplicate manager GUID `3A5D97896C4BD2F1` and the lab context GUIDs
  `4B6EA89A7D5CE302` / `5C7FBAAB8E6DF413`.

## 4. Action behaviour (unchanged)

`ARMST_T4A_AddRoundUserAction : ScriptedUserAction` (label **"T4a: add 1 test round"**,
`GetActionNameScript`), shown/invocable via the standard interaction menu. `PerformAction`
operates on `GetOwner()` — only the magazine the player interacts with — and performs **one**
guarded write: reject (`no-magazine` / `already-used` / `full`) without writing, otherwise
`SetAmmoCount(current+1)` once, then re-read + identity check. `ARMST_T4A_SetterProbe` still sets
the disposable baseline (`m_iT4AStartAmmo`, 0…max) on init. Logs `[ARMST_T4A-SETTER]`.

## 5. Identities / static checks

- Retained: prefab resource `{B8D52F01E4C35A79}`, `.et` entity ID `C9E63012F5D46B8A`; probe
  `{DAF7412306E57C9B}`; new action `{6D80CBBC9F7E0524}`; lab project `ARMSTMP133T4ASetProbe`
  `{A7C41E90D3B24F68}`.
- Prefab has exactly **1** `ActionsManagerComponent`. New GUIDs unique; `{F092E6B0537754FD}` is
  the inherited GUID (appears in snapshot corpus + this prefab).
- Script unchanged: SHA-256 `BE8EF1AF0869385F2C55E764A53F3E15C67524A93E3D89D9212D9A8B4FF8700A`;
  braces 22/22, ASCII clean; no `modded`/input/spawn/inventory/RPC/fire calls.
- Unchanged: Weapons dirty 29, Core dirty 4; T2A `E978EDAF…`; V2 `654B2437C5689D4D`.
  Agent cannot compile — **effective inheritance / interactivity NOT verified**.

## 6. Owner steps (inspect tree FIRST, then run)

1. Loadout: base + `ARMST-PLATFORM---Weapons` + `ARMSTMP133T4A_SetProbe`; Core/V2/P2 OFF.
2. **Workbench tree check first:** the resolved `ARMST_T4A_TestMagazine.et` must show **exactly
   one** `ActionsManagerComponent` with the stock pickup/attach actions **and** the T4a action.
   STOP if a second manager or missing stock actions appear.
3. Compile `Game` (STOP on own SCRIPT(E)); place **one** disposable magazine; confirm
   `phase=init` / `phase=baseline` (0/10).
4. Invoke the contextual action **"T4a: add 1 test round"** → `pre ammo=0/10` → `post ammo=1/10
   sameIdentity=1`; invoke again → `reject reason=already-used`.
5. Full case: set `m_iT4AStartAmmo=10`, re-enter, invoke → `reject reason=full`.
6. Send the `[ARMST_T4A-SETTER]` excerpt + the Workbench tree screenshot + visible ammo.

## 7. Stop / authorization

`T4A_SINGLE_MANAGER_PATCH_PREPARED_OWNER_RUN_REQUIRED`. If Workbench shows a second manager, a
broken pickup action, a SCRIPT(E), or a mis-targeted action → STOP and report. Real transfer,
donor depletion, installed-mag mutation and MP authority remain separately authorised.
