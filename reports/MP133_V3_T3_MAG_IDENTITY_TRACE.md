# MP-133 V3 — T3 passive physical-magazine identity trace (lab-only)

**Status:** `T3_LOGGING_ADDED; STATIC_PASS; OWNER_RUN_REQUIRED`.
Lab-only; production Weapons/Core, frozen V2/P2 and all graph/ASI/AST/AGR/AW/ANM/TXA/prefab/
meta files **unchanged**; Workbench/game NOT run by the agent. Source: Issue #27 comment
5970404708. This is the only authorised T3 change; no state-machine edit, no per-shell work.

---

## 1. Installed-SDK verification (done before editing)

Authorities = installed Tools docs, not the online pages
(`C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs\
ArmaReforgerScriptAPIPublic\html\`). Confirmed signatures (read-only getters only):

| Method | Return | Source doc |
|---|---|---|
| `BaseWeaponComponent.GetCurrentMagazine()` | `BaseMagazineComponent` | `interfaceBaseWeaponComponent.html` |
| `BaseWeaponComponent.GetCurrentMuzzle()` | `BaseMuzzleComponent` | same |
| `BaseWeaponComponent.GetOwner()` | `IEntity` | same |
| `BaseWeaponComponent.IsChamberingNecessary()/IsChamberingPossible()` | `bool` | same |
| `BaseMagazineComponent.GetAmmoCount()/GetMaxAmmoCount()` | `int` | `interfaceBaseMagazineComponent.html` |
| `BaseMagazineComponent.GetOwner()` | `IEntity` | same |
| `BaseMuzzleComponent.GetAmmoCount()/GetMaxAmmoCount()/GetCurrentBarrelIndex()` | `int` | `interfaceBaseMuzzleComponent.html` |
| `BaseMuzzleComponent.IsChamberingPossible()` | `bool` | same |

`WeaponAnimationComponent` inherits `BaseItemAnimationComponent`; `GetOwner()` is available.
`WeaponComponent` (the concrete prefab component) inherits `BaseWeaponComponent`. The T2c
`OnCharacterCommand(int,int,float)` and `OnAnimationEvent(...)` callbacks are present.

---

## 2. What was added (one file, passive)

`ARMSTMP133T2A_Diag/Scripts/Game/ARMST_MP133_T2A/ARMST_MP133_T2A_Log.c` — inside the existing
`ARMST_T2A_WeaponAnimationComponent` (**no second gameplay file touched**):

- new T3 fields (event IDs, sequence counter, baseline flag, reference-tag state);
- `T3EventName(id)` resolves the targeted events via the SDK;
- `T3Snapshot(phase, ev, t)` prints one line;
- `T3Final()` prints the delayed final sample;
- `OnAnimationEvent` now emits, for targeted events only:
  **baseline (once) → pre-super → super → post-super**, and a **final** sample 250 ms after
  `BlendOut` (`CallLater`, passive).
- The targeted-event logging is **independent and uncapped** (its own `#n` counter), so the
  existing 30-line generic weapon cap cannot suppress late native events.
- T2a/T2b markers and the T2c `OnCharacterCommand` trace are **unchanged**; `super` is always
  called for both callbacks.

Snapshot line (example):
```
[ARMST_T3-MAG] #n phase=baseline|pre-super|post-super|final ev=<name> t=<s> srv=<0|1>
  wpnTag=Wn wep=<prefab> magTag=Mn mag=<prefab> ammo=<a>/<m>
  muzzle=<a>/<m> barrel=<i> chNeed=<0|1> chPoss=<0|1> mzChPoss=<0|1>
```
- `wpnTag`/`magTag` are **per-test reference-comparison tags** (W1/M1, M2 …): they change only
  when the weapon/magazine **owning entity reference** changes — never prefab GUIDs. The
  current magazine is obtained via `WeaponComponent.GetCurrentMagazine()` and its owning
  `IEntity` is `BaseMagazineComponent.GetOwner()`.
- `ammo` = `GetAmmoCount()/GetMaxAmmoCount()` of the current magazine; `muzzle`/`barrel`/
  `chNeed/chPoss/mzChPoss` describe the chamber/barrel state (getters only).

---

## 3. Static checks — PASS

- Braces 30/30, parens 210/210, ASCII clean.
- `super.OnAnimationEvent(...)` and `super.OnCharacterCommand(...)` still called; override
  signatures unchanged.
- No disallowed calls: `SetAmmoCount`, `SetMaxAmmoCount`, `Delete`, `SpawnEntity`,
  `CreateEntity`, `SetReloadWeapon`, `ReloadWeapon(`, `AddActionListener`,
  `HandleWeaponReloading`, `HandleWeaponFire`, `Rpc(`, `RpcDo_`, inventory access — all absent.
- Stale `resourceDatabase.rdb` removed so Workbench rescans.
- Lab script hash: before (T2c) `03AE04C6191370E1DF616D701E8FB8BAC4371B8E4347602F820FC60880FE96D1`
  → after (T3) `A66B4CCFABF6100F0B5168ACD42290D6B9E7C0C4E64619A8AEC139D7BE0CB00A`.

---

## 4. Unchanged-set verification

- 23-file asset set (production + T2A graph/ASI/clip/prefab): **pre == post**.
- Frozen V2 lab graph/ASI hashes unchanged (`MP133_Lab.agf 654B2437C5689D4D`, `.agr
  23A31D89D3B209E7`, `.ast 53F33E08C5824FB4`, `.aw B3D7EB1F88C4E840`, player `DDE9C574CA3C1F7B`,
  weapon `0DC0C20940D0E96F`).
- Weapons dirty ≈ 29, Core dirty ≈ 4 (owner work preserved).

---

## 5. Owner run (ONE native R magazine swap)

1. Loadout: base + `ARMST-PLATFORM---Weapons` + `ARMSTMP133T2A_Diag`; Core and V2/P2 OFF.
2. Recompile `Game` in Workbench (lab script changed; rdb removed).
3. Equip the diagnostic `MP-133 [T2A-DIAG]`.
4. Prepare an **old, partly depleted** magazine (e.g. 7/10) in the weapon and a **separate
   known full 10/10** magazine in inventory; note the actual chamber before the test.
5. Perform **ONE** native R magazine swap (expected `commandID=0,intValue=5`): no extra racks,
   no second reload during capture.
6. Capture the **full** log (not just the first 30 WPN lines); filter `ARMST_T2C-CMD` +
   `ARMST_T3-MAG`. Also record the visible HUD/chamber and the inventory old/new magazine
   counts after the swap.

---

## 6. Read-out / evaluation (prove, don't assume)

- Does `magTag` transition **M1 → M2** and does `WeaponComponent.GetCurrentMagazine()` change
  representative entity? (docs: `SOURCE`; observation: `OWNER-RUNTIME`).
- Does the **M1** old magazine remain (partial) in inventory? (If the component has no
  read-only inventory API for it → report `UNRESOLVED` and use the owner's visual inventory
  observation; do not add global hooks or mutate inventory.)
- Do `ammo`/`muzzle`/`barrel` change and at which snapshot (pre/post-super/final)? Correlate
  with delivered event names.
- **Event-mutation causality stays `UNRESOLVED`** unless the snapshots support it — adjacency
  in the log is not proof that an event causes the change.

**Limits recorded up front:** the native `Weapon_*Magazine` events may not be delivered to the
weapon-side `OnAnimationEvent` callback at all; the trace will show whether they are (if not,
only `BlendIn/BlendOut` + `final` snapshots appear). No claim is made here that a per-shell
path or ammo conservation works.

## 7. STOP / rollback

- One native R only; STOP after the owner sends the T3 log. Sanitised clips, `GrabShell/
  InsertShell` graph design, bridge, per-shell commit, input interception and native cmd-7
  work all require **new separate owner approval**.
- Rollback = restore the previous lab script (T2c hash) and delete the regenerated rdb.

## 8. Integrity

Only the local lab script changed (lab has no remote). Knowledge repo holds this report +
minimal index/sync pointers only. No agent Workbench/game run.
