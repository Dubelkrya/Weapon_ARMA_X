# CORE (ARMST-PLATFORM---Core) — read-only audit for MP-133 V3

> **Status: `CORE_READONLY_AUDIT_READY_FOR_REVIEW`** (static, read-only).
> Owner task: Issue #33 and its owner-confirmation comment `5971525177`.
> Mode: strictly read-only. No game/Workbench launch, no compile, no edits to
> Core / Weapons / MP-133 / labs / Astra. The only file this audit created is
> this report.
>
> **Runtime honesty:** nothing here is `OWNER_RUNTIME_VERIFIED` unless it is an
> owner statement already recorded elsewhere. This audit cannot and does not
> claim that any Core mechanism works in-game.

---

## 0. TL;DR

- The **legacy SHIFT+R path is real source and config, but it is not a working
  reload.** `ARMST_LIGHT_RELOAD_ACTION` (= `KC_R` + `KC_LSHIFT`) is defined and
  wired into `CharacterGeneralContext`; `OnRackBoltMDown` is registered and
  routes to `TAO_DecrementAmmoOnRack` / `TAO_ClearChamberIfNoMagOrEmpty`. The
  owner has explicitly ruled this out as functional (§9). Classify it as
  **legacy/inactive**, not as a Core feature to preserve.
- The single most MP-133-relevant Core system is **`MagazineRepack`**: a
  server-authoritative, RPC-driven, inventory-validated **donor magazine → target
  magazine** ammo transfer with donor consumption and cleanup. It is an
  *approach* worth reusing for T4/T5, **not** code to copy, and it still proves
  no atomic per-shell API exists.
- Core depends on **Weapons** (`addon.gproj` lists `6A70E400C54051DC`), so loading
  Core loads Weapons. Weapons does **not** depend on Core. T2A/T4A labs (no Core)
  therefore cannot use Core mechanisms.
- `ARMST_SHOTGUN_COMPONENTS` is attached to **no prefab and no config** — its
  whole "trim a full magazine down to `m_MaxMagazineAmmo`" path is dead code.
- Two broad global hooks (`modded class SCR_CharacterControllerComponent`,
  `modded class SCR_InventoryMenuUI`) plus two R-overlapping actions are a **real,
  unresolved interference risk** for native R. Core was *not* loaded during the
  T0 clean pass, so this is untested.

---

## 1. Access verification (no `CORE_SOURCE_UNAVAILABLE`)

| Check | Result |
|---|---|
| Path | `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Core` |
| `addon.gproj` | present |
| `addon.gproj` `ID` | `ARMSTPLATFORMCore` |
| `addon.gproj` `GUID` | `69E4C3542B6CDC19` |
| `addon.gproj` `TITLE` | `ARMST PLATFORM - Core 2.5` |
| Local branch / HEAD | `main` = `08cb1f389b16fe552c4b66caac64da2e7f4a65d6` |
| `Scripts/` real | 254 files (`243 .c`, `9 .md`, `2 .txt`), ≈2.44 MB |

Access is present — no blocker. Note that `git` and `gh` are **not installed** in
this environment, so HEAD was read directly from `.git` (§12), and git
`status`/diff could not be produced.

---

## 2. Evidence vocabulary

| Tag | Meaning |
|---|---|
| `SOURCE_PRESENT` | The class/method/file exists on disk. |
| `REFERENCED_BY_ACTIVE_RESOURCE` | A prefab/config that the addon loads actually names it. |
| `COMPILES_OWNER_VERIFIED` | Owner/Workbench has confirmed it compiles. **Not** established by this audit. |
| `OWNER_RUNTIME_VERIFIED` | Owner observed behaviour in-game. Only quoted from existing records. |
| `LEGACY/INACTIVE` | Present, but not a functioning/used mechanic. |
| `UNRESOLVED` | Cannot be decided statically; needs a controlled owner test. |

Static presence is never treated as an active game mechanic.

---

## 3. Core shape (inventory)

