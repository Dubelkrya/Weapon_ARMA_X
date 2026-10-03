# MP-133 V3 — T4a: disposable `SetAmmoCount` semantics probe

**Status:** `T4A_INTERACTION_PATCH_PREPARED_OWNER_RUN_REQUIRED`.
Isolated lab only. Production Weapons/Core, frozen V2/P2, the T2A diagnostic and Astra's
graph lab are byte-identical. Source: Issue #27 comments 5970853781 (T4a) and 5971080837
(interaction fix). Knowledge-repo changes are on branch `t4a/interaction-patch` (PR #31 is
concurrent; main untouched).

Labels: **SOURCE** (installed SDK / project file), **INFERENCE**, **UNRESOLVED**.

---

## 1. Why this patch

The first T4a lab exposed only a custom input action (key **P**) registered by a global
`AddActionListener` on each placed magazine. Owner run 1 proved only `phase=init` /
`phase=baseline`; no `phase=pre/post/reject`, and the owner could not interact with the
magazine. Two defects: (a) no **standard, discoverable interaction**, and (b) a **global**
listener per placed magazine would let one keypress mutate several instances. This patch
replaces the input-key approach with a **per-entity context interaction** and removes the
input config entirely.

## 2. New design (context interaction)

The disposable test magazine now carries an `ActionsManagerComponent` whose
`additionalActions` contains a `ScriptedUserAction` child — the standard Reforger pattern
(**SOURCE** Core loot prefab `Prefabs/LOOT_BOX/3_TIER/3_TIER_hidden_Loot_army.et`:
`ActionsManagerComponent { ActionContexts { UserActionContext … } additionalActions { ARMST_OpenStorageAction … } }`).

- Action label (**SOURCE** `GetActionNameScript`): **"T4a: add 1 test round"**.
- It appears in the normal interaction menu when the player is near / looks at the magazine
  (the `UserActionContext` + `Position` define the interaction point).
- `PerformAction(IEntity pOwnerEntity, IEntity pUserEntity)` operates on `GetOwner()` — the
  **specific magazine the player interacted with**, so only that instance is affected.
- One-shot guarded write: reject (`no-magazine` / `already-used` / `full`) without writing;
  otherwise `SetAmmoCount(current+1)` once, then re-read and compare identity.
- `CanBeShownScript`/`CanBePerformedScript` return true so the guards run and the reject
  reason is logged (a disabled action would be silent).
- Server-authoritative broadcast (`HasLocalEffectOnlyScript=false`, `CanBroadcastScript=true`),
  matching the project-proven user-action pattern.
- Baseline ammo (0…max) is still applied once by `ARMST_T4A_SetterProbe` on init from the
  owner attribute `m_iT4AStartAmmo` (disposable object only), so the full case is testable.

**Removed:** `Configs/System/chimeraInputCommon.conf` and `Configs/System/keyBindingMenu.conf`
(the key P approach) — no global input action/listener remains.

## 3. Installed-SDK evidence (**SOURCE**)

`ScriptedUserAction`: `void PerformAction(IEntity pOwnerEntity, IEntity pUserEntity)`;
`bool GetActionNameScript(out string outName)`; `bool GetActionDescriptionScript(out string outName)`;
`bool CanBeShownScript(IEntity user)`; `bool CanBePerformedScript(IEntity user)`;
`void Init(IEntity pOwnerEntity, GenericComponent pManagerComponent)`. `ActionsManagerComponent`
manages `ActionContexts` + `additionalActions`. Project example: `class ARMST_OpenStorageAction :
ScriptedUserAction` (no companion `Class`).

## 4. Files & GUIDs

| File | Purpose |
|---|---|
| `ARMSTMP133T4A_SetProbe/addon.gproj` | new lab project `ARMSTMP133T4ASetProbe`, GUID `A7C41E90D3B24F68`, deps base + Weapons |
| `Scripts/Game/ARMST_T4A/ARMST_T4A_SetterProbe.c` | `ARMST_T4A_SetterProbe` (baseline) + `ARMST_T4A_AddRoundUserAction` (context action) |
| `Prefabs/Test/ARMST_T4A_TestMagazine.et` + `.et.meta` | disposable magazine (inherits `{B0DFDF7AAA9C5D39}armst_12ga_Buckshot.et`) + `ActionsManagerComponent` + action + baseline component |

Prefab resource identity retained: meta `B8D52F01E4C35A79`, `.et` ID `C9E63012F5D46B8A`.
New GUIDs: probe `DAF7412306E57C9B`, ActionsManager `3A5D97896C4BD2F1`, context
`4B6EA89A7D5CE302`, point `5C7FBAAB8E6DF413`, action `6D80CBBC9F7E0524`. All verified unique
across the addon set (each 1 occurrence); new resources only.

## 5. Static checks

- Script: braces 22/22, parens 124/124, ASCII clean, no line with >9 `+`.
- Forbidden scan clean: `modded class`, `AddActionListener`, `SpawnEntity`, `TryRemoveItem`,
  `TryInsertItem`, `Launch(`, `Rpc(`, `HandleWeaponFire`, `SetReloadWeapon` all 0.
- Script SHA-256 `BE8EF1AF0869385F2C55E764A53F3E15C67524A93E3D89D9212D9A8B4FF8700A`.
- Unchanged: Weapons dirty 29, Core dirty 4; T2A script `E978EDAF…`; V2 `MP133_Lab.agf`
  `654B2437C5689D4D`. Agent cannot compile — **compilation/interaction NOT verified**.

## 6. Owner run steps (owner-only)

1. Loadout: base engine + `ARMST-PLATFORM---Weapons` + **`ARMSTMP133T4A_SetProbe`**; Core and
   V2/P2 OFF. Recompile `Game`; **STOP on any own/resource SCRIPT(E)**.
2. Place **one** `Prefabs/Test/ARMST_T4A_TestMagazine.et` in a test world (not inventory, not
   on a weapon). Confirm `[ARMST_T4A-SETTER] #0 phase=init … phase=baseline …`.
3. Walk up to the magazine and select the contextual action **"T4a: add 1 test round"** in the
   standard interaction menu.
4. **+1 case** (`m_iT4AStartAmmo=0`): expect `phase=pre ammo=0/10` → `phase=post … ammo=1/10
   sameIdentity=1`. Invoke again → `phase=reject reason=already-used`.
5. **Full case**: set the placed component's `m_iT4AStartAmmo=10` in Workbench Properties,
   re-enter, invoke the action → `phase=reject reason=full` (no write).
6. If several magazines are placed, confirm the log records **only the interacted instance**
   (one `entTag` per invocation).
7. Send the full `[ARMST_T4A-SETTER]` excerpt, loadout, and the visible ammo before/after.

## 7. Risks / UNRESOLVED

- Whether the `ActionsManagerComponent` + `additionalActions` action is **visible and
  invocable** in the running game is **UNRESOLVED** until the owner run (the loot prefab proves
  the pattern, not this entity).
- `SetAmmoCount` authority/persistence/replication are **UNRESOLVED**; a disposable-mag result
  does not validate an installed magazine or multiplayer.
- Agent cannot compile/run: all runtime behaviour is **OWNER-RUNTIME** only.

## 8. Stop

`T4A_INTERACTION_PATCH_PREPARED_OWNER_RUN_REQUIRED`. STOP for owner Workbench/game evidence.
Installed-mag test, donor depletion, real transfer and MP authority remain separately authorised.
