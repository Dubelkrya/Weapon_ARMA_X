# MP-133 V3 — T4: one real shell transfer into the installed magazine (Phase A)

**Status:** `T4_API_OR_TRANSACTION_BLOCKED` (Phase A HARD STOP).
Read-only. No addon created or modified; production Weapons/Core, frozen V2/P2, the existing
`ARMSTMP133T2A_Diag` and Astra's graph lab are untouched. Source: Issue #27 comment 5970812620
(T4) and correction 5970820808 ("agent cannot run Workbench/game; stop rather than risk a
speculative mutation").

Labels: **SOURCE** (installed SDK doc), **INFERENCE**, **UNRESOLVED**.

---

## 1. Scope

T4 asks for **one controlled transfer of one real shell from a legitimate inventory source into
the ALREADY INSTALLED magazine** in a **new isolated lab addon**. Phase A (mandatory, read-only)
must establish the exact installed-SDK write/transfer API, donor selection/consumption, server
authority, atomicity and a safe rollback **before** any Phase B implementation. If any of these
cannot be established, the task mandates `T4_API_OR_TRANSACTION_BLOCKED`.

Authority inspected: installed Tools docs
`…\Arma Reforger Tools\Workbench\docs\ArmaReforgerScriptAPIPublic\html\` (1.8.0.13).
Resolved production addon `…\addons\ARMST-PLATFORM---Weapons` (ID `ARMSTPLATFORMWeapons`), all
files unchanged; knowledge `main` at `99c1819` (origin divergence 0/0).

---

## 2. Phase A — installed-SDK API evidence (**SOURCE**)

| Need | API (exact) | Doc | Verdict |
|---|---|---|---|
| Installed magazine ref | `proto external BaseMagazineComponent BaseWeaponComponent.GetCurrentMagazine()` | interfaceBaseWeaponComponent.html | present |
| Magazine ammo / max | `proto external int BaseMagazineComponent.GetAmmoCount()` / `GetMaxAmmoCount()` | interfaceBaseMagazineComponent.html | present |
| Magazine owning entity | `proto external IEntity BaseMagazineComponent.GetOwner()` | same | present |
| Ammo type | `proto external ResourceName GetAmmoType(int idx=0)` | same | present |
| **Modify ammo** | `proto external void BaseMagazineComponent.SetAmmoCount(int ammoCount)` | same | **setter only — no add/consume-one primitive** |
| Muzzle/chamber read | `BaseWeaponComponent.GetCurrentMuzzle()`; `BaseMuzzleComponent.GetAmmoCount/GetMaxAmmoCount/GetCurrentBarrelIndex/IsChamberingPossible` | interfaceBaseWeaponComponent.html, interfaceBaseMuzzleComponent.html | present |
| Chamber write | `BaseMuzzleComponent.ClearChamber(int barrelIndex)` only | interfaceBaseMuzzleComponent.html | **no chamber setter** |
| Inventory enumerate/find | `InventoryStorageManagerComponent.GetItems(...)`, `FindItemWithComponents(...)`, `FindItemsWithComponents(...)`, `Contains(...)`, `GetStorages(...)` | interfaceInventoryStorageManagerComponent.html | present |
| Inventory item move/remove | `TryRemoveItemFromStorage(...)`, `TryDeleteItem(...)`, `TryMoveItemToStorage(...)`, `TryInsertItemInStorage(...)` | same | **item-level, not ammo-level** |
| Resupply (candidate) | `SCR_InventoryStorageManagerComponent.ResupplyMagazines(map<ResourceName,int>)`, `GetValidResupplyItemsAndCount(...)`, `CanResupplyItem(...)` | interfaceSCR__InventoryStorageManagerComponent.html | **semantics UNRESOLVED** (arsenal-style; may create/replace magazines) |
| Atomic ammo transfer | — | — | **ABSENT** |
| Loose-round / ammo-stack transfer | — | — | **ABSENT** (no ammo item/round component found) |
| Authority / replication of `SetAmmoCount` | no doc note on server/`RplComponent`, no `OnAmmoCountChanged` invoker on the weapon | — | **UNRESOLVED** |

**Key finding.** The only primitive that writes magazine ammo is `SetAmmoCount(int)` — a direct
value setter. There is **no** engine API to (a) add exactly one round to an existing magazine,
(b) legitimately consume exactly one round from a donor magazine, or (c) perform an atomic
target+donor transfer. Inventory APIs are item-level (find/move/remove whole items), not
ammo-level.

---

## 3. Decision / rejection table

| Requirement (T4) | Available | Rejected / why |
|---|---|---|
| Add exactly one round to the installed mag without a whole-mag reload / new mag / chamber change | `SetAmmoCount(t+1)` on `GetCurrentMagazine()` | Works value-wise, but it is a raw setter — not evidence of authority/replication/atomicity (spec explicitly forbids treating a compiling setter as proof) |
| Consume exactly one from a legitimate donor, preserving donor identity | donor found via inventory APIs; `SetAmmoCount(d-1)` | No legitimate engine consumption API; a setter on an inventory magazine may not update the inventory/ammo system correctly → risk of phantom/lost shells |
| Atomic transfer or validated two-step with rollback | none | A two-step setter is not atomic; rollback of an inventory item's ammo is not guaranteed by any documented API |
| Authoritative write context / sync | none documented for `SetAmmoCount` | Cannot establish on the installed SDK statically |
| Compatibility check | `GetAmmoType(idx)` exists | possible to compare, but insufficient without the transfer API |
| Server/MP correctness | — | out of scope for a local test, but authority is also unverifiable |

Per the Phase A HARD STOP, none of "authoritative write context" or "safe transaction/recovery
behavior" can be established; compensating with a raw setter on a real inventory item would be
exactly the unsupported-API workaround the task forbids. Therefore **no isolated T4 lab addon was
created** (avoiding a speculative mutation), per the correction instruction: *"If agent's proposed
mutation cannot be bounded safely without runtime verification, do not risk speculative tests;
stop for owner review before implementation."*

---

## 4. Minimal next experiment for owner review (not implemented)

One of the following, chosen by the owner:

1. **Runtime semantics probe (narrowest).** A tiny, isolated, owner-run lab that, on one explicit
   owner action, calls `SetAmmoCount` on a **throwaway test magazine only** (not the equipped
   weapon and not a live inventory item) and observes in-game/HUD/inventory whether the change
   persists, replicates and leaves item identity intact. This establishes whether
   `SetAmmoCount` is a usable write primitive at all **before** any real transfer.
2. **Explicit authorisation of a local-only, setter-based PoC.** Owner accepts that replication /
   authority / atomicity are UNRESOLVED and authorises a local/offline one-shot transfer
   (`target+1`, `donor-1`, with pre/post conservation checks and best-effort rollback), plus a
   defined **invocation mechanism** (a dedicated lab input action — not R — is itself an SDK
   question that must be confirmed first).

Either path is a **new, separately scoped task**; T4 Phase B is not started here.

## 5. Facts / unresolved

- **SOURCE:** `SetAmmoCount(int)` is the only magazine-ammo writer; no atomic/consume/loose-round
  API; inventory APIs are item-level; muzzle has only `ClearChamber`.
- **UNRESOLVED:** `SetAmmoCount` authority/replication; legitimate donor consumption; atomic
  rollback; `ResupplyMagazines` semantics; a safe non-R lab invocation.
- **No changes made:** 23-file graph/ASI/clip/prefab set unchanged; Weapons dirty ≈ 29, Core ≈ 4;
  T2A diagnostic and V2/P2 untouched.

## 6. Stop

`T4_API_OR_TRANSACTION_BLOCKED`. STOP for owner review before Phase B. Any graph/R-input/animation/
production integration remains separately authorised.