| Tree | Files |
|---|---|
| `Configs/` | 669 |
| `Prefabs/` | 3,933 |
| `Scripts/` | 254 |
| `Scripts/Game/MUTANTS` | 50 |
| `Scripts/Game/UI` | 24 |
| `Scripts/Game/UserActions` | 21 |
| `Scripts/Game/DataBase` | 19 |
| `Scripts/Game/Inventory` | 18 |
| `Scripts/Game/SCR_Player` | 14 |
| `Scripts/Game/Player` | 13 |
| `Scripts/Game/Editors` | 13 |
| `Scripts/Game/Configs` | 12 |
| `Scripts/Game/Anomaly` | 11 |
| `Scripts/Game/TRIGGER` | 10 |
| `Scripts/Game/Items` | 10 |
| (others) | ALIFE 5, Devices 5, Artefacts 4, Animations 4, Damages 2, Camera 2, Dialogs 2, VLST_Code 2 |

Core is a **whole platform mod**, not a weapon helper: mutants, anomalies,
ALIFE, database/PDA/saves, traders, factions, quests, editor tooling, UI, poses.
The MP-133-interesting surface is a small subset: `Items/`, `Inventory/`,
`UserActions/`, `Animations/`, `SCR_Player/`, `Player/`, and the input configs.

---

## 4. Weapon handler — `Scripts/Game/Items/ARMST_WEAPONS_HANDLER.c`

Contains several distinct mechanisms:

1. **`ARMST_12g_SpreadEffect : BaseProjectileEffect`** — custom shotgun pellet
   spawning (`GetGame().SpawnEntityPrefab` + `ProjectileMoveComponent.Launch`).
   `SOURCE_PRESENT`; reference in a config not established here.
2. **`ARMST_SHOTGUN_COMPONENTS : ScriptComponent`** with attribute
   `m_MaxMagazineAmmo` — `SOURCE_PRESENT` but **attached to no `.et`/`.conf`**
   (`ARMST_SHOTGUN_COMPONENTS` has 0 matches in `Prefabs/**` and
   `Configs/**`). Its magazine-trimming logic (`WeaponHandler`, lines ~463–530:
   `SetAmmoCount(max)`, spawn an overflow magazine prefab, insert it into the
   inventory) is therefore **dead / `LEGACY`**.
3. **`modded class SCR_WeaponInfo`** — on `OnAmmoCountChanged`, calls
   `RequestWeaponHandler` (server RPC) and, when the weapon's
   `ARMST_ITEMS_STATS_COMPONENTS` condition is low, rolls a jam chance and calls
   `OnRackBoltMDown()`. `SOURCE_PRESENT`, condition-driven, tied to the legacy
   rack path.
4. **`modded class SCR_CharacterControllerComponent`** (the important one):
   - `OnInit`: registers animation event `Weapon_Rack_Bolt` and subscribes
     `OnAnimEvent_RackBoltCaseEject` to `GetOnAnimationEvent()`.
   - `OnAnimEvent_RackBoltCaseEject`: if server-master and
     `m_ServerManualRackPending`, calls `TAO_DecrementAmmoOnRack()` +
     `TAO_ClearChamberIfNoMagOrEmpty()`, then sets a ~220 ms cooldown.
   - `RpcAsk_TAO_ManualRack` (`[RplRpc(RplChannel.Reliable, RplRcver.Server)]`):
     debounced server request; schedules a `CallLater` fallback (~6 × 30 ms) if
     the AnimEvent never arrives.
   - `TAO_DecrementAmmoOnRack`: `mag.SetAmmoCount(Math.Max(count - 1, 0))` on the
     **current installed magazine**.
   - `TAO_ClearChamberIfNoMagOrEmpty`: `muzzle.ClearChamber(muzzle.GetCurrentBarrelIndex())`
     when no mag / empty mag and the barrel is chambered.
   - `OnRackBoltMDown`: client-side guard against `IsReloading()`, ~220 ms
     cooldown, `Rpc(RpcAsk_TAO_ManualRack)`, then
     `inputCtx.SetReloadWeapon(1)`.
   - `RequestWeaponHandler` / `RpcAsk_WeaponHandler` / `WeaponHandler`: server
     authority + condition damage + the dead shotgun trim.

**Classification:** `SOURCE_PRESENT`; reachable only through the legacy
SHIFT+R input; owner says non-functional → **`LEGACY/INACTIVE`** as a feature.
The individual *APIs* it demonstrates (`SetAmmoCount` on the installed mag,
`ClearChamber`, server RPC + pending/cooldown/fallback) are valid and reusable
as patterns (§8).

