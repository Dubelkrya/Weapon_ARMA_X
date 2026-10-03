# MP-133 V3 — G3 Phase A: real donor → same installed magazine (read-only audit + design)

**Status:** `G3_PHASE_A_READONLY_AUTHORIZED / G3_REAL_DONOR_TRANSACTION_NOT_IMPLEMENTED`.
Documentation only — no code, lab, production, Core, graph/ASI/ANM, world/layer or `main` change.
Source: Issue #34 comment 5972965844. Verified G2 baseline (owner runtime, not re-tested):
one-shot `SetAmmoCount(+1)` → same installed M1 `1/10` stable +250 ms/+1 s; native short-R
(`CMD_Weapon_Reload intValue=1`) + `Weapon_Rack_Bolt` chambers it (M1 `1→0`, `chambered 0→1`);
then firing empties the chamber. Keep the lab byte-identical (script SHA
`D581B9C9EE270725FFEC94C7685CBBCB2AB41DBA717F2B4FBCF8C4AC8DDCBEB1`).

Labels: **SOURCE** (installed SDK 1.8.0.13 / project), **INFERENCE**, **UNRESOLVED**.

---

## 1. Real source object selection (donor discovery)

Base facts (**SOURCE**, `ArmaReforgerScriptAPIPublic` installed docs):
- `BaseMagazineComponent`: `GetAmmoCount()`, `GetMaxAmmoCount()`, `GetAmmoType(int idx=0)` →
  `ResourceName`, `GetMagazineWell()`, `GetOwner()` → `IEntity`, `IsUsed()`,
  `SetAmmoCount(int)`.
- `BaseWeaponComponent.GetCurrentMagazine()` → `BaseMagazineComponent` (installed target).
- Acting user / inventory: `SCR_PlayerController.GetLocalControlledEntity()` (static);
  `SCR_InventoryStorageManagerComponent` reachable via
  `SCR_InventoryStorageManagerComponent.Cast(userEntity.FindComponent(SCR_InventoryStorageManagerComponent))`
  (project-proven pattern, Core `ARMST_ACTION_LOOT.c`).
- Enumerate items: `InventoryStorageManagerComponent.GetItems(out array<IEntity>, EStoragePurpose)`,
  `SCR_InventoryStorageManagerComponent.GetAllRootItems(out array<IEntity>)`,
  `FindItemsWithComponents(out array<IEntity>, array<TypeName> componentsQuery, EStoragePurpose)`,
  `FindItemWithComponents(array<TypeName>, EStoragePurpose)`, `Contains(IEntity)`.
- Storages: `GetStorages(out array<BaseInventoryStorageComponent>, EStoragePurpose)`,
  `GetCharacterStorage()`; storage contents:
  `BaseInventoryStorageComponent.GetAll(out array<IEntity>, bool includeChildComponents=true)`,
  `GetItem(int slotID)`, `GetOwnedItems(out array<InventoryItemComponent>, bool)`,
  `Contains(IEntity)`, `FindItemSlot(IEntity)`.
- Slot/ownership: `InventoryItemComponent.GetParentSlot()` → `InventoryStorageSlot`
  (`GetStorage()`, `GetID()`, `IsLocked()`).

**Selection plan (design, no writes):** for each candidate item entity in the user's reachable
storages, resolve the magazine as `BaseMagazineComponent.Cast(itemEntity.FindComponent(MagazineComponent))`
(fallback `BaseMagazineComponent`); require **all**: `mag != weapon.GetCurrentMagazine()` (exclude
the installed target), `mag.GetAmmoCount() >= 1`, `mag.GetOwner() == itemEntity`, and the item is
actually owned by the acting user (`invMgr.Contains(itemEntity)`, and `GetParentSlot()` resolves to
one of the user's storages). If the item is nested in a container, scope explicitly (containers only
if intentionally selected). Never use a spawn-only fake reserve and never the target itself.

**Exclusivity / lifetime:** capture the donor item entity + magazine component reference + owning
entity; re-verify immediately before committing; abort if the reference, owner or storage changed
(**INFERENCE**; exact invalidation semantics **UNRESOLVED**).

**Ammo compatibility:** compare `donor.GetAmmoType(0)` with `target.GetAmmoType(0)` (**SOURCE**
getter). Accept **strict equality** for the first homogeneous transfer. Do **not** assume all 12ga
variants are interchangeable, and do **not** treat identical prefab GUID as entity identity
(**INFERENCE**). `AmmoMapping`/`MagazineWell` are prefab data; only `GetMagazineWell()` is a runtime
getter.

