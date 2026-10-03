# MP-133 V3 — T2c passive `OnCharacterCommand` trace (lab-only)

**Status:** `T2C_LOGGING_ADDED; STATIC_PASS; OWNER_RUN_REQUIRED`.
Lab-only; production Weapons/Core/other labs/V2 untouched; Workbench/game NOT run by the
agent. Source: Issue #27 comment 5970274540. No graph/ASI/clip/prefab, no input override, no
ammo/magazine/reload logic.

---

## 1. SDK compatibility check (required before editing)

The published `community.bistudio.com` API pages are SDK **1.13.2**; the installed version is
**1.8.0.13**, so compatibility was verified against the **installed** SDK instead:

- Local authority: `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\
  Workbench\docs\ArmaReforgerScriptAPIPublic\html\` (installed with the game Tools,
  doc file mtime 2026-09-19).
- `interfaceWeaponAnimationComponent.html` (inherits `BaseItemAnimationComponent`) lists:
  `protected void OnCharacterCommand(int commandID, int intValue, float floatValue)` —
  *"Called when animation command was called in synced character's animation logic."*
- Also present: `protected void OnAnimationEvent(AnimationEventID, AnimationEventID, int, float, float)`
  (the callback our diagnostic already overrides) and `IsAnimationEvent(...)`.
- **Conclusion:** the override is available in the installed version → compatible. No online
  1.13.2 assumption is relied upon.

---

## 2. What was added (single file, passive)

`ARMSTMP133T2A_Diag/Scripts/Game/ARMST_MP133_T2A/ARMST_MP133_T2A_Log.c` —
`ARMST_T2A_WeaponAnimationComponent` (the subclass already assigned to the T2A test prefab):

- new counter `m_iCmdCalls`;
- new override:
  ```
  override void OnCharacterCommand(int commandID, int intValue, float floatValue)
  {
      super.OnCharacterCommand(commandID, intValue, floatValue);   // always
      m_iCmdCalls++;
      ... Print("[ARMST_T2C-CMD] #n commandID=<id> intValue=<i> floatValue=<f> srv=<0|1> wep=<prefab>", NORMAL);
  }
  ```
- logs **command type id** (`commandID`) separately from its **parameters** (`intValue`,
  `floatValue`), plus the weapon instance (`wep=`) and a monotonic call index (`#n`).
- `super` is always called; nothing else in the class changed (the T2a/T2b marker trace is
  intact). No input handling, no graph/ASI/clip/prefab edit, no ammo/magazine/reload change.

---

## 3. Static checks — PASS

- Braces 16/16, parens 109/109, ASCII clean.
- `super.OnCharacterCommand(...)` present; no `HandleWeaponReloading`/`HandleWeaponFire`/
  `AddActionListener`/`SetReloadWeapon`/`SetAmmoCount`/`*Magazine`/`ReloadWeapon(`;
  no `modded WeaponAnimationComponent`.
- Stale `resourceDatabase.rdb` removed so Workbench rescans.
- Lab file SHA-256: `03AE04C6191370E1DF616D701E8FB8BAC4371B8E4347602F820FC60880FE96D1`.

---

## 4. Owner run (one ordinary short R + one stock magazine reload)

1. Loadout unchanged: `ARMST-PLATFORM---Weapons` + `ARMSTMP133T2A_Diag`; Core and V2/P2 OFF.
2. Recompile `Game` in Workbench (the lab script changed; rdb removed).
3. Equip `MP-133 [T2A-DIAG]`; open `console.log`/`script.log`; filter `ARMST_T2C-CMD`.
4. Do **one ordinary short R** (no Shift), then **one stock magazine reload** if it is
   reachable without changing controls (empty/missing magazine so the engine routes
   `CMD_Weapon_Reload` 2/4). Do not use Shift+R or any custom action.
5. Capture the `[ARMST_T2C-CMD] ...` lines.

---

## 5. Read-out

- `commandID` = animation-command **type** (compare with the `CMD_Weapon_Reload` conditions in
  `MP133.agf`); `intValue` = its **parameter** (the graph compares `GetCommandI` against 1/2/3/
  4/5/6, and `GetCommandF` against 0.0).
- Expected (to confirm, not assume): ordinary short R → a `CMD_Weapon_Reload` call with
  `intValue=1` (rack); stock magazine reload → `intValue=2/4` (attach / detach+attach). The
  trace decides this from evidence instead of the 1.13.2 docs.
- This tells us whether a future per-shell route could piggyback on an existing command or
  needs a distinct one; it does **not** prove ammo/magazine behaviour (that is T3) and does not
  add a per-shell path.

## 6. STOP / rollback

- No graph/ASI/clip/prefab/input/ammo changes were made; rollback = restore the previous lab
  script (the T2a/T2b version) and delete the regenerated `resourceDatabase.rdb`.
- If the override fails to compile (should not, per §1) or `[ARMST_T2C-CMD]` never appears,
  STOP and report; do not add further hooks.

## 7. Integrity

- Only the local lab script changed (no git remote for the lab). Knowledge repo holds only
  this report + index/sync pointers.
- Production Weapons dirty 29, Core dirty 4 (unchanged, owner work preserved).