---

## 5. Inventory / item transfer / authority

### 5.1 `Scripts/Game/SCR_Player/ARMST_SCR_PlayerMagRepacks.c` — **donor→mag transfer**

`modded class SCR_PlayerController` adds:

- `MagazineRepack(fromMag, toMag, manager, invTo, invFrom)` — **server only**
  (`if (!Replication.IsServer() || fromMagazine == toMagazine) return;`):
  - requires both magazines, both `GetMagazineWell()` non-null, equal well
    `Type()`, `fromAmmo > 0`, `toAmmo < maxAmmo`;
  - moves `space = max - to`:
    `toMag.SetAmmoCount(to + from)` / `fromMag.SetAmmoCount(0)`, or partial;
  - if donor reaches 0: `manager.TryRemoveItemFromInventory(fromEntity)`, else
    `SCR_EntityHelper.DeleteEntityAndChildren(fromEntity)`.
- `MagazineRepack_Request(...)` — `Rpc(MagazineRepack_RPC, …Ids…)`.
- `MagazineRepack_RPC(...)` — `[RplRpc(RplChannel.Reliable, RplRcver.Server)]`,
  resolves entities via `Replication.FindItem(id)` then calls `MagazineRepack`.

### 5.2 `Scripts/Game/Inventory/ARMST_SCR_InventoryMenuUI.c` — UI trigger

`modded class SCR_InventoryMenuUI` overrides `MoveItemToStorageSlot()` to try a
repack first; `TryMagazineRepackSlots` does the client-side validation
(magazine well present/type match, capacity, `IsStorageArsenal` guard) and then
calls `pc.MagazineRepack(...)` on a listen server or
`pc.MagazineRepack_Request(...)` from a client.

**Classification:** `SOURCE_PRESENT` + `REFERENCED_BY_ACTIVE_RESOURCE` (the
`SCR_InventoryMenuUI` override is an active UI path). This is a **real,
server-authoritative, inventory-validated donor→target magazine transaction.**
It is the strongest candidate for *approach* reuse in T4/T5 (§8.2).

### 5.3 `Scripts/Game/Items/ARMST_ITEMS_STATS_COMPONENT.c`

- Attached broadly (`ARMST_ITEMS_STATS_COMPONENTS` appears in many character /
  item prefabs) → `REFERENCED_BY_ACTIVE_RESOURCE`.
- `DeleteEmpty()` (server `OnPostInit` → `CallLater(…, 5000)`): if the owner has
  a `BaseMagazineComponent` with `GetAmmoCount() <= 0`, deletes the entity. This
  is a **magazine cleanup** hook relevant to donor lifecycle.
- Database-driven stats/weights/prices; server-gated mutations.

### 5.4 Item grant / consume primitives used across Core

`SCR_InventoryStorageManagerComponent.TryInsertItem(...)`,
`TryRemoveItemFromInventory(...)`, `SCR_EntityHelper.DeleteEntityAndChildren(...)`,
`GetGame().SpawnEntityPrefab(...)` appear throughout (loot, quests, traders,
artefacts, shelters). Standard, `SOURCE_PRESENT` / active in their own systems.

---

## 6. One-shot actions on a specific entity (`UserActions/`)

Pattern observed in `ARMST_USER_PUT_ARTEFACT`, `ARMST_OpenStorageAction`,
`ARMST_USER_LOOT_BODY`, etc.: `class X : ScriptedUserAction` with
`GetActionNameScript(out string)`, `CanBeShownScript(IEntity user)`,
`PerformAction(IEntity pOwnerEntity, IEntity pUserEntity)`, and for inspection
`SCR_InspectionUserAction`. These are attached to active prefabs as
`<ClassName> "{GUID}" { ... }` blocks inside an `ActionsManagerComponent`
(e.g. `ARMST_USER_PUT_ARTEFACT` on artefact-drop prefabs,
`ARMST_USER_LOOT_BODY` on character prefabs) →
`REFERENCED_BY_ACTIVE_RESOURCE`.

