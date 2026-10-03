# MP-133 V3 — T4a: disposable `SetAmmoCount` semantics probe

**Status:** `T4A_LAB_PREPARED_OWNER_RUN_REQUIRED`.
New isolated lab only. Production Weapons/Core, frozen V2/P2, the T2A diagnostic and Astra's
graph lab are byte-identical. Source: Issue #27 comment 5970853781.

Labels: **SOURCE** (installed SDK / project file), **INFERENCE**, **UNRESOLVED**.

---

## 1. Goal & isolation

Prove **only** whether `BaseMagazineComponent.SetAmmoCount(int)` is a usable write primitive on
a **disposable, non-production, unattached** test magazine — no transfer, no donor, no player
inventory, no weapon/chamber mutation, no production edits. This does **not** validate an
installed magazine or engine replication (explicitly out of T4a scope).

New lab addon: `ARMSTMP133T4A_SetProbe` (**SOURCE** `addon.gproj`): `ID ARMSTMP133T4ASetProbe`,
`GUID A7C41E90D3B24F68`, dependencies `58D0FB3206B6F859` (base) + `6A70E400C54051DC` (Weapons).

---

## 2. Installed-SDK evidence (**SOURCE**)

| Item | Signature / location |
|---|---|
| Ammo read | `proto external int BaseMagazineComponent.GetAmmoCount()`, `GetMaxAmmoCount()` |
| Ammo write | `proto external void BaseMagazineComponent.SetAmmoCount(int ammoCount)` |
| Owning entity | `proto external IEntity BaseMagazineComponent.GetOwner()` |
| Component init | `ScriptComponent.OnPostInit(IEntity owner)` / `OnDelete(IEntity owner)` |
| Input listener | `Game.GetInputManager()` → `ActionManager.AddActionListener(string, EActionTrigger, ActionListenerCallback)` / `RemoveActionListener` |
| Custom action | project pattern `Configs/System/chimeraInputCommon.conf` (`Action …` + `ActionContext … ActionRefs +{ … }`) and `Configs/System/keyBindingMenu.conf` (Core: `ARMST_LIGHT_RELOAD_ACTION`) |

Setters are **not** assumed authoritative/persistent/replicated — this run is the test.

---

## 3. New lab files (allowlist) and GUIDs

| File | Purpose |
|---|---|
| `ARMSTMP133T4A_SetProbe/addon.gproj` | new lab project (`ARMSTMP133T4ASetProbe`, GUID `A7C41E90D3B24F68`) |
| `Scripts/Game/ARMST_T4A/ARMST_T4A_SetterProbe.c` | `ScriptComponent` probe (`[BaseContainerProps()]`, `OnPostInit`/`OnDelete`) |
| `Prefabs/Test/ARMST_T4A_TestMagazine.et` + `.et.meta` | disposable magazine; inherits `{B0DFDF7AAA9C5D39}…armst_12ga_Buckshot.et`; carries the probe |
| `Configs/System/chimeraInputCommon.conf` | action `ARMST_T4A_SETTER_ACTION` (default key **P**) added to `CharacterGeneralContext` |
| `Configs/System/keyBindingMenu.conf` | keybinding entry ("ARMST T4A" category) |

New GUIDs: test-mag meta `B8D52F01E4C35A79`, `.et` ID `C9E63012F5D46B8A`, probe component
`DAF7412306E57C9B`, action `EB08423417F68DAC`, source `FC19534528079EBD`, click-filter
`0D2A64563918AFCE`, keybind category `1E3B75674A29B0DF`, entry `2F4C86785B3AC1E0`.
All verified unique across the addon set (0 pre-existing collisions); new resources only.

---

## 4. Behaviour

- On component init: subscribe to `ARMST_T4A_SETTER_ACTION`; apply a **baseline** ammo to the
  disposable magazine from an owner-set attribute `m_iT4AStartAmmo` (0…max, default 0) — this is
  a setup write on the **disposable object only**, so the full case can be tested.
- On the action (default **P**): one guarded write, one-shot latch:
  - `# phase=pre` — logs identity tag + prefab + `ammo/max` + `used` + `srv`;
  - reject **without writing** if the magazine is missing, `already-used`, or `full`;
  - otherwise `SetAmmoCount(a+1)`, then `# phase=post` logs `want`, resulting `ammo/max`,
    `sameIdentity` (owner-entity reference unchanged) and `srv`.
- One write per component instance. Logs: `[ARMST_T4A-SETTER] #n phase=init|baseline|pre|post|reject …`.

No `modded`, no spawn/delete, no inventory, no donor, no chamber/weapon mutation, no RPC,
no auto-trigger.

---

## 5. Static checks

- Braces 16/16, parens 100/100, ASCII clean; no line with >9 `+`.
- Forbidden-call scan clean (`modded class`, `SpawnEntity`, `TryRemoveItem`, `TryInsertItem`,
  `Launch(`, `Rpc(`, `HandleWeaponFire`, `SetReloadWeapon`, `GetInventory` all 0).
- Script SHA-256 `7761C5EC70D863D118FB637F77260AAF9918A49A1136FD698982053B52AE22AF`.
- Unchanged: Weapons dirty 29, Core dirty 4; T2A script `E978EDAF…`; V2 `MP133_Lab.agf`
  `654B2437C5689D4D`. Agent cannot compile — **compilation is NOT verified**.

---

## 6. Owner run steps (owner-only)

1. Loadout: base engine + `ARMST-PLATFORM---Weapons` + **`ARMSTMP133T4A_SetProbe`**. Core and
   V2/P2 OFF. Recompile `Game` in Workbench; **STOP on any SCRIPT(E)** not in the base game.
2. In a test world, **place** `Prefabs/Test/ARMST_T4A_TestMagazine.et` (do not put it in the
   player inventory; do not attach it to any weapon). Confirm the `[ARMST_T4A-SETTER] #0
   phase=init … phase=baseline …` lines in the log.
3. Stand near the placed magazine; press the lab key (default **P**; rebind under
   Settings → Controls → "ARMST T4A" if needed).
4. **+1 case** (attribute `m_iT4AStartAmmo = 0`): expect `phase=pre ammo=0/10` →
   `phase=post … ammo=1/10 sameIdentity=1`. Press again → `phase=reject reason=already-used`.
5. **Full case**: set the placed component's `m_iT4AStartAmmo` to `10` (Workbench Properties),
   re-enter, press P → `phase=reject reason=full` (no write).
6. Inspect the item visibly and the log; send the full `[ARMST_T4A-SETTER]` excerpt, the exact
   loadout, and the observed ammo before/after.

Expected if `SetAmmoCount` works locally: `ammo` changes to `want`, `sameIdentity=1`, no third
entity, no SCRIPT(E). If the write has unexpected effects (identity change, wrong value, errors),
**STOP** and report — no retry.

## 7. Risks / UNRESOLVED

- Config merge of the lab `chimeraInputCommon.conf` with the base/Core one and keybind
  registration are **UNRESOLVED** until the owner compiles and the action fires.
- `SetAmmoCount` authority/persistence/replication are **UNRESOLVED**; a local disposable-mag
  result does **not** validate an installed magazine or multiplayer.
- Agent cannot compile/run: all runtime behaviour is **OWNER-RUNTIME** only.

## 8. Stop

`T4A_LAB_PREPARED_OWNER_RUN_REQUIRED`. STOP for owner Workbench/game evidence. Installed-mag
test, donor depletion, real transfer and MP authority remain separately authorised.