## 2. Write / observer / transaction feasibility

- **Only** magazine-ammo writer found: `BaseMagazineComponent.SetAmmoCount(int)` (**SOURCE**).
  No native atomic one-round transfer and no round-level consume API were found (revalidated on the
  installed SDK; matches the earlier T4 Phase A `MP133_V3_T4_ONE_SHELL_TRANSFER.md`).
- **Donor presentation update:** how a setter on an inventory item's magazine propagates to the
  inventory UI/count is **not documented** → **OWNER-RUNTIME test needed**. Whether the engine
  authorizes/serializes a script `SetAmmoCount` on an inventory item is **UNRESOLVED**.
- `SCR_InventoryStorageManagerComponent` also exposes `ResupplyMagazines(int maxMagazineCount=4,
  EMuzzleType=-1, InventoryStorageManagerComponent mustBeInStorage=null)` /
  `ResupplyMagazines(map<ResourceName,int>)`, `GetValidResupplyItemsAndCount(...)`,
  `CanResupplyItem(...)`, `CanResupplyMuzzle(...)`, `EndResupplyMagazines()`. Their semantics may
  create/replace magazines (arsenal-style) and are **UNRESOLVED**; they may **not** be substituted
  until proven to preserve the target identity and deduct exactly one compatible **real source**
  round.
- **Server authority:** `Replication.IsServer()==true` in a solo/offline run is **not** MP-authority
  proof. Authoritative write context and replication of `SetAmmoCount` are **UNRESOLVED**.

## 3. Failure / concurrency matrix and transaction contract (no mutation executed)

Two setters are **not atomic**; no compensation can be promised to work. Order windows:
- **donor-first** (`donor-1` then `target+1`): if the target write fails → one real round lost.
- **target-first** (`target+1` then `donor-1`): if the donor write fails → one round duplicated.
Neither order is provably safe (**INFERENCE**); the order must be chosen explicitly and accepted as
risky, with a partial-failure STOP.

| Condition | Expected handling |
|---|---|
| donor gone / replaced / moved | `REJECTED` (no write) |
| donor ammo 0 | `REJECTED` |
| ammo type incompatible | `REJECTED` |
| target full (`>= max`) | `REJECTED` |
| target identity changed / not installed | `REJECTED` |
| weapon switched / interrupting action | `REJECTED` |
| competing request / duplicate animation event | `REJECTED` (per-cycle token) |
| `target+1` ok, `donor-1` failed | `INDETERMINATE` → STOP/quarantine/log, no auto-repeat |
| `donor-1` ok, `target+1` failed | `INDETERMINATE` → STOP/quarantine/log, no auto-repeat |
| rollback failed / lost ack | `INDETERMINATE` |
| both writes ok, identities validated, sum conserved, chamber unchanged | `COMMITTED` |

**Result states:** `REJECTED` (nothing written), `COMMITTED` (both identities validated + `donor`
before−1 + `target` before+1 + `donorBefore+targetBefore == donorAfter+targetAfter`; chamber
unchanged), `INDETERMINATE` (any partial/uncertain outcome → STOP, quarantine, log; **never**
silently repeat).

**Idempotence:** exactly-once **per insertion cycle / transaction token**, advanced only when the
cycle's real donor→same-installed-magazine transfer and validations complete — **not** T4b's
permanent `already-used` latch (which is an intentional lab one-shot guard).

## 4. Future adapter boundary (conceptual, no guessed Enforce API)

A backend-agnostic contract kept separate from input/animation:
```
validate()   -> { eligible: bool, reason: string }          // donor/target identity, type, capacity, ownership, no in-progress op
commitOne()  -> { status: COMMITTED|REJECTED|INDETERMINATE, donorTag, targetTag, donorBefore/After, targetBefore/After, chamberBefore/After }
```
The SDK 1.8 custom backend uses the two setters; a future SDK 1.9 `SCR_MagazineRepackingSystem`
adapter may replace `commitOne` **only after** a feasibility audit (repacking may not support a
weapon-attached magazine). No implementation now; no guessed method names.

## 5. Proposed G3-B experiment (separate owner approval) + lab allowlist

**One minimum owner-only runtime experiment:**
- Fresh lab target MP-133 with the **same already-installed magazine** (e.g. `0/10`) and **one**
  separate, explicitly expendable, compatible homogeneous buckshot donor magazine in the owner's
  inventory (e.g. `10/10`); chamber noted; Core OFF.