`Scripts/Game/UserActions/ARMST_AttachementAction.c` additionally shows an
**async inventory operation with a completion callback**:
`class ARMST_AttachementActionCallback : ScriptedInventoryOperationCallback`
with `OnComplete()` / `OnFailed()`, and a `m_ARMST_Removing` re-entrancy guard.
This is a reusable pattern for "operate on entity X, continue only on success,
roll back otherwise" (§8.4).

---

## 7. Animations / command handler

- `Scripts/Game/Animations/ARMST_STATIC_ANIMATION.c` uses
  `SCR_CharacterControllerComponent.GetAnimationComponent().GetCommandHandler()`
  and `SCR_CharacterCommandHandlerComponent.GetScriptedStaticTable()` +
  `StartLoitering(...)`; server-gated pose sync via
  `Rpc_ApplyPoseToClients` (`[RplRpc(Reliable, Broadcast, RplCondition.NoOwner)]`).
- `ARMST_PLAYER_ANIMATION` is attached on `Prefabs/Factions/Character_Base.et`.
- These are **pose/cinematic** mechanisms, not weapon reload. `SOURCE_PRESENT` +
  `REFERENCED_BY_ACTIVE_RESOURCE`.

> Note: `SCR_CharacterCommandHandlerComponent` appears here, but Core does **not**
> define a global `modded SCR_CharacterCommandHandlerComponent` — the P2 global
> handler that broke ordinary R was in the **frozen V2 lab**, not in Core. Keep
> that distinction.

---

## 8. What is potentially reusable for MP-133 V3 (approaches, not code)

The task explicitly asks for reuse of **approaches**. Findings:

### 8.1 Installed-magazine ammo writer (already known from T4)
`BaseMagazineComponent.SetAmmoCount(int)` is the only ammo writer — confirmed in
the installed SDK docs (§10). Core's `TAO_DecrementAmmoOnRack` writes to
`wpn.GetCurrentMagazine()`, i.e. the **already-installed** magazine, which matches
the T2c owner finding that V3 must operate on the installed magazine.

### 8.2 Donor→target transfer transaction — **the key reusable approach**
`ARMST_SCR_PlayerMagRepacks.c` + `ARMST_SCR_InventoryMenuUI.c` demonstrate a full
transaction shape that T4/T5 can mirror:

1. client validation (compatibility / capacity),
2. `[RplRpc(Reliable, Server)]` request with stable `RplId`s
   (`Replication.FindId` → `Replication.FindItem`),
3. server re-validation,
4. `SetAmmoCount` arithmetic that consumes the donor and respects capacity,
5. donor cleanup (remove from inventory or delete).

**Hard limit — do not overclaim:** this transfers between two existing magazine
*entities* with matching `MagazineWell`. Core contains **no** loose-shell →
magazine, no donor-shell spawning, and no atomic transfer API. T4's
`T4_API_OR_TRANSACTION_BLOCKED` conclusion for an *atomic* transfer still stands;
Core supplies a **scripted transaction pattern**, not a native atomic primitive.

### 8.3 Server authority + once-only commit + safe stop
`ARMST_WEAPONS_HANDLER.c`'s `m_ServerManualRackPending` + cooldown +
`GetGame().GetCallqueue().CallLater(...)` fallback, and `RpcAsk_*` guards, are a
template for: request → authoritative gate → exactly-once commit → cancel/stop.
Reusable shape for per-shell commit and safe-stop semantics.

### 8.4 Async inventory callback for rollback
`ScriptedInventoryOperationCallback.OnComplete/OnFailed`
(`ARMST_AttachementAction.c`) is the closest thing to a rollback hook. Worth
checking whether it can gate a once-only per-shell commit. `UNRESOLVED` — needs
SDK/owner confirmation of atomicity semantics.

### 8.5 Inventory presence & donor lookup
`SCR_InventoryStorageManagerComponent` (`TryInsertItem`,
`TryRemoveItemFromInventory`, `FindStorageForItem`, `CanMoveItemToStorage`) plus
`B_PrefabNamePredicate` (`InventorySearchPredicate`) show how to find a specific
prefab's item instance in inventory — usable to locate a legal donor ammo source.
`TryInsertItem`/`TryRemoveItemFromInventory` signatures confirmed in §10.

### 8.6 Chamber APIs for safe stop
`BaseMuzzleComponent.IsCurrentBarrelChambered()`,
`GetCurrentBarrelIndex()`, `ClearChamber(int)` — confirmed in §10; already used by
`TAO_ClearChamberIfNoMagOrEmpty`.

### 8.7 One-shot entity action
`ScriptedUserAction` (`PerformAction(pOwnerEntity, pUserEntity)`) attached to a
prefab is a clean **"single action on a specific entity"** mechanism (explicitly
requested by the task). It is a candidate for a dedicated load action or for
diagnostics, **not** a replacement for a short-R input.

> The task asks to state plainly if there is no legal donor→mag transfer: there
> **is** a magazine-to-magazine transfer pattern (8.2), but **there is no
> legitimate loose-shell donor / per-shell transfer primitive anywhere in Core**.

---

## 9. SHIFT+R verdict (owner correction, encoded)

`Configs/System/chimeraInputCommon.conf`:

- `Action ARMST_LIGHT_RELOAD_ACTION` — combo `keyboard:KC_R` +
  `keyboard:KC_LSHIFT` (line ~113).
- Added to `ActionContext CharacterGeneralContext` (line ~221).
- `Configs/System/keyBindingMenu.conf` maps it (`m_sActionName
  "ARMST_LIGHT_RELOAD_ACTION"`).
- `Scripts/Game/Player/ARMST_PLAYER_CharacterController.c` registers
  `inputMgr.AddActionListener("ARMST_LIGHT_RELOAD_ACTION", EActionTrigger.DOWN,
  OnRackBoltMDown)` on `OnControlledByPlayer`.