- A single **weapon-local, non-R** invocation (the existing lab action pattern) that, once,
  `validate()`s, then attempts the two writes with explicit snapshots.
- Full snapshots at pre / post / +250 ms / +1 s of: target mag component+entity tag and
  ammo/max; donor item entity + magazine component tag and ammo/max; inventory membership;
  muzzle supply, barrel, chamber flag. Owner-visible inventory counts before/after.
- Pass criterion: total `donor+installed` rounds conserved, **neither magazine replaced**
  (entity references unchanged), chamber unchanged; donor at 0 → **do not auto-delete** its item.
- Negative cases recorded as no-write rejects: no donor, incompatible ammo, target full, duplicate
  invocation.
- Not in Phase B: production/MP tests, repeated `+1`, real gameplay integration.

**Lab allowlist (proposed, no code now):** a **separate isolated T4c fixture/addon** is recommended
to keep the verified T4b one-shot baseline byte-identical — either a new prefab+component inside a
new lab addon, or a new isolated prefab in a new addon; decision for review. The T4b lab, original
T2a/T4a, production Weapons/Core, frozen V2/P2 and Astra stay untouched.

## 6. Verified facts / unresolved

- **SOURCE:** the setter/getter/inventory/storage/slot API signatures above; no atomic transfer or
  round-consume API; `ResupplyMagazines` exists but semantics unproven.
- **UNRESOLVED:** how a setter on an inventory donor updates inventory presentation/count; whether
  the write is authorized/replicated; exact failure/rollback behaviour; whether `GetItems`
  includes nested-container items by default; whether 12ga variants share interchangable ammo type;
  MP authority.
- `GAMEPLAY_FILES_CHANGED = 0`; local == remote publication; no code commit.

---

```
G3_PHASE_A_RESULT:
SDK_VERSION: ArmaReforgerScriptAPIPublic (installed, Enfusion 1.8.0.13; docs dated 2026-09-19)
BRANCH_HEAD: t4b/installed-mag-probe @ 996360f2e54c3edc0e1c935155d8739c593d3648 (T4b script SHA D581B9C9EE270725FFEC94C7685CBBCB2AB41DBA717F2B4FBCF8C4AC8DDCBEB1 unchanged)
DONOR_DISCOVERY: user inventory via SCR_PlayerController.GetLocalControlledEntity() -> SCR_InventoryStorageManagerComponent; enumerate via GetItems/GetAllRootItems/FindItemsWithComponents/GetStorages + BaseInventoryStorageComponent.GetAll/GetOwnedItems; resolve BaseMagazineComponent via itemEntity.FindComponent(MagazineComponent); exclude weapon.GetCurrentMagazine()
DONOR_OWNERSHIP_CHECK: invMgr.Contains(itemEntity) + InventoryItemComponent.GetParentSlot()->InventoryStorageSlot; re-verify before commit (exact invalidation semantics UNRESOLVED)
AMMO_COMPATIBILITY: BaseMagazineComponent.GetAmmoType(int idx=0) ResourceName; strict equality required for the first homogeneous transfer; 12ga interchangeability NOT assumed
SETTER_ON_INVENTORY_DONOR: BaseMagazineComponent.SetAmmoCount(int) is the only writer; inventory presentation update and authorization UNRESOLVED (owner-runtime needed)
SERVER_AUTHORITY: UNRESOLVED; Replication.IsServer()==true offline is NOT MP proof
ATOMICITY: NOT atomic; two setters; no compensation guarantee; donor-first vs target-first both have loss/dup windows
PARTIAL_FAILURE_POLICY: REJECTED (no write) / COMMITTED (validated + donor-1 + target+1 + sum conserved + chamber unchanged) / INDETERMINATE (partial -> STOP/quarantine/log; never auto-repeat); exactly-once per insertion-cycle token
G3B_PROPOSED_TEST: one owner-only offline run: fresh lab target MP-133 with same installed mag + one expendable inventory donor mag, single weapon-local non-R invocation, full pre/post/+250ms/+1s identity+count+inventory+chamber snapshots; conservation + no replacement; donor 0 -> no auto-delete; no-donor/incompatible/full/duplicate = no-write rejects; separate T4c fixture recommended
GAMEPLAY_FILES_CHANGED: 0
UNRESOLVED: inventory-donor presentation/authority/replication, rollback, nested-container item coverage, 12ga ammo-type equality, MP authority, ResupplyMagazines substitution
NEXT_GATE: STOP_FOR_OWNER_REVIEW
```