So the wiring is `SOURCE_PRESENT` + `REFERENCED_BY_ACTIVE_RESOURCE`, **but** the
owner states there is no working reload through SHIFT+R (Issue #33). Therefore:

- **Do not treat `ARMST_LIGHT_RELOAD_ACTION`, `OnRackBoltMDown`, or a "frozen
  LSHIFT+R behaviour" as a Core feature or a requirement to preserve.**
- Classification: `LEGACY/INACTIVE` (owner-reported non-functional). The exact
  runtime failure cause is `UNRESOLVED` (not tested here).

### 9.1 Static defects found in the legacy path (report only, not fixed)
- `ARMST_PLAYER_CharacterController.c` `OnControlledByPlayer`: only the first
  `AddActionListener` is inside `if (inputMgr)`; the remaining 9 run
  unconditionally (missing braces). Same shape in the removal branch.
- Removal branch uses `"ARMST_NVG_UP_ACTION1"` / `"ARMST_NVG_DOWN_ACTION1"` while
  registration uses `"ARMST_NVG_UP_ACTION"` / `"ARMST_NVG_DOWN_ACTION"` → those
  listeners are never removed (leak).
- `ARMST_CHECK_AMMO_ACTION` (`KC_R` + `KC_LCONTROL`) and
  `ARMST_LIGHT_RELOAD_ACTION` (`KC_R` + `KC_LSHIFT`) both live in
  `CharacterGeneralContext` alongside native `R`; if the listeners fire on the
  same physical input, native R handling is at risk (see §11).

---

## 10. Signatures checked against the installed SDK

SDK docs root:
`C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs\ArmaReforgerScriptAPIPublic\html`
(Steam tools build `buildid 24870687`; the owner/task reference this as Enfusion
1.8.0.13). Signatures confirmed from the generated HTML:

| Symbol | Installed-SDK signature |
|---|---|
| `BaseMagazineComponent.SetAmmoCount` | `proto external void SetAmmoCount(int ammoCount)` |
| `BaseMagazineComponent.GetAmmoCount` | `proto external int GetAmmoCount()` |
| `BaseMagazineComponent.GetMaxAmmoCount` | `proto external int GetMaxAmmoCount()` |
| `BaseMagazineComponent.GetMagazineWell` | `proto external BaseMagazineWell GetMagazineWell()` |
| `CharacterInputContext.SetReloadWeapon` | `proto external void SetReloadWeapon(int ReloadType)` |
| `BaseMuzzleComponent.ClearChamber` | `proto external bool ClearChamber(int barrelIndex)` |
| `BaseMuzzleComponent.IsCurrentBarrelChambered` | `proto external bool IsCurrentBarrelChambered()` |
| `BaseMuzzleComponent.GetCurrentBarrelIndex` | `proto external int GetCurrentBarrelIndex()` |
| `InventoryStorageManagerComponent.TryInsertItem` | `proto external bool TryInsertItem(IEntity item, EStoragePurpose purpose = PURPOSE_ANY, InventoryOperationCallback cb = null)` |
| `InventoryStorageManagerComponent.TryRemoveItemFromStorage` | `proto external bool TryRemoveItemFromStorage(IEntity item, BaseInventoryStorageComponent storage, InventoryOperationCallback cb = null)` |
| `SCR_InventoryStorageManagerComponent.TryRemoveItemFromInventory` | present (`interfaceSCR__InventoryStorageManagerComponent.html`) — Core calls `manager.TryRemoveItemFromInventory(fromEntity)` |
| `SCR_EntityHelper.DeleteEntityAndChildren` | `static void DeleteEntityAndChildren(IEntity entity)` |

Not documented in the public API HTML (engine-level; used by vanilla and Core,
signature source = Core/vanilla usage, not the public class index): `RplRpc`,
`RplRcver`, `RplCondition`, `Replication.IsServer/FindId/FindItem/BumpMe`.
Do not cite these as "SDK-doc-verified".

---

## 11. Risks for MP-133

1. **Core → Weapons dependency.** `ARMST-PLATFORM---Core/addon.gproj`
   dependencies include `6A70E400C54051DC` which is
   `ARMST-PLATFORM---Weapons`. Loading Core therefore pulls Weapons. Weapons'
   own dependencies (`58D0FB3206B6F859`, `6922BE16974B3AED`) do **not** include
   Core. Consequence: research labs built *without* Core (T2A, T4A) cannot use
   Core mechanisms; conversely any Core-inclusive test drags the full Weapons
   addon.
2. **Global `modded SCR_CharacterControllerComponent` (two Core files).** This is
   a broad global hook of the same class the P2 lab regression implicated (P2
   was a global `modded SCR_CharacterCommandHandlerComponent`; different class,
   similar blast radius). The T0 clean pass excluded Core, so
   "Core × native R on pumps" is **`UNRESOLVED`**. A controlled, owner-run A/B
   (Core loaded vs not) is the only way to settle it.
3. **`modded class SCR_InventoryMenuUI`** globally changes item drag semantics
   (any two magazines auto-repack). Side effect on unrelated inventories is
   possible.
4. **R-overlapping actions** (`R+CTRL`, `R+LSHIFT`) in the same context as native
   `R` — see §9.1.
5. **Dead `ARMST_SHOTGUN_COMPONENTS`** — if a future MP-133 path is meant to use
   it, it is currently attached to nothing.

---

## 12. Git state (read directly from `.git`; `git` binary unavailable)

| Repo | HEAD / branch | Local ref | Remote ref | Note |
|---|---|---|---|---|
| `ARMST-PLATFORM---Core` | `main` | `08cb1f389b16fe552c4b66caac64da2e7f4a65d6` | loose `origin/main` = `cc8035f228040ae84567819d8f5f6dece62789ef`; packed = `877383a4…` | **local ≠ remote → divergence recorded, nothing overwritten** |
| `ARMST-PLATFORM---Core` | — | `refs/stash` = `75eda2e4ce303efe8c54fb634f9fda83cfaa9e46` | — | an existing stash is present; **not touched** |
| `ARMST-PLATFORM---Core` | remote branches | — | `main`, `zombie` | — |
| `Weapon_ARMA_X` | **checked-out branch** = `t4b/installed-mag-probe` | `main` = `bcf3ab41c5aec230ae3a5333ed1ca40678e51d30` | loose `origin/main` = `bcf3ab41…`; packed = `dc12d9a9…` | working repo is on the T4b branch, not `main` |
| `Weapon_ARMA_X` | remote branches (GitHub API) | — | `main`, `docs/knowledge-handoff-20261003`, `t4a/interaction-patch`, `t4b/installed-mag-probe` | **no Core-research branch exists** |

Per the task, the Core-report branch should be a *new* isolated branch. That
could not be created because no git/gh client and no authenticated write path is
available (§13).

---

## 13. Publication status

- **`git` is not installed** (searched PATH, `C:\Program Files\Git\**`,
  `C:\Program Files (x86)\Git\**`, `%LOCALAPPDATA%\Programs\Git`, scoop,
  chocolatey, `C:\Git`, `C:\tools`, msys64 — none found).
- **`gh` is not installed.** Authenticated GitHub write could not be performed
  through the CLI.
- The public GitHub API is reachable for reads only from this session
  (branch list enumerated); unauthenticated writes (branch/PR/file) are not
  possible, and no token was found.
- The browser's GitHub session is **not authenticated** (checked 2026-10-03:
  `meta[name="user-login"]` empty, page shows "Sign in", no avatar), so the
  GitHub Web UI also cannot create the branch/PR.
- Therefore the report is **saved locally only** at
  `Weapon_ARMA_X/reports/CORE_ARMST_READONLY_AUDIT.md`.
- **No branch was created. No PR was opened. Nothing was merged into `main`.**
  This must not be reported as published.

To publish (owner action, or an agent with git + credentials): create a branch
from the current knowledge-repo base (suggest e.g.
`research/core-readonly-audit-20261003`), commit only
`reports/CORE_ARMST_READONLY_AUDIT.md`, open a PR to `main`, and reconcile with
open PR #31 and the T4a branch so neither is overwritten.

---

## 14. Read-only proof

The set consumed by this audit (Core `*.c *.conf *.et *.meta *.layer *.gproj`
plus the consumed Weapons `*.et *.meta` under MP-133 / 12ga / Magazines) was
hashed before and after. Manifest:
`Weapon_ARMA_X/artifacts/core_audit/protected_manifest_before.txt`
(git-ignored scratch).

| Metric | Value |
|---|---|
| Files hashed | 5570 |
| Aggregate SHA256 (before) | `064719B65EB60A26BC2E5E86E6C1BF517D8C9AA6BA326C4A8BF3A37438520861` |
| Aggregate SHA256 (after) | `064719B65EB60A26BC2E5E86E6C1BF517D8C9AA6BA326C4A8BF3A37438520861` |
| `GAMEPLAY_FILES_CHANGED_BY_AUDIT` | **0** |
| `META_FILES_CHANGED` | 0 |
| `GUID_CHANGES` | 0 |

No `reset`, `stash`, `restore`, `clean` or any destructive git command was run.

---

## 15. Doc corrections proposed (NOT applied)

1. Any claim that **Core provides a working SHIFT+R reload** should be removed or
   replaced with "legacy experiment, owner-reported non-functional; see
   `CORE_ARMST_READONLY_AUDIT.md`".
2. `MP133_INDEX.md` / `CURRENT_AI_SYNC.md` — update the "Core interaction" row:
   T0 excluded Core; Core's global `modded SCR_CharacterControllerComponent` and
   R-overlapping actions are `UNRESOLVED` interference risks, and Core depends on
   Weapons.
3. Add a note that `ARMST_SHOTGUN_COMPONENTS` is attached to no prefab/config
   (dead code) and that the only real Core donor→mag mechanism is
   `MagazineRepack`.

These edits were **not** made; they need the owner's allowlist.

---

## 16. Questions for a separate, owner-run check (no implementation)

1. Does loading Core change native `R` behaviour on MP-133 / other pump shotguns
   versus Weapons-only? (Controlled A/B; the P2 lesson.)
2. Why does owner describe `ARMST_LIGHT_RELOAD_ACTION`/`OnRackBoltMDown` as
   non-functional? Does the `Weapon_Rack_Bolt` AnimEvent fire at all on the
   installed engine?
3. Does `MagazineRepack` accept the MP-133 magazine
   (`{B0DFDF7AAA9C5D39}Prefabs/Weapons/Magazines/12ga/armst_12ga_Buckshot.et`) —
   i.e. does it expose a compatible non-null `GetMagazineWell()`?
4. Is `ScriptedInventoryOperationCallback` atomic enough for a once-only
   per-shell commit + rollback?
5. Can a `ScriptedUserAction` load action coexist with native R without the
   global-hook regression?

## 17. Explicit non-goals respected

No feature development, no Core fixes, no new labs, no T4a replacement, no Astra
launch, no edits to Core/Weapons/MP-133/labs, no copying of Core sources into
this repository.
